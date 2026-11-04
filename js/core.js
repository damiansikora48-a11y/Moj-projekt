/* Rdzeń gry: stan, czas, gospodarka, kolejki, zapis */
(function () {
  const C = P.cfg;
  const U = P.u = {};

  // ---------- narzędzia ----------
  U.fmt = (n) => {
    n = Math.floor(n || 0);
    const a = Math.abs(n);
    if (a >= 1e9) return (n / 1e9).toFixed(a >= 1e10 ? 0 : 1).replace('.', ',') + ' mld';
    if (a >= 1e6) return (n / 1e6).toFixed(a >= 1e7 ? 1 : 2).replace('.', ',') + ' mln';
    if (a >= 1e4) return (n / 1e3).toFixed(a >= 1e5 ? 0 : 1).replace('.', ',') + ' tys.';
    return n.toLocaleString('pl-PL');
  };
  U.full = (n) => Math.floor(n || 0).toLocaleString('pl-PL');
  U.pct = (x, d = 0) => (x * 100).toFixed(d).replace('.', ',') + '%';
  U.dur = (ms) => {
    ms = Math.max(0, ms); let s = Math.ceil(ms / 1000);
    const d = Math.floor(s / 86400); s -= d * 86400;
    const h = Math.floor(s / 3600); s -= h * 3600;
    const m = Math.floor(s / 60); s -= m * 60;
    if (d) return `${d} d ${h} h`;
    if (h) return `${h} h ${m} min`;
    if (m) return `${m} min ${s} s`;
    return `${s} s`;
  };
  U.clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  U.rnd = (a, b) => a + Math.random() * (b - a);
  U.ri = (a, b) => Math.floor(U.rnd(a, b + 1));
  U.pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  U.chance = (p) => Math.random() < p;
  U.uid = () => Math.random().toString(36).slice(2, 9);
  U.esc = (t) => String(t).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  U.seeded = (seed) => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
  U.roman = (n) => ['I', 'II', 'III', 'IV', 'V', 'VI'][n - 1] || n;
  U.stageOf = (lvl) => lvl <= 0 ? -1 : Math.min(5, Math.floor((lvl - 1) / 5));
  U.dayIdx = (t) => Math.floor(t / C.DAY);
  U.weekIdx = (t) => Math.floor((t - 4 * C.DAY) / (7 * C.DAY)); // tydzień od poniedziałku 00:00 UTC
  U.weekday = (t) => new Date(t).getUTCDay();
  U.hourUTC = (t) => new Date(t).getUTCHours();
  U.clock = (t) => { const d = new Date(t); return d.toLocaleString('pl-PL', { weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' }); };
  U.addTo = (obj, k, v) => { obj[k] = (obj[k] || 0) + v; };
  U.armyCount = (a) => { let n = 0; for (const t in a) for (const r in a[t]) n += a[t][r]; return n; };
  U.armyAdd = (dst, src, mult = 1) => { for (const t in src) for (const r in src[t]) { const v = src[t][r] * mult; if (!v) continue; dst[t] = dst[t] || {}; dst[t][r] = (dst[t][r] || 0) + v; if (dst[t][r] <= 0) delete dst[t][r]; if (!Object.keys(dst[t]).length) delete dst[t]; } return dst; };
  U.armyClone = (a) => JSON.parse(JSON.stringify(a || {}));

  // ---------- stan ----------
  P.newState = function (name) {
    const t = Date.now();
    const s = {
      v: C.version, created: t, time: t, speed: 1, lastReal: t, seed: Math.floor(Math.random() * 1e9),
      ruler: { name: name || 'Władca', sets: { war: {}, eco: {} }, set: 'war', rot: 0 },
      res: { ...C.start.res }, rubies: C.start.rubies, coins: 0, tokens: 0, vip: 0, vipLvl: 0,
      items: {}, speedups: { sp_any: 30, sp_build: 30 }, cosmetics: {}, skin: 'base', banner: 'base',
      pop: C.start.pop, popAcc: 0,
      b: {}, bq: [], damagedWalls: 0,
      research: {}, rq: null,
      units: U.armyClone(C.start.units), wounded: {}, healQ: null, trainQ: {},
      energy: { v: C.energy.startValue, acc: 0 }, ebuy: { day: -1, d: 0, week: -1, w: 0 },
      heroes: {}, gear: {}, forgeQ: null,
      marches: [], reports: [], unread: 0,
      board: { offers: [], taken: [], lastSlot: -1, chains: {} },
      quest: { step: 0, flags: {} }, story: {},
      stats: { defenses: 0, bridges: 0, wins: 0, losses: 0, kills: 0, monsters: 0, tasks: 0, discovered: 0 },
      glory: { cur: 0, total: 0, kills: 0, best: '', title: '', recent: {} },
      alliance: null, arena: null, ev: { week: -1, pts: 0, claimed: [], waves: {}, zakon: 0 },
      chat: { ch: 'ogolny', msgs: { ogolny: [], sojusz: [], prywatne: [] }, blocked: {}, groups: [] },
      shield: t + C.start.shieldDays * C.DAY,
      raid: { next: t + C.start.shieldDays * C.DAY + 6 * C.HOUR, incoming: null },
      lastDay: U.dayIdx(t), lastWeek: U.weekIdx(t), lastHour: Math.floor(t / C.HOUR),
      pass: 0, king: 0, defense: { hero: null, towers: 'piechota' }, presets: [],
      arenaTeams: null, settings: { sound: false }, log: [],
    };
    for (const id in C.buildings) s.b[id] = 0;
    P.world.generate(s);
    P.board.init(s);
    return s;
  };

  // ---------- premie ----------
  P.bonus = function (s, key) {
    let v = 0;
    for (const id in s.research) {
      const r = C.research[id]; if (!r || !r.eff || !r.eff[key]) continue;
      v += r.eff[key] * s.research[id];
    }
    // wyposażenie władcy (aktywny zestaw)
    const set = s.ruler.sets[s.ruler.set] || {};
    for (const slot in set) {
      const g = s.gear[set[slot]]; if (!g) continue;
      const st = (C.gearStats[slot] || {})[s.ruler.set === 'war' ? 'war' : 'eco'] || {};
      if (st[key]) v += st[key] * (g.tier + 1) * (1 + 0.1 * g.refine);
      if (key === 'prod_food' || key === 'prod_wood' || key === 'prod_stone' || key === 'prod_iron') {
        if (st.prod) v += st.prod * (g.tier + 1) * (1 + 0.1 * g.refine);
      }
    }
    // sojusz
    if (s.alliance) {
      const ar = s.alliance.research;
      const map = { protect: ['zapasy', 0.02], load: ['karawany', 0.03] };
      if (map[key]) v += (ar[map[key][0]] || 0) * map[key][1];
      if (key === 'gather' && P.alliance.inTerritory(s)) v += (ar.teren || 0) * 0.02;
      if (key === 'def_home' && P.alliance.inTerritory(s)) v += (ar.obrona_ter || 0) * 0.02;
      if (key === 'gather' && s.alliance.kingBonusUntil > s.time) v += C.crown.kingBonus.gather;
    }
    return v;
  };

  // ---------- gospodarka ----------
  const PROD_BASE = { food: 460, wood: 440, stone: 320, iron: 240 };
  const PROD_B = { food: 'gospodarstwa', wood: 'tartak', stone: 'kamieniolom', iron: 'kopalnia' };
  P.eco = {
    PROD_B,
    workersNeeded(s) { let n = 0; for (const r in PROD_B) { const L = s.b[PROD_B[r]]; if (L > 0) n += Math.round(3.5 * Math.pow(L, 1.3)); } return n; },
    popCap(s) { const L = s.b.domy; return Math.round((40 + (L > 0 ? 60 * Math.pow(1.17, L - 1) : 0)) * (1 + P.bonus(s, 'pop'))); },
    workFactor(s) { const need = P.eco.workersNeeded(s); return need <= 0 ? 1 : Math.min(1, s.pop / need); },
    prodRaw(res, L) { return L > 0 ? PROD_BASE[res] * Math.pow(C.prodGrowth, L - 1) : 0; },
    prod(s, res) {
      const L = s.b[PROD_B[res]];
      const base = P.eco.prodRaw(res, L) + (res === 'food' ? 40 : res === 'wood' ? 30 : 0); // drobne zbieractwo ocalałych
      return base * (1 + P.bonus(s, 'prod_' + res)) * P.eco.workFactor(s);
    },
    silverRate(s) { return 15 + s.b.rynek * 8 * Math.pow(1.09, Math.max(0, s.b.rynek - 1)) + s.b.siedziba * 4; },
    upkeep(s) {
      let u = 0; const all = [s.units, s.wounded];
      for (const m of s.marches) all.push(m.army);
      for (const a of all) for (const t in a) for (const r in a[t]) { const d = C.units[t]; if (d && d.upkeep) u += a[t][r] * d.upkeep * C.tierCost[r - 1]; }
      return u * (1 - P.bonus(s, 'upkeep'));
    },
    cap(s) { const L = s.b.magazyn; return Math.round((3000 + (L > 0 ? 6000 * Math.pow(1.27, L - 1) : 0)) * (1 + P.bonus(s, 'storage'))); },
    protectedPct(s) { return Math.min(0.6, C.protectBase + P.bonus(s, 'protect')); },
    netRates(s) {
      const r = {};
      for (const k of C.basic) r[k] = P.eco.prod(s, k);
      r.food -= P.eco.upkeep(s);
      r.silver = P.eco.silverRate(s);
      return r;
    },
    starving(s) { return s.res.food <= 0 && P.eco.netRates(s).food < 0; },
  };

  P.canPay = (s, cost) => {
    for (const k in cost) {
      if (k === 'items') { for (const i in cost.items) if ((s.items[i] || 0) < cost.items[i]) return false; continue; }
      if (k === 'rubies') { if (s.rubies < cost.rubies) return false; continue; }
      if ((s.res[k] || 0) < cost[k]) return false;
    }
    return true;
  };
  P.pay = (s, cost) => {
    if (!P.canPay(s, cost)) return false;
    for (const k in cost) {
      if (k === 'items') { for (const i in cost.items) s.items[i] -= cost.items[i]; continue; }
      if (k === 'rubies') { s.rubies -= cost.rubies; continue; }
      s.res[k] -= cost[k];
    }
    return true;
  };
  P.gain = (s, res, mult = 1) => {
    const cap = P.eco.cap(s); const out = {};
    for (const k in res) {
      const v = Math.floor(res[k] * mult); if (!v) continue;
      if (k === 'rubies') { s.rubies += v; out.rubies = v; continue; }
      if (k === 'xp' || k === 'glory') continue;
      if (C.items[k]) { U.addTo(s.items, k, v); out[k] = v; continue; }
      if (C.speedups[k]) { U.addTo(s.speedups, k, v); out[k] = v; continue; }
      if (k === 'silver') { s.res.silver += v; out.silver = v; continue; }
      if (C.resources[k]) {
        // nagrody mogą przekroczyć pojemność magazynu (jak paczki) - przepełnienie nie produkuje dalej
        s.res[k] = (s.res[k] || 0) + v; out[k] = v; continue;
      }
      if (k === 'coins') { s.coins += v; out.coins = v; continue; }
      if (k === 'tokens') { s.tokens += v; out.tokens = v; continue; }
      if (k === 'vip') { P.vip.add(s, v); out.vip = v; continue; }
    }
    return out;
  };
  P.costStr = (cost, s) => {
    const parts = [];
    for (const k in cost) {
      if (k === 'items') { for (const i in cost.items) { const ok = !s || (s.items[i] || 0) >= cost.items[i]; parts.push(`<span class="${ok ? '' : 'bad'}">${C.items[i].icon} ${U.fmt(cost.items[i])}</span>`); } continue; }
      if (!cost[k]) continue;
      const ic = k === 'rubies' ? '💎' : C.resources[k] ? C.resources[k].icon : k;
      const have = k === 'rubies' ? s && s.rubies : s && s.res[k];
      const ok = !s || have >= cost[k];
      parts.push(`<span class="${ok ? '' : 'bad'}">${ic} ${U.fmt(cost[k])}</span>`);
    }
    return parts.join(' ');
  };
  P.rewardStr = (r) => {
    const parts = [];
    for (const k in r) {
      if (!r[k]) continue;
      if (k === 'rubies') parts.push(`💎 ${U.fmt(r[k])}`);
      else if (k === 'xp') parts.push(`⭐ ${U.fmt(r[k])} dośw.`);
      else if (k === 'glory') parts.push(`🏅 ${U.fmt(r[k])} chwały`);
      else if (k === 'coins') parts.push(`🔰 ${U.fmt(r[k])} monet sojuszu`);
      else if (k === 'tokens') parts.push(`🎟️ ${U.fmt(r[k])} żetonów`);
      else if (k === 'vip') parts.push(`✨ ${U.fmt(r[k])} VIP`);
      else if (C.resources[k]) parts.push(`${C.resources[k].icon} ${U.fmt(r[k])}`);
      else if (C.items[k]) parts.push(`${C.items[k].icon} ${C.items[k].name} ×${r[k]}`);
      else if (C.speedups[k]) parts.push(`${C.speedups[k].icon} ${r[k]} min`);
    }
    return parts.join(', ');
  };

  // ---------- budynki ----------
  P.bld = {
    cost(id, L) {
      const d = C.buildings[id]; const c = {};
      for (const k in d.cost) { const [base, from] = d.cost[k]; if (L >= from) c[k] = Math.round(base * Math.pow(C.costGrowth, L - 1) / 10) * 10; }
      return c;
    },
    time(s, id, L) { const d = C.buildings[id]; return d.time * 1000 * Math.pow(C.timeGrowth, L - 1) / (1 + P.bonus(s, 'build')); },
    queues(s) { return C.buildQueuesBase + P.bonus(s, 'queues'); },
    reqs(s, id, L) {
      const d = C.buildings[id]; const out = [];
      if (id === 'siedziba') {
        if (L === 1 && !s.quest.flags.plac) out.push({ ok: false, t: 'Najpierw oczyść plac i napraw studnię (zadanie)' });
        if (L >= 3) out.push({ ok: s.b.magazyn >= L - 1, t: `Magazyn poz. ${L - 1}` });
        if (L >= 6) out.push({ ok: s.b.mury >= L - 1, t: `Mury poz. ${L - 1}` });
        if (L >= 10) out.push({ ok: s.b.akademia >= L - 2, t: `Akademia poz. ${L - 2}` });
      } else {
        if (s.b.siedziba < d.unlock) out.push({ ok: false, t: `Siedziba poz. ${d.unlock}` });
        if (L > Math.max(1, s.b.siedziba) && d.max > 5) out.push({ ok: false, t: `Siedziba poz. ${L} (siedziba ogranicza poziom)` });
        if (id === 'arena' && s.b.siedziba < C.arena.unlockSiedziba) out.push({ ok: false, t: `Siedziba poz. ${C.arena.unlockSiedziba}` });
      }
      return out;
    },
    inQueue(s, id) { return s.bq.find((q) => q.id === id); },
    canUpgrade(s, id) {
      const L = s.b[id] + 1; const d = C.buildings[id];
      if (L > d.max) return { ok: false, why: 'Maksymalny poziom' };
      if (P.bld.inQueue(s, id)) return { ok: false, why: 'Trwa ulepszanie' };
      const rq = P.bld.reqs(s, id, L).filter((r) => !r.ok);
      if (rq.length) return { ok: false, why: 'Wymagania: ' + rq.map((r) => r.t).join(', ') };
      if (s.bq.length >= P.bld.queues(s)) return { ok: false, why: 'Wszystkie kolejki budowy zajęte' };
      if (!P.canPay(s, P.bld.cost(id, L))) return { ok: false, why: 'Brak surowców', res: true };
      return { ok: true };
    },
    start(s, id) {
      const c = P.bld.canUpgrade(s, id); if (!c.ok) { P.ui.toast(c.why, 'bad'); return false; }
      const L = s.b[id] + 1;
      P.pay(s, P.bld.cost(id, L));
      const dur = P.bld.time(s, id, L);
      s.bq.push({ id, to: L, start: s.time, end: s.time + dur, helps: 0, helpReq: false });
      P.ui.toast(`Rozpoczęto: ${C.buildings[id].name} → poz. ${L}`);
      P.quests.check(s);
      return true;
    },
    finish(s, q) {
      s.b[q.id] = q.to;
      s.bq = s.bq.filter((x) => x !== q);
      const d = C.buildings[q.id];
      const st = U.stageOf(q.to), pst = U.stageOf(q.to - 1);
      let msg = `${d.name}: poziom ${q.to}`;
      if (st !== pst && d.max === 30) msg += ` — nowy etap wyglądu: ${C.stages[st].bld}`;
      P.ui.toast(msg, 'good');
      P.log(s, '🏗️ ' + msg);
      if (q.id === 'siedziba') { if (st !== pst) P.ui.toast(`Osada staje się: ${C.stages[st].city}`, 'gold'); P.alliance && P.alliance.maybeInvite(s); }
      P.quests.check(s);
    },
    cancel(s, q) {
      const c = P.bld.cost(q.id, q.to);
      for (const k in c) s.res[k] += Math.floor(c[k] * 0.5);
      s.bq = s.bq.filter((x) => x !== q);
      P.ui.toast('Anulowano budowę (zwrot 50%)');
    },
  };

  // ---------- przyspieszenia ----------
  P.speedup = function (s, target, kind, minutes) {
    // target: obiekt z polem end
    const have = (s.speedups[kind] || 0);
    const use = Math.min(have, minutes);
    if (use <= 0) return 0;
    s.speedups[kind] -= use;
    target.end -= use * C.MIN;
    return use;
  };
  P.speedupAuto = function (s, target, kinds) {
    // zużywa przyspieszenia (najpierw konkretne, potem ogólne) aż do końca lub wyczerpania
    let need = Math.ceil((target.end - s.time) / C.MIN);
    let used = 0;
    for (const k of kinds.concat(['sp_any'])) {
      if (need <= 0) break;
      const u = P.speedup(s, target, k, need); need -= u; used += u;
    }
    return used;
  };
  P.rubyFinishCost = (ms) => Math.max(1, Math.ceil(ms / C.MIN / 3)); // 1 rubin za 3 minuty

  // ---------- badania ----------
  P.res = {
    time(s, id, L) { const r = C.research[id]; return r.time * 1000 * Math.pow(r.growth, L - 1) / (1 + P.bonus(s, 'research')); },
    cost(id, L) {
      const r = C.research[id]; const f = Math.pow(r.growth, L - 1) * (r.time / 1800);
      return { food: Math.round(400 * f), wood: Math.round(400 * f), stone: Math.round(250 * f), iron: Math.round(150 * f), silver: Math.round(60 * f) };
    },
    reqs(s, id, L) {
      const r = C.research[id]; const out = [];
      const ak = Math.max(1, Math.min(30, (L - 1) * 3 + 1 + (r.max <= 3 ? 4 : 0)));
      const pre = C.researchPrereq[id];
      let need = ak; if (pre) need = Math.max(need, +pre.split(':')[1]);
      if (r.tierOf) { // stopnie jednostek wymagają też budynku
        const bid = Object.keys(C.buildings).find((b) => C.buildings[b].unit === r.tierOf);
        const bl = C.tierBuilding[L];
        out.push({ ok: s.b[bid] >= bl, t: `${C.buildings[bid].name} poz. ${bl}` });
        need = Math.max(need, Math.min(30, bl));
      }
      out.unshift({ ok: s.b.akademia >= need, t: `Akademia poz. ${need}` });
      return out;
    },
    can(s, id) {
      const L = (s.research[id] || 0) + 1; const r = C.research[id];
      if (L > r.max) return { ok: false, why: 'Ukończone' };
      if (s.rq) return { ok: false, why: 'Trwa inne badanie' };
      const rq = P.res.reqs(s, id, L).filter((x) => !x.ok);
      if (rq.length) return { ok: false, why: 'Wymagania: ' + rq.map((x) => x.t).join(', ') };
      if (!P.canPay(s, P.res.cost(id, L))) return { ok: false, why: 'Brak surowców' };
      return { ok: true };
    },
    start(s, id) {
      const c = P.res.can(s, id); if (!c.ok) { P.ui.toast(c.why, 'bad'); return; }
      const L = (s.research[id] || 0) + 1;
      P.pay(s, P.res.cost(id, L));
      s.rq = { id, to: L, start: s.time, end: s.time + P.res.time(s, id, L), helps: 0, helpReq: false };
      P.ui.toast(`Rozpoczęto badanie: ${C.research[id].name} ${L}`);
    },
    finish(s) {
      const q = s.rq; s.research[q.id] = q.to; s.rq = null;
      P.ui.toast(`Badanie ukończone: ${C.research[q.id].name} ${q.to}`, 'good');
      P.log(s, `📘 Badanie: ${C.research[q.id].name} poz. ${q.to}`);
    },
  };

  // ---------- czas i pętla ----------
  function accrue(s, dt) {
    if (dt <= 0) return;
    const h = dt / C.HOUR;
    const cap = P.eco.cap(s);
    const rates = P.eco.netRates(s);
    for (const k of C.basic) {
      const r = rates[k];
      if (r >= 0) { if (s.res[k] < cap) s.res[k] = Math.min(cap, s.res[k] + r * h); }
      else s.res[k] = Math.max(0, s.res[k] + r * h);
    }
    s.res.silver += rates.silver * h;
    // ludność
    const pc = P.eco.popCap(s);
    if (s.pop < pc) s.pop = Math.min(pc, s.pop + Math.max(1, pc * 0.08) * h);
    else if (s.pop > pc) s.pop = pc;
    // energia
    const E = s.energy;
    if (E.v >= C.energy.max) E.acc = 0;
    else {
      E.acc += dt;
      const step = C.energy.regenMin * C.MIN;
      while (E.acc >= step && E.v < C.energy.max) { E.v++; E.acc -= step; }
      if (E.v >= C.energy.max) E.acc = 0;
    }
  }

  function nextEvents(s) {
    const ev = [];
    for (const q of s.bq) ev.push([q.end, () => P.bld.finish(s, q)]);
    if (s.rq) ev.push([s.rq.end, () => P.res.finish(s)]);
    for (const b in s.trainQ) { const q = s.trainQ[b]; if (q) ev.push([q.end, () => P.army.finishTrain(s, b)]); }
    if (s.healQ) ev.push([s.healQ.end, () => P.army.finishHeal(s)]);
    if (s.forgeQ) ev.push([s.forgeQ.end, () => P.forge.finish(s)]);
    for (const m of s.marches) ev.push([m.next, () => P.world.marchStep(s, m)]);
    if (s.raid.incoming) ev.push([s.raid.incoming.arrive, () => P.raids.resolve(s)]);
    else ev.push([s.raid.next, () => P.raids.announce(s)]);
    ev.push([(s.lastHour + 1) * C.HOUR, () => hourTick(s)]);
    return ev;
  }

  function hourTick(s) {
    s.lastHour++;
    const t = s.lastHour * C.HOUR;
    const day = U.dayIdx(t);
    if (day !== s.lastDay) { s.lastDay = day; dailyReset(s); }
    const wk = U.weekIdx(t);
    if (wk !== s.lastWeek) { s.lastWeek = wk; weeklyReset(s); }
    P.board.hourly(s);
    P.alliance.hourly(s);
    P.world.hourly(s);
    P.events.hourly(s);
    P.arena.hourly(s);
  }

  function dailyReset(s) {
    // chwała: spadek 0,05% aktualnego stanu dziennie [DOK 31]
    P.glory.decay(s);
    s.ebuy.d = 0; s.ebuy.day = s.lastDay;
    if (s.alliance) { s.alliance.donatedToday = 0; s.alliance.coinsToday = 0; }
    if (s.arena) { s.arena.freeUsed = 0; s.arena.paidToday = 0; s.arena.vs = {}; s.arena.offers = null; }
    if (s.pass > s.time) { s.rubies += C.shop.pass.dailyRubies; P.log(s, `🎫 Przepustka: +${C.shop.pass.dailyRubies} rubinów`); }
    s.vipClaimed = false;
  }
  function weeklyReset(s) {
    s.ebuy.w = 0; s.ebuy.week = s.lastWeek;
    if (s.alliance) s.alliance.shopWeek = {};
    P.arena.seasonEnd(s);
    P.events.weekReset(s);
  }

  P.advance = function (s, dt) {
    const target = s.time + dt;
    let guard = 0;
    while (guard++ < 200000) {
      const ev = nextEvents(s);
      let best = null;
      for (const e of ev) if (e[0] <= target && (!best || e[0] < best[0])) best = e;
      if (!best) break;
      const tt = Math.max(s.time, best[0]);
      accrue(s, tt - s.time); s.time = tt;
      best[1]();
    }
    accrue(s, target - s.time); s.time = target;
  };

  // ---------- dziennik ----------
  P.log = (s, msg) => { s.log.unshift({ t: s.time, m: msg }); if (s.log.length > 120) s.log.length = 120; };
  P.report = (s, rep) => {
    rep.id = U.uid(); rep.t = s.time; rep.read = false;
    s.reports.unshift(rep); if (s.reports.length > 80) s.reports.length = 80;
    s.unread++;
  };

  // ---------- zapis ----------
  P.save = function (s) {
    s.lastReal = Date.now();
    try { localStorage.setItem(C.saveKey, JSON.stringify(s)); } catch (e) { /* brak miejsca lub tryb prywatny */ }
  };
  P.load = function () {
    try { const raw = localStorage.getItem(C.saveKey); if (!raw) return null; const s = JSON.parse(raw); if (!s || s.v !== C.version) return null; return s; } catch (e) { return null; }
  };
  P.catchUp = function (s) {
    const realGap = Math.max(0, Date.now() - (s.lastReal || Date.now()));
    const dt = Math.min(realGap * s.speed, C.offlineCapDays * C.DAY);
    if (dt > 5000) {
      const before = { ...s.res };
      const rep0 = s.reports.length;
      P.advance(s, dt);
      return { dt, gained: Object.fromEntries(C.basic.map((k) => [k, Math.max(0, s.res[k] - before[k])])), reports: s.reports.length - rep0 };
    }
    return null;
  };
})();
