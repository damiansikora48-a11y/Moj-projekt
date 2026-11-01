// ---- Nectar Kingdom: core game -----------------------------------------
const SAVE_KEY = 'nectarKingdom_save_v1';
const BASE_OFFLINE_HOURS = 8;
const BASE_OFFLINE_EFF = 0.5;
const BOOST_MS = 10 * 60 * 1000;

// ---------- helpers ----------
const $ = (id) => document.getElementById(id);
const SUFFIXES = ['', 'K', 'M', 'B', 'T', 'Qa', 'Qi', 'Sx', 'Sp', 'Oc', 'No', 'Dc', 'UDc', 'DDc', 'TDc', 'QaDc', 'QiDc'];
function fmt(n) {
  if (!isFinite(n)) return '∞';
  if (n < 1000) return n < 10 && n % 1 ? n.toFixed(1) : Math.floor(n).toString();
  const e = Math.floor(Math.log10(n) / 3);
  if (e >= SUFFIXES.length) return n.toExponential(2);
  const v = n / Math.pow(1000, e);
  return (v < 10 ? v.toFixed(2) : v < 100 ? v.toFixed(1) : Math.floor(v)) + ' ' + SUFFIXES[e];
}
function fmtTime(ms) {
  const s = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  if (h) return `${h}h ${m}m`;
  if (m) return `${m}m ${sec.toString().padStart(2, '0')}s`;
  return `${sec}s`;
}
const ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII'];

function toast(msg) {
  const el = document.createElement('div');
  el.className = 'toast';
  el.textContent = msg;
  $('toasts').appendChild(el);
  setTimeout(() => el.remove(), 3000);
  while ($('toasts').children.length > 4) $('toasts').firstChild.remove();
}
function showModal(html, buttons) {
  $('modalBody').innerHTML = html;
  const box = $('modalButtons');
  box.innerHTML = '';
  buttons.forEach((b) => {
    const btn = document.createElement('button');
    btn.className = 'btn ' + (b.cls || '');
    btn.textContent = b.label;
    btn.onclick = () => { if (!b.keepOpen) hideModal(); b.onClick && b.onClick(); };
    box.appendChild(btn);
  });
  $('modal').classList.remove('hidden');
}
function hideModal() { $('modal').classList.add('hidden'); }
function confirmBox(text, onYes) {
  showModal(`<p>${text}</p>`, [{ label: t('no') }, { label: t('yes'), cls: 'btn-gold', onClick: onYes }]);
}

// ---------- state ----------
function freshState() {
  return {
    honey: 0, runEarned: 0, lifetimeEarned: 0,
    clicks: 0, goldenClicks: 0, prestiges: 0,
    gens: {}, upgrades: [], achievements: [],
    jelly: 0, jellyEarned: 0, perks: {},
    boostUntil: 0, frenzyUntil: 0, clickFrenzyUntil: 0,
    lang: (navigator.language || 'en').toLowerCase().startsWith('pl') ? 'pl' : 'en',
    playTime: 0, lastSave: Date.now(), startedAt: Date.now(),
  };
}
let S = freshState();
let buyAmount = 1;
let paused = false;
let nextGoldenAt = 0;

const perkLvl = (id) => S.perks[id] || 0;
const hasUpg = (id) => S.upgrades.includes(id);

// ---------- economy ----------
function costMultiplier() { return 1 - 0.03 * perkLvl('cheap'); }
function genCost(g, n) {
  const owned = S.gens[g.id] || 0;
  const r = COST_GROWTH;
  return g.baseCost * costMultiplier() * Math.pow(r, owned) * (Math.pow(r, n) - 1) / (r - 1);
}
function maxAffordable(g) {
  const owned = S.gens[g.id] || 0;
  const r = COST_GROWTH;
  const first = g.baseCost * costMultiplier() * Math.pow(r, owned);
  if (S.honey < first) return 0;
  return Math.floor(Math.log(S.honey * (r - 1) / first + 1) / Math.log(r));
}
function amountFor(g) { return buyAmount === 'max' ? Math.max(1, maxAffordable(g)) : buyAmount; }

