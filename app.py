import datetime as dt
import hmac
import io
import os
import secrets
import smtplib
import ssl
import threading
import time
from email.message import EmailMessage
from functools import wraps
from zoneinfo import ZoneInfo

from PIL import Image, ImageOps
from flask import (Flask, abort, jsonify, redirect, render_template, request, send_file,
                   session, url_for)
from werkzeug.security import check_password_hash

import content_seed
import excel_export
from store import DEFAULT_RATE, FIELDS_NUM, make_store

TZ = ZoneInfo("Europe/Rome")
MESI_IT = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", "Luglio", "Agosto",
           "Settembre", "Ottobre", "Novembre", "Dicembre"]
MONEY = ["parcheggi", "alloggio", "benzina", "pedaggi", "diaria", "varie"]

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "1") == "1",
    PERMANENT_SESSION_LIFETIME=dt.timedelta(days=30),
    JSON_AS_ASCII=False,
    MAX_CONTENT_LENGTH=15 * 1024 * 1024,
)
Image.MAX_IMAGE_PIXELS = 80_000_000
if not os.environ.get("SECRET_KEY"):
    print("ATTENZIONE: SECRET_KEY non impostata: le sessioni si azzerano a ogni riavvio.")

store = make_store()

ADMIN_EMAIL = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or ""
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH") or ""
CRON_TOKEN = os.environ.get("CRON_TOKEN") or ""


# ----------------------------------------------------------------------------- utilità
def now_local():
    return dt.datetime.now(TZ)


def current_month():
    return now_local().strftime("%Y-%m")


def month_label(ym):
    return f"{MESI_IT[int(ym[5:7]) - 1]} {ym[:4]}"


def valid_month(ym):
    try:
        dt.datetime.strptime(ym, "%Y-%m")
        return True
    except (TypeError, ValueError):
        return False


def num(v, field):
    if v in (None, ""):
        return 0.0
    try:
        x = float(str(v).replace(",", "."))
    except ValueError:
        raise ValueError(f"Valore non valido per {field}")
    if x < 0 or x > 1_000_000:
        raise ValueError(f"Valore fuori intervallo per {field}")
    return round(x, 2) if field != "rate" else round(x, 4)


def clean_expense(data, rate=None):
    try:
        day = dt.date.fromisoformat(str(data.get("date", "")))
    except ValueError:
        raise ValueError("Data non valida")
    doc = {"date": day.isoformat(),
           "luogo": str(data.get("luogo") or "").strip()[:120],
           "descrizione": str(data.get("descrizione") or "").strip()[:300]}
    for f in FIELDS_NUM:
        doc[f] = num(data.get(f), f)
    if rate is not None:
        doc["rate"] = rate
    return doc


def row_totals(e):
    km_tot = round(float(e.get("km", 0)) * float(e.get("rate", DEFAULT_RATE)), 2)
    total = round(km_tot + sum(float(e.get(f, 0)) for f in MONEY), 2)
    return km_tot, total


def public_expense(e):
    km_tot, total = row_totals(e)
    out = {k: e.get(k) for k in ["date", "luogo", "descrizione", "km", "rate", *MONEY]}
    out.update(id=e["_id"], tot_km=km_tot, totale=total)
    return out


def month_summary(rows, anticipo):
    tot = {f: round(sum(float(e.get(f, 0)) for e in rows), 2) for f in ["km", *MONEY]}
    tot["tot_km"] = round(sum(row_totals(e)[0] for e in rows), 2)
    tot["totale"] = round(sum(row_totals(e)[1] for e in rows), 2)
    tot["anticipo"] = anticipo
    tot["da_rimborsare"] = round(tot["totale"] - anticipo, 2)
    return tot


# ----------------------------------------------------------------------------- email + fine mese
def mail_configured():
    return bool(os.environ.get("SMTP_HOST") and os.environ.get("SMTP_USER") and os.environ.get("SMTP_PASS"))


