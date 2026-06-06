/* =============================================================================
   VS Code Skills Store — Application Logic
============================================================================= */

'use strict';

// ── Category color map ──────────────────────────────────────────────────────
const CATEGORY_COLORS = {
  'DevOps':        { bg: '#dbeafe', text: '#1d4ed8', border: '#bfdbfe' },
  'Data Science':  { bg: '#ede9fe', text: '#7c3aed', border: '#ddd6fe' },
  'Frontend':      { bg: '#fef3c7', text: '#b45309', border: '#fde68a' },
  'Backend':       { bg: '#dcfce7', text: '#166534', border: '#bbf7d0' },
  'Python':        { bg: '#f0fdf4', text: '#15803d', border: '#bbf7d0' },
  'Hardware':      { bg: '#fee2e2', text: '#991b1b', border: '#fecaca' },
  'Productivity':  { bg: '#fff7ed', text: '#9a3412', border: '#fed7aa' },
  'AI / ML':       { bg: '#f5f3ff', text: '#6d28d9', border: '#ddd6fe' },
  'CAD / Mechanical': { bg: '#ecfeff', text: '#0e7490', border: '#a5f3fc' },
  'Robotics':      { bg: '#f0fdf4', text: '#15803d', border: '#bbf7d0' },
  'Finance / Data': { bg: '#fefce8', text: '#a16207', border: '#fde68a' },
  'Free API':      { bg: '#eef2ff', text: '#3730a3', border: '#c7d2fe' },
  'API':           { bg: '#f5f3ff', text: '#6d28d9', border: '#ddd6fe' },
};

const DEFAULT_COLOR = { bg: '#f1f5f9', text: '#475569', border: '#e2e8f0' };

function getCategoryColor(cat) {
  return CATEGORY_COLORS[cat] || DEFAULT_COLOR;
}

// ── DOM helpers ─────────────────────────────────────────────────────────────
const $  = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => ctx.querySelectorAll(sel);

// ── State ───────────────────────────────────────────────────────────────────
let currentModalSkill = null;

// ── Navigation ──────────────────────────────────────────────────────────────
function navigateTo(page) {
  $$('.page').forEach(p => p.classList.add('hidden'));
  $$('.nav-btn').forEach(b => b.classList.remove('active'));

  const pageEl = $(`#page-${page}`);
  if (pageEl) pageEl.classList.remove('hidden');

  const navBtn = $(`.nav-btn[data-page="${page}"]`);
  if (navBtn) navBtn.classList.add('active');

  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Update URL hash without triggering hashchange handler
  history.replaceState(null, '', `#${page}`);
}

// ── Category filter population ───────────────────────────────────────────────
function populateCategoryFilter() {
  const select = $('#category-filter');
  const categories = [...new Set(window.SKILLS_DATA.map(s => s.category))].sort();
  categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    select.appendChild(opt);
  });
}

