"""Tworzy samodzielny podgląd (modele osadzone w base64) do publikacji.
Użycie: python3 pack_viewer.py <plik_wyjściowy.html>"""
import base64, json, os, struct, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta = json.load(open(os.path.join(ROOT, 'export', 'units.json'), encoding='utf-8'))
emb, stats = {}, {}
for key in ('soldier', 'golem', 'hybrid'):
    raw = open(os.path.join(ROOT, 'export', f'{key}.glb'), 'rb').read()
    emb[key] = base64.b64encode(raw).decode()
    n = struct.unpack('<I', raw[12:16])[0]
    j = json.loads(raw[20:20 + n])
    tris = sum(j['accessors'][p['indices']]['count'] // 3 for m in j['meshes'] for p in m['primitives'])
    m = meta[key]
    stats[key] = {'tris': f'{tris:,}'.replace(',', ' '), 'mats': len(j['materials']),
                  'event': m['attack_event'], 'event_time': m['attack_event_time_s'], 'length': m['attack_length_s']}
html = open(os.path.join(ROOT, 'podglad', 'viewer.html'), encoding='utf-8').read()
tag = ('<script>window.EMBED=' + json.dumps(emb) + ';window.STATS=' + json.dumps(stats) + ';</script>\n')
i = html.index('<script>\nconst UNITS')
open(sys.argv[1], 'w', encoding='utf-8').write(html[:i] + tag + html[i:])
print(stats)
