# Jednostki 3D do gry (Godot, styl chunky)

Modele powstają **z kodu** (Blender jako biblioteka Pythona). Kod opisuje wygląd, chód i atak każdej jednostki, a skrypt `build.py` zamienia go na pliki `.glb` dla Godota.

**Plan pracy:** jednostki podstawowe → fuzje (połączenie dwóch różnych jednostek w jedną) → zamknięta lista jednostek wydana do gry → później aktualizacje w kontrolowanych wersjach.

---

## 1. Mapa folderów: co gdzie jest

```
modele3d/
├── roster.json            ← LISTA JEDNOSTEK W GRZE + ich wersje (to edytujesz)
├── src/                   ← KOD
│   ├── jednostki/         ← jednostki podstawowe: 1 plik = 1 jednostka
│   │   ├── zolnierz.py
│   │   └── golem.py
│   ├── fuzje/             ← fuzje dopracowane ręcznie: 1 plik = 1 fuzja
│   │   └── kamienny_rycerz.py
│   ├── ataki/
│   │   ├── ruchy/         ← animacje ataku: ciecie.py, rzut.py, uderzenie.py
│   │   └── efekty/        ← pociski i efekty: glaz.py, krysztaly.py
│   ├── czesci/            ← części używane przez kilka jednostek (np. peleryna)
│   ├── build.py           ← JEDYNY skrypt, który uruchamiasz
│   ├── kit.py             ← silnik generatora (zwykle nie ruszasz)
│   ├── rejestr.py         ← sam znajduje jednostki i pilnuje zasad (nie ruszasz)
│   ├── fuzja.py           ← narzędzia fuzji + fuzje automatyczne (szkice)
│   ├── wydania.py         ← zamrażanie wydań i wykrywanie zmian (nie ruszasz)
│   └── pack_viewer.py     ← tworzy stronę z podglądem 3D
├── export/                ← WYNIK budowy (robocze): .glb jednostek, efekty, units.json
├── podglad/               ← rendery: z kamery gry 52°, przód, tył, chód, fazy ataku
├── szkice/                ← fuzje automatyczne (NIE idą do gry)
├── wydanie/               ← ZAMROŻONE wydania gry: wydanie/1.0/, wydanie/1.1/ … + ZMIANY.md
└── godot/unit.gd          ← jeden skrypt Godota dla wszystkich jednostek
```

## 2. „Chcę zmienić…”: gdzie szukać

| Chcę zmienić… | Plik | Czego szukać w pliku |
|---|---|---|
| wygląd hełmu żołnierza | `src/jednostki/zolnierz.py` | funkcja `helm` |
| kolory jednostki | plik jednostki | `PALETA` |
| proporcje (wzrost, szerokość barków…) | plik jednostki | `SZKIELET` |
| tempo i styl chodu | plik jednostki | `JEDNOSTKA['chod']` |
| którym atakiem walczy jednostka | plik jednostki | `JEDNOSTKA['atak']` (`ruch` + `efekt`) |
| przebieg animacji cięcia (zamach, moment trafienia) | `src/ataki/ruchy/ciecie.py` | pozy w `keys`, moment w `event` |
| wygląd głazu (w dłoni i w locie) | `src/ataki/efekty/glaz.py` | `model_glazu` |
| wygląd Kamiennego Rycerza | `src/fuzje/kamienny_rycerz.py` | `tulow`, `glowa`, `rece`… |
| pelerynę (u wszystkich, którzy ją noszą) | `src/czesci/tkaniny.py` | `peleryna` |
| które jednostki są w grze | `roster.json` | lista `jednostki` |

Każdy plik ma na górze krótki opis, co zawiera.

### Słowniczek pliku jednostki

```python
JEDNOSTKA = {
    'id': 'zolnierz',              # nazwa techniczna = nazwa pliku .glb
    'nazwa': 'Żołnierz',           # nazwa wyświetlana
    'szkielet': SZKIELET,          # proporcje (metry)
    'paleta': PALETA,              # kolory: (kolor, szorstkość, metaliczność, świecenie)
    'czesci': {'Head': glowa, ...},# slot -> funkcja budująca część
    'chod': dict(...),             # chód i oddech (amplitudy w stopniach)
    'atak': {'ruch': 'ciecie', 'efekt': None},
}
```

**Sloty** (stały słownik, każda jednostka używa tylko tych nazw): `Head` (głowa), `Headgear` (nakrycie głowy), `Body` (tułów), `Back` (plecy, peleryna), `Arms` (ręce), `Legs` (nogi), `Weapon` (broń w prawej ręce), `Offhand` (tarcza itp. w lewej). Slot `Prop` (rekwizyt w dłoni, np. głaz) dodaje się sam, gdy ruch ataku go używa.

**Szkielet:** każda jednostka ma te same 21 kości, różnią się tylko proporcje. Dzięki temu animacje i części pasują do każdej jednostki.

## 3. Polecenia

Uruchamiane z folderu `modele3d/src`:

| Polecenie | Co robi |
|---|---|
| `python build.py` | buduje wszystkie jednostki z `roster.json` do `export/` |
| `python build.py golem` | buduje jedną jednostkę (może być spoza rostera, np. nowa w trakcie pracy) |
| `python build.py golem --szybko` | … i robi szybkie rendery podglądu |
| `python build.py --podglad` | wszystko + rendery w pełnej jakości (kilkanaście minut) |
| `python build.py --szkice` | fuzje automatyczne wszystkich par jednostek podstawowych do `szkice/` |
| `python build.py --sprawdz` | co się zmieniło względem ostatniego wydania? |
| `python build.py --wydaj 1.0` | zamraża wydanie gry w `wydanie/1.0/` |
| `python3 pack_viewer.py podglad.html` | strona z interaktywnym podglądem 3D wszystkich jednostek |

Instalacja (jednorazowo): `python3.11 -m venv venv && ./venv/bin/pip install bpy pillow`, a potem uruchamiasz `../venv/bin/python build.py …`.

## 4. Jak pracować: krok po kroku

### Nowa jednostka podstawowa
1. Skopiuj `src/jednostki/golem.py` jako np. `src/jednostki/lucznik.py`.
2. Zmień `id`, `nazwa`, `SZKIELET`, `PALETA` i funkcje części.
3. Wybierz atak: istniejący ruch i efekt albo dopisz nowy plik w `ataki/ruchy/` lub `ataki/efekty/` (skopiuj podobny).
4. `python build.py lucznik --szybko` i obejrzyj rendery w `podglad/`. Popraw i powtórz.
5. Gdy gotowa: dopisz `"lucznik": { "wersja": 1 }` do `roster.json`.

Rejestr sam znajdzie nowy plik. Jeśli coś jest niezgodne z zasadami (np. nieznany slot albo nieistniejący atak), budowa przerwie się z komunikatem, co poprawić.

### Nowa fuzja
1. `python build.py --szkice`: dla każdej pary jednostek podstawowych powstaje szkic fuzji automatycznej w `szkice/` (model + 2 rendery). Szkic bierze sylwetkę od większego rodzica, a głowę i broń od mniejszego. Atak to ruch mniejszego i efekt większego.
2. Wybierz pary, które chcesz w grze.
3. Dla każdej zrób plik w `src/fuzje/`. Wzorem jest `kamienny_rycerz.py`: proporcje i kolory liczą się z rodziców (`polacz_szkielet`, `polacz_palete`), a części mieszane i atak projektujesz sam. Wpisz `'rodzice': ('a', 'b')`.
4. Dopisz fuzję do `roster.json`.

Szkic nigdy nie trafi do gry sam z siebie. Do gry trafia tylko to, co jest w `roster.json`.

### Wydanie gry
1. `python build.py --sprawdz`: przegląd, co się zmieniło.
2. `python build.py --wydaj 1.0`: pliki trafiają do `wydanie/1.0/` i są **zamrożone** (tego folderu się nie zmienia).
3. Do Godota kopiujesz zawartość `wydanie/1.0/`.
4. Dopisz w `wydanie/ZMIANY.md` krótko, co i dlaczego.

### Aktualizacja po wydaniu (wygląd, atak…)
1. Zmień kod, np. hełm w `jednostki/zolnierz.py`.
2. `python build.py --sprawdz` pokaże dokładnie, co się zmieniło:
   ```
   zolnierz   ZMIENIONA BEZ PODBICIA WERSJI v1 – zmiany: Headgear
   golem      bez zmian v1
   ```
3. Jeśli zmiana jest zamierzona, podnieś wersję w `roster.json` (`"zolnierz": { "wersja": 2 }`). Jeśli nie, cofnij ją w kodzie.
4. `python build.py --wydaj 1.1`. Wydanie z niepodbitą wersją zmienionej jednostki zostanie **odrzucone**, więc nic nie zmieni się po cichu.

**Uwaga na części wspólne:** zmiana w `czesci/` albo w ruchu lub efekcie ataku dotyka wszystkich jednostek, które ich używają. `--sprawdz` pokaże wtedy każdą z nich osobno.

## 5. Godot

Pliki z `wydanie/<wersja>/` (albo roboczo z `export/`) kopiujesz do `res://units/`:

- `<id>.glb`: jednostka z animacjami `Idle_loop`, `Walk_loop` (zapętlone) i `Attack`;
- `efekt_<id>.glb`: pociski i efekty ataków;
- `units.json`: dane dla gry, czyli nazwy plików i animacji, długość ataku, moment trafienia (`moment_s`), typ ataku, plik efektu i kość, z której startuje pocisk.

`godot/unit.gd` to jeden skrypt dla wszystkich jednostek. Ustawiasz w nim tylko `unit_id`, a resztę czyta z `units.json`, więc **nowa jednostka nie wymaga nowego kodu w grze**. Skrypt nie był jeszcze uruchamiany w edytorze Godota; sprawdź go przy pierwszym imporcie.

Statystyki walki (obrażenia, życie, zasięg) trzymaj osobno w grze, np. w `balans.json`. Balans zmieniasz wtedy bez ruszania modeli.

## 6. Jednostki (stan obecny)

| id | Nazwa | Atak (ruch + efekt) | Moment trafienia |
|---|---|---|---|
| `zolnierz` | Żołnierz | cięcie, wręcz | 0,45 s z 1,00 s |
| `golem` | Golem | rzut + głaz (pocisk z kości `prop.R`) | 1,24 s z 2,00 s |
| `kamienny_rycerz` | Kamienny Rycerz (fuzja golem + żołnierz) | uderzenie + kryształy (obszar) | 0,83 s z 1,60 s |
