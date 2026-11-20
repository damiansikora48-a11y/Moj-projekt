"""PODGLĄD 3D: tworzy samodzielną stronę z osadzonymi modelami (do obejrzenia/udostępnienia).

Użycie:  python3 pack_viewer.py <plik_wyjściowy.html>
Bierze jednostki z export/units.json (czyli z roster.json) – nowe pojawiają się same.
"""
import base64
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT = os.path.join(ROOT, 'export')

meta = json.load(open(os.path.join(EXPORT, 'units.json'), encoding='utf-8'))
emb = {}
for jid, u in meta.items():
    raw = open(os.path.join(EXPORT, u['plik']), 'rb').read()
    emb[jid] = base64.b64encode(raw).decode()
    n = struct.unpack('<I', raw[12:16])[0]
    j = json.loads(raw[20:20 + n])
    tris = sum(j['accessors'][p['indices']]['count'] // 3 for m in j['meshes'] for p in m['primitives'])
    u['trojkaty'] = f'{tris:,}'.replace(',', ' ')
    u['sloty'] = [m['name'].rsplit('_', 1)[-1] for m in j['meshes']]
html = open(os.path.join(ROOT, 'podglad', 'viewer.html'), encoding='utf-8').read()
tag = '<script>window.UNITS=' + json.dumps(meta, ensure_ascii=False) + ';window.EMBED=' + json.dumps(emb) + ';</script>\n'
i = html.index('<script>\n// Dane wstrzykuje')
open(sys.argv[1], 'w', encoding='utf-8').write(html[:i] + tag + html[i:])
print('OK:', ', '.join(f"{k} ({v['trojkaty']} tr.)" for k, v in meta.items()))
