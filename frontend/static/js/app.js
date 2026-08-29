/* ═══════════════════════════════
   AI STUDY ASSISTANT — app.js
   ═══════════════════════════════ */

const API = '';  // Same origin via FastAPI

// ── STATE ──
let currentTopic = '';
let hasDocument = false;

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupUpload();
  checkExistingDoc();
});

// ── CHECK EXISTING DOC ON LOAD ──
async function checkExistingDoc() {
  try {
    const res = await fetch(`${API}/api/upload/status`);
    const data = await res.json();
    if (data.has_document) {
      enableDocTabs();
    }
  } catch (_) {}
}

// ── NAVIGATION ──
function setupNavigation() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!btn.disabled) switchTab(btn.dataset.tab);
    });
  });
}

function switchTab(tab) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  document.getElementById(`tab-${tab}`).classList.add('active');

  // Pre-fill topic if switching from study
  if (tab === 'quiz' && currentTopic) {
    document.getElementById('quiz-topic').value = currentTopic;
  }
  if (tab === 'doubts' && currentTopic) {
    document.getElementById('doubt-input').placeholder =
      `Ask anything about "${currentTopic}"…`;
  }
}

function enableDocTabs() {
  hasDocument = true;
  ['nav-study', 'nav-quiz', 'nav-doubts'].forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.disabled = false;
  });
  const dot = document.querySelector('.status-dot');
  dot.classList.remove('inactive');
  dot.classList.add('active');
  const status = document.getElementById('doc-status');
  status.querySelector('span').textContent = 'Document loaded';
}

// ── UPLOAD ──
function setupUpload() {
  const zone = document.getElementById('drop-zone');
  const input = document.getElementById('file-input');

  zone.addEventListener('click', () => input.click());

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('dragover');
  });

  zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));

  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file?.name.endsWith('.pdf')) handleUpload(file);
    else showError(zone, 'Please drop a PDF file.');
  });

  input.addEventListener('change', () => {
    if (input.files[0]) handleUpload(input.files[0]);
  });
}

async function handleUpload(file) {
  const progress = document.getElementById('upload-progress');
  const fill = document.getElementById('progress-fill');
  const label = document.getElementById('progress-label');
  const result = document.getElementById('upload-result');
  const zone = document.getElementById('drop-zone');

  // Clear previous errors
  document.querySelectorAll('.error-toast').forEach(e => e.remove());

  zone.classList.add('hidden');
  progress.classList.remove('hidden');
  result.classList.add('hidden');

  // Animate progress bar
  let pct = 0;
  const tick = setInterval(() => {
    pct = Math.min(pct + Math.random() * 12, 88);
    fill.style.width = pct + '%';
  }, 400);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API}/api/upload/`, {
      method: 'POST',
      body: formData
    });

    clearInterval(tick);

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }

    const data = await res.json();
    fill.style.width = '100%';

    await delay(400);
    progress.classList.add('hidden');
    zone.classList.remove('hidden');
    result.classList.remove('hidden');

    document.getElementById('r-filename').textContent = data.filename;
    document.getElementById('r-pages').textContent = data.pages;
    document.getElementById('r-chunks').textContent = data.chunks;

    enableDocTabs();

  } catch (err) {
    clearInterval(tick);
    progress.classList.add('hidden');
    zone.classList.remove('hidden');
    showError(zone.parentElement, err.message);
  }
}

// ── STUDY ──
async function fetchSummary() {
  const topic = document.getElementById('study-topic').value.trim();
  if (!topic) return;

  currentTopic = topic;

  const spinner = document.getElementById('study-spinner');
  const output = document.getElementById('study-output');
  const summaryBox = document.getElementById('summary-box');
  const contextBox = document.getElementById('context-box');

  output.classList.add('hidden');
  spinner.classList.remove('hidden');
  document.querySelectorAll('.error-toast').forEach(e => e.remove());

  try {
    const res = await fetch(`${API}/api/study/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate summary');
    }

    const data = await res.json();

    summaryBox.innerHTML = formatMarkdown(data.summary);

    contextBox.innerHTML = data.context_snippets
      .map(s => `<div class="context-snippet">${escapeHtml(s)}</div>`)
      .join('');

    spinner.classList.add('hidden');
    output.classList.remove('hidden');

  } catch (err) {
    spinner.classList.add('hidden');
    showError(document.getElementById('tab-study'), err.message);
  }
}

function toggleContext() {
  const box = document.getElementById('context-box');
  const btn = document.querySelector('.link-btn');
  box.classList.toggle('hidden');
  btn.textContent = box.classList.contains('hidden')
    ? '▸ View retrieved context'
    : '▾ Hide context';
}

// ── QUIZ ──
async function fetchQuiz() {
  const topic = document.getElementById('quiz-topic').value.trim();
  if (!topic) return;

  const spinner = document.getElementById('quiz-spinner');
  const output = document.getElementById('quiz-output');
  const quizBox = document.getElementById('quiz-box');

  output.classList.add('hidden');
  spinner.classList.remove('hidden');
  document.querySelectorAll('.error-toast').forEach(e => e.remove());

  try {
    const res = await fetch(`${API}/api/quiz/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to generate quiz');
    }

    const data = await res.json();
    quizBox.innerHTML = formatMarkdown(data.quiz);

    spinner.classList.add('hidden');
    output.classList.remove('hidden');

  } catch (err) {
    spinner.classList.add('hidden');
    showError(document.getElementById('tab-quiz'), err.message);
  }
}

// ── DOUBTS / CHAT ──
async function askDoubt() {
  const input = document.getElementById('doubt-input');
  const question = input.value.trim();
  if (!question) return;

  const chatWindow = document.getElementById('chat-window');

  // Remove welcome message if present
  const welcome = chatWindow.querySelector('.chat-welcome');
  if (welcome) welcome.remove();

  // User bubble
  const userBubble = createBubble('user', question);
  chatWindow.appendChild(userBubble);
  input.value = '';

  // Thinking bubble
  const thinking = createBubble('thinking', '⋯ thinking');
  chatWindow.appendChild(thinking);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const res = await fetch(`${API}/api/doubts/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, topic: currentTopic || null })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to get answer');
    }

    const data = await res.json();

    thinking.remove();
    const answerBubble = createBubble('assistant', data.answer);
    chatWindow.appendChild(answerBubble);

  } catch (err) {
    thinking.remove();
    const errBubble = createBubble('assistant', `⚠ ${err.message}`);
    chatWindow.appendChild(errBubble);
  }

  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function createBubble(type, text) {
  const div = document.createElement('div');
  div.className = `chat-bubble ${type}`;
  if (type === 'assistant') {
    div.innerHTML = formatMarkdown(text);
  } else {
    div.textContent = text;
  }
  return div;
}

// ── HELPERS ──
function formatMarkdown(text) {
  return text
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^[-•] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n{2,}/g, '<br><br>')
    .replace(/--- ANSWERS ---/g, '<hr style="border-color:var(--border2);margin:16px 0"><strong style="color:var(--accent)">Answers</strong>');
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function showError(parent, message) {
  const div = document.createElement('div');
  div.className = 'error-toast';
  div.textContent = `⚠ ${message}`;
  parent.appendChild(div);
}

function delay(ms) {
  return new Promise(res => setTimeout(res, ms));
}
