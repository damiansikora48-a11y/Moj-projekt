/* Tablica ogłoszeń, zadania, sojusz, arena, VIP, chwała, wydarzenia, sklep, czat */
(function () {
  const C = P.cfg, U = P.u;

  // ================= TABLICA OGŁOSZEŃ [DOK 14] =================
  const TASKS = {
    polowanie: { name: 'Polowanie', icon: '🐗', monster: 'zwierzeta', titles: ['Bestia napada na gospodarstwa', 'Wilki krążą przy owczarni', 'Dzik niszczy pola młynarza', 'Niedźwiedź przy barciach'], prep: 'Dobrać skład, dotrzeć do celu i pokonać przeciwnika.' },
    ratunek: { name: 'Ratunek', icon: '🗝️', monster: 'bandyci', titles: ['Bandyci porwali córkę młynarza', 'Uprowadzono kowala z Brodu', 'Jeńcy w obozie dezerterów', 'Porwany posłaniec'], prep: 'Odbić obóz i sprowadzić uratowaną osobę.' },
    eskorta: { name: 'Eskorta', icon: '🛒', monster: 'bandyci', titles: ['Kupiec potrzebuje ochrony', 'Wóz soli do Grodu', 'Karawana z suknem', 'Pielgrzymi na trakcie'], prep: 'Przydzielić ochronę i przeprowadzić karawanę przez zagrożoną trasę. Liczy się przetrwanie (straty < 50%).' },
    odzyskanie: { name: 'Odzyskanie zapasów', icon: '📦', monster: 'garnizon', titles: ['Zaginął transport żelaza', 'Zrabowane zapasy zboża', 'Skradzione drewno budowlane', 'Porzucony wóz z kamieniem'], prep: 'Odnaleźć transport, odbić go i przywieźć ładunek. Liczy się również udźwig.' },
  };
  const CHAINS = {
    jara: { name: 'Bestia przy polach', hero: 'jara', steps: 3, type: 'polowanie', unlock: 3, desc: 'Łowczyni Jara tropi bestię nękającą okolicę.' },
    borys: { name: 'Jeniec z Czarnego Obozu', hero: 'borys', steps: 3, type: 'ratunek', unlock: 5, desc: 'W obozie zbuntowanego garnizonu przetrzymywany jest dawny dowódca.' },
  };
  P.TASKS = TASKS;
  P.board = {
    init(s) { s.board.lastSlot = Math.floor(s.time / (C.board.every * C.HOUR)); for (let i = 0; i < 3; i++) s.board.offers.push(P.board.gen(s, i === 0 ? 'polowanie' : null)); },
    gen(s, type, chain) {
      type = type || U.pick(Object.keys(TASKS));
      const T = TASKS[type];
      const lvl = U.clamp(Math.max(1, s.b.siedziba) + U.ri(-1, 1) + (chain ? 1 : 0), 1, 25);
      const scale = Math.pow(1.24, lvl - 1) * (1 + 0.04 * s.b.karczma);
      const energy = U.ri(C.energy.costBoard[0], C.energy.costBoard[1]);
      const reward = { [U.pick(C.basic)]: Math.round(1500 * scale), silver: Math.round(250 * scale), xp: Math.round(120 * Math.pow(1.15, lvl)) };
      if (U.chance(0.5)) reward[U.pick(['sztaby', 'skory', 'plany'])] = 1 + Math.floor(lvl / 6);
      if (U.chance(0.25)) reward[U.pick(['k_hart', 'k_skupienie', 'k_duch'])] = 1;
      if (U.chance(0.2)) reward.sp_any = 10;
      const o = { id: U.uid(), type, lvl, energy, reward, title: U.pick(T.titles), chain: chain || null, cargo: type === 'odzyskanie' ? Math.round(900 * scale) : 0, created: s.time };
      const army = P.world.monsterArmy({ kind: T.monster, lvl, mult: type === 'eskorta' ? 1.2 : 1 });
      o.threat = P.armyPower(army, P.world.monsterMods({ lvl }));
      o.distance = U.ri(3, 7);
      o.estTime = Math.round(o.distance * C.march.secPerTile * 2 * 1000);
      if (chain) { const ch = CHAINS[chain]; o.title = `${ch.name} (${(s.board.chains[chain] || 0) + 1}/${ch.steps})`; }
      return o;
    },
    hourly(s) {
      const slot = Math.floor(s.lastHour * C.HOUR / (C.board.every * C.HOUR));
      if (slot !== s.board.lastSlot) {
        s.board.lastSlot = slot;
        let added = 0;
        for (let i = 0; i < C.board.perRefresh; i++) if (s.board.offers.length < C.board.limit) { s.board.offers.push(P.board.gen(s)); added++; }
        // łańcuchy fabularne
        for (const cid in CHAINS) { const ch = CHAINS[cid]; if (s.b.siedziba >= ch.unlock && !s.heroes[ch.hero] && (s.board.chains[cid] || 0) < ch.steps && !s.board.offers.concat(s.board.taken).some((o) => o.chain === cid) && s.board.offers.length < C.board.limit) s.board.offers.push(P.board.gen(s, ch.type, cid)); }
        if (added) P.log(s, `📋 Na tablicy pojawiły się nowe zlecenia (${added})`);
      }
    },
    nextRefresh(s) { return (s.board.lastSlot + 1) * C.board.every * C.HOUR; },
    accept(s, id) {
      const o = s.board.offers.find((x) => x.id === id); if (!o) return;
      if (s.board.taken.length >= C.board.activeMax) return P.ui.toast(`Możesz mieć najwyżej ${C.board.activeMax} przyjęte zlecenia`, 'bad');
      s.board.offers = s.board.offers.filter((x) => x !== o);
      s.board.taken.push(o);
      const h = P.world.home(s); const T = TASKS[o.type];
      let x, y, k = 0;
      do { const a = Math.random() * Math.PI * 2; x = U.clamp(Math.round(h.x + Math.cos(a) * o.distance), 0, C.map.w - 1); y = U.clamp(Math.round(h.y + Math.sin(a) * o.distance), 0, C.map.h - 1); k++; } while (k < 40 && (P.world.at(s, x, y).length || ['river', 'bridge'].includes(P.world.terrain(s, x, y))));
      const obj = P.world.addObj(s, { type: 'task', taskId: o.id, kind: T.monster, x, y, lvl: o.lvl, name: `${T.icon} ${o.title}`, mult: o.type === 'eskorta' ? 1.2 : 1 });
      o.objId = obj.id;
      P.world.reveal(s, x, y, 1);
      P.ui.toast('Zlecenie przyjęte – cel zaznaczono na mapie');
    },
    abandon(s, id) { const o = s.board.taken.find((x) => x.id === id); if (!o) return; s.board.taken = s.board.taken.filter((x) => x !== o); s.map.objs = s.map.objs.filter((x) => x.id !== o.objId); },
    chainProgress(s, cid) {
      s.board.chains[cid] = (s.board.chains[cid] || 0) + 1; const ch = CHAINS[cid];
      if (s.board.chains[cid] >= ch.steps && !s.heroes[ch.hero]) P.heroes.add(s, ch.hero);
      else if (s.board.offers.length < C.board.limit) s.board.offers.push(P.board.gen(s, ch.type, cid));
    },
    CHAINS,
  };

  // ================= ZADANIA FABULARNE I KRONIKA [DOK 2] =================
  const TUT = [
    { t: 'Oczyść plac i napraw studnię', d: 'Ocalali potrzebują wody i miejsca do pracy. Zlecenie kosztuje 100 drewna.', ok: (s) => s.quest.flags.plac, action: 'plac', reward: { food: 500, wood: 500 } },
    { t: 'Zdobądź jedzenie oraz drewno', d: 'Zbuduj Gospodarstwa i Tartak (poziom 1).', ok: (s) => s.b.gospodarstwa >= 1 && s.b.tartak >= 1, reward: { wood: 600, stone: 300 } },
    { t: 'Odbuduj pierwsze schronienie', d: 'Odbuduj Siedzibę władcy na ruinie strażnicy (poziom 1).', ok: (s) => s.b.siedziba >= 1, reward: { food: 800, wood: 800, sp_build: 15 } },
    { t: 'Uratuj zwiadowcę', d: 'Bandyci więżą zwiadowcę w obozie na wschód od osady. Wyślij ocalałych (mapa → obóz bandytów).', ok: (s) => s.quest.flags.wit, reward: { food: 1000, iron: 300 } },
    { t: 'Zorganizuj milicję', d: 'Rozbuduj siedzibę do poz. 2, zbuduj Koszary mieczników i miej co najmniej 50 żołnierzy.', ok: (s) => s.b.koszary >= 1 && U.armyCount(s.units) + U.armyCount(P.army.totalArmy(s)) / 2 >= 50, reward: { food: 1500, wood: 1000, iron: 500 } },
    { t: 'Odeprzyj niewielki napad', d: 'Zbóje z traktu idą na osadę. Wybierz dowódcę obrony i utrzymaj garnizon w osadzie.', ok: (s) => s.quest.flags.raid, start: (s) => P.raids.scriptRaid(s), reward: { stone: 1500, iron: 800, k_hart: 1 } },
    { t: 'Otwórz drogę do dalszej części mapy', d: 'Blokada na szlaku odcina osadę od świata. Rozbij ją (mapa).', ok: (s) => s.quest.flags.road, start: (s) => { const h = P.world.home(s); P.world.addObj(s, { type: 'monster', kind: 'bandyci', x: h.x + 2, y: h.y - 4, lvl: 2, mult: 0.6, name: 'Blokada na szlaku', story: 'block' }); P.world.reveal(s, h.x + 2, h.y - 4, 1); }, reward: { rubies: 50, food: 2000, wood: 2000, sp_any: 30 } },
  ];
  const CHRON = [
    { t: 'Siedziba na poziomie 5', ok: (s) => s.b.siedziba >= 5, reward: { rubies: 30, stone: 3000 } },
    { t: 'Dołącz do sojuszu lub załóż własny', ok: (s) => !!s.alliance, reward: { rubies: 30, silver: 2000 } },
    { t: 'Pokonaj 10 przeciwników na mapie', ok: (s) => s.stats.monsters >= 10, reward: { sp_train: 30, iron: 3000 } },
    { t: 'Wykonaj 5 zleceń z tablicy', ok: (s) => s.stats.tasks >= 5, reward: { k_skupienie: 1, k_hart: 1, silver: 3000 } },
    { t: 'Odbuduj przeprawę na rzece', ok: (s) => s.stats.bridges >= 1, reward: { rubies: 40, wood: 5000 } },
    { t: 'Osada przechodzi w etap: Osada (siedziba 6)', ok: (s) => s.b.siedziba >= 6, reward: { rubies: 50, sp_build: 60 } },
    { t: 'Wyszkol jednostkę stopnia II', ok: (s) => Object.values(P.army.totalArmy(s)).some((t) => t[2] || t[3]), reward: { plany: 2, sp_research: 60 } },
    { t: 'Odeprzyj 3 napady', ok: (s) => s.stats.defenses >= 3, reward: { rubies: 40, mat_wladcy: 3 } },
    { t: 'Siedziba na poziomie 10 (arena)', ok: (s) => s.b.siedziba >= 10, reward: { rubies: 80, sp_any: 120 } },
    { t: 'Etap: Gród (siedziba 11)', ok: (s) => s.b.siedziba >= 11, reward: { rubies: 100, k_duch: 2 } },
    { t: 'Zdobądź 100 000 chwały', ok: (s) => s.glory.cur >= 100000, reward: { rubies: 100 } },
    { t: 'Etap: Miasto warowne (siedziba 16)', ok: (s) => s.b.siedziba >= 16, reward: { rubies: 150 } },
    { t: 'Etap: Twierdza (siedziba 21)', ok: (s) => s.b.siedziba >= 21, reward: { rubies: 200 } },
    { t: 'Etap: Siedziba książęca (siedziba 26)', ok: (s) => s.b.siedziba >= 26, reward: { rubies: 300 } },
    { t: 'Siedziba na poziomie 30', ok: (s) => s.b.siedziba >= 30, reward: { rubies: 500 } },
  ];
  P.quests = {
    TUT, CHRON,
    current(s) { return s.quest.step < TUT.length ? TUT[s.quest.step] : null; },
    check(s) {
      const q = P.quests.current(s);
      if (q && q.ok(s)) {
        P.gain(s, q.reward); P.ui.toast(`✔ Zadanie: ${q.t}`, 'gold');
        P.log(s, `✔ Zadanie: ${q.t} (${P.rewardStr(q.reward)})`);
        s.quest.step++;
        const n = P.quests.current(s); if (n && n.start) n.start(s);
        if (!n) P.report(s, { kind: 'info', title: 'Koniec samouczka', body: 'Droga na Pogranicze stoi otworem. Kronika osady podpowie kolejne cele, a tablica ogłoszeń co 8 godzin przynosi nowe zlecenia.' });
      }
      s.quest.chron = s.quest.chron || {};
    },
    action(s, a) {
      if (a === 'plac') { if (!P.pay(s, { wood: 100 })) return P.ui.toast('Potrzeba 100 drewna', 'bad'); s.quest.flags.plac = true; P.quests.check(s); }
    },
    claimChron(s, i) { const c = CHRON[i]; s.quest.chron = s.quest.chron || {}; if (s.quest.chron[i] || !c.ok(s)) return; s.quest.chron[i] = true; const g = P.gain(s, c.reward); P.ui.toast(`Kronika: ${P.rewardStr(g)}`, 'gold'); },
  };

  // ================= SOJUSZ [DOK 18–22] =================
  const BOT_CHAT = {
    sojusz: ['Kto potrzebuje pomocy przy budowie? Klikam wszystkim.', 'Okno walk o fort dziś wieczorem – zbieramy się!', 'Wrzuciłem zasoby do badania.', 'Uwaga, Bractwo krąży przy naszej strażnicy.', 'Ktoś idzie na wiwernę? Zakładam zgrupowanie.', 'Dzięki za posiłki!', 'Pamiętajcie o dziennym wkładzie do akademii.', 'Nowi – pytajcie śmiało, pomożemy.', 'Po odnowieniu tablicy są dobre zlecenia eskorty.', 'Mur mi padł, ale lazaret uratował większość.'],
    ogolny: ['Sprzedam nudę, kupię spokój na trakcie.', 'Ktoś wie, gdzie są dobre złoża żelaza?', 'Zakon Świtu rekrutuje aktywnych!', 'Wojna o Koronę w ten weekend, kto w ogóle ma szansę?', 'Pozdro z Bagien Mgieł.', 'Ile wam zajęła siedziba 10?', 'Strażnicy dotknięci klątwą są mocni, uważajcie.', 'Arena w tym tygodniu ciężka w Złotej.'],
    prywatne: ['Hej, dzięki za pomoc!', 'Wpadniesz na zgrupowanie?', 'Możesz przysłać posiłki?', 'Dobra robota przy forcie.'],
  };
  P.alliance = {
    limit(s) { return C.alliance.baseLimit + C.alliance.perLevel * ((s.alliance && s.alliance.research.rozbudowa) || 0); },
    maybeInvite(s) { if (!s.alliance && s.b.siedziba >= 3 && !s.story.invited) { s.story.invited = true; P.report(s, { kind: 'info', title: 'Zaproszenie do sojuszu', body: 'Sojusz „Strażnicy Pogranicza” [SP] zaprasza Cię w swoje szeregi. Otwórz zakładkę Sojusz.' }); } },
    genMembers(s, ali, n) {
      const bots = s.map.objs.filter((o) => o.type === 'bot' && o.ali === ali);
      const m = bots.map((b) => ({ name: b.name, power: b.power, lvl: b.lvl, role: 'Członek', active: U.chance(0.8), contrib: 0, botId: b.id }));
      let i = 0;
      while (m.length < n) { const lvl = U.ri(2, 20); m.push({ name: P.BOT_NAMES[(i++ * 7 + ali * 3) % P.BOT_NAMES.length] + ' ' + U.pick(['z Brodu', 'Mały', 'Siwy', 'z Wrzosów', 'Śmiały', 'Rudy', 'z Doliny', 'Młodszy', 'Stary', 'z Wichrów']), power: lvl * lvl * 250, lvl, role: 'Członek', active: U.chance(0.75), contrib: 0 }); }
      if (m[0]) m[0].role = 'Przywódca'; if (m[1]) m[1].role = 'Zastępca'; for (let k = 2; k < 5 && k < m.length; k++) m[k].role = 'Oficer';
      return m;
    },
    base(s, name, tag, botAli, own) {
      return { name, tag, botAli, own, role: own ? 'Przywódca' : 'Członek', members: [], research: {}, prog: {}, priority: 'rozbudowa', coinsToday: 0, donatedToday: 0, shopWeek: {}, reinf: {}, totalCoins: 0, towers: [], project: null, joined: s.time, helpsGiven: 0, desc: own ? 'Nasz sojusz – opis do uzupełnienia.' : 'Bronimy Pogranicza od pierwszego dnia. Aktywni, pomocni, wspólne zgrupowania co wieczór.', news: [], kingBonusUntil: 0 };
    },
    join(s, ali) {
      if (s.alliance) return;
      const name = s.map.allies[ali], tag = s.map.tags[ali];
      const a = P.alliance.base(s, name, tag, ali, false);
      a.members = P.alliance.genMembers(s, ali, ali === 0 ? 32 : 36);
      a.research = { rozbudowa: 0, posilki: 2, garnizon: 1, obrona_ter: 1, umocniona: 1, pomoc: 2, zapasy: 1, karawany: 1, teren: 1 };
      a.hq = s.map.objs.find((o) => o.type === 'allyhq' && o.ali === ali) || null;
      if (!a.hq) { const any = s.map.objs.find((o) => o.type === 'bot' && o.ali === ali); a.hq = P.world.addObj(s, { type: 'allyhq', x: any.x, y: any.y + 1, name: 'Siedziba: ' + name, ali, tag }); }
      s.alliance = a;
      P.alliance.news(s, `${s.ruler.name} dołącza do sojuszu.`);
      P.ui.toast(`Dołączono do sojuszu ${name} [${tag}]`, 'good');
      P.quests.check(s);
    },
    create(s, name, tag) {
      if (s.alliance) return;
      name = (name || '').trim().slice(0, 28) || 'Sojusz ' + s.ruler.name; tag = (tag || '').trim().slice(0, 4).toUpperCase() || 'NEW';
      s.map.allies.push(name); s.map.tags.push(tag);
      const ali = s.map.allies.length - 1;
      const a = P.alliance.base(s, name, tag, ali, true);
      const h = P.world.home(s);
      a.hq = P.world.addObj(s, { type: 'allyhq', x: U.clamp(h.x + 1, 0, C.map.w - 1), y: U.clamp(h.y - 1, 0, C.map.h - 1), name: 'Siedziba: ' + name, ali, tag });
      s.alliance = a;
      P.ui.toast(`Założono sojusz ${name} [${tag}]`, 'good');
      P.quests.check(s);
    },
    leave(s) {
      if (!s.alliance) return;
      // monety zostają u gracza [DOK 22]; badania należą do sojuszu
      s.alliance = null; P.ui.toast('Opuszczono sojusz. Monety sojuszu pozostają u Ciebie.');
    },
    news(s, t) { if (!s.alliance) return; s.alliance.news.unshift({ t: s.time, m: t }); s.alliance.news.length = Math.min(30, s.alliance.news.length); },
    active(s) { return s.alliance ? s.alliance.members.filter((m) => m.active).length : 0; },
    researchNeed(id, lvl) { return Math.round(60000 * Math.pow(2.1, lvl)); },
    donateCost(s) { const f = 1 + s.b.siedziba * 0.5; return { food: Math.round(800 * f), wood: Math.round(800 * f), stone: Math.round(400 * f) }; },
    donate(s, n = 1) {
      const a = s.alliance; if (!a) return;
      let done = 0;
      for (let i = 0; i < n; i++) {
        if (a.donatedToday >= C.alliance.donateDaily) { P.ui.toast('Dzienny limit wkładu wyczerpany', 'bad'); break; }
        const c = P.alliance.donateCost(s); if (!P.pay(s, c)) { if (!done) P.ui.toast('Brak surowców', 'bad'); break; }
        a.donatedToday++; done++;
        const pts = Math.round(Object.values(c).reduce((x, y) => x + y, 0) * 1.5);
        P.alliance.addProgress(s, a.priority, pts);
        P.alliance.coins(s, C.alliance.coinsPerDonate);
      }
      if (done) P.ui.toast(`Wkład ×${done} do badania: ${C.allianceResearch[a.priority].name}`, 'good');
    },
    coins(s, n) { const a = s.alliance; if (!a) return 0; const room = Math.max(0, C.alliance.coinCapDaily - a.coinsToday); const g = Math.min(room, n); a.coinsToday += g; s.coins += g; a.totalCoins += g; if (!a.own) { if (a.totalCoins > 3000 && a.role === 'Członek') { a.role = 'Oficer'; P.ui.toast('Awans w sojuszu: Oficer', 'gold'); } if (a.totalCoins > 15000 && a.role === 'Oficer') { a.role = 'Zastępca'; P.ui.toast('Awans w sojuszu: Zastępca', 'gold'); } } return g; },
    addProgress(s, id, pts) {
      const a = s.alliance; const cur = a.research[id] || 0; if (cur >= 5) { const next = Object.keys(C.allianceResearch).find((k) => (a.research[k] || 0) < 5); if (!next) return; a.priority = next; id = next; }
      a.prog[id] = (a.prog[id] || 0) + pts;
      const need = P.alliance.researchNeed(id, a.research[id] || 0);
      if (a.prog[id] >= need) { a.prog[id] -= need; a.research[id] = (a.research[id] || 0) + 1; P.alliance.news(s, `Badanie ukończone: ${C.allianceResearch[id].name} ${a.research[id]}`); P.ui.toast(`Sojusz: ${C.allianceResearch[id].name} poz. ${a.research[id]}`, 'gold'); }
    },
    setPriority(s, id) { const a = s.alliance; if (!a || !['Przywódca', 'Zastępca'].includes(a.role)) return P.ui.toast('Priorytet wskazuje przywódca lub zastępca', 'bad'); a.priority = id; },
    helpLimit(s) { return C.alliance.helpBase + ((s.alliance && s.alliance.research.pomoc) || 0); },
    askHelp(s, q) {
      if (!s.alliance || q.helpReq) return;
      q.helpReq = true;
      const n = Math.min(P.alliance.helpLimit(s), P.alliance.active(s));
      for (let i = 0; i < n; i++) { const rem = q.end - s.time; if (rem <= 0) break; q.end -= Math.max(C.alliance.helpSec * 1000, rem * C.alliance.helpPct); }
      q.helps = n;
      P.ui.toast(`Sojusznicy pomogli ${n}×`, 'good');
    },
    helpAll(s) { const a = s.alliance; if (!a) return; const today = U.dayIdx(s.time); if (a.helpDay === today) return P.ui.toast('Dziś już pomogłeś wszystkim'); a.helpDay = today; const n = Math.min(30, P.alliance.active(s)); const g = P.alliance.coins(s, n); P.ui.toast(`Pomogłeś ${n} sojusznikom (+${g} monet)`, 'good'); },
    reinfCap(s) { return s.b.poselstwo > 0 ? Math.round(C.alliance.reinforceBase * Math.pow(1.22, s.b.poselstwo - 1) * (1 + 0.05 * ((s.alliance && s.alliance.research.garnizon) || 0))) : 0; },
    autoReinforce(s) {
      const a = s.alliance; const cap = P.alliance.reinfCap(s); if (!cap) return;
      const incoming = U.armyCount(s.raid.incoming.army);
      const n = Math.min(cap, Math.round(incoming * U.rnd(0.2, 0.6) * Math.min(1, P.alliance.active(s) / 15)));
      if (n <= 0) return;
      const tier = U.clamp(1 + Math.floor(s.b.siedziba / 5), 1, 6);
      a.reinf = { miecznik: { [tier]: Math.round(n * 0.5) }, pikinier: { [tier]: Math.round(n * 0.3) }, lucznik: { [tier]: Math.round(n * 0.2) } };
      const who = U.pick(a.members.filter((m) => m.active)) || { name: 'Sojusznik' };
      s.raid.incoming.reinfNote = `${who.name} i inni sojusznicy wysyłają ok. ${U.fmt(n)} żołnierzy (limit poselstwa: ${U.fmt(cap)}).`;
      P.log(s, '🛡️ Posiłki w drodze: ' + s.raid.incoming.reinfNote);
      a.reinfUntil = s.raid.incoming.arrive + C.HOUR;
    },
    reinforced(s, m, o) { const g = P.alliance.coins(s, 20); P.report(s, { kind: 'info', title: `Posiłki dotarły do: ${o.name}`, body: `Twoje wojsko wzmacnia sojusznika przez 8 godzin. +${g} monet sojuszu.` }); },
    rallyArmy(s, o) {
      // wojsko sojuszników dołączających do zgrupowania
      const joiners = Math.min(8, Math.max(2, Math.round(P.alliance.active(s) / 4)));
      const tier = U.clamp(1 + Math.floor(s.b.siedziba / 5), 1, 6);
      const per = Math.round(120 * Math.pow(1.2, Math.max(1, s.b.siedziba)));
      return { army: { miecznik: { [tier]: per * joiners * 0.35 | 0 }, pikinier: { [tier]: per * joiners * 0.25 | 0 }, lucznik: { [tier]: per * joiners * 0.25 | 0 }, kawaleria: { [tier]: per * joiners * 0.15 | 0 } }, joiners };
    },
    rallyArrive(s, m, o) {
      const ally = P.alliance.rallyArmy(s, o);
      const combined = U.armyAdd(U.armyClone(m.army), ally.army);
      const enemy = o.beast ? P.world.monsterArmy(o) : o.type === 'fort' ? P.forts.garrison(s, o) : P.world.monsterArmy(o);
      const res = P.fight({ army: combined, mods: P.sideMods(s, { hero: m.hero, helper: m.helper }), tactic: m.tactic }, { army: enemy, mods: P.world.monsterMods(o) }, { terrain: P.world.terrain(s, o.x, o.y), attLabel: 'zgrupowania', defLabel: 'przeciwnika' });
      // straty gracza proporcjonalne do jego udziału
      const myN = U.armyCount(m.army), allN = U.armyCount(combined) || 1; const myLoss = {};
      for (const t in res.attLoss) for (const r in res.attLoss[t]) { const mine = (m.army[t] || {})[r] || 0; const tot = (combined[t] || {})[r] || 1; const l = Math.round(res.attLoss[t][r] * mine / tot); if (l) { myLoss[t] = myLoss[t] || {}; myLoss[t][r] = l; } }
      const split = P.splitWounded(s, myLoss, C.battle.woundedPvE);
      U.armyAdd(m.army, myLoss, -1); U.armyAdd(s.wounded, split.wounded);
      const win = res.win === 'att';
      let loot = null;
      if (win) {
        const R = C.monsterReward; const sc = Math.pow(R.levelScale, o.lvl - R.refLevel) * 2;
        loot = { [U.pick(C.basic)]: Math.round(4000 * sc / 2), xp: 200 };
        if (U.chance(0.2)) loot[U.pick(C.basic)] = Math.round(50000 * sc / 2);
        let roll = Math.random(), acc = 0; for (const [v, p] of R.strongRubies) { acc += p; if (roll < acc) { if (v) loot.rubies = v; break; } }
        if (o.beast) { loot.mat_tow = 2 + Math.floor(o.lvl / 4); loot.skladniki = 1; s.stats.zakon = (s.stats.zakon || 0) + (P.events.current(s) === 'zakon' ? 1 : 0); if (!s.heroes.sambor && P.events.current(s) === 'zakon') P.heroes.add(s, 'sambor'); }
        m.loot = loot; s.map.objs = s.map.objs.filter((x) => x !== o);
        P.events.addPts(s, 'rally', 3);
        if (m.hero) P.heroes.addXp(s, m.hero, 300);
      }
      const g = P.alliance.coins(s, win ? 30 : 10);
      P.report(s, { kind: 'battle', title: `Zgrupowanie: ${o.name} – ${win ? 'zwycięstwo' : 'porażka'}`, win, reasons: res.reasons, rounds: res.log, myArmy: U.armyAdd(U.armyClone(m.army), myLoss), myLoss, wounded: split.wounded, dead: split.dead, enemyLoss: res.defLoss, enemyLeft: res.defLeft, power: res.power0, loot, note: `Dołączyło ${ally.joiners} sojuszników. Twój udział: ${U.pct(myN / allN)}. Własny raport i rozliczenie strat. +${g} monet sojuszu.`, hero: m.hero, energy: m.energy });
    },
    inTerritory(s) {
      const a = s.alliance; if (!a || !a.hq) return false; const h = P.world.home(s);
      const nodes = [{ x: a.hq.x, y: a.hq.y, r: 5 }].concat(a.towers.filter((t) => t.connected).map((t) => ({ ...t, r: 4 })));
      return nodes.some((n) => Math.hypot(n.x - h.x, n.y - h.y) <= n.r);
    },
    startProject(s) {
      const a = s.alliance; if (!a || a.project) return;
      if (!['Przywódca', 'Zastępca', 'Oficer'].includes(a.role)) return P.ui.toast('Projekt rozpoczyna przywódca, zastępca lub oficer', 'bad');
      const last = a.towers.length ? a.towers[a.towers.length - 1] : a.hq;
      const h = P.world.home(s); const ang = Math.atan2(h.y - a.hq.y, h.x - a.hq.x) + U.rnd(-0.8, 0.8);
      const x = U.clamp(Math.round(last.x + Math.cos(ang) * 5), 0, C.map.w - 1), y = U.clamp(Math.round(last.y + Math.sin(ang) * 5), 0, C.map.h - 1);
      a.project = { name: 'Odbudowa strażnicy granicznej', x, y, need: 250000 * (a.towers.length + 1), prog: 0 };
      P.alliance.news(s, 'Rozpoczęto projekt: odbudowa strażnicy granicznej.');
    },
    contribProject(s) {
      const a = s.alliance; if (!a || !a.project) return;
      const c = { wood: 2000, stone: 2000 }; if (!P.pay(s, c)) return P.ui.toast('Potrzeba 2000 drewna i 2000 kamienia', 'bad');
      a.project.prog += 6000; P.alliance.coins(s, 15); P.alliance.checkProject(s);
    },
    checkProject(s) {
      const a = s.alliance; const p = a.project; if (!p || p.prog < p.need) return;
      const tw = { x: p.x, y: p.y, connected: true, name: `Strażnica ${a.towers.length + 1}` };
      a.towers.push(tw); P.world.addObj(s, { type: 'tower', x: p.x, y: p.y, name: `${tw.name} [${a.tag}]`, ali: a.botAli });
      a.project = null; P.alliance.news(s, `${tw.name} odbudowana – teren sojuszu powiększony.`); P.ui.toast('Strażnica graniczna odbudowana!', 'gold');
    },
    shopBuy(s, id, pick) {
      const it = C.allianceShop.find((x) => x.id === id); const a = s.alliance;
      const used = (a ? a.shopWeek[id] : (s.shopWeekSolo || {})[id]) || 0;
      if (used >= it.weekly) return P.ui.toast('Tygodniowy limit wyczerpany', 'bad');
      if (s.coins < it.price) return P.ui.toast('Za mało monet sojuszu', 'bad');
      if (it.give.relocate && !a) return P.ui.toast('Przeniesienie wymaga sojuszu', 'bad');
      s.coins -= it.price;
      if (a) a.shopWeek[id] = used + 1; else { s.shopWeekSolo = s.shopWeekSolo || {}; s.shopWeekSolo[id] = used + 1; }
      P.giveBundle(s, it.give, pick);
    },
    hourly(s) {
      const a = s.alliance;
      if (!a) return;
      const act = P.alliance.active(s);
      // wkład botów w badania
      P.alliance.addProgress(s, a.priority, Math.round(act * U.rnd(150, 500)));
      if (a.project) { a.project.prog += act * U.rnd(400, 900); P.alliance.checkProject(s); }
      // aktywność członków
      for (const m of a.members) { if (U.chance(0.05)) m.active = !m.active ? U.chance(0.7) : U.chance(0.9); m.power = Math.round(m.power * (1 + U.rnd(0, 0.004))); }
      // nowi członkowie we własnym sojuszu
      if (a.own && a.members.length < P.alliance.limit(s) - 1 && U.chance(0.12)) { const nm = P.alliance.genMembers(s, -5, 1)[0]; nm.role = 'Członek'; a.members.push(nm); P.alliance.news(s, `${nm.name} dołącza do sojuszu.`); }
      // koniec posiłków
      if (a.reinfUntil && s.time > a.reinfUntil) { a.reinf = {}; a.reinfUntil = 0; }
      // prośby sojuszników o wsparcie
      if (U.chance(0.04) && a.members.length) { const m = U.pick(a.members); P.alliance.news(s, `${m.name} prosi o posiłki – nadciąga napad.`); }
      // zagrożenie strażnic
      if (a.towers.length && U.chance(0.01)) { const t = U.pick(a.towers); t.connected = U.chance(0.6); if (!t.connected) { P.report(s, { kind: 'warn', title: `${t.name} zagrożona!`, body: 'Wrogi sojusz zdobył strażnicę. Teren poza nią jest odcięty – członkowie mają 24 h na przywrócenie połączenia, potem lokalne premie wygasną.' }); t.cutAt = s.time; } }
      for (const t of a.towers) if (!t.connected && s.time - t.cutAt > C.DAY) { t.connected = true; P.alliance.news(s, `${t.name} odbita przez sojuszników.`); }
    },
  };

  // wspólne wydawanie nagród ze sklepów
  P.giveBundle = function (s, give, pick) {
    if (give.vip) P.vip.add(s, give.vip);
    if (give.items) for (const k in give.items) U.addTo(s.items, k, give.items[k]);
    if (give.speed) for (const k in give.speed) U.addTo(s.speedups, k, give.speed[k]);
    if (give.resPick) { const r = pick || 'wood'; s.res[r] += give.resPick; }
    if (give.cosmetic) { s.cosmetics[give.cosmetic] = true; P.ui.toast('Odblokowano wygląd (Profil → Wygląd)'); }
    if (give.relocate) {
      const a = s.alliance; const h = P.world.home(s);
      const x = U.clamp(a.hq.x + U.ri(-2, 2), 0, C.map.w - 1), y = U.clamp(a.hq.y + U.ri(-2, 2), 0, C.map.h - 1);
      if (!P.world.at(s, x, y).length) { h.x = x; h.y = y; P.world.reveal(s, x, y, 4); P.ui.toast('Osada przeniesiona do regionu sojuszu', 'gold'); }
    }
    P.ui.toast('Zakupiono', 'good');
  };

  // ================= ARENA [DOK 35] =================
  P.arena = {
    unlocked(s) { return s.b.arena >= 1; },
    ensure(s) {
      if (!P.arena.unlocked(s)) return null;
      if (!s.arena) {
        s.arena = { league: 0, pts: 0, wins: 0, fights: 0, freeUsed: 0, paidToday: 0, paidWeek: 0, vs: {}, offers: null, group: [], week: U.weekIdx(s.time), partClaimed: false, history: [], cups: [] };
        P.arena.newGroup(s);
      }
      if (!s.arenaTeams) s.arenaTeams = { att: { army: {}, hero: null, helper: null, tactic: 'rownowaga' }, def: { army: {}, hero: null, helper: null, tactic: 'tarcze' } };
      return s.arena;
    },
    myPower(s) { const t = s.arenaTeams.att; return P.armyPower(t.army, P.sideMods(s, { hero: t.hero, helper: t.helper })); },
    newGroup(s) {
      const A = s.arena; const base = Math.max(200, s.arenaTeams ? P.arena.myPower(s) : 300) * Math.pow(1.25, A.league);
      A.group = [];
      for (let i = 0; i < C.arena.groupSize - 1; i++) A.group.push({ name: U.pick(P.BOT_NAMES) + ' ' + U.pick(['Twardy', 'z Grodu', 'Lis', 'Kruk', 'Wilk', 'Sokół', 'Dąb', 'Rys', 'z Pól', 'Bystry']), pts: 0, wins: 0, fights: 0, power: Math.round(base * U.rnd(0.6, 1.5)), active: U.chance(0.85), id: U.uid() });
    },
    tries(s) { const A = s.arena; return { free: C.arena.free - A.freeUsed, paidLeftWeek: C.arena.paidWeekly - A.paidWeek, paidLeftDay: C.arena.paidDaily - A.paidToday }; },
    offers(s) {
      const A = s.arena; if (A.offers) return A.offers;
      const me = Math.max(50, P.arena.myPower(s));
      const pool = A.group.filter((g) => !(A.vs[g.id] >= C.arena.sameOpponentDaily));
      const pickNear = (f) => pool.slice().sort((x, y) => Math.abs(x.power - me * f) - Math.abs(y.power - me * f))[U.ri(0, 4)];
      const pickAny = () => U.pick(pool);
      A.offers = [[0.8, 10], [1.1, 15], [1.4, 20]].map(([f, p]) => { const g = pickAny(); if (!g) return null; g.power = Math.round(me * f * U.rnd(0.92, 1.08) * Math.pow(1.08, A.league)); return { id: g.id, name: g.name, power: g.power, pts: p }; }).filter(Boolean);
      A.offersAt = s.time;
      return A.offers;
    },
    refresh(s) { const A = s.arena; if (A.offersAt && s.time - A.offersAt < C.HOUR) return P.ui.toast('Darmowe odświeżenie co godzinę', 'bad'); A.offers = null; },
    botTeam(power, tier) {
      tier = tier || U.clamp(Math.round(1 + Math.log(power / 200 + 1) * 1.3), 1, 6);
      const st = P.unitStats('miecznik', tier); const per = (st.atk + st.def + st.hp / 2) / 10;
      const n = Math.min(C.arena.unitLimit, Math.round(power / per));
      const mix = U.pick([[0.35, 0.25, 0.25, 0.15], [0.2, 0.3, 0.2, 0.3], [0.3, 0.1, 0.45, 0.15], [0.25, 0.25, 0.25, 0.25]]);
      return { miecznik: { [tier]: Math.round(n * mix[0]) }, pikinier: { [tier]: Math.round(n * mix[1]) }, lucznik: { [tier]: Math.round(n * mix[2]) }, kawaleria: { [tier]: Math.round(n * mix[3]) } };
    },
    fight(s, oppId) {
      const A = s.arena; const o = (A.offers || []).find((x) => x.id === oppId); if (!o) return;
      const team = s.arenaTeams.att;
      if (U.armyCount(team.army) <= 0) return P.ui.toast('Najpierw zapisz drużynę atakującą', 'bad');
      const t = P.arena.tries(s);
      if (t.free <= 0) {
        if (t.paidLeftWeek <= 0 || t.paidLeftDay <= 0) return P.ui.toast('Brak prób (dokupione: 1 dziennie, 3 na sezon)', 'bad');
        if (s.rubies < C.arena.paidPrice) return P.ui.toast('Za mało rubinów', 'bad');
        s.rubies -= C.arena.paidPrice; A.paidToday++; A.paidWeek++;
      } else A.freeUsed++;
      const res = P.fight({ army: team.army, mods: P.sideMods(s, { hero: team.hero, helper: team.helper }), tactic: team.tactic }, { army: P.arena.botTeam(o.power, Math.max(1, ...Object.values(team.army).flatMap((x) => Object.keys(x).map(Number)))), mods: { atk: 0.05 * A.league, def: 0.05 * A.league } }, { terrain: 'plains', attLabel: 'Twojej drużyny', defLabel: 'rywala', symmetric: true });
      const win = res.win === 'att';
      A.fights++; A.vs[o.id] = (A.vs[o.id] || 0) + 1;
      if (win) { A.pts += o.pts; A.wins++; s.tokens += C.arena.winTokens; }
      A.offers = null;
      P.events.addPts(s, 'arena', 1);
      P.report(s, { kind: 'battle', arena: true, title: `Arena: ${win ? 'wygrana' : 'porażka'} z ${o.name}`, win, reasons: res.reasons, rounds: res.log, myArmy: team.army, myLoss: res.attLoss, enemyLoss: res.defLoss, enemyLeft: res.defLeft, power: res.power0, note: win ? `+${o.pts} pkt, +${C.arena.winTokens} żetonów. Arena nie zabija żołnierzy i nie tworzy rannych.` : 'Porażka nie odbiera punktów. Arena nie zabija żołnierzy.' });
      P.ui.toast(win ? `Arena: wygrana! +${o.pts} pkt` : 'Arena: porażka', win ? 'good' : 'bad');
    },
    saveTeam(s, which, army, hero, helper, tactic) {
      let n = U.armyCount(army); if (n > C.arena.unitLimit) return P.ui.toast(`Limit ${C.arena.unitLimit} jednostek arenowych`, 'bad');
      for (const t in army) for (const r in army[t]) if (r > P.army.maxTier(s, t)) return P.ui.toast('Tylko odblokowane stopnie', 'bad');
      s.arenaTeams[which] = { army, hero, helper, tactic };
      P.ui.toast('Zapisano drużynę');
    },
    ranking(s) {
      const A = s.arena; const me = { name: s.ruler.name + ' (Ty)', pts: A.pts, wins: A.wins, fights: A.fights, me: true };
      return A.group.concat([me]).sort((a, b) => b.pts - a.pts || b.wins - a.wins);
    },
    hourly(s) {
      const A = s.arena; if (!A) return;
      for (const g of A.group) if (g.active && U.chance(0.22)) { g.fights++; if (U.chance(0.55)) { g.wins++; g.pts += U.pick([10, 15, 15, 20]); } }
    },
    seasonEnd(s) {
      const A = s.arena; if (!A) return;
      const rank = P.arena.ranking(s); const place = rank.findIndex((r) => r.me) + 1;
      const activeN = rank.filter((r) => r.fights >= C.arena.activeFights).length;
      let msg = `Sezon zakończony. Miejsce: ${place}/${rank.length}, ${A.pts} pkt, ${A.wins} zwycięstw w ${A.fights} walkach.`;
      const gained = {};
      if (A.fights >= C.arena.participation.fights) { s.tokens += C.arena.participation.tokens; s.rubies += C.arena.participation.rubies; gained.tokens = C.arena.participation.tokens; gained.rubies = C.arena.participation.rubies; msg += ' Nagroda udziału odebrana.'; }
      if (A.fights >= C.arena.activeFights && A.wins >= 1 && activeN >= 50) {
        const pr = C.arena.placeRewards.find((p) => place >= p[0] && place <= p[1]);
        if (pr) { s.rubies += pr[2]; s.tokens += pr[3]; gained.rubies = (gained.rubies || 0) + pr[2]; gained.tokens = (gained.tokens || 0) + pr[3]; msg += ` Nagroda za miejsce: ${pr[4]}.`; if (place <= 3) A.cups.push({ week: A.week, place, league: C.arena.leagues[A.league] }); }
        if (place <= Math.ceil(rank.length * C.arena.promo) && A.league < 4) { A.league++; msg += ` Awans do ligi ${C.arena.leagues[A.league]}!`; }
        else if (place > rank.length * (1 - C.arena.promo) && A.league > 0) { A.league--; msg += ` Spadek do ligi ${C.arena.leagues[A.league]}.`; }
      } else if (activeN < 50) msg += ' Sezon treningowy (za mało aktywnych w grupie) – bez nagród za miejsce i bez zmian ligi.';
      A.history.unshift({ week: A.week, place, pts: A.pts, league: C.arena.leagues[A.league] });
      P.report(s, { kind: 'info', title: 'Arena: koniec sezonu', body: msg, loot: gained });
      Object.assign(A, { pts: 0, wins: 0, fights: 0, paidWeek: 0, devWeek: 0, week: U.weekIdx(s.time), offers: null, vs: {} });
      P.arena.newGroup(s);
    },
    shopBuy(s, id, pick) {
      const it = C.arena.shop.find((x) => x.id === id); const A = s.arena;
      if (it.dev && (A.devWeek || 0) >= C.arena.devWeekly) return P.ui.toast('Wspólny limit 2 zakupów rozwojowych na tydzień', 'bad');
      if (s.tokens < it.price) return P.ui.toast('Za mało żetonów', 'bad');
      s.tokens -= it.price; if (it.dev) A.devWeek = (A.devWeek || 0) + 1;
      P.giveBundle(s, it.give, pick);
    },
  };

  // ================= VIP [DOK 25] =================
  P.vip = {
    total(i) { return C.vip.levels.slice(0, i).reduce((a, b) => a + b, 0); },
    level(s) { let l = 0, acc = 0; for (const c of C.vip.levels) { acc += c; if (s.vip >= acc) l++; else break; } return l; },
    add(s, pts) {
      const before = P.vip.level(s); s.vip += pts; const after = P.vip.level(s);
      for (let l = before + 1; l <= after; l++) { s.cosmetics['vip' + l] = true; P.ui.toast(`VIP ${l}! Nagroda: ${C.vip.rewards[l - 1]}`, 'gold'); }
      s.vipLvl = after;
    },
    claimDaily(s) { if (s.vipClaimed) return; s.vipClaimed = true; P.vip.add(s, C.vip.daily); P.ui.toast(`+${C.vip.daily} pkt VIP`, 'good'); },
    buy(s, i) { const o = C.vip.shop[i]; if (s.rubies < o.price) return P.ui.toast('Za mało rubinów', 'bad'); s.rubies -= o.price; P.vip.add(s, o.pts); },
  };

  // ================= CHWAŁA [DOK 31] =================
  P.glory = {
    award(s, pts, { target, ratio }) {
      if (pts <= 0) return 0;
      const rec = s.glory.recent; const now = s.time;
      for (const k in rec) rec[k] = rec[k].filter((t) => now - t < C.DAY);
      const n = (rec[target] || []).length;
      let f = Math.pow(C.glory.repeatFactor, n);
      if (ratio != null && ratio < C.glory.weakRatio) f *= Math.max(0.05, ratio / C.glory.weakRatio);
      const g = Math.round(pts * f);
      rec[target] = (rec[target] || []).concat([now]);
      s.glory.cur += g; s.glory.total += g;
      const t = P.glory.titleFor(s.glory.cur); if (t && (!s.glory.best || P.glory.idx(t) > P.glory.idx(s.glory.best))) s.glory.best = t;
      P.glory.validate(s);
      return g;
    },
    idx(name) { return C.glory.titles.findIndex((t) => t[1] === name); },
    titleFor(v) { let t = ''; for (const [th, n] of C.glory.titles) if (v >= th) t = n; return t; },
    available(s) { return C.glory.titles.filter(([th]) => s.glory.cur >= th).map((t) => t[1]); },
    validate(s) {
      const av = P.glory.available(s);
      if (s.glory.title && !av.includes(s.glory.title)) { const nt = av[av.length - 1] || ''; P.report(s, { kind: 'info', title: 'Utrata tytułu chwały', body: `Bieżąca chwała spadła poniżej progu tytułu „${s.glory.title}”. ${nt ? 'Ustawiono: ' + nt : 'Pole tytułu pozostaje puste.'}` }); s.glory.title = nt; }
      if (!s.glory.title && av.length && !s.glory.manualEmpty) s.glory.title = av[av.length - 1];
    },
    decay(s) { s.glory.cur = Math.floor(s.glory.cur * (1 - C.glory.decay) * 100) / 100; P.glory.validate(s); },
    set(s, t) { if (t && !P.glory.available(s).includes(t)) return; s.glory.title = t; s.glory.manualEmpty = !t; },
  };

  // ================= WYDARZENIA [DOK 24] =================
  P.events = {
    current(s, t = s.time) { const k = C.events.schedule[U.weekday(t)]; if (k === 'weekend') return P.crown.active(s) ? 'korona' : 'karawany'; return k; },
    info: {
      obrona: { name: 'Obrona Pogranicza', desc: 'Przygotowanie osady i obrona przed kilkoma falami (8:00, 12:00, 16:00, 20:00 UTC).', reward: 'Materiały do wyposażenia władcy' },
      zakon: { name: 'Wyprawa Zakonu', desc: 'Zwiad, zaopatrzenie i wspólna walka sojuszu z wielką bestią (zgrupowanie).', reward: 'Materiały do wyposażenia towarzyszy' },
      korona: { name: 'Wojna o Koronę', desc: 'Kilka celów na mapie i finał przy centralnym zamku.', reward: 'Tytuły, prestiż, wygląd i ograniczone korzyści' },
      karawany: { name: 'Szlaki Karawan', desc: 'Zlecenia eskorty i odzyskiwania transportów pojawiają się częściej.', reward: 'Surowce, srebro i materiały' },
    },
    activeDefense(s) { return s.raid.incoming && s.raid.incoming.wave; },
    hourly(s) {
      const t = s.lastHour * C.HOUR; const cur = P.events.current(s, t); const h = U.hourUTC(t);
      if (cur === 'obrona' && C.events.obronaWaves.includes(h) && !s.raid.incoming && s.b.siedziba >= 3) {
        const wi = C.events.obronaWaves.indexOf(h);
        const pow = Math.max(80, P.armyPower(s.units)) * (0.5 + 0.18 * wi);
        const tier = U.clamp(1 + Math.floor(s.b.siedziba / 5), 1, 6); const st = P.unitStats('bandyta', tier); const per = (st.atk + st.def + st.hp / 2) / 10;
        const n = Math.max(15, Math.round(pow / per));
        s.raid.incoming = { arrive: t + 15 * C.MIN, army: { bandyta: { [tier]: Math.round(n * 0.6) }, strzelec: { [tier]: Math.round(n * 0.3) }, wilk: { [tier]: Math.round(n * 0.1) } }, from: `Fala ${wi + 1}/4 – Najeźdźcy z Mroczych Ostępów`, wave: wi + 1 };
        P.ui.toast(`Obrona Pogranicza: fala ${wi + 1} za 15 min!`, 'bad');
      }
      if (cur === 'zakon' && h === 9 && !s.map.objs.some((o) => o.beast) && s.b.siedziba >= 4) { const b = P.world.spawnBeast(s); if (b) P.report(s, { kind: 'info', title: 'Wyprawa Zakonu: wiwerna!', body: `Wielka bestia (poz. ${b.lvl}) pojawiła się w pobliżu (${b.x}, ${b.y}). Wymaga zgrupowania sojuszu.` }); }
      if (cur === 'karawany' && h % 6 === 0 && s.board.offers.length < C.board.limit) s.board.offers.push(P.board.gen(s, U.pick(['eskorta', 'odzyskanie'])));
    },
    onRaid(s, win) {
      // wywoływane po każdej obronie; fale wydarzenia dają materiały władcy
      const last = s.reports[0];
      if (last && /Fala (\d)/.test(last.title)) {
        const wave = +last.title.match(/Fala (\d)/)[1];
        if (win) { const g = P.gain(s, { mat_wladcy: wave, silver: 500 * wave }); P.events.addPts(s, 'wave', 4); last.note = (last.note || '') + ` Nagroda fali: ${P.rewardStr(g)}.`; }
      }
    },
    addPts(s, kind, n) {
      const wk = U.weekIdx(s.time); if (s.ev.week !== wk) { s.ev.week = wk; s.ev.pts = 0; s.ev.claimed = []; }
      s.ev.pts += n;
    },
    claim(s, i) {
      const th = C.events.thresholds[i]; P.events.addPts(s, 'x', 0);
      if (s.ev.claimed[i] || s.ev.pts < th) return;
      s.ev.claimed[i] = true; s.rubies += C.events.rubiesWeekly / C.events.thresholds.length; P.ui.toast(`+${C.events.rubiesWeekly / 2} rubinów z wydarzeń`, 'gold');
    },
    weekReset(s) { s.ev.week = U.weekIdx(s.time); s.ev.pts = 0; s.ev.claimed = []; },
  };

  // ================= SKLEP (tryb testowy) [DOK 26, 34, 36] =================
  P.shop = {
    buyRubies(s, i) { const p = C.shop.rubyPacks[i]; s.rubies += p.r; P.ui.toast(`Tryb testowy: +${p.r} rubinów (bez płatności)`, 'gold'); P.log(s, `💎 Zakup testowy: ${p.label} (${p.r})`); },
    buyPass(s) { s.pass = Math.max(s.pass, s.time) + C.shop.pass.days * C.DAY; s.cosmetics.pass_banner = true; P.ui.toast('Tryb testowy: przepustka aktywna'); },
    energyInfo(s) {
      const d = U.dayIdx(s.time), w = U.weekIdx(s.time);
      if (s.ebuy.day !== d) { s.ebuy.day = d; s.ebuy.d = 0; }
      if (s.ebuy.week !== w) { s.ebuy.week = w; s.ebuy.w = 0; }
      return { leftD: C.energy.buyDaily - s.ebuy.d, leftW: C.energy.buyWeekly - s.ebuy.w, room: C.energy.max - s.energy.v };
    },
    buyEnergy(s) {
      const i = P.shop.energyInfo(s);
      // najpierw miejsce i limit, potem płatność i przyznanie jako jedna operacja [DOK 34]
      if (i.room < C.energy.buyUnit) return P.ui.toast('Zakup możliwy, gdy w pasku zmieści się całe 10 punktów', 'bad');
      if (i.leftD <= 0) return P.ui.toast('Dzienny limit: 3 zakupy (30 energii)', 'bad');
      if (i.leftW <= 0) return P.ui.toast('Tygodniowy limit: 21 zakupów (210 energii)', 'bad');
      if (s.rubies < C.energy.buyPrice) return P.ui.toast('Za mało rubinów', 'bad');
      s.rubies -= C.energy.buyPrice; s.ebuy.d++; s.ebuy.w++; s.energy.v += C.energy.buyUnit;
      P.ui.toast(`+${C.energy.buyUnit} punktów wypraw`, 'good');
    },
    buyCosmetic(s, id) { const c = C.shop.cosmetics.find((x) => x.id === id); if (s.cosmetics[id]) return; if (s.rubies < c.price) return P.ui.toast('Za mało rubinów', 'bad'); s.rubies -= c.price; s.cosmetics[id] = true; P.ui.toast('Odblokowano: ' + c.name, 'good'); },
    finishNow(s, q, kinds) {
      const ms = q.end - s.time; const cost = P.rubyFinishCost(ms);
      if (s.rubies < cost) return P.ui.toast('Za mało rubinów', 'bad');
      s.rubies -= cost; q.end = s.time;
    },
  };

  // ================= CZAT [DOK 27] =================
  P.chat = {
    post(s, ch, from, text, sys) {
      const list = s.chat.msgs[ch] = s.chat.msgs[ch] || [];
      list.push({ t: s.time, from, text: String(text).slice(0, 300), sys: !!sys }); if (list.length > 80) list.shift();
    },
    send(s, ch, text) {
      text = (text || '').trim(); if (!text) return;
      const now = Date.now(); if (s.chat.lastSend && now - s.chat.lastSend < 2000) return P.ui.toast('Zwolnij – ograniczenie spamu (2 s)', 'bad');
      s.chat.lastSend = now;
      if (ch === 'sojusz' && !s.alliance) return P.ui.toast('Nie należysz do sojuszu', 'bad');
      P.chat.post(s, ch, s.ruler.name, text);
      if (ch.startsWith('grupa_') || ch === 'prywatne' || ch === 'sojusz') setTimeout(() => { const pool = ch === 'sojusz' ? s.alliance.members : null; const who = pool ? U.pick(pool).name : U.pick(P.BOT_NAMES); P.chat.post(s, ch, who, U.pick(['Jasne!', 'Zgoda.', 'Dzięki!', 'Daj znać, jak coś.', 'Już idę z wojskiem.', 'Dobry pomysł.', 'Haha, prawda.'])); P.ui.refresh(); }, 1500 + Math.random() * 3000);
    },
    tick(s) {
      const ch = U.pick(['ogolny', 'ogolny', 'sojusz', 'prywatne']);
      if (ch === 'sojusz' && !s.alliance) return;
      if (ch === 'prywatne' && !U.chance(0.15)) return;
      const who = ch === 'sojusz' ? U.pick(s.alliance.members).name : U.pick(P.BOT_NAMES) + (ch === 'ogolny' ? ' [' + U.pick(s.map.tags.slice(0, 3)) + ']' : '');
      if (s.chat.blocked[who.split(' [')[0]]) return;
      P.chat.post(s, ch, who, U.pick(BOT_CHAT[ch]));
    },
    block(s, name) { s.chat.blocked[name] = true; P.ui.toast(`Zablokowano: ${name}`); },
    report(s, name) { P.ui.toast(`Zgłoszono użytkownika ${name} do moderacji`); },
    newGroup(s, name, members) { const id = 'grupa_' + U.uid(); s.chat.groups.push({ id, name: (name || 'Grupa').slice(0, 24), members }); s.chat.msgs[id] = []; P.chat.post(s, id, 'System', `Utworzono grupę. Zaproszeni: ${members.join(', ')}`, true); return id; },
  };
})();
