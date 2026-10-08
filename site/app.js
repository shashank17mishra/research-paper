/**
 * Daily Tech Intelligence - Client-side Dashboard Application
 * Zero-backend, lightning fast paper browsing, searching, and filtering.
 */

let allPapers = [];
let appStats = {};
let activeCategory = 'all';
let searchQuery = '';
let currentSort = 'score';

document.addEventListener('DOMContentLoaded', () => {
  initApp();
});

async function initApp() {
  await loadData();
  setupEventListeners();
  renderStats();
  renderPapers();
  renderLatestInfographic();
}

async function loadData() {
  try {
    // Attempt loading from site/data/ or fallback paths
    const [papersRes, statsRes] = await Promise.allSettled([
      fetch('data/papers.json'),
      fetch('data/statistics.json')
    ]);

    if (papersRes.status === 'fulfilled' && papersRes.value.ok) {
      allPapers = await papersRes.value.json();
    } else {
      // Fallback try ../data/papers.json if opened in some environments
      const fb = await fetch('../data/papers.json');
      if (fb.ok) allPapers = await fb.json();
    }

    if (statsRes.status === 'fulfilled' && statsRes.value.ok) {
      appStats = await statsRes.value.json();
    } else {
      const fbs = await fetch('../data/statistics.json');
      if (fbs.ok) appStats = await fbs.json();
    }
  } catch (err) {
    console.warn('Notice loading local dataset:', err);
  }
}

function setupEventListeners() {
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value.trim().toLowerCase();
      renderPapers();
    });
  }

  const sortSelect = document.getElementById('sort-select');
  if (sortSelect) {
    sortSelect.addEventListener('change', (e) => {
      currentSort = e.target.value;
      renderPapers();
    });
  }

  const pillButtons = document.querySelectorAll('.pill-btn');
  pillButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      pillButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCategory = btn.getAttribute('data-category');
      renderPapers();
    });
  });
}

function renderStats() {
  const totalPapersEl = document.getElementById('stat-total-papers');
  const totalRunsEl = document.getElementById('stat-total-runs');
  const totalCatsEl = document.getElementById('stat-total-cats');
  const lastUpdatedEl = document.getElementById('stat-last-updated');

  const count = allPapers.length || (appStats.total_papers || 0);
  if (totalPapersEl) totalPapersEl.textContent = count;
  if (totalRunsEl) totalRunsEl.textContent = `${appStats.total_runs || 1}d`;
  
  const cats = appStats.categories_breakdown ? Object.keys(appStats.categories_breakdown).length : 6;
  if (totalCatsEl) totalCatsEl.textContent = cats;

  if (lastUpdatedEl) {
    lastUpdatedEl.textContent = appStats.last_run_date || 'Today';
  }
}

function getFilteredPapers() {
  return allPapers.filter(paper => {
    // Category match
    if (activeCategory !== 'all') {
      const topicLower = (paper.primary_topic || '').toLowerCase();
      const cats = (paper.categories || []).map(c => c.toLowerCase());
      const catMatch = topicLower.includes(activeCategory.toLowerCase()) ||
                       cats.some(c => c.includes(activeCategory.toLowerCase()));
      if (!catMatch) return false;
    }

    // Search query match
    if (searchQuery) {
      const title = (paper.title || '').toLowerCase();
      const authors = (paper.authors || []).join(' ').toLowerCase();
      const abstract = (paper.abstract || '').toLowerCase();
      const concepts = (paper.key_concepts || []).join(' ').toLowerCase();
      const date = (paper.published_date || '').toLowerCase();

      const inTitle = title.includes(searchQuery);
      const inAuthors = authors.includes(searchQuery);
      const inAbstract = abstract.includes(searchQuery);
      const inConcepts = concepts.includes(searchQuery);
      const inDate = date.includes(searchQuery);

      if (!inTitle && !inAuthors && !inAbstract && !inConcepts && !inDate) {
        return false;
      }
    }

    return true;
  }).sort((a, b) => {
    if (currentSort === 'date') {
      return new Date(b.published_date || 0) - new Date(a.published_date || 0);
    }
    // Default score
    return (b.relevance_score || 0) - (a.relevance_score || 0);
  });
}

