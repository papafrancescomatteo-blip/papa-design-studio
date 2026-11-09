(() => {
  const CSRF = document.body.dataset.csrf;
  const $ = (s, r = document) => r.querySelector(s);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  const CATS = ['Minipiscine', 'Vasche', 'Docce e rubinetteria', 'Saune e bagno turco', 'Sanitari', 'Accessori e complementi'].map(c => [c, c]);
  const TYPES = {
    catalog: {
      title: 'Prodotti', add: 'Aggiungi prodotto', photo: true, search: true,
      hint: 'Il catalogo completo mostrato nella pagina Prodotti. Raggruppati automaticamente per azienda e categoria.',
      fields: [
        ['title', 'Nome prodotto', 'text', 'w3', true], ['brand', 'Azienda / marchio (scrivi sempre uguale)', 'text', 'w3'],
        ['category', 'Categoria', 'select', 'w6', false, CATS],
        ['text', 'Breve descrizione', 'textarea', 'w6'], ['url', 'Link (facoltativo, https://…)', 'text', 'w6']],
      row: i => [i.title, [i.brand, i.category].filter(Boolean).join(' · ')]
    },
    news: {
      title: 'Riviste e Cersaie', add: 'Aggiungi articolo / evento', photo: true,
      hint: 'Servizi su riviste, presentazioni a Cersaie, eventi e fiere. Indica il tipo per farlo comparire nel filtro della home.',
      fields: [
        ['kind', 'Tipo', 'select', 'w3', false, [['Rivista', 'Rivista'], ['Stampa', 'Stampa (quotidiani)'], ['Cersaie', 'Cersaie'], ['Evento', 'Evento'], ['Web', 'Web']]],
        ['source', 'Testata / luogo (es. Domus, Cersaie · Bologna)', 'text', 'w3'],
        ['title', 'Titolo', 'text', 'w3', true], ['when', 'Data (es. Settembre 2025)', 'text', 'w3'],
        ['text', 'Breve descrizione', 'textarea', 'w6'], ['url', 'Link all’articolo (facoltativo, https://…)', 'text', 'w6']],
      row: i => [i.title, [i.kind, i.source, i.when].filter(Boolean).join(' · ')]
    },
    award: {
      title: 'Premi', add: 'Aggiungi premio', photo: false,
      hint: 'I premi compaiono nell’ordine mostrato qui sotto: usa le frecce per spostarli.',
      fields: [['year', 'Anno (es. 2019 o 2017 · 2018)', 'text', 'w3'], ['title', 'Premio', 'text', 'w3', true], ['detail', 'Progetto / dettaglio', 'text', 'w6']],
      row: i => [i.title, [i.year, i.detail].filter(Boolean).join(' · ')]
    },
    timeline: {
      title: 'Percorso', add: 'Aggiungi tappa', photo: false,
      hint: 'Le tappe della storia di Claudio Papa, in ordine cronologico: usa le frecce per riordinarle.',
      fields: [['year', 'Anno / periodo', 'text', 'w3'], ['text', 'Cosa è successo', 'textarea', 'w6', true]],
      row: i => [i.text, i.year]
    }
  };

  let tab = 'catalog', data = { items: [], portrait: null };

  async function api(url, method = 'GET', body) {
    const r = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': CSRF },
      body: body ? JSON.stringify(body) : undefined, credentials: 'same-origin' });
    if (r.status === 401) { location.href = '/login'; return; }
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || 'Errore');
    return d;
  }
  async function upload(slot, file) {
    const fd = new FormData(); fd.append('file', file);
    const r = await fetch('/api/media/' + slot, { method: 'POST', headers: { 'X-CSRF-Token': CSRF }, body: fd, credentials: 'same-origin' });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || 'Caricamento non riuscito');
  }
  function toast(msg) {
    const t = document.createElement('div'); t.className = 'toast'; t.textContent = msg;
    document.body.appendChild(t); setTimeout(() => t.remove(), 2600);
  }
  function openModal(html) {
    const root = $('#modalRoot');
    root.innerHTML = `<div class="overlay"><div class="modal" role="dialog" aria-modal="true">${html}</div></div>`;
    const close = () => root.innerHTML = '';
    $('.overlay', root).addEventListener('mousedown', e => { if (e.target.classList.contains('overlay')) close(); });
    return { root, close };
  }

  // ------------------------------------------------------------ rendering
  function render() {
    document.querySelectorAll('#tabs button').forEach(b => b.classList.toggle('on', b.dataset.t === tab));
    const p = $('#panel');
    if (tab === 'portrait') {
      p.innerHTML = `<div class="ahead"><h2>Ritratto di Claudio Papa</h2></div>
        <p class="hint" style="margin:-4px 0 14px">Compare nella sezione “Chi è” della home. Meglio una foto verticale (4:5). Usa una foto di cui hai i diritti.</p>
        <div class="portrait-box"><div class="th">${data.portrait ? `<img src="/media/ritratto?v=${data.portrait}" alt="">` : 'Nessuna foto'}</div>
          <div><label class="btn primary">${data.portrait ? 'Sostituisci foto' : 'Carica foto'}<input id="portraitFile" type="file" accept="image/*" hidden></label>
          ${data.portrait ? '<button class="btn danger" id="portraitRm">Rimuovi</button>' : ''}</div></div>`;
      return;
    }
    const T = TYPES[tab], list = data.items.filter(i => i.type === tab);
    p.innerHTML = `<div class="ahead"><h2>${T.title}</h2><span class="muted">${list.length}</span><span class="sp"></span>
      <button class="btn primary" id="addItem">＋ ${T.add}</button></div>
      <p class="hint" style="margin:-4px 0 14px">${esc(T.hint)}</p>
      ${list.length > 8 ? '<input id="q" class="search" placeholder="Cerca…" aria-label="Cerca">' : ''}
      <div class="alist">${list.map((i, n) => {
        const [a, b] = T.row(i);
        return `<div class="arow" data-id="${i.id}">
          ${T.photo ? `<div class="th">${i.version ? `<img src="/media/c-${i.id}?v=${i.version}" alt="">` : 'foto'}</div>` : ''}
          <div class="tx"><b>${esc(a)}</b><span>${esc(b)}</span></div>
          <div class="acts"><button class="btn small" data-mv="-1" ${n === 0 ? 'disabled' : ''} title="Sposta su">↑</button>
            <button class="btn small" data-mv="1" ${n === list.length - 1 ? 'disabled' : ''} title="Sposta giù">↓</button>
            <button class="btn small" data-edit>Modifica</button><button class="btn small danger" data-del>Elimina</button></div></div>`;
      }).join('') || '<div class="empty"><h3>Ancora niente qui</h3><p>Premi il pulsante per aggiungere il primo elemento.</p></div>'}</div>`;
  }

  async function load() { data = await api('/api/content'); render(); }

  // ------------------------------------------------------------ form
  function openForm(item) {
    const T = TYPES[tab], editing = !!item;
    const input = ([name, label, type, cls, req, opts]) => {
      let v = item ? item[name] : '';
      if (name === 'items') v = (v || []).join('\n');
      if (type === 'textarea') return `<div class="f ${cls}"><label>${label}</label><textarea name="${name}">${esc(v)}</textarea></div>`;
      if (type === 'select') return `<div class="f ${cls}"><label>${label}</label><select name="${name}">${opts.map(([k, l]) => `<option value="${k}" ${v === k ? 'selected' : ''}>${l}</option>`).join('')}</select></div>`;
      return `<div class="f ${cls}"><label>${label}${req ? ' *' : ''}</label><input name="${name}" type="text" value="${esc(v)}" ${req ? 'required' : ''}></div>`;
    };
    const { root, close } = openModal(`<h2>${editing ? 'Modifica' : T.add}</h2>
      <form class="form modalform" id="cf">
        ${T.fields.map(input).join('')}
        ${T.photo ? `<div class="f w6"><label>Foto (facoltativa)</label><div class="photo-edit">
            <div class="th">${item && item.version ? `<img src="/media/c-${item.id}?v=${item.version}" alt="">` : 'nessuna'}</div>
            <div><label class="btn small">Scegli foto<input type="file" name="photo" accept="image/*" hidden></label>
            ${item && item.version ? '<button type="button" class="btn small danger" id="rmPhoto">Rimuovi foto</button>' : ''}
            <div class="hint" id="pname" style="margin-top:6px">Usa foto di cui hai i diritti.</div></div></div></div>` : ''}
        <div class="foot"><span class="err" id="ferr"></span>
          <button type="button" class="btn ghost" data-cancel>Annulla</button><button class="btn primary" type="submit">Salva</button></div>
      </form>`);
    const form = $('#cf', root);
    $('[data-cancel]', form).onclick = close;
    const file = form.elements.photo;
    if (file) file.onchange = () => { $('#pname', form).textContent = file.files[0] ? file.files[0].name : ''; };
    const rm = $('#rmPhoto', form);
    if (rm) rm.onclick = async () => { await api('/api/media/c-' + item.id, 'DELETE'); toast('Foto rimossa'); close(); load(); };
    form.onsubmit = async e => {
      e.preventDefault();
      const body = {}; T.fields.forEach(([n]) => body[n] = form.elements[n].value);
      try {
        let id = item && item.id;
        if (editing) await api('/api/content/' + id, 'PUT', body);
        else id = (await api('/api/content/' + tab, 'POST', body)).id;
        if (file && file.files[0]) await upload('c-' + id, file.files[0]);
        close(); toast('Salvato'); load();
      } catch (x) { $('#ferr', form).textContent = x.message; }
    };
  }

  // ------------------------------------------------------------ eventi
  $('#tabs').addEventListener('click', e => { const b = e.target.closest('button'); if (b) { tab = b.dataset.t; render(); } });
  $('#panel').addEventListener('click', async e => {
    if (e.target.closest('#addItem')) return openForm(null);
    if (e.target.closest('#portraitRm')) { if (confirm('Rimuovere il ritratto?')) { await api('/api/media/ritratto', 'DELETE'); toast('Ritratto rimosso'); load(); } return; }
    const row = e.target.closest('.arow'); if (!row) return;
    const id = row.dataset.id, item = data.items.find(i => i.id === id);
    if (e.target.closest('[data-edit]')) openForm(item);
    if (e.target.closest('[data-del]')) { if (confirm('Eliminare definitivamente questa voce?')) { await api('/api/content/' + id, 'DELETE'); toast('Eliminato'); load(); } }
    const mv = e.target.closest('[data-mv]');
    if (mv) { await api(`/api/content/${id}/move`, 'POST', { dir: +mv.dataset.mv }); load(); }
  });
  $('#panel').addEventListener('input', e => {
    if (e.target.id !== 'q') return;
    const q = e.target.value.toLowerCase();
    document.querySelectorAll('.arow').forEach(r => r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none');
  });
  $('#panel').addEventListener('change', async e => {
    if (e.target.id !== 'portraitFile' || !e.target.files[0]) return;
    try { await upload('ritratto', e.target.files[0]); toast('Ritratto aggiornato'); load(); } catch (x) { toast(x.message); }
  });

  load();
})();
