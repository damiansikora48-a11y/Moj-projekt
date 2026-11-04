/* Rysowanie dużej mapy świata (canvas) z mgłą, terytorium i marszami */
(function () {
  const C = P.cfg, U = P.u;
  const TC = { plains: '#9fb26a', forest: '#5f7f43', hills: '#a3926a', swamp: '#6f7f6a', river: '#4f86ad', bridge: '#8a6a44', pass: '#9a8a6a' };
  const ICON = { home: '🏰', castle: '👑', fort: '🛡️', bot: '🏘️', allyhq: '🚩', tower: '🗼', find: '❔', node: '', bridge: '🌉', strategic: '⚑', task: '❗' };
  const NODE = { food: '🌾', wood: '🪵', stone: '🪨', iron: '⛓️' };
  const V = P.mapView = { tile: 30, ox: 0, oy: 0, sel: null, drag: null, canvas: null };

  V.centerOn = function (x, y) {
    const c = V.canvas; if (!c) return;
    V.ox = x * V.tile - c.width / (2 * devicePixelRatio) + V.tile / 2; V.oy = y * V.tile - c.height / (2 * devicePixelRatio) + V.tile / 2;
  };
  V.attach = function (canvas, s) {
    V.canvas = canvas;
    const resize = () => { const r = canvas.parentElement.getBoundingClientRect(); canvas.width = r.width * devicePixelRatio; canvas.height = r.height * devicePixelRatio; canvas.style.width = r.width + 'px'; canvas.style.height = r.height + 'px'; V.draw(s); };
    V.resize = resize; resize();
    if (!V.centered) { const h = P.world.home(s); V.centerOn(h.x, h.y); V.centered = true; V.draw(s); }
    let moved = 0;
    const pos = (e) => { const r = canvas.getBoundingClientRect(); const p = e.touches ? e.touches[0] : e; return { x: p.clientX - r.left, y: p.clientY - r.top }; };
    const down = (e) => { const p = pos(e); V.drag = { x: p.x, y: p.y, ox: V.ox, oy: V.oy }; moved = 0; };
    const move = (e) => { if (!V.drag) return; const p = pos(e); const dx = p.x - V.drag.x, dy = p.y - V.drag.y; moved = Math.max(moved, Math.abs(dx) + Math.abs(dy)); V.ox = V.drag.ox - dx; V.oy = V.drag.oy - dy; V.draw(P.S); if (e.cancelable) e.preventDefault(); };
    const up = (e) => {
      if (V.drag && moved < 6) { const p = V.drag; const tx = Math.floor((p.x + V.ox) / V.tile), ty = Math.floor((p.y + V.oy) / V.tile); if (tx >= 0 && ty >= 0 && tx < C.map.w && ty < C.map.h) { V.sel = { x: tx, y: ty }; V.draw(P.S); P.ui.mapSelect(tx, ty); } }
      V.drag = null;
    };
    canvas.onmousedown = down; canvas.onmousemove = move; window.onmouseup = up;
    canvas.ontouchstart = down; canvas.ontouchmove = move; canvas.ontouchend = up;
    canvas.onwheel = (e) => { e.preventDefault(); const old = V.tile; V.tile = U.clamp(V.tile * (e.deltaY < 0 ? 1.12 : 0.89), 14, 60); const r = canvas.getBoundingClientRect(); const mx = e.clientX - r.left, my = e.clientY - r.top; V.ox = (V.ox + mx) * V.tile / old - mx; V.oy = (V.oy + my) * V.tile / old - my; V.draw(P.S); };
  };
  V.zoom = function (f) { const c = V.canvas; const cx = c.width / devicePixelRatio / 2, cy = c.height / devicePixelRatio / 2; const old = V.tile; V.tile = U.clamp(V.tile * f, 14, 60); V.ox = (V.ox + cx) * V.tile / old - cx; V.oy = (V.oy + cy) * V.tile / old - cy; V.draw(P.S); };

  V.clampView = function () {
    const c = V.canvas; const w = c.width / devicePixelRatio, h = c.height / devicePixelRatio; const T = V.tile;
    const mw = C.map.w * T, mh = C.map.h * T, pad = 60;
    V.ox = mw + 2 * pad < w ? (mw - w) / 2 : U.clamp(V.ox, -pad, mw - w + pad);
    V.oy = mh + 2 * pad < h ? (mh - h) / 2 : U.clamp(V.oy, -pad, mh - h + pad);
  };
  V.draw = function (s) {
    const c = V.canvas; if (!c || !c.isConnected) return;
    V.clampView();
    const ctx = c.getContext('2d'); const T = V.tile;
    ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
    const w = c.width / devicePixelRatio, h = c.height / devicePixelRatio;
    ctx.fillStyle = '#1d1a14'; ctx.fillRect(0, 0, w, h);
    const x0 = Math.max(0, Math.floor(V.ox / T)), y0 = Math.max(0, Math.floor(V.oy / T));
    const x1 = Math.min(C.map.w - 1, Math.ceil((V.ox + w) / T)), y1 = Math.min(C.map.h - 1, Math.ceil((V.oy + h) / T));
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
      const px = x * T - V.ox, py = y * T - V.oy;
      const rev = P.world.isRev(s, x, y);
      const t = s.map.terr[y * C.map.w + x];
      ctx.fillStyle = TC[t] || '#999'; ctx.fillRect(px, py, T + 0.5, T + 0.5);
      if (t === 'forest') { ctx.fillStyle = 'rgba(30,60,20,.35)'; ctx.beginPath(); ctx.moveTo(px + T * 0.3, py + T * 0.8); ctx.lineTo(px + T * 0.5, py + T * 0.25); ctx.lineTo(px + T * 0.7, py + T * 0.8); ctx.fill(); }
      if (t === 'hills') { ctx.fillStyle = 'rgba(90,70,40,.3)'; ctx.beginPath(); ctx.arc(px + T / 2, py + T * 0.85, T * 0.35, Math.PI, 0); ctx.fill(); }
      if (!rev) { ctx.fillStyle = 'rgba(20,18,14,.86)'; ctx.fillRect(px, py, T + 0.5, T + 0.5); }
    }
    // granice regionów
    ctx.strokeStyle = 'rgba(255,240,200,.18)'; ctx.lineWidth = 2;
    for (let k = 1; k < 3; k++) { const p = k * C.map.regionSize * T; ctx.beginPath(); ctx.moveTo(p - V.ox, -V.oy); ctx.lineTo(p - V.ox, C.map.h * T - V.oy); ctx.moveTo(-V.ox, p - V.oy); ctx.lineTo(C.map.w * T - V.ox, p - V.oy); ctx.stroke(); }
    // terytorium sojuszu
    if (s.alliance && s.alliance.hq) {
      const nodes = [{ x: s.alliance.hq.x, y: s.alliance.hq.y, r: 5, ok: true }].concat(s.alliance.towers.map((t) => ({ x: t.x, y: t.y, r: 4, ok: t.connected })));
      for (const n of nodes) { ctx.fillStyle = n.ok ? 'rgba(60,110,220,.14)' : 'rgba(220,60,60,.12)'; ctx.beginPath(); ctx.arc((n.x + 0.5) * T - V.ox, (n.y + 0.5) * T - V.oy, n.r * T, 0, Math.PI * 2); ctx.fill(); }
    }
    // obiekty
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    for (const o of s.map.objs) {
      if (o.x < x0 - 1 || o.x > x1 + 1 || o.y < y0 - 1 || o.y > y1 + 1) continue;
      const rev = P.world.isRev(s, o.x, o.y);
      const big = ['home', 'castle', 'fort'].includes(o.type);
      if (o.type === 'fog' || (!rev && !big)) continue;
      const px = (o.x + 0.5) * T - V.ox, py = (o.y + 0.5) * T - V.oy;
      let ic = ICON[o.type];
      if (o.type === 'monster') ic = o.beast ? '🐉' : (C.monsters[o.kind] || {}).icon || '⚔️';
      if (o.type === 'node') ic = NODE[o.res];
      if (o.type === 'find' && o.done) ic = '✔️';
      if (o.type === 'bridge') ic = o.broken ? '🚧' : '🌉';
      if (o.type === 'fort' || o.type === 'castle') { const own = o.owner; ctx.fillStyle = own === 'neutral' ? 'rgba(200,200,200,.5)' : (s.alliance && own === s.alliance.botAli) ? 'rgba(60,110,220,.6)' : 'rgba(200,60,60,.55)'; ctx.beginPath(); ctx.arc(px, py, T * 0.55, 0, Math.PI * 2); ctx.fill(); }
      if (o.type === 'bot' && s.alliance && o.ali === s.alliance.botAli) { ctx.fillStyle = 'rgba(60,110,220,.5)'; ctx.beginPath(); ctx.arc(px, py, T * 0.45, 0, Math.PI * 2); ctx.fill(); }
      if (o.type === 'home') { ctx.fillStyle = 'rgba(255,215,120,.6)'; ctx.beginPath(); ctx.arc(px, py, T * 0.6, 0, Math.PI * 2); ctx.fill(); }
      ctx.globalAlpha = rev ? 1 : 0.5;
      ctx.font = `${Math.round(T * (big ? 0.8 : 0.62))}px serif`; ctx.fillText(ic || '•', px, py + 1);
      ctx.globalAlpha = 1;
      if ((o.type === 'monster' || o.type === 'task') && T >= 22) { ctx.font = `bold ${Math.round(T * 0.32)}px sans-serif`; ctx.fillStyle = '#fff'; ctx.strokeStyle = '#000'; ctx.lineWidth = 3; ctx.strokeText(o.lvl, px + T * 0.32, py - T * 0.3); ctx.fillText(o.lvl, px + T * 0.32, py - T * 0.3); }
      if (o.busy) { ctx.strokeStyle = '#ffd27a'; ctx.lineWidth = 2; ctx.strokeRect(px - T / 2 + 2, py - T / 2 + 2, T - 4, T - 4); }
    }
    // marsze
    const home = P.world.home(s);
    for (const m of s.marches) {
      const hx = (home.x + 0.5) * T - V.ox, hy = (home.y + 0.5) * T - V.oy, tx = (m.tx + 0.5) * T - V.ox, ty = (m.ty + 0.5) * T - V.oy;
      let f = 0; if (m.state === 'out') f = U.clamp((s.time - m.start) / m.travel, 0, 1); else if (m.state === 'return') f = U.clamp(1 - (m.next - s.time) / m.travel, 0, 1); else f = 1;
      const fx = m.state === 'return' ? tx + (hx - tx) * f : hx + (tx - hx) * f, fy = m.state === 'return' ? ty + (hy - ty) * f : hy + (ty - hy) * f;
      ctx.setLineDash([5, 5]); ctx.strokeStyle = m.state === 'return' ? 'rgba(120,220,120,.8)' : 'rgba(255,220,120,.9)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(hx, hy); ctx.lineTo(tx, ty); ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle = '#2c4a8a'; ctx.beginPath(); ctx.arc(fx, fy, T * 0.22, 0, Math.PI * 2); ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = `${Math.round(T * 0.3)}px sans-serif`; ctx.fillText('⚑', fx, fy);
    }
    if (V.sel) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.strokeRect(V.sel.x * T - V.ox + 1, V.sel.y * T - V.oy + 1, T - 2, T - 2); }
  };
})();
