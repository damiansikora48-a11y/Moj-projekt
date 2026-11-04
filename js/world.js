/* Duża mapa, odkrywanie, marsze, przeciwnicy, napady, forty i centralny zamek */
(function () {
  const C = P.cfg, U = P.u;
  const BOT_NAMES = ['Bolesław', 'Mieszko', 'Dobrosław', 'Ziemowit', 'Radosław', 'Przemysł', 'Witosław', 'Gniewko', 'Czcibor', 'Lubomir', 'Wszebor', 'Bogumił', 'Sulisław', 'Domarat', 'Jaromir', 'Bronisz', 'Mściwój', 'Świętopełk', 'Krzesimir', 'Siemowit', 'Zbysław', 'Wojsław', 'Milena', 'Dobrawa', 'Wanda', 'Jarosława', 'Bogna', 'Radomira', 'Świętosława', 'Wiesława', 'Ludmiła', 'Zdzisława', 'Grzymisław', 'Racibor', 'Unisław', 'Bogdan', 'Cieszymir', 'Dalibor', 'Mirogniew', 'Sobiesław', 'Wit', 'Żelisław', 'Kazimir', 'Lechosław', 'Pakosław', 'Budzisław', 'Chwalibóg', 'Drogomir', 'Gościsław', 'Jaksa'];
  const REGION_NAMES = [['Mroczne Ostępy', 'Szczyty Wiatru', 'Zimne Wrzosowiska'], ['Dolina Rzek', 'Serce Królestwa', 'Stepy Wschodu'], ['Pogranicze', 'Bagna Mgieł', 'Żelazne Wzgórza']];
  P.BOT_NAMES = BOT_NAMES;

  P.world = {
    regionOf(x, y) { const rs = C.map.regionSize; return { rx: Math.floor(x / rs), ry: Math.floor(y / rs) }; },
    regionName(x, y) { const r = P.world.regionOf(x, y); return REGION_NAMES[r.ry][r.rx]; },
    // poziom zagrożenia rośnie z odległością od Pogranicza i ku zamkowi
    dangerAt(x, y) { const cx = C.map.w / 2, cy = C.map.h / 2; const dStart = Math.hypot(x - C.map.startX, y - C.map.startY); const dC = Math.hypot(x - cx, y - cy); return U.clamp(Math.round(1 + dStart / 2.6 + Math.max(0, 10 - dC) * 0.6), 1, C.monsterBase.maxLevel); },
    generate(s) {
      const { w, h } = C.map; const R = U.seeded(s.seed);
      const terr = [];
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        const n = Math.sin(x * 0.31 + s.seed % 7) + Math.cos(y * 0.27 + (s.seed % 11)) + Math.sin((x + y) * 0.13) + R() * 0.8;
        let t = n > 1.5 ? 'forest' : n < -1.6 ? 'hills' : 'plains';
        const r = P.world.regionOf(x, y);
        if (r.rx === 1 && r.ry === 2 && R() < 0.45) t = 'swamp';
        if (r.rx === 2 && r.ry === 1 && R() < 0.5) t = 'plains';
        if (r.rx === 2 && r.ry === 2 && R() < 0.4) t = 'hills';
        if (r.rx === 0 && r.ry === 0 && R() < 0.5) t = 'forest';
        terr.push(t);
      }
      // rzeki
      for (let y = 0; y < h; y++) { const x = Math.round(16 + Math.sin(y * 0.25) * 2); terr[y * w + x] = 'river'; }
      for (let x = 16; x < w; x++) { const y = Math.round(31 + Math.sin(x * 0.3) * 1.5); terr[y * w + x] = 'river'; }
      const objs = [];
      const occ = new Set();
      const put = (o) => { const k = o.x + ',' + o.y; if (occ.has(k) || terr[o.y * w + o.x] === 'river') return false; occ.add(k); o.id = o.id || U.uid(); objs.push(o); return true; };
      put({ type: 'home', x: C.map.startX, y: C.map.startY, name: 'Twoja osada' });
      // mosty (uszkodzone przeprawy) na rzekach
      for (const y of [8, 22, 40]) { const x = Math.round(16 + Math.sin(y * 0.25) * 2); objs.push({ id: U.uid(), type: 'bridge', x, y, broken: true, name: 'Uszkodzona przeprawa' }); occ.add(x + ',' + y); terr[y * w + x] = 'bridge'; }
      for (const x of [24, 38]) { const y = Math.round(31 + Math.sin(x * 0.3) * 1.5); objs.push({ id: U.uid(), type: 'bridge', x, y, broken: true, name: 'Uszkodzona przeprawa' }); occ.add(x + ',' + y); terr[y * w + x] = 'bridge'; }
      // zamek centralny
      put({ type: 'castle', x: 24, y: 24, name: 'Zamek Koronny', owner: 'neutral' });
      // forty
      put({ type: 'fort', fort: 'zelazna', x: 36, y: 38, name: C.forts.zelazna.name, owner: 'neutral' });
      put({ type: 'fort', fort: 'stepowa', x: 40, y: 18, name: C.forts.stepowa.name, owner: 'neutral' });
      put({ type: 'fort', fort: 'cytadela', x: 10, y: 14, name: C.forts.cytadela.name, owner: 'neutral' });
      // cele strategiczne
      put({ type: 'strategic', sub: 'przelecz', x: 28, y: 33, name: 'Przełęcz Wilcza' });
      put({ type: 'strategic', sub: 'archiwum', x: 20, y: 20, name: 'Archiwum Kronikarzy' });
      put({ type: 'strategic', sub: 'przeprawa', x: 30, y: 24, name: 'Przeprawa Koronna' });
      // osady botów (3 sojusze + niezależni)
      const allies = ['Strażnicy Pogranicza', 'Bractwo Wilczego Szlaku', 'Zakon Świtu'];
      const tags = ['SP', 'BWS', 'ZŚ'];
      let bi = 0;
      for (let i = 0; i < 46; i++) {
        const x = Math.floor(R() * w), y = Math.floor(R() * h);
        if (Math.hypot(x - C.map.startX, y - C.map.startY) < 4) continue;
        const ali = i < 16 ? 0 : i < 30 ? 1 : i < 40 ? 2 : -1;
        const lvl = U.clamp(Math.round(2 + R() * 10 + P.world.dangerAt(x, y) * 0.4), 1, 30);
        if (put({ type: 'bot', x, y, name: BOT_NAMES[bi++ % BOT_NAMES.length], lvl, ali, tag: ali >= 0 ? tags[ali] : null, power: Math.round(lvl * lvl * 220 * (0.6 + R())) })) { /* ok */ }
      }
      // ruiny, znaleziska, niezależne osady
      const finds = [['ruin_find', 'Opuszczone ruiny'], ['mine_find', 'Opuszczona kopalnia'], ['village', 'Niezależna osada'], ['archive', 'Stare archiwum']];
      for (let i = 0; i < 26; i++) { const f = finds[i % 4]; put({ type: 'find', sub: f[0], x: Math.floor(R() * w), y: Math.floor(R() * h), name: f[1], done: false }); }
      // złoża
      for (let i = 0; i < 40; i++) {
        const res = U.pick(['food', 'wood', 'stone', 'iron']);
        const x = Math.floor(R() * w), y = Math.floor(R() * h);
        put({ type: 'node', res, x, y, lvl: P.world.dangerAt(x, y), amount: 0, name: { food: 'Pola', wood: 'Las do wyrębu', stone: 'Złoże kamienia', iron: 'Żyła żelaza' }[res] });
      }
      // siedziba sojuszu "Strażnicy Pogranicza" w pobliżu
      put({ type: 'allyhq', x: C.map.startX + 4, y: C.map.startY - 3, name: 'Siedziba: Strażnicy Pogranicza', ali: 0, tag: 'SP' });
      s.map = { terr, objs, rev: new Array(w * h).fill(0), allies, tags };
      for (const o of objs) if (o.type === 'node') o.amount = Math.round(20000 * Math.pow(1.25, o.lvl));
      P.world.reveal(s, C.map.startX, C.map.startY, C.map.revealStart);
      // potwory
      for (let i = 0; i < 55; i++) P.world.spawnMonster(s);
      // blokada drogi (samouczek)
      P.world.addObj(s, { type: 'monster', kind: 'bandyci', x: C.map.startX + 3, y: C.map.startY - 1, lvl: 1, mult: 0.45, name: 'Obóz bandytów (więzień!)', story: 'wit' });
    },
    addObj(s, o) { o.id = o.id || U.uid(); s.map.objs.push(o); return o; },
    obj(s, id) { return s.map.objs.find((o) => o.id === id); },
    at(s, x, y) { return s.map.objs.filter((o) => o.x === x && o.y === y); },
    terrain(s, x, y) { return s.map.terr[y * C.map.w + x]; },
    isRev(s, x, y) { return x >= 0 && y >= 0 && x < C.map.w && y < C.map.h && s.map.rev[y * C.map.w + x]; },
    reveal(s, cx, cy, r) {
      let n = 0;
      for (let y = cy - r; y <= cy + r; y++) for (let x = cx - r; x <= cx + r; x++) {
        if (x < 0 || y < 0 || x >= C.map.w || y >= C.map.h) continue;
        if (Math.hypot(x - cx, y - cy) > r + 0.3) continue;
        const i = y * C.map.w + x; if (!s.map.rev[i]) { s.map.rev[i] = 1; n++; }
      }
      s.stats.discovered += n;
      return n;
    },
    home(s) { return s.map.objs.find((o) => o.type === 'home'); },
    dist(s, o) { const h = P.world.home(s); return Math.hypot(o.x - h.x, o.y - h.y); },
    // przeprawy: bez naprawionego mostu przejście przez rzekę jest dłuższe (objazd)
    pathFactor(s, o) {
      const h = P.world.home(s);
      const crossV = (h.x < 16) !== (o.x < 16); const crossH = (h.y > 31) !== (o.y > 31);
      let f = 1;
      if (crossV) f += s.map.objs.some((b) => b.type === 'bridge' && !b.broken && b.x < 20) ? 0 : 0.6;
      if (crossH) f += s.map.objs.some((b) => b.type === 'bridge' && !b.broken && b.x >= 20) ? 0 : 0.6;
      return f;
    },
    travelTime(s, o, army, hero) { return P.world.dist(s, o) * P.world.pathFactor(s, o) * C.march.secPerTile * 1000 / P.army.armySpeed(s, army, hero); },
    spawnMonster(s, near) {
      const { w, h } = C.map;
      for (let k = 0; k < 30; k++) {
        let x, y;
        if (near) { x = U.clamp(near.x + U.ri(-6, 6), 0, w - 1); y = U.clamp(near.y + U.ri(-6, 6), 0, h - 1); }
        else { x = U.ri(0, w - 1); y = U.ri(0, h - 1); }
        if (s.map.objs.some((o) => o.x === x && o.y === y)) continue;
        const t = P.world.terrain(s, x, y); if (t === 'river' || t === 'bridge') continue;
        const lvl = P.world.dangerAt(x, y);
        let kind = t === 'forest' ? U.pick(['zwierzeta', 'zwierzeta', 'bandyci']) : t === 'hills' ? U.pick(['garnizon', 'ruiny', 'bandyci']) : t === 'swamp' ? U.pick(['klatwa', 'zwierzeta']) : U.pick(['bandyci', 'bandyci', 'zwierzeta', 'garnizon']);
        if (kind === 'klatwa' && lvl < 4) kind = 'bandyci';
        const M = C.monsters[kind];
        return P.world.addObj(s, { type: 'monster', kind, x, y, lvl, name: M.name });
      }
    },
    spawnBeast(s, lvl) {
      const o = P.world.spawnMonster(s, P.world.home(s)); if (!o) return null;
      Object.assign(o, { kind: 'bestia', name: 'Wiwerna z Gór', lvl: lvl || Math.max(5, Math.round(s.b.siedziba * 0.8)), beast: true, hpLeft: 1 });
      P.world.reveal(s, o.x, o.y, 1);
      return o;
    },
    monsterArmy(o) {
      const lvl = o.lvl;
      if (o.beast) return { wiwerna: { 1: Math.max(1, Math.round(Math.pow(1.35, lvl - 5) * 3)) } };
      const M = C.monsters[o.kind] || C.monsters.bandyci;
      const total = C.monsterBase.count * Math.pow(C.monsterBase.growth, lvl - 1) * (M.strong ? 1.8 : 1) * (o.mult || 1);
      const tier = U.clamp(1 + Math.floor((lvl - 1) / C.monsterBase.tierEvery), 1, 6);
      const a = {};
      for (const t in M.units) { const n = Math.round(total * M.units[t] / (t === 'niedzwiedz' ? 3 : 1)); if (n > 0) a[t] = { [tier]: n }; }
      return a;
    },
    monsterMods(o) { const l = o.lvl; return { atk: 0.03 * l, def: 0.03 * l, hp: 0.02 * l }; },

    // ---------- marsze ----------
    // kinds: monster, board, gather, scout, bridge, find, bot(PvP), fort, rally, strategic, reinforce
    send(s, spec) {
      const { target, army, hero, helper, tactic, kind } = spec;
      const n = U.armyCount(army);
      if (kind !== 'scout' && n <= 0) return P.ui.toast('Wybierz wojsko', 'bad');
      if (s.marches.length >= P.army.maxMarches(s)) return P.ui.toast('Brak wolnych marszów (zbadaj Sztukę marszu)', 'bad');
      if (n > P.army.marchCap(s)) return P.ui.toast('Przekroczono pojemność marszu', 'bad');
      for (const t in army) for (const r in army[t]) if (((s.units[t] || {})[r] || 0) < army[t][r]) return P.ui.toast('Za mało wojska w osadzie', 'bad');
      if (hero && P.heroes.busy(s, hero)) return P.ui.toast('Towarzysz jest już w drodze', 'bad');
      if (helper && (helper === hero || P.heroes.busy(s, helper))) return P.ui.toast('Pomocnik jest niedostępny', 'bad');
      // energia: rezerwacja przy wysłaniu, zwrot przy zawróceniu przed walką [DOK 15]
      const energy = spec.energy || 0;
      if (energy > s.energy.v) return P.ui.toast('Za mało punktów wypraw', 'bad');
      s.energy.v -= energy;
      U.armyAdd(s.units, army, -1);
      const travel = kind === 'scout' ? P.world.dist(s, target) * 8 * 1000 : P.world.travelTime(s, target, army, hero);
      const m = { id: U.uid(), kind, targetId: target.id, tx: target.x, ty: target.y, tname: target.name, army: U.armyClone(army), hero: hero || null, helper: helper || null, tactic: tactic || 'rownowaga', energy, start: s.time, travel, next: s.time + travel, state: 'out', loot: {}, task: spec.task || null, extra: spec.extra || null };
      s.marches.push(m);
      if (target.type === 'monster' || target.type === 'task') target.busy = m.id;
      P.ui.toast(`Wysłano marsz: ${target.name} (${U.dur(travel)})`);
      return m;
    },
    recall(s, m) {
      if (m.state === 'out') {
        s.energy.v = Math.min(C.energy.max + 999, s.energy.v + m.energy); // zwrot rezerwacji
        const el = s.time - m.start; m.state = 'return'; m.next = s.time + el; m.energy = 0;
        const o = P.world.obj(s, m.targetId); if (o && o.busy === m.id) o.busy = null;
        P.ui.toast('Wojsko zawraca – energia zwrócona');
      } else if (m.state === 'gather' || m.state === 'garrison') {
        P.world.finishGather(s, m, true);
      }
    },
    marchStep(s, m) {
      if (m.state === 'out') return P.world.arrive(s, m);
      if (m.state === 'gather') return P.world.finishGather(s, m);
      if (m.state === 'garrison') { m.state = 'return'; m.next = s.time + m.travel; return; }
      if (m.state === 'return') return P.world.returnHome(s, m);
      m.next = s.time + C.MIN; // bezpieczeństwo
    },
    returnHome(s, m) {
      U.armyAdd(s.units, m.army);
      const got = P.gain(s, m.loot);
      s.marches = s.marches.filter((x) => x !== m);
      if (Object.keys(got).length) P.ui.toast(`Wojsko wróciło: ${P.rewardStr(got)}`, 'good');
      P.quests.check(s);
    },
    finishGather(s, m, early) {
      const o = P.world.obj(s, m.targetId);
      const el = s.time - m.gStart;
      const rate = m.gRate; const amt = Math.min(m.gMax, Math.floor(rate * el / C.HOUR));
      if (o) { o.amount = Math.max(0, o.amount - amt); o.busy = null; if (o.amount <= 0) s.map.objs = s.map.objs.filter((x) => x !== o); }
      m.loot[m.gRes] = (m.loot[m.gRes] || 0) + amt;
      m.state = 'return'; m.next = s.time + m.travel;
      if (early) P.ui.toast('Przerwano zbieranie');
    },
    arrive(s, m) {
      const o = P.world.obj(s, m.targetId);
      m.state = 'return'; m.next = s.time + m.travel;
      if (!o) { P.report(s, { kind: 'info', title: 'Cel zniknął', body: `Po dotarciu na miejsce (${m.tname}) nie zastano celu. Wojsko wraca.` }); return; }
      const h = P.world[('on_' + m.kind)];
      if (h) h(s, m, o);
    },
    battle(s, m, o, enemyArmy, enemyMods, opts = {}) {
      const mods = P.sideMods(s, { hero: m.hero, helper: m.helper });
      const res = P.fight({ army: m.army, mods, tactic: m.tactic }, { army: enemyArmy, mods: enemyMods || {}, fort: opts.fort, tactic: opts.enemyTactic }, { terrain: opts.terrain || P.world.terrain(s, o.x, o.y), attLabel: 'Twoich', defLabel: 'przeciwnika' });
      // straty gracza: ranni / polegli
      const split = P.splitWounded(s, res.attLoss, opts.woundedRatio != null ? opts.woundedRatio : C.battle.woundedPvE);
      U.armyAdd(m.army, res.attLoss, -1);
      U.armyAdd(s.wounded, split.wounded);
      // doświadczenie towarzyszy
      const xp = Math.round((opts.xp || 50) * (res.win === 'att' ? 1 : 0.3));
      if (m.hero) P.heroes.addXp(s, m.hero, xp);
      if (m.helper) P.heroes.addXp(s, m.helper, xp * 0.5);
      if (res.win === 'att') { s.stats.wins++; if (m.hero === 'borys') s.stats.cmdWins = (s.stats.cmdWins || 0) + 1; } else s.stats.losses++;
      s.stats.kills += U.armyCount(res.defLoss);
      return { res, split, xp };
    },
    battleReport(s, m, title, r, extra = {}) {
      P.report(s, {
        kind: 'battle', title, win: r.res.win === 'att', reasons: r.res.reasons, rounds: r.res.log,
        myArmy: U.armyAdd(U.armyClone(m.army), r.res.attLoss), myLoss: r.res.attLoss, wounded: r.split.wounded, dead: r.split.dead,
        enemyLoss: r.res.defLoss, enemyLeft: r.res.defLeft, power: r.res.power0, hero: m.hero, helper: m.helper, tactic: m.tactic, ...extra,
      });
    },
    monsterLoot(s, o, strong) {
      const R = C.monsterReward; const M = C.monsters[o.kind] || C.monsters.bandyci;
      const scale = Math.pow(R.levelScale, o.lvl - R.refLevel) * (strong ? 2 : 1);
      const loot = {}; const resKey = U.pick(M.res);
      loot[resKey] = Math.round(R.base * scale);
      if (M.silver) loot.silver = Math.round(300 * scale);
      if (U.chance(R.bonusChance)) loot[U.pick(C.basic)] = (loot[U.pick(C.basic)] || 0) + Math.round(R.bonusPacks * R.bonusPack * scale);
      const sp = U.chance(R.spChance) ? (strong ? 4 : R.spCount) * R.spMin : 0;
      if (sp) loot[M.sp] = sp;
      const table = strong ? R.strongRubies : R.rubies; let roll = Math.random(), acc = 0;
      for (const [v, p] of table) { acc += p; if (roll < acc) { if (v) loot.rubies = v; break; } }
      for (const it in M.items) if (U.chance(0.5 + 0.03 * o.lvl)) loot[it] = M.items[it] * (strong ? 2 : 1) * (1 + Math.floor(o.lvl / 8));
      if (M.stones && U.chance(0.4)) loot[U.pick(['k_hart', 'k_skupienie', 'k_duch'])] = 1;
      return { loot, xp: Math.round(R.xp * scale) };
    },
    on_monster(s, m, o) {
      o.busy = null;
      const enemy = P.world.monsterArmy(o);
      const strong = C.monsters[o.kind] && C.monsters[o.kind].strong;
      const { loot, xp } = P.world.monsterLoot(s, o, strong);
      const r = P.world.battle(s, m, o, enemy, P.world.monsterMods(o), { xp });
      if (r.res.win === 'att') {
        const load = P.army.armyLoad(s, m.army);
        const fromRes = {}; let left = load;
        for (const k in loot) { if (C.resources[k]) { const take = Math.min(loot[k], Math.max(0, left)); fromRes[k] = take; left -= take; } else fromRes[k] = loot[k]; }
        // nagroda gwarantowana nie zależy od udźwigu dla zadań; dla potworów udźwig ogranicza surowce
        m.loot = fromRes;
        s.map.objs = s.map.objs.filter((x) => x !== o);
        s.stats.monsters++; if (o.kind === 'zwierzeta') s.stats.beasts = (s.stats.beasts || 0) + 1;
        if (o.story === 'wit') { P.heroes.add(s, 'wit'); s.quest.flags.wit = true; }
        if (o.story === 'block') { s.quest.flags.road = true; P.world.reveal(s, C.map.startX, C.map.startY, 9); }
        if (o.story && o.storyChain) P.board.chainProgress(s, o.storyChain);
        P.events.addPts(s, 'hunt', 1);
        P.world.spawnMonster(s);
      }
      P.world.battleReport(s, m, `${r.res.win === 'att' ? 'Zwycięstwo' : 'Porażka'}: ${o.name} (poz. ${o.lvl})`, r, { loot: r.res.win === 'att' ? m.loot : null, xp, energy: m.energy });
      P.quests.check(s);
    },
    on_task(s, m, o) {
      o.busy = null;
      const task = s.board.taken.find((t) => t.id === o.taskId);
      const enemy = P.world.monsterArmy(o);
      const r = P.world.battle(s, m, o, enemy, P.world.monsterMods(o), { xp: 120 });
      let ok = r.res.win === 'att', note = '';
      if (ok && task && task.type === 'eskorta') { const lostFrac = U.armyCount(r.res.attLoss) / Math.max(1, U.armyCount(r.res.attLoss) + U.armyCount(m.army)); if (lostFrac > 0.5) { ok = false; note = 'Eskorta poniosła zbyt duże straty – karawana nie przetrwała.'; } }
      if (ok && task && task.type === 'odzyskanie') { if (P.army.armyLoad(s, m.army) < task.cargo) { ok = false; note = `Za mały udźwig: potrzeba ${U.fmt(task.cargo)}, było ${U.fmt(P.army.armyLoad(s, m.army))}.`; } }
      if (task) {
        s.board.taken = s.board.taken.filter((t) => t !== task);
        if (ok) { m.loot = { ...task.reward }; s.stats.tasks++; if (task.chain) P.board.chainProgress(s, task.chain); P.events.addPts(s, 'task', 1); }
      }
      s.map.objs = s.map.objs.filter((x) => x !== o);
      P.world.battleReport(s, m, `${ok ? 'Zlecenie wykonane' : 'Zlecenie nieudane'}: ${o.name}`, r, { loot: ok ? m.loot : null, note, energy: m.energy });
      P.quests.check(s);
    },
    on_gather(s, m, o) {
      const load = P.army.armyLoad(s, m.army);
      m.state = 'gather'; m.gStart = s.time; m.gRes = o.res; m.gMax = Math.min(load, o.amount);
      m.gRate = Math.max(500, load * C.march.gatherPerHour * (1 + P.bonus(s, 'gather')));
      m.next = s.time + m.gMax / m.gRate * C.HOUR;
      o.busy = m.id;
    },
    on_scout(s, m, o) {
      const r = 2 + P.bonus(s, 'scout') + (m.hero ? (P.heroes.effects(s, m.hero).scout || 0) : 0);
      const n = P.world.reveal(s, o.x, o.y, Math.round(r));
      let body = `Zwiadowcy odkryli ${n} nowych pól wokół (${o.x}, ${o.y}).`;
      const found = s.map.objs.filter((x) => Math.hypot(x.x - o.x, x.y - o.y) <= r && x.type !== 'node');
      if (found.length) body += ' Zauważono: ' + [...new Set(found.map((x) => x.name))].slice(0, 6).join(', ') + '.';
      P.report(s, { kind: 'scout', title: `Zwiad: ${P.world.regionName(o.x, o.y)}`, body });
      if (o.type === 'fog') s.map.objs = s.map.objs.filter((x) => x !== o);
      P.quests.check(s);
    },
    on_bridge(s, m, o) {
      if (!o.broken) return;
      o.broken = false; o.name = 'Odbudowana przeprawa'; s.stats.bridges++;
      P.report(s, { kind: 'info', title: 'Przeprawa odbudowana', body: 'Most otwiera krótszą trasę przez rzekę. Marsze na drugi brzeg są szybsze.' });
      if (!s.heroes.miroslaw) P.heroes.add(s, 'miroslaw');
      P.events.addPts(s, 'explore', 2);
    },
    on_find(s, m, o) {
      if (o.done) return; o.done = true;
      let loot = {}, body = '';
      if (o.sub === 'ruin_find') { loot = { relikty: 2, [U.pick(['k_hart', 'k_skupienie', 'k_duch'])]: 1, stone: 3000 }; body = 'W ruinach znaleziono relikty i kamień awansu.'; }
      if (o.sub === 'mine_find') { loot = { iron: 5000, sztaby: 3 }; body = 'Opuszczona kopalnia skrywała zapasy rudy.'; }
      if (o.sub === 'archive') { loot = { plany: 2, sp_research: 30 }; body = 'Stare archiwum: plany wojskowe i notatki badaczy.'; }
      if (o.sub === 'village') { loot = { food: 6000, silver: 1500 }; body = 'Pomogliście niezależnej osadzie. Wdzięczni mieszkańcy dzielą się zapasami.'; s.stats.tasks++; if (!s.heroes.dobrawa && s.stats.tasks >= 3) { P.heroes.add(s, 'dobrawa'); body += ' Zielarka Dobrawa postanawia dołączyć.'; } }
      m.loot = loot; o.name += ' (zbadane)';
      P.report(s, { kind: 'info', title: o.name, body, loot });
      P.events.addPts(s, 'explore', 1);
    },
    on_bot(s, m, o) { P.pvp.attack(s, m, o); },
    on_fort(s, m, o) { P.forts.attack(s, m, o); },
    on_castle(s, m, o) { P.crown.attack(s, m, o); },
    on_strategic(s, m, o) { P.crown.attack(s, m, o); },
    on_rally(s, m, o) { P.alliance.rallyArrive(s, m, o); },
    on_reinforce(s, m, o) { m.state = 'garrison'; m.next = s.time + 8 * C.HOUR; P.alliance.reinforced(s, m, o); },
    hourly(s) {
      // uzupełnianie przeciwników
      const mons = s.map.objs.filter((o) => o.type === 'monster' && !o.story).length;
      if (mons < 55) for (let i = 0; i < 3; i++) P.world.spawnMonster(s);
      // okazjonalnie wielka bestia
      if (!s.map.objs.some((o) => o.beast) && s.b.siedziba >= 5 && U.chance(0.04)) P.world.spawnBeast(s);
      // wzrost osad botów
      for (const o of s.map.objs) if (o.type === 'bot' && U.chance(0.01)) { o.lvl = Math.min(30, o.lvl + 1); o.power = Math.round(o.power * 1.12); }
      P.forts.hourly(s);
      P.crown.hourly(s);
    },
  };

  // ---------- PvP z osadami innych graczy (symulowanych) ----------
  P.pvp = {
    botArmy(o) {
      const total = Math.round(30 * Math.pow(1.22, o.lvl));
      const tier = U.clamp(1 + Math.floor((o.lvl - 1) / 5), 1, 6);
      return { miecznik: { [tier]: Math.round(total * 0.35) }, pikinier: { [tier]: Math.round(total * 0.25) }, lucznik: { [tier]: Math.round(total * 0.25) }, kawaleria: { [tier]: Math.round(total * 0.15) } };
    },
    botFort(o) { return { wallHp: 400 * Math.pow(1.25, o.lvl), wallBonus: 0.15 + 0.012 * o.lvl, towers: 15 * Math.pow(1.2, o.lvl), towerMode: 'piechota' }; },
    attack(s, m, o) {
      if (s.shield > s.time) { s.shield = s.time; P.ui.toast('Atak przerwał Twoją ochronę początkową'); }
      const enemy = P.pvp.botArmy(o);
      const r = P.world.battle(s, m, o, enemy, { def: 0.02 * o.lvl, atk: 0.02 * o.lvl }, { fort: P.pvp.botFort(o), woundedRatio: C.battle.woundedAttack, xp: 80 + o.lvl * 10, terrain: P.world.terrain(s, o.x, o.y) });
      const win = r.res.win === 'att';
      // chwała: pula = wartość pokonanych (polegli + ranni) obu stron [DOK 31]
      const pool = P.lossValue(r.res.attLoss) + P.lossValue(r.res.defLoss);
      const myPower = P.armyPower(U.armyAdd(U.armyClone(m.army), r.res.attLoss)), enPower = P.armyPower(enemy);
      const share = win ? C.glory.winAtt : C.glory.loseAtt;
      const gl = P.glory.award(s, pool * share, { target: o.id, ratio: enPower / Math.max(1, myPower) });
      let loot = null;
      if (win) {
        const load = P.army.armyLoad(s, m.army); const base = 2000 * Math.pow(1.3, o.lvl);
        loot = {}; let left = load;
        for (const k of C.basic) { const v = Math.min(left / 4, base * U.rnd(0.6, 1)); loot[k] = Math.round(v); }
        loot.silver = Math.round(base * 0.2);
        m.loot = loot;
        o.power = Math.round(o.power * 0.9);
      }
      P.world.battleReport(s, m, `${win ? 'Najazd udany' : 'Najazd odparty'}: ${o.name}${o.tag ? ' [' + o.tag + ']' : ''}`, r, { loot, glory: gl, pool: Math.round(pool) });
    },
  };

  // ---------- napady na osadę gracza [DOK 11] ----------
  P.raids = {
    fortSpec(s) {
      const dmg = 1 - (s.damagedWalls || 0);
      const wallBonus = (0.05 + 0.012 * s.b.mury) * dmg * (1 + (s.heroes.miroslaw ? (P.heroes.effects(s, 'miroslaw').walls || 0) : 0));
      return { wallHp: (300 + 250 * Math.pow(1.22, s.b.brama)) * dmg, wallBonus: s.b.mury > 0 ? wallBonus : 0, towers: s.b.wieze > 0 ? 12 * Math.pow(1.2, s.b.wieze) : 0, towerMode: s.defense.towers };
    },
    announce(s) {
      if (s.shield > s.time) { s.raid.next = s.shield + U.rnd(2, 8) * C.HOUR; return; }
      const myPow = Math.max(60, P.armyPower(s.units));
      const scale = U.rnd(0.45, 1.05);
      const lvl = U.clamp(Math.round(s.b.siedziba * 0.9 + 1), 1, 30);
      const tier = U.clamp(1 + Math.floor((lvl - 1) / 5), 1, 6);
      const mix = U.pick([[0.4, 0.2, 0.25, 0.15], [0.2, 0.2, 0.2, 0.4], [0.3, 0.1, 0.5, 0.1], [0.25, 0.35, 0.15, 0.25]]);
      const base = P.unitStats('miecznik', tier); const perUnit = (base.atk + base.def + base.hp / 2) / 10;
      let total = Math.max(15, Math.round(myPow * scale / perUnit));
      const army = { miecznik: { [tier]: Math.round(total * mix[0]) }, pikinier: { [tier]: Math.round(total * mix[1]) }, lucznik: { [tier]: Math.round(total * mix[2]) }, kawaleria: { [tier]: Math.round(total * mix[3]) } };
      if (s.b.brama >= 6) army.taran = { [tier]: Math.max(1, Math.round(total * 0.04)) };
      const attacker = U.pick(s.map.objs.filter((o) => o.type === 'bot' && (!s.alliance || o.ali !== s.alliance.botAli))) || { name: 'Najeźdźcy', lvl };
      s.raid.incoming = { arrive: s.time + C.raids.warnMin * C.MIN, army, from: attacker.name, fromId: attacker.id, tag: attacker.tag };
      P.ui.toast(`⚠️ Zwiadowcy donoszą: nadciąga napad (${attacker.name}) za ${C.raids.warnMin} min!`, 'bad');
      P.report(s, { kind: 'warn', title: 'Nadciąga napad!', body: `${attacker.name}${attacker.tag ? ' [' + attacker.tag + ']' : ''} prowadzi ok. ${U.fmt(U.armyCount(army))} żołnierzy. Dotrą o ${U.clock(s.raid.incoming.arrive)}. Przygotuj garnizon i dowódcę obrony.` });
      if (s.alliance) P.alliance.autoReinforce(s);
    },
    resolve(s, scripted) {
      const inc = s.raid.incoming; s.raid.incoming = null;
      s.raid.next = s.time + U.rnd(C.raids.minGapH, C.raids.maxGapH) * C.HOUR;
      // garnizon = wojsko w osadzie + posiłki sojuszu
      const reinf = s.alliance ? (s.alliance.reinf || {}) : {};
      const defArmy = U.armyAdd(U.armyClone(s.units), reinf);
      const mods = P.sideMods(s, { hero: s.defense.hero && !P.heroes.busy(s, s.defense.hero) ? s.defense.hero : null, home: true });
      const atkMods = { atk: 0.02 * s.b.siedziba, def: 0.02 * s.b.siedziba };
      const res = P.fight({ army: inc.army, mods: atkMods, tactic: U.pick(['rownowaga', 'szarza', 'ostrzal', 'oskrzydlenie']) }, { army: defArmy, mods, fort: P.raids.fortSpec(s), tactic: 'tarcze' }, { terrain: 'hills', attLabel: 'napastników', defLabel: 'Twoich' });
      // straty obrony rozłożone proporcjonalnie na własne i posiłki
      const myLoss = {}, reinfLoss = {};
      for (const t in res.defLoss) for (const r in res.defLoss[t]) {
        const own = (s.units[t] || {})[r] || 0, rf = (reinf[t] || {})[r] || 0, tot = own + rf || 1;
        const l = res.defLoss[t][r]; const lo = Math.round(l * own / tot);
        if (lo) { myLoss[t] = myLoss[t] || {}; myLoss[t][r] = lo; }
        if (l - lo) { reinfLoss[t] = reinfLoss[t] || {}; reinfLoss[t][r] = l - lo; }
      }
      const split = P.splitWounded(s, myLoss, C.battle.woundedDefense);
      U.armyAdd(s.units, myLoss, -1); U.armyAdd(s.wounded, split.wounded);
      if (s.alliance) { U.armyAdd(s.alliance.reinf, reinfLoss, -1); }
      const win = res.win === 'def';
      let lost = null;
      if (!win) {
        lost = {}; const prot = P.eco.cap(s) * P.eco.protectedPct(s);
        for (const k of C.basic) { const ex = Math.max(0, s.res[k] - prot); const l = Math.floor(ex * C.raids.lootPct); s.res[k] -= l; lost[k] = l; }
        s.damagedWalls = Math.min(0.6, (s.damagedWalls || 0) + C.raids.wallDamage);
      } else { s.stats.defenses++; P.events.addPts(s, 'defense', 2); }
      // chwała: zwycięska obrona dostaje 70% puli, dzielone wg wkładu (właściciel vs posiłki)
      const pool = P.lossValue(res.attLoss) + P.lossValue(res.defLoss);
      const ownShare = U.armyCount(s.units) + U.armyCount(myLoss);
      const allShare = ownShare + U.armyCount(reinf) || 1;
      const myFrac = ownShare / allShare;
      const gl = P.glory.award(s, pool * (win ? C.glory.winDef : C.glory.loseDef) * myFrac, { target: inc.fromId || 'raid', ratio: 1 });
      if (s.defense.hero && s.heroes[s.defense.hero]) P.heroes.addXp(s, s.defense.hero, win ? 150 : 40);
      P.report(s, {
        kind: 'battle', defense: true, title: `${win ? 'Obrona udana' : 'Obrona przełamana'}: napad ${inc.from}${inc.tag ? ' [' + inc.tag + ']' : ''}`, win,
        reasons: res.reasons, rounds: res.log, myArmy: defArmy, myLoss, wounded: split.wounded, dead: split.dead, enemyLoss: res.attLoss, enemyLeft: res.attLeft, power: { a: res.power0.d, d: res.power0.a },
        lost, glory: gl, pool: Math.round(pool), hero: s.defense.hero, reinf: U.armyCount(reinf), note: win ? '' : 'Mury zostały uszkodzone – napraw je w panelu Murów. Poziomy budynków i towarzysze pozostają nienaruszeni.',
      });
      P.ui.toast(win ? 'Napad odparty!' : 'Napastnicy przełamali obronę…', win ? 'good' : 'bad');
      if (scripted || inc.scripted) s.quest.flags.raid = true;
      P.events.onRaid(s, win);
      P.quests.check(s);
    },
    repairCost(s) { const c = P.bld.cost('mury', Math.max(1, s.b.mury)); for (const k in c) c[k] = Math.round(c[k] * (s.damagedWalls || 0) * 1.5); return c; },
    repair(s) { if (!P.pay(s, P.raids.repairCost(s))) return P.ui.toast('Brak surowców na naprawę', 'bad'); s.damagedWalls = 0; P.ui.toast('Umocnienia naprawione', 'good'); },
    scriptRaid(s) {
      s.raid.incoming = { arrive: s.time + 90 * 1000, army: { bandyta: { 1: 12 }, strzelec: { 1: 5 } }, from: 'Zbóje z traktu', scripted: true };
      P.ui.toast('⚠️ Niewielki napad zbójów nadciąga do osady!', 'bad');
    },
  };

  // ---------- forty [DOK 16] ----------
  P.forts = {
    list(s) { return s.map.objs.filter((o) => o.type === 'fort'); },
    owned(s, fid) { const f = P.forts.list(s).find((o) => o.fort === fid); return f && s.alliance && f.owner === s.alliance.botAli; },
    windowOpen(s, t = s.time) { const day = U.dayIdx(t); const h = U.hourUTC(t); return day % C.fortRules.windowEveryDays === 0 && h >= C.fortRules.windowHourUTC && h < C.fortRules.windowHourUTC + C.fortRules.windowLenH; },
    nextWindow(s) { let d = U.dayIdx(s.time); for (let i = 0; i < 10; i++) { const dd = d + i; if (dd % C.fortRules.windowEveryDays === 0) { const t = dd * C.DAY + C.fortRules.windowHourUTC * C.HOUR; if (t + C.fortRules.windowLenH * C.HOUR > s.time) return t; } } return 0; },
    garrison(s, f) { const lvl = 12 + (f.owner === 'neutral' ? 0 : 6); const tier = 3; const n = Math.round(400 * Math.pow(1.15, lvl - 10) * (f.owner === 'neutral' ? 1 : 1.6)); const [a, b] = C.forts[f.fort].units; return { [a]: { [tier]: Math.round(n * 0.5) }, [b]: { [tier]: Math.round(n * 0.3) }, miecznik: { [tier]: Math.round(n * 0.2) } }; },
    canRecruit(s, type, n) {
      const d = C.units[type];
      if (!P.forts.owned(s, d.fort)) return { ok: false, why: `Sojusz musi kontrolować fort ${C.forts[d.fort].name}` };
      const total = U.armyCount(P.army.totalArmy(s)); let spec = 0; const all = P.army.totalArmy(s);
      for (const t in all) if (C.units[t].fort) spec += U.armyCount({ [t]: all[t] });
      if ((spec + n) > Math.max(50, total * C.fortRules.shareLimit)) return { ok: false, why: `Limit udziału wojsk specjalnych: ${U.pct(C.fortRules.shareLimit)} armii` };
      const used = s.fortRecruit && s.fortRecruit.day === U.dayIdx(s.time) ? s.fortRecruit.n : 0;
      if (used + n > C.fortRules.dailyRecruit) return { ok: false, why: `Dzienny limit rekrutacji fortowej: ${C.fortRules.dailyRecruit} (pozostało ${C.fortRules.dailyRecruit - used})` };
      return { ok: true };
    },
    noteRecruit(s, n) { const d = U.dayIdx(s.time); if (!s.fortRecruit || s.fortRecruit.day !== d) s.fortRecruit = { day: d, n: 0 }; s.fortRecruit.n += n; },
    attack(s, m, o) {
      if (!P.forts.windowOpen(s)) { P.report(s, { kind: 'info', title: `${o.name}: poza oknem walk`, body: `Walki o forty odbywają się w zapowiedzianych oknach. Najbliższe: ${U.clock(P.forts.nextWindow(s))}. Wojsko wraca.` }); return; }
      const mine = s.alliance && o.owner === s.alliance.botAli;
      if (mine) { m.state = 'garrison'; m.next = s.time + C.fortRules.windowLenH * C.HOUR; o.defenders = (o.defenders || 0) + P.armyPower(m.army); P.report(s, { kind: 'info', title: `Obrona fortu: ${o.name}`, body: 'Twoje wojsko wzmocniło garnizon sojuszu do końca okna walk.' }); return; }
      const g = P.forts.garrison(s, o);
      const r = P.world.battle(s, m, o, g, { def: 0.15, atk: 0.1 }, { fort: { wallHp: 30000, wallBonus: 0.35, towers: 900, towerMode: 'piechota' }, terrain: C.forts[o.fort].terrain, woundedRatio: 0.75, xp: 300 });
      o.siegeDmg = (o.siegeDmg || 0) + P.lossValue(r.res.defLoss);
      const pool = P.lossValue(r.res.attLoss) + P.lossValue(r.res.defLoss);
      const gl = P.glory.award(s, pool * (r.res.win === 'att' ? C.glory.winAtt : C.glory.loseAtt), { target: o.id, ratio: 1 });
      if (s.alliance) s.alliance.fortContrib = (s.alliance.fortContrib || 0) + P.lossValue(r.res.defLoss);
      P.world.battleReport(s, m, `Szturm fortu: ${o.name} – ${r.res.win === 'att' ? 'wyłom w obronie' : 'odparci'}`, r, { glory: gl, note: 'O przejęciu fortu decyduje łączny wynik sojuszy na koniec okna walk.' });
    },
    hourly(s) {
      // rozstrzygnięcie na koniec okna
      const t = s.lastHour * C.HOUR;
      const day = U.dayIdx(t), h = U.hourUTC(t);
      if (day % C.fortRules.windowEveryDays === 0 && h === C.fortRules.windowHourUTC + C.fortRules.windowLenH) {
        for (const f of P.forts.list(s)) {
          const scores = s.map.allies.map((_, a) => a > 2 ? 0 : U.rnd(0.5, 1.5) * (a === 0 ? 1.1 : a === 1 ? 1.0 : 0.85) * 1000);
          if (s.alliance) scores[s.alliance.botAli] += (s.alliance.fortContrib || 0) * 0.02 + (f.defenders || 0) * 0.05 + (s.alliance.own ? 300 : 0);
          if (f.owner !== 'neutral') scores[f.owner] *= 1.25; // przewaga obrońcy
          const win = scores.indexOf(Math.max(...scores));
          const prev = f.owner; f.owner = win; f.defenders = 0;
          const ali = s.map.allies[win];
          if (prev !== win) P.log(s, `🏰 ${f.name} przechodzi w ręce sojuszu ${ali}`);
          if (s.alliance && (prev === s.alliance.botAli || win === s.alliance.botAli)) P.report(s, { kind: 'info', title: `${f.name}: ${win === s.alliance.botAli ? 'fort zdobyty!' : prev === win ? 'utrzymany' : 'fort utracony'}`, body: win === s.alliance.botAli ? `Sojusz kontroluje fort. Możesz rekrutować: ${C.forts[f.fort].units.map((u) => C.units[u].name).join(' i ')}.` : 'Sojusz stracił fort. Wyszkolone jednostki zostają, ale nowa rekrutacja jest wstrzymana.' });
        }
        if (s.alliance) s.alliance.fortContrib = 0;
      }
    },
  };

  // ---------- Wojna o Koronę i centralny zamek [DOK 17, 24] ----------
  P.crown = {
    period(s, t = s.time) { const d = U.dayIdx(t); const start = Math.floor(d / C.crown.everyDays) * C.crown.everyDays + (C.crown.everyDays - C.crown.durationDays); return { start: start * C.DAY, end: (start + C.crown.durationDays) * C.DAY }; },
    active(s) { const p = P.crown.period(s); return s.time >= p.start && s.time < p.end; },
    attack(s, m, o) {
      if (!P.crown.active(s)) { P.report(s, { kind: 'info', title: `${o.name}: spokój`, body: `Wojna o Koronę zaczyna się ${U.clock(P.crown.period(s).start)}. Wojsko wraca.` }); return; }
      const lvl = o.type === 'castle' ? 22 : 15;
      const n = Math.round(600 * Math.pow(1.12, lvl - 10));
      const g = { miecznik: { 4: Math.round(n * 0.4) }, kusznik: { 4: Math.round(n * 0.3) }, kawaleria: { 4: Math.round(n * 0.3) } };
      const r = P.world.battle(s, m, o, g, { def: 0.2, atk: 0.15 }, { fort: o.type === 'castle' ? { wallHp: 60000, wallBonus: 0.4, towers: 1500, towerMode: 'piechota' } : null, terrain: 'hills', woundedRatio: 0.75, xp: 400 });
      const pts = Math.round(P.lossValue(r.res.defLoss) * (o.type === 'castle' ? 2 : 1));
      s.crownPts = (s.crownPts || 0) + pts;
      const gl = P.glory.award(s, (P.lossValue(r.res.attLoss) + P.lossValue(r.res.defLoss)) * (r.res.win === 'att' ? C.glory.winAtt : C.glory.loseAtt), { target: o.id, ratio: 1 });
      P.events.addPts(s, 'crown', Math.ceil(pts / 50));
      P.world.battleReport(s, m, `Wojna o Koronę: ${o.name}`, r, { glory: gl, note: `Punkty wojny dla sojuszu: +${U.fmt(pts)}` });
    },
    hourly(s) {
      const t = s.lastHour * C.HOUR; const p = P.crown.period(s, t - 1);
      if (t === p.end) {
        const scores = s.map.allies.map((_, a) => a > 2 ? 0 : U.rnd(a === 2 ? 2000 : 3000, a === 2 ? 8000 : 9000));
        let mine = -1;
        if (s.alliance) { mine = s.alliance.botAli; scores[mine] += (s.crownPts || 0) + (s.alliance.own ? 0 : 1500); }
        const win = scores.indexOf(Math.max(...scores));
        const castle = s.map.objs.find((o) => o.type === 'castle'); castle.owner = win;
        const king = win === mine && (s.alliance.own || (s.crownPts || 0) > 2000);
        if (king) { s.king = s.time + C.crown.kingDays * C.DAY; s.alliance.kingBonusUntil = s.king; }
        if (win === mine) s.alliance.kingBonusUntil = s.time + C.crown.kingDays * C.DAY;
        if (s.alliance) P.report(s, { kind: 'info', title: 'Koniec Wojny o Koronę', body: `Zamek Koronny zdobywa sojusz ${s.map.allies[win]}.` + (king ? ' Zostajesz Królem Pogranicza na 7 dni! (tytuł, prestiż i +5% zbierania dla sojuszu)' : win === mine ? ' Twój sojusz wygrywa – członkowie otrzymują +5% zbierania na 7 dni.' : '') });
        s.crownPts = 0;
      }
    },
  };
})();
