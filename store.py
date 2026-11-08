"""Livello dati: MongoDB in produzione, memoria locale se MONGODB_URI non è impostata (solo test)."""
import datetime as dt
import os
import threading
import uuid

DEFAULT_RATE = 0.6107
FIELDS_TEXT = ["luogo", "descrizione"]
FIELDS_NUM = ["km", "parcheggi", "alloggio", "benzina", "pedaggi", "diaria", "varie"]


def _next_month(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y + 1}-01" if m == 12 else f"{y}-{m + 1:02d}"


def _now() -> str:
    return dt.datetime.utcnow().isoformat(timespec="seconds")


class BaseStore:
    # --- regole comuni ---------------------------------------------------------------
    def get_settings(self) -> dict:
        s = self._get_settings() or {}
        return {"rate": float(s.get("rate", DEFAULT_RATE)), "anticipo": float(s.get("anticipo", 0) or 0)}

    def month_bounds(self, ym):
        return f"{ym}-01", f"{_next_month(ym)}-01"


class MemoryStore(BaseStore):
    kind = "memory"
    media = None

    def __init__(self):
        self.lock = threading.RLock()
        self.expenses, self.notifs, self.settings = {}, {}, {}
        self.media = {}

    def _get_settings(self):
        return self.settings.get("main")

    def set_settings(self, **kw):
        with self.lock:
            self.settings.setdefault("main", {}).update(kw)

    def list_expenses(self, ym):
        lo, hi = self.month_bounds(ym)
        with self.lock:
            rows = [dict(e) for e in self.expenses.values() if lo <= e["date"] < hi]
        return sorted(rows, key=lambda e: (e["date"], e["created_at"]))

    def add_expense(self, doc):
        doc = dict(doc, _id=uuid.uuid4().hex, created_at=_now() + f".{len(self.expenses):06d}")
        with self.lock:
            self.expenses[doc["_id"]] = doc
        return doc

    def update_expense(self, _id, doc):
        with self.lock:
            if _id not in self.expenses:
                return False
            self.expenses[_id].update(doc)
            return True

    def delete_expense(self, _id):
        with self.lock:
            return self.expenses.pop(_id, None) is not None

    def months_with_expenses(self):
        with self.lock:
            return sorted({e["date"][:7] for e in self.expenses.values()})

    def get_notif(self, ym):
        return self.notifs.get(ym)

    def set_media(self, slot, data, mime):
        with self.lock:
            self.media[slot] = {"_id": slot, "data": data, "mime": mime, "updated": int(dt.datetime.utcnow().timestamp())}

    def get_media(self, slot):
        return self.media.get(slot)

    def delete_media(self, slot):
        with self.lock:
            return self.media.pop(slot, None) is not None

    def media_info(self):
        return {k: v["updated"] for k, v in self.media.items()}

    def create_notif(self, ym):
        with self.lock:
            if ym in self.notifs:
                return False
            self.notifs[ym] = {"_id": ym, "created_at": _now(), "read": False, "emailed": False,
                               "email_error": None}
            return True

    def list_notifs(self):
        with self.lock:
            return sorted((dict(n) for n in self.notifs.values()), key=lambda n: n["_id"], reverse=True)

    def update_notif(self, ym, **kw):
        with self.lock:
            if ym in self.notifs:
                self.notifs[ym].update(kw)


class MongoStore(BaseStore):
    kind = "mongodb"

    def __init__(self, uri, dbname):
        from pymongo import MongoClient, ASCENDING
        self.client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        self.db = self.client[dbname]
        self.db.expenses.create_index([("date", ASCENDING)])

    def _get_settings(self):
        return self.db.settings.find_one({"_id": "main"})

    def set_settings(self, **kw):
        self.db.settings.update_one({"_id": "main"}, {"$set": kw}, upsert=True)

    def list_expenses(self, ym):
        lo, hi = self.month_bounds(ym)
        return list(self.db.expenses.find({"date": {"$gte": lo, "$lt": hi}}).sort([("date", 1), ("created_at", 1)]))

    def add_expense(self, doc):
        doc = dict(doc, _id=uuid.uuid4().hex, created_at=_now())
        self.db.expenses.insert_one(doc)
        return doc

    def update_expense(self, _id, doc):
        return self.db.expenses.update_one({"_id": _id}, {"$set": doc}).matched_count == 1

    def delete_expense(self, _id):
        return self.db.expenses.delete_one({"_id": _id}).deleted_count == 1

    def months_with_expenses(self):
        return sorted({d[:7] for d in self.db.expenses.distinct("date")})

    def get_notif(self, ym):
        return self.db.notifications.find_one({"_id": ym})

    def set_media(self, slot, data, mime):
        from bson.binary import Binary
        self.db.media.update_one({"_id": slot}, {"$set": {"data": Binary(data), "mime": mime,
                                 "updated": int(dt.datetime.utcnow().timestamp())}}, upsert=True)

    def get_media(self, slot):
        d = self.db.media.find_one({"_id": slot})
        if d:
            d["data"] = bytes(d["data"])
        return d

    def delete_media(self, slot):
        return self.db.media.delete_one({"_id": slot}).deleted_count == 1

    def media_info(self):
        return {d["_id"]: d.get("updated", 0) for d in self.db.media.find({}, {"updated": 1})}

    def create_notif(self, ym):
        from pymongo.errors import DuplicateKeyError
        try:
            self.db.notifications.insert_one({"_id": ym, "created_at": _now(), "read": False,
                                              "emailed": False, "email_error": None})
            return True
        except DuplicateKeyError:
            return False

    def list_notifs(self):
        return list(self.db.notifications.find().sort("_id", -1))

    def update_notif(self, ym, **kw):
        self.db.notifications.update_one({"_id": ym}, {"$set": kw})


def make_store():
    uri = os.environ.get("MONGODB_URI")
    if uri:
        return MongoStore(uri, os.environ.get("MONGODB_DB", "pds_note_spese"))
    print("ATTENZIONE: MONGODB_URI non impostata, uso la memoria locale (i dati si perdono al riavvio).")
    return MemoryStore()