def send_month_email(ym):
    rows = store.list_expenses(ym)
    settings = store.get_settings()
    data = excel_export.build_workbook(ym, rows, settings["anticipo"])
    summ = month_summary(rows, settings["anticipo"])
    msg = EmailMessage()
    msg["Subject"] = f"Nota spese {month_label(ym)} pronta – Papa Design Studio"
    msg["From"] = os.environ.get("MAIL_FROM") or os.environ["SMTP_USER"]
    msg["To"] = os.environ.get("MAIL_TO") or ADMIN_EMAIL
    msg.set_content(
        f"Ciao,\n\nla nota spese di {month_label(ym)} è pronta e la trovi in allegato.\n"
        f"Voci registrate: {len(rows)} · Totale: € {summ['totale']:.2f} · "
        f"Da rimborsare: € {summ['da_rimborsare']:.2f}\n\n"
        f"Puoi scaricarla anche dal sito, nella sezione Note spese.\n")
    msg.add_attachment(data, maintype="application",
                       subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       filename=excel_export.nome_file(ym))
    host, port = os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587"))
    ctx = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=30) as s:
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            s.send_message(msg)


_tick_lock = threading.Lock()


def tick():
    """Chiude i mesi finiti: crea la notifica nel sito e invia l'email con l'Excel.
    È idempotente e recupera i mesi persi se il servizio era spento a mezzanotte."""
    if not _tick_lock.acquire(blocking=False):
        return
    try:
        cur = current_month()
        for ym in store.months_with_expenses():
            if ym < cur and store.get_notif(ym) is None:
                store.create_notif(ym)
        if mail_configured():
            for n in store.list_notifs():
                if n.get("emailed"):
                    continue
                last = n.get("email_last_try")
                if last and time.time() - last < 900:  # ritenta al massimo ogni 15 minuti
                    continue
                try:
                    send_month_email(n["_id"])
                    store.update_notif(n["_id"], emailed=True, email_error=None, email_last_try=time.time())
                except Exception as exc:  # noqa: BLE001
                    store.update_notif(n["_id"], email_error=str(exc)[:200], email_last_try=time.time())
    finally:
        _tick_lock.release()


def scheduler_loop():
    while True:
        try:
            tick()
        except Exception as exc:  # noqa: BLE001
            print("tick error:", exc)
        time.sleep(30)


_started = False


def start_scheduler():
    global _started
    if not _started:
        _started = True
        threading.Thread(target=scheduler_loop, daemon=True, name="month-end").start()


_last_req_tick = 0.0


@app.before_request
def opportunistic_tick():
    # se il servizio era "addormentato" a mezzanotte, al primo accesso recupera la chiusura del mese
    global _last_req_tick
    if time.time() - _last_req_tick > 60 and request.endpoint not in ("healthz", "static"):
        _last_req_tick = time.time()
        threading.Thread(target=tick, daemon=True).start()


# ----------------------------------------------------------------------------- auth
_fails = {}


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def check_csrf():
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf") or ""
    if not hmac.compare_digest(sent, session.get("csrf", "x")):
        abort(403)


def login_required(api=False):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if not session.get("auth"):
                if api:
                    return jsonify(error="Non autenticato"), 401
                return redirect(url_for("login"))
            if api and request.method != "GET":
                check_csrf()
            return fn(*a, **kw)
        return wrapper
    return deco


def credentials_ok(email, password):
    if not ADMIN_EMAIL or not (ADMIN_PASSWORD or ADMIN_PASSWORD_HASH):
        return False
    ok_mail = hmac.compare_digest(email.strip().lower(), ADMIN_EMAIL)
    if ADMIN_PASSWORD_HASH:
        ok_pw = check_password_hash(ADMIN_PASSWORD_HASH, password)
    else:
        ok_pw = hmac.compare_digest(password.encode(), ADMIN_PASSWORD.encode())
    return ok_mail and ok_pw


