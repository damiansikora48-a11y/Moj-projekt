/* Widok osady (SVG): taras pod skałą, wąwóz z rzeką na wschodzie, mury na zachodzie i południu [DOK 3, 37] */
(function () {
  const C = P.cfg, U = P.u;
  const W = 1000, H = 800;

  const PAL = {
    base:  { ground: '#b9a77c', ground2: '#a8966b', grass: '#7f8f4e', road: '#c9b48a', rock: '#8b8a84', rock2: '#6f6e69' },
    skin_jesien: { ground: '#b98f5a', ground2: '#a87d4b', grass: '#a5713a', road: '#d1a86f', rock: '#8a7f74', rock2: '#6e655c' },
    skin_zima: { ground: '#e6e9ee', ground2: '#d5dbe3', grass: '#c9d3dd', road: '#f3f4f6', rock: '#9aa1ab', rock2: '#7c838d' },
    skin_turniej: { ground: '#c2b089', ground2: '#ae9c72', grass: '#6f8f4e', road: '#d8c59a', rock: '#8f8a80', rock2: '#726d64' },
  };
  const M = { wood: '#8a5a32', wood2: '#6e4526', woodL: '#a8743f', stone: '#b3ab9c', stone2: '#958d7e', stoneD: '#7e766a', gont: '#6b4a2b', gontL: '#7d5833', slate: '#44506a', slate2: '#36405a', banner: '#2c4a8a', gold: '#c9a34a', win: '#2a2118', lit: '#ffd27a' };

  // pozycje działek (środek dolnej krawędzi)
  const PLOTS = {
    siedziba:  { x: 470, y: 230, label: 'Siedziba władcy' },
    akademia:  { x: 690, y: 215, label: 'Akademia' },
    sala:      { x: 250, y: 215, label: 'Sala towarzyszy' },
    magazyn:   { x: 165, y: 330, label: 'Magazyn i spichlerz' },
    karczma:   { x: 330, y: 345, label: 'Karczma' },
    rynek:     { x: 470, y: 395, label: 'Rynek' },
    kuznia:    { x: 620, y: 340, label: 'Kuźnia' },
    warsztat:  { x: 760, y: 345, label: 'Warsztat oblężniczy' },
    koszary:   { x: 150, y: 475, label: 'Koszary mieczników' },
    pikinierzy:{ x: 330, y: 490, label: 'Plac pikinierów' },
    lucznicy:  { x: 150, y: 600, label: 'Strzelnica łuczników' },
    poselstwo: { x: 615, y: 455, label: 'Poselstwo' },
    domy:      { x: 770, y: 480, label: 'Domy' },
    stajnia:   { x: 600, y: 600, label: 'Stajnia' },
    lazaret:   { x: 790, y: 600, label: 'Lazaret' },
    arena:     { x: 340, y: 615, label: 'Arena' },
    kopalnia:  { x: 95, y: 118, label: 'Kopalnia żelaza' },
    kamieniolom:{ x: 820, y: 112, label: 'Kamieniołom' },
    gospodarstwa:{ x: 210, y: 745, label: 'Gospodarstwa' },
    tartak:    { x: 720, y: 750, label: 'Tartak' },
    mury:      { x: 40, y: 400, label: 'Mury', hit: [20, 140, 60, 520] },
    brama:     { x: 470, y: 672, label: 'Brama' },
    wieze:     { x: 58, y: 660, label: 'Wieże' },
  };
  P.city = { PLOTS };

  // ---------- prymitywy ----------
  const box = (x, y, w, h, wall, roof, roofH, opt = {}) => {
    // bryła z fasadą i dachem dwuspadowym (lekko izometryczna: bok przesunięty)
    const d = opt.depth || Math.round(w * 0.28);
    const side = `<polygon points="${x + w},${y} ${x + w + d * 0.6},${y - d * 0.45} ${x + w + d * 0.6},${y - h - d * 0.45} ${x + w},${y - h}" fill="${shade(wall, -18)}"/>`;
    const front = `<rect x="${x}" y="${y - h}" width="${w}" height="${h}" fill="${wall}"/>`;
    const rh = roofH || Math.round(h * 0.7);
    const roofF = `<polygon points="${x - 4},${y - h} ${x + w / 2},${y - h - rh} ${x + w + 4},${y - h}" fill="${roof}"/>`;
    const roofS = `<polygon points="${x + w / 2},${y - h - rh} ${x + w / 2 + d * 0.6},${y - h - rh - d * 0.45} ${x + w + 4 + d * 0.6},${y - h - d * 0.45} ${x + w + 4},${y - h}" fill="${shade(roof, -14)}"/>`;
    return side + front + roofS + roofF;
  };
  const shade = (hex, amt) => { const n = parseInt(hex.slice(1), 16); let r = (n >> 16) + amt, g = ((n >> 8) & 255) + amt, b = (n & 255) + amt; r = U.clamp(r, 0, 255); g = U.clamp(g, 0, 255); b = U.clamp(b, 0, 255); return '#' + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0'); };
  const door = (x, y, w = 10, h = 16, arch) => arch ? `<path d="M${x},${y} v-${h - w / 2} a${w / 2},${w / 2} 0 0 1 ${w},0 v${h - w / 2} z" fill="${M.win}"/>` : `<rect x="${x}" y="${y - h}" width="${w}" height="${h}" fill="${M.win}"/>`;
  const win = (x, y, w = 6, h = 8) => `<rect class="win" x="${x}" y="${y}" width="${w}" height="${h}" fill="${M.win}"/>`;
  const flag = (x, y, h = 26, col = M.banner) => `<line x1="${x}" y1="${y}" x2="${x}" y2="${y - h}" stroke="#3a2a1a" stroke-width="1.6"/><path class="flag" d="M${x},${y - h} l14,4 l-14,5 z" fill="${col}"/>`;
  const banner = (x, y, w = 8, h = 14, col = M.banner) => `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${col}"/><path d="M${x},${y + h} l${w / 2},-4 l${w / 2},4 z" fill="${shade(col, -20)}"/><circle cx="${x + w / 2}" cy="${y + h / 2 - 1}" r="1.8" fill="${M.gold}"/>`;
  const tower = (x, y, w, h, wall, roof, opt = {}) => {
    let s = `<rect x="${x}" y="${y - h}" width="${w}" height="${h}" fill="${wall}"/><rect x="${x + w}" y="${y - h - 4}" width="${w * 0.25}" height="${h}" fill="${shade(wall, -18)}"/>`;
    if (opt.crenel) for (let i = 0; i < 4; i++) s += `<rect x="${x + i * w / 4}" y="${y - h - 5}" width="${w / 8}" height="5" fill="${wall}"/>`;
    if (roof) s += `<polygon points="${x - 3},${y - h} ${x + w / 2 + 2},${y - h - w * 0.9} ${x + w * 1.25 + 3},${y - h - 3}" fill="${roof}"/>`;
    s += win(x + w / 2 - 3, y - h + 8, 5, 8);
    return s;
  };
  const person = (x, y, col = '#3b3b5a') => `<g class="npc"><circle cx="${x}" cy="${y - 9}" r="2.4" fill="#e0b48c"/><rect x="${x - 2.2}" y="${y - 7}" width="4.4" height="7" rx="1.5" fill="${col}"/></g>`;
  const horse = (x, y, col = '#7a4a26') => `<g><ellipse cx="${x}" cy="${y - 6}" rx="8" ry="4" fill="${col}"/><rect x="${x + 5}" y="${y - 13}" width="3.5" height="8" fill="${col}" transform="rotate(20 ${x + 6} ${y - 9})"/><line x1="${x - 5}" y1="${y - 3}" x2="${x - 5}" y2="${y + 1}" stroke="${col}" stroke-width="1.6"/><line x1="${x + 4}" y1="${y - 3}" x2="${x + 4}" y2="${y + 1}" stroke="${col}" stroke-width="1.6"/></g>`;
  const fence = (x1, y1, x2, y2, col = M.woodL) => { let s = `<line x1="${x1}" y1="${y1 - 5}" x2="${x2}" y2="${y2 - 5}" stroke="${col}" stroke-width="1.6"/><line x1="${x1}" y1="${y1 - 2}" x2="${x2}" y2="${y2 - 2}" stroke="${col}" stroke-width="1.2"/>`; const n = Math.max(2, Math.round(Math.hypot(x2 - x1, y2 - y1) / 12)); for (let i = 0; i <= n; i++) { const x = x1 + (x2 - x1) * i / n, y = y1 + (y2 - y1) * i / n; s += `<line x1="${x}" y1="${y}" x2="${x}" y2="${y - 8}" stroke="${col}" stroke-width="1.6"/>`; } return s; };
  const target = (x, y, r = 6) => `<circle cx="${x}" cy="${y}" r="${r}" fill="#f1e3c0" stroke="#7a5a3a"/><circle cx="${x}" cy="${y}" r="${r * 0.6}" fill="none" stroke="#b33" stroke-width="1.4"/><circle cx="${x}" cy="${y}" r="${r * 0.2}" fill="#b33"/>`;
  const dummy = (x, y) => `<line x1="${x}" y1="${y}" x2="${x}" y2="${y - 16}" stroke="#7a5a3a" stroke-width="2"/><ellipse cx="${x}" cy="${y - 10}" rx="4" ry="5" fill="#d9c27a"/><circle cx="${x}" cy="${y - 17}" r="3" fill="#d9c27a"/>`;
  const pikeRack = (x, y, n = 5) => { let s = `<rect x="${x - 2}" y="${y - 4}" width="${n * 5 + 4}" height="3" fill="${M.wood2}"/>`; for (let i = 0; i < n; i++) s += `<line x1="${x + i * 5}" y1="${y}" x2="${x + i * 5}" y2="${y - 34}" stroke="#5a4630" stroke-width="1.3"/><path d="M${x + i * 5 - 1.5},${y - 34} l1.5,-5 l1.5,5 z" fill="#9aa"/>`; return s; };
  const scaffold = (x, y, w, h) => { let s = `<g class="scaffold" opacity=".9">`; for (let i = 0; i <= 4; i++) s += `<line x1="${x + i * w / 4}" y1="${y}" x2="${x + i * w / 4}" y2="${y - h}" stroke="#c49a5a" stroke-width="2"/>`; for (let j = 1; j <= 3; j++) s += `<line x1="${x - 4}" y1="${y - j * h / 3}" x2="${x + w + 4}" y2="${y - j * h / 3}" stroke="#c49a5a" stroke-width="2"/>`; s += `<line x1="${x}" y1="${y}" x2="${x + w}" y2="${y - h}" stroke="#b08a50" stroke-width="1.2"/>` + person(x + w * 0.3, y - h / 3, '#8a5a2a') + person(x + w * 0.75, y - 2 * h / 3, '#8a5a2a') + '</g>'; return s; };
  const ruin = (x, y, w = 50) => `<g opacity=".95"><polygon points="${x},${y} ${x},${y - 18} ${x + 8},${y - 24} ${x + 14},${y - 12} ${x + 22},${y - 16} ${x + 22},${y}" fill="${M.stone2}"/><rect x="${x + 26}" y="${y - 8}" width="${w - 26}" height="8" fill="${M.stoneD}"/><circle cx="${x + w - 6}" cy="${y - 3}" r="3" fill="${M.stoneD}"/><line x1="${x + 30}" y1="${y - 8}" x2="${x + 40}" y2="${y - 18}" stroke="${M.wood2}" stroke-width="2"/></g>`;
  const emptyPlot = (x, y, w = 70) => `<ellipse cx="${x}" cy="${y - 6}" rx="${w / 2}" ry="12" fill="none" stroke="rgba(60,40,20,.35)" stroke-dasharray="4 4"/>`;
  const wallCol = (st) => st <= 1 ? M.wood : st === 2 ? M.stone2 : M.stone;
  const roofCol = (st) => st <= 1 ? M.gont : M.slate;

  // ---------- budynki główne (6 etapów) ----------
  const DRAW = {
    siedziba(L, x, y) {
      const st = U.stageOf(L); let s = '';
      if (L <= 0) return ruin(x - 30, y, 70) + `<text x="${x}" y="${y + 16}" class="lbl" text-anchor="middle">ruina strażnicy</text>`;
      const tw = st >= 2 ? M.stone : M.stone2;
      if (st === 0) { // strażnica (stary fragment) + drewniana sala
        s += `<polygon points="${x - 60},${y} ${x - 60},${y - 40} ${x - 52},${y - 46} ${x - 44},${y - 38} ${x - 36},${y - 44} ${x - 36},${y}" fill="${M.stone2}"/>`;
        s += box(x - 30, y, 64, 32, M.wood, L >= 3 ? M.gontL : M.gont, 22) + door(x - 3, y, 10, 16) + win(x - 22, y - 22) + win(x + 18, y - 22);
        if (L >= 3) s += `<rect x="${x - 8}" y="${y - 20}" width="24" height="3" fill="${M.wood2}"/>`;
        s += `<rect x="${x - 50}" y="${y - 6}" width="12" height="5" fill="${M.woodL}"/>` + `<rect x="${x + 40}" y="${y - 8}" width="8" height="8" fill="${M.wood2}"/>`;
        if (L >= 5) s += flag(x - 48, y - 46, 18);
      } else if (st === 1) { // pełny drewniany dwór, wieża z drewnianą nadbudową
        s += tower(x - 66, y, 26, 52, M.stone2, null) + `<rect x="${x - 70}" y="${y - 66}" width="34" height="14" fill="${M.wood}"/><polygon points="${x - 72},${y - 66} ${x - 53},${y - 84} ${x - 34},${y - 66}" fill="${M.gont}"/>` + flag(x - 53, y - 84, 22);
        s += `<rect x="${x - 36}" y="${y - 10}" width="96" height="10" fill="${M.stone2}"/>` + box(x - 36, y - 10, 96, 34, M.wood, M.gont, 30) + door(x + 5, y - 10, 12, 18) + `<rect x="${x + 1}" y="${y - 30}" width="20" height="3" fill="${M.wood2}"/><line x1="${x + 3}" y1="${y - 27}" x2="${x + 3}" y2="${y - 10}" stroke="${M.wood2}" stroke-width="2"/><line x1="${x + 19}" y1="${y - 27}" x2="${x + 19}" y2="${y - 10}" stroke="${M.wood2}" stroke-width="2"/>`;
        s += win(x - 26, y - 34) + win(x + 34, y - 34) + win(x + 48, y - 34);
        if (L >= 8) s += `<rect x="${x - 29}" y="${y - 35}" width="3" height="10" fill="${M.wood2}"/><rect x="${x - 18}" y="${y - 35}" width="3" height="10" fill="${M.wood2}"/>`;
        if (L >= 10) s += `<rect x="${x - 40}" y="${y}" width="104" height="6" fill="${M.stone2}"/>`;
      } else if (st === 2) { // pierwsza murowana siedziba grodowa
        s += tower(x - 70, y, 30, 70, M.stone, M.slate, { crenel: false });
        s += box(x - 38, y, 104, 30, M.stone, M.slate, 0) + `<rect x="${x - 38}" y="${y - 54}" width="104" height="24" fill="${M.wood}"/><polygon points="${x - 42},${y - 54} ${x + 14},${y - 92} ${x + 70},${y - 54}" fill="${M.slate}"/><polygon points="${x + 14},${y - 92} ${x + 36},${y - 104} ${x + 98},${y - 64} ${x + 70},${y - 54}" fill="${M.slate2}"/>`;
        s += door(x + 7, y, 14, 22, true) + `<rect x="${x}" y="${y - 34}" width="28" height="4" fill="${M.stoneD}"/>` + win(x - 28, y - 48) + win(x + 44, y - 48) + win(x - 28, y - 22) + win(x + 50, y - 22);
        s += `<rect x="${x - 50}" y="${y}" width="130" height="8" fill="${M.stone2}"/>` + `<rect x="${x + 12}" y="${y}" width="18" height="16" fill="${M.stone2}"/>`;
        if (L >= 13) s += `<rect x="${x + 50}" y="${y - 104}" width="7" height="18" fill="${M.stoneD}"/>`;
        if (L >= 15) s += banner(x + 10, y - 50, 8, 12);
        s += person(x - 44, y + 4, '#33415a') + person(x + 74, y + 4, '#33415a');
      } else if (st === 3) { // dwa skrzydła, dziedziniec, wieżyczka schodowa
        s += tower(x - 84, y - 8, 30, 74, M.stone, M.slate);
        s += box(x - 50, y - 8, 30, 46, M.stone, M.slate, 20) + box(x + 70, y - 8, 30, 46, M.stone, M.slate, 20);
        s += box(x - 22, y - 28, 92, 52, M.stone, M.slate, 40) + win(x - 10, y - 66) + win(x + 18, y - 66) + win(x + 46, y - 66);
        s += `<rect x="${x - 6}" y="${y - 46}" width="58" height="4" fill="${M.wood2}"/>` + `<rect x="${x - 54}" y="${y - 8}" width="160" height="8" fill="${M.stone2}"/>`;
        s += box(x + 8, y + 6, 32, 20, M.stone, M.slate, 14) + door(x + 17, y + 6, 14, 16, true);
        s += tower(x + 58, y - 28, 12, 62, M.stone2, M.slate);
        s += banner(x - 46, y - 40) + banner(x + 86, y - 40);
        if (L >= 18) s += `<circle cx="${x - 36}" cy="${y - 14}" r="2.5" fill="${M.lit}"/><circle cx="${x + 82}" cy="${y - 14}" r="2.5" fill="${M.lit}"/>`;
        if (L >= 20) s += `<rect x="${x - 10}" y="${y + 6}" width="70" height="10" fill="${M.stoneD}" opacity=".5"/>`;
      } else { // 4 i 5: zamek z czterema narożnymi wieżami
        const lux = st === 5;
        s += tower(x - 92, y - 30, 28, 76, M.stone, M.slate) + tower(x + 92, y - 30, 28, 76, M.stone, M.slate);
        s += box(x - 64, y - 30, 156, 60, M.stone, M.slate, 46) + win(x - 40, y - 76, 7, 10) + win(x + 10, y - 76, 7, 10) + win(x + 26, y - 76, 7, 10) + win(x + 42, y - 76, 7, 10) + win(x + 70, y - 76, 7, 10);
        s += `<rect x="${x + 2}" y="${y - 58}" width="54" height="5" fill="${M.stoneD}"/>`;
        s += tower(x - 96, y + 14, 26, 56, M.stone, M.slate) + tower(x + 100, y + 14, 26, 56, M.stone, M.slate);
        s += `<rect x="${x - 70}" y="${y - 2}" width="170" height="16" fill="${M.stone}"/>`;
        for (let i = 0; i < 12; i++) s += `<rect x="${x - 70 + i * 14.5}" y="${y - 8}" width="7" height="6" fill="${M.stone}"/>`;
        s += box(x + 6, y + 14, 46, 26, M.stone, M.slate, 16) + door(x + 18, y + 14, 20, 22, true);
        s += banner(x - 30, y - 50) + banner(x + 74, y - 50) + banner(x - 4, y - 2) + banner(x + 58, y - 2);
        if (L >= 23) s += `<rect x="${x + 4}" y="${y - 53}" width="50" height="3" fill="${M.stoneD}"/>`;
        if (lux) { s += `<circle cx="${x + 29}" cy="${y - 64}" r="4" fill="${M.gold}"/>` + flag(x - 78, y - 106, 18) + flag(x + 106, y - 106, 18); for (const tx of [x - 78, x + 106, x - 83, x + 113]) s += `<circle cx="${tx}" cy="${y - 140}" r="0"/>`; }
        if (L >= 28) s += `<path d="M${x + 22},${y - 62} l7,-8 l7,8 z" fill="${M.gold}"/>`;
        s += person(x + 2, y + 18, '#2c4a8a') + person(x + 56, y + 18, '#2c4a8a');
      }
      return s;
    },
    stajnia(L, x, y) {
      const st = U.stageOf(L); if (L <= 0) return emptyPlot(x, y, 110);
      let s = ''; const n = st <= 0 ? 2 : st === 1 ? 4 : 4 + st;
      // wybieg po prawej
      s += `<ellipse cx="${x + 50}" cy="${y - 8}" rx="${50 + st * 4}" ry="18" fill="rgba(120,90,50,.35)"/>`;
      s += fence(x + 4, y + 8, x + 104 + st * 6, y + 8) + fence(x + 104 + st * 6, y + 8, x + 104 + st * 6, y - 22);
      if (st === 0) {
        s += `<rect x="${x - 70}" y="${y - 26}" width="72" height="26" fill="none"/>` + `<polygon points="${x - 74},${y - 26} ${x + 6},${y - 26} ${x - 2},${y - 40} ${x - 66},${y - 40}" fill="${M.gont}"/>`;
        for (const px of [x - 70, x - 34, x + 2]) s += `<line x1="${px}" y1="${y}" x2="${px}" y2="${y - 26}" stroke="${M.wood2}" stroke-width="3"/>`;
        s += `<rect x="${x - 70}" y="${y - 24}" width="72" height="4" fill="${M.wood}"/>` + `<rect x="${x - 60}" y="${y - 8}" width="14" height="6" fill="#c9b04a"/>` + `<rect x="${x + 8}" y="${y - 4}" width="16" height="4" fill="${M.wood2}"/>`;
        if (L >= 3) s += `<rect x="${x - 82}" y="${y - 14}" width="10" height="14" fill="${M.woodL}"/>`;
      } else {
        const w = 90 + st * 8; const wall = st >= 2 ? M.stone : M.wood;
        s += box(x - w + 10, y, w, 24, wall, roofCol(st), 16, { depth: 20 });
        for (let i = 0; i < Math.min(6, 2 + st); i++) s += door(x - w + 18 + i * (w - 14) / Math.min(6, 2 + st), y, 9, 14, st >= 2);
        if (st >= 1) s += `<rect x="${x - w / 2 - 4}" y="${y - 38}" width="12" height="8" fill="#c9b04a"/>`;
        if (st >= 3) s += box(x - w - 6, y + 16, 26, 22, wall, roofCol(st), 14); // skrzydło L
        if (st >= 3) s += `<ellipse cx="${x + 60}" cy="${y - 8}" rx="22" ry="8" fill="none" stroke="${M.woodL}" stroke-width="1.5"/>`;
        if (st >= 4) s += `<rect x="${x - w / 2 - 6}" y="${y - 56}" width="12" height="10" fill="${M.slate2}"/>`;
        if (st >= 2) s += `<path d="M${x - 12},${y - 30} a5,5 0 1 1 10,0" stroke="${M.gold}" fill="none" stroke-width="2"/>`;
        if (st >= 5) s += banner(x + 6, y - 30, 7, 12);
      }
      for (let i = 0; i < Math.min(n, 6); i++) s += horse(x + 26 + i * 14 + (i % 2) * 4, y - (i % 2) * 8, ['#7a4a26', '#5a3a1e', '#a0703e', '#ddd'][i % 4]);
      s += person(x + 16, y + 2, '#5a4630');
      return s;
    },
    lucznicy(L, x, y) {
      const st = U.stageOf(L); if (L <= 0) return emptyPlot(x, y, 120);
      let s = ''; const lanes = st <= 0 ? 2 : st === 1 ? 3 : st <= 3 ? 4 : 5;
      // tory od frontu, cele z tyłu, wał ziemny za celami
      s += `<polygon points="${x - 10},${y} ${x + 150},${y} ${x + 160},${y - 36} ${x + 0},${y - 36}" fill="rgba(140,120,70,.35)"/>`;
      for (let i = 0; i <= lanes; i++) s += `<line x1="${x - 4 + i * 160 / lanes}" y1="${y}" x2="${x + 6 + i * 160 / lanes}" y2="${y - 36}" stroke="rgba(255,255,255,.35)" stroke-width="1"/>`;
      s += `<path d="M${x + 135},${y - 40} q20,-14 36,0 v6 h-36 z" fill="#6f8040"/>`;
      for (let i = 0; i < lanes; i++) s += target(x + 140 + (i - lanes / 2) * 7, y - 30 - i * 2, 5);
      const wall = wallCol(st), roof = roofCol(st);
      if (st === 0) { s += `<polygon points="${x - 48},${y - 22} ${x - 6},${y - 22} ${x - 10},${y - 34} ${x - 44},${y - 34}" fill="${M.gont}"/><line x1="${x - 46}" y1="${y}" x2="${x - 46}" y2="${y - 22}" stroke="${M.wood2}" stroke-width="3"/><line x1="${x - 8}" y1="${y}" x2="${x - 8}" y2="${y - 22}" stroke="${M.wood2}" stroke-width="3"/>` + banner(x - 34, y - 20); }
      else { s += box(x - 56, y, 46, 30 + st * 3, wall, roof, 20) + door(x - 38, y, 9, 14) + banner(x - 52, y - 26); if (st >= 2) s += `<rect x="${x - 8}" y="${y - 26}" width="${40 + st * 8}" height="4" fill="${roof}"/>` + `<line x1="${x}" y1="${y}" x2="${x}" y2="${y - 22}" stroke="${M.wood2}" stroke-width="2"/><line x1="${x + 30 + st * 8}" y1="${y}" x2="${x + 30 + st * 8}" y2="${y - 22}" stroke="${M.wood2}" stroke-width="2"/>`; if (st >= 3) s += `<rect x="${x + 100}" y="${y - 20}" width="14" height="20" fill="${M.wood}"/><rect x="${x + 98}" y="${y - 22}" width="18" height="3" fill="${M.wood2}"/>` + person(x + 107, y - 22, '#2c4a8a'); }
      s += fence(x - 12, y + 8, x + 156, y + 8);
      for (let i = 0; i < Math.min(lanes, 3); i++) s += person(x + 16 + i * 30, y - 2, '#4a5a3a');
      return s;
    },
    koszary(L, x, y) {
      const st = U.stageOf(L); if (L <= 0) return emptyPlot(x, y, 110);
      let s = ''; const wall = wallCol(st), roof = roofCol(st);
      s += `<ellipse cx="${x + 10}" cy="${y - 6}" rx="${56 + st * 3}" ry="16" fill="${st >= 2 ? 'rgba(150,140,125,.5)' : 'rgba(120,95,60,.35)'}"/>`;
      if (st >= 4) s += `<ellipse cx="${x + 10}" cy="${y - 6}" rx="30" ry="9" fill="none" stroke="rgba(255,255,255,.5)"/>`;
      s += box(x - 50, y - 18, 96 + (st >= 1 ? 16 : 0), 26 + st * 3, wall, roof, 16);
      if (st >= 2) s += box(x - 76, y + 4, 26, 30, wall, roof, 16);
      if (st >= 3) s += box(x + 72, y + 4, 26, 30, wall, roof, 16);
      if (st >= 4) s += `<rect x="${x - 6}" y="${y - 54 - st * 3}" width="34" height="10" fill="${M.wood}"/>`;
      s += door(x - 2, y - 18, 12, 16, st >= 2);
      for (let i = 0; i < 2 + Math.min(st, 3); i++) s += dummy(x - 30 + i * 18, y + 6);
      s += `<g>${[0, 1, 2].map((i) => `<circle cx="${x + 34 + i * 9}" cy="${y - 30 - st * 3}" r="4" fill="${i % 2 ? '#8a3a2a' : '#2c4a8a'}" stroke="#ddd" stroke-width=".8"/>`).join('')}</g>`;
      s += `<path d="M${x - 40},${y - 34} l10,10 M${x - 30},${y - 34} l-10,10" stroke="#ccc" stroke-width="2"/>` + banner(x + 50, y - 10);
      s += person(x + 26, y + 6, '#6a2f2f') + person(x + 36, y + 6, '#6a2f2f');
      return s;
    },
    pikinierzy(L, x, y) {
      const st = U.stageOf(L); if (L <= 0) return emptyPlot(x, y, 130);
      let s = ''; const wall = wallCol(st), roof = roofCol(st);
      s += `<rect x="${x - 70}" y="${y - 30}" width="150" height="40" rx="6" fill="${st >= 4 ? 'rgba(160,150,130,.5)' : 'rgba(150,120,80,.35)'}"/>`;
      for (let i = 0; i < 2 + Math.min(st, 3); i++) s += `<line x1="${x - 60}" y1="${y - 22 + i * 8}" x2="${x + 70}" y2="${y - 22 + i * 8}" stroke="rgba(255,255,255,.35)" stroke-dasharray="6 4"/>`;
      if (st === 0) s += `<polygon points="${x - 70},${y - 32} ${x + 20},${y - 32} ${x + 14},${y - 44} ${x - 64},${y - 44}" fill="${M.gont}"/>` + [x - 66, x - 22, x + 16].map((px) => `<line x1="${px}" y1="${y - 30}" x2="${px}" y2="${y - 32}" stroke="${M.wood2}" stroke-width="3"/>`).join('');
      else s += box(x - 70, y - 30, 120 + st * 6, 20 + st * 2, wall, roof, 12, { depth: 18 });
      s += pikeRack(x + 64 + st * 3, y - 28, 3 + Math.min(st, 4));
      if (st >= 2) s += `<g transform="translate(${x + 40},${y - 2})"><rect x="-10" y="-8" width="20" height="8" fill="${M.wood}"/><ellipse cx="0" cy="-12" rx="9" ry="6" fill="#d9c27a"/><circle cx="-7" cy="1" r="3" fill="${M.wood2}"/><circle cx="7" cy="1" r="3" fill="${M.wood2}"/></g>`;
      const men = st === 0 ? 3 : st <= 2 ? 4 : 8;
      for (let i = 0; i < men; i++) { const px = x - 50 + (i % 6) * 14, py = y - 4 + Math.floor(i / 6) * 10; s += person(px, py, '#3a4a6a') + `<line x1="${px + 3}" y1="${py - 6}" x2="${px + 3}" y2="${py - 28}" stroke="#5a4630" stroke-width="1"/>`; }
      s += banner(x - 74, y - 26);
      return s;
    },
    // ---------- pozostałe budynki (prostsza rozbudowa) ----------
    generic(id, L, x, y) {
      const st = U.stageOf(L); if (L <= 0) return emptyPlot(x, y, 70);
      const w = 44 + st * 6, h = 24 + st * 4;
      let s = box(x - w / 2, y, w, h, wallCol(st), roofCol(st), 16 + st * 2) + door(x - 5, y, 10, 14, st >= 2) + win(x - w / 2 + 6, y - h + 8) + win(x + w / 2 - 12, y - h + 8);
      const icon = { akademia: '📘', sala: '🎖️', magazyn: '📦', karczma: '🍺', kuznia: '⚒️', warsztat: '🪵', poselstwo: '🕊️', lazaret: '➕', arena: '🏟️' }[id];
      if (id === 'kuznia') s += `<rect x="${x + w / 2 - 14}" y="${y - h - 22}" width="7" height="14" fill="${M.stoneD}"/><circle class="smoke" cx="${x + w / 2 - 10}" cy="${y - h - 28}" r="4" fill="rgba(200,200,200,.6)"/>`;
      if (id === 'magazyn') s += box(x - w / 2 - 30, y + 6, 26, 18 + st * 2, wallCol(st), roofCol(st), 10) + `<rect x="${x + w / 2 + 6}" y="${y - 10}" width="10" height="10" fill="${M.wood}"/><rect x="${x + w / 2 + 18}" y="${y - 8}" width="8" height="8" fill="${M.woodL}"/>`;
      if (id === 'karczma') s += `<rect x="${x - w / 2 - 18}" y="${y - 22}" width="14" height="12" fill="#e8d6a8" stroke="${M.wood2}"/><line x1="${x - w / 2 - 11}" y1="${y - 10}" x2="${x - w / 2 - 11}" y2="${y}" stroke="${M.wood2}" stroke-width="2"/>`;
      if (id === 'warsztat') s += `<g transform="translate(${x + w / 2 + 16},${y})"><rect x="-14" y="-10" width="28" height="7" fill="${M.wood}"/><circle cx="-9" cy="-2" r="4" fill="${M.wood2}"/><circle cx="9" cy="-2" r="4" fill="${M.wood2}"/><rect x="-18" y="-15" width="36" height="4" fill="${M.wood2}"/></g>`;
      if (id === 'arena') s = `<ellipse cx="${x}" cy="${y - 10}" rx="${60 + st * 4}" ry="20" fill="${M.stone2}"/><ellipse cx="${x}" cy="${y - 12}" rx="${48 + st * 4}" ry="14" fill="#c9b48a"/>` + banner(x - 50, y - 36, 8, 14, '#8a2a2a') + banner(x + 42, y - 36) + person(x - 8, y - 8, '#8a2a2a') + person(x + 8, y - 8, '#2c4a8a');
      if (id === 'lazaret') s += `<rect x="${x - 5}" y="${y - h - 6}" width="10" height="3" fill="#b33"/><rect x="${x - 1.5}" y="${y - h - 9.5}" width="3" height="10" fill="#b33"/>`;
      if (st >= 3 && id !== 'arena') s += banner(x + w / 2 - 2, y - h + 2, 6, 10);
      return s + (icon ? `<text x="${x}" y="${y - h - 30 - st * 2}" text-anchor="middle" font-size="14" class="ico">${icon}</text>` : '');
    },
    domy(L, x, y) {
      if (L <= 0) return emptyPlot(x, y, 90) + ruin(x - 20, y, 40);
      const st = U.stageOf(L); const n = Math.min(9, 2 + Math.floor(L / 3)); let s = '';
      for (let i = 0; i < n; i++) { const px = x - 60 + (i % 3) * 44 + (Math.floor(i / 3) % 2) * 12, py = y - 34 + Math.floor(i / 3) * 24; s += box(px, py, 26, 16 + st, wallCol(st), roofCol(st), 12) + door(px + 9, py, 7, 10) + win(px + 3, py - 12, 4, 5); }
      s += person(x + 30, y + 6, '#5a3a5a') + person(x - 40, y + 4, '#3a5a5a');
      return s;
    },
    gospodarstwa(L, x, y) {
      if (L <= 0) return emptyPlot(x, y, 140);
      const n = Math.min(8, 2 + Math.floor(L / 4)); let s = '';
      for (let i = 0; i < n; i++) { const px = x - 150 + i * 40, py = y - (i % 2) * 6; s += `<polygon points="${px},${py} ${px + 36},${py} ${px + 42},${py - 22} ${px + 6},${py - 22}" fill="${i % 3 === 0 ? '#c9a840' : i % 3 === 1 ? '#8fa04a' : '#b5933a'}"/>`; for (let k = 1; k < 5; k++) s += `<line x1="${px + k * 8}" y1="${py}" x2="${px + 6 + k * 8}" y2="${py - 22}" stroke="rgba(80,60,20,.35)"/>`; }
      s += box(x + 180, y, 34, 22, M.wood, M.gont, 14) + person(x - 40, y + 4, '#6a5a2a') + person(x + 20, y + 2, '#6a5a2a');
      return s;
    },
    tartak(L, x, y) {
      if (L <= 0) return emptyPlot(x, y, 90);
      const st = U.stageOf(L); let s = '';
      for (let i = 0; i < 6 + st; i++) s += `<polygon points="${x + 60 + i * 14},${y - 4} ${x + 68 + i * 14},${y - 34 - (i % 3) * 6} ${x + 76 + i * 14},${y - 4}" fill="${i % 2 ? '#4f6b33' : '#5e7a3a'}"/>`;
      s += box(x - 40, y, 56 + st * 4, 22 + st * 2, wallCol(Math.min(st, 2)), roofCol(st), 14) + `<circle cx="${x + 22}" cy="${y - 10}" r="7" fill="none" stroke="#999" stroke-width="2"/>`;
      for (let i = 0; i < 3 + st; i++) s += `<rect x="${x - 50 + (i % 4) * 4}" y="${y - 6 - Math.floor(i / 4) * 5 - i * 1.2}" width="34" height="4" rx="2" fill="${M.woodL}"/>`;
      return s;
    },
    kamieniolom(L, x, y) { if (L <= 0) return ''; const st = U.stageOf(L); let s = `<polygon points="${x - 46},${y} ${x - 34},${y - 40} ${x + 30},${y - 44} ${x + 48},${y}" fill="${shade(M.stone, -6)}"/>`; for (let i = 0; i < 2 + st; i++) s += `<rect x="${x - 30 + i * 12}" y="${y - 12 - (i % 2) * 8}" width="10" height="8" fill="${M.stone}" stroke="${M.stoneD}" stroke-width=".6"/>`; return s + person(x + 10, y, '#5a5a5a'); },
    kopalnia(L, x, y) { if (L <= 0) return ''; const st = U.stageOf(L); return `<path d="M${x - 18},${y} v-18 a18,16 0 0 1 36,0 v18 z" fill="#2a241e"/><path d="M${x - 22},${y} v-20 a22,20 0 0 1 44,0 v20" fill="none" stroke="${st >= 2 ? M.stone : M.wood}" stroke-width="5"/><g transform="translate(${x + 30},${y})"><rect x="-10" y="-10" width="20" height="8" fill="${M.wood2}"/><circle cx="-6" cy="-1" r="3" fill="#333"/><circle cx="6" cy="-1" r="3" fill="#333"/><rect x="-8" y="-14" width="16" height="4" fill="#666"/></g>`; },
  };

  function walls(s, st0, wallsL, gateL, towersL, palette) {
    const st = U.stageOf(wallsL); const gst = U.stageOf(gateL);
    let g = '';
    const y = 672, x0 = 58, x1 = 868, gx = 470;
    const dmg = s.damagedWalls || 0;
    if (wallsL <= 0) {
      g += `<line x1="${x0}" y1="140" x2="${x0}" y2="${y}" stroke="rgba(80,60,40,.35)" stroke-width="3" stroke-dasharray="6 8"/><line x1="${x0}" y1="${y}" x2="${x1}" y2="${y}" stroke="rgba(80,60,40,.35)" stroke-width="3" stroke-dasharray="6 8"/>`;
    } else if (st <= 1) {
      // palisada
      for (let yy = 140; yy < y; yy += 9) g += `<rect x="${x0 - 4}" y="${yy}" width="${7 + st * 2}" height="10" fill="${M.wood}" stroke="${M.wood2}" stroke-width=".6"/>`;
      for (let xx = x0; xx < x1; xx += 9) if (Math.abs(xx - gx) > 34) g += `<polygon points="${xx},${y} ${xx},${y - 18 - st * 4} ${xx + 4},${y - 23 - st * 4} ${xx + 8},${y - 18 - st * 4} ${xx + 8},${y}" fill="${M.wood}" stroke="${M.wood2}" stroke-width=".6"/>`;
    } else {
      const hh = 16 + st * 5;
      g += `<rect x="${x0 - 8}" y="140" width="${10 + st * 2}" height="${y - 140}" fill="${M.stone2}"/>`;
      g += `<rect x="${x0}" y="${y - hh}" width="${gx - 34 - x0}" height="${hh}" fill="${M.stone}"/><rect x="${gx + 34}" y="${y - hh}" width="${x1 - gx - 34}" height="${hh}" fill="${M.stone}"/>`;
      for (let xx = x0; xx < x1; xx += 14) if (Math.abs(xx - gx) > 40) g += `<rect x="${xx}" y="${y - hh - 6}" width="7" height="6" fill="${M.stone}"/>`;
      for (let xx = x0 + 6; xx < x1; xx += 24) if (Math.abs(xx - gx) > 40) g += `<line x1="${xx}" y1="${y - hh + 4}" x2="${xx + 12}" y2="${y - hh + 4}" stroke="${M.stoneD}" stroke-width=".6"/>`;
    }
    if (dmg > 0 && wallsL > 0) g += `<g fill="${M.stoneD}">` + [180, 640, 760].map((xx) => `<polygon points="${xx},${y} ${xx + 10},${y - 22} ${xx + 22},${y - 8} ${xx + 30},${y}"/>`).join('') + `</g><text x="${x1 - 60}" y="${y + 18}" class="lbl warnTxt">uszkodzone</text>`;
    // brama
    if (gateL > 0) {
      const gw = gateL <= 5 ? M.wood : M.stone, gh = 34 + gst * 6;
      g += `<rect x="${gx - 34}" y="${y - gh}" width="20" height="${gh}" fill="${gw}"/><rect x="${gx + 14}" y="${y - gh}" width="20" height="${gh}" fill="${gw}"/><rect x="${gx - 34}" y="${y - gh - 8}" width="68" height="12" fill="${gw}"/>`;
      g += `<path d="M${gx - 14},${y} v-${gh - 18} a14,12 0 0 1 28,0 v${gh - 18}" fill="${gateL <= 5 ? M.wood2 : '#4a3a2a'}"/>`;
      if (gst >= 1) g += `<polygon points="${gx - 38},${y - gh - 8} ${gx - 24},${y - gh - 26} ${gx - 10},${y - gh - 8}" fill="${roofCol(gst)}"/><polygon points="${gx + 10},${y - gh - 8} ${gx + 24},${y - gh - 26} ${gx + 38},${y - gh - 8}" fill="${roofCol(gst)}"/>`;
      if (gst >= 3) g += banner(gx - 30, y - gh + 6) + banner(gx + 22, y - gh + 6);
      if (s.cosmetics.vip11) g += `<circle cx="${gx}" cy="${y - gh - 2}" r="4" fill="${M.gold}"/>`;
    } else g += `<rect x="${gx - 30}" y="${y - 4}" width="60" height="4" fill="rgba(80,60,40,.4)"/>`;
    // wieże na murach
    if (towersL > 0) {
      const ts = U.stageOf(towersL);
      const spots = [[x0 - 4, y], [x0 - 4, 300], [260, y], [680, y], [x1 - 6, y], [x0 - 4, 460]].slice(0, 2 + Math.min(4, Math.floor(towersL / 5)));
      for (const [tx, ty] of spots) g += tower(tx - 10, ty + 4, 22, 46 + ts * 6, ts >= 2 ? M.stone : M.wood, roofCol(ts), { crenel: ts >= 2 });
    }
    return g;
  }

  P.city.render = function (s, opts = {}) {
    const pal = PAL[s.skin] || PAL.base;
    const hour = U.hourUTC(s.time) + new Date(s.time).getUTCMinutes() / 60;
    const NM = 0.32; const night = hour < 5 || hour > 21 ? NM : hour < 7 ? NM * (7 - hour) / 2 : hour > 19 ? NM * (hour - 19) / 2 : 0;
    const busy = {}; for (const q of s.bq) busy[q.id] = q;
    let g = '';
    g += `<defs><linearGradient id="gRock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="${pal.rock2}"/><stop offset="1" stop-color="${pal.rock}"/></linearGradient><linearGradient id="gRiver" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3f6f8f"/><stop offset=".5" stop-color="#5f93b3"/><stop offset="1" stop-color="#3f6f8f"/></linearGradient><pattern id="pGrass" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="${pal.ground}"/><circle cx="4" cy="5" r="1" fill="${pal.ground2}"/><circle cx="13" cy="12" r="1.2" fill="${pal.ground2}"/></pattern></defs>`;
    g += `<rect width="${W}" height="${H}" fill="${pal.grass}"/>`;
    g += `<rect x="40" y="120" width="850" height="560" fill="url(#pGrass)"/>`;
    // rzeka w wąwozie (wschód)
    g += `<path d="M900,0 C880,120 930,220 905,330 C880,440 935,560 905,680 C890,740 910,780 905,800 L1000,800 L1000,0 Z" fill="#5d5a52"/><path d="M930,0 C912,120 958,220 935,330 C912,440 962,560 935,680 C922,740 940,780 935,800 L985,800 C990,700 1000,600 985,500 C970,400 1000,250 985,0 Z" fill="url(#gRiver)"/><path class="flow" d="M948,0 C930,150 975,260 952,380 C930,500 975,620 950,800" stroke="rgba(255,255,255,.35)" stroke-width="2" fill="none" stroke-dasharray="10 16"/>`;
    g += `<text x="960" y="420" class="lbl" transform="rotate(90 960 420)" fill="#e8f1f6">rzeka w głębokim wąwozie</text>`;
    // ściana skalna (północ)
    let rock = 'M0,0 L1000,0 L1000,90 '; for (let x = 1000; x >= 0; x -= 40) rock += `L${x},${105 + ((x / 40) % 2 ? 22 : 0) + Math.sin(x) * 6} `; rock += 'Z';
    g += `<path d="${rock}" fill="url(#gRock)"/><path d="M0,40 L1000,30" stroke="rgba(0,0,0,.08)" stroke-width="12"/><text x="500" y="40" class="lbl" text-anchor="middle" fill="#eeeae0">niedostępna ściana skalna</text>`;
    // taras siedziby
    g += `<path d="M300,250 L320,170 L650,170 L670,250 Z" fill="${pal.ground2}" opacity=".9"/><path d="M300,250 L670,250 L680,262 L290,262 Z" fill="${pal.rock}"/>`;
    for (let i = 0; i < 5; i++) g += `<rect x="${458}" y="${250 + i * 5}" width="28" height="4" fill="${pal.rock2}"/>`;
    // drogi
    g += `<path d="M470,800 L470,672 L470,420 M470,420 L470,262 M330,420 L610,420 M160,500 L470,520 L790,500 M470,560 L600,610" stroke="${pal.road}" stroke-width="16" fill="none" stroke-linecap="round" opacity=".85"/>`;
    g += `<text x="470" y="790" class="lbl" text-anchor="middle">szlak na mapę świata ↓</text>`;
    // rynek
    const rL = s.b.rynek;
    g += `<ellipse cx="470" cy="420" rx="${70 + U.stageOf(rL) * 6}" ry="26" fill="${rL >= 11 ? '#b3ab9c' : pal.road}"/>`;
    if (s.cosmetics.market_deco || s.cosmetics.vip6) g += `<circle cx="470" cy="418" r="10" fill="#8aa"/><circle cx="470" cy="418" r="5" fill="#5f93b3"/>`;
    // studnia
    g += s.quest.flags.plac ? `<g><ellipse cx="400" cy="440" rx="11" ry="5" fill="${M.stone2}"/><rect x="389" y="425" width="22" height="14" fill="${M.stone}"/><line x1="391" y1="425" x2="391" y2="410" stroke="${M.wood2}" stroke-width="2"/><line x1="409" y1="425" x2="409" y2="410" stroke="${M.wood2}" stroke-width="2"/><polygon points="386,410 400,401 414,410" fill="${M.gont}"/></g>` : `<g><ellipse cx="400" cy="440" rx="11" ry="5" fill="${M.stoneD}"/><rect x="389" y="430" width="22" height="9" fill="${M.stone2}"/></g>`;
    // ogniska
    g += `<g class="fire"><circle cx="540" cy="455" r="4" fill="#ff9a3a"/><circle cx="540" cy="451" r="2.5" fill="#ffd27a"/></g>`;
    if (rL > 0) for (let i = 0; i < Math.min(6, 2 + Math.floor(rL / 4)); i++) { const px = 410 + i * 24; g += `<rect x="${px}" y="400" width="18" height="10" fill="${M.wood}"/><polygon points="${px - 2},400 ${px + 9},392 ${px + 20},400" fill="${['#b33', '#2c4a8a', '#c9a34a', '#4a8a4a'][i % 4]}"/>`; }
    // mury, brama, wieże
    g += walls(s, 0, s.b.mury, s.b.brama, s.b.wieze, pal);
    // budynki (od tyłu do przodu)
    const order = Object.keys(PLOTS).filter((id) => !['mury', 'brama', 'wieze'].includes(id)).sort((a, b) => PLOTS[a].y - PLOTS[b].y);
    for (const id of order) {
      const p = PLOTS[id]; const L = s.b[id];
      const fn = DRAW[id] || ((LL, x, y) => DRAW.generic(id, LL, x, y));
      let body = fn(L, p.x, p.y);
      if (busy[id]) body += scaffold(p.x - 30, p.y, 60, 40);
      const locked = s.b.siedziba < C.buildings[id].unlock && L <= 0;
      g += `<g class="plot${locked ? ' locked' : ''}" data-b="${id}">${body}<rect class="hit" x="${p.x - 75}" y="${p.y - 75}" width="150" height="90" fill="transparent"/>`;
      if (opts.labels !== false) g += `<g class="tag" transform="translate(${p.x},${p.y + 14})"><rect x="-46" y="-9" width="92" height="15" rx="7" fill="rgba(20,16,10,.62)"/><text y="2" text-anchor="middle" class="tagTxt">${p.label.split(' ')[0]}${L > 0 ? ' ' + L : ''}${busy[id] ? ' ⚒' : ''}${locked ? ' 🔒' : ''}</text></g>`;
      g += `</g>`;
    }
    // klikane strefy murów/bramy/wież
    g += `<g class="plot" data-b="mury"><rect x="30" y="140" width="50" height="520" fill="transparent"/></g><g class="plot" data-b="brama"><rect x="430" y="612" width="80" height="64" fill="transparent"/></g><g class="plot" data-b="wieze"><rect x="30" y="600" width="70" height="80" fill="transparent"/></g>`;
    if (opts.labels !== false) for (const id of ['mury', 'brama', 'wieze']) { const p = PLOTS[id]; g += `<g class="tag" transform="translate(${p.x + (id === 'mury' ? 22 : 0)},${p.y + 20})"><rect x="-32" y="-9" width="64" height="15" rx="7" fill="rgba(20,16,10,.62)"/><text y="2" text-anchor="middle" class="tagTxt">${p.label} ${s.b[id] || ''}${busy[id] ? ' ⚒' : ''}</text></g>`; }
    // mieszkańcy w ruchu
    const npcN = Math.min(14, Math.max(2, Math.round(s.pop / 25)));
    const paths = ['M470,700 L470,430 L330,420', 'M160,500 L470,520 L790,500', 'M470,420 L610,420 L600,600', 'M330,420 L470,262', 'M200,740 L470,700 L700,745'];
    for (let i = 0; i < npcN; i++) { const pth = paths[i % paths.length]; g += `<g>${person(0, 0, ['#5a3a2a', '#3a4a6a', '#6a5a2a', '#4a2a4a'][i % 4])}<animateMotion dur="${18 + (i * 7) % 15}s" begin="-${i * 3}s" repeatCount="indefinite" path="${pth}" keyPoints="0;1;0" keyTimes="0;0.5;1" calcMode="linear"/></g>`; }
    // noc
    if (night > 0.02) g += `<rect width="${W}" height="${H}" fill="#0b1430" opacity="${night.toFixed(2)}" pointer-events="none"/>`;
    return `<svg viewBox="0 0 ${W} ${H}" class="citySvg${night > 0.2 ? ' night' : ''}" xmlns="http://www.w3.org/2000/svg">${g}</svg>`;
  };

  // podgląd jednego budynku (do panelu ulepszeń i plansz etapów)
  P.city.preview = function (id, L, s) {
    const fn = DRAW[id] || ((LL, x, y) => DRAW.generic(id, LL, x, y));
    const big = ['siedziba', 'stajnia', 'lucznicy', 'pikinierzy', 'koszary', 'gospodarstwa', 'domy', 'tartak'].includes(id);
    const vb = id === 'gospodarstwa' ? '-170 -70 420 100' : id === 'lucznicy' ? '-100 -90 290 120' : big ? '-140 -150 300 200' : '-90 -110 190 140';
    return `<svg viewBox="${vb}" class="prevSvg" xmlns="http://www.w3.org/2000/svg"><ellipse cx="0" cy="4" rx="${big ? 130 : 80}" ry="20" fill="#b9a77c"/>${fn(L, 0, 0)}</svg>`;
  };
})();
