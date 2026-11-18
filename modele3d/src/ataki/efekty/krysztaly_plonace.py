"""EFEKT ATAKU: płonące kryształowe kolce (Przebudzony Kamienny Rycerz).

Te same kolce co efekt 'krysztaly', ale z rozżarzonymi czerwonymi końcami i płomieniami
buchającymi spomiędzy nich. Trafieni wrogowie zostają podpaleni (status 'podpalenie').
"""
from ataki.efekty.krysztaly import model_kolcow

PALETA = {
    'crystal': ('#7fd6ef', 0.12, 0.0, 1.2),
    'spike_red': ('#d80000', 0.3, 0.0, 1.4),
    'stone': ('#5a4a42', 0.92),
    'stone_dark': ('#3a2e2a', 0.95),
    'rune_fire': ('#ff5a1a', 0.4, 0.0, 4.0),
    'fire': ('#ff5200', 0.4, 0.0, 2.2),
    'fire_core': ('#ffae00', 0.3, 0.0, 3.0),
}

EFEKT = {
    'id': 'krysztaly_plonace',
    'nazwa': 'Płonące kryształowe kolce',
    'typ': 'obszar',
    'paleta': PALETA,
    'model': lambda sl: model_kolcow(sl, koniec='spike_red', ogien=True, runa='rune_fire'),
    'w_dloni': None,
    'uwagi': '3 kępy w linii co 0.8 m, kolejno co 0.08 s; trafieni wrogowie płoną (status w atak.status)',
}
