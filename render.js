/* === Robot Learning Survey 2026 — Data-driven Renderer === */
(function () {
  'use strict';

  let _cache = null;

  /** Load and cache papers.json (works on both http:// and file://) */
  async function loadData() {
    if (_cache) return _cache;
    // Check if data was pre-loaded via <script> tag
    if (window.SURVEY_DATA) {
      _cache = window.SURVEY_DATA;
      return _cache;
    }
    try {
      const resp = await fetch('papers.json');
      _cache = await resp.json();
    } catch (e) {
      // file:// fallback: synchronous XHR
      const xhr = new XMLHttpRequest();
      xhr.open('GET', 'papers.json', false);
      xhr.send();
      if (xhr.status === 0 || xhr.status === 200) {
        _cache = JSON.parse(xhr.responseText);
      } else {
        console.error('Failed to load papers.json', e);
        _cache = { papers: [], timeline: [], citations: [] };
      }
    }
    return _cache;
  }

  /** Escape HTML entities */
  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  /** Determine the CSS topic class for a paper */
  function topicClass(paper, pageId) {
    const t = paper.topic || '';
    const map = { vla: 'vla', wam: 'wam', rl: 'rl', diff: 'diff', hybrid: 'hybrid', unitree: 'unitree' };
    if (map[t]) return map[t];
    // Fallback: infer from page
    const pageMap = { p1: '', p2: 'wam', p3: 'rl', p4: 'diff', p5: 'hybrid', p6: 'unitree' };
    return pageMap[pageId] || '';
  }

  /** Generate card HTML for a single paper */
  function cardHTML(p, pageId) {
    const cls = topicClass(p, pageId);
    const tags = (p.tags || []).map(t => `<span class="tag">${esc(t)}</span>`).join('');
    const meta = p.meta ? `<div class="meta">${esc(p.meta)}</div>` : '';
    const desc = p.description ? `<p>${p.description}</p>` : '';
    const diagram = p.diagram ? `<div class="mini-diagram">${esc(p.diagram)}</div>` : '';
    const insight = p.insight ? `<div class="insight">${p.insight}</div>` : '';

    let link = '';
    if (p.url) {
      const label = p.id && /^\d{4}\./.test(p.id) ? `arXiv ${p.id} →` : 'Paper →';
      link = `<a href="${esc(p.url)}" target="_blank" class="paper-link">${label}</a>`;
    }

    return `<div class="card${cls ? ' ' + cls : ''}">
      ${tags}
      <h4>${p.title}</h4>
      ${meta}${desc}${diagram}${insight}${link}
    </div>`;
  }

  /** Render card grid into a container element */
  function renderCards(container, papers, pageId) {
    container.innerHTML = papers.map(p => cardHTML(p, pageId)).join('\n');
  }

  /** Render timeline items into a container element */
  function renderTimeline(container, items) {
    const accentAttr = container.dataset.accent;
    container.innerHTML = items.map(item => {
      const yearStyle = accentAttr ? ` style="color:var(--accent-${accentAttr})"` : '';
      return `<div class="timeline-item">
        <span class="year"${yearStyle}>${esc(item.year)}</span>
        <h4>${item.title}</h4>
        <p>${item.description}</p>
      </div>`;
    }).join('\n');
  }

  /**
   * Filter papers for a given container based on data-* attributes:
   *   data-page="p1"          — papers on this page
   *   data-section="vla-rl"   — papers in this section (optional)
   *   data-ids="2604.01570,2604.01618" — explicit paper IDs (highest priority)
   */
  function filterPapers(papers, dataset) {
    let result = papers;

    // Explicit IDs take priority
    if (dataset.ids) {
      const ids = new Set(dataset.ids.split(',').map(s => s.trim()));
      return papers.filter(p => ids.has(p.id));
    }

    // Filter by page
    if (dataset.page) {
      const pg = dataset.page;
      result = result.filter(p => (p.pages || []).includes(pg));
    }

    // Filter by section
    if (dataset.section) {
      const sec = dataset.section;
      result = result.filter(p => p.section === sec);
    }

    // Filter by topic
    if (dataset.topic) {
      const topic = dataset.topic;
      result = result.filter(p => p.topic === topic);
    }

    // Exclude foundation-only papers unless explicitly requested
    if (dataset.foundation !== 'true') {
      result = result.filter(p => !p.foundation);
    }

    return result;
  }

  /**
   * Return { nodes, edges } for p7 citation graph.
   * nodes: paper objects with id, shortTitle, topic, authors, institution, year, description, url
   * edges: { source, target } pairs
   */
  function loadGraphData(data) {
    const nodes = data.papers.map(p => ({
      id: p.id,
      shortTitle: p.shortTitle || p.title,
      topic: p.topic || 'unknown',
      authors: p.authors || '',
      institution: p.institution || '',
      year: p.year || 0,
      description: p.description || '',
      url: p.url || '',
      foundation: !!p.foundation,
      pages: p.pages || []
    }));
    const edges = (data.citations || []).map(e => ({ source: e.source, target: e.target }));
    return { nodes, edges };
  }

  /** Navigation pages config — single source of truth */
  const NAV_PAGES = [
    { href: 'index.html',              label: 'Home',      accent: null },
    { href: 'survey.html',             label: 'Survey',    accent: null, color: '#2b6cb0' },
    { href: 'p1-vla.html',             label: 'VLA',       accent: 'vla' },
    { href: 'p2-wam.html',             label: 'WAM',       accent: 'wam' },
    { href: 'p3-rl-sim2real.html',     label: 'RL',        accent: 'rl' },
    { href: 'p4-diffusion.html',       label: 'Diffusion', accent: 'diff' },
    { href: 'p5-hybrid.html',          label: 'Hybrid',    accent: 'hybrid' },
    { href: 'p6-unitree.html',         label: 'Unitree',   accent: 'unitree' },
    { href: 'p7-citation-graph.html',  label: 'Graph',     accent: null, color: '#8b5cf6' },
  ];

  /** Render nav bar into <nav id="main-nav"> */
  function renderNav() {
    const nav = document.getElementById('main-nav');
    if (!nav) return;

    const currentPath = location.pathname.split('/').pop() || 'index.html';

    const links = NAV_PAGES.map(p => {
      const isActive = currentPath === p.href;
      let activeStyle = '';
      if (isActive) {
        if (p.accent) activeStyle = ` style="background:var(--accent-${p.accent})"`;
        else if (p.color) activeStyle = ` style="background:${p.color}"`;
      }
      const cls = isActive ? ' class="active"' : '';
      return `<a href="${p.href}"${cls}${activeStyle}>${esc(p.label)}</a>`;
    }).join('\n    ');

    nav.innerHTML = `
  <span class="logo">Robot Learning 2026</span>
  <button class="nav-burger" aria-label="Menu"><span></span></button>
  <div class="nav-links">
    ${links}
  </div>`;

    // Hamburger toggle
    const burger = nav.querySelector('.nav-burger');
    const linksEl = nav.querySelector('.nav-links');
    if (burger && linksEl) {
      burger.addEventListener('click', () => {
        burger.classList.toggle('open');
        linksEl.classList.toggle('open');
      });
      // Close menu when a link is clicked
      linksEl.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
          burger.classList.remove('open');
          linksEl.classList.remove('open');
        });
      });
    }
  }

  /** Main init — auto-scan and render all data-driven containers */
  async function init() {
    renderNav();
    const data = await loadData();

    // Render card grids: <div class="card-grid" data-page="p1" ...>
    document.querySelectorAll('.card-grid[data-page], .card-grid[data-ids]').forEach(el => {
      const papers = filterPapers(data.papers, el.dataset);
      renderCards(el, papers, el.dataset.page);
    });

    // Render timelines: <div class="timeline" data-page="p1">
    document.querySelectorAll('.timeline[data-page]').forEach(el => {
      const pg = el.dataset.page;
      const items = (data.timeline || []).filter(t => t.page === pg);
      renderTimeline(el, items);
    });
  }

  // Auto-run on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose for p7 and other custom use
  window.SurveyData = { loadData, loadGraphData, renderCards, renderTimeline, filterPapers };
})();
