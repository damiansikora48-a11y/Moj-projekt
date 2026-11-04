/* Ekrany: wojsko, towarzysze, tablica, sojusz, władca, badania, kuźnia, arena, wydarzenia, VIP, sklep, chwała, raporty, czat */
(function () {
  const C = P.cfg, U = P.u, UI = P.ui, A = P.act, PG = P.pages;
  P.act2 = {};

  // ================= WOJSKO =================
  PG.army = (s) => {
    let h = `<h1>⚔️ Wojsko</h1>` + UI.tabs('army', [['home', 'W osadzie'], ['train', 'Szkolenie'], ['marches', `Marsze (${s.marches.length}/${P.army.maxMarches(s)})`], ['defense', 'Obrona'], ['info', 'Rodzaje']]);
    const t = UI.cur('army', 'home');
    if (t === 'home') {
      const tot = P.army.totalArmy(s);
      h += `<div class="box"><p>W osadzie: <b>${U.full(U.armyCount(s.units))}</b> · łącznie z marszami: ${U.full(U.armyCount(tot))} · siła garnizonu: <b>${U.fmt(P.armyPower(s.units, P.sideMods(s, { home: true })))}</b></p><p>Utrzymanie: <span class="bad">−${U.fmt(P.eco.upkeep(s))} 🌾/h</span> · pojemność marszu ${U.full(P.army.marchCap(s))}</p></div>`;
      let rows = '';
      for (const ty in s.units) for (const r in s.units[ty]) { const n = s.units[ty][r]; if (!n) continue; const st = P.unitStats(ty, +r); rows += `<tr><td>${C.units[ty].icon} ${C.units[ty].name}</td><td>${U.roman(+r)}</td><td class="num">${U.full(n)}</td><td class="num muted">${st.atk.toFixed(0)}/${st.def.toFixed(0)}/${st.hp.toFixed(0)}</td><td><button class="btn xs ghost" data-a="dismiss" data-t="${ty}" data-r="${r}">zwolnij 10</button></td></tr>`; }
      h += `<table class="tbl"><tr><th>Jednostka</th><th>St.</th><th class="num">Liczba</th><th class="num">A/O/W</th><th></th></tr>${rows || '<tr><td colspan=5>Brak wojska.</td></tr>'}</table>`;
      h += PG.lazaret(s);
    }
    if (t === 'train') {
      for (const bid of ['koszary', 'pikinierzy', 'lucznicy', 'stajnia', 'warsztat']) { const d = C.buildings[bid]; const q = s.trainQ[bid]; h += `<div class="row box"><span>${C.units[d.unit].icon} <b>${d.name}</b> poz. ${s.b[bid]} · stopień maks. ${U.roman(P.army.maxTier(s, d.unit)) || '—'}</span>${q ? `<span>${q.n}× ${U.roman(q.tier)} · ${UI.timer(q.end)}</span>` : '<span class="muted">wolne</span>'}<button class="btn sm" data-a="bld" data-b="${bid}">Otwórz</button></div>`; }
      h += `<h3>Jednostki fortowe</h3>`;
      for (const fid in C.forts) { const f = C.forts[fid]; const owned = P.forts.owned(s, fid); h += `<div class="box"><b>${f.name}</b> – ${owned ? '<span class="good">sojusz kontroluje fort</span>' : '<span class="muted">brak kontroli</span>'}${f.units.map((u) => { const bid = 'fort_' + fid; const q = s.trainQ[bid]; const tier = P.army.maxTier(s, u); return `<div class="row"><span>${C.units[u].icon} ${C.units[u].name} ${U.roman(tier)} – ${C.units[u].role}; ${C.units[u].weak}</span>${owned ? (q ? `<span>${q.n}× · ${UI.timer(q.end)}</span>` : `<input type="number" id="fq_${u}" value="50" min="1" max="${P.army.batchMax(s, bid)}"><button class="btn xs" data-a="trainFort" data-u="${u}" data-r="${tier}">Szkol</button>`) : ''}</div>`; }).join('')}</div>`; }
      h += `<p class="muted">Limit udziału wojsk specjalnych: ${U.pct(C.fortRules.shareLimit)} armii; dzienny limit rekrutacji fortowej: ${C.fortRules.dailyRecruit}. Po utracie fortu wyszkolone jednostki zostają.</p>`;
    }
    if (t === 'marches') {
      if (!s.marches.length) h += `<p class="muted">Brak aktywnych marszów. Wybierz cel na mapie.</p>`;
      for (const m of s.marches) h += `<div class="box"><div class="row"><b>⚑ ${U.esc(m.tname)}</b><span>${{ out: 'w drodze', return: 'powrót', gather: 'zbieranie', garrison: 'wsparcie/garnizon' }[m.state]} · ${UI.timer(m.next)}</span></div><p class="muted">${U.full(U.armyCount(m.army))} żołnierzy${m.hero ? ' · dowódca ' + C.heroes[m.hero].name : ''}${m.energy ? ' · zarezerwowano ' + m.energy + '⚡' : ''}</p>${['out', 'gather', 'garrison'].includes(m.state) ? `<button class="btn sm ghost" data-a="recall" data-m="${m.id}">${m.state === 'out' ? 'Zawróć (zwrot energii)' : 'Zakończ i wróć'}</button>` : ''} <button class="btn sm ghost" data-a="showOnMap" data-o="${m.targetId}">Na mapie</button></div>`;
    }
    if (t === 'defense') {
      const f = P.raids.fortSpec(s); const heroes = Object.keys(s.heroes);
      h += `<div class="box"><h3>🛡️ Obrona osady</h3><p>Obrona działa także, gdy jesteś offline. Oddziały na wyprawie nie bronią osady.</p><p>Dowódca obrony: <select data-a2="defHero"><option value="">— brak —</option>${heroes.map((x) => `<option value="${x}" ${s.defense.hero === x ? 'selected' : ''}>${C.heroes[x].icon} ${C.heroes[x].name}</option>`).join('')}</select></p><p>Tryb wież: <b>${s.defense.towers === 'piechota' ? 'ostrzał piechoty' : 'zwalczanie machin'}</b> (zmień w panelu Wież)</p><p>Garnizon: <b>${U.full(U.armyCount(s.units))}</b> · siła ${U.fmt(P.armyPower(s.units, P.sideMods(s, { hero: s.defense.hero, home: true })))}${s.alliance && U.armyCount(s.alliance.reinf || {}) ? ` · posiłki sojuszu: ${U.full(U.armyCount(s.alliance.reinf))}` : ''}</p><p>Mury +${U.pct(f.wallBonus)} obrony · brama ${U.fmt(f.wallHp)} · wieże ${U.fmt(f.towers)}/runda${s.damagedWalls ? ` · <span class="bad">uszkodzenia ${U.pct(s.damagedWalls)}</span>` : ''}</p><p>Chronione zapasy: ${U.pct(P.eco.protectedPct(s))} pojemności magazynu.</p></div>`;
      h += s.raid.incoming ? `<div class="alert">⚠️ Nadciąga: ${U.esc(s.raid.incoming.from)} · ${U.full(U.armyCount(s.raid.incoming.army))} wojowników · za ${UI.timer(s.raid.incoming.arrive)}${UI.armyTable(s.raid.incoming.army)}</div>` : s.shield > s.time ? `<p class="info">Ochrona początkowa jeszcze ${UI.timer(s.shield)}. Atak na innego gracza przerywa ochronę.</p>` : `<p class="muted">Zwiadowcy nie widzą zagrożenia.</p>`;
      h += `<p class="muted">Skutki porażki: straty, ranni, utrata części niechronionych zasobów i uszkodzenie umocnień. Porażka nie kasuje poziomów budynków ani bohaterów.</p>`;
    }
    if (t === 'info') {
      h += `<table class="tbl"><tr><th>Rodzaj</th><th>Rola</th><th>Ograniczenie</th></tr>${['miecznik', 'pikinier', 'lucznik', 'kawaleria', 'taran', 'tarcznik', 'kusznik', 'konny_lucznik', 'lekki_jezdziec', 'saper', 'balista'].map((u) => `<tr><td>${C.units[u].icon} ${C.units[u].name}</td><td>${C.units[u].role}</td><td>${C.units[u].weak}</td></tr>`).join('')}</table><p class="muted">Sześć stopni wyszkolenia (I–VI) wymaga poziomów budynku 1/6/11/16/21/26 i badania w Akademii. Wcześniej wyszkolone oddziały można przeszkolić do wyższego stopnia.</p>`;
    }
    return h;
  };
  A.dismiss = (d) => P.army.dismiss(P.S, d.t, +d.r, 10);
  A.recall = (d) => { const m = P.S.marches.find((x) => x.id === d.m); if (m) P.world.recall(P.S, m); };
  A.trainFort = (d) => P.army.train(P.S, d.u, +d.r, +document.getElementById('fq_' + d.u).value);
  P.act2.defHero = (el) => { P.S.defense.hero = el.value || null; };

  // ================= TOWARZYSZE =================
  PG.heroes = (s) => {
    let h = `<h1>🎖️ Towarzysze</h1><p class="muted">Towarzyszy zdobywa się jako całe postacie – przez historie na mapie, zlecenia i wydarzenia. Rozwój: doświadczenie, specjalizacja i próba awansu. Maks. poziom: ${P.heroes.cap(s)} (Sala towarzyszy).</p><div class="cards">`;
    for (const id in C.heroes) {
      const d = C.heroes[id]; const hh = s.heroes[id];
      if (!hh) { h += `<div class="card locked"><div class="hIcon">❔</div><b>${d.name}</b><small>${d.role}</small><p class="muted">${d.origin}</p></div>`; continue; }
      const need = P.heroes.xpNeed(hh.lvl);
      h += `<div class="card" data-a="hero" data-h="${id}"><div class="hIcon">${d.icon}</div><b>${d.name}</b><small>${d.role} · poz. ${hh.lvl} · awans ${hh.promo}/5</small><div class="pbar"><i style="width:${Math.min(100, hh.xp / need * 100)}%"></i></div><p class="muted">${P.heroes.effText(P.heroes.effects(s, id))}</p>${P.heroes.busy(s, id) ? '<span class="tag2">w drodze</span>' : ''}</div>`;
    }
    return h + '</div>';
  };
  A.hero = (d) => UI.modal((s) => {
    const id = d.h; const hd = C.heroes[id]; const hh = s.heroes[id]; const tr = P.heroes.trial(s, id);
    let h = `<h2>${hd.icon} ${hd.name} – ${hd.role}</h2><p>Poziom <b>${hh.lvl}</b> (limit ${P.heroes.lvlCap(s, id)}) · doświadczenie ${U.fmt(hh.xp)} / ${U.fmt(P.heroes.xpNeed(hh.lvl))} · awanse ${hh.promo}/${C.heroPromotions.length}</p><p>Premie: ${P.heroes.effText(P.heroes.effects(s, id))}</p><p class="muted">Pochodzenie: ${hd.origin}</p>`;
    h += `<h3>Specjalizacje</h3>${hd.specs.map((sp) => `<div class="row"><span>${hh.spec.includes(sp.id) ? '✔' : '○'} <b>${sp.name}</b> – ${P.heroes.effText(sp.eff)}</span></div>`).join('')}`;
    if (!tr.max) {
      h += `<h3>Próba awansu ${hh.promo + 1}</h3><ul class="req"><li class="${tr.lvlOk ? 'good' : 'bad'}">Poziom ${C.heroPromotions[hh.promo]}</li><li class="${tr.taskOk ? 'good' : 'bad'}">Zadanie charakterystyczne: ${tr.task} (${tr.have}/${tr.need})</li><li class="${tr.stoneOk ? 'good' : 'bad'}">${C.items[tr.stone].icon} ${C.items[tr.stone].name} ×${tr.stones} (masz ${s.items[tr.stone] || 0})</li><li class="${tr.silverOk ? 'good' : 'bad'}">🪙 ${U.fmt(tr.silver)} srebra</li></ul>`;
      const ok = tr.lvlOk && tr.taskOk && tr.stoneOk && tr.silverOk;
      if (hh.promo === 0) h += hd.specs.map((sp) => `<button class="btn" data-a="promote" data-h="${id}" data-sp="${sp.id}" ${ok ? '' : 'disabled'}>Awans: ${sp.name}</button> `).join('');
      else h += `<button class="btn" data-a="promote" data-h="${id}" ${ok ? '' : 'disabled'}>Wykonaj awans</button>`;
      h += `<p class="muted">Kamienie awansu zdobywasz w ruinach, zleceniach i wydarzeniach – możesz celować w konkretny rodzaj. Brak losowej szansy niepowodzenia.</p>`;
    } else h += `<p class="good">Wszystkie awanse wykonane.</p>`;
    h += `<h3>Wyposażenie towarzysza</h3>${Object.entries(C.heroSlots).map(([sl, nm]) => { const gid = hh.gear[sl]; const opts = Object.values(s.gear).filter((g) => g.kind === 'hero' && g.slot === sl); return `<div class="row"><span>${nm}: <b>${gid && s.gear[gid] ? P.forge.name(s.gear[gid]) : '—'}</b></span><select data-a2="heroGear" data-h="${id}" data-sl="${sl}"><option value="">— zdejmij —</option>${opts.map((g) => `<option value="${g.id}" ${gid === g.id ? 'selected' : ''}>${P.forge.name(g)}</option>`).join('')}</select></div>`; }).join('')}`;
    return h;
  }, { live: true });
  A.promote = (d) => P.heroes.promote(P.S, d.h, d.sp);
  P.act2.heroGear = (el) => { const s = P.S; const h = s.heroes[el.dataset.h]; if (!el.value) delete h.gear[el.dataset.sl]; else P.forge.equip(s, el.value, 'hero:' + el.dataset.h); };

  // ================= TABLICA =================
  PG.board = (s) => {
    let h = `<h1>📋 Tablica ogłoszeń</h1><div class="box"><p>⚡ ${s.energy.v}/${C.energy.max} · oferty ${s.board.offers.length}/${C.board.limit} · przyjęte ${s.board.taken.length}/${C.board.activeMax} · nowe ${C.board.perRefresh} za ${UI.timer(P.board.nextRefresh(s))}</p><p class="muted">Co 8 godzin pojawiają się 3 nowe zlecenia (do 9 na dobę). Niewykonane oferty gromadzą się do limitu 9 i nie wygasają. Odświeżenie nie kasuje przyjętych zadań. Energia pobierana jest dopiero przy wysłaniu wojska.</p></div>`;
    if (s.board.taken.length) { h += `<h3>Przyjęte</h3>`; for (const o of s.board.taken) { const obj = P.world.obj(s, o.objId); h += `<div class="box task"><div class="row"><b>${P.TASKS[o.type].icon} ${U.esc(o.title)}</b><span>poz. ${o.lvl} · ${o.energy}⚡</span></div><p class="muted">${P.TASKS[o.type].prep}</p><p>Nagroda: ${P.rewardStr(o.reward)}</p>${obj && obj.busy ? '<p class="good">Wojsko w drodze.</p>' : `<button class="btn sm" data-a="march" data-o="${o.objId}" data-k="task" data-e="${o.energy}">Wyślij wojsko</button>`} <button class="btn sm ghost" data-a="showOnMap" data-o="${o.objId}">Na mapie</button> <button class="btn sm ghost" data-a="abandon" data-t="${o.id}">Porzuć</button></div>`; } }
    h += `<h3>Oferty</h3>`;
    for (const o of s.board.offers) { const T = P.TASKS[o.type]; const myPow = P.armyPower(s.units); const thr = o.threat; h += `<div class="box task"><div class="row"><b>${T.icon} ${T.name}: ${U.esc(o.title)}</b><span>poz. ${o.lvl}</span></div><p class="muted">${T.prep}${o.chain ? ` <span class="gold">Historia: ${P.board.CHAINS[o.chain].desc}</span>` : ''}</p><p>Nagroda: ${P.rewardStr(o.reward)}</p><p>Zagrożenie: ~${U.fmt(thr)} (Twój garnizon ${U.fmt(myPow)}) · koszt ${o.energy}⚡ · przewidywany czas ~${U.dur(o.estTime)}${o.cargo ? ` · ładunek do przewiezienia ${U.fmt(o.cargo)}` : ''}</p><button class="btn sm" data-a="accept" data-t="${o.id}">Przyjmij</button></div>`; }
    if (!s.board.offers.length) h += `<p class="muted">Brak ofert. Wróć po odnowieniu tablicy.</p>`;
    h += `<h3>Historie</h3>${Object.entries(P.board.CHAINS).map(([k, c]) => `<p>${s.heroes[c.hero] ? '✔' : '○'} <b>${c.name}</b> (${s.board.chains[k] || 0}/${c.steps}) – ${c.desc} ${s.b.siedziba < c.unlock ? `<span class="muted">(od siedziby ${c.unlock})</span>` : ''}</p>`).join('')}`;
    return h;
  };
  A.accept = (d) => P.board.accept(P.S, d.t);
  A.abandon = (d) => P.board.abandon(P.S, d.t);

  // ================= SOJUSZ =================
  PG.alliance = (s) => {
    const a = s.alliance;
    if (!a) {
      let h = `<h1>🚩 Sojusz</h1><p>Sojusz zapewnia pomoc w budowie, posiłki, wspólne badania, walkę o forty i koronę.</p>`;
      if (s.b.siedziba < 2) h += `<p class="muted">Najpierw odbuduj siedzibę (poz. 2).</p>`;
      for (let i = 0; i < 3; i++) { const n = s.map.objs.filter((o) => o.type === 'bot' && o.ali === i).length; h += `<div class="box row"><span><b>${s.map.allies[i]}</b> [${s.map.tags[i]}] · ok. ${n + 20} członków · ${['blisko Twojej osady, przyjaźni nowym', 'agresywni, silni w PvP', 'zdyscyplinowani, mniejsi'][i]}</span><button class="btn sm" data-a="joinAli" data-i="${i}" ${s.b.siedziba < 2 ? 'disabled' : ''}>Dołącz</button></div>`; }
      h += `<div class="box"><h3>Załóż własny sojusz</h3><input id="aliName" placeholder="Nazwa" maxlength="28"> <input id="aliTag" placeholder="Skrót" maxlength="4" style="width:70px"> <button class="btn sm" data-a="createAli" ${s.b.siedziba < 2 ? 'disabled' : ''}>Załóż</button><p class="muted">Własny sojusz zaczyna od Ciebie – nowi członkowie dołączają z czasem (limit 40, badanie do 100).</p></div>`;
      return h;
    }
    let h = `<h1>🚩 ${U.esc(a.name)} [${a.tag}]</h1><p>Rola: <b>${a.role}</b> · członkowie ${a.members.length + 1}/${P.alliance.limit(s)} · aktywni ${P.alliance.active(s)} · 🔰 ${U.fmt(s.coins)} monet</p>` + UI.tabs('ali', [['over', 'Przegląd'], ['members', 'Członkowie'], ['research', 'Badania'], ['shop', 'Sklep'], ['terr', 'Terytorium'], ['war', 'Forty i korona']]);
    const t = UI.cur('ali', 'over');
    if (t === 'over') {
      h += `<div class="box"><p>${U.esc(a.desc)}</p><p>Dzisiejsze monety: ${a.coinsToday}/${C.alliance.coinCapDaily} · wkład: ${a.donatedToday}/${C.alliance.donateDaily}</p><button class="btn sm" data-a="helpAll">🤝 Pomóż wszystkim</button> <button class="btn sm" data-a="go" data-p="chat">💬 Czat sojuszu</button></div>`;
      h += `<div class="box"><p>Pomoc przy budowie/badaniu: do ${P.alliance.helpLimit(s)} pomocy (każda −1 min lub −1%). Poselstwo przyjmie do ${U.fmt(P.alliance.reinfCap(s))} posiłków.</p><p>Zgrupowania: wybierz na mapie wielką bestię, fort lub obóz – sojusznicy dołączą własnym wojskiem; każdy dostaje własny raport.</p></div>`;
      h += `<h3>Ogłoszenia</h3>${a.news.slice(0, 12).map((n) => `<p class="muted">${U.clock(n.t)} – ${U.esc(n.m)}</p>`).join('') || '<p class="muted">Brak.</p>'}<button class="btn sm ghost" data-a="leaveAli">Opuść sojusz</button>`;
    }
    if (t === 'members') { const list = [{ name: s.ruler.name + ' (Ty)', role: a.role, power: P.armyPower(P.army.totalArmy(s)), active: true, lvl: s.b.siedziba }].concat(a.members).sort((x, y) => C.alliance.roles.indexOf(x.role) - C.alliance.roles.indexOf(y.role) || y.power - x.power); h += `<table class="tbl"><tr><th>Członek</th><th>Rola</th><th class="num">Siła</th><th></th></tr>${list.map((m) => `<tr><td>${m.active ? '🟢' : '⚪'} ${U.esc(m.name)}</td><td>${m.role}</td><td class="num">${U.fmt(m.power)}</td><td>${m.name.includes('(Ty)') ? '' : `<button class="btn xs ghost" data-a="pm" data-n="${U.esc(m.name)}">✉</button>`}</td></tr>`).join('')}</table>`; }
    if (t === 'research') {
      h += `<p>Priorytet: <b>${C.allianceResearch[a.priority].name}</b>. Członkowie przekazują zasoby w ramach dziennego limitu i otrzymują monety sojuszu.</p><div class="row"><span>Wkład: ${P.costStr(P.alliance.donateCost(s), s)} → +${C.alliance.coinsPerDonate} 🔰</span><button class="btn sm" data-a="donate" data-n="1">Wpłać ×1</button><button class="btn sm" data-a="donate" data-n="5">×5</button></div>`;
      let tab = '';
      for (const id in C.allianceResearch) { const r = C.allianceResearch[id]; const L = a.research[id] || 0; const need = P.alliance.researchNeed(id, L); const pr = a.prog[id] || 0; if (r.tab !== tab) { tab = r.tab; h += `<h3>${tab}</h3>`; } h += `<div class="box row"><span><b>${r.name}</b> ${L}/5 – ${r.desc}${L < 5 ? `<div class="pbar"><i style="width:${Math.min(100, pr / need * 100)}%"></i></div><small>${U.fmt(pr)} / ${U.fmt(need)}</small>` : ' <span class="good">ukończone</span>'}</span>${L < 5 && a.priority !== id && ['Przywódca', 'Zastępca'].includes(a.role) ? `<button class="btn xs" data-a="aliPrio" data-r="${id}">Priorytet</button>` : a.priority === id ? '<span class="tag2">priorytet</span>' : ''}</div>`; }
    }
    if (t === 'shop') h += PG.aliShop(s);
    if (t === 'terr') {
      const inT = P.alliance.inTerritory(s);
      h += `<div class="box"><p>Siedziba sojuszu: (${a.hq.x}, ${a.hq.y}) · strażnice: ${a.towers.length}</p><p>Twoja osada ${inT ? '<b class="good">jest na aktywnym terenie</b> (premie: obrona terytorialna, znajomość terenu)' : '<b class="bad">jest poza terenem</b> – kup przeniesienie osady w sklepie sojuszu'}.</p><p class="muted">Nakładające się obszary nie zwielokrotniają premii. Odcięta strażnica daje 24 h na przywrócenie połączenia. Obrona terytorialna nie działa przy atakowaniu innych ani w walkach o forty.</p></div>`;
      for (const tw of a.towers) h += `<p>${tw.connected ? '🟦' : '🟥'} ${tw.name} (${tw.x}, ${tw.y}) ${tw.connected ? '' : '– odcięta!'}</p>`;
      if (a.project) h += `<div class="box"><b>${a.project.name}</b><div class="pbar"><i style="width:${Math.min(100, a.project.prog / a.project.need * 100)}%"></i></div><small>${U.fmt(a.project.prog)} / ${U.fmt(a.project.need)}</small><br><button class="btn sm" data-a="contribProject">Wnieś 2000 🪵 + 2000 🪨 (+15 🔰)</button></div>`;
      else h += `<button class="btn" data-a="startProject">Rozpocznij projekt: strażnica graniczna</button>`;
    }
    if (t === 'war') {
      for (const f of P.forts.list(s)) h += `<div class="box row"><span>🛡️ <b>${f.name}</b> – ${f.owner === 'neutral' ? 'neutralny' : s.map.allies[f.owner]}${f.owner === a.botAli ? ' <span class="good">(nasz)</span>' : ''}<br><small>${C.forts[f.fort].units.map((u) => C.units[u].name).join(' + ')}</small></span><button class="btn xs ghost" data-a="showOnMap" data-o="${f.id}">Mapa</button></div>`;
      h += `<p>Okna walk o forty: co ${C.fortRules.windowEveryDays} dni, ${C.fortRules.windowHourUTC}:00–${C.fortRules.windowHourUTC + C.fortRules.windowLenH}:00 UTC. ${P.forts.windowOpen(s) ? '<b class="good">Trwa teraz!</b>' : 'Następne: ' + U.clock(P.forts.nextWindow(s))}</p>`;
      const p = P.crown.period(s); h += `<div class="box"><h3>👑 Wojna o Koronę</h3><p>${P.crown.active(s) ? `<b class="good">Trwa</b> do ${U.clock(p.end)}. Twoje punkty: ${U.fmt(s.crownPts || 0)}` : `Następna: ${U.clock(p.start)} (co ${C.crown.everyDays} dni, ${C.crown.durationDays} dni)`}</p><p class="muted">Cele: Przełęcz Wilcza, Archiwum Kronikarzy, Przeprawa Koronna i finał przy Zamku Koronnym. Zwycięski sojusz zyskuje premię; najbardziej zasłużony gracz – tytuł Króla na ${C.crown.kingDays} dni.</p>${s.king > s.time ? `<p class="gold">👑 Jesteś Królem Pogranicza jeszcze ${UI.timer(s.king)}</p>` : ''}</div>`;
    }
    return h;
  };
  PG.aliShop = (s) => `<p>🔰 ${U.fmt(s.coins)} monet. Najcenniejsze pozycje mają tygodniowy limit na konto; zmiana sojuszu go nie odnawia.</p>${C.allianceShop.map((it) => { const used = (s.alliance ? s.alliance.shopWeek[it.id] : 0) || 0; return `<div class="box row"><span><b>${it.name}</b><br><small>${it.price} 🔰 · limit ${used}/${it.weekly} tyg.</small></span>${it.give.resPick ? `<select id="pick_${it.id}">${C.basic.map((k) => `<option value="${k}">${C.resources[k].name}</option>`).join('')}</select>` : ''}<button class="btn sm" data-a="aliBuy" data-i="${it.id}" ${used >= it.weekly || s.coins < it.price ? 'disabled' : ''}>Kup</button></div>`; }).join('')}`;
  A.joinAli = (d) => P.alliance.join(P.S, +d.i);
  A.createAli = () => P.alliance.create(P.S, document.getElementById('aliName').value, document.getElementById('aliTag').value);
  A.leaveAli = () => { if (confirm('Opuścić sojusz? Monety zostają u Ciebie.')) P.alliance.leave(P.S); };
  A.helpAll = () => P.alliance.helpAll(P.S);
  A.donate = (d) => P.alliance.donate(P.S, +d.n);
  A.aliPrio = (d) => P.alliance.setPriority(P.S, d.r);
  A.aliBuy = (d) => { const p = document.getElementById('pick_' + d.i); P.alliance.shopBuy(P.S, d.i, p && p.value); };
  A.startProject = () => P.alliance.startProject(P.S);
  A.contribProject = () => P.alliance.contribProject(P.S);
  A.pm = (d) => { UI.tab.chat = 'prywatne'; P.chat.post(P.S, 'prywatne', 'System', `Rozmowa z: ${d.n}`, true); UI.go('chat'); };

  // ================= WIĘCEJ =================
  PG.more = (s) => {
    const items = [['ruler', '👤', 'Profil władcy'], ['research', '📘', 'Badania'], ['forge', '⚒️', 'Kuźnia'], ['arena', '🏟️', 'Arena'], ['events', '🎪', 'Wydarzenia'], ['glory', '🏅', 'Chwała'], ['vip', '✨', 'VIP'], ['shop', '💎', 'Sklep'], ['reports', '📜', `Raporty${s.unread ? ' (' + s.unread + ')' : ''}`], ['chat', '💬', 'Czat'], ['chronicle', '📖', 'Kronika'], ['items', '🎒', 'Przedmioty'], ['log', '🗒️', 'Dziennik'], ['settings', '⚙️', 'Ustawienia']];
    return `<h1>Więcej</h1><div class="menuGrid">${items.map(([p, i, n]) => `<button class="mItem" data-a="go" data-p="${p}"><span>${i}</span>${n}</button>`).join('')}</div>`;
  };

  // ================= PROFIL WŁADCY =================
  PG.ruler = (s) => {
    const set = s.ruler.set; const vipL = P.vip.level(s);
    let h = `<h1>👤 ${U.esc(s.ruler.name)}</h1><div class="grid2"><div><div class="ruler3d" id="ruler3d"><div class="rot" id="rulerRot" style="transform:rotateY(${s.ruler.rot || 0}deg)">${PG.rulerSvg(s, false)}${PG.rulerSvg(s, true)}</div></div><p class="muted center">Przeciągnij, aby obrócić postać.</p></div><div>`;
    h += `<p>Status: <b>${P.ruler.title(s)}</b>${s.king > s.time ? ' · <b class="gold">👑 Król Pogranicza</b>' : ''}</p><p>Tytuł chwały: <b>${s.glory.title || '—'}</b></p>${vipL && !s.hideVip ? `<p>✨ VIP ${vipL}</p>` : ''}<p>Chwała: ${U.fmt(s.glory.cur)} · zabici: ${U.fmt(s.stats.kills)}</p>`;
    h += `<h3>Zestawy wyposażenia</h3><div class="row"><button class="btn sm ${set === 'war' ? 'on' : 'ghost'}" data-a="rSet" data-v="war">⚔️ Wojenny</button><button class="btn sm ${set === 'eco' ? 'on' : 'ghost'}" data-a="rSet" data-v="eco">🌾 Gospodarczy</button></div><p class="muted">Aktywny zestaw działa na całe konto. Zmiana zablokowana podczas marszu, obrony lub fali wydarzenia.</p>`;
    for (const which of ['war', 'eco']) { h += `<h4>${which === 'war' ? 'Zestaw wojenny' : 'Zestaw gospodarczy'}${which === set ? ' (aktywny)' : ''}</h4>`; for (const [sl, nm] of Object.entries(C.rulerSlots)) { const gid = s.ruler.sets[which][sl]; const opts = Object.values(s.gear).filter((g) => g.kind === 'ruler' && g.slot === sl); const st = (C.gearStats[sl] || {})[which] || {}; h += `<div class="row"><span>${nm}: <b>${gid && s.gear[gid] ? P.forge.name(s.gear[gid]) : '—'}</b> <small class="muted">${gid && s.gear[gid] ? P.heroes.effText(Object.fromEntries(Object.entries(st).map(([k, v]) => [k, v * (s.gear[gid].tier + 1) * (1 + 0.1 * s.gear[gid].refine)]))) : ''}</small></span><select data-a2="rGear" data-set="${which}" data-sl="${sl}"><option value="">—</option>${opts.map((g) => `<option value="${g.id}" ${gid === g.id ? 'selected' : ''}>${P.forge.name(g)}</option>`).join('')}</select></div>`; } }
    h += `<h3>Wygląd</h3><div class="row">Osada: <select data-a2="skin"><option value="base">Podstawowy</option>${[['skin_jesien', 'Jesienne Pogranicze'], ['skin_zima', 'Zimowa Straż'], ['skin_turniej', 'Turniejowy']].filter(([k]) => s.cosmetics[k]).map(([k, n]) => `<option value="${k}" ${s.skin === k ? 'selected' : ''}>${n}</option>`).join('')}</select></div><p class="muted">Wyglądy nie zmieniają statystyk. Kupisz je w sklepie, na arenie i za poziomy VIP.</p>`;
    h += `<p><button class="btn sm ghost" data-a="rename">Zmień imię</button> ${vipL ? `<label><input type="checkbox" data-a2="hideVip" ${s.hideVip ? 'checked' : ''}> ukryj oznaczenie VIP</label>` : ''}</p></div></div>`;
    return h;
  };
  PG.rulerSvg = (s, back) => {
    const set = s.ruler.sets[s.ruler.set]; const has = (sl) => set[sl] && s.gear[set[sl]];
    const tier = (sl) => has(sl) ? s.gear[set[sl]].tier : -1;
    const metal = (t) => ['#8a8a8a', '#9a9a9a', '#b0b4ba', '#c9ccd2', '#d9c27a', '#e8d38a'][t] || '#7a6a5a';
    const cape = s.cosmetics.cape_gold ? '#a8862a' : s.cosmetics.vip5 ? '#6a1f2a' : '#2c4a8a';
    const crown = s.king > s.time;
    let g = `<svg viewBox="0 0 200 300" class="rulerFace ${back ? 'back' : 'front'}"><ellipse cx="100" cy="285" rx="60" ry="10" fill="rgba(0,0,0,.25)"/>`;
    if (s.cosmetics.vip12) g += `<rect x="20" y="10" width="160" height="270" rx="10" fill="rgba(120,60,30,.2)"/>`;
    // peleryna
    g += `<path d="M62,90 Q100,80 138,90 L${back ? 150 : 146},270 L${back ? 50 : 54},270 Z" fill="${cape}" ${back ? '' : 'opacity=".55"'}/>`;
    // nogi i buty
    g += `<rect x="78" y="190" width="18" height="75" fill="#4a3a2a"/><rect x="104" y="190" width="18" height="75" fill="#4a3a2a"/>`;
    g += `<rect x="74" y="258" width="26" height="14" rx="4" fill="${has('buty') ? metal(tier('buty')) : '#3a2a1a'}"/><rect x="100" y="258" width="26" height="14" rx="4" fill="${has('buty') ? metal(tier('buty')) : '#3a2a1a'}"/>`;
    // tułów / pancerz
    g += `<path d="M70,95 L130,95 L136,195 L64,195 Z" fill="${has('pancerz') ? metal(tier('pancerz')) : '#7a5a3a'}"/>`;
    if (!back) { g += `<rect x="64" y="160" width="72" height="8" fill="#3a2a1a"/><circle cx="100" cy="164" r="5" fill="${M2('gold')}"/>`; if (has('insygnium')) g += `<circle cx="100" cy="118" r="9" fill="${M2('gold')}" stroke="#7a5a1a"/><path d="M95,118 l5,-6 l5,6 l-5,6 z" fill="#b33"/>`; }
    // ręce, rękawice
    g += `<rect x="50" y="98" width="18" height="72" rx="8" fill="${has('pancerz') ? metal(tier('pancerz')) : '#7a5a3a'}"/><rect x="132" y="98" width="18" height="72" rx="8" fill="${has('pancerz') ? metal(tier('pancerz')) : '#7a5a3a'}"/>`;
    g += `<circle cx="59" cy="176" r="9" fill="${has('rekawice') ? metal(tier('rekawice')) : '#e0b48c'}"/><circle cx="141" cy="176" r="9" fill="${has('rekawice') ? metal(tier('rekawice')) : '#e0b48c'}"/>`;
    // broń
    if (has('bron')) g += back ? `<rect x="96" y="100" width="8" height="110" fill="${metal(tier('bron'))}" transform="rotate(20 100 150)"/>` : `<rect x="138" y="120" width="6" height="110" fill="${metal(tier('bron'))}"/><rect x="128" y="168" width="26" height="6" fill="#5a3a1a"/>`;
    // głowa i hełm
    g += `<circle cx="100" cy="70" r="22" fill="#e0b48c"/>`;
    if (back) g += `<path d="M78,66 Q100,40 122,66 L122,78 Q100,86 78,78 Z" fill="#5a3a1a"/>`;
    else g += `<circle cx="92" cy="70" r="2.5" fill="#2a1a0a"/><circle cx="108" cy="70" r="2.5" fill="#2a1a0a"/><path d="M92,82 q8,5 16,0" stroke="#7a4a2a" fill="none" stroke-width="2"/>`;
    if (has('helm')) g += `<path d="M76,68 Q100,30 124,68 L124,60 Q100,38 76,60 Z" fill="${metal(tier('helm'))}"/><path d="M76,62 Q100,34 124,62" fill="${metal(tier('helm'))}"/>${back ? '' : `<rect x="97" y="50" width="6" height="26" fill="${metal(tier('helm'))}"/>`}`;
    if (crown) g += `<path d="M80,52 l6,-16 l8,12 l6,-16 l6,16 l8,-12 l6,16 z" fill="${M2('gold')}" stroke="#8a6a1a"/>`;
    return g + `</svg>`;
  };
  const M2 = (k) => ({ gold: '#c9a34a' }[k]);
  PG.bindRuler = (s) => {
    const el = document.getElementById('ruler3d'); if (!el) return;
    let sx = null, r0 = 0;
    const down = (e) => { sx = (e.touches ? e.touches[0] : e).clientX; r0 = s.ruler.rot || 0; };
    const move = (e) => { if (sx == null) return; const x = (e.touches ? e.touches[0] : e).clientX; s.ruler.rot = r0 + (x - sx) * 0.8; document.getElementById('rulerRot').style.transform = `rotateY(${s.ruler.rot}deg)`; };
    const up = () => { sx = null; };
    el.onmousedown = down; el.onmousemove = move; el.onmouseup = up; el.onmouseleave = up; el.ontouchstart = down; el.ontouchmove = move; el.ontouchend = up;
  };
  A.rSet = (d) => P.ruler.switchSet(P.S, d.v);
  A.rename = () => { const n = prompt('Imię władcy:', P.S.ruler.name); if (n) P.S.ruler.name = n.slice(0, 24); };
  P.act2.rGear = (el) => { const s = P.S; if (!el.value) delete s.ruler.sets[el.dataset.set][el.dataset.sl]; else P.forge.equip(s, el.value, 'ruler:' + el.dataset.set); };
  P.act2.skin = (el) => { P.S.skin = el.value; };
  P.act2.hideVip = (el) => { P.S.hideVip = el.checked; };

  // ================= BADANIA =================
  PG.research = (s) => {
    const tabs = ['Wojsko', 'Surowce', 'Ekonomia i administracja'];
    let h = `<h1>📘 Badania osobiste</h1><p class="muted">Akademia poz. ${s.b.akademia}. Jedna kolejka badań. Pełny rozwój wszystkich specjalizacji to cel długoterminowy (ok. rok lub dłużej); użyteczne specjalizacje zdobywa się znacznie wcześniej.</p>`;
    if (s.rq) h += `<div class="box"><b>Trwa: ${C.research[s.rq.id].name} ${s.rq.to}</b>${UI.bar(s.rq.start, s.rq.end)}${UI.timer(s.rq.end)} <button class="btn xs" data-a="qSpeed" data-k="r">⏩ Przyspiesz / pomoc</button></div>`;
    h += UI.tabs('res', tabs.map((t) => [t, t]));
    const cur = UI.cur('res', 'Wojsko');
    for (const id in C.research) {
      const r = C.research[id]; if (r.tab !== cur) continue; const L = s.research[id] || 0; const nx = L + 1;
      if (L >= r.max) { h += `<div class="box row"><span><b>${r.name}</b> ${L}/${r.max} <span class="good">✔</span><br><small class="muted">${r.desc}</small></span></div>`; continue; }
      const can = P.res.can(s, id); const rq = P.res.reqs(s, id, nx);
      h += `<div class="box"><div class="row"><b>${r.name} ${L}/${r.max}</b><button class="btn sm" data-a="research" data-r="${id}" ${can.ok ? '' : 'disabled'}>Badaj ${nx}</button></div><small class="muted">${r.desc}${r.tierOf ? ` Następny: stopień ${U.roman(nx + 1)}.` : ''}</small><p>${P.costStr(P.res.cost(id, nx), s)} · ${U.dur(P.res.time(s, id, nx))}</p><p>${rq.map((x) => `<span class="${x.ok ? 'good' : 'bad'}">${x.ok ? '✔' : '✖'} ${x.t}</span>`).join(' · ')}</p></div>`;
    }
    return h;
  };
  A.research = (d) => P.res.start(P.S, d.r);

  // ================= KUŹNIA =================
  PG.forge = (s) => {
    const mt = P.forge.maxTier(s);
    let h = `<h1>⚒️ Kuźnia</h1>`;
    if (s.b.kuznia <= 0) return h + `<p>Zbuduj kuźnię (siedziba 5), aby wytwarzać wyposażenie.</p><button class="btn" data-a="bld" data-b="kuznia">Kuźnia</button>`;
    h += `<p class="muted">Wytworzenie zgodnie z recepturą jest gwarantowane. Ulepszanie bez ryzyka zniszczenia. Rozbieranie odzyskuje część materiałów. Najwyższy stopień: ${C.gearTiers[mt]}.</p>`;
    if (s.forgeQ) h += `<div class="box">Wykuwanie: ${C.gearTiers[s.forgeQ.tier]} ${(s.forgeQ.kind === 'hero' ? C.heroSlots : C.rulerSlots)[s.forgeQ.slot]} ${UI.bar(s.forgeQ.start, s.forgeQ.end)}${UI.timer(s.forgeQ.end)}</div>`;
    const kind = UI.cur('fkind', 'ruler'); const tier = Math.min(mt, +UI.cur('ftier', 0));
    h += UI.tabs('fkind', [['ruler', 'Dla władcy'], ['hero', 'Dla towarzyszy']]);
    h += `<div class="row">Stopień: ${C.gearTiers.map((n, i) => `<button class="btn xs ${i === tier ? 'on' : 'ghost'}" data-a="tab" data-k="ftier" data-v="${i}" ${i > mt ? `disabled title="Kuźnia poz. ${C.gearTierForge[i]}"` : ''}>${n}</button>`).join('')}</div>`;
    const r = P.forge.recipe('bron', tier);
    h += `<p>Receptura: ${P.costStr({ iron: r.iron, silver: r.silver, items: r.items }, s)} · czas ${U.dur(P.forge.time(tier))}</p>`;
    h += `<div class="cards">${Object.entries(kind === 'hero' ? C.heroSlots : C.rulerSlots).map(([sl, nm]) => { const st = (C.gearStats[sl] || {}).war || {}; const eco = (C.gearStats[sl] || {}).eco; return `<div class="card"><b>${nm}</b><small>${P.heroes.effText(Object.fromEntries(Object.entries(st).map(([k, v]) => [k, v * (tier + 1)])))}${eco ? '<br>gosp.: ' + P.heroes.effText(Object.fromEntries(Object.entries(eco).map(([k, v]) => [k, v * (tier + 1)]))) : ''}</small><button class="btn sm" data-a="craft" data-sl="${sl}" data-k="${kind}" data-t="${tier}" ${s.forgeQ ? 'disabled' : ''}>Wykuj</button></div>`; }).join('')}</div>`;
    h += `<h3>Posiadane wyposażenie</h3>`;
    const gear = Object.values(s.gear);
    h += gear.length ? `<table class="tbl">${gear.map((g) => { const ow = P.forge.owner(s, g.id); return `<tr><td>${P.forge.name(g)}<br><small class="muted">${g.kind === 'hero' ? 'towarzysz' : 'władca'}${ow ? ' · założone' : ''}</small></td><td>${g.refine < C.gearRefineMax ? `<button class="btn xs" data-a="refine" data-g="${g.id}" title="${P.costStr(P.forge.refineCost(g)).replace(/<[^>]+>/g, '')}">Ulepsz</button>` : ''} <button class="btn xs ghost" data-a="dismantle" data-g="${g.id}">Rozbierz</button></td></tr>`; }).join('')}</table>` : '<p class="muted">Brak.</p>';
    h += `<p class="muted">Ulepszenie: srebro, sztaby i materiały władcy (z Obrony Pogranicza) lub materiały towarzyszy (z Wyprawy Zakonu i wielkich bestii).</p>`;
    return h;
  };
  A.craft = (d) => P.forge.craft(P.S, d.sl, +d.t, d.k);
  A.refine = (d) => P.forge.refine(P.S, d.g);
  A.dismantle = (d) => { if (confirm('Rozebrać przedmiot?')) P.forge.dismantle(P.S, d.g); };

  // ================= PRZEDMIOTY =================
  PG.items = (s) => `<h1>🎒 Przedmioty</h1><h3>Materiały i kamienie awansu</h3><table class="tbl">${Object.entries(C.items).map(([k, it]) => `<tr><td>${it.icon} ${it.name}</td><td class="num">${U.full(s.items[k] || 0)}</td></tr>`).join('')}</table><h3>Przyspieszenia</h3><table class="tbl">${Object.entries(C.speedups).map(([k, it]) => `<tr><td>${it.icon} ${it.name}</td><td class="num">${U.full(s.speedups[k] || 0)} min</td></tr>`).join('')}</table><h3>Waluty</h3><table class="tbl"><tr><td>💎 Rubiny</td><td class="num">${U.full(s.rubies)}</td></tr><tr><td>🔰 Monety sojuszu</td><td class="num">${U.full(s.coins)}</td></tr><tr><td>🎟️ Żetony areny</td><td class="num">${U.full(s.tokens)}</td></tr><tr><td>✨ Punkty VIP</td><td class="num">${U.full(s.vip)}</td></tr></table>`;

  // ================= ARENA =================
  PG.arena = (s) => {
    let h = `<h1>🏟️ Arena</h1>`;
    if (!P.arena.unlocked(s)) return h + `<p>Arena odblokowuje się przy siedzibie na poziomie ${C.arena.unlockSiedziba}. Zbuduj budynek Areny.</p><button class="btn" data-a="bld" data-b="arena">Arena</button>`;
    const Ar = P.arena.ensure(s); const t = P.arena.tries(s);
    const nextMon = (U.weekIdx(s.time) + 1) * 7 * C.DAY + 4 * C.DAY;
    h += `<div class="box"><p>Liga: <b>${C.arena.leagues[Ar.league]}</b> · punkty: <b>${Ar.pts}</b> · walki ${Ar.fights} (${Ar.wins} wygr.) · koniec sezonu za ${UI.timer(nextMon)}</p><p>Próby darmowe: <b>${t.free}/${C.arena.free}</b> · dokupione: dziś ${C.arena.paidDaily - t.paidLeftDay}/${C.arena.paidDaily}, sezon ${C.arena.paidWeekly - t.paidLeftWeek}/${C.arena.paidWeekly} (${C.arena.paidPrice} 💎) · 🎟️ ${s.tokens}</p><p class="muted">Walki automatyczne, bez strat wojska, bez rannych, bez energii. Liczą się rozwinięte jednostki, wyposażenie władcy i bohaterów. Nie działają premie terytorialne sojuszu ani posiłki.</p></div>`;
    h += UI.tabs('arena', [['fight', 'Walka'], ['team', 'Drużyny'], ['rank', 'Ranking'], ['shop', 'Sklep areny']]);
    const tab = UI.cur('arena', 'fight');
    if (tab === 'fight') {
      const offers = P.arena.offers(s);
      h += `<p>Twoja drużyna: siła <b>${U.fmt(P.arena.myPower(s))}</b> (${U.full(U.armyCount(s.arenaTeams.att.army))}/${C.arena.unitLimit})</p>`;
      for (const o of offers) h += `<div class="box row"><span><b>${U.esc(o.name)}</b> · siła ~${U.fmt(o.power)} · za wygraną <b>${o.pts} pkt</b> + ${C.arena.winTokens} 🎟️</span><button class="btn sm" data-a="arenaFight" data-o="${o.id}">Walcz${t.free <= 0 ? ` (${C.arena.paidPrice}💎)` : ''}</button></div>`;
      h += `<button class="btn sm ghost" data-a="arenaRefresh">Odśwież rywali (co godzinę)</button>`;
    }
    if (tab === 'team') {
      for (const which of ['att', 'def']) {
        const tm = s.arenaTeams[which];
        h += `<div class="box"><h3>${which === 'att' ? 'Drużyna atakująca' : 'Drużyna obronna'}</h3><p class="muted">Wojsko turniejowe – nie trzeba zabierać go z garnizonu. Wspólny limit ${C.arena.unitLimit} jednostek, tylko odblokowane stopnie.</p>`;
        h += `<table class="tbl">${['miecznik', 'pikinier', 'lucznik', 'kawaleria'].map((u) => { const mt = P.army.maxTier(s, u); if (!mt) return ''; const v = (tm.army[u] || {})[mt] || 0; return `<tr><td>${C.units[u].icon} ${C.units[u].name} ${U.roman(mt)}</td><td><input type="number" id="ar_${which}_${u}" class="arIn" data-w="${which}" data-u="${u}" data-r="${mt}" value="${v}" min="0" max="${C.arena.unitLimit}"></td></tr>`; }).join('')}</table>`;
        h += `<p>Dowódca: <select id="arh_${which}_hero" class="arHero" data-w="${which}" data-f="hero"><option value="">—</option>${Object.keys(s.heroes).map((x) => `<option value="${x}" ${tm.hero === x ? 'selected' : ''}>${C.heroes[x].name}</option>`).join('')}</select> Pomocnik: <select id="arh_${which}_helper" class="arHero" data-w="${which}" data-f="helper"><option value="">—</option>${Object.keys(s.heroes).map((x) => `<option value="${x}" ${tm.helper === x ? 'selected' : ''}>${C.heroes[x].name}</option>`).join('')}</select> Taktyka: <select id="arh_${which}_tactic" class="arHero" data-w="${which}" data-f="tactic">${Object.entries(C.tactics).map(([k, v]) => `<option value="${k}" ${tm.tactic === k ? 'selected' : ''}>${v.name}</option>`).join('')}</select></p><button class="btn sm" data-a="arenaSave" data-w="${which}">Zapisz drużynę</button></div>`;
      }
    }
    if (tab === 'rank') {
      const rk = P.arena.ranking(s); const me = rk.findIndex((r) => r.me);
      h += `<p>Grupa ${rk.length} uczestników · Twoje miejsce: <b>${me + 1}</b>. Awans: górne 10%, spadek: dolne 10% (przy min. 50 aktywnych).</p><table class="tbl"><tr><th>#</th><th>Gracz</th><th class="num">Pkt</th><th class="num">Wygr.</th></tr>${rk.slice(0, 15).map((r, i) => `<tr class="${r.me ? 'me' : ''}"><td>${i + 1}</td><td>${U.esc(r.name)}</td><td class="num">${r.pts}</td><td class="num">${r.wins}</td></tr>`).join('')}${me >= 15 ? `<tr class="me"><td>${me + 1}</td><td>${U.esc(rk[me].name)}</td><td class="num">${rk[me].pts}</td><td class="num">${rk[me].wins}</td></tr>` : ''}</table>`;
      h += `<h3>Nagrody sezonowe</h3><p>Udział (20 walk): ${C.arena.participation.tokens} 🎟️ + ${C.arena.participation.rubies} 💎</p><table class="tbl"><tr><th>Miejsce</th><th>💎</th><th>🎟️</th><th>Wyróżnienie</th></tr>${C.arena.placeRewards.map((p) => `<tr><td>${p[0] === p[1] ? p[0] : p[0] + '–' + p[1]}</td><td>${p[2]}</td><td>${p[3]}</td><td>${p[4]}</td></tr>`).join('')}</table>${Ar.cups.length ? `<p>🏆 Puchary: ${Ar.cups.map((c) => `${c.place}. miejsce (${c.league})`).join(', ')}</p>` : ''}`;
    }
    if (tab === 'shop') h += `<p>🎟️ ${s.tokens} · zakupy rozwojowe w tym tygodniu: ${Ar.devWeek || 0}/${C.arena.devWeekly}</p>${C.arena.shop.map((it) => `<div class="box row"><span><b>${it.name}</b> · ${it.price} 🎟️${it.dev ? ' · limit rozwojowy' : ' · kosmetyka'}${s.cosmetics[it.give.cosmetic] ? ' ✔' : ''}</span>${it.give.resPick ? `<select id="apick_${it.id}">${C.basic.map((k) => `<option value="${k}">${C.resources[k].name}</option>`).join('')}</select>` : ''}<button class="btn sm" data-a="arenaBuy" data-i="${it.id}" ${s.tokens < it.price || (it.give.cosmetic && s.cosmetics[it.give.cosmetic]) ? 'disabled' : ''}>Kup</button></div>`).join('')}`;
    return h;
  };
  A.arenaFight = (d) => P.arena.fight(P.S, d.o);
  A.arenaRefresh = () => P.arena.refresh(P.S);
  A.arenaBuy = (d) => { const p = document.getElementById('apick_' + d.i); P.arena.shopBuy(P.S, d.i, p && p.value); };
  A.arenaSave = (d) => {
    const s = P.S; const army = {}; document.querySelectorAll(`.arIn[data-w="${d.w}"]`).forEach((el) => { const v = Math.max(0, Math.floor(+el.value || 0)); if (v) army[el.dataset.u] = { [el.dataset.r]: v }; });
    const g = (f) => { const el = document.querySelector(`.arHero[data-w="${d.w}"][data-f="${f}"]`); return el && el.value || null; };
    P.arena.saveTeam(s, d.w, army, g('hero'), g('helper'), g('tactic') || 'rownowaga'); s.arena.offers = null;
  };

  // ================= WYDARZENIA =================
  PG.events = (s) => {
    P.events.addPts(s, 'x', 0);
    const cur = P.events.current(s); const inf = P.events.info[cur];
    let h = `<h1>🎪 Wydarzenia</h1><div class="box gold"><h3>Teraz: ${inf.name}</h3><p>${inf.desc}</p><p>Nagrody: ${inf.reward}</p></div>`;
    h += `<div class="box"><h3>Tygodniowe nagrody udziału</h3><p>Punkty udziału: <b>${s.ev.pts}</b> (polowania, zlecenia, obrona, zgrupowania, arena, wojna)</p>${C.events.thresholds.map((th, i) => `<div class="row"><span>Próg ${th} pkt → ${C.events.rubiesWeekly / 2} 💎</span><button class="btn sm" data-a="evClaim" data-i="${i}" ${s.ev.claimed[i] || s.ev.pts < th ? 'disabled' : ''}>${s.ev.claimed[i] ? 'Odebrano' : 'Odbierz'}</button></div>`).join('')}<p class="muted">Budżet 80 rubinów z wydarzeń jest wspólny dla tygodnia, bez premii za wydanie pieniędzy.</p></div>`;
    h += `<h3>Kalendarz tygodnia (UTC)</h3><table class="tbl">${[[1, 'Pon'], [2, 'Wt'], [3, 'Śr'], [4, 'Czw'], [5, 'Pt'], [6, 'Sob'], [0, 'Niedz']].map(([d, n]) => { const k = C.events.schedule[d]; return `<tr class="${U.weekday(s.time) === d ? 'me' : ''}"><td>${n}</td><td>${k === 'weekend' ? 'Wojna o Koronę (co 2 tyg.) / Szlaki Karawan' : P.events.info[k].name}</td></tr>`; }).join('')}</table>`;
    h += `<p class="muted">Obrona Pogranicza: fale o ${C.events.obronaWaves.map((x) => x + ':00').join(', ')} UTC (od siedziby 3). Wyprawa Zakonu: wiwerna pojawia się o 9:00 UTC (od siedziby 4). Podstawowe materiały mają też wolniejsze źródła poza wydarzeniami.</p>`;
    return h;
  };
  A.evClaim = (d) => P.events.claim(P.S, +d.i);

  // ================= VIP =================
  PG.vip = (s) => {
    const L = P.vip.level(s); const next = C.vip.levels[L]; const have = s.vip - P.vip.total(L);
    let h = `<h1>✨ VIP ${L}</h1><div class="box"><p>Punkty: <b>${U.full(s.vip)}</b>${next ? ` · do VIP ${L + 1}: ${U.full(have)} / ${U.full(next)}` : ' · poziom maksymalny'}</p>${next ? `<div class="pbar"><i style="width:${have / next * 100}%"></i></div>` : ''}<button class="btn" data-a="vipDaily" ${s.vipClaimed ? 'disabled' : ''}>${s.vipClaimed ? 'Dzisiejsza nagroda odebrana' : `Odbierz dzienną nagrodę (+${C.vip.daily})`}</button><p class="muted">Poziom nie wygasa; opuszczenie dnia nie odbiera postępu. VIP ma charakter prestiżowy i kosmetyczny – nie daje premii do produkcji, badań ani siły.</p></div>`;
    h += `<div class="row">${C.vip.shop.map((o, i) => `<button class="btn sm" data-a="vipBuy" data-i="${i}">+${U.fmt(o.pts)} pkt za ${o.price} 💎</button>`).join('')}</div>`;
    h += `<table class="tbl"><tr><th>VIP</th><th class="num">Koszt</th><th class="num">Łącznie</th><th>Nagroda</th></tr>${C.vip.levels.map((c, i) => `<tr class="${i < L ? 'done' : ''}"><td>${i + 1}</td><td class="num">${U.full(c)}</td><td class="num">${U.full(P.vip.total(i + 1))}</td><td>${C.vip.rewards[i]}${i < L ? ' ✔' : ''}</td></tr>`).join('')}</table>`;
    return h;
  };
  A.vipDaily = () => P.vip.claimDaily(P.S);
  A.vipBuy = (d) => P.vip.buy(P.S, +d.i);

  // ================= SKLEP =================
  PG.shop = (s) => {
    const ei = P.shop.energyInfo(s);
    let h = `<h1>💎 Sklep</h1><div class="box warn">Tryb testowy: zakupy nie pobierają pieniędzy. Cennik w złotych pozostaje do ustalenia.</div>`;
    h += `<h3>Rubiny</h3><div class="cards">${C.shop.rubyPacks.map((p, i) => `<div class="card"><b>${p.label}</b><span class="big">💎 ${U.full(p.r)}</span><button class="btn sm" data-a="buyRubies" data-i="${i}">Kup (test)</button></div>`).join('')}</div>`;
    h += `<div class="box"><h3>${C.shop.pass.label}</h3><p>${C.shop.pass.dailyRubies} 💎 dziennie przez ${C.shop.pass.days} dni + sztandar. Nie omija żadnych limitów.</p>${s.pass > s.time ? `<p class="good">Aktywna jeszcze ${UI.timer(s.pass)}</p>` : ''}<button class="btn sm" data-a="buyPass">Aktywuj (test)</button></div>`;
    h += `<div class="box"><h3>⚡ Energia</h3><p>10 punktów za ${C.energy.buyPrice} 💎 · dziś ${C.energy.buyDaily - ei.leftD}/${C.energy.buyDaily} · tydzień ${C.energy.buyWeekly - ei.leftW}/${C.energy.buyWeekly}</p><button class="btn sm" data-a="buyEnergy" ${ei.room < 10 ? 'disabled' : ''}>Kup 10 ⚡</button><p class="muted">Zakup tylko gdy całe 10 pkt mieści się w pasku. Nie ma odkładanych mikstur energii.</p></div>`;
    h += `<h3>Wyglądy</h3>${C.shop.cosmetics.map((c) => `<div class="box row"><span>${c.name}</span><button class="btn sm" data-a="buyCos" data-i="${c.id}" ${s.cosmetics[c.id] ? 'disabled' : ''}>${s.cosmetics[c.id] ? 'Posiadane' : c.price + ' 💎'}</button></div>`).join('')}`;
    h += `<p class="muted">Cel balansu: gracz korzystający z pełnej oferty rozwija się ok. 10–15% szybciej od równie aktywnego gracza bez wpłat. Darmowy gracz może zdobywać rubiny w grze i kupować te same limitowane korzyści.</p>`;
    return h;
  };
  A.buyRubies = (d) => P.shop.buyRubies(P.S, +d.i);
  A.buyPass = () => P.shop.buyPass(P.S);
  A.buyCos = (d) => P.shop.buyCosmetic(P.S, d.i);

  // ================= CHWAŁA =================
  PG.glory = (s) => {
    const av = P.glory.available(s);
    let h = `<h1>🏅 Chwała wojenna</h1><div class="box"><p>Bieżąca chwała: <b>${U.full(s.glory.cur)}</b> · łącznie zdobyta: ${U.full(s.glory.total)} · najwyższy tytuł: ${s.glory.best || '—'} · zabici przeciwnicy: ${U.full(s.stats.kills)}</p><p>Dzienny spadek: 0,05% stanu (dziś ok. −${U.fmt(s.glory.cur * C.glory.decay)}).</p><p class="muted">Chwałę daje rzeczywista walka między graczami – w ataku i w obronie. Zwycięska obrona dostaje 70% puli, przegrany atak 30%; pula dzielona wg wkładu. Powtarzane walki z tym samym przeciwnikiem dają malejące nagrody; walki ze znacznie słabszym – ograniczone. Tytuły są wyłącznie prestiżowe.</p></div>`;
    h += `<table class="tbl"><tr><th class="num">Min. chwała</th><th>Tytuł</th><th></th></tr>${C.glory.titles.map(([th, n]) => `<tr class="${s.glory.title === n ? 'me' : ''}"><td class="num">${U.full(th)}</td><td>${n}</td><td>${av.includes(n) ? `<button class="btn xs" data-a="gTitle" data-t="${n}" ${s.glory.title === n ? 'disabled' : ''}>Ustaw</button>` : `<small class="muted">brakuje ${U.fmt(th - s.glory.cur)}</small>`}</td></tr>`).join('')}</table><button class="btn sm ghost" data-a="gTitle" data-t="">Bez tytułu</button>`;
    h += `<h3>Spadek bez nowych punktów</h3><table class="tbl">${[7, 30, 90, 180, 365].map((d) => `<tr><td>${d} dni</td><td class="num">${U.pct(1 - Math.pow(1 - C.glory.decay, d), 2)}</td></tr>`).join('')}</table>`;
    return h;
  };
  A.gTitle = (d) => P.glory.set(P.S, d.t);

  // ================= RAPORTY =================
  PG.reports = (s) => {
    let h = `<h1>📜 Raporty</h1><button class="btn xs ghost" data-a="readAll">Oznacz wszystkie jako przeczytane</button>`;
    for (const r of s.reports) h += `<div class="rep ${r.read ? '' : 'unread'} ${r.kind}" data-a="rep" data-r="${r.id}"><span>${r.kind === 'battle' ? (r.win ? '🟢' : '🔴') : r.kind === 'warn' ? '⚠️' : r.kind === 'scout' ? '🧭' : 'ℹ️'} ${U.esc(r.title)}</span><small>${U.clock(r.t)}</small></div>`;
    return h + (s.reports.length ? '' : '<p class="muted">Brak raportów.</p>');
  };
  A.readAll = () => { for (const r of P.S.reports) r.read = true; P.S.unread = 0; };
  A.rep = (d) => {
    const s = P.S; const r = s.reports.find((x) => x.id === d.r); if (!r) return;
    if (!r.read) { r.read = true; s.unread = Math.max(0, s.unread - 1); }
    UI.modal(() => {
      let h = `<h2>${U.esc(r.title)}</h2><p class="muted">${U.clock(r.t)}</p>`;
      if (r.body) h += `<p>${U.esc(r.body)}</p>`;
      if (r.kind === 'battle') {
        h += `<div class="box ${r.win ? 'good' : 'bad'}"><b>${r.win ? 'Zwycięstwo' : 'Porażka'}</b> · siła ${U.fmt(r.power.a)} vs ${U.fmt(r.power.d)}${r.hero ? ` · dowódca ${C.heroes[r.hero].name}` : ''}${r.tactic ? ` · taktyka ${C.tactics[r.tactic].name}` : ''}</div>`;
        h += `<h3>Ważne przyczyny wyniku</h3><ul>${r.reasons.map((x) => `<li>${x}</li>`).join('')}</ul>`;
        h += `<div class="grid2"><div><h3>Twoje straty</h3>${UI.armyTable(r.myLoss, { empty: 'brak strat' })}${r.wounded && U.armyCount(r.wounded) ? `<p>Ranni do lazaretu: <b>${U.full(U.armyCount(r.wounded))}</b> · polegli: <b>${U.full(U.armyCount(r.dead))}</b></p>` : ''}</div><div><h3>Straty przeciwnika</h3>${UI.armyTable(r.enemyLoss, { empty: 'brak' })}<p class="muted">Pozostało: ${U.full(U.armyCount(r.enemyLeft || {}))}</p></div></div>`;
        h += `<h3>Przebieg</h3><table class="tbl"><tr><th>Runda</th><th class="num">${r.defense ? 'Napastnicy' : 'Twoi'} −</th><th class="num">${r.defense ? 'Obrońcy' : 'Przeciwnik'} −</th>${r.rounds.some((x) => x.wall != null) ? '<th class="num">Umocnienia</th>' : ''}</tr>${r.rounds.map((x) => `<tr><td>${x.round}</td><td class="num">${U.full(x.aLost)}</td><td class="num">${U.full(x.dLost)}</td>${x.wall != null ? `<td class="num">${x.wall}%</td>` : ''}</tr>`).join('')}</table>`;
        if (r.glory != null) h += `<p>🏅 Chwała: <b>+${U.full(r.glory)}</b> (pula bitwy ${U.full(r.pool)})</p>`;
        if (r.lost) h += `<p class="bad">Zrabowano: ${P.rewardStr(r.lost)}</p>`;
        if (r.reinf) h += `<p>Posiłki sojuszu w obronie: ${U.full(r.reinf)}</p>`;
        if (r.energy) h += `<p class="muted">Zużyta energia: ${r.energy}⚡</p>`;
      }
      if (r.loot && Object.keys(r.loot).length) h += `<p class="good">Łup: ${P.rewardStr(r.loot)}</p>`;
      if (r.xp) h += `<p>Doświadczenie towarzyszy: +${r.xp}</p>`;
      if (r.note) h += `<p class="muted">${r.note}</p>`;
      return h + `<button class="btn" data-a="close">Zamknij</button>`;
    }, { wide: true });
  };

  // ================= CZAT =================
  PG.chat = (s) => {
    const ch = UI.cur('chat', 'ogolny');
    const tabs = [['ogolny', 'Ogólny'], ['sojusz', 'Sojusz'], ['prywatne', 'Prywatne']].concat(s.chat.groups.map((g) => [g.id, '👥 ' + g.name]));
    const list = (s.chat.msgs[ch] || []).filter((m) => !s.chat.blocked[m.from.split(' [')[0]]);
    return `<h1>💬 Czat</h1>${UI.tabs('chat', tabs)}<div id="chatBox" class="chatBox">${list.map((m) => `<div class="msg ${m.sys ? 'sys' : ''} ${m.from === s.ruler.name ? 'mine' : ''}"><b data-a="chatUser" data-n="${U.esc(m.from.split(' [')[0])}">${U.esc(m.from)}</b> <small>${new Date(m.t).toISOString().slice(11, 16)}</small><br>${U.esc(m.text)}</div>`).join('') || '<p class="muted">Brak wiadomości.</p>'}</div><div class="row"><input id="chatIn" placeholder="Napisz wiadomość…" maxlength="300"><button class="btn" data-a="chatSend">Wyślij</button></div><p><button class="btn xs ghost" data-a="newGroup">Nowa grupa</button> <small class="muted">Grupy z zapraszanymi osobami, także z innych sojuszy. Kliknij nadawcę, aby zablokować lub zgłosić.</small></p>`;
  };
  A.chatSend = () => { const el = document.getElementById('chatIn'); if (!el) return; P.chat.send(P.S, UI.cur('chat', 'ogolny'), el.value); el.value = ''; el.blur(); };
  A.chatUser = (d) => { if (d.n === P.S.ruler.name || d.n === 'System') return; UI.modal(() => `<h2>${U.esc(d.n)}</h2><button class="btn" data-a="chatBlock" data-n="${U.esc(d.n)}">Zablokuj</button> <button class="btn ghost" data-a="chatReport" data-n="${U.esc(d.n)}">Zgłoś</button> <button class="btn ghost" data-a="close">Zamknij</button>`); };
  A.chatBlock = (d) => { P.chat.block(P.S, d.n); UI.close(); };
  A.chatReport = (d) => { P.chat.report(P.S, d.n); UI.close(); };
  A.newGroup = () => { const s = P.S; const n = prompt('Nazwa grupy:', 'Wyprawa'); if (!n) return; const members = (s.alliance ? s.alliance.members.slice(0, 3).map((m) => m.name) : []).concat([U.pick(P.BOT_NAMES) + ' [' + s.map.tags[1] + ']']); UI.tab.chat = P.chat.newGroup(s, n, members); };

  // ================= KRONIKA =================
  PG.chronicle = (s) => {
    let h = `<h1>📖 Kronika osady</h1><h3>Początek przygody</h3>`;
    P.quests.TUT.forEach((q, i) => { h += `<p>${i < s.quest.step ? '✔' : i === s.quest.step ? '▶' : '○'} ${q.t}</p>`; });
    h += `<h3>Cele</h3>`; s.quest.chron = s.quest.chron || {};
    P.quests.CHRON.forEach((c, i) => { const ok = c.ok(s); const got = s.quest.chron[i]; h += `<div class="row box"><span>${got ? '✔' : ok ? '★' : '○'} ${c.t}<br><small class="muted">${P.rewardStr(c.reward)}</small></span>${ok && !got ? `<button class="btn sm gold" data-a="chron" data-i="${i}">Odbierz</button>` : ''}</div>`; });
    h += `<h3>Statystyki</h3><table class="tbl">${[['Zwycięstwa', s.stats.wins], ['Porażki', s.stats.losses], ['Pokonani przeciwnicy na mapie', s.stats.monsters], ['Wykonane zlecenia', s.stats.tasks], ['Udane obrony', s.stats.defenses], ['Odbudowane przeprawy', s.stats.bridges], ['Odkryte pola', s.stats.discovered]].map(([n, v]) => `<tr><td>${n}</td><td class="num">${U.full(v)}</td></tr>`).join('')}</table>`;
    return h;
  };
  A.chron = (d) => P.quests.claimChron(P.S, +d.i);

  PG.log = (s) => `<h1>🗒️ Dziennik</h1>${s.log.map((l) => `<p><small class="muted">${U.clock(l.t)}</small> ${U.esc(l.m)}</p>`).join('') || '<p class="muted">Pusto.</p>'}`;

  // ================= USTAWIENIA =================
  PG.settings = (s) => `<h1>⚙️ Ustawienia</h1>
    <div class="box"><h3>Tempo gry (do testów)</h3><div class="row">${C.speeds.map((v) => `<button class="btn sm ${s.speed === v ? 'on' : 'ghost'}" data-a="setSpeed" data-v="${v}">×${v}</button>`).join('')}</div><p class="muted">×1 to docelowe tempo. Wyższe tempo przyspiesza cały czas gry: produkcję, budowy, energię, tablicę, wydarzenia i sezony.</p>
    <div class="row"><button class="btn sm" data-a="skip" data-h="1">Przewiń +1 h</button><button class="btn sm" data-a="skip" data-h="8">+8 h</button><button class="btn sm" data-a="skip" data-h="24">+1 dzień</button><button class="btn sm" data-a="skip" data-h="168">+7 dni</button></div></div>
    <div class="box"><h3>Zapis</h3><p class="muted">Gra zapisuje się automatycznie w przeglądarce co kilka sekund. Po powrocie nadrabia czas nieobecności (do ${C.offlineCapDays} dni czasu gry).</p><button class="btn sm" data-a="saveNow">Zapisz teraz</button> <button class="btn sm" data-a="export">Eksportuj</button> <button class="btn sm" data-a="import">Importuj</button> <button class="btn sm danger" data-a="reset">Nowa gra</button><textarea id="saveTxt" class="saveTxt" rows="3" placeholder="Tu pojawi się / wklej zapis"></textarea></div>
    <div class="box"><h3>O grze</h3><p><b>Pogranicza: Droga do Korony</b> – prototyp na podstawie koncepcji v1.3 (4 listopada 2026). Rozgrywka jednoosobowa: inni gracze, sojusze, arena i rywalizacja są symulowane. Wszystkie robocze wartości balansu są w pliku <code>js/config.js</code>.</p></div>`;
  A.setSpeed = (d) => { P.S.speed = +d.v; };
  A.skip = (d) => { P.advance(P.S, +d.h * C.HOUR); UI.toast(`Przewinięto ${d.h} h czasu gry`); UI.citySig = ''; };
  A.saveNow = () => { P.save(P.S); UI.toast('Zapisano'); };
  A.export = () => { document.getElementById('saveTxt').value = btoa(unescape(encodeURIComponent(JSON.stringify(P.S)))); };
  A.import = () => { try { const s = JSON.parse(decodeURIComponent(escape(atob(document.getElementById('saveTxt').value.trim())))); if (s.v !== C.version) throw 0; P.S = s; P.save(s); UI.toast('Wczytano zapis', 'good'); UI.go('city'); } catch (e) { UI.toast('Nieprawidłowy zapis', 'bad'); } };
  A.reset = () => { if (!confirm('Rozpocząć nową grę? Obecny postęp zostanie usunięty.')) return; localStorage.removeItem(C.saveKey); location.reload(); };
})();