function renderPapers() {
  const feedEl = document.getElementById('papers-feed');
  const countEl = document.getElementById('results-count');
  if (!feedEl) return;

  const filtered = getFilteredPapers();
  if (countEl) {
    countEl.textContent = `${filtered.length} papers`;
  }

  if (filtered.length === 0) {
    feedEl.innerHTML = `
      <div style="text-align: center; padding: 48px 24px; color: var(--text-muted); background: var(--bg-card); border-radius: var(--radius-md); border: 1px solid var(--border-color);">
        <h3>No research papers found</h3>
        <p style="margin-top: 8px;">Try clearing search keywords or switching category filters.</p>
      </div>
    `;
    return;
  }

  feedEl.innerHTML = filtered.map((paper, idx) => {
    const aid = paper.arxiv_id || '';
    const title = paper.title || 'Untitled Paper';
    const authors = (paper.authors || []).join(', ');
    const score = (paper.relevance_score || 0).toFixed(2);
    const pubDate = paper.published_date ? paper.published_date.substring(0, 10) : 'Recent';
    const summary = paper.summary || paper.abstract || '';
    const topic = paper.primary_topic || 'AI';
    const concepts = (paper.key_concepts || []).map(c => `<span class="concept-chip">${escapeHtml(c)}</span>`).join('');

    const insights = paper.insights || {};
    const hasInsights = Object.keys(insights).length > 0;
    const cardId = `paper-card-${idx}`;

    return `
      <article class="paper-card" id="${cardId}">
        <div class="paper-card-header">
          <h3 class="paper-title">${escapeHtml(title)}</h3>
          <span class="relevance-badge">Score: ${score}</span>
        </div>

        <div class="paper-meta">
          <span>📅 ${escapeHtml(pubDate)}</span>
          <span>🏷️ ${escapeHtml(topic)}</span>
          <span>👥 ${escapeHtml(authors)}</span>
        </div>

        <p class="paper-summary">${escapeHtml(summary)}</p>

        ${concepts ? `<div class="concepts-row">${concepts}</div>` : ''}

        ${hasInsights ? `
          <button class="insights-toggle" onclick="toggleInsights('${cardId}-panel')">
            <span>🔬 Deep Technical Insights</span>
          </button>
          <div class="insights-panel" id="${cardId}-panel">
            <div class="insights-grid">
              <div class="insight-item">
                <h5>Problem</h5>
                <p>${escapeHtml(insights.problem || 'Not specified.')}</p>
              </div>
              <div class="insight-item">
                <h5>Approach</h5>
                <p>${escapeHtml(insights.approach || 'Not specified.')}</p>
              </div>
              <div class="insight-item">
                <h5>Key Innovation</h5>
                <p>${escapeHtml(insights.key_innovation || 'Not specified.')}</p>
              </div>
              <div class="insight-item">
                <h5>Results</h5>
                <p>${escapeHtml(insights.results || 'Not specified.')}</p>
              </div>
              <div class="insight-item">
                <h5>Applications</h5>
                <p>${escapeHtml(insights.applications || 'Not specified.')}</p>
              </div>
              <div class="insight-item">
                <h5>Limitations</h5>
                <p>${escapeHtml(insights.limitations || 'Not specified.')}</p>
              </div>
            </div>
          </div>
        ` : ''}

        <div class="paper-actions">
          <span style="font-size: 0.8rem; color: var(--text-dim);">arXiv ID: ${escapeHtml(aid)}</span>
          <div class="link-buttons">
            <a href="${paper.url || '#'}" target="_blank" rel="noopener" class="btn-link btn-arxiv">Read on arXiv ↗</a>
            ${paper.pdf_url ? `<a href="${paper.pdf_url}" target="_blank" rel="noopener" class="btn-link btn-pdf">PDF ↗</a>` : ''}
          </div>
        </div>
      </article>
    `;
  }).join('');
}

function toggleInsights(panelId) {
  const panel = document.getElementById(panelId);
  if (panel) {
    panel.classList.toggle('open');
  }
}

function renderLatestInfographic() {
  const infoImg = document.getElementById('daily-infographic-img');
  if (!infoImg) return;
  if (appStats.last_run_date) {
    const [y, m, d] = appStats.last_run_date.split('-');
    // Try site-local reports path first, fallback to parent relative path
    infoImg.src = `reports/${y}/${m}/${d}/infographic.png`;
    infoImg.onerror = () => {
      infoImg.src = `../reports/${y}/${m}/${d}/infographic.png`;
      infoImg.onerror = () => {
        const wrap = document.getElementById('infographic-container');
        if (wrap) wrap.style.display = 'none';
      };
    };
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
