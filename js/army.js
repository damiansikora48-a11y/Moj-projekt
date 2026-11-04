/* Wojsko, lazaret, towarzysze, wyposażenie i władca */
(function () {
  const C = P.cfg, U = P.u;

  P.army = {
    bldOf(type) { const d = C.units[type]; if (d.fort) return 'fort_' + d.fort; return Object.keys(C.buildings).find((b) => C.buildings[b].unit === type); },
    maxTier(s, type) {
      const d = C.units[type];
      if (d.fort) { let m = 1; for (const t of ['miecznik', 'pikinier', 'lucznik', 'kawaleria']) m = Math.max(m, P.army.maxTier(s, t)); return m; }
      const bid = P.army.bldOf(type); const L = s.b[bid]; if (L <= 0) return 0;
      const rs = s.research['st_' + type] || 0;
      let m = 1;
      for (let r = 2; r <= 6; r++) if (L >= C.tierBuilding[r - 1] && rs >= r - 1) m = r;
      return m;
    },
    batchMax(s, bid) { const L = bid.startsWith('fort_') ? 10 : s.b[bid]; return Math.round(20 + 18 * L * Math.pow(1.06, L)); },
    unitCost(type, tier, n = 1) { const d = C.units[type]; const c = {}; for (const k in d.cost) c[k] = Math.ceil(d.cost[k] * C.tierCost[tier - 1] * n); return c; },
    unitTime(s, type, tier, n = 1) { const d = C.units[type]; return d.time * 1000 * C.tierTime[tier - 1] * n / (1 + P.bonus(s, 'train')); },
    train(s, type, tier, n) {
      const bid = P.army.bldOf(type); n = Math.floor(n);
      if (n <= 0) return;
      if (s.trainQ[bid]) return P.ui.toast('Ten budynek już szkoli partię', 'bad');
      if (tier > P.army.maxTier(s, type)) return P.ui.toast('Ten stopień nie jest odblokowany', 'bad');
      if (n > P.army.batchMax(s, bid)) return P.ui.toast('Za duża partia', 'bad');
      if (C.units[type].fort) { const chk = P.forts.canRecruit(s, type, n); if (!chk.ok) return P.ui.toast(chk.why, 'bad'); }
      const cost = P.army.unitCost(type, tier, n);
      if (!P.pay(s, cost)) return P.ui.toast('Brak surowców', 'bad');
      if (C.units[type].fort) P.forts.noteRecruit(s, n);
      s.trainQ[bid] = { type, tier, n, start: s.time, end: s.time + P.army.unitTime(s, type, tier, n) };
      P.ui.toast(`Szkolenie: ${n} × ${C.units[type].name} ${U.roman(tier)}`);
    },
    retrain(s, type, from, to, n) {
      n = Math.floor(Math.min(n, (s.units[type] || {})[from] || 0));
      const bid = P.army.bldOf(type);
      if (n <= 0 || to <= from) return;
      if (s.trainQ[bid]) return P.ui.toast('Ten budynek już szkoli partię', 'bad');
      if (to > P.army.maxTier(s, type)) return P.ui.toast('Ten stopień nie jest odblokowany', 'bad');
      const c1 = P.army.unitCost(type, to, n), c0 = P.army.unitCost(type, from, n), cost = {};
      for (const k in c1) cost[k] = Math.max(0, c1[k] - (c0[k] || 0));
      if (!P.pay(s, cost)) return P.ui.toast('Brak surowców', 'bad');
      s.units[type][from] -= n; if (!s.units[type][from]) delete s.units[type][from];
      const time = (P.army.unitTime(s, type, to, n) - P.army.unitTime(s, type, from, n)) * 0.7 + 1000;
      s.trainQ[bid] = { type, tier: to, n, start: s.time, end: s.time + time, retrain: from };
      P.ui.toast(`Przeszkolenie: ${n} × ${C.units[type].name} ${U.roman(from)} → ${U.roman(to)}`);
    },
    finishTrain(s, bid) {
      const q = s.trainQ[bid]; delete s.trainQ[bid];
      U.armyAdd(s.units, { [q.type]: { [q.tier]: q.n } });
      P.ui.toast(`Gotowa partia: ${q.n} × ${C.units[q.type].name} ${U.roman(q.tier)}`, 'good');
      P.quests.check(s);
    },
    lazaretCap(s) { const L = s.b.lazaret; return Math.round((L > 0 ? 300 * Math.pow(1.26, L - 1) : 80) * (1 + P.bonus(s, 'heal'))); },
    healCost(s, army) { const c = {}; for (const t in army) for (const r in army[t]) { const uc = P.army.unitCost(t, +r, army[t][r]); for (const k in uc) c[k] = (c[k] || 0) + Math.ceil(uc[k] * C.heal.costFactor); } return c; },
    healTime(s, army) { let n = 0; for (const t in army) for (const r in army[t]) n += army[t][r] * (+r); return n * C.heal.timePerUnit * 1000 / (1 + P.bonus(s, 'heal')); },
    heal(s) {
      if (s.healQ) return P.ui.toast('Leczenie już trwa', 'bad');
      const army = U.armyClone(s.wounded); if (!U.armyCount(army)) return;
      const cost = P.army.healCost(s, army);
      if (!P.pay(s, cost)) return P.ui.toast('Brak surowców na leczenie', 'bad');
      s.wounded = {};
      s.healQ = { army, start: s.time, end: s.time + P.army.healTime(s, army) };
    },
    finishHeal(s) { U.armyAdd(s.units, s.healQ.army); P.ui.toast(`Wyleczono ${U.fmt(U.armyCount(s.healQ.army))} żołnierzy`, 'good'); s.healQ = null; },
    dismiss(s, type, tier, n) { const have = (s.units[type] || {})[tier] || 0; n = Math.min(n, have); if (n > 0) U.armyAdd(s.units, { [type]: { [tier]: -n } }); },
    marchCap(s) { return Math.round((C.march.baseCap + C.march.capPerSiedziba * s.b.siedziba * Math.pow(1.08, s.b.siedziba)) * (1 + P.bonus(s, 'cap'))); },
    maxMarches(s) { return C.march.baseMarches + P.bonus(s, 'marches') + (s.b.siedziba >= 10 ? 1 : 0); },
    armyLoad(s, army) { let l = 0; for (const t in army) for (const r in army[t]) l += army[t][r] * C.units[t].load * (1 + 0.1 * (r - 1)); return l * (1 + P.bonus(s, 'load')); },
    armySpeed(s, army, hero) { let v = 99; for (const t in army) if (U.armyCount({ [t]: army[t] }) > 0) v = Math.min(v, C.units[t].spd); if (v === 99) v = 1; let b = P.bonus(s, 'spd'); if (hero) b += (P.heroes.effects(s, hero).spd || 0); return v * (1 + b); },
    totalArmy(s) { const a = U.armyClone(s.units); for (const m of s.marches) U.armyAdd(a, m.army); return a; },
  };

  // ---------- towarzysze ----------
  P.heroes = {
    add(s, id) {
      if (s.heroes[id]) return;
      s.heroes[id] = { lvl: 1, xp: 0, promo: 0, spec: [], gear: {}, base: {} };
      const h = C.heroes[id];
      P.ui.toast(`Nowy towarzysz: ${h.name} (${h.role})`, 'gold');
      P.log(s, `🎖️ Dołącza towarzysz: ${h.name}, ${h.role}`);
      P.report(s, { kind: 'info', title: `Nowy towarzysz: ${h.name}`, body: `${h.icon} ${h.name} (${h.role}) dołącza do Twojej drużyny. ${h.origin}.` });
      P.heroes.snap(s, id);
    },
    snap(s, id) { const h = s.heroes[id]; h.base = { ...P.heroes.trialStat(s, id) }; },
    cap(s) { return Math.max(10, s.b.sala * 2); },
    xpNeed(l) { return Math.round(C.heroXpBase * Math.pow(C.heroXpGrowth, l - 1)); },
    lvlCap(s, id) { const h = s.heroes[id]; const promoCap = C.heroPromotions[h.promo] || C.heroMaxLevel; return Math.min(C.heroMaxLevel, promoCap, P.heroes.cap(s)); },
    addXp(s, id, xp) {
      const h = s.heroes[id]; if (!h) return;
      const bonus = P.heroes.gearEff(s, id).heroXp || 0;
      h.xp += xp * (1 + bonus);
      while (h.lvl < P.heroes.lvlCap(s, id) && h.xp >= P.heroes.xpNeed(h.lvl)) { h.xp -= P.heroes.xpNeed(h.lvl); h.lvl++; P.ui.toast(`${C.heroes[id].name} osiąga poziom ${h.lvl}`, 'good'); }
      if (h.lvl >= P.heroes.lvlCap(s, id)) h.xp = Math.min(h.xp, P.heroes.xpNeed(h.lvl));
    },
    trialStat(s, id) {
      const st = s.stats;
      return { wit: { v: st.discovered }, jara: { v: st.beasts || 0 }, borys: { v: st.cmdWins || 0 }, miroslaw: { v: st.bridges }, dobrawa: { v: st.tasks }, sambor: { v: st.zakon || 0 } }[id];
    },
    trial(s, id) {
      const h = s.heroes[id]; const p = h.promo; const d = C.heroes[id];
      const need = { wit: 40, jara: 8, borys: 6, miroslaw: 1, dobrawa: 6, sambor: 2 }[id] * (p + 1);
      const have = P.heroes.trialStat(s, id).v - (h.base.v || 0);
      return {
        lvlOk: h.lvl >= (C.heroPromotions[p] || 999), task: d.trial, need, have: Math.max(0, have), taskOk: have >= need,
        stone: d.stone, stones: 2 * (p + 1), stoneOk: (s.items[d.stone] || 0) >= 2 * (p + 1),
        silver: 2000 * Math.pow(2.5, p), silverOk: s.res.silver >= 2000 * Math.pow(2.5, p), max: p >= C.heroPromotions.length,
      };
    },
    promote(s, id, specId) {
      const tr = P.heroes.trial(s, id); const h = s.heroes[id];
      if (tr.max || !tr.lvlOk || !tr.taskOk || !tr.stoneOk || !tr.silverOk) return P.ui.toast('Próba awansu niespełniona', 'bad');
      s.items[tr.stone] -= tr.stones; s.res.silver -= tr.silver;
      h.promo++;
      if (specId && !h.spec.includes(specId)) h.spec.push(specId);
      if (h.promo === 3) for (const sp of C.heroes[id].specs) if (!h.spec.includes(sp.id)) h.spec.push(sp.id);
      P.heroes.snap(s, id);
      P.ui.toast(`${C.heroes[id].name}: awans ${h.promo}!`, 'gold');
    },
    gearEff(s, id) {
      const h = s.heroes[id]; const out = {};
      for (const slot in h.gear) { const g = s.gear[h.gear[slot]]; if (!g) continue; const st = (C.gearStats[slot] || {}).war || {}; for (const k in st) out[k] = (out[k] || 0) + st[k] * (g.tier + 1) * (1 + 0.1 * g.refine); }
      return out;
    },
    effects(s, id) {
      const h = s.heroes[id]; const d = C.heroes[id]; if (!h) return {};
      const out = {}; const m = (1 + 0.02 * (h.lvl - 1)) * (1 + 0.25 * h.promo);
      for (const k in d.base) out[k] = (out[k] || 0) + d.base[k] * m;
      for (const sid of h.spec) { const sp = d.specs.find((x) => x.id === sid); if (sp) for (const k in sp.eff) out[k] = (out[k] || 0) + sp.eff[k] * (1 + 0.1 * h.promo); }
      const ge = P.heroes.gearEff(s, id); for (const k in ge) if (k !== 'heroXp') out[k] = (out[k] || 0) + ge[k];
      return out;
    },
    busy(s, id) { return s.marches.some((m) => m.hero === id || m.helper === id); },
    effText(eff) {
      const names = { atk: 'atak', def: 'obrona', hp: 'wytrzymałość', atk_front: 'atak piechoty', def_front: 'obrona piechoty', atk_back: 'atak strzelców', atk_cav: 'atak kawalerii', spd: 'prędkość marszu', siege: 'obrażenia vs umocnienia', beast: 'vs wielkie bestie', heal: 'leczenie', wounded: 'więcej rannych zamiast poległych', build: 'szybkość budowy', walls: 'umocnienia', scout: 'zasięg zwiadu', heroXp: 'doświadczenie', prod: 'produkcja', storage: 'pojemność magazynu', gather: 'zbieranie', load: 'udźwig', research: 'badania' };
      return Object.entries(eff).map(([k, v]) => k === 'scout' ? `+${v.toFixed(0)} ${names[k]}` : `+${(v * 100).toFixed(1).replace('.', ',')}% ${names[k] || k}`).join(', ');
    },
  };

  // ---------- kuźnia i wyposażenie ----------
  P.forge = {
    maxTier(s) { let t = -1; C.gearTierForge.forEach((l, i) => { if (s.b.kuznia >= l) t = i; }); return t; },
    recipe(slot, tier) { const r = C.gearRecipe(tier); return { iron: r.iron, silver: r.silver, items: r.items }; },
    time(tier) { return 20 * C.MIN * Math.pow(tier + 1, 1.7); },
    craft(s, slot, tier, kind) {
      if (s.forgeQ) return P.ui.toast('Kuźnia jest zajęta', 'bad');
      if (tier > P.forge.maxTier(s)) return P.ui.toast('Za niski poziom kuźni', 'bad');
      const r = P.forge.recipe(slot, tier);
      if (!P.pay(s, r)) return P.ui.toast('Brak materiałów', 'bad');
      s.forgeQ = { slot, tier, kind, start: s.time, end: s.time + P.forge.time(tier) };
      P.ui.toast(`Kuźnia: ${C.gearTiers[tier]} ${(kind === 'hero' ? C.heroSlots : C.rulerSlots)[slot]}`);
    },
    finish(s) {
      const q = s.forgeQ; s.forgeQ = null;
      const id = U.uid();
      s.gear[id] = { id, slot: q.slot, tier: q.tier, kind: q.kind, refine: 0 };
      P.ui.toast(`Wykuto: ${P.forge.name(s.gear[id])}`, 'good');
    },
    name(g) { return `${C.gearTiers[g.tier]} ${(g.kind === 'hero' ? C.heroSlots : C.rulerSlots)[g.slot]}${g.refine ? ' +' + g.refine : ''}`; },
    refineCost(g) { return { silver: Math.round(500 * Math.pow(2.2, g.tier) * (g.refine + 1)), items: { sztaby: (g.refine + 1) * (g.tier + 1), ...(g.kind === 'hero' ? { mat_tow: g.refine + 1 } : { mat_wladcy: g.refine + 1 }) } }; },
    refine(s, id) { const g = s.gear[id]; if (g.refine >= C.gearRefineMax) return; if (!P.pay(s, P.forge.refineCost(g))) return P.ui.toast('Brak materiałów', 'bad'); g.refine++; P.ui.toast(`Ulepszono: ${P.forge.name(g)} (bez ryzyka)`, 'good'); },
    dismantle(s, id) {
      const g = s.gear[id]; P.forge.unequip(s, id);
      const r = P.forge.recipe(g.slot, g.tier);
      for (const k in r.items) U.addTo(s.items, k, Math.floor(r.items[k] * 0.5));
      s.res.iron += Math.floor(r.iron * 0.4);
      delete s.gear[id];
      P.ui.toast('Rozebrano przedmiot – odzyskano część materiałów');
    },
    owner(s, id) {
      for (const set of ['war', 'eco']) for (const sl in s.ruler.sets[set]) if (s.ruler.sets[set][sl] === id) return 'ruler:' + set;
      for (const h in s.heroes) for (const sl in s.heroes[h].gear) if (s.heroes[h].gear[sl] === id) return 'hero:' + h;
      return null;
    },
    unequip(s, id) {
      for (const set of ['war', 'eco']) for (const sl in s.ruler.sets[set]) if (s.ruler.sets[set][sl] === id) delete s.ruler.sets[set][sl];
      for (const h in s.heroes) for (const sl in s.heroes[h].gear) if (s.heroes[h].gear[sl] === id) delete s.heroes[h].gear[sl];
    },
    equip(s, id, target) {
      const g = s.gear[id];
      if (target.startsWith('ruler:')) {
        if (g.kind !== 'ruler') return;
        const set = target.split(':')[1];
        // przedmiot może być w obu zestawach jednocześnie (zestawy ograniczają ręczne przekładanie)
        s.ruler.sets[set][g.slot] = id;
      } else {
        if (g.kind !== 'hero') return;
        const h = target.split(':')[1]; P.forge.unequip(s, id);
        s.heroes[h].gear[g.slot] = id;
      }
    },
  };

  P.ruler = {
    title(s) {
      let t = C.rulerTitles[0].name;
      for (const rt of C.rulerTitles) {
        if (s.b.siedziba < rt.lvl) break;
        const n = rt.need; if (n && ((n.defenses && s.stats.defenses < n.defenses) || (n.bridges && s.stats.bridges < n.bridges))) break;
        t = rt.name;
      }
      return t;
    },
    nextTitle(s) {
      const cur = P.ruler.title(s); const i = C.rulerTitles.findIndex((x) => x.name === cur);
      return C.rulerTitles[i + 1] || null;
    },
    canSwitch(s) { return !s.marches.length && !s.raid.incoming && !P.events.activeDefense(s); },
    switchSet(s, set) { if (!P.ruler.canSwitch(s)) return P.ui.toast('Nie można zmienić zestawu podczas marszu, obrony lub trwającej fali wydarzenia', 'bad'); s.ruler.set = set; P.ui.toast(`Aktywny zestaw: ${set === 'war' ? 'wojenny' : 'gospodarczy'}`); },
  };
})();
