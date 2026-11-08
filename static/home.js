(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // nav che si solidifica + menu mobile
  const nav = $('#hnav'), menu = $('#menu'), burger = $('#burger');
  const onScroll = () => nav.classList.toggle('solid', scrollY > 30);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  burger.addEventListener('click', () => {
    const open = menu.classList.toggle('open'); burger.setAttribute('aria-expanded', open);
  });
  menu.addEventListener('click', e => { if (e.target.tagName === 'A') { menu.classList.remove('open'); burger.setAttribute('aria-expanded', false); } });

  // comparsa allo scorrimento
  const items = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    items.forEach(i => io.observe(i));
  } else items.forEach(i => i.classList.add('in'));

  // numeri che salgono
  const fmt = { plain: n => String(Math.round(n)), x: n => '×' + Math.round(n) };
  document.querySelectorAll('[data-n]').forEach(el => {
    const to = +el.dataset.n, f = fmt[el.dataset.f] || fmt.plain;
    if (reduce) { el.textContent = f(to); return; }
    const run = () => {
      const t0 = performance.now(), dur = 1400;
      const step = now => {
        const k = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - k, 4);
        el.textContent = f(to * e); if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    };
    setTimeout(run, 500);
  });
})();