function genMultiplier(g) {
  let m = 1;
  GEN_TIERS.forEach((_, i) => { if (hasUpg(`g_${g.id}_${i}`)) m *= 2; });
  return m;
}
function globalMultiplier(includeTemp = true) {
  let m = 1 + 0.01 * S.achievements.length;
  m *= 1 + 0.03 * S.jelly;
  UPGRADES.forEach((u) => { if (u.kind === 'global' && hasUpg(u.id)) m *= u.mult; });
  if (includeTemp) {
    const now = Date.now();
    if (S.boostUntil > now) m *= 2;
    if (S.frenzyUntil > now) m *= 7;
  }
  return m;
}
function genProd(g) { return g.baseProd * (S.gens[g.id] || 0) * genMultiplier(g); }
function hps(includeTemp = true) {
  return GENERATORS.reduce((a, g) => a + genProd(g), 0) * globalMultiplier(includeTemp);
}
function clickValue() {
  let base = 1, pct = 0;
  UPGRADES.forEach((u) => { if (u.kind === 'click' && hasUpg(u.id)) { base *= 2; pct += 0.01; } });
  base *= Math.pow(2, perkLvl('click'));
  let v = base + hps(false) * pct;
  if (S.frenzyUntil > Date.now()) v *= 7;
  if (S.clickFrenzyUntil > Date.now()) v *= 10;
  return v;
}
function earn(x) {
  S.honey += x; S.runEarned += x; S.lifetimeEarned += x;
}

// ---------- prestige ----------
function jellyPotential(lifetime = S.lifetimeEarned) { return Math.floor(Math.sqrt(lifetime / 1e7)); }
function jellyGain() { return Math.max(0, jellyPotential() - S.jellyEarned); }
function honeyForJelly(n) { return n * n * 1e7; }

function prestige() {
  const gain = jellyGain();
  if (gain <= 0) { toast(t('prestigeNone')); return; }
  confirmBox(t('prestigeConfirm', { x: fmt(gain) }), () => {
    S.jelly += gain; S.jellyEarned += gain; S.prestiges++;
    S.honey = 0; S.runEarned = 0; S.gens = {}; S.upgrades = [];
    S.frenzyUntil = 0; S.clickFrenzyUntil = 0;
    applyStartPerk();
    checkAchievements();
    buildGenList();
    save();
    Ads.midgame();
  });
}
function applyStartPerk() {
  const n = 10 * perkLvl('start');
  if (n) S.gens.bee = (S.gens.bee || 0) + n;
}
function buyPerk(p) {
  const lvl = perkLvl(p.id);
  if (lvl >= p.costs.length) return;
  const cost = p.costs[lvl];
  if (S.jelly < cost) return;
  S.jelly -= cost;
  S.perks[p.id] = lvl + 1;
  if (p.id === 'start') S.gens.bee = (S.gens.bee || 0) + 10;
  renderPerks();
}

// ---------- actions ----------
function clickHive(ev) {
  const v = clickValue();
  earn(v);
  S.clicks++;
  spawnFloater(ev, '+' + fmt(v));
}
function buyGen(g) {
  const n = amountFor(g);
  const cost = genCost(g, n);
  if (S.honey < cost) return;
  S.honey -= cost;
  S.gens[g.id] = (S.gens[g.id] || 0) + n;
}
function buyUpgrade(u) {
  if (hasUpg(u.id) || S.honey < u.cost) return;
  S.honey -= u.cost;
  S.upgrades.push(u.id);
  renderUpgrades(true);
}

