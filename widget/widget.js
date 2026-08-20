const API_URL = 'https://bible-widget-backend.vercel.app/api/morning';
const CACHE_KEY = 'bibleWidgetDesktopCache';
const DUBAI_OFFSET_HOURS = 4;

function pad2(n) {
  return String(n).padStart(2, '0');
}

function dubaiKeyFromUtcMillis(utcMillis) {
  const shifted = new Date(utcMillis + DUBAI_OFFSET_HOURS * 60 * 60 * 1000);
  return `${shifted.getUTCFullYear()}-${pad2(shifted.getUTCMonth() + 1)}-${pad2(shifted.getUTCDate())}`;
}

function dubaiKeyFromIsoDate(iso) {
  if (!iso) return null;
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return null;
  return dubaiKeyFromUtcMillis(dt.getTime());
}

function todayKeyDubai() {
  return dubaiKeyFromUtcMillis(Date.now());
}

function loadCache() {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY) || '{}');
  } catch {
    return {};
  }
}

function saveCache(data) {
  localStorage.setItem(CACHE_KEY, JSON.stringify(data));
}

function cleanVerseText(raw, reference) {
  let text = (raw || '').trim();
  if (text.includes('\n')) {
    const lines = text.split('\n').map((l) => l.trim()).filter(Boolean);
    if (lines.length && lines[0].toLowerCase() === (reference || '').toLowerCase()) {
      text = lines.slice(1).join('\n\n');
    }
  }
  return text || raw || '';
}

async function fetchVerse(force = false) {
  const todayKey = todayKeyDubai();
  const cache = loadCache();

  if (!force && cache[todayKey]) {
    return cache[todayKey];
  }

  const res = await fetch(API_URL, {
    headers: { Accept: 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  const json = await res.json();
  const apiKey = dubaiKeyFromIsoDate(json.generated_at) || todayKey;

  const verse = {
    text: cleanVerseText(json.esv_text, json.reference),
    reference: json.reference || 'Daily Verse',
    meaning: json.simple_meaning || '',
    message: json.message || '',
    generated_at: json.generated_at || null,
  };

  cache[apiKey] = verse;
  cache.lastVerse = verse;
  saveCache(cache);

  return verse;
}

function showLoading(message = "Fetching today's verse...", sub = 'Connecting to Bible Widget') {
  document.getElementById('loading').classList.remove('hidden');
  document.getElementById('content').classList.add('hidden');
  document.getElementById('status').classList.add('hidden');
  document.querySelector('.loading-text').textContent = message;
  document.querySelector('.loading-sub').textContent = sub;
}

function showOfflineStatus() {
  const status = document.getElementById('status');
  status.textContent = 'Will update when you are back online';
  status.classList.remove('hidden');
}

function render(verse) {
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('content').classList.remove('hidden');
  document.getElementById('status').classList.add('hidden');

  document.getElementById('verseText').textContent = verse.text;
  document.getElementById('reference').textContent = verse.reference;

  const messageEl = document.getElementById('message');
  if (verse.message) {
    messageEl.textContent = verse.message;
    messageEl.classList.remove('hidden');
  } else {
    messageEl.classList.add('hidden');
  }

  const meaningBox = document.getElementById('meaningBox');
  const meaningEl = document.getElementById('meaning');
  if (verse.meaning) {
    meaningEl.textContent = verse.meaning;
    meaningBox.classList.remove('hidden');
  } else {
    meaningBox.classList.add('hidden');
  }
}

function showCachedOrError(err) {
  const cache = loadCache();
  const todayKey = todayKeyDubai();

  if (cache[todayKey]) {
    render(cache[todayKey]);
    showOfflineStatus();
    return;
  }

  if (cache.lastVerse) {
    render(cache.lastVerse);
    showOfflineStatus();
    return;
  }

  showLoading('Waiting for connection...', 'Bible Widget');
  showOfflineStatus();
  console.error(err);
}

async function loadVerse(force = false) {
  if (!force) {
    showLoading();
  }

  try {
    const verse = await fetchVerse(force);
    render(verse);
  } catch (err) {
    showCachedOrError(err);
  }
}

function scheduleDailyRefresh() {
  const now = Date.now();
  const dubaiNow = new Date(now + DUBAI_OFFSET_HOURS * 60 * 60 * 1000);
  const next = new Date(dubaiNow);
  next.setUTCHours(9, 30, 0, 0);

  if (next.getTime() <= dubaiNow.getTime()) {
    next.setUTCDate(next.getUTCDate() + 1);
  }

  const delay = next.getTime() - dubaiNow.getTime();
  setTimeout(() => {
    loadVerse(true);
    scheduleDailyRefresh();
  }, delay);
}

document.getElementById('btnRefresh').addEventListener('click', () => loadVerse(true));

document.getElementById('btnPin').addEventListener('click', async () => {
  const btn = document.getElementById('btnPin');
  if (window.pywebview && window.pywebview.api) {
    const onTop = await window.pywebview.api.toggle_on_top();
    btn.classList.toggle('active', !!onTop);
  }
});

document.getElementById('btnClose').addEventListener('click', () => {
  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.close();
  } else {
    window.close();
  }
});

function startWhenReady() {
  loadVerse();
  scheduleDailyRefresh();
}

if (window.pywebview) {
  window.addEventListener('pywebviewready', startWhenReady);
} else {
  startWhenReady();
}