@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "same-origin"
    resp.headers["Cache-Control"] = "no-store" if request.endpoint != "static" else "public, max-age=3600"
    return resp


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        check_csrf()
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",")[0].strip()
        tries = [t for t in _fails.get(ip, []) if time.time() - t < 600]
        if len(tries) >= 5:
            error = "Troppi tentativi. Riprova tra qualche minuto."
        elif credentials_ok(request.form.get("email", ""), request.form.get("password", "")):
            _fails.pop(ip, None)
            token = session.get("csrf")
            session.clear()
            session["auth"] = True
            session["csrf"] = token or secrets.token_hex(16)
            session.permanent = True
            return redirect(url_for("index"))
        else:
            tries.append(time.time())
            _fails[ip] = tries
            error = "Email o password non corretti."
    elif session.get("auth"):
        return redirect(url_for("index"))
    return render_template("login.html", error=error, csrf=csrf_token())


@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))


# ----------------------------------------------------------------------------- pagine
MEDIA_SLOTS = {"ritratto": "Ritratto di Claudio Papa"}


def slot_ok(slot):
    return slot in MEDIA_SLOTS or (slot.startswith("c-") and store.get_content(slot[2:]) is not None)
STATIC_IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "img")


def media_versions():
    """slot -> versione (per la cache). Prima le foto caricate dal sito, poi quelle messe in static/img."""
    out = {}
    for slot in MEDIA_SLOTS:
        p = os.path.join(STATIC_IMG, f"{slot}.jpg")
        if os.path.exists(p):
            out[slot] = int(os.path.getmtime(p))
    out.update(store.media_info())
    return out


def ensure_seed():
    if not store.content_seeded():
        if not store.list_content():
            for d in content_seed.seed_docs():
                store.add_content(d)
        store.mark_content_seeded()


CONTENT_TYPES = {
    "product": {"icon": 20, "brand": 120, "title": 120, "text": 600, "items": 2000, "url": 400, "urllabel": 60},
    "news": {"kind": 20, "source": 80, "title": 160, "when": 60, "text": 600, "url": 400},
    "award": {"year": 40, "title": 160, "detail": 240},
    "timeline": {"year": 40, "text": 500},
}
ICONS = {"vapore", "acqua", "ceramica", "doccia", "fuoco"}
KINDS = {"Rivista", "Cersaie", "Evento", "Web"}


def clean_content(ctype, data):
    spec = CONTENT_TYPES[ctype]
    out = {}
    for k, mx in spec.items():
        v = data.get(k, "")
        if k == "items":
            lines = [str(x).strip()[:160] for x in (v if isinstance(v, list) else str(v).splitlines()) if str(x).strip()]
            out[k] = lines[:30]
            continue
        out[k] = str(v or "").strip()[:mx]
    if "url" in out and out["url"] and not out["url"].lower().startswith(("http://", "https://")):
        raise ValueError("Il link deve iniziare con http:// o https://")
    if ctype == "product":
        out["icon"] = out["icon"] if out["icon"] in ICONS else "acqua"
    if ctype == "news":
        out["kind"] = out["kind"] if out["kind"] in KINDS else "Rivista"
    required = {"product": "title", "news": "title", "award": "title", "timeline": "text"}[ctype]
    if not out.get(required):
        raise ValueError("Compila il campo obbligatorio")
    return out


@app.route("/")
def home():
    ensure_seed()
    groups = {t: [] for t in CONTENT_TYPES}
    for c in store.list_content():
        groups.setdefault(c["type"], []).append(c)
    return render_template("home.html", media=media_versions(), g=groups)


@app.get("/media/<slot>")
def media_get(slot):
    if not slot_ok(slot):
        abort(404)
    doc = store.get_media(slot)
    if doc:
        resp = send_file(io.BytesIO(doc["data"]), mimetype=doc["mime"])
    else:
        p = os.path.join(STATIC_IMG, f"{slot}.jpg")
        if not os.path.exists(p):
            abort(404)
        resp = send_file(p, mimetype="image/jpeg")
    resp.headers["Cache-Control"] = "public, max-age=31536000, immutable" if request.args.get("v") else "public, max-age=300"
    return resp


@app.get("/api/media")
@login_required(api=True)
def api_media_list():
    info = media_versions()
    return jsonify([{"slot": k, "label": v, "version": info.get(k)} for k, v in MEDIA_SLOTS.items()])


@app.route("/admin")
@login_required()
def admin():
    return render_template("admin.html", csrf=csrf_token())


