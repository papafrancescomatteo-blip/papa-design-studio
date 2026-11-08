(() => {
  const B = document.body;
  const CSRF = B.dataset.csrf;
  const NOW_MONTH = B.dataset.month;
  const MAIL_OK = B.dataset.mail === '1';
  const $ = (s, r = document) => r.querySelector(s);
  const eur = n => (Number(n) || 0).toLocaleString('it-IT', { style: 'currency', currency: 'EUR' });
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const MONEY = [['parcheggi', 'Parcheggi'], ['alloggio', 'Alloggio'], ['benzina', 'Benzina'],
                 ['pedaggi', 'Pedaggi'], ['diaria', 'Diaria'], ['varie', 'Varie/Pasti']];

  let month = NOW_MONTH;
  let state = null;

  async function api(url, method = 'GET', body) {
    const r = await fetch(url, {
      method, headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF },
      body: body ? JSON.stringify(body) : undefined, credentials: 'same-origin'
    });
    if (r.status === 401) { location.href = '/login'; return; }
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || 'Errore');
    return data;
  }

  function toast(msg) {
    const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg;
    document.body.appendChild(t); setTimeout(() => t.remove(), 2600);
  }

  const shiftMonth = (ym, d) => {
    const [y, m] = ym.split('-').map(Number); const dt = new Date(y, m - 1 + d, 1);
    return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}`;
  };
  const dayLabel = iso => new Date(iso + 'T12:00:00').toLocaleDateString('it-IT',
    { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });


  // ---------------------------------------------------------------- saluto, animazioni, grafici
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  (function greet() {
    const h = new Date().getHours();
    $('#hello').textContent = (h < 5 ? 'Buonanotte' : h < 13 ? 'Buongiorno' : h < 18 ? 'Buon pomeriggio' : 'Buonasera') + ', Claudio';
  })();

  const FMT = { int: n => String(Math.round(n)), km: n => n.toLocaleString('it-IT', { maximumFractionDigits: 1 }) + ' km', eur };
  function countUp() {
    document.querySelectorAll('#stats [data-n]').forEach(el => {
      const to = Number(el.dataset.n), f = FMT[el.dataset.f];
      if (reduce || !to) { el.textContent = f(to); return; }
      const t0 = performance.now(), dur = 900;
      const step = now => {
        const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 3);
        el.textContent = f(to * e);
        if (k < 1) requestAnimationFrame(step); else el.textContent = f(to);
      };
      requestAnimationFrame(step);
    });
  }

  const SPLIT = [['tot_km', 'Rimborso km'], ['parcheggi', 'Parcheggi'], ['alloggio', 'Alloggio'], ['benzina', 'Benzina'],
                 ['pedaggi', 'Pedaggi'], ['diaria', 'Diaria'], ['varie', 'Varie/Pasti']];
  function renderSplit() {
    const t = state.totals, rows = SPLIT.map(([k, l]) => [l, t[k] || 0]).filter(r => r[1] > 0).sort((a, b) => b[1] - a[1]);
    const tot = rows.reduce((a, r) => a + r[1], 0);
    $('#splitSub').textContent = state.label;
    $('#split').innerHTML = rows.length ? rows.map(([l, v], i) => `<div class="split-row">
      <span class="nm">${l}</span>
      <div class="track"><div class="fill" style="width:${(v / rows[0][1]) * 100}%;animation-delay:${i * 0.07}s"></div></div>
      <span class="am">${eur(v)}<i>${Math.round(v / tot * 100)}%</i></span></div>`).join('')
      : '<div class="split-empty">Quando aggiungerai delle spese, qui vedrai come si dividono.</div>';
  }

  let yearData = null;
  const SHORT = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'];
  function renderYear() {
    if (!yearData) return;
    const W = 600, H = 210, top = 22, bot = 28, ch = H - top - bot, n = yearData.length, slot = W / n, bw = slot * 0.58;
    const max = Math.max(1, ...yearData.map(d => d.totale));
    let g = `<defs><linearGradient id="gg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e0c68f"/><stop offset="1" stop-color="#a98d55"/></linearGradient></defs>`;
    [0.5, 1].forEach(f => g += `<line class="grid" x1="0" x2="${W}" y1="${top + ch * (1 - f)}" y2="${top + ch * (1 - f)}"/>`);
    g += `<line class="base" x1="0" x2="${W}" y1="${top + ch}" y2="${top + ch}"/>`;
    yearData.forEach((d, i) => {
      const h = d.totale > 0 ? Math.max(4, ch * d.totale / max) : 0, x = i * slot + (slot - bw) / 2, y = top + ch - h;
      g += `<g class="col ${d.month === month ? 'sel' : ''}" data-m="${d.month}" tabindex="0" role="button" aria-label="${esc(d.label)}: ${eur(d.totale)}">
        <rect x="${i * slot}" y="0" width="${slot}" height="${H}" fill="transparent"/>
        ${h ? `<rect class="bar-r" x="${x}" y="${y}" width="${bw}" height="${h}" rx="4" style="animation-delay:${i * 0.04}s"/>` : ''}
        ${d.totale > 0 ? `<text class="val" x="${i * slot + slot / 2}" y="${y - 6}">${Math.round(d.totale).toLocaleString('it-IT')}</text>` : ''}
        <text class="lab" x="${i * slot + slot / 2}" y="${H - 8}">${SHORT[+d.month.slice(5) - 1]}</text>
        <title>${esc(d.label)} · ${eur(d.totale)}</title></g>`;
    });
    $('#yearChart').innerHTML = `<svg class="ychart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Totale spese degli ultimi 12 mesi">${g}</svg>`;
  }
  $('#yearChart').addEventListener('click', e => {
    const c = e.target.closest('.col'); if (c) { month = c.dataset.m; load(); }
  });
  $('#yearChart').addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') { const c = e.target.closest('.col'); if (c) { e.preventDefault(); month = c.dataset.m; load(); } }
  });
  async function loadYear() { yearData = await api('/api/year'); renderYear(); }

  // ---------------------------------------------------------------- form riutilizzabile
  function formHTML({ withDate, e = {}, rate }) {
    const f = (name, label, type = 'number', extra = '', cls = '') =>
      `<div class="f ${cls}"><label for="${name}">${label}</label>
       <input id="${name}" name="${name}" type="${type}" ${type === 'number' ? 'step="0.01" min="0" inputmode="decimal"' : ''} value="${esc(e[name] ?? '')}" ${extra}></div>`;
    return `
      ${withDate ? f('date', 'Data', 'date', 'required', 'w3') : ''}
      ${f('luogo', 'Luogo', 'text', 'maxlength="120"', withDate ? 'w3' : 'w3')}
      ${f('descrizione', 'Descrizione', 'text', 'maxlength="300"', withDate ? 'w6' : 'w3')}
      ${f('km', 'Chilometri', 'number', '', '')}
      <div class="f"><label>Rimb. chil. (€/km)</label><input id="rate" readonly value="${(e.rate ?? rate).toFixed(4)}"></div>
      <div class="f"><label>Tot. rimb. chil.</label><input id="totkm" readonly value="€ 0,00"></div>
      ${MONEY.map(([k, l]) => f(k, l)).join('')}
      <div class="foot"><span class="sum">Totale voce <b id="totale">€ 0,00</b></span>
        <span class="err" id="ferr"></span>
        <button type="button" class="btn ghost" data-cancel>Annulla</button>
        <button type="submit" class="btn primary">Salva</button></div>`;
  }

  function wireCalc(form, rate) {
    const calc = () => {
      const g = n => parseFloat((form.elements[n].value || '0').replace(',', '.')) || 0;
      const r = parseFloat(form.elements.rate.value) || rate;
      const km = Math.round(g('km') * r * 100) / 100;
      form.elements.totkm.value = eur(km);
      $('#totale', form).textContent = eur(km + MONEY.reduce((s, [k]) => s + g(k), 0));
    };
    form.addEventListener('input', calc); calc();
  }

  function collect(form, date) {
    const d = {}; [...form.elements].forEach(el => { if (el.name) d[el.name] = el.value; });
    if (date) d.date = date;
    return d;
  }

  // ---------------------------------------------------------------- rendering
  function render() {
    const s = state, t = s.totals;
    $('#monthTitle').textContent = s.label;
    $('#nextM').disabled = month >= NOW_MONTH;
    $('#dlBtn').href = `/download/${month}.xlsx`;
    $('#stats').innerHTML = `
      <div class="stat"><small>Voci</small><strong data-n="${s.expenses.length}" data-f="int">0</strong></div>
      <div class="stat"><small>Chilometri</small><strong data-n="${t.km}" data-f="km">0</strong></div>
      <div class="stat"><small>Totale spese</small><strong data-n="${t.totale}" data-f="eur">0</strong></div>
      <div class="stat hl"><small>Da rimborsare</small><strong data-n="${t.da_rimborsare}" data-f="eur">0</strong></div>`;
    countUp();
    renderSplit();
    $('#heroSub').textContent = s.expenses.length
      ? `Ecco la situazione di ${s.label}: ${s.expenses.length} ${s.expenses.length === 1 ? 'voce registrata' : 'voci registrate'}.`
      : `Nessuna spesa registrata in ${s.label}.`;

    const groups = {};
    s.expenses.forEach(e => (groups[e.date] ||= []).push(e));
    const days = Object.keys(groups).sort();
    if (!days.length) {
      $('#days').innerHTML = `<div class="empty"><h3>Nessuna spesa in ${esc(s.label)}</h3>
        <p>Premi “Aggiungi spesa” per registrare la prima voce del mese.</p></div>`;
      return;
    }
    $('#days').innerHTML = days.map(d => {
      const list = groups[d], dayTot = list.reduce((a, e) => a + e.totale, 0);
      return `<article class="day" data-day="${d}">
        <div class="day-head"><h3>${esc(dayLabel(d))}</h3><span class="muted">${list.length} ${list.length === 1 ? 'voce' : 'voci'}</span>
          <span class="tot">${eur(dayTot)}</span></div>
        ${list.map(itemHTML).join('')}
        <div class="addmore" data-addmore><button type="button">＋ Aggiungi cosa nello stesso giorno</button></div>
      </article>`;
    }).join('');
  }

  function itemHTML(e) {
    const chips = [];
    if (e.km) chips.push(`<span class="chip"><b>${e.km}</b> km · ${eur(e.tot_km)}</span>`);
    MONEY.forEach(([k, l]) => { if (e[k]) chips.push(`<span class="chip">${l} <b>${eur(e[k])}</b></span>`); });
    return `<div class="item" data-id="${e.id}">
      <div class="what"><b>${esc(e.luogo) || '—'}</b><span>${esc(e.descrizione)}</span></div>
      <div class="chips">${chips.join('')}</div>
      <div class="amt">${eur(e.totale)}</div>
      <div class="acts"><button class="btn small" data-edit>Modifica</button>
        <button class="btn small danger" data-del>Elimina</button></div></div>`;
  }

  // ---------------------------------------------------------------- azioni
  $('#days').addEventListener('click', async ev => {
    const day = ev.target.closest('.day'); if (!day) return;
    if (ev.target.closest('[data-addmore] button')) {
      const box = $('[data-addmore]', day);
      if ($('form', day)) return;
      const form = document.createElement('form'); form.className = 'form';
      form.innerHTML = formHTML({ withDate: false, rate: state.rate });
      box.after(form); wireCalc(form, state.rate); form.elements.luogo.focus();
      $('[data-cancel]', form).onclick = () => form.remove();
      form.onsubmit = async e => {
        e.preventDefault();
        try { await api('/api/expenses', 'POST', collect(form, day.dataset.day)); toast('Voce aggiunta'); await load(); }
        catch (x) { $('#ferr', form).textContent = x.message; }
      };
    }
    const item = ev.target.closest('.item');
    if (item && ev.target.closest('[data-del]')) {
      if (!confirm('Eliminare questa voce?')) return;
      await api('/api/expenses/' + item.dataset.id, 'DELETE'); toast('Voce eliminata'); load();
    }
    if (item && ev.target.closest('[data-edit]')) {
      const e = state.expenses.find(x => x.id === item.dataset.id);
      const form = document.createElement('form'); form.className = 'form';
      form.innerHTML = formHTML({ withDate: true, e, rate: state.rate });
      item.replaceWith(form); wireCalc(form, state.rate);
      $('[data-cancel]', form).onclick = () => load();
      form.onsubmit = async x => {
        x.preventDefault();
        try { await api('/api/expenses/' + e.id, 'PUT', collect(form)); toast('Modifiche salvate'); await load(); }
        catch (err) { $('#ferr', form).textContent = err.message; }
      };
    }
  });

  function openModal(html) {
    const root = $('#modalRoot');
    root.innerHTML = `<div class="overlay"><div class="modal" role="dialog" aria-modal="true">${html}</div></div>`;
    const close = () => root.innerHTML = '';
    $('.overlay', root).addEventListener('mousedown', e => { if (e.target.classList.contains('overlay')) close(); });
    document.addEventListener('keydown', function esc_(e) { if (e.key === 'Escape') { close(); document.removeEventListener('keydown', esc_); } });
    return { root, close };
  }

  $('#addBtn').onclick = () => {
    const { root, close } = openModal(`<h2>Aggiungi spesa</h2><form class="form modalform" id="addForm"></form>`);
    const form = $('#addForm', root);
    form.innerHTML = formHTML({ withDate: true, rate: state.rate });
    const today = new Date(); const iso = new Date(today - today.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
    form.elements.date.value = iso.startsWith(month) ? iso : month + '-01';
    wireCalc(form, state.rate); form.elements.luogo.focus();
    $('[data-cancel]', form).onclick = close;
    form.onsubmit = async e => {
      e.preventDefault();
      try {
        const d = collect(form); await api('/api/expenses', 'POST', d); close();
        month = d.date.slice(0, 7); toast('Spesa aggiunta'); await load();
      } catch (x) { $('#ferr', form).textContent = x.message; }
    };
  };

  $('#setBtn').onclick = async () => {
    const s = await api('/api/settings');
    const { root, close } = openModal(`<h2>Impostazioni</h2>
      <form class="form modalform" id="setForm">
        <div class="f w3"><label>Rimborso chilometrico (€/km)</label>
          <input name="rate" type="number" step="0.0001" min="0.0001" value="${s.rate}" required></div>
        <div class="f w3"><label>Anticipo (€)</label>
          <input name="anticipo" type="number" step="0.01" min="0" value="${s.anticipo || ''}" placeholder="0,00"></div>
        <div class="f w6"><label style="text-transform:none;letter-spacing:0;font-size:13.5px;display:flex;gap:10px;align-items:center">
          <input type="checkbox" name="apply_current_month" style="width:auto"> Applica la nuova tariffa anche alle spese del mese in corso</label>
          <span class="muted" style="font-size:13px">Le spese dei mesi passati mantengono la tariffa con cui sono state registrate.</span></div>
        <div class="foot"><span class="err" id="ferr"></span>
          <button type="button" class="btn ghost" data-cancel>Annulla</button>
          <button type="submit" class="btn primary">Salva</button></div></form>`);
    const form = $('#setForm', root);
    $('[data-cancel]', form).onclick = close;
    form.onsubmit = async e => {
      e.preventDefault();
      try {
        await api('/api/settings', 'PUT', { rate: form.elements.rate.value, anticipo: form.elements.anticipo.value,
          apply_current_month: form.elements.apply_current_month.checked });
        close(); toast('Impostazioni salvate'); load();
      } catch (x) { $('#ferr', form).textContent = x.message; }
    };
  };

  $('#photoBtn').onclick = async () => {
    const slots = await api('/api/media');
    const draw = list => list.map(s => `<div class="slot" data-slot="${s.slot}">
        <div class="thumb">${s.version ? `<img src="/media/${s.slot}?v=${s.version}" alt="">` : '<span class="muted">Nessuna foto</span>'}</div>
        <div class="sl-info"><b>${esc(s.label)}</b>
          <div class="row"><label class="btn small primary">${s.version ? 'Sostituisci' : 'Carica foto'}<input type="file" accept="image/*" hidden></label>
            ${s.version ? '<button class="btn small danger" data-rm>Rimuovi</button>' : ''}</div></div></div>`).join('');
    const { root } = openModal(`<h2>Foto del sito</h2>
      <p class="muted" style="margin-top:-8px">Le foto compaiono subito nella home pubblica. Usa immagini di cui hai i diritti (le tue o quelle dei prodotti che ti hanno fornito le aziende).</p>
      <div id="slots" class="slots">${draw(slots)}</div>
      <div class="foot" style="margin-top:16px;display:flex;justify-content:flex-end"><button class="btn" data-cancel>Chiudi</button></div>`);
    $('[data-cancel]', root).onclick = () => root.innerHTML = '';
    const refresh = async () => { $('#slots', root).innerHTML = draw(await api('/api/media')); };
    root.addEventListener('change', async e => {
      if (e.target.type !== 'file' || !e.target.files[0]) return;
      const slot = e.target.closest('.slot').dataset.slot, fd = new FormData(); fd.append('file', e.target.files[0]);
      e.target.closest('label').firstChild.textContent = 'Carico…';
      const r = await fetch('/api/media/' + slot, { method: 'POST', headers: { 'X-CSRF-Token': CSRF }, body: fd, credentials: 'same-origin' });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) toast(d.error || 'Caricamento non riuscito'); else toast('Foto aggiornata');
      refresh();
    });
    root.addEventListener('click', async e => {
      if (!e.target.closest('[data-rm]')) return;
      if (!confirm('Rimuovere questa foto?')) return;
      await api('/api/media/' + e.target.closest('.slot').dataset.slot, 'DELETE'); toast('Foto rimossa'); refresh();
    });
  };

  $('#prevM').onclick = () => { month = shiftMonth(month, -1); load(); };
  $('#nextM').onclick = () => { if (month < NOW_MONTH) { month = shiftMonth(month, 1); load(); } };

  // ---------------------------------------------------------------- archivio + notifiche
  async function loadArchive() {
    const months = await api('/api/months');
    $('#archive').innerHTML = months.map(m => `<div class="mcard">
      <h3>${esc(m.label)}</h3>
      <div class="meta">${m.count} ${m.count === 1 ? 'voce' : 'voci'} · ${eur(m.totale)}</div>
      <div class="row"><span class="tag ${m.closed ? 'ok' : ''}">${m.closed ? 'Chiuso' : 'In corso'}</span>
        ${m.emailed ? '<span class="tag ok">Email inviata</span>' : ''}
        <span style="flex:1"></span>
        <a class="btn small" href="/download/${m.month}.xlsx">⬇ Excel</a>
        <button class="btn small ghost" data-open="${m.month}">Apri</button></div></div>`).join('');
  }
  $('#archive').addEventListener('click', e => {
    const b = e.target.closest('[data-open]'); if (b) { month = b.dataset.open; load(); scrollTo({ top: 0, behavior: 'smooth' }); }
  });

  let notifs = [];
  async function loadNotifs() {
    notifs = await api('/api/notifications');
    const unread = notifs.filter(n => !n.read);
    const badge = $('#bellBadge'); badge.textContent = unread.length; badge.classList.toggle('hidden', !unread.length);
    $('#banner').innerHTML = unread.map(n => `<div class="banner"><span class="dot"></span>
      <div class="txt"><b>La nota spese di ${esc(n.label)} è pronta.</b>
        <span class="muted">${n.emailed ? 'Te l’abbiamo inviata anche per email.' : (MAIL_OK ? 'Invio email in corso…' : 'Email non configurata sul server.')}</span></div>
      <a class="btn primary small" href="/download/${n.month}.xlsx" data-read="${n.month}">⬇ Scarica Excel</a>
      <button class="btn small ghost" data-dismiss="${n.month}">Segna come letta</button></div>`).join('');
    $('#notifList').innerHTML = notifs.length ? notifs.map(n => `<div class="notif ${n.read ? '' : 'unread'}">
      <b>Nota spese ${esc(n.label)}</b>
      <span class="muted" style="font-size:13px">${n.emailed ? 'Email inviata' : 'Email non ancora inviata'}${n.email_error ? ' · errore: ' + esc(n.email_error) : ''}</span>
      <div><a class="btn small" href="/download/${n.month}.xlsx" data-read="${n.month}">⬇ Scarica Excel</a></div></div>`).join('')
      : '<div class="notif muted">Nessuna notifica. A fine mese troverai qui la nota spese pronta.</div>';
  }
  document.addEventListener('click', async e => {
    const r = e.target.closest('[data-read],[data-dismiss]');
    if (r) { const m = r.dataset.read || r.dataset.dismiss; await api(`/api/notifications/${m}/read`, 'POST'); setTimeout(loadNotifs, 400); }
    if (!e.target.closest('#bellDrop') && !e.target.closest('#bellBtn')) $('#bellDrop').classList.add('hidden');
  });
  $('#bellBtn').onclick = () => $('#bellDrop').classList.toggle('hidden');

  async function load() {
    state = await api('/api/month/' + month);
    render(); loadArchive(); loadNotifs(); loadYear();
  }
  load();
  setInterval(loadNotifs, 5 * 60 * 1000);
})();
