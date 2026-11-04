/* Automatyczne bitwy [DOK 10]. Serwer w docelowej grze; tu deterministyczny silnik lokalny. */
(function () {
  const C = P.cfg, U = P.u;

  function unitStats(t, r) {
    const d = C.units[t]; const m = C.tierStat[r - 1] || 1;
    return { atk: d.atk * m, def: d.def * m, hp: d.hp * m };
  }
  P.unitStats = unitStats;

  // premie gracza (lub NPC) w postaci słownika
  P.sideMods = function (s, opts = {}) {
    const keys = ['atk', 'def', 'hp', 'atk_front', 'atk_back', 'atk_cav', 'def_front', 'siege', 'beast', 'wounded'];
    const m = {};
    for (const k of keys) m[k] = s ? P.bonus(s, k) : 0;
    const addHero = (id, w) => {
      if (!id || !s || !s.heroes[id]) return;
      const eff = P.heroes.effects(s, id);
      for (const k in eff) m[k] = (m[k] || 0) + eff[k] * w;
    };
    addHero(opts.hero, 1); addHero(opts.helper, 0.5);
    if (opts.home && s) m.def += P.bonus(s, 'def_home');
    if (s && P.eco.starving(s)) { m.atk -= 0.2; m.starving = true; }
    return m;
  };

  P.armyPower = function (army, mods = {}) {
    let p = 0;
    for (const t in army) for (const r in army[t]) {
      const st = unitStats(t, +r); const n = army[t][r];
      p += n * (st.atk * (1 + (mods.atk || 0)) + st.def * (1 + (mods.def || 0)) + st.hp * (1 + (mods.hp || 0)) / 2);
    }
    return Math.round(p / 10);
  };

  function mkSide(spec) {
    const groups = [];
    for (const t in spec.army) for (const r in spec.army[t]) {
      const n = spec.army[t][r]; if (n <= 0) continue;
      const st = unitStats(t, +r); const d = C.units[t];
      groups.push({ t, r: +r, n, n0: n, line: d.line, ...st, d, dealt: 0, taken: 0 });
    }
    return { ...spec, groups, mods: spec.mods || {}, tactic: C.tactics[spec.tactic || 'rownowaga'] || C.tactics.rownowaga };
  }
  const alive = (side, lines) => side.groups.filter((g) => g.n > 0.5 && (!lines || lines.includes(g.line)));

  function lineMod(side, g, stat) {
    const m = side.mods; let v = 1 + (m[stat] || 0);
    if (stat === 'atk') {
      if (g.line === 'front' || g.line === 'siege') v += m.atk_front || 0;
      if (g.line === 'back') v += m.atk_back || 0;
      if (g.line === 'cav') v += m.atk_cav || 0;
    }
    if (stat === 'def' && g.line === 'front') v += m.def_front || 0;
    const tac = side.tactic;
    if (tac.all && tac.all[stat]) v *= tac.all[stat];
    if (tac[g.line] && tac[g.line][stat]) v *= tac[g.line][stat];
    const ter = side.terrainMod || {};
    if (ter[g.line] && ter[g.line][stat]) v *= ter[g.line][stat];
    if (side.isDefender && ter.defender && ter.defender[stat]) v *= ter.defender[stat];
    return v;
  }

  P.fight = function (attSpec, defSpec, opts = {}) {
    const A = mkSide(attSpec), D = mkSide(defSpec);
    D.isDefender = true;
    const terrain = C.terrains[opts.terrain || 'plains'];
    A.terrainMod = terrain.mod; D.terrainMod = terrain.mod;
    const fort = defSpec.fort ? { ...defSpec.fort, hp0: defSpec.fort.wallHp } : null;
    const log = []; const kills = {}; // kills[attackerType][targetType]
    const meleeStart = 2 + ((A.tactic.delayMelee || D.tactic.delayMelee) ? 1 : 0);
    const power0 = { a: P.armyPower(attSpec.army, A.mods), d: P.armyPower(defSpec.army, D.mods) };
    let towerKills = 0, wallBrokenRound = 0;

    for (let round = 1; round <= C.battle.rounds; round++) {
      if (!alive(A).length || !alive(D).length) break;
      const pending = [];
      const act = (S, T) => {
        const tFront = alive(T, ['front']), tBack = alive(T, ['back', 'siege']), tCav = alive(T, ['cav']);
        const pikeN = tFront.filter((g) => g.t === 'pikinier' || g.t === 'tarcznik').reduce((a, g) => a + g.n, 0);
        const frontN = tFront.reduce((a, g) => a + g.n, 0) || 1;
        for (const g of alive(S)) {
          if ((g.line === 'front' || g.line === 'siege') && round < meleeStart) continue;
          let dmg = g.n * g.atk * lineMod(S, g, 'atk') * U.rnd(1 - C.battle.random, 1 + C.battle.random);
          if (g.line === 'cav' && round === 1) dmg *= S.tactic.cavFirst || 1.15;
          // tarany i saperzy: uderzają w umocnienia
          if (g.d.siege && fort && fort.wallHp > 0 && S === A) {
            const sd = g.n * g.atk * g.d.siege * (1 + (S.mods.siege || 0)) * 2;
            fort.wallHp = Math.max(0, fort.wallHp - sd);
            if (fort.wallHp <= 0 && !wallBrokenRound) wallBrokenRound = round;
            if (g.line === 'siege') continue;
            dmg *= 0.6;
          }
          // wybór celu
          const targets = [];
          if (g.line === 'cav') {
            let f = 0.45 + (S.tactic.flank || 0) - 0.7 * (pikeN / frontN) * (tFront.length ? 1 : 0);
            f = U.clamp(f, 0.08, 0.9);
            if (!tBack.length) f = 0;
            if (!tFront.length && !tCav.length) f = 1;
            if (f > 0 && tBack.length) targets.push([tBack, f]);
            const rest = tFront.length ? tFront : tCav.length ? tCav : tBack;
            if (1 - f > 0 && rest.length) targets.push([rest, 1 - f]);
          } else {
            const tl = tFront.length ? tFront : tCav.length ? tCav : tBack;
            if (tl.length) targets.push([tl, 1]);
            // strzelcy częściowo wybierają kawalerię, gdy linia stoi
            if (g.line === 'back' && tFront.length && tCav.length) { targets[0][1] = 0.7; targets.push([tCav, 0.3]); }
          }
          for (const [list, frac] of targets) {
            const w = list.reduce((a, x) => a + x.n * x.hp, 0) || 1;
            for (const tg of list) {
              const share = dmg * frac * (tg.n * tg.hp) / w;
              let mult = ((C.counters[g.t] || {})[tg.t]) || 1;
              if (tg.d.isBeast && g.d.beast) mult *= g.d.beast;
              if (tg.d.isBeast) mult *= 1 + (S.mods.beast || 0);
              let def = tg.def * lineMod(T, tg, 'def') * (1 - (g.d.pierce || 0));
              if (fort && T === D && fort.wallHp > 0 && g.line !== 'back') def *= 1 + fort.wallBonus;
              if (fort && T === D && fort.wallHp > 0 && g.line === 'back') def *= 1 + fort.wallBonus * 0.5;
              const hp = tg.hp * lineMod(T, tg, 'hp') * (1 + def / 25);
              const k = share * mult / hp;
              pending.push([tg, k]);
              g.dealt += k * tg.hp; tg.taken += k * tg.hp;
              kills[g.t] = kills[g.t] || {}; kills[g.t][tg.t] = (kills[g.t][tg.t] || 0) + k;
            }
          }
        }
      };
      act(A, D); act(D, A);
      // wieże obrońcy
      if (fort && fort.towers > 0) {
        const mode = fort.towerMode || 'piechota';
        const list = mode === 'machiny' ? alive(A, ['siege']).concat(alive(A, ['front'])) : alive(A, ['front', 'siege']);
        const tw = fort.towers * (mode === 'machiny' && alive(A, ['siege']).length ? 1.6 : 1);
        const w = list.reduce((a, x) => a + x.n * x.hp, 0) || 1;
        for (const tg of list) { const k = tw * (tg.n * tg.hp / w) / (tg.hp * (1 + tg.def / 25)); pending.push([tg, k]); towerKills += k; }
      }
      const before = { a: alive(A).reduce((x, g) => x + g.n, 0), d: alive(D).reduce((x, g) => x + g.n, 0) };
      for (const [tg, k] of pending) tg.n = Math.max(0, tg.n - k);
      const after = { a: alive(A).reduce((x, g) => x + g.n, 0), d: alive(D).reduce((x, g) => x + g.n, 0) };
      log.push({ round, aLost: Math.round(before.a - after.a), dLost: Math.round(before.d - after.d), wall: fort ? Math.round(100 * fort.wallHp / (fort.hp0 || 1)) : null });
    }

    const remain = (S) => S.groups.reduce((a, g) => a + g.n * (g.atk + g.def + g.hp / 2), 0);
    const start = (S) => S.groups.reduce((a, g) => a + g.n0 * (g.atk + g.def + g.hp / 2), 0) || 1;
    const aFrac = remain(A) / start(A), dFrac = remain(D) / start(D);
    let win;
    if (!alive(D).length && alive(A).length) win = 'att';
    else if (!alive(A).length) win = 'def';
    else if (opts.symmetric) win = aFrac > dFrac ? 'att' : 'def';
    else win = (remain(A) > remain(D) * 2.2 && dFrac < 0.35) ? 'att' : 'def';

    const losses = (S) => { const o = {}; for (const g of S.groups) { const l = Math.min(g.n0, Math.round(g.n0 - g.n)); if (l > 0) { o[g.t] = o[g.t] || {}; o[g.t][g.r] = (o[g.t][g.r] || 0) + l; } } return o; };
    const survivors = (S) => { const o = {}; for (const g of S.groups) { const v = g.n0 - Math.min(g.n0, Math.round(g.n0 - g.n)); if (v > 0) { o[g.t] = o[g.t] || {}; o[g.t][g.r] = (o[g.t][g.r] || 0) + v; } } return o; };

    // przyczyny wyniku
    const reasons = [];
    const lostOfLine = (S, lines) => S.groups.filter((g) => lines.includes(g.line)).reduce((a, g) => a + (g.n0 - g.n), 0);
    const killsBy = (types, targetLines, T) => { let k = 0; for (const t of types) for (const tg of T.groups) if (targetLines.includes(tg.line)) k += (kills[t] || {})[tg.t] || 0; return k; };
    const label = (S) => S === A ? (opts.attLabel || 'atakujących') : (opts.defLabel || 'obrońców');
    for (const [S, T] of [[A, D], [D, A]]) {
      const cavLost = lostOfLine(T, ['cav']);
      const pk = killsBy(['pikinier', 'tarcznik'], ['cav'], T);
      if (cavLost >= 5 && pk >= cavLost * 0.35) reasons.push(`Pikinierzy ${label(S)} zatrzymali szarżę kawalerii.`);
      const backLost = lostOfLine(T, ['back', 'siege']);
      const ck = killsBy(['kawaleria', 'lekki_jezdziec', 'wilk'], ['back', 'siege'], T);
      if (backLost >= 5 && ck >= backLost * 0.4) reasons.push(`Kawaleria ${label(S)} oskrzydliła szyk i rozbiła strzelców.`);
      const totalK = S.groups.reduce((a, g) => a + g.dealt, 0) || 1;
      const backK = S.groups.filter((g) => g.line === 'back').reduce((a, g) => a + g.dealt, 0);
      if (backK / totalK > 0.45 && totalK > 50) reasons.push(`Strzelcy ${label(S)} przerzedzili szeregi przeciwnika przed zwarciem.`);
      const front = S.groups.filter((g) => g.line === 'front'); const back = S.groups.filter((g) => g.line === 'back');
      if (front.length && back.length) {
        const bSurv = back.reduce((a, g) => a + g.n, 0) / (back.reduce((a, g) => a + g.n0, 0) || 1);
        const fTaken = front.reduce((a, g) => a + g.taken, 0) / (S.groups.reduce((a, g) => a + g.taken, 0) || 1);
        if (fTaken > 0.6 && bSurv > 0.7) reasons.push(`Piechota ${label(S)} utrzymała linię i osłoniła strzelców.`);
      }
      const backN = back.reduce((a, g) => a + g.n0, 0), frontN0 = front.reduce((a, g) => a + g.n0, 0);
      if (backN > 0 && frontN0 < backN * 0.25 && lostOfLine(S, ['back']) > backN * 0.4) reasons.push(`Strzelcy ${label(S)} zostali bez osłony piechoty.`);
    }
    if (fort) {
      if (wallBrokenRound) reasons.push(`Tarany skruszyły umocnienia w ${wallBrokenRound}. rundzie.`);
      else if (fort.wallBonus > 0) reasons.push('Mury i brama utrzymały się do końca bitwy, wzmacniając obronę.');
      if (towerKills > 5) reasons.push(`Wieże ostrzelały nacierających (ok. ${U.fmt(towerKills)} trafionych).`);
    }
    const ratio = power0.a / Math.max(1, power0.d);
    if (ratio > 1.8) reasons.push('Wyraźna przewaga siły atakujących przeważyła.');
    if (ratio < 0.55) reasons.push('Obrońcy mieli wyraźną przewagę siły.');
    if (opts.terrain && opts.terrain !== 'plains') reasons.push(`Teren: ${terrain.name} wpłynął na przebieg walki.`);
    if (A.mods.starving || D.mods.starving) reasons.push('Głód w osadzie osłabił wojsko (−20% ataku).');
    if (A.tactic !== C.tactics.rownowaga) reasons.push(`Taktyka atakujących: ${A.tactic.name}.`);
    if (!reasons.length) reasons.push(win === 'att' ? 'Lepiej dobrany skład przeważył.' : 'Obrona okazała się zbyt silna.');

    return {
      win, log, reasons: [...new Set(reasons)].slice(0, 6), power0,
      attLoss: losses(A), defLoss: losses(D), attLeft: survivors(A), defLeft: survivors(D),
      attContrib: A.groups.reduce((a, g) => a + g.dealt + g.taken, 0), defContrib: D.groups.reduce((a, g) => a + g.dealt + g.taken, 0),
      wallLeft: fort ? fort.wallHp / (fort.hp0 || 1) : null,
    };
  };

  // wartość pokonanych jednostek (do chwały)
  P.lossValue = function (loss) {
    let v = 0;
    for (const t in loss) for (const r in loss[t]) v += loss[t][r] * C.glory.perUnit * (C.tierGlory[r - 1] || 1);
    return v;
  };

  // podział strat na rannych i poległych
  P.splitWounded = function (s, loss, ratio) {
    const wounded = {}, dead = {};
    let capLeft = P.army.lazaretCap(s) - U.armyCount(s.wounded);
    const r = Math.min(0.95, ratio + P.bonus(s, 'wounded'));
    for (const t in loss) for (const tier in loss[t]) {
      const n = loss[t][tier];
      let w = Math.floor(n * r); w = Math.max(0, Math.min(w, capLeft)); capLeft -= w;
      if (w) { wounded[t] = wounded[t] || {}; wounded[t][tier] = w; }
      if (n - w) { dead[t] = dead[t] || {}; dead[t][tier] = n - w; }
    }
    return { wounded, dead };
  };
})();