// ---------- golden bee ----------
function scheduleGolden() {
  const freq = 1 + 0.15 * perkLvl('golden');
  nextGoldenAt = Date.now() + (60 + Math.random() * 120) * 1000 / freq;
}
function spawnGolden() {
  const b = document.createElement('button');
  b.className = 'golden-bee';
  b.textContent = '🐝';
  b.setAttribute('aria-label', 'Golden bee');
  const W = window.innerWidth, H = window.innerHeight;
  let x = Math.random() * (W - 80) + 20, y = Math.random() * (H - 140) + 70;
  b.style.left = x + 'px'; b.style.top = y + 'px';
  $('goldenLayer').appendChild(b);
  // drift around
  let vx = (Math.random() - 0.5) * 3, vy = (Math.random() - 0.5) * 3;
  const mover = setInterval(() => {
    x += vx; y += vy;
    if (x < 10 || x > W - 70) vx *= -1;
    if (y < 60 || y > H - 80) vy *= -1;
    b.style.left = x + 'px'; b.style.top = y + 'px';
  }, 30);
  const remove = () => { clearInterval(mover); b.remove(); };
  const timeout = setTimeout(remove, 13000);
  b.onclick = (e) => {
    e.stopPropagation();
    clearTimeout(timeout); remove();
    S.goldenClicks++;
    const roll = Math.random();
    if (roll < 0.45) {
      const prize = Math.max(13, Math.min(S.honey * 0.15, hps(false) * 900) + 13);
      earn(prize);
      toast(t('goldenLucky', { x: fmt(prize) }));
    } else if (roll < 0.85) {
      S.frenzyUntil = Date.now() + 30000;
      toast(t('goldenFrenzy'));
    } else {
      S.clickFrenzyUntil = Date.now() + 15000;
      toast(t('goldenClick'));
    }
  };
}

// ---------- ads / boost ----------
async function watchBoost() {
  const ok = await Ads.rewarded();
  if (ok) S.boostUntil = Math.max(Date.now(), S.boostUntil) + BOOST_MS;
}

// ---------- achievements ----------
function checkAchievements() {
  ACHIEVEMENTS.forEach((a) => {
    if (!S.achievements.includes(a.id) && a.check(S)) {
      S.achievements.push(a.id);
      toast(t('achUnlocked', { x: a.desc() }));
      const el = document.querySelector(`[data-ach="${a.id}"]`);
      if (el) el.classList.add('got');
    }
  });
}

// ---------- save / load ----------
function save(silent = true) {
  S.lastSave = Date.now();
  try { localStorage.setItem(SAVE_KEY, JSON.stringify(S)); } catch (e) { /* storage blocked */ }
  if (!silent) toast(t('saved'));
}
function load() {
  let raw = null;
  try { raw = localStorage.getItem(SAVE_KEY); } catch (e) { /* ignore */ }
  if (!raw) return false;
  try { S = Object.assign(freshState(), JSON.parse(raw)); return true; } catch (e) { return false; }
}
function exportSave() {
  save();
  const box = $('saveText');
  box.classList.remove('hidden');
  box.value = btoa(unescape(encodeURIComponent(JSON.stringify(S))));
  box.select();
}
function importSave() {
  const box = $('saveText');
  if (box.classList.contains('hidden') || !box.value.trim()) {
    box.classList.remove('hidden'); box.value = ''; box.focus();
    toast(t('importPrompt'));
    return;
  }
  try {
    const data = JSON.parse(decodeURIComponent(escape(atob(box.value.trim()))));
    if (typeof data.honey !== 'number') throw new Error('bad');
    S = Object.assign(freshState(), data);
    save(); toast(t('importOk'));
    setTimeout(() => location.reload(), 600);
  } catch (e) { toast(t('importFail')); }
}