def public_content(c, versions):
    d = {k: v for k, v in c.items() if k != "_id"}
    d["id"] = c["_id"]
    d["version"] = versions.get("c-" + c["_id"])
    return d


@app.get("/api/content")
@login_required(api=True)
def api_content_list():
    ensure_seed()
    versions = media_versions()
    return jsonify({"items": [public_content(c, versions) for c in store.list_content()],
                    "portrait": versions.get("ritratto")})


@app.post("/api/content/<ctype>")
@login_required(api=True)
def api_content_add(ctype):
    if ctype not in CONTENT_TYPES:
        abort(404)
    try:
        doc = clean_content(ctype, request.get_json(force=True) or {})
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    same = [c.get("order", 0) for c in store.list_content() if c["type"] == ctype]
    doc.update(type=ctype, order=(max(same) + 1) if same else 0)
    return jsonify(id=store.add_content(doc)["_id"]), 201


@app.put("/api/content/<_id>")
@login_required(api=True)
def api_content_edit(_id):
    cur = store.get_content(_id)
    if not cur:
        return jsonify(error="Voce non trovata"), 404
    try:
        doc = clean_content(cur["type"], request.get_json(force=True) or {})
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    store.update_content(_id, doc)
    return jsonify(ok=True)


@app.delete("/api/content/<_id>")
@login_required(api=True)
def api_content_del(_id):
    if not store.delete_content(_id):
        return jsonify(error="Voce non trovata"), 404
    return jsonify(ok=True)


@app.post("/api/content/<_id>/move")
@login_required(api=True)
def api_content_move(_id):
    cur = store.get_content(_id)
    if not cur:
        return jsonify(error="Voce non trovata"), 404
    step = -1 if (request.get_json(force=True) or {}).get("dir") == -1 else 1
    same = [c for c in store.list_content() if c["type"] == cur["type"]]
    for i, c in enumerate(same):  # rinumera 0..n per sicurezza
        c["order"] = i
    idx = next(i for i, c in enumerate(same) if c["_id"] == _id)
    j = idx + step
    if 0 <= j < len(same):
        same[idx], same[j] = same[j], same[idx]
    for i, c in enumerate(same):
        store.update_content(c["_id"], {"order": i})
    return jsonify(ok=True)


@app.post("/api/media/<slot>")
@login_required(api=True)
def api_media_put(slot):
    if not slot_ok(slot):
        abort(404)
    f = request.files.get("file")
    if not f:
        return jsonify(error="Nessun file ricevuto"), 400
    try:
        img = Image.open(f.stream)
        img.load()
        img = ImageOps.exif_transpose(img).convert("RGB")
    except Exception:  # noqa: BLE001
        return jsonify(error="Il file non è un'immagine valida (usa JPG, PNG o WebP)"), 400
    img.thumbnail((1800, 1800), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=86, optimize=True, progressive=True)
    store.set_media(slot, buf.getvalue(), "image/jpeg")
    return jsonify(ok=True, version=store.media_info().get(slot))


@app.delete("/api/media/<slot>")
@login_required(api=True)
def api_media_del(slot):
    if not slot_ok(slot):
        abort(404)
    store.delete_media(slot)
    return jsonify(ok=True)


@app.route("/app")
@login_required()
def index():
    return render_template("index.html", csrf=csrf_token(), month=current_month(),
                           mail_ok=mail_configured())


@app.route("/healthz")
def healthz():
    return "ok"


@app.route("/api/cron/tick")
def cron_tick():
    """Da chiamare con un pinger esterno (es. cron-job.org) ogni 5-10 minuti: tiene sveglio
    il servizio e garantisce che la chiusura del mese scatti subito dopo mezzanotte."""
    if not CRON_TOKEN or not hmac.compare_digest(request.args.get("token", ""), CRON_TOKEN):
        abort(404)
    tick()
    return jsonify(ok=True, month=current_month())


