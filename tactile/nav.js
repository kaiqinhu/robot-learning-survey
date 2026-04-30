/* === Tactile Sub-site Navigation === */
(function () {
  'use strict';

  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  const NAV_PAGES = [
    { href: '../index.html',       label: '\u2190 Main',     accent: null, color: '#57534e' },
    { href: 'index.html',          label: 'Home',           accent: null, color: '#0e7490' },
    { href: 'p1-sensing.html',     label: 'Sensing',        accent: null, color: '#7c3aed' },
    { href: 'p2-soc.html',         label: 'SoC',            accent: null, color: '#d97706' },
    { href: 'p3-model-loop.html',  label: 'Model+FWM',     accent: null, color: '#3b5bdb' },
    { href: 'p5-benchmark.html',   label: 'Benchmark',      accent: null, color: '#059669' },
    { href: 'p6-ttt.html',         label: 'TTT',            accent: null, color: '#8b5cf6' },
    { href: 'p7-materials-companies.html', label: 'Flex Sensor', accent: null, color: '#9d174d' },
  ];

  function renderNav() {
    const nav = document.getElementById('main-nav');
    if (!nav) return;

    const currentPath = location.pathname.split('/').pop() || 'index.html';

    const links = NAV_PAGES.map(p => {
      const isActive = currentPath === p.href.replace(/^\.\.\//, '');
      let activeStyle = '';
      if (isActive && p.color) activeStyle = ` style="background:${p.color}"`;
      const cls = isActive ? ' class="active"' : '';
      return `<a href="${p.href}"${cls}${activeStyle}>${esc(p.label)}</a>`;
    }).join('\n    ');

    nav.innerHTML = `
  <span class="logo">Tactile & Embodied AI 2026</span>
  <button class="nav-burger" aria-label="Menu"><span></span></button>
  <div class="nav-links">
    ${links}
  </div>`;

    const burger = nav.querySelector('.nav-burger');
    const linksEl = nav.querySelector('.nav-links');
    if (burger && linksEl) {
      burger.addEventListener('click', () => {
        burger.classList.toggle('open');
        linksEl.classList.toggle('open');
      });
      linksEl.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
          burger.classList.remove('open');
          linksEl.classList.remove('open');
        });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderNav);
  } else {
    renderNav();
  }
})();