function offlineProgress() {
  const away = Date.now() - S.lastSave;
  if (away < 60000) return;
  const capMs = (BASE_OFFLINE_HOURS + 4 * perkLvl('offline')) * 3600000;
  const eff = BASE_OFFLINE_EFF + 0.1 * perkLvl('offline');
  const used = Math.min(away, capMs);
  const gained = hps(false) * (used / 1000) * eff;
  if (gained <= 0) return;
  earn(gained);
  showModal(
    `<h2>${t('welcomeBack')}</h2><p>${t('offlineEarned', { t: fmtTime(used) })}</p><h2 style="color:var(--gold)">+${fmt(gained)} 🍯</h2>`,
    [
      { label: t('collect') },
      { label: t('doubleIt'), cls: 'btn-ad', onClick: async () => { if (await Ads.rewarded()) { earn(gained); toast('+' + fmt(gained) + ' 🍯'); } } },
    ]
  );
}

// ---------- rendering ----------
function spawnFloater(ev, text) {
  const layer = $('floaters');
  const rect = layer.getBoundingClientRect();
  const el = document.createElement('div');
  el.className = 'floater';
  el.textContent = text;
  const x = (ev && ev.clientX ? ev.clientX : rect.left + rect.width / 2) - rect.left;
  const y = (ev && ev.clientY ? ev.clientY : rect.top + rect.height / 2) - rect.top;
  el.style.left = (x - 20 + Math.random() * 20) + 'px';
  el.style.top = (y - 30) + 'px';
  layer.appendChild(el);
  setTimeout(() => el.remove(), 1000);
}

const genEls = {};
function buildGenList() {
  const list = $('genList');
  list.innerHTML = '';
  GENERATORS.forEach((g) => {
    const b = document.createElement('button');
    b.className = 'gen';
    b.innerHTML = `<div class="gen-icon">${g.icon}</div>
      <div><div class="gen-name"></div><div class="gen-sub"></div><div class="gen-cost"></div></div>
      <div class="gen-count">0</div>`;
    b.onclick = () => buyGen(g);
    list.appendChild(b);
    genEls[g.id] = {
      root: b, name: b.querySelector('.gen-name'), sub: b.querySelector('.gen-sub'),
      cost: b.querySelector('.gen-cost'), count: b.querySelector('.gen-count'), icon: b.querySelector('.gen-icon'),
    };
  });
}
function renderGens() {
  const gm = globalMultiplier();
  let prevOwned = true;
  GENERATORS.forEach((g, i) => {
    const el = genEls[g.id];
    const owned = S.gens[g.id] || 0;
    const visible = i === 0 || owned > 0 || prevOwned || S.runEarned >= g.baseCost * 0.5;
    const revealed = owned > 0 || S.runEarned >= g.baseCost * 0.3 || i === 0;
    el.root.classList.toggle('hidden', !visible);
    prevOwned = owned > 0;
    if (!visible) return;
    const n = amountFor(g);
    const cost = genCost(g, n);
    const can = S.honey >= cost;
    el.root.classList.toggle('affordable', can);
    el.root.classList.toggle('locked', !revealed);
    el.icon.textContent = revealed ? g.icon : '❔';
    el.name.textContent = revealed ? `${L(g.name)}${n > 1 ? ' ×' + n : ''}` : t('locked');
    const each = g.baseProd * genMultiplier(g) * gm;
    el.sub.textContent = revealed ? `${fmt(each)}/s ${t('each')} · ${fmt(genProd(g) * gm)}/s` : '';
    el.cost.textContent = '🍯 ' + fmt(cost);
    el.cost.classList.toggle('cant', !can);
    el.count.textContent = owned;
  });
}