# ----------------------------------------------------------------------------- API
@app.get("/api/month/<ym>")
@login_required(api=True)
def api_month(ym):
    if not valid_month(ym):
        return jsonify(error="Mese non valido"), 400
    rows = store.list_expenses(ym)
    s = store.get_settings()
    return jsonify(month=ym, label=month_label(ym), rate=s["rate"], anticipo=s["anticipo"],
                   expenses=[public_expense(e) for e in rows],
                   totals=month_summary(rows, s["anticipo"]), is_current=ym == current_month())


@app.post("/api/expenses")
@login_required(api=True)
def api_add():
    try:
        doc = clean_expense(request.get_json(force=True) or {}, rate=store.get_settings()["rate"])
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(public_expense(store.add_expense(doc))), 201


@app.put("/api/expenses/<_id>")
@login_required(api=True)
def api_edit(_id):
    try:
        doc = clean_expense(request.get_json(force=True) or {})
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    if not store.update_expense(_id, doc):
        return jsonify(error="Voce non trovata"), 404
    return jsonify(ok=True)


@app.delete("/api/expenses/<_id>")
@login_required(api=True)
def api_delete(_id):
    if not store.delete_expense(_id):
        return jsonify(error="Voce non trovata"), 404
    return jsonify(ok=True)


@app.get("/api/settings")
@login_required(api=True)
def api_settings():
    return jsonify(store.get_settings())


@app.put("/api/settings")
@login_required(api=True)
def api_settings_put():
    data = request.get_json(force=True) or {}
    try:
        rate = num(data.get("rate"), "rate")
        anticipo = num(data.get("anticipo"), "anticipo")
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    if rate <= 0:
        return jsonify(error="La tariffa deve essere maggiore di zero"), 400
    store.set_settings(rate=rate, anticipo=anticipo)
    updated = 0
    if data.get("apply_current_month"):  # opzionale: riallinea le voci del mese in corso
        for e in store.list_expenses(current_month()):
            store.update_expense(e["_id"], {"rate": rate})
            updated += 1
    return jsonify(ok=True, rate=rate, anticipo=anticipo, updated=updated)


def shift_month(ym, d):
    y, m = int(ym[:4]), int(ym[5:7])
    t = y * 12 + (m - 1) + d
    return f"{t // 12}-{t % 12 + 1:02d}"


@app.get("/api/year")
@login_required(api=True)
def api_year():
    cur = current_month()
    out = []
    for i in range(11, -1, -1):
        ym = shift_month(cur, -i)
        t = month_summary(store.list_expenses(ym), 0)
        out.append({"month": ym, "label": month_label(ym), "totale": t["totale"], "km": t["km"]})
    return jsonify(out)


@app.get("/api/months")
@login_required(api=True)
def api_months():
    cur = current_month()
    months = set(store.months_with_expenses()) | {cur}
    notifs = {n["_id"]: n for n in store.list_notifs()}
    out = []
    for ym in sorted(months, reverse=True):
        rows = store.list_expenses(ym)
        n = notifs.get(ym)
        out.append({"month": ym, "label": month_label(ym), "count": len(rows),
                    "totale": month_summary(rows, 0)["totale"], "closed": ym < cur,
                    "emailed": bool(n and n.get("emailed"))})
    return jsonify(out)


@app.get("/api/notifications")
@login_required(api=True)
def api_notifs():
    return jsonify([{"month": n["_id"], "label": month_label(n["_id"]), "created_at": n["created_at"],
                     "read": n.get("read", False), "emailed": n.get("emailed", False),
                     "email_error": n.get("email_error")} for n in store.list_notifs()])


@app.post("/api/notifications/<ym>/read")
@login_required(api=True)
def api_notif_read(ym):
    if valid_month(ym) and store.get_notif(ym):
        store.update_notif(ym, read=True)
    return jsonify(ok=True)


@app.get("/download/<ym>")
@login_required()
def download(ym):
    ym = ym.removesuffix(".xlsx")
    if not valid_month(ym):
        abort(404)
    data = excel_export.build_workbook(ym, store.list_expenses(ym), store.get_settings()["anticipo"])
    return send_file(io.BytesIO(data), as_attachment=True, download_name=excel_export.nome_file(ym),
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


start_scheduler()

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
