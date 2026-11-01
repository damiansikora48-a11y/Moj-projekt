// ---- Game balance data -------------------------------------------------
// Tweak numbers here to change pacing. Cost of the next unit = baseCost * COST_GROWTH^owned.
const COST_GROWTH = 1.14;

const GENERATORS = [
  { id: 'bee',     icon: '🐝', baseCost: 12,     baseProd: 0.15,  name: { en: 'Worker Bee',     pl: 'Pszczoła robotnica' } },
  { id: 'flower',  icon: '🌼', baseCost: 120,    baseProd: 1.2,   name: { en: 'Flower Bed',     pl: 'Rabatka' } },
  { id: 'hive',    icon: '🪺', baseCost: 1300,   baseProd: 9,     name: { en: 'Wooden Hive',    pl: 'Drewniany ul' } },
  { id: 'meadow',  icon: '🌻', baseCost: 15e3,   baseProd: 60,    name: { en: 'Sunflower Meadow', pl: 'Łąka słoneczników' } },
  { id: 'apiary',  icon: '🏡', baseCost: 18e4,   baseProd: 400,   name: { en: 'Apiary',         pl: 'Pasieka' } },
  { id: 'orchard', icon: '🌳', baseCost: 2.2e6,  baseProd: 2600,  name: { en: 'Blossom Orchard', pl: 'Kwitnący sad' } },
  { id: 'lab',     icon: '🧪', baseCost: 2.8e7,  baseProd: 17e3,  name: { en: 'Pollen Lab',     pl: 'Laboratorium pyłku' } },
  { id: 'factory', icon: '🏭', baseCost: 3.6e8,  baseProd: 11e4,  name: { en: 'Honey Refinery', pl: 'Rafineria miodu' } },
  { id: 'island',  icon: '🏝️', baseCost: 4.8e9,  baseProd: 75e4,  name: { en: 'Floral Island',  pl: 'Kwiecista wyspa' } },
  { id: 'moon',    icon: '🌙', baseCost: 6.5e10, baseProd: 5e6,   name: { en: 'Moon Garden',    pl: 'Księżycowy ogród' } },
  { id: 'portal',  icon: '🌀', baseCost: 9e11,   baseProd: 34e6,  name: { en: 'Nectar Portal',  pl: 'Portal nektaru' } },
  { id: 'galaxy',  icon: '🌌', baseCost: 1.3e13, baseProd: 240e6, name: { en: 'Galactic Swarm', pl: 'Galaktyczny rój' } },
];

// Generator upgrades: each doubles that generator. Unlocked at owned threshold.
const GEN_TIERS = [
  { owned: 10,  costMul: 15 },
  { owned: 25,  costMul: 150 },
  { owned: 50,  costMul: 4000 },
  { owned: 100, costMul: 1.2e5 },
  { owned: 150, costMul: 6e6 },
  { owned: 200, costMul: 5e8 },
];

const UPGRADES = [];
GENERATORS.forEach((g) => {
  GEN_TIERS.forEach((tier, i) => {
    UPGRADES.push({
      id: `g_${g.id}_${i}`, kind: 'gen', gen: g.id, icon: g.icon, tier: i,
      cost: g.baseCost * tier.costMul,
      unlocked: (s) => (s.gens[g.id] || 0) >= tier.owned,
    });
  });
});
// Click upgrades
[100, 5e3, 5e5, 5e7, 5e9, 5e11, 5e13].forEach((cost, i) => {
  UPGRADES.push({ id: `c_${i}`, kind: 'click', icon: '👆', tier: i, cost, unlocked: (s) => s.runEarned >= cost * 0.3 });
});
// Global upgrades
[[5e4, 1.25], [5e6, 1.5], [5e8, 1.5], [5e10, 2], [5e12, 2], [5e14, 2], [5e16, 3]].forEach(([cost, mult], i) => {
  UPGRADES.push({ id: `x_${i}`, kind: 'global', icon: '👑', tier: i, cost, mult, unlocked: (s) => s.runEarned >= cost * 0.4 });
});
const UPGRADE_BY_ID = Object.fromEntries(UPGRADES.map((u) => [u.id, u]));

// Permanent perks bought with Royal Jelly (survive prestige)
const PERKS = [
  { id: 'golden',  icon: '🌟', costs: [3, 8, 20, 50, 120],  name: { en: 'Golden Pheromones', pl: 'Złote feromony' },  desc: { en: 'Golden bees appear 15% more often per level', pl: 'Złote pszczoły pojawiają się o 15% częściej na poziom' } },
  { id: 'offline', icon: '🌙', costs: [2, 6, 15, 40, 100],  name: { en: 'Night Shift',       pl: 'Nocna zmiana' },    desc: { en: '+4h offline time cap and +10% offline efficiency per level', pl: '+4 h limitu offline i +10% wydajności offline na poziom' } },
  { id: 'start',   icon: '🐣', costs: [2, 5, 12, 30, 80],   name: { en: 'Head Start',        pl: 'Dobry start' },     desc: { en: 'Start each swarm with 10 more Worker Bees per level', pl: 'Każdy rój zaczyna z +10 robotnicami na poziom' } },
  { id: 'click',   icon: '💪', costs: [1, 4, 10, 25, 60],   name: { en: 'Mighty Paws',       pl: 'Silne łapki' },     desc: { en: 'Clicks ×2 per level', pl: 'Kliknięcia ×2 na poziom' } },
  { id: 'cheap',   icon: '🏷️', costs: [5, 15, 40, 100, 250], name: { en: 'Royal Discount',    pl: 'Królewski rabat' }, desc: { en: 'Everything in the colony is 3% cheaper per level', pl: 'Wszystko w kolonii tańsze o 3% na poziom' } },
];

// Achievements – each gives +1% production
const ACHIEVEMENTS = [];
GENERATORS.forEach((g) => {
  [1, 50, 100, 200].forEach((n) => {
    ACHIEVEMENTS.push({ id: `a_${g.id}_${n}`, icon: g.icon, desc: () => t('achOwn', { n, g: L(g.name) }), check: (s) => (s.gens[g.id] || 0) >= n });
  });
});
[1e3, 1e6, 1e9, 1e12, 1e15, 1e18, 1e21, 1e24].forEach((x) => {
  ACHIEVEMENTS.push({ id: `a_earn_${x}`, icon: '🍯', desc: () => t('achEarn', { x: fmt(x) }), check: (s) => s.lifetimeEarned >= x });
});
[100, 1000, 10000, 50000].forEach((n) => {
  ACHIEVEMENTS.push({ id: `a_click_${n}`, icon: '👆', desc: () => t('achClicks', { n: fmt(n) }), check: (s) => s.clicks >= n });
});
[1, 10, 50, 200].forEach((n) => {
  ACHIEVEMENTS.push({ id: `a_gold_${n}`, icon: '🌟', desc: () => t('achGolden', { n }), check: (s) => s.goldenClicks >= n });
});
[1, 5, 20, 50].forEach((n) => {
  ACHIEVEMENTS.push({ id: `a_pres_${n}`, icon: '👑', desc: () => t('achPrestige', { n }), check: (s) => s.prestiges >= n });
});
