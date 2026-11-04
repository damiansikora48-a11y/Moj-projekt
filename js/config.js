/* =====================================================================
   Pogranicza: Droga do Korony  -  KONFIGURACJA I BALANS (wartości robocze)
   ---------------------------------------------------------------------
   Wszystkie liczby, które koncepcja oznacza jako "Otwarte", zostały tu
   dobrane roboczo do prototypu. Wartości "Przyjęte" i "Robocze" z
   dokumentu (wersja 1.3) są przeniesione 1:1 i oznaczone [DOK].
   Zmiana wartości tutaj zmienia balans całej gry.
   ===================================================================== */
window.P = window.P || {};

P.cfg = {
  version: 1,
  saveKey: 'pogranicza_save_v1',

  // ---------- czas ----------
  MIN: 60e3, HOUR: 3600e3, DAY: 86400e3,
  speeds: [1, 10, 60, 360],            // tryb przyspieszony do testów
  offlineCapDays: 14,                   // maks. nadrabianie po powrocie (czasu gry)

  // ---------- start ----------
  start: {
    res: { food: 1500, wood: 1500, stone: 400, iron: 200, silver: 300 },
    rubies: 100,
    pop: 20,
    units: { miecznik: { 1: 25 } },     // grupa ocalałych zdolnych do walki
    shieldDays: 3,                      // ochrona początkowa przed napadami
  },

  // ---------- surowce ----------
  resources: {
    food:   { name: 'Jedzenie', icon: '🌾' },
    wood:   { name: 'Drewno',   icon: '🪵' },
    stone:  { name: 'Kamień',   icon: '🪨' },
    iron:   { name: 'Żelazo',   icon: '⛓️' },
    silver: { name: 'Srebro',   icon: '🪙' },
  },
  basic: ['food', 'wood', 'stone', 'iron'],

  // Przedmioty / materiały (osobne od surowców) [DOK 6, 8]
  items: {
    skory:     { name: 'Skóry',              icon: '🦌' },
    sztaby:    { name: 'Sztaby stali',       icon: '🔩' },
    plany:     { name: 'Plany wojskowe',     icon: '📜' },
    relikty:   { name: 'Relikty',            icon: '🏺' },
    skladniki: { name: 'Rzadkie składniki',  icon: '🧪' },
    mat_wladcy:{ name: 'Materiały władcy',   icon: '👑' },
    mat_tow:   { name: 'Materiały towarzyszy', icon: '🎖️' },
    k_hart:    { name: 'Kamień hartu',       icon: '🔴' },
    k_skupienie:{ name: 'Kamień skupienia',  icon: '🔵' },
    k_duch:    { name: 'Kamień ducha',       icon: '🟣' },
  },

  // Przyspieszenia w minutach, wg rodzaju
  speedups: {
    sp_any:   { name: 'Przyspieszenie ogólne', icon: '⏩' },
    sp_build: { name: 'Przyspieszenie budowy', icon: '🔨' },
    sp_train: { name: 'Przyspieszenie rekrutacji', icon: '🗡️' },
    sp_heal:  { name: 'Przyspieszenie leczenia', icon: '➕' },
    sp_research: { name: 'Przyspieszenie badań', icon: '📘' },
  },

  // ---------- energia: punkty wypraw [DOK 15, 34] ----------
  energy: {
    max: 240, regenMin: 6,
    costBoard: [15, 25], costMonster: 10, costStrong: 25, costRally: 20,
    buyUnit: 10, buyPrice: 60, buyDaily: 3, buyWeekly: 21,
    startValue: 240,
  },

  // ---------- tablica ogłoszeń [DOK 14] ----------
  board: { every: 8, perRefresh: 3, limit: 9, activeMax: 3 },

  // ---------- etapy wyglądu [DOK 4, 37] ----------
  stages: [
    { from: 1,  to: 5,  city: 'Obozowisko',        bld: 'Odbudowane schronienie' },
    { from: 6,  to: 10, city: 'Osada',             bld: 'Stała zabudowa drewniana' },
    { from: 11, to: 15, city: 'Gród',              bld: 'Początek zabudowy murowanej' },
    { from: 16, to: 20, city: 'Miasto warowne',    bld: 'Rozwinięty kompleks' },
    { from: 21, to: 25, city: 'Twierdza',          bld: 'Zaplecze twierdzy' },
    { from: 26, to: 30, city: 'Siedziba książęca', bld: 'Zabudowa książęca' },
  ],

  // ---------- tytuły władcy [DOK 7] ----------
  rulerTitles: [
    { lvl: 1,  name: 'Przywódca ocalałych', need: null },
    { lvl: 6,  name: 'Naczelnik osady',     need: { defenses: 1 } },
    { lvl: 11, name: 'Kasztelan',           need: { defenses: 3, bridges: 1 } },
    { lvl: 16, name: 'Baron',               need: { defenses: 6, bridges: 2 } },
    { lvl: 21, name: 'Hrabia',              need: { defenses: 10, bridges: 3 } },
    { lvl: 26, name: 'Książę',              need: { defenses: 15, bridges: 4 } },
  ],

  // ---------- budynki ----------
  // cost: [baza, od poziomu]; koszt(L) = baza * costGrowth^(L-1)
  // time: sekundy dla poziomu 1; czas(L) = time * timeGrowth^(L-1)
  costGrowth: 1.40, timeGrowth: 1.42, prodGrowth: 1.155,
  buildQueuesBase: 1,
  buildings: {
    siedziba: { name: 'Siedziba władcy', cat: 'zarzad', max: 30, unlock: 0, time: 90,
      cost: { wood: [140, 1], food: [100, 1], stone: [130, 3], iron: [100, 9] },
      desc: 'Główny budynek rozwoju. Odblokowuje etapy osady i ogranicza poziom pozostałych budynków.' },
    domy: { name: 'Domy', cat: 'zarzad', max: 30, unlock: 1, time: 30,
      cost: { wood: [90, 1], food: [40, 1], stone: [60, 8] },
      desc: 'Miejsce dla mieszkańców. Więcej mieszkańców to więcej pracowników w budynkach produkcyjnych.' },
    gospodarstwa: { name: 'Gospodarstwa', cat: 'produkcja', max: 30, unlock: 0, time: 25, prod: 'food',
      cost: { wood: [70, 1], stone: [40, 6] }, desc: 'Produkują jedzenie dla mieszkańców i wojska.' },
    tartak: { name: 'Tartak', cat: 'produkcja', max: 30, unlock: 0, time: 25, prod: 'wood',
      cost: { wood: [40, 1], food: [50, 1], stone: [40, 6] }, desc: 'Produkuje drewno do budowy i prac warsztatowych.' },
    kamieniolom: { name: 'Kamieniołom', cat: 'produkcja', max: 30, unlock: 2, time: 35, prod: 'stone',
      cost: { wood: [90, 1], food: [60, 1] }, desc: 'Dostarcza kamień, kluczowy przy przejściu na zabudowę murowaną.' },
    kopalnia: { name: 'Kopalnia żelaza', cat: 'produkcja', max: 30, unlock: 3, time: 40, prod: 'iron',
      cost: { wood: [100, 1], food: [70, 1], stone: [60, 3] }, desc: 'Dostarcza żelazo na wyposażenie, szkolenie i rozwój wojskowy. Wejście w skale.' },
    magazyn: { name: 'Magazyn i spichlerz', cat: 'zaplecze', max: 30, unlock: 1, time: 30,
      cost: { wood: [100, 1], stone: [70, 3], iron: [50, 12] }, desc: 'Przechowuje zasoby. Część pojemności jest chroniona przed rabunkiem.' },
    koszary: { name: 'Koszary mieczników', cat: 'wojsko', max: 30, unlock: 2, time: 45, unit: 'miecznik',
      cost: { wood: [120, 1], food: [80, 1], stone: [80, 4], iron: [60, 8] }, desc: 'Rekrutują podstawową piechotę walczącą mieczem i tarczą.' },
    pikinierzy: { name: 'Plac pikinierów', cat: 'wojsko', max: 30, unlock: 3, time: 45, unit: 'pikinier',
      cost: { wood: [130, 1], food: [80, 1], stone: [70, 4], iron: [60, 8] }, desc: 'Szkoli piechotę z pikami, zatrzymującą kawalerię i broniącą podejść.' },
    lucznicy: { name: 'Strzelnica łuczników', cat: 'wojsko', max: 30, unlock: 4, time: 45, unit: 'lucznik',
      cost: { wood: [140, 1], food: [70, 1], stone: [70, 4], iron: [50, 8] }, desc: 'Szkoli łuczników, którzy potrzebują osłony innych jednostek.' },
    stajnia: { name: 'Stajnia', cat: 'wojsko', max: 30, unlock: 6, time: 50, unit: 'kawaleria',
      cost: { wood: [150, 1], food: [120, 1], stone: [80, 4], iron: [80, 8] }, desc: 'Rekrutacja i przeszkalanie kawalerii.' },
    warsztat: { name: 'Warsztat oblężniczy', cat: 'wojsko', max: 30, unlock: 8, time: 60, unit: 'taran',
      cost: { wood: [200, 1], stone: [120, 1], iron: [100, 1] }, desc: 'Przygotowuje tarany do działań przeciw umocnieniom.' },
    mury: { name: 'Mury', cat: 'obrona', max: 30, unlock: 2, time: 40,
      cost: { wood: [110, 1], stone: [120, 3], iron: [40, 12] }, desc: 'Zamykają zachodnią i południową stronę osady. Zwiększają obronę garnizonu.' },
    brama: { name: 'Brama', cat: 'obrona', max: 30, unlock: 2, time: 35,
      cost: { wood: [100, 1], stone: [80, 3], iron: [60, 10] }, desc: 'Kontroluje główny dostęp od strony szlaku. Wytrzymałość umocnień.' },
    wieze: { name: 'Wieże', cat: 'obrona', max: 30, unlock: 5, time: 40,
      cost: { wood: [120, 1], stone: [140, 1], iron: [60, 8] }, desc: 'Ostrzeliwują napastników. Tryb: ostrzał piechoty lub zwalczanie machin.' },
    lazaret: { name: 'Lazaret', cat: 'obrona', max: 30, unlock: 3, time: 35,
      cost: { wood: [90, 1], food: [90, 1], stone: [50, 5] }, desc: 'Przyjmuje rannych po bitwach. Leczenie przywraca część wojska.' },
    akademia: { name: 'Akademia', cat: 'zaplecze', max: 30, unlock: 4, time: 60,
      cost: { wood: [160, 1], stone: [120, 1], iron: [60, 6], silver: [50, 1] }, desc: 'Osobiste badania: Wojsko, Surowce oraz Ekonomia i administracja.' },
    kuznia: { name: 'Kuźnia', cat: 'zaplecze', max: 30, unlock: 5, time: 50,
      cost: { wood: [120, 1], stone: [100, 1], iron: [120, 1] }, desc: 'Wytwarzanie, ulepszanie i rozbieranie wyposażenia.' },
    sala: { name: 'Sala towarzyszy', cat: 'zaplecze', max: 30, unlock: 5, time: 50,
      cost: { wood: [140, 1], stone: [100, 1], silver: [60, 1] }, desc: 'Zarządzanie towarzyszami. Poziom sali ogranicza poziom towarzyszy.' },
    rynek: { name: 'Rynek', cat: 'zaplecze', max: 30, unlock: 3, time: 40,
      cost: { wood: [120, 1], food: [60, 1], stone: [60, 5] }, desc: 'Handel i wymiana zasobów na srebro.' },
    karczma: { name: 'Karczma z tablicą ogłoszeń', cat: 'zaplecze', max: 30, unlock: 1, time: 30,
      cost: { wood: [100, 1], food: [80, 1], stone: [40, 6] }, desc: 'Krótkie zlecenia i powiązane historie. Poziom zwiększa nagrody zleceń.' },
    poselstwo: { name: 'Poselstwo', cat: 'zaplecze', max: 30, unlock: 6, time: 45,
      cost: { wood: [130, 1], stone: [90, 1], silver: [40, 1] }, desc: 'Pomoc sojuszu i przyjmowanie posiłków.' },
    arena: { name: 'Arena', cat: 'zaplecze', max: 5, unlock: 10, time: 600,
      cost: { wood: [4000, 1], stone: [4000, 1], iron: [1500, 1] }, desc: 'Turniejowe walki rankingowe bez strat wojska. Przebudowy zmieniają wygląd i liczbę zestawów.' },
  },
  // Pierwsza budowa przy siedzibie (koszary 2, pikinierzy 3, łucznicy 4, stajnia 6) [DOK 37]

  // ---------- jednostki [DOK 9, 16] ----------
  tierStat: [1, 1.4, 1.95, 2.7, 3.7, 5.0],
  tierCost: [1, 1.5, 2.2, 3.2, 4.6, 6.5],
  tierTime: [1, 1.4, 1.9, 2.6, 3.5, 4.7],
  tierGlory: [1, 1.6, 2.5, 4, 6, 9],
  tierBuilding: [1, 6, 11, 16, 21, 26],   // poziom budynku wymagany dla stopnia I–VI
  units: {
    miecznik:  { name: 'Miecznicy',  short: 'Miecz.', icon: '🛡️', line: 'front', atk: 10, def: 15, hp: 32, spd: 1.0, load: 12, upkeep: 0.4,
                 cost: { food: 30, wood: 14, iron: 10 }, time: 9, role: 'Utrzymanie linii i osłona innych oddziałów', weak: 'Wymagają wsparcia przeciw niektórym składom' },
    pikinier:  { name: 'Pikinierzy', short: 'Pik.', icon: '🔱', line: 'front', atk: 11, def: 12, hp: 28, spd: 1.0, load: 10, upkeep: 0.4,
                 cost: { food: 30, wood: 20, iron: 8 }, time: 9, role: 'Zatrzymywanie kawalerii i obrona podejść', weak: 'Przewaga zależy od przeciwnika i ustawienia' },
    lucznik:   { name: 'Łucznicy',   short: 'Łucz.', icon: '🏹', line: 'back',  atk: 15, def: 5,  hp: 18, spd: 1.0, load: 8,  upkeep: 0.4,
                 cost: { food: 28, wood: 26, iron: 4 }, time: 10, role: 'Ostrzał przeciwnika', weak: 'Są wrażliwi po utracie osłony' },
    kawaleria: { name: 'Kawaleria',  short: 'Kaw.', icon: '🐎', line: 'cav',   atk: 16, def: 9,  hp: 34, spd: 1.8, load: 18, upkeep: 0.8,
                 cost: { food: 55, wood: 14, iron: 20 }, time: 14, role: 'Szybkie działania i oskrzydlenie', weak: 'Jest zagrożona przez przygotowanych pikinierów' },
    taran:     { name: 'Tarany',     short: 'Tar.', icon: '🪵', line: 'siege', atk: 4,  def: 6,  hp: 70, spd: 0.6, load: 0,  upkeep: 0.6,
                 cost: { wood: 90, stone: 40, iron: 30 }, time: 28, siege: 10, role: 'Niszczenie umocnień', weak: 'Bezbronne w otwartym polu' },
    // jednostki fortowe [DOK 16]
    tarcznik:  { name: 'Tarcznicy', short: 'Tarcz.', icon: '🧱', line: 'front', atk: 8,  def: 24, hp: 42, spd: 0.7, load: 10, upkeep: 0.6, fort: 'zelazna',
                 cost: { food: 70, wood: 40, iron: 35 }, time: 16, role: 'Silni w przygotowanej obronie', weak: 'Powolni i podatni na oskrzydlenie' },
    kusznik:   { name: 'Kusznicy',  short: 'Kusz.', icon: '🎯', line: 'back',  atk: 21, def: 7,  hp: 20, spd: 0.8, load: 8,  upkeep: 0.6, fort: 'zelazna', pierce: 0.35,
                 cost: { food: 60, wood: 50, iron: 30 }, time: 16, role: 'Przebijanie pancerzy w przygotowanej obronie', weak: 'Powolni, podatni na oskrzydlenie' },
    konny_lucznik: { name: 'Konni łucznicy', short: 'K.łucz.', icon: '🏇', line: 'back', atk: 13, def: 6, hp: 26, spd: 2.0, load: 14, upkeep: 0.9, fort: 'stepowa',
                 cost: { food: 90, wood: 50, iron: 20 }, time: 18, role: 'Mobilny ostrzał i działania na mapie', weak: 'Mniejsza przydatność w oblężeniach' },
    lekki_jezdziec: { name: 'Lekcy jeźdźcy', short: 'L.jeźdź.', icon: '🐴', line: 'cav', atk: 12, def: 7, hp: 28, spd: 2.4, load: 30, upkeep: 0.8, fort: 'stepowa',
                 cost: { food: 80, wood: 20, iron: 25 }, time: 14, role: 'Rajdy, transport łupów, pościg', weak: 'Mniejsza przydatność w oblężeniach' },
    saper:     { name: 'Saperzy',   short: 'Sap.', icon: '⛏️', line: 'front', atk: 9,  def: 11, hp: 30, spd: 0.9, load: 10, upkeep: 0.6, fort: 'cytadela', siege: 4,
                 cost: { food: 60, wood: 60, iron: 30 }, time: 16, role: 'Walka z umocnieniami', weak: 'Wymagają osłony innymi oddziałami' },
    balista:   { name: 'Obsługi balist', short: 'Bal.', icon: '🎇', line: 'back', atk: 27, def: 3, hp: 30, spd: 0.5, load: 0, upkeep: 0.9, fort: 'cytadela', siege: 3, beast: 1.8,
                 cost: { wood: 140, iron: 50, stone: 40 }, time: 24, role: 'Ostrzał umocnień i wielkich bestii', weak: 'Konieczność osłony innymi oddziałami' },
    // jednostki przeciwników
    bandyta:   { name: 'Bandyci', icon: '🗡️', line: 'front', atk: 9, def: 9, hp: 26, spd: 1, load: 0, npc: true },
    strzelec:  { name: 'Strzelcy zbójeccy', icon: '🏹', line: 'back', atk: 12, def: 4, hp: 16, spd: 1, load: 0, npc: true },
    wilk:      { name: 'Wilki', icon: '🐺', line: 'cav', atk: 12, def: 6, hp: 22, spd: 2, load: 0, npc: true, beastly: true },
    dzik:      { name: 'Dziki', icon: '🐗', line: 'front', atk: 12, def: 10, hp: 34, spd: 1.3, load: 0, npc: true, beastly: true },
    niedzwiedz:{ name: 'Niedźwiedzie', icon: '🐻', line: 'front', atk: 22, def: 14, hp: 90, spd: 1, load: 0, npc: true, beastly: true },
    straznik:  { name: 'Strażnicy dotknięci klątwą', icon: '💀', line: 'front', atk: 20, def: 18, hp: 50, spd: 1, load: 0, npc: true },
    wiwerna:   { name: 'Wiwerna', icon: '🐉', line: 'front', atk: 900, def: 60, hp: 9000, spd: 1, load: 0, npc: true, beastly: true, isBeast: true },
  },
  // mnożniki przewag (atakujący -> cel) [DOK 9]
  counters: {
    pikinier:  { kawaleria: 2.0, lekki_jezdziec: 2.0, konny_lucznik: 1.6, wilk: 1.6 },
    miecznik:  { pikinier: 1.35, bandyta: 1.2, saper: 1.2 },
    lucznik:   { pikinier: 1.3, tarcznik: 0.6, miecznik: 0.75, taran: 0.5 },
    kawaleria: { lucznik: 1.7, kusznik: 1.7, balista: 1.9, konny_lucznik: 1.3, strzelec: 1.7, tarcznik: 0.6, pikinier: 0.6 },
    lekki_jezdziec: { lucznik: 1.6, kusznik: 1.6, balista: 1.8, strzelec: 1.6, taran: 1.5 },
    kusznik:   { miecznik: 1.3, tarcznik: 1.4, kawaleria: 1.2 },
    konny_lucznik: { pikinier: 1.4, saper: 1.3 },
    balista:   { tarcznik: 1.3 },
  },
  terrains: {
    plains: { name: 'Równina', mod: { cav: { atk: 1.15 } } },
    forest: { name: 'Las', mod: { cav: { atk: 0.85 }, back: { def: 1.2 } } },
    hills:  { name: 'Wzgórza', mod: { defender: { def: 1.1 } } },
    pass:   { name: 'Przełęcz', mod: { front: { def: 1.15 }, cav: { atk: 0.9 } } },
    swamp:  { name: 'Bagno', mod: { cav: { atk: 0.8 }, front: { atk: 0.95 } } },
  },
  tactics: {
    rownowaga: { name: 'Zrównoważona', desc: 'Bez premii i kar.' },
    tarcze:    { name: 'Obrona tarczami', desc: '+20% obrony linii, -10% ataku.', front: { def: 1.2 }, all: { atk: 0.9 } },
    szarza:    { name: 'Szarża', desc: 'Kawaleria +35% w 1. rundzie, -10% obrony.', cavFirst: 1.35, all: { def: 0.9 } },
    ostrzal:   { name: 'Ostrzał', desc: 'Strzelcy +15%, zwarcie od 3. rundy.', back: { atk: 1.15 }, delayMelee: 1 },
    oskrzydlenie: { name: 'Oskrzydlenie', desc: 'Kawaleria częściej uderza w tyły, -10% obrony kawalerii.', flank: 0.25, cav: { def: 0.9 } },
  },
  battle: { rounds: 7, random: 0.08, woundedPvE: 0.7, woundedDefense: 0.85, woundedAttack: 0.6 },

  // ---------- wojsko - marsze ----------
  march: { baseCap: 600, capPerSiedziba: 250, secPerTile: 30, baseMarches: 1, gatherPerHour: 0.5 },

  // ---------- leczenie ----------
  heal: { timePerUnit: 4, costFactor: 0.25 },

  // ---------- sojusz [DOK 18, 21, 22] ----------
  alliance: {
    baseLimit: 40, perLevel: 12, // 40 -> 100
    roles: ['Przywódca', 'Zastępca', 'Oficer', 'Członek'],
    donateDaily: 20, coinsPerDonate: 10, coinCapDaily: 300,
    helpBase: 10, helpSec: 60, helpPct: 0.01,
    reinforceBase: 2000,
  },
  allianceResearch: {
    rozbudowa:   { name: 'Rozbudowa sojuszu', tab: 'Organizacja', per: 12, unit: ' miejsc', desc: 'Limit członków rośnie z 40 do 100' },
    posilki:     { name: 'Sprawne posiłki', tab: 'Organizacja', per: 5, unit: '%', desc: '25% większa prędkość marszu wsparcia' },
    garnizon:    { name: 'Organizacja garnizonu', tab: 'Organizacja', per: 5, unit: '%', desc: '25% większa pojemność przyjmowanych posiłków' },
    obrona_ter:  { name: 'Obrona terytorialna', tab: 'Obrona', per: 2, unit: '%', desc: '10% większa obrona własnych osad na aktywnym terenie' },
    umocniona:   { name: 'Umocniona siedziba', tab: 'Obrona', per: 3, unit: '%', desc: '15% większa wytrzymałość siedziby sojuszu' },
    pomoc:       { name: 'Wzajemna pomoc', tab: 'Wsparcie i gospodarka', per: 1, unit: ' pomocy', desc: '5 dodatkowych pomocy przy budowie lub badaniu' },
    zapasy:      { name: 'Bezpieczne zapasy', tab: 'Wsparcie i gospodarka', per: 2, unit: '%', desc: '10% większa chroniona pojemność magazynu' },
    karawany:    { name: 'Zaopatrzenie karawan', tab: 'Wsparcie i gospodarka', per: 3, unit: '%', desc: '15% większy udźwig transportów' },
    teren:       { name: 'Znajomość terenu', tab: 'Wsparcie i gospodarka', per: 2, unit: '%', desc: '10% szybsze zbieranie na terenie sojuszu' },
  },
  allianceShop: [
    { id: 'vip500',  name: 'Punkty VIP ×500',   price: 250,  weekly: 5, give: { vip: 500 } },
    { id: 'vip5000', name: 'Punkty VIP ×5000',  price: 2200, weekly: 1, give: { vip: 5000 } },
    { id: 'mat',     name: 'Materiały rzemieślnicze', price: 80, weekly: 10, give: { items: { sztaby: 5, skory: 5 } } },
    { id: 'sp',      name: 'Przyspieszenie 15 min', price: 60, weekly: 10, give: { speed: { sp_any: 15 } } },
    { id: 'res',     name: 'Pakiet surowców (5000 wybranego)', price: 50, weekly: 10, give: { resPick: 5000 } },
    { id: 'move',    name: 'Przeniesienie osady (do regionu sojuszu)', price: 1000, weekly: 1, give: { relocate: 1 } },
    { id: 'banner',  name: 'Sztandar sojuszowy (dekoracja)', price: 1500, weekly: 1, give: { cosmetic: 'banner_ally' } },
  ],

  // ---------- osobiste badania [DOK 23] ----------
  research: {
    // Wojsko
    st_miecznik: { tab: 'Wojsko', name: 'Stopnie mieczników', max: 5, time: 3600, growth: 2.6, tierOf: 'miecznik', desc: 'Odblokowuje stopnie II–VI (wymaga też poziomu budynku 6/11/16/21/26).' },
    st_pikinier: { tab: 'Wojsko', name: 'Stopnie pikinierów', max: 5, time: 3600, growth: 2.6, tierOf: 'pikinier', desc: 'Odblokowuje stopnie II–VI.' },
    st_lucznik:  { tab: 'Wojsko', name: 'Stopnie łuczników', max: 5, time: 3600, growth: 2.6, tierOf: 'lucznik', desc: 'Odblokowuje stopnie II–VI.' },
    st_kawaleria:{ tab: 'Wojsko', name: 'Stopnie kawalerii', max: 5, time: 4200, growth: 2.6, tierOf: 'kawaleria', desc: 'Odblokowuje stopnie II–VI.' },
    st_taran:    { tab: 'Wojsko', name: 'Machiny: stopnie taranów', max: 5, time: 4200, growth: 2.6, tierOf: 'taran', desc: 'Odblokowuje stopnie II–VI taranów.' },
    formacje:    { tab: 'Wojsko', name: 'Formacje', max: 10, time: 1800, growth: 1.7, eff: { def: 0.02 }, desc: '+2% obrony wszystkich jednostek za poziom.' },
    bron:        { tab: 'Wojsko', name: 'Uzbrojenie', max: 10, time: 1800, growth: 1.7, eff: { atk: 0.02 }, desc: '+2% ataku wszystkich jednostek za poziom.' },
    pancerze:    { tab: 'Wojsko', name: 'Pancerze', max: 10, time: 2000, growth: 1.7, eff: { hp: 0.02 }, desc: '+2% wytrzymałości jednostek za poziom.' },
    zwiad:       { tab: 'Wojsko', name: 'Zwiad', max: 5, time: 1500, growth: 1.8, eff: { scout: 1 }, desc: '+1 do zasięgu zwiadowców, dokładniejsze raporty zwiadu.' },
    machiny:     { tab: 'Wojsko', name: 'Machiny oblężnicze', max: 5, time: 3000, growth: 1.8, eff: { siege: 0.1 }, desc: '+10% obrażeń przeciw umocnieniom.' },
    leczenie:    { tab: 'Wojsko', name: 'Leczenie rannych', max: 5, time: 2400, growth: 1.8, eff: { heal: 0.12 }, desc: '+12% pojemności lazaretu i szybsze leczenie.' },
    marsze:      { tab: 'Wojsko', name: 'Sztuka marszu', max: 3, time: 7200, growth: 3.0, eff: { marches: 1 }, desc: '+1 jednoczesny marsz.' },
    dowodzenie:  { tab: 'Wojsko', name: 'Dowodzenie', max: 10, time: 2400, growth: 1.7, eff: { cap: 0.06 }, desc: '+6% pojemności marszu.' },
    // Surowce
    pr_food:     { tab: 'Surowce', name: 'Uprawa pól', max: 10, time: 1200, growth: 1.65, eff: { prod_food: 0.05 }, desc: '+5% produkcji jedzenia.' },
    pr_wood:     { tab: 'Surowce', name: 'Wyręb', max: 10, time: 1200, growth: 1.65, eff: { prod_wood: 0.05 }, desc: '+5% produkcji drewna.' },
    pr_stone:    { tab: 'Surowce', name: 'Kamieniarstwo', max: 10, time: 1400, growth: 1.65, eff: { prod_stone: 0.05 }, desc: '+5% produkcji kamienia.' },
    pr_iron:     { tab: 'Surowce', name: 'Górnictwo', max: 10, time: 1600, growth: 1.65, eff: { prod_iron: 0.05 }, desc: '+5% produkcji żelaza.' },
    zbieranie:   { tab: 'Surowce', name: 'Zbieranie', max: 10, time: 1500, growth: 1.7, eff: { gather: 0.06 }, desc: '+6% szybkości zbierania na mapie.' },
    udzwig:      { tab: 'Surowce', name: 'Udźwig', max: 10, time: 1500, growth: 1.7, eff: { load: 0.06 }, desc: '+6% udźwigu wojska.' },
    skladowanie: { tab: 'Surowce', name: 'Przechowywanie', max: 10, time: 1500, growth: 1.7, eff: { storage: 0.06 }, desc: '+6% pojemności magazynu.' },
    ochrona:     { tab: 'Surowce', name: 'Ochrona zapasów', max: 5, time: 2400, growth: 1.8, eff: { protect: 0.04 }, desc: '+4 pkt. proc. chronionej części magazynu.' },
    // Ekonomia i administracja
    budowa:      { tab: 'Ekonomia i administracja', name: 'Organizacja budowy', max: 10, time: 1800, growth: 1.7, eff: { build: 0.03 }, desc: '+3% szybkości budowy.' },
    kolejka:     { tab: 'Ekonomia i administracja', name: 'Druga kolejka budowy', max: 1, time: 14400, growth: 1, eff: { queues: 1 }, desc: 'Odblokowuje drugą równoległą kolejkę budowy.' },
    nauka:       { tab: 'Ekonomia i administracja', name: 'Szkolnictwo', max: 10, time: 1800, growth: 1.7, eff: { research: 0.03 }, desc: '+3% szybkości badań.' },
    szkolenie:   { tab: 'Ekonomia i administracja', name: 'Musztra', max: 10, time: 1800, growth: 1.7, eff: { train: 0.04 }, desc: '+4% szybkości rekrutacji.' },
    handel:      { tab: 'Ekonomia i administracja', name: 'Handel', max: 5, time: 1500, growth: 1.8, eff: { trade: 0.04 }, desc: 'Lepszy kurs wymiany na rynku.' },
    pracownicy:  { tab: 'Ekonomia i administracja', name: 'Osadnictwo', max: 5, time: 1800, growth: 1.8, eff: { pop: 0.06 }, desc: '+6% limitu mieszkańców.' },
    utrzymanie:  { tab: 'Ekonomia i administracja', name: 'Zaopatrzenie wojska', max: 5, time: 2000, growth: 1.8, eff: { upkeep: 0.05 }, desc: '-5% kosztu utrzymania armii.' },
  },
  researchPrereq: {
    st_miecznik: 'akademia:1', st_pikinier: 'akademia:1', st_lucznik: 'akademia:1', st_kawaleria: 'akademia:3', st_taran: 'akademia:5',
    kolejka: 'akademia:6', marsze: 'akademia:8',
  },

  // ---------- towarzysze [DOK 8] ----------
  heroMaxLevel: 60, heroXpBase: 120, heroXpGrowth: 1.13,
  heroPromotions: [10, 20, 30, 40, 50],
  heroes: {
    wit:     { name: 'Wit', role: 'Zwiadowca', icon: '🧭', base: { scout: 1, spd: 0.05 },
      specs: [{ id: 'trop', name: 'Tropiciel', eff: { spd: 0.10, scout: 1 } }, { id: 'zasadzka', name: 'Mistrz zasadzek', eff: { atk_cav: 0.12 } }],
      stone: 'k_skupienie', trial: 'Odkryj nowe obszary mapy', origin: 'Uratowany z rąk bandytów (samouczek)' },
    jara:    { name: 'Jara', role: 'Łowczyni', icon: '🏹', base: { atk_back: 0.06 },
      specs: [{ id: 'lowy', name: 'Łowy na bestie', eff: { beast: 0.15 } }, { id: 'oko', name: 'Sokole oko', eff: { atk_back: 0.12 } }],
      stone: 'k_skupienie', trial: 'Pokonaj zwierzęta zagrażające gospodarstwom', origin: 'Łańcuch zleceń: "Bestia przy polach"' },
    borys:   { name: 'Borys', role: 'Dowódca', icon: '⚔️', base: { def_front: 0.06, atk: 0.02 },
      specs: [{ id: 'tarcze', name: 'Obrona tarczami', eff: { def_front: 0.12 } }, { id: 'przelam', name: 'Przełamywanie linii', eff: { atk_front: 0.12 } }],
      stone: 'k_hart', trial: 'Wygraj bitwy jako dowódca', origin: 'Uwolniony z niewoli (łańcuch ratunkowy)' },
    miroslaw:{ name: 'Mirosław', role: 'Inżynier', icon: '📐', base: { siege: 0.10, build: 0.03 },
      specs: [{ id: 'oblezenia', name: 'Oblężnik', eff: { siege: 0.2 } }, { id: 'budowniczy', name: 'Budowniczy', eff: { build: 0.06, walls: 0.1 } }],
      stone: 'k_duch', trial: 'Odbuduj przeprawy na mapie', origin: 'Przekonany do odbudowy mostu' },
    dobrawa: { name: 'Dobrawa', role: 'Zielarka', icon: '🌿', base: { heal: 0.10, hp: 0.02 },
      specs: [{ id: 'lazaret', name: 'Opatrywanie ran', eff: { wounded: 0.08 } }, { id: 'hart', name: 'Hartowanie ducha', eff: { hp: 0.06 } }],
      stone: 'k_duch', trial: 'Pomóż niezależnym osadom', origin: 'Pomoc niezależnej osadzie' },
    sambor:  { name: 'Sambor', role: 'Rycerz zakonny', icon: '🛡️', base: { atk_cav: 0.06, def: 0.02 },
      specs: [{ id: 'kopia', name: 'Kruszyciel kopii', eff: { atk_cav: 0.12 } }, { id: 'straz', name: 'Straż zakonu', eff: { def: 0.06 } }],
      stone: 'k_hart', trial: 'Weź udział w Wyprawie Zakonu', origin: 'Wydarzenie: Wyprawa Zakonu' },
  },

  // ---------- wyposażenie [DOK 7, 8, 28] ----------
  rulerSlots: { bron: 'Broń', helm: 'Hełm', pancerz: 'Pancerz', rekawice: 'Rękawice', buty: 'Buty', insygnium: 'Insygnium' },
  heroSlots: { bron: 'Broń', zbroja: 'Zbroja', talizman: 'Talizman' },
  gearTiers: ['Prosty', 'Kowalski', 'Wyborny', 'Mistrzowski', 'Książęcy', 'Legendarny'],
  gearTierForge: [1, 6, 11, 16, 21, 26],
  gearStats: {   // premia na stopień (I..VI): wartość * (tier+1)
    bron: { war: { atk: 0.02 }, eco: { prod: 0.01 } },
    helm: { war: { def: 0.02 }, eco: { build: 0.01 } },
    pancerz: { war: { hp: 0.02 }, eco: { storage: 0.015 } },
    rekawice: { war: { atk_front: 0.02, atk_back: 0.02 }, eco: { gather: 0.02 } },
    buty: { war: { spd: 0.02 }, eco: { load: 0.02 } },
    insygnium: { war: { def: 0.01, atk: 0.01 }, eco: { research: 0.015 } },
    zbroja: { war: { hp: 0.02, def: 0.01 } },
    talizman: { war: { atk: 0.015, heroXp: 0.05 } },
  },
  gearRecipe: (tier) => ({ iron: Math.round(800 * Math.pow(3.1, tier)), silver: Math.round(200 * Math.pow(2.6, tier)), items: { sztaby: 2 + tier * 3, skory: 2 + tier * 2, ...(tier >= 2 ? { plany: tier } : {}), ...(tier >= 4 ? { skladniki: tier - 2 } : {}) } }),
  gearRefineMax: 5,

  // ---------- przeciwnicy na mapie [DOK 13, 33] ----------
  monsters: {
    bandyci:   { name: 'Bandyci i dezerterzy', icon: '🗡️', units: { bandyta: 0.7, strzelec: 0.3 }, res: ['wood', 'iron'], silver: true, sp: 'sp_build', items: { sztaby: 1 }, terrain: 'plains' },
    zwierzeta: { name: 'Wilki, dziki i niedźwiedzie', icon: '🐺', units: { wilk: 0.5, dzik: 0.4, niedzwiedz: 0.1 }, res: ['food'], sp: 'sp_heal', items: { skory: 2 }, terrain: 'forest' },
    garnizon:  { name: 'Zbuntowany garnizon', icon: '🏴', units: { bandyta: 0.5, strzelec: 0.3, wilk: 0.2 }, res: ['iron', 'stone'], sp: 'sp_train', items: { plany: 1, sztaby: 1 }, terrain: 'hills' },
    ruiny:     { name: 'Ruiny dawnego królestwa', icon: '🏛️', units: { straznik: 0.4, bandyta: 0.6 }, res: ['stone'], sp: 'sp_research', items: { relikty: 1 }, stones: true, terrain: 'hills' },
    klatwa:    { name: 'Strażnicy dotknięci klątwą', icon: '💀', units: { straznik: 1 }, res: ['iron'], sp: 'sp_any', items: { skladniki: 1 }, strong: true, terrain: 'swamp' },
  },
  monsterBase: { count: 30, growth: 1.26, maxLevel: 25, tierEvery: 5 },
  monsterReward: {   // tabela zwykłego przeciwnika za 10 energii [DOK 33]; ilości skalowane poziomem
    base: 2000, xp: 100, bonusChance: 0.20, bonusPacks: 5, bonusPack: 5000, spChance: 0.10, spCount: 2, spMin: 5,
    rubies: [[0, 0.70], [5, 0.15], [10, 0.08], [20, 0.04], [30, 0.02], [50, 0.01]],
    // silniejszy przeciwnik/wyprawa za 20: x2 podstawy i bonusów, rubiny 60%
    strongRubies: [[0, 0.40], [5, 0.30], [10, 0.16], [20, 0.08], [30, 0.04], [50, 0.02]],
    levelScale: 1.22, refLevel: 5,
  },

  // ---------- chwała wojenna [DOK 31] ----------
  glory: {
    perUnit: 2, decay: 0.0005, winDef: 0.7, loseAtt: 0.3, winAtt: 0.65, loseDef: 0.35,
    repeatFactor: 0.5, weakRatio: 0.5,
    titles: [[100000, 'Wojownik Pogranicza'], [300000, 'Weteran Bitew'], [1000000, 'Zdobywca'], [3000000, 'Postrach Królestwa'], [10000000, 'Legendarny Wódz'], [30000000, 'Nieśmiertelna Legenda']],
  },

  // ---------- VIP [DOK 25] ----------
  vip: {
    daily: 500,
    levels: [500, 1500, 3000, 5000, 10000, 20000, 35000, 60000, 100000, 150000, 230000, 350000, 500000, 700000, 1000000],
    rewards: ['Oznaczenie VIP z możliwością ukrycia', 'Ramka portretu', 'Symbole herbu', 'Ozdobny sztandar osady', 'Strój władcy', 'Dekoracje rynku', 'Poza postaci w profilu', 'Wygląd obozu wyprawowego', 'Proporce maszerującej armii', 'Bogatszy zestaw stroju', 'Ozdobna brama', 'Sala tronowa jako sceneria profilu', 'Dekoracyjny zestaw wież i murów', 'Prezentacja zwycięstwa', 'Pełny motyw osady i reprezentacyjny strój'],
    shop: [{ pts: 500, price: 75 }, { pts: 5000, price: 650 }],
  },

  // ---------- arena [DOK 35] ----------
  arena: {
    unlockSiedziba: 10, free: 5, paidWeekly: 3, paidDaily: 1, paidPrice: 60, unitLimit: 1000,
    pts: [10, 15, 20], winTokens: 5, sameOpponentDaily: 1,
    leagues: ['Brązowa', 'Srebrna', 'Złota', 'Diamentowa', 'Mistrzowska'],
    groupSize: 100, minActiveForPromo: 50, activeFights: 20, promo: 0.1,
    participation: { fights: 20, tokens: 150, rubies: 80 },
    placeRewards: [[1, 1, 120, 100, 'Skórka mistrza na 7 dni i trwały puchar'], [2, 2, 100, 90, 'Srebrna ramka na 7 dni i puchar'], [3, 3, 80, 80, 'Brązowa ramka na 7 dni i puchar'],
      [4, 10, 60, 70, 'Sztandar turniejowy na 7 dni'], [11, 25, 40, 60, 'Wpis wyniku w kronice'], [26, 50, 30, 50, 'Wpis wyniku w kronice'], [51, 100, 20, 40, 'Wpis wyniku w kronice']],
    shop: [
      { id: 'a_sp', name: '5 przyspieszeń po 1 minucie', price: 50, dev: true, give: { speed: { sp_any: 5 } } },
      { id: 'a_res', name: '5 paczek wybranego zasobu po 1000', price: 50, dev: true, give: { resPick: 5000 } },
      { id: 'a_banner', name: 'Stały wzór sztandaru', price: 400, give: { cosmetic: 'banner_arena' } },
      { id: 'a_market', name: 'Stała dekoracja rynku', price: 600, give: { cosmetic: 'market_deco' } },
      { id: 'a_city', name: 'Stały podstawowy wygląd miasta', price: 1200, give: { cosmetic: 'skin_turniej' } },
    ],
    devWeekly: 2,
  },

  // ---------- wydarzenia [DOK 24, 34] ----------
  events: {
    rubiesWeekly: 80, thresholds: [40, 80], // w punktach udziału: dwa progi po 40 rubinów
    // harmonogram tygodnia (dzień tygodnia UTC: 1=pon ... 0=niedz)
    schedule: { 1: 'obrona', 2: 'obrona', 3: 'obrona', 4: 'zakon', 5: 'zakon', 6: 'weekend', 0: 'weekend' },
    obronaWaves: [8, 12, 16, 20],        // godziny fal (UTC)
  },

  // ---------- sklep (tryb testowy, bez prawdziwych płatności) [DOK 26, 36] ----------
  shop: {
    rubyPacks: [{ r: 100, label: 'Garść rubinów' }, { r: 550, label: 'Sakiewka rubinów' }, { r: 1200, label: 'Szkatułka rubinów' }, { r: 2600, label: 'Skrzynia rubinów' }, { r: 6500, label: 'Skarbiec rubinów' }],
    pass: { days: 30, dailyRubies: 40, label: 'Przepustka Pogranicza (30 dni)' },
    cosmetics: [
      { id: 'skin_jesien', name: 'Wygląd osady: Jesienne Pogranicze', price: 800 },
      { id: 'skin_zima', name: 'Wygląd osady: Zimowa Straż', price: 800 },
      { id: 'banner_czerw', name: 'Sztandar: Szkarłatny', price: 300 },
      { id: 'banner_ziel', name: 'Sztandar: Leśny', price: 300 },
      { id: 'cape_gold', name: 'Płaszcz władcy: Złocony', price: 500 },
      { id: 'frame_oak', name: 'Ramka portretu: Dębowa', price: 200 },
    ],
  },

  // ---------- obrona / PvP ----------
  raids: { minGapH: 10, maxGapH: 22, warnMin: 20, lootPct: 0.25, wallDamage: 0.15 },
  protectBase: 0.2,

  // ---------- forty i zamek [DOK 16, 17] ----------
  forts: {
    zelazna:  { name: 'Żelazna Przełęcz', units: ['tarcznik', 'kusznik'], terrain: 'pass' },
    stepowa:  { name: 'Strażnica Stepowa', units: ['konny_lucznik', 'lekki_jezdziec'], terrain: 'plains' },
    cytadela: { name: 'Cytadela Inżynierów', units: ['saper', 'balista'], terrain: 'hills' },
  },
  fortRules: { shareLimit: 0.25, dailyRecruit: 300, windowEveryDays: 3, windowHourUTC: 19, windowLenH: 2 },
  crown: { everyDays: 14, durationDays: 2, kingDays: 7, kingBonus: { gather: 0.05 } },

  // ---------- mapa ----------
  map: { w: 48, h: 48, regionSize: 16, startX: 8, startY: 39, revealStart: 4 },
};
