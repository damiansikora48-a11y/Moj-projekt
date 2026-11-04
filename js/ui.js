/* Interfejs: szkielet, pasek zasobów, osada, budynki, mapa i marsze */
(function () {
  const C = P.cfg, U = P.u;
  const $ = (q) => document.querySelector(q);
  const UI = P.ui = { page: 'city', tab: {}, modalFn: null, labels: true, citySig: '' };
  const A = P.act = {};
  P.pages = {};

  // ---------- podstawy ----------
  UI.toast = (msg, cls = '') => {
    if (!document.body) return;
    const box = $('#toasts'); if (!box) return;
    const el = document.createElement('div'); el.className = 'toast ' + cls; el.innerHTML = msg;
    box.appendChild(el); setTimeout(() => el.classList.add('out'), 2600); setTimeout(() => el.remove(), 3100);
    while (box.children.length > 3) box.firstChild.remove();
  };
  UI.timer = (end, label = '') => `<span class="timer" data-end="${end}">${U.dur(end - P.S.time)}</span>${label}`;
  UI.bar = (start, end) => `<div class="pbar"><i data-start="${start}" data-pend="${end}" style="width:${U.clamp((P.S.time - start) / (end - start) * 100, 0, 100)}%"></i></div>`;
  UI.tabs = (key, list) => { const cur = UI.tab[key] || list[0][0]; return `<div class="tabs">${list.map(([id, n]) => `<button class="tabb${cur === id ? ' on' : ''}" data-a="tab" data-k="${key}" data-v="${id}">${n}</button>`).join('')}</div>`; };
  UI.cur = (key, def) => UI.tab[key] || def;
  UI.armyTable = (a, opts = {}) => {
    const rows = []; for (const t in a) for (const r in a[t]) if (a[t][r] > 0) rows.push(`<tr><td>${C.units[t].icon} ${C.units[t].name}</td><td>${C.units[t].npc ? '' : U.roman(+r)}</td><td class="num">${U.full(a[t][r])}</td></tr>`);
    return rows.length ? `<table class="tbl">${opts.head ? `<tr><th>Jednostka</th><th>St.</th><th class="num">Liczba</th></tr>` : ''}${rows.join('')}</table>` : `<p class="muted">${opts.empty || 'brak'}</p>`;
  };

  UI.modal = (fn, opts = {}) => { UI.modalFn = fn; UI.modalFresh = true; UI.modalLive = !!opts.live; $('#modal').classList.remove('hidden'); $('#modal').classList.toggle('wide', !!opts.wide); UI.renderModal(); $('#modalCard').scrollTop = 0; };
  // zachowanie wartości pól (po id) przy przerysowaniu
  const keepVals = (root) => { const o = {}; root.querySelectorAll('input[id],select[id],textarea[id]').forEach((el) => { o[el.id] = el.type === 'checkbox' ? el.checked : el.value; }); return o; };
  const putVals = (root, o) => { for (const id in o) { const el = root.querySelector('#' + CSS.escape(id)); if (el) { if (el.type === 'checkbox') el.checked = o[id]; else el.value = o[id]; } } };
  UI.keepVals = keepVals; UI.putVals = putVals;
  UI.renderModal = () => { if (!UI.modalFn) return; const body = $('#modalBody'); const st = $('#modalCard').scrollTop; const kv = UI.modalFresh ? {} : keepVals(body); UI.modalFresh = false; body.innerHTML = UI.modalFn(P.S); putVals(body, kv); $('#modalCard').scrollTop = st; };
  UI.close = () => { UI.modalFn = null; $('#modal').classList.add('hidden'); };
  A.close = () => { if (P.S) UI.close(); };
  A.tab = (d) => { UI.tab[d.k] = d.v; };
  A.go = (d) => UI.go(d.p);

  UI.go = (p) => {
    UI.page = p; UI.close();
    document.querySelectorAll('#nav button').forEach((b) => b.classList.toggle('on', b.dataset.p === p || (b.dataset.p === 'more' && !['city', 'map', 'army', 'heroes', 'board', 'alliance'].includes(p))));
    UI.citySig = ''; UI.renderView(true);
    $('#view').scrollTop = 0;
  };
  UI.refresh = () => {
    UI.renderTop();
    UI.renderView(false);
    const focused = document.activeElement && ['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement.tagName);
    if (UI.modalFn && !focused) UI.renderModal();
  };
  UI.renderView = (force) => {
    const s = P.S; const v = $('#view');
    v.dataset.page = UI.page;
    if (UI.page === 'city') {
      const sig = JSON.stringify([s.b, s.bq.map((q) => q.id), s.skin, s.damagedWalls, s.quest.flags.plac, Math.floor(U.hourUTC(s.time) / 2), UI.labels, s.cosmetics.market_deco]);
      if (force || sig !== UI.citySig || !$('#cityBox')) { UI.citySig = sig; if (!$('#cityBox')) v.innerHTML = `<div id="cityBox" class="cityBox"></div><div id="cityHud"></div>`; const box = $('#cityBox'); const first = !box.firstChild; const sl = box.scrollLeft; box.innerHTML = P.city.render(s, { labels: UI.labels }); UI.fitCity(first ? null : sl); }
      $('#cityHud').innerHTML = P.pages.cityHud(s);
      return;
    }
    if (UI.page === 'map') {
      if (force || !$('#mapCanvas')) { v.innerHTML = `<div class="mapWrap"><canvas id="mapCanvas"></canvas><div class="mapCtl"><button data-a="zoom" data-f="1.25">＋</button><button data-a="zoom" data-f="0.8">－</button><button data-a="mapHome">🏰</button><button data-a="mapLegend">?</button></div><div id="mapInfo" class="mapInfo"></div></div>`; P.mapView.attach($('#mapCanvas'), s); }
      P.mapView.draw(s);
      const sel = P.mapView.sel; if (sel) $('#mapInfo').innerHTML = P.pages.tileInfo(s, sel.x, sel.y); else $('#mapInfo').innerHTML = `<div class="hint">Dotknij pola na mapie. Region: ${P.world.regionName(P.world.home(s).x, P.world.home(s).y)}. Odkryto ${U.full(s.stats.discovered)} pól.</div>`;
      return;
    }
    const fn = P.pages[UI.page]; if (!fn) return;
    const focused = document.activeElement && v.contains(document.activeElement) && ['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement.tagName);
    if (focused && !force) return;
    const st = v.scrollTop; const kv = force ? {} : keepVals(v); v.innerHTML = `<div class="page">${fn(s)}</div>`; putVals(v, kv); v.scrollTop = st;
    if (UI.page === 'chat') { const box = $('#chatBox'); if (box) box.scrollTop = box.scrollHeight; }
    if (UI.page === 'ruler') P.pages.bindRuler && P.pages.bindRuler(s);
  };

  UI.fitCity = (sl) => {
    const box = $('#cityBox'); if (!box) return; const svg = box.querySelector('svg'); if (!svg) return;
    const w = box.clientWidth, h = box.clientHeight;
    if (w / h < 1.25) { svg.style.width = Math.round(h * 1.25) + 'px'; svg.style.height = h + 'px'; box.scrollLeft = sl != null ? sl : (h * 1.25 - w) / 2; }
    else { svg.style.width = '100%'; svg.style.height = '100%'; }
  };
  window.addEventListener('resize', () => { if (UI.page === 'city') UI.fitCity(); });
  UI.renderTop = () => {
    const s = P.S; const cap = P.eco.cap(s); const r = P.eco.netRates(s);
    let h = '';
    for (const k of C.basic) {
      const v = s.res[k]; const full = v >= cap;
      h += `<div class="res${full ? ' full' : ''}" title="${C.resources[k].name}: ${U.full(v)} / ${U.full(cap)} (${r[k] >= 0 ? '+' : ''}${U.fmt(r[k])}/h)"><span>${C.resources[k].icon}</span><b>${U.fmt(v)}</b><small class="${r[k] < 0 ? 'bad' : ''}">${r[k] >= 0 ? '+' : ''}${U.fmt(r[k])}/h</small></div>`;
    }
    h += `<div class="res" title="Srebro"><span>🪙</span><b>${U.fmt(s.res.silver)}</b></div>`;
    h += `<div class="res ruby" data-a="go" data-p="shop" title="Rubiny"><span>💎</span><b>${U.fmt(s.rubies)}</b></div>`;
    const E = s.energy; const nextE = E.v >= C.energy.max ? '' : U.dur(C.energy.regenMin * C.MIN - E.acc);
    h += `<div class="energy" data-a="energyInfo" title="Punkty wypraw: 1 punkt co 6 minut, maks. 240"><span>⚡</span><div class="ebar"><i style="width:${Math.min(100, E.v / C.energy.max * 100)}%"></i></div><b>${E.v}/${C.energy.max}</b>${nextE ? `<small>+1 za ${nextE}</small>` : ''}</div>`;
    const sp = s.speed;
    h += `<div class="clock" data-a="speed" title="Czas gry (UTC). Kliknij, aby zmienić tempo testowe."><span>🕰️ ${new Date(s.time).toLocaleString('pl-PL', { weekday: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })} UTC</span><b class="${sp > 1 ? 'fast' : ''}">×${sp}</b></div>`;
    $('#top').innerHTML = h;
    const nb = (p, n) => { const b = document.querySelector(`#nav [data-p="${p}"] .badge`); if (b) { b.textContent = n || ''; b.classList.toggle('hidden', !n); } };
    nb('more', s.unread); nb('board', s.board.offers.length); nb('army', s.raid.incoming ? '!' : U.armyCount(s.wounded) && !s.healQ ? '+' : '');
  };

  A.speed = () => { const s = P.S; const i = C.speeds.indexOf(s.speed); s.speed = C.speeds[(i + 1) % C.speeds.length]; UI.toast(`Tempo gry: ×${s.speed}${s.speed > 1 ? ' (tryb testowy)' : ''}`); };
  A.energyInfo = () => UI.modal((s) => { const i = P.shop.energyInfo(s); return `<h2>⚡ Punkty wypraw</h2><p>Jeden wspólny pasek dla całego konta. Korzystają z niego zlecenia z tablicy i działania PvE na mapie. Obrona i PvP nie zużywają punktów.</p><table class="tbl"><tr><td>Zapas</td><td class="num">${s.energy.v} / ${C.energy.max}</td></tr><tr><td>Regeneracja</td><td class="num">1 punkt co ${C.energy.regenMin} minut (24 h od zera)</td></tr><tr><td>Krótkie zlecenie</td><td class="num">${C.energy.costBoard.join('–')}</td></tr><tr><td>Zwykły potwór</td><td class="num">${C.energy.costMonster}</td></tr><tr><td>Silniejszy przeciwnik / wyprawa sojuszu</td><td class="num">${C.energy.costStrong} / ${C.energy.costRally}</td></tr></table><p class="muted">Koszt pobierany jest przy wysłaniu (rezerwacja). Zawrócenie przed walką zwraca energię. Pełny pasek nie gromadzi nadmiaru.</p><h3>Zakup energii</h3><p>10 punktów za 60 💎 · dziś pozostało: ${i.leftD}/3 · w tym tygodniu: ${i.leftW}/21</p><button class="btn" data-a="buyEnergy">Kup 10 ⚡ za 60 💎</button>`; }, { live: true });
  A.buyEnergy = () => P.shop.buyEnergy(P.S);

  // ---------- HUD osady ----------
  P.pages.cityHud = (s) => {
    let h = '';
    const q = P.quests.current(s);
    if (q) h += `<div class="quest"><b>Zadanie ${s.quest.step + 1}/7:</b> ${q.t}<div class="muted">${q.d}</div>${q.action ? `<button class="btn sm" data-a="questAct" data-q="${q.action}">Wykonaj (100 🪵)</button>` : ''}<span class="rw">Nagroda: ${P.rewardStr(q.reward)}</span></div>`;
    if (s.raid.incoming) h += `<div class="alert" data-a="go" data-p="army">⚠️ Napad: ${U.esc(s.raid.incoming.from)} – za ${UI.timer(s.raid.incoming.arrive)} · ${U.fmt(U.armyCount(s.raid.incoming.army))} wojowników${s.raid.incoming.reinfNote ? '<br><small>🛡️ ' + s.raid.incoming.reinfNote + '</small>' : ''}</div>`;
    else if (s.shield > s.time) h += `<div class="info">🛡️ Ochrona początkowa: ${UI.timer(s.shield)}</div>`;
    // kolejki
    let qh = '';
    const nq = P.bld.queues(s);
    for (let i = 0; i < nq; i++) {
      const b = s.bq[i];
      if (b) qh += `<div class="qi"><span>🔨 ${C.buildings[b.id].name} → ${b.to}</span>${UI.bar(b.start, b.end)}<span class="qt">${UI.timer(b.end)}</span><button class="btn xs" data-a="qSpeed" data-k="b" data-i="${i}">⏩</button></div>`;
      else qh += `<div class="qi idle" data-a="hint" data-t="Kliknij budynek w osadzie, aby go ulepszyć.">🔨 Kolejka budowy ${i + 1}: wolna</div>`;
    }
    if (nq < 2) qh += `<div class="qi idle muted">🔒 2. kolejka: badanie „Druga kolejka budowy”</div>`;
    if (s.rq) qh += `<div class="qi"><span>📘 ${C.research[s.rq.id].name} ${s.rq.to}</span>${UI.bar(s.rq.start, s.rq.end)}<span class="qt">${UI.timer(s.rq.end)}</span><button class="btn xs" data-a="qSpeed" data-k="r">⏩</button></div>`;
    for (const bid in s.trainQ) { const t = s.trainQ[bid]; qh += `<div class="qi"><span>${C.units[t.type].icon} ${t.n}× ${C.units[t.type].short || C.units[t.type].name} ${U.roman(t.tier)}</span>${UI.bar(t.start, t.end)}<span class="qt">${UI.timer(t.end)}</span><button class="btn xs" data-a="qSpeed" data-k="t" data-i="${bid}">⏩</button></div>`; }
    if (s.healQ) qh += `<div class="qi"><span>➕ Leczenie ${U.fmt(U.armyCount(s.healQ.army))}</span>${UI.bar(s.healQ.start, s.healQ.end)}<span class="qt">${UI.timer(s.healQ.end)}</span><button class="btn xs" data-a="qSpeed" data-k="h">⏩</button></div>`;
    if (s.forgeQ) qh += `<div class="qi"><span>⚒️ Kuźnia</span>${UI.bar(s.forgeQ.start, s.forgeQ.end)}<span class="qt">${UI.timer(s.forgeQ.end)}</span></div>`;
    for (const m of s.marches) qh += `<div class="qi march"><span>⚑ ${U.esc(m.tname)} · ${{ out: 'marsz', return: 'powrót', gather: 'zbieranie', garrison: 'wsparcie' }[m.state]}</span><span class="qt">${UI.timer(m.next)}</span></div>`;
    h += UI.hideQ ? `<button class="btn xs qToggle" data-a="toggleQ">▴ kolejki (${s.bq.length + s.marches.length + Object.keys(s.trainQ).length + (s.rq ? 1 : 0)})</button>` : `<div class="queues"><button class="btn xs ghost qToggle2" data-a="toggleQ">▾</button>${qh}</div>`;
    const st = U.stageOf(Math.max(1, s.b.siedziba));
    h += `<div class="cityName">${U.esc(s.ruler.name)} · ${P.ruler.title(s)} · <b>${s.b.siedziba > 0 ? C.stages[st].city : 'Ruiny'}</b> · 👥 ${U.fmt(s.pop)}/${U.fmt(P.eco.popCap(s))}${P.eco.workFactor(s) < 1 ? ` <span class="bad" title="Za mało mieszkańców do pracy – rozbuduj Domy">(praca ${U.pct(P.eco.workFactor(s))})</span>` : ''}${P.eco.starving(s) ? ' <span class="bad">· GŁÓD!</span>' : ''}<button class="btn xs ghost" data-a="toggleLabels">${UI.labels ? 'ukryj' : 'pokaż'} etykiety</button></div>`;
    return h;
  };
  A.toggleLabels = () => { UI.labels = !UI.labels; };
  A.toggleQ = () => { UI.hideQ = !UI.hideQ; };
  A.questAct = (d) => P.quests.action(P.S, d.q);
  A.hint = (d) => UI.toast(d.t);
  A.qSpeed = (d) => {
    const s = P.S; let q, kinds;
    if (d.k === 'b') { q = s.bq[+d.i]; kinds = ['sp_build']; }
    if (d.k === 'r') { q = s.rq; kinds = ['sp_research']; }
    if (d.k === 't') { q = s.trainQ[d.i]; kinds = ['sp_train']; }
    if (d.k === 'h') { q = s.healQ; kinds = ['sp_heal']; }
    if (!q) return;
    UI.modal((s2) => {
      const rem = q.end - s2.time; if (rem <= 0) return '<p>Ukończono!</p><button class="btn" data-a="close">OK</button>';
      const items = kinds.concat(['sp_any']).map((k) => `<div class="row"><span>${C.speedups[k].icon} ${C.speedups[k].name}: <b>${s2.speedups[k] || 0} min</b></span><button class="btn sm" data-a="useSp" data-k="${k}" ${!(s2.speedups[k] > 0) ? 'disabled' : ''}>Użyj</button></div>`).join('');
      const helpable = (d.k === 'b' || d.k === 'r') && s2.alliance && !q.helpReq;
      return `<h2>Przyspiesz</h2><p>Pozostało: ${UI.timer(q.end)}</p>${UI.bar(q.start, q.end)}${items}<div class="row"><span>Ukończ natychmiast</span><button class="btn sm gold" data-a="finishNow">${P.rubyFinishCost(rem)} 💎</button></div>${helpable ? `<div class="row"><span>Pomoc sojuszu (${Math.min(P.alliance.helpLimit(s2), P.alliance.active(s2))}×, min. 1 min lub 1%)</span><button class="btn sm" data-a="askHelp">Poproś</button></div>` : q.helpReq ? `<p class="muted">Sojusz pomógł ${q.helps}×.</p>` : ''}${d.k === 'b' ? `<button class="btn ghost sm" data-a="cancelBuild">Anuluj budowę (zwrot 50%)</button>` : ''}`;
    }, { live: true });
    UI.curQ = { q, kinds };
  };
  A.useSp = (d) => { const s = P.S; const { q } = UI.curQ; P.speedup(s, q, d.k, Math.ceil((q.end - s.time) / C.MIN)); P.advance(s, 0); };
  A.finishNow = () => { const s = P.S; P.shop.finishNow(s, UI.curQ.q); P.advance(s, 0); };
  A.askHelp = () => P.alliance.askHelp(P.S, UI.curQ.q);
  A.cancelBuild = () => { P.bld.cancel(P.S, UI.curQ.q); UI.close(); };

  // ---------- okno budynku ----------
  A.bld = (d) => UI.building(d.b);
  UI.building = (id) => UI.modal((s) => P.pages.building(s, id), { live: true, wide: true });
  P.pages.building = (s, id) => {
    const d = C.buildings[id]; const L = s.b[id]; const st = U.stageOf(L); const next = L + 1;
    const main = ['siedziba', 'stajnia', 'lucznicy', 'koszary', 'pikinierzy'].includes(id);
    let h = `<div class="bhead"><div class="prev">${P.city.preview(id, L, s)}</div><div><h2>${d.name} <span class="lvl">poz. ${L}/${d.max}</span></h2><p class="muted">${d.desc}</p>${L > 0 && d.max === 30 ? `<p>Etap wyglądu: <b>${C.stages[st].bld}</b> (poz. ${C.stages[st].from}–${C.stages[st].to})</p>` : ''}${main ? `<button class="btn sm ghost" data-a="stages" data-b="${id}">Plansza sześciu etapów</button>` : ''}</div></div>`;
    // ulepszenie
    const q = P.bld.inQueue(s, id);
    if (q) h += `<div class="box"><b>Trwa ulepszenie do poz. ${q.to}</b> – rusztowanie otacza dobudowywany fragment, budynek działa normalnie.${UI.bar(q.start, q.end)}${UI.timer(q.end)} <button class="btn xs" data-a="qSpeed" data-k="b" data-i="${s.bq.indexOf(q)}">⏩ Przyspiesz</button></div>`;
    else if (L < d.max) {
      const c = P.bld.canUpgrade(s, id); const cost = P.bld.cost(id, next); const t = P.bld.time(s, id, next);
      const reqs = P.bld.reqs(s, id, next);
      const nst = U.stageOf(next);
      h += `<div class="box"><h3>${L === 0 ? 'Budowa' : 'Ulepszenie'}: poz. ${L} → ${next}</h3>`;
      if (nst !== st && d.max === 30) h += `<div class="newStage"><div class="prev small">${P.city.preview(id, next, s)}</div><div><b>Nowa bryła: ${C.stages[nst].bld}</b><br><span class="muted">Model zmieni się po ukończeniu budowy.</span></div></div>`;
      else if (d.max === 30 && [3, 8, 13, 18, 23, 28, 5, 10, 15, 20, 25, 30].includes(next)) h += `<p class="muted">Poziom ${next}: drobne dodatki i wykończenie etapu.</p>`;
      h += `<p>Koszt: ${P.costStr(cost, s)}</p><p>Czas: ${U.dur(t)}</p>`;
      if (reqs.length) h += `<p>Wymagania: ${reqs.map((r) => `<span class="${r.ok ? 'good' : 'bad'}">${r.ok ? '✔' : '✖'} ${r.t}</span>`).join(' · ')}</p>`;
      h += P.pages.upgradeGain(s, id, next);
      h += `<button class="btn" data-a="upgrade" data-b="${id}" ${c.ok ? '' : 'disabled'}>${L === 0 ? 'Zbuduj' : 'Ulepsz'}</button> ${!c.ok ? `<span class="bad">${c.why}</span>` : ''}</div>`;
    } else h += `<div class="box good">Maksymalny poziom.</div>`;
    h += P.pages.bldFunc(s, id);
    return h;
  };
  P.pages.upgradeGain = (s, id, next) => {
    const d = C.buildings[id];
    if (d.prod) { const a = P.eco.prodRaw(d.prod, next - 1), b = P.eco.prodRaw(d.prod, next); return `<p class="muted">Produkcja bazowa: ${U.fmt(a)} → <b>${U.fmt(b)}</b>/h. Pracownicy: ${Math.round(3.5 * Math.pow(next, 1.3))}.</p>`; }
    if (id === 'magazyn') return `<p class="muted">Pojemność wzrośnie do ok. ${U.fmt((3000 + 6000 * Math.pow(1.27, next - 1)) * (1 + P.bonus(s, 'storage')))}.</p>`;
    if (id === 'domy') return `<p class="muted">Limit mieszkańców: ${U.fmt(P.eco.popCap(s))} → ${U.fmt(Math.round((40 + 60 * Math.pow(1.17, next - 1)) * (1 + P.bonus(s, 'pop'))))}.</p>`;
    if (d.unit) { const tr = C.tierBuilding.indexOf(next); return `<p class="muted">Większa partia szkolenia (${P.army.batchMax(s, id)} → ${Math.round(20 + 18 * next * Math.pow(1.06, next))}).${tr > 0 ? ` <b>Warunek stopnia ${U.roman(tr + 1)}</b> (wymaga też badania).` : ''}</p>`; }
    if (id === 'siedziba') return `<p class="muted">Podnosi pułap rozbudowy pozostałych budynków do poz. ${next}. Nie przebudowuje ich automatycznie.</p>`;
    return '';
  };
  A.upgrade = (d) => P.bld.start(P.S, d.b);
  A.stages = (d) => UI.modal((s) => `<h2>${C.buildings[d.b].name} na sześciu etapach</h2><div class="stageGrid">${[1, 6, 11, 16, 21, 26].map((l) => `<div class="stg${s.b[d.b] >= l ? ' have' : ''}">${P.city.preview(d.b, l, s)}<b>POZ. ${l === 26 ? '26–30' : l}</b><small>${C.stages[U.stageOf(l)].bld}</small></div>`).join('')}</div><p class="muted">Kierunek wyglądu. O aktualnym modelu decyduje ostatni ukończony poziom danego budynku; rozpoczęcie ulepszenia pokazuje rusztowanie.</p><button class="btn" data-a="bld" data-b="${d.b}">Wróć</button>`, { wide: true });

  P.pages.bldFunc = (s, id) => {
    const d = C.buildings[id]; let h = '';
    if (d.prod) { const r = P.eco.prod(s, d.prod); h += `<div class="box"><h3>Produkcja</h3><p>${C.resources[d.prod].icon} <b>${U.fmt(r)}/h</b> (premie: ${U.pct(P.bonus(s, 'prod_' + d.prod))}, praca: ${U.pct(P.eco.workFactor(s))})</p>${d.prod === 'food' ? `<p>Utrzymanie wojska: <b class="bad">−${U.fmt(P.eco.upkeep(s))}/h</b></p>` : ''}</div>`; }
    if (id === 'magazyn') h += `<div class="box"><p>Pojemność każdego surowca: <b>${U.fmt(P.eco.cap(s))}</b></p><p>Chronione przed rabunkiem: <b>${U.pct(P.eco.protectedPct(s))}</b> (${U.fmt(P.eco.cap(s) * P.eco.protectedPct(s))})</p></div>`;
    if (id === 'domy') h += `<div class="box"><p>Mieszkańcy: <b>${U.fmt(s.pop)} / ${U.fmt(P.eco.popCap(s))}</b></p><p>Potrzebni pracownicy w produkcji: ${U.fmt(P.eco.workersNeeded(s))}. Wydajność pracy: <b>${U.pct(P.eco.workFactor(s))}</b>.</p></div>`;
    if (d.unit) h += P.pages.recruit(s, id);
    if (id === 'siedziba') h += `<div class="box"><p>Tytuł władcy: <b>${P.ruler.title(s)}</b>${P.ruler.nextTitle(s) ? ` · następny: ${P.ruler.nextTitle(s).name} (siedziba ${P.ruler.nextTitle(s).lvl}${P.ruler.nextTitle(s).need ? `, obrony ${P.ruler.nextTitle(s).need.defenses || 0}, przeprawy ${P.ruler.nextTitle(s).need.bridges || 0}` : ''})` : ''}</p><p>Pojemność marszu: ${U.fmt(P.army.marchCap(s))} · marsze: ${P.army.maxMarches(s)}</p><button class="btn sm" data-a="allStages">Plansze wszystkich budynków</button></div>`;
    if (id === 'akademia') h += `<button class="btn" data-a="go" data-p="research">Otwórz badania</button>`;
    if (id === 'kuznia') h += `<button class="btn" data-a="go" data-p="forge">Otwórz kuźnię</button>`;
    if (id === 'karczma') h += `<p>Nagrody zleceń +${s.b.karczma * 4}%.</p><button class="btn" data-a="go" data-p="board">Tablica ogłoszeń</button>`;
    if (id === 'sala') h += `<p>Maks. poziom towarzyszy: <b>${P.heroes.cap(s)}</b></p><button class="btn" data-a="go" data-p="heroes">Towarzysze</button>`;
    if (id === 'arena') h += s.b.arena ? `<button class="btn" data-a="go" data-p="arena">Wejdź na arenę</button>` : `<p class="muted">Arena odblokowuje automatyczne walki rankingowe bez strat wojska.</p>`;
    if (id === 'poselstwo') h += `<div class="box"><p>Pojemność posiłków: <b>${U.fmt(P.alliance.reinfCap(s))}</b></p></div>`;
    if (id === 'lazaret') h += P.pages.lazaret(s);
    if (id === 'rynek' && s.b.rynek > 0) h += P.pages.market(s);
    if (id === 'mury' || id === 'brama' || id === 'wieze') { const f = P.raids.fortSpec(s); h += `<div class="box"><p>Premia murów do obrony: <b>${U.pct(f.wallBonus)}</b> · wytrzymałość bramy: <b>${U.fmt(f.wallHp)}</b> · ostrzał wież: <b>${U.fmt(f.towers)}</b>/runda</p>${s.damagedWalls ? `<p class="bad">Umocnienia uszkodzone (${U.pct(s.damagedWalls)}). Naprawa: ${P.costStr(P.raids.repairCost(s), s)}</p><button class="btn" data-a="repair">Napraw</button>` : '<p class="good">Umocnienia sprawne.</p>'}${id === 'wieze' ? `<p>Tryb wież: <button class="btn xs ${s.defense.towers === 'piechota' ? 'on' : 'ghost'}" data-a="towerMode" data-m="piechota">Ostrzał piechoty</button> <button class="btn xs ${s.defense.towers === 'machiny' ? 'on' : 'ghost'}" data-a="towerMode" data-m="machiny">Zwalczanie machin</button></p>` : ''}</div>`; }
    return h;
  };
  A.allStages = () => UI.modal((s) => `<h2>Pięć budynków – wspólne progi wyglądu</h2>${['siedziba', 'stajnia', 'lucznicy', 'koszary', 'pikinierzy'].map((b) => `<h3>${C.buildings[b].name} (poz. ${s.b[b]})</h3><div class="stageGrid">${[1, 6, 11, 16, 21, 26].map((l) => `<div class="stg${s.b[b] >= l ? ' have' : ''}">${P.city.preview(b, l, s)}<b>POZ. ${l === 26 ? '26–30' : l}</b></div>`).join('')}</div>`).join('')}`, { wide: true });
  A.repair = () => P.raids.repair(P.S);
  A.towerMode = (d) => { P.S.defense.towers = d.m; };

  P.pages.recruit = (s, bid) => {
    const type = C.buildings[bid].unit; const u = C.units[type]; const max = P.army.maxTier(s, type);
    let h = `<div class="box"><h3>${u.icon} Rekrutacja: ${u.name}</h3><p class="muted">${u.role}. Słabość: ${u.weak}.</p>`;
    if (s.b[bid] <= 0) return h + '<p>Zbuduj budynek, aby rekrutować.</p></div>';
    const q = s.trainQ[bid];
    if (q) h += `<p>Szkolenie: ${q.n} × ${U.roman(q.tier)}${q.retrain ? ` (przeszkolenie z ${U.roman(q.retrain)})` : ''}</p>${UI.bar(q.start, q.end)}${UI.timer(q.end)} <button class="btn xs" data-a="qSpeed" data-k="t" data-i="${bid}">⏩</button>`;
    else {
      const tier = Math.min(max, +(UI.tab['tier_' + bid] || max));
      const bm = P.army.batchMax(s, bid);
      h += `<div class="row">Stopień: ${[1, 2, 3, 4, 5, 6].map((r) => `<button class="btn xs ${r === tier ? 'on' : 'ghost'}" ${r > max ? 'disabled title="Wymaga poziomu budynku i badania"' : ''} data-a="tab" data-k="tier_${bid}" data-v="${r}">${U.roman(r)}</button>`).join('')}</div>`;
      const st = P.unitStats(type, tier); const c1 = P.army.unitCost(type, tier);
      h += `<p class="muted">Atak ${st.atk.toFixed(0)} · Obrona ${st.def.toFixed(0)} · Wytrzymałość ${st.hp.toFixed(0)} · Prędkość ${u.spd} · Udźwig ${u.load} · Utrzymanie ${(u.upkeep * C.tierCost[tier - 1]).toFixed(1)} 🌾/h</p><p>Koszt 1: ${P.costStr(c1)} · czas 1: ${U.dur(P.army.unitTime(s, type, tier))}</p>`;
      h += `<div class="row"><input type="range" id="rq_${bid}" min="1" max="${bm}" value="${Math.min(bm, +(UI.tab['n_' + bid] || bm))}" oninput="document.getElementById('rqn_${bid}').value=this.value"><input type="number" id="rqn_${bid}" min="1" max="${bm}" value="${Math.min(bm, +(UI.tab['n_' + bid] || bm))}" oninput="document.getElementById('rq_${bid}').value=this.value"><button class="btn" data-a="train" data-b="${bid}" data-t="${type}" data-r="${tier}">Szkol</button></div><p class="muted">Maks. partia: ${bm}. Jedna kolejka szkolenia na budynek.</p>`;
      // przeszkolenie
      const have = s.units[type] || {}; const low = Object.keys(have).map(Number).filter((r) => r < max && have[r] > 0);
      if (low.length) h += `<h4>Przeszkolenie</h4>${low.map((r) => `<div class="row"><span>${U.roman(r)} → ${U.roman(max)}: masz ${U.full(have[r])}</span><button class="btn sm" data-a="retrain" data-t="${type}" data-f="${r}" data-to="${max}" data-n="${Math.min(have[r], bm)}">Przeszkol ${Math.min(have[r], bm)}</button></div>`).join('')}<p class="muted">Dopłacasz różnicę kosztu; czas to ok. 70% różnicy czasu szkolenia.</p>`;
    }
    const have = s.units[type] || {};
    h += `<p>W osadzie: ${Object.keys(have).length ? Object.entries(have).map(([r, n]) => `${U.roman(+r)}: <b>${U.full(n)}</b>`).join(' · ') : 'brak'}</p></div>`;
    return h;
  };
  A.train = (d) => { const n = +document.getElementById('rqn_' + d.b).value; UI.tab['n_' + d.b] = n; P.army.train(P.S, d.t, +d.r, n); };
  A.retrain = (d) => P.army.retrain(P.S, d.t, +d.f, +d.to, +d.n);

  P.pages.lazaret = (s) => {
    const w = U.armyCount(s.wounded); let h = `<div class="box"><h3>➕ Lazaret</h3><p>Ranni: <b>${U.full(w)}</b> / pojemność ${U.full(P.army.lazaretCap(s))}. Ranni ponad limit giną.</p>`;
    if (s.healQ) h += `<p>Leczenie ${U.full(U.armyCount(s.healQ.army))}</p>${UI.bar(s.healQ.start, s.healQ.end)}${UI.timer(s.healQ.end)} <button class="btn xs" data-a="qSpeed" data-k="h">⏩</button>`;
    else if (w) h += UI.armyTable(s.wounded) + `<p>Koszt: ${P.costStr(P.army.healCost(s, s.wounded), s)} · czas: ${U.dur(P.army.healTime(s, s.wounded))}</p><button class="btn" data-a="heal">Lecz wszystkich</button>`;
    return h + '</div>';
  };
  A.heal = () => P.army.heal(P.S);
  P.pages.market = (s) => {
    const rate = 0.1 * (1 + P.bonus(s, 'trade')), buy = 8 * (1 + P.bonus(s, 'trade'));
    return `<div class="box"><h3>🪙 Rynek</h3><p class="muted">Sprzedaż: 1000 surowca → ${Math.round(1000 * rate)} srebra. Zakup: 100 srebra → ${Math.round(100 * buy)} surowca. Handel bezpośredni między kontami nie został jeszcze ustalony.</p>${C.basic.map((k) => `<div class="row"><span>${C.resources[k].icon} ${C.resources[k].name}</span><button class="btn xs" data-a="trade" data-r="${k}" data-m="sell">Sprzedaj 1000</button><button class="btn xs" data-a="trade" data-r="${k}" data-m="buy">Kup za 100 🪙</button></div>`).join('')}</div>`;
  };
  A.trade = (d) => { const s = P.S; const rate = 0.1 * (1 + P.bonus(s, 'trade')), buy = 8 * (1 + P.bonus(s, 'trade')); if (d.m === 'sell') { if (s.res[d.r] < 1000) return UI.toast('Za mało', 'bad'); s.res[d.r] -= 1000; s.res.silver += Math.round(1000 * rate); } else { if (s.res.silver < 100) return UI.toast('Za mało srebra', 'bad'); s.res.silver -= 100; s.res[d.r] += Math.round(100 * buy); } };

  // ---------- mapa ----------
  A.zoom = (d) => P.mapView.zoom(+d.f);
  A.mapHome = () => { const h = P.world.home(P.S); P.mapView.centerOn(h.x, h.y); P.mapView.sel = { x: h.x, y: h.y }; P.mapView.draw(P.S); UI.mapSelect(h.x, h.y); };
  A.mapLegend = () => UI.modal(() => `<h2>Legenda mapy</h2><p>🏰 Twoja osada · 👑 Zamek Koronny · 🛡️ forty · 🏘️ osady innych graczy · 🚩 siedziba sojuszu · 🗼 strażnica · 🗡️🐺🏴🏛️💀 przeciwnicy (liczba = poziom) · 🐉 wielka bestia · ❗ cel zlecenia · 🌾🪵🪨⛓️ złoża · ❔ znalezisko · 🚧 uszkodzona przeprawa · ⚑ cel strategiczny.</p><p>Niebieskie koło = teren sojuszu. Ciemne pola nie są odkryte – wyślij zwiadowców. Bez odbudowanych mostów marsze przez rzekę idą objazdem (+60% drogi).</p><button class="btn" data-a="close">OK</button>`);
  UI.mapSelect = (x, y) => { if (UI.page === 'map') $('#mapInfo').innerHTML = P.pages.tileInfo(P.S, x, y); };
  A.showOnMap = (d) => { const o = P.world.obj(P.S, d.o); UI.go('map'); if (o) { P.mapView.centerOn(o.x, o.y); P.mapView.sel = { x: o.x, y: o.y }; P.mapView.draw(P.S); UI.mapSelect(o.x, o.y); } };

  P.pages.tileInfo = (s, x, y) => {
    const rev = P.world.isRev(s, x, y); const t = P.world.terrain(s, x, y);
    const objs = P.world.at(s, x, y).filter((o) => o.type !== 'fog' && (rev || ['home', 'castle', 'fort'].includes(o.type)));
    let h = `<div class="ti"><div class="tiHead"><b>(${x}, ${y})</b> ${P.world.regionName(x, y)} · ${(C.terrains[t] || { name: t === 'river' ? 'Rzeka' : t === 'bridge' ? 'Przeprawa' : t }).name} · zagrożenie ${P.world.dangerAt(x, y)}<button class="btn xs ghost" data-a="mapClose">✕</button></div>`;
    if (!rev) h += `<p class="muted">Nieodkryty obszar.</p><button class="btn sm" data-a="scout" data-x="${x}" data-y="${y}">🧭 Wyślij zwiadowców (bez energii)</button>`;
    for (const o of objs) h += P.pages.objInfo(s, o);
    if (rev && !objs.length) h += `<p class="muted">Puste pole.</p>`;
    return h + '</div>';
  };
  A.mapClose = () => { P.mapView.sel = null; P.mapView.draw(P.S); $('#mapInfo').innerHTML = ''; };
  P.pages.objInfo = (s, o) => {
    const dist = P.world.dist(s, o).toFixed(1);
    const btn = (kind, label, energy = 0, extra = '') => `<button class="btn sm" data-a="march" data-o="${o.id}" data-k="${kind}" data-e="${energy}" ${extra}>${label}${energy ? ` · ${energy}⚡` : ''}</button>`;
    let h = `<div class="obj">`;
    if (o.type === 'home') return h + `<b>🏰 ${U.esc(s.ruler.name)} – Twoja osada</b><p class="muted">Siedziba poz. ${s.b.siedziba}. Siła garnizonu: ${U.fmt(P.armyPower(s.units))}.</p><button class="btn sm" data-a="go" data-p="city">Wejdź do osady</button></div>`;
    if (o.type === 'monster') {
      const M = C.monsters[o.kind] || {}; const army = P.world.monsterArmy(o); const pow = P.armyPower(army, P.world.monsterMods(o));
      const strong = M.strong; const cost = o.beast ? C.energy.costRally : strong ? C.energy.costStrong : C.energy.costMonster;
      h += `<b>${o.beast ? '🐉' : M.icon} ${U.esc(o.name)} · poz. ${o.lvl}</b><p>Siła: ~${U.fmt(pow)} · odległość ${dist} · teren: ${(C.terrains[P.world.terrain(s, o.x, o.y)] || {}).name || ''}</p>`;
      if ((s.research.zwiad || 0) >= 1 || o.lvl <= 3) h += `<p class="muted">Skład (zwiad): ${Object.entries(army).map(([t, r]) => `${C.units[t].icon} ${C.units[t].name} ~${U.fmt(Object.values(r)[0])}`).join(', ')}</p>`;
      else h += `<p class="muted">Zbadaj „Zwiad”, aby widzieć skład przeciwnika.</p>`;
      if (!o.beast) h += `<p class="muted">Nagrody: ${(M.res || []).map((r) => C.resources[r].icon).join('')} ${M.silver ? '🪙' : ''} ${Object.keys(M.items || {}).map((i) => C.items[i].icon).join('')} · szansa na 💎 ${strong ? '60' : '30'}%</p>`;
      if (o.busy) h += `<p class="good">Twoje wojsko jest w drodze.</p>`;
      else if (o.beast) h += s.alliance ? btn('rally', '⚔️ Zgrupowanie sojuszu', cost) : `<p class="bad">Wielka bestia wymaga zgrupowania – dołącz do sojuszu.</p>`;
      else h += btn('monster', '⚔️ Atakuj', cost);
    }
    if (o.type === 'task') { const tk = s.board.taken.find((t) => t.id === o.taskId); h += `<b>${U.esc(o.name)} · poz. ${o.lvl}</b>`; if (tk) h += `<p>${P.TASKS[tk.type].prep}</p><p>Nagroda: ${P.rewardStr(tk.reward)}</p>${tk.cargo ? `<p>Ładunek: ${U.fmt(tk.cargo)} udźwigu</p>` : ''}${o.busy ? '<p class="good">W drodze.</p>' : btn('task', '📋 Wykonaj zlecenie', tk.energy)}`; }
    if (o.type === 'node') h += `<b>${C.resources[o.res].icon} ${o.name} · poz. ${o.lvl}</b><p>Zasoby: ${U.fmt(o.amount)} · odległość ${dist}${P.alliance.inTerritory(s) ? ' · premia terenu sojuszu' : ''}</p>${o.busy ? '<p class="good">Trwa zbieranie.</p>' : btn('gather', '⛏️ Zbieraj')}`;
    if (o.type === 'bridge') h += `<b>${o.broken ? '🚧' : '🌉'} ${o.name}</b>${o.broken ? `<p>Odbudowa mostu otwiera krótszą trasę. Koszt: ${P.costStr({ wood: 3000, stone: 2000 }, s)} + wysłanie oddziału.</p>${btn('bridge', '🔨 Odbuduj przeprawę', 0, 'data-pay="1"')}` : '<p class="good">Przeprawa działa.</p>'}`;
    if (o.type === 'find') h += `<b>❔ ${o.name}</b>${o.done ? '<p class="muted">Zbadane.</p>' : `<p>Znalezisko osobiste – dostępne także dla nowych graczy.</p>${btn('find', '🔍 Zbadaj')}`}`;
    if (o.type === 'bot') {
      const mine = s.alliance && o.ali === s.alliance.botAli;
      h += `<b>🏘️ ${o.name} ${o.tag ? '[' + o.tag + ']' : '(bez sojuszu)'}</b><p>Siedziba ~${o.lvl} · siła ~${U.fmt(o.power)} · odległość ${dist}</p>`;
      if (mine) h += btn('reinforce', '🛡️ Wyślij posiłki');
      else h += `${btn('bot', '⚔️ Najazd (PvP, bez energii)')} <span class="muted">Chwała za realną walkę; powtórne ataki na ten sam cel dają malejącą nagrodę.</span>`;
    }
    if (o.type === 'fort') {
      const own = o.owner === 'neutral' ? 'neutralny garnizon' : s.map.allies[o.owner]; const mine = s.alliance && o.owner === s.alliance.botAli;
      const open = P.forts.windowOpen(s);
      h += `<b>🛡️ ${o.name}</b><p>Właściciel: <b>${own}</b>. Rekrutacja: ${C.forts[o.fort].units.map((u) => C.units[u].icon + ' ' + C.units[u].name).join(', ')}.</p><p>${open ? '<span class="good">Okno walk trwa!</span>' : `Następne okno walk: ${U.clock(P.forts.nextWindow(s))} (${C.fortRules.windowLenH} h)`}</p>`;
      h += s.alliance ? btn('fort', mine ? '🛡️ Wzmocnij obronę' : '⚔️ Szturm') : '<p class="muted">Walki o forty prowadzą sojusze.</p>';
    }
    if (o.type === 'castle' || o.type === 'strategic') { const p = P.crown.period(s); h += `<b>${o.type === 'castle' ? '👑' : '⚑'} ${o.name}</b><p>${P.crown.active(s) ? '<span class="good">Wojna o Koronę trwa!</span> Koniec: ' + U.clock(p.end) : 'Wojna o Koronę: ' + U.clock(p.start)}</p>${o.type === 'castle' && o.owner !== 'neutral' && o.owner != null ? `<p>Zamek w rękach: ${s.map.allies[o.owner]}</p>` : ''}${s.alliance ? btn(o.type, '⚔️ Atakuj cel') : '<p class="muted">Wymaga sojuszu.</p>'}`; }
    if (o.type === 'allyhq' || o.type === 'tower') h += `<b>${o.type === 'allyhq' ? '🚩' : '🗼'} ${o.name}</b><p class="muted">${o.type === 'allyhq' ? 'Siedziba tworzy pierwszy obszar wpływów sojuszu.' : 'Strażnica graniczna rozszerza teren sojuszu.'}</p>`;
    return h + '</div>';
  };
  A.scout = (d) => { const s = P.S; const o = P.world.addObj(s, { type: 'fog', x: +d.x, y: +d.y, name: `Zwiad (${d.x}, ${d.y})` }); if (!P.world.send(s, { target: o, army: {}, kind: 'scout', hero: s.heroes.wit && !P.heroes.busy(s, 'wit') ? 'wit' : null })) s.map.objs = s.map.objs.filter((x) => x !== o); };

  // ---------- okno marszu ----------
  A.march = (d) => {
    const s = P.S; const o = P.world.obj(s, d.o); if (!o) return;
    if (d.pay) { if (!P.canPay(s, { wood: 3000, stone: 2000 })) return UI.toast('Brak surowców na odbudowę', 'bad'); }
    UI.marchSpec = { o, kind: d.k, energy: +d.e || 0, pay: !!d.pay, army: {}, hero: null, helper: null, tactic: 'rownowaga' };
    // domyślny skład: proporcjonalnie do pojemności
    A.mFill({ m: 'auto' });
    UI.modal(P.pages.marchModal, { wide: true });
  };
  P.pages.marchModal = (s) => {
    const M = UI.marchSpec; const o = M.o; const cap = P.army.marchCap(s);
    const n = U.armyCount(M.army); const mods = P.sideMods(s, { hero: M.hero, helper: M.helper });
    const pow = P.armyPower(M.army, mods);
    let threat = null;
    if (o.type === 'monster' || o.type === 'task') threat = P.armyPower(P.world.monsterArmy(o), P.world.monsterMods(o));
    if (o.type === 'bot') threat = P.armyPower(P.pvp.botArmy(o));
    if (o.type === 'fort') threat = P.armyPower(P.forts.garrison(s, o));
    if (M.kind === 'rally') threat = P.armyPower(P.world.monsterArmy(o), P.world.monsterMods(o));
    const time = U.armyCount(M.army) ? P.world.travelTime(s, o, M.army, M.hero) : 0;
    const freeHeroes = Object.keys(s.heroes).filter((h) => !P.heroes.busy(s, h));
    let rows = '';
    for (const t in s.units) for (const r in s.units[t]) { const have = s.units[t][r]; if (!have) continue; const v = (M.army[t] || {})[r] || 0; rows += `<tr><td>${C.units[t].icon} ${C.units[t].name} ${U.roman(+r)}</td><td class="num">${U.full(have)}</td><td><input type="number" class="mIn" data-t="${t}" data-r="${r}" min="0" max="${have}" value="${v}"></td><td><button class="btn xs ghost" data-a="mMax" data-t="${t}" data-r="${r}">maks.</button></td></tr>`; }
    const tactics = Object.entries(C.tactics).map(([k, v]) => `<option value="${k}" ${M.tactic === k ? 'selected' : ''}>${v.name} – ${v.desc}</option>`).join('');
    const hsel = (sel, field) => `<select data-a2="mHero" data-f="${field}"><option value="">— brak —</option>${freeHeroes.map((h) => `<option value="${h}" ${sel === h ? 'selected' : ''}>${C.heroes[h].icon} ${C.heroes[h].name} (${C.heroes[h].role}, poz. ${s.heroes[h].lvl})</option>`).join('')}</select>`;
    const ratio = threat ? pow / Math.max(1, threat) : null;
    const verdict = ratio == null ? '' : ratio > 1.6 ? '<span class="good">przewaga</span>' : ratio > 1.0 ? '<span class="good">wyrównana z przewagą</span>' : ratio > 0.7 ? '<span class="warn">ryzykowne</span>' : '<span class="bad">duże ryzyko porażki</span>';
    const kindName = { monster: 'Atak', task: 'Zlecenie', gather: 'Zbieranie', bridge: 'Odbudowa przeprawy', find: 'Badanie znaleziska', bot: 'Najazd', fort: 'Fort', castle: 'Wojna o Koronę', strategic: 'Wojna o Koronę', rally: 'Zgrupowanie sojuszu', reinforce: 'Posiłki' }[M.kind];
    return `<h2>${kindName}: ${U.esc(o.name)}</h2>
      <div class="grid2"><div><h3>1. Dowódca i pomocnik</h3><p>Dowódca: ${hsel(M.hero, 'hero')}</p><p>Pomocnik (50% premii): ${hsel(M.helper, 'helper')}</p>${M.hero ? `<p class="muted">${P.heroes.effText(P.heroes.effects(s, M.hero))}</p>` : ''}<h3>2. Taktyka</h3><select data-a2="mTactic">${tactics}</select></div>
      <div><h3>3. Skład armii</h3><div class="row"><button class="btn xs" data-a="mFill" data-m="auto">Proporcjonalnie</button><button class="btn xs" data-a="mFill" data-m="all">Wszystko</button><button class="btn xs ghost" data-a="mFill" data-m="none">Wyczyść</button></div><table class="tbl">${rows || '<tr><td>Brak wojska w osadzie</td></tr>'}</table></div></div>
      <div class="box marchSum"><p>Liczebność: <b class="${n > cap ? 'bad' : ''}">${U.full(n)} / ${U.full(cap)}</b> · Siła: <b>${U.fmt(pow)}</b>${threat != null ? ` vs przeciwnik ~${U.fmt(threat)} (${verdict})` : ''}</p><p>Udźwig: ${U.fmt(P.army.armyLoad(s, M.army))} · Czas marszu: <b>${U.dur(time)}</b> (w jedną stronę) · Energia: <b>${M.energy}⚡</b> (masz ${s.energy.v})</p><p class="muted">Liczba mocy jest pomocnicza – wynik zależy od składu, przewag, terenu, taktyki i umiejętności. Do rozpoczęcia walki możesz zawrócić (zwrot energii).</p>
      <button class="btn gold" data-a="mSend">Wyślij armię</button> <button class="btn ghost" data-a="close">Anuluj</button></div>`;
  };
  A.mMax = (d) => { const s = P.S; const M = UI.marchSpec; M.army[d.t] = M.army[d.t] || {}; M.army[d.t][d.r] = s.units[d.t][d.r]; UI.renderModal(); };
  A.mFill = (d) => {
    const s = P.S; const M = UI.marchSpec; const cap = P.army.marchCap(s); M.army = {};
    if (d.m === 'none') return UI.renderModal();
    const total = U.armyCount(s.units); const f = d.m === 'all' ? Math.min(1, cap / Math.max(1, total)) : Math.min(1, cap / Math.max(1, total));
    for (const t in s.units) for (const r in s.units[t]) { const v = Math.floor(s.units[t][r] * f); if (v > 0) { M.army[t] = M.army[t] || {}; M.army[t][r] = v; } }
    if (M.kind === 'gather') { /* zbieranie: preferuj udźwig – kawaleria i lekcy jeźdźcy */ }
    if (UI.modalFn) UI.renderModal();
  };
  A.mSend = () => {
    const s = P.S; const M = UI.marchSpec;
    if (M.pay && !P.pay(s, { wood: 3000, stone: 2000 })) return UI.toast('Brak surowców', 'bad');
    const m = P.world.send(s, { target: M.o, army: M.army, hero: M.hero, helper: M.helper, tactic: M.tactic, kind: M.kind, energy: M.energy });
    if (m) UI.close(); else if (M.pay) { s.res.wood += 3000; s.res.stone += 2000; }
  };
  document.addEventListener('input', (e) => {
    const el = e.target;
    if (el.classList.contains('mIn')) { const M = UI.marchSpec; const v = U.clamp(Math.floor(+el.value || 0), 0, +el.max); M.army[el.dataset.t] = M.army[el.dataset.t] || {}; M.army[el.dataset.t][el.dataset.r] = v; if (!v) delete M.army[el.dataset.t][el.dataset.r]; const sum = document.querySelector('.marchSum'); if (sum) { const tmp = document.createElement('div'); tmp.innerHTML = P.pages.marchModal(P.S); sum.innerHTML = tmp.querySelector('.marchSum').innerHTML; } }
  });
  document.addEventListener('change', (e) => {
    const el = e.target; const a = el.dataset.a2; if (!a) return;
    if (a === 'mHero') { UI.marchSpec[el.dataset.f] = el.value || null; UI.renderModal(); }
    if (a === 'mTactic') { UI.marchSpec.tactic = el.value; UI.renderModal(); }
    if (P.act2 && P.act2[a]) { P.act2[a](el); UI.refresh(); }
  });

  // ---------- delegacja kliknięć ----------
  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-a]');
    if (!el) { const plot = e.target.closest('.plot'); if (plot && UI.page === 'city') { UI.building(plot.dataset.b); } return; }
    if (el.disabled) return;
    const fn = A[el.dataset.a]; if (!fn) return;
    e.preventDefault();
    fn(el.dataset, el, e);
    UI.refresh();
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') UI.close(); if (e.key === 'Enter' && e.target.id === 'chatIn') { A.chatSend(); UI.refresh(); } });
})();