function upgradeName(u) {
  if (u.kind === 'gen') { const g = GENERATORS.find((x) => x.id === u.gen); return `${L(g.name)} ${ROMAN[u.tier + 1]}`; }
  if (u.kind === 'click') return (LANG === 'pl' ? 'Lepkie łapki ' : 'Sticky Paws ') + ROMAN[u.tier];
  return (LANG === 'pl' ? 'Błogosławieństwo Królowej ' : "Queen's Blessing ") + ROMAN[u.tier];
}
function upgradeDesc(u) {
  if (u.kind === 'gen') return t('upgGen', { g: L(GENERATORS.find((x) => x.id === u.gen).name) });
  if (u.kind === 'click') return t('upgClick');
  return t('upgGlobal', { x: u.mult });
}
let lastUpgKey = '';
function renderUpgrades(force) {
  const avail = UPGRADES.filter((u) => !hasUpg(u.id) && u.unlocked(S)).sort((a, b) => a.cost - b.cost);
  const key = avail.map((u) => u.id).join(',') + LANG;
  const list = $('upgList');
  if (force || key !== lastUpgKey) {
    lastUpgKey = key;
    list.innerHTML = '';
    avail.forEach((u) => {
      const b = document.createElement('button');
      b.className = 'upg';
      b.dataset.cost = u.cost;
      b.innerHTML = `<div class="upg-icon">${u.icon}</div><div><div class="upg-name">${upgradeName(u)}</div><div class="upg-desc">${upgradeDesc(u)}</div></div><div class="upg-cost">🍯 ${fmt(u.cost)}</div>`;
      b.onclick = () => buyUpgrade(u);
      list.appendChild(b);
    });
    $('upgEmpty').classList.toggle('hidden', avail.length > 0);
  }
  let affordable = 0;
  list.querySelectorAll('.upg').forEach((b) => {
    const can = S.honey >= +b.dataset.cost;
    b.classList.toggle('affordable', can);
    if (can) affordable++;
  });
  const badge = $('upgBadge');
  badge.textContent = affordable;
  badge.classList.toggle('hidden', affordable === 0);
}

function buildAchievements() {
  const grid = $('achList');
  grid.innerHTML = '';
  ACHIEVEMENTS.forEach((a) => {
    const d = document.createElement('div');
    d.className = 'ach' + (S.achievements.includes(a.id) ? ' got' : '');
    d.dataset.ach = a.id;
    d.textContent = a.icon;
    d.title = a.desc();
    grid.appendChild(d);
  });
}

function renderPerks() {
  const list = $('perkList');
  list.innerHTML = '';
  PERKS.forEach((p) => {
    const lvl = perkLvl(p.id);
    const maxed = lvl >= p.costs.length;
    const cost = maxed ? 0 : p.costs[lvl];
    const b = document.createElement('button');
    b.className = 'upg' + (!maxed && S.jelly >= cost ? ' affordable' : '');
    b.innerHTML = `<div class="upg-icon">${p.icon}</div><div><div class="upg-name">${L(p.name)} · ${t('level')} ${lvl}/${p.costs.length}</div><div class="upg-desc">${L(p.desc)}</div></div><div class="upg-cost">${maxed ? t('max') : '👑 ' + cost}</div>`;
    b.onclick = () => buyPerk(p);
    list.appendChild(b);
  });
}

function renderPrestige() {
  $('jelly').textContent = fmt(S.jelly);
  $('jellyGain').textContent = fmt(jellyGain());
  $('jellyNext').textContent = fmt(honeyForJelly(jellyPotential() + 1));
  $('prestigeBtn').disabled = jellyGain() <= 0;
}

function renderStats() {
  const rows = [
    [t('stHoney'), fmt(S.runEarned)],
    [t('stLifetime'), fmt(S.lifetimeEarned)],
    [t('stClicks'), fmt(S.clicks)],
    [t('stGolden'), S.goldenClicks],
    [t('stPrestiges'), S.prestiges],
    [t('stPlay'), fmtTime(S.playTime)],
    [t('stMult'), '×' + globalMultiplier().toFixed(2)],
  ];
  $('stats').innerHTML = rows.map(([a, b]) => `<div>${a}</div><div>${b}</div>`).join('');
}