// ── Render skill cards ───────────────────────────────────────────────────────
function renderSkillCards(skills) {
  const grid   = $('#skills-grid');
  const empty  = $('#empty-state');
  const count  = $('#result-count');

  grid.innerHTML = '';

  if (skills.length === 0) {
    empty.classList.remove('hidden');
    count.textContent = '';
    return;
  }

  empty.classList.add('hidden');
  count.textContent = `${skills.length} skill${skills.length !== 1 ? 's' : ''}`;

  skills.forEach(skill => {
    const color = getCategoryColor(skill.category);
    const tagHTML = skill.tags
      .slice(0, 4)
      .map(t => `<span class="tag">${escapeHTML(t)}</span>`)
      .join('');

    const card = document.createElement('article');
    card.className = 'skill-card';
    card.setAttribute('role', 'listitem');
    card.innerHTML = `
      <div class="card-top">
        <span class="card-icon" aria-hidden="true">${skill.icon}</span>
        <span class="category-badge"
              style="background:${color.bg};color:${color.text};border-color:${color.border}">
          ${escapeHTML(skill.category)}
        </span>
      </div>
      <h3 class="card-name">${escapeHTML(skill.name)}</h3>
      <p class="card-desc">${escapeHTML(skill.description)}</p>
      <div class="card-tags" aria-label="Tags">${tagHTML}</div>
      <div class="card-footer">
        <span class="card-author">by ${escapeHTML(skill.author)} · v${escapeHTML(skill.version)}</span>
        <div class="card-actions">
          <button class="btn btn-outline btn-sm"
                  data-action="read"
                  data-id="${skill.id}"
                  aria-label="Read ${escapeHTML(skill.name)}">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12" aria-hidden="true">
              <path d="M0 1.75A.75.75 0 0 1 .75 1h4.253c1.227 0 2.317.59 3 1.501A3.743 3.743 0 0 1 11.006 1h4.245a.75.75 0 0 1 .75.75v10.5a.75.75 0 0 1-.75.75h-4.507a2.25 2.25 0 0 0-1.591.659l-.622.621a.75.75 0 0 1-1.06 0l-.622-.621A2.25 2.25 0 0 0 5.258 13H.75a.75.75 0 0 1-.75-.75Z"/>
            </svg>
            Read
          </button>
          <button class="btn btn-primary btn-sm"
                  data-action="download"
                  data-id="${skill.id}"
                  aria-label="Download ${escapeHTML(skill.name)} as ZIP">
            <svg viewBox="0 0 16 16" fill="currentColor" width="12" height="12" aria-hidden="true">
              <path d="M7.47 10.78a.75.75 0 0 0 1.06 0l3.75-3.75a.75.75 0 0 0-1.06-1.06L8.75 8.44V1.75a.75.75 0 0 0-1.5 0v6.69L4.78 5.97a.75.75 0 0 0-1.06 1.06l3.75 3.75ZM3.75 13a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5h-8.5Z"/>
            </svg>
            Download
          </button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// ── Filter logic ─────────────────────────────────────────────────────────────
function filterSkills() {
  const query    = $('#search-input').value.toLowerCase().trim();
  const category = $('#category-filter').value;

  const filtered = window.SKILLS_DATA.filter(skill => {
    const searchable = [skill.name, skill.description, ...skill.tags, skill.category];
    const matchSearch   = !query    || searchable.some(f => f.toLowerCase().includes(query));
    const matchCategory = !category || skill.category === category;
    return matchSearch && matchCategory;
  });

  renderSkillCards(filtered);
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function openModal(skillId) {
  const skill = window.SKILLS_DATA.find(s => s.id === skillId);
  if (!skill) return;

  currentModalSkill = skill;
  const color = getCategoryColor(skill.category);

  $('#modal-icon').textContent     = skill.icon;
  $('#modal-title').textContent    = skill.name;
  $('#modal-version').textContent  = `v${skill.version}`;

  const catBadge = $('#modal-category');
  catBadge.textContent = skill.category;
  catBadge.style.cssText =
    `background:${color.bg};color:${color.text};border-color:${color.border}`;

  // Strip YAML frontmatter before rendering
  const rawContent = skill.content.replace(/^---[\s\S]*?---\s*\n/, '');

  // Render markdown → HTML
  const rendered = marked.parse(rawContent);
  $('#modal-body').innerHTML = rendered;

  // Apply syntax highlighting to all code blocks
  $$('#modal-body pre code').forEach(block => {
    hljs.highlightElement(block);
  });

  $('#modal-overlay').classList.remove('hidden');
  document.body.style.overflow = 'hidden';

  // Focus the close button for accessibility
  setTimeout(() => $('#modal-close-btn').focus(), 60);
}

function closeModal() {
  $('#modal-overlay').classList.add('hidden');
  document.body.style.overflow = '';
  currentModalSkill = null;
}

// ── Download ZIP ──────────────────────────────────────────────────────────────
async function downloadSkill(skillId) {
  const skill = window.SKILLS_DATA.find(s => s.id === skillId);
  if (!skill) return;

  try {
    const zip    = new JSZip();
    const folder = zip.folder(skill.id);
    folder.file('SKILL.md', skill.content);

    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `${skill.id}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Download failed:', err);
    alert('Download failed. Please try again.');
  }
}

async function downloadAllSkills() {
  const skills = window.SKILLS_DATA || [];
  if (!skills.length) return;

  try {
    const zip = new JSZip();

    skills.forEach(skill => {
      const folder = zip.folder(skill.id);
      folder.file('SKILL.md', skill.content);
    });

    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'vscode-skills-all.zip';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Download all failed:', err);
    alert('Download failed. Please try again.');
  }
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function escapeHTML(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Initialise ────────────────────────────────────────────────────────────────
function init() {

  // ── Configure marked.js ──
  marked.use({
    gfm: true,
    breaks: false,
  });

  // ── Navigation buttons ──
  $$('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => navigateTo(btn.dataset.page));
  });

  // ── Search + filter ──
  $('#search-input').addEventListener('input', filterSkills);
  $('#category-filter').addEventListener('change', filterSkills);
  $('#download-all-btn').addEventListener('click', downloadAllSkills);

  // ── Card actions (event delegation) ──
  $('#skills-grid').addEventListener('click', e => {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;
    const { action, id } = btn.dataset;
    if (action === 'read')     openModal(id);
    if (action === 'download') downloadSkill(id);
  });

  // ── Modal close ──
  $('#modal-close-btn').addEventListener('click', closeModal);

  $('#modal-overlay').addEventListener('click', e => {
    if (e.target === $('#modal-overlay')) closeModal();
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !$('#modal-overlay').classList.contains('hidden')) {
      closeModal();
    }
  });

  // ── Modal download button ──
  $('#modal-download-btn').addEventListener('click', () => {
    if (currentModalSkill) downloadSkill(currentModalSkill.id);
  });

  // ── Guide sidebar — smooth scroll to sections ──
  $$('.sidebar-link').forEach(link => {
    link.addEventListener('click', e => {
      const href = link.getAttribute('href');
      if (!href.startsWith('#')) return;
      e.preventDefault();
      const target = $(href);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ── Hash-based routing ──
  function routeFromHash() {
    const hash = location.hash.slice(1); // strip '#'
    // 'guide' and 'store' are top-level pages; everything else might be an
    // anchor inside the guide, which we handle separately
    if (hash === 'guide' || hash === 'store') {
      navigateTo(hash);
    } else if (!hash) {
      navigateTo('store');
    }
  }

  window.addEventListener('hashchange', routeFromHash);
  routeFromHash();

  // ── Populate filters + initial render ──
  populateCategoryFilter();
  renderSkillCards(window.SKILLS_DATA);
}

document.addEventListener('DOMContentLoaded', init);
