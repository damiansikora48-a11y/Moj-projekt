/* Start gry, pętla czasu, zapis automatyczny */
(function () {
  const C = P.cfg, U = P.u, UI = P.ui;
  let last = Date.now(), acc = 0, saveAcc = 0, chatAcc = 0;

  function loop() {
    const s = P.S; if (!s) return;
    const now = Date.now(); const dt = Math.min(5000, now - last); last = now;
    P.advance(s, dt * s.speed);
    s.lastReal = now;
    // liczniki
    document.querySelectorAll('[data-end]').forEach((el) => { el.textContent = U.dur(+el.dataset.end - s.time); });
    document.querySelectorAll('[data-pend]').forEach((el) => { const a = +el.dataset.start, b = +el.dataset.pend; el.style.width = U.clamp((s.time - a) / (b - a) * 100, 0, 100) + '%'; });
    acc += dt; saveAcc += dt; chatAcc += dt;
    if (acc >= 1000) { acc = 0; UI.refresh(); }
    if (saveAcc >= 5000) { saveAcc = 0; P.save(s); }
    if (chatAcc >= 18000) { chatAcc = 0; P.chat.tick(s); }
  }

  function start(offline) {
    UI.go('city');
    setInterval(loop, 250);
    document.addEventListener('visibilitychange', () => { if (document.hidden) P.save(P.S); else last = Date.now(); });
    window.addEventListener('beforeunload', () => P.save(P.S));
    window.addEventListener('resize', () => { if (UI.page === 'map' && P.mapView.resize) P.mapView.resize(); });
    if (offline) {
      const g = offline.gained;
      UI.modal(() => `<h2>Witaj z powrotem!</h2><p>Minęło <b>${U.dur(offline.dt)}</b> czasu gry.</p><p>Osada wyprodukowała: ${P.rewardStr(g) || 'nic (magazyny pełne?)'}</p>${offline.reports ? `<p>Nowe raporty: <b>${offline.reports}</b> (napady, marsze, zlecenia).</p>` : ''}<button class="btn" data-a="close">Dalej</button>${offline.reports ? ' <button class="btn ghost" data-a="go" data-p="reports">Raporty</button>' : ''}`);
    }
  }

  function intro() {
    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modalBody').innerHTML = `<div class="intro"><h1>Pogranicza</h1><h3>Droga do Korony</h3><p>Dawne królestwo rozpadło się. Drogi są niebezpieczne, część osad opuszczono, a dawne twierdze zajęli bandyci, niezależne oddziały lub zakony. W ruinach tli się dawna magia.</p><p>Prowadzisz grupę ocalałych. Na skalnym tarasie, pod niedostępną ścianą i nad wąwozem rzeki, odnajdujecie ruinę strażnicy, studnię i kilka zniszczonych domów. Tu powstanie Twoja siedziba.</p><p><label>Imię władcy: <input id="introName" value="Władca" maxlength="24"></label></p><button class="btn gold" id="introGo">Rozpocznij</button><p class="muted">Prototyp do testów: gra jednoosobowa, inni gracze są symulowani. Tempo czasu zmienisz w prawym górnym rogu (×1 / ×10 / ×60 / ×360).</p></div>`;
    document.getElementById('introGo').onclick = () => {
      const name = document.getElementById('introName').value.trim() || 'Władca';
      P.S = P.newState(name);
      P.save(P.S);
      document.getElementById('modal').classList.add('hidden');
      last = Date.now();
      start(null);
      UI.toast('Zacznij od zadania u góry ekranu: oczyść plac i napraw studnię.', 'gold');
    };
  }

  window.addEventListener('DOMContentLoaded', () => {
    const s = P.load();
    if (!s) return intro();
    P.S = s;
    let off = null;
    try { off = P.catchUp(s); } catch (e) { console.error(e); }
    last = Date.now();
    start(off);
  });
})();