function renderBuffs() {
  const now = Date.now();
  const parts = [];
  if (S.boostUntil > now) parts.push(`<span class="buff boost">${t('boostActive', { t: fmtTime(S.boostUntil - now) })}</span>`);
  if (S.frenzyUntil > now) parts.push(`<span class="buff frenzy">${t('frenzy', { t: fmtTime(S.frenzyUntil - now) })}</span>`);
  if (S.clickFrenzyUntil > now) parts.push(`<span class="buff frenzy">${t('clickFrenzy', { t: fmtTime(S.clickFrenzyUntil - now) })}</span>`);
  const html = parts.join('');
  if ($('buffs').innerHTML !== html) $('buffs').innerHTML = html;
  $('boostBtn').textContent = S.boostUntil > now ? t('boostActive', { t: fmtTime(S.boostUntil - now) }) : t('boostBtn');
}

let activeTab = 'shop';
function render() {
  const h = hps();
  $('honey').textContent = fmt(S.honey);
  $('hps').textContent = fmt(h);
  $('perClick').textContent = fmt(clickValue());
  document.title = `${fmt(S.honey)} 🍯 — ${t('title')}`;
  renderBuffs();
  if (activeTab === 'shop') renderGens();
  renderUpgrades(false);
  if (activeTab === 'prestige') renderPrestige();
  if (activeTab === 'settings') renderStats();
  $('achCount').textContent = `${S.achievements.length}/${ACHIEVEMENTS.length}`;
}

function applyLang() {
  LANG = S.lang;
  document.documentElement.lang = LANG;
  document.querySelectorAll('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $('langBtn').textContent = LANG === 'pl' ? 'EN' : 'PL';
  buildAchievements();
  renderPerks();
  renderUpgrades(true);
}

// ---------- main loop ----------
let lastTick = Date.now();
function tick() {
  const now = Date.now();
  const dt = Math.min((now - lastTick) / 1000, 60);
  lastTick = now;
  if (!paused) {
    earn(hps() * dt);
    S.playTime += dt * 1000;
    if (now >= nextGoldenAt) { spawnGolden(); scheduleGolden(); }
  }
}

const Game = {
  pause(p) { paused = p; lastTick = Date.now(); },
};

function init() {
  const loaded = load();
  if (!loaded) applyStartPerk();
  LANG = S.lang;
  buildGenList();
  applyLang();
  scheduleGolden();
  offlineProgress();
  checkAchievements();

  $('hive').addEventListener('click', clickHive);
  $('boostBtn').onclick = watchBoost;
  $('langBtn').onclick = () => { S.lang = S.lang === 'pl' ? 'en' : 'pl'; applyLang(); };
  $('prestigeBtn').onclick = prestige;
  $('saveBtn').onclick = () => save(false);
  $('exportBtn').onclick = exportSave;
  $('importBtn').onclick = importSave;
  $('resetBtn').onclick = () => confirmBox(t('resetConfirm'), () => {
    try { localStorage.removeItem(SAVE_KEY); } catch (e) { /* ignore */ }
    S = freshState(); save(); location.reload();
  });
  document.querySelectorAll('.amt').forEach((b) => b.onclick = () => {
    document.querySelectorAll('.amt').forEach((x) => x.classList.remove('active'));
    b.classList.add('active');
    buyAmount = b.dataset.amt === 'max' ? 'max' : +b.dataset.amt;
  });
  document.querySelectorAll('.tab').forEach((b) => b.onclick = () => {
    document.querySelectorAll('.tab').forEach((x) => x.classList.remove('active'));
    b.classList.add('active');
    activeTab = b.dataset.tab;
    document.querySelectorAll('.tab-body').forEach((x) => x.classList.add('hidden'));
    $('tab-' + activeTab).classList.remove('hidden');
    if (activeTab === 'prestige') renderPerks();
  });

  setInterval(tick, 50);
  setInterval(render, 100);
  setInterval(checkAchievements, 1000);
  setInterval(save, 10000);
  window.addEventListener('beforeunload', () => save());
  document.addEventListener('visibilitychange', () => { if (document.hidden) save(); });

  Ads.init();
  render();
}

init();
