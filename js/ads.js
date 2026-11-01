// Ads abstraction layer.
// The game only calls Ads.rewarded() and Ads.midgame(). Plug any provider in here:
//  - CrazyGames SDK v3 (https://docs.crazygames.com/)  -> detected automatically
//  - Poki SDK, GameDistribution, AdMob (via Capacitor) -> add a branch below
// Without any SDK the game runs in "dev" mode and simulates a 3 s ad so you can test the flow.
const Ads = (() => {
  const cg = () => window.CrazyGames && window.CrazyGames.SDK && window.CrazyGames.SDK.ad;
  let lastMidgame = 0;

  async function init() {
    try {
      if (window.CrazyGames && window.CrazyGames.SDK && window.CrazyGames.SDK.init) {
        await window.CrazyGames.SDK.init();
      }
    } catch (e) { console.warn('Ad SDK init failed', e); }
  }

  function simulate() {
    return new Promise((resolve) => {
      let n = 3;
      showModal(`<div class="ad-sim">${t('adWatching')}<div class="count">${n}</div><div class="muted">(dev mode)</div></div>`, []);
      const timer = setInterval(() => {
        n--;
        const c = document.querySelector('.ad-sim .count');
        if (c) c.textContent = n;
        if (n <= 0) { clearInterval(timer); hideModal(); resolve(true); }
      }, 1000);
    });
  }

  // Resolves true if the player watched the whole ad and should get the reward.
  function rewarded() {
    const ad = cg();
    if (ad) {
      return new Promise((resolve) => {
        ad.requestAd('rewarded', {
          adStarted: () => Game.pause(true),
          adFinished: () => { Game.pause(false); resolve(true); },
          adError: () => { Game.pause(false); toast(t('adUnavailable')); resolve(false); },
        });
      });
    }
    return simulate();
  }

  // Interstitial – call at natural breaks (e.g. after a prestige). Rate limited to 1 per 3 min.
  function midgame() {
    const ad = cg();
    if (!ad || Date.now() - lastMidgame < 180000) return Promise.resolve();
    lastMidgame = Date.now();
    return new Promise((resolve) => {
      ad.requestAd('midgame', {
        adStarted: () => Game.pause(true),
        adFinished: () => { Game.pause(false); resolve(); },
        adError: () => { Game.pause(false); resolve(); },
      });
    });
  }

  return { init, rewarded, midgame };
})();
