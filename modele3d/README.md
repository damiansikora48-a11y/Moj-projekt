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
│   │   ├── golem.py
│   │   ├── mag_ognia.py
│   │   └── lesny_lucznik.py
│   ├── fuzje/             ← fuzje dopracowane ręcznie: 1 plik = 1 fuzja
│   │   └── kamienny_rycerz.py
│   ├── ataki/
│   │   ├── ruchy/         ← animacje ataku: ciecie.py, rzut.py, uderzenie.py
│   │   └── efekty/        ← pociski i efekty: glaz.py, krysztaly.py
│   ├── zywioly/           ← przepisy żywiołów: stal.py, kamien.py, ogien.py, natura.py
│   ├── czesci/            ← części używane przez kilka jednostek (np. peleryna)
│   ├── siatka.py          ← role, żywioły i nazwy pól siatki fuzji
│   ├── build.py           ← JEDYNY skrypt, który uruchamiasz
│   ├── kit.py             ← silnik generatora (zwykle nie ruszasz)
│   ├── rejestr.py         ← sam znajduje jednostki i pilnuje zasad (nie ruszasz)
│   ├── fuzja.py           ← narzędzia fuzji, szkice automatyczne, Przebudzenie
│   ├── wydania.py         ← zamrażanie wydań i wykrywanie zmian (nie ruszasz)
│   └── pack_viewer.py     ← tworzy stronę z podglądem 3D
├── export/                ← WYNIK budowy (robocze): .glb jednostek, efekty, units.json
├── podglad/               ← rendery: z kamery gry 52°, przód, tył, chód, fazy ataku
├── szkice/                ← fuzje automatyczne (NIE idą do gry) + siatka.png: cała siatka na 1 obrazku
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
| sposób upadku przy śmierci | plik jednostki | `smierc` ('tyl' / 'przod') i `smierc_dlon` (kąt dłoni z bronią) w `chod` |
| przebieg trafienia i śmierci (wspólny dla wszystkich) | `src/kit.py` | `reakcje` |
| którym atakiem walczy jednostka | plik jednostki | `JEDNOSTKA['atak']` (`ruch` + `efekt`) |
| przebieg animacji cięcia (zamach, moment trafienia) | `src/ataki/ruchy/ciecie.py` | pozy w `keys`, moment w `event` |
| wygląd głazu (w dłoni i w locie) | `src/ataki/efekty/glaz.py` | `model_glazu` |
| wygląd Kamiennego Rycerza | `src/fuzje/kamienny_rycerz.py` | `tulow`, `glowa`, `rece`… |
| pelerynę (u wszystkich, którzy ją noszą) | `src/czesci/tkaniny.py` | `peleryna` |
| jak wygląda żywioł w fuzjach (barwy, ozdoby, efekty) | `src/zywioly/<żywioł>.py` | `barwy`, `zamiany`, `ozdoby`, `efekty` |
| nazwę pola siatki (np. Kryształowy Łucznik) | `src/siatka.py` | `NAZWY` |
| wygląd Przebudzenia wspólny dla wszystkich (złocenie, świecenie) | `src/fuzja.py` | `przebudz` |
| wyjątkowe dodatki Przebudzenia danej fuzji (np. kolce) | plik fuzji | `'przebudzenie'` w `JEDNOSTKA` |
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
    'rola': 'wojownik',            # wojownik / kolos / mag / strzelec (siatka.py)
    'zywiol': 'stal',              # stal / kamien / ogien / natura
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
| `python build.py --szkice` | szkice fuzji: dla każdej pary OBIE możliwości (rola od A + żywioł B i odwrotnie) + `szkice/siatka.png` |
| `python build.py --siatka` | tylko odśwież obraz siatki z istniejących renderów |
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
Fuzje są **wybierane ręcznie** (lista w `projekt/zasady_gry.md`): każda musi mieć nową sylwetkę i nową rolę, a każda jednostka podstawowa wchodzi w najwyżej 2 fuzje. Szkice automatyczne to tylko pomoc w szukaniu pomysłów (rola od jednego rodzica, żywioł od drugiego).

1. `python build.py --szkice`: dla każdej pary powstają **dwa** szkice (obie możliwości) i obraz `szkice/siatka.png`. Szkic bierze od rodzica-roli sylwetkę, części, chód i ruch ataku, a od rodzica-żywiołu barwy, przebarwienie materiałów, ozdoby na barkach (slot `Element`) i efekt ataku (tabela `efekty` w pliku żywiołu).
2. Dla każdej pary wybierz jedną możliwość i zdecyduj, czy idzie do gry.
3. Dla każdej zrób plik w `src/fuzje/`. Wzorem jest `kamienny_rycerz.py`: proporcje i kolory liczą się z rodziców (`polacz_szkielet`, `polacz_palete`), a części mieszane i atak projektujesz sam. Wpisz `'rodzice': ('a', 'b')`.
4. Dopisz fuzję do `roster.json`.
5. **Przebudzenie** (rzadki wynik) powstaje samo: każda fuzja ręczna ma wariant `<id>_przebudzony` (złocone metale, mocniejsze świecenie). Wyjątkowe dodatki fuzja ustawia w swoim pliku w `'przebudzenie'`: części (slot `Aura`), kolory i to, czy pokazać ogólną aureolę z kręgiem run (`'poswiata'`). Kamienny Rycerz ma kryształowe kolce ze świecącymi czerwonymi końcami zamiast poświaty. Dopisz wariant do `roster.json` razem z fuzją.

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

- `<id>.glb`: jednostka z animacjami `Idle_loop`, `Walk_loop` (zapętlone), `Attack`, `Hit` (reakcja na trafienie, ok. 0,5 s) i `Death` (upadek, kończy się na leżącej postaci);
- `efekt_<id>.glb`: pociski i efekty ataków;
- `units.json`: dane dla gry, czyli nazwy plików i animacji, długość ataku, moment trafienia (`moment_s`), typ ataku, plik efektu i kość, z której startuje pocisk.

**Statusy ataku:** jeśli atak nakłada status (np. podpalenie), `units.json` ma w `atak.status` jego typ, zakres czasu (`czas_min_s`–`czas_max_s`, gra losuje z niego przy każdym trafieniu) i plik efektu. W Godocie wywołujesz `apply_status(wróg)` dla każdego trafionego wroga, a obrażenia od statusu liczy gra.

`godot/unit.gd` to jeden skrypt dla wszystkich jednostek. Ustawiasz w nim tylko `unit_id`, a resztę czyta z `units.json`, więc **nowa jednostka nie wymaga nowego kodu w grze**. Skrypt nie był jeszcze uruchamiany w edytorze Godota; sprawdź go przy pierwszym imporcie.

Statystyki walki (obrażenia, życie, zasięg) trzymaj osobno w grze, np. w `balans.json`. Balans zmieniasz wtedy bez ruszania modeli.

## 6. Mapa miasta

Miasto pod wysoką górą, z murami z 3 stron (lewy, przedni z bramą, prawy). Każdy mur i brama ulepszają się **osobno**, w 4 poziomach: Palisada → Wzmocniona palisada → Mur kamienny → Warownia. Wieże na przednich narożnikach przyjmują poziom wyższego z dwóch sąsiednich murów.

| Chcę zmienić… | Plik |
|---|---|
| wymiary miasta, położenie murów, działki pod budynki, strefy ataku | `src/mapa/uklad.py` |
| wygląd murów, bramy i wież na każdym poziomie, liczbę miejsc dla obrońców | `src/mapa/mury.py` |
| teren: góra, łąki, lasy, staw z wodospadem, plac, drogi | `src/mapa/teren.py` |

Polecenie: `python build.py --mapa` (eksport) albo `python build.py --mapa --podglad` (eksport + rendery).

Pliki w `export/mapa/`:
- `teren.glb`, `mur_bok_<1-4>.glb` (lewy i prawy to ten sam element, obrócony), `mur_front_<1-4>.glb`, `brama_<1-4>.glb`, `naroznik_<1-4>.glb`;
- w każdym murze, bramie i wieży są puste węzły `obronca_01`, `obronca_02`… czyli **miejsca dla obrońców**. Wyższy poziom ma więcej miejsc;
- `uklad.json`: gdzie postawić każdy element (już w układzie współrzędnych Godota), liczba miejsc obrońców na poziom, **działki pod budynki** (D1–D9, wszystkie na razie wolne), plac i **strefy ataku** przed każdym murem.

W Godocie `godot/mapa.gd` składa miasto z tych plików i ma funkcje `ustaw_poziom_muru("przod", 3)`, `ustaw_poziom_bramy(2)`, `miejsca_obroncow("lewy")` i `dzialka("D1")`. Skrypt nie był jeszcze uruchamiany w edytorze.

**Nowy budynek w przyszłości:** wpisz go w `DZIALKI` w `src/mapa/uklad.py` (zajmij wolną działkę albo dodaj nową).

## 7. Jednostki (stan obecny)

| id | Nazwa | Atak (ruch + efekt) | Moment trafienia |
|---|---|---|---|
| `zolnierz` | Żołnierz | cięcie, wręcz | 0,45 s z 1,00 s |
| `golem` | Golem | rzut + głaz (pocisk z kości `prop.R`) | 1,24 s z 2,00 s |
| `kamienny_rycerz` | Kamienny Rycerz (fuzja golem + żołnierz) | uderzenie + kryształy (obszar) | 0,83 s z 1,60 s |
| `mag_ognia` | Mag ognia | czar + kula ognia (pocisk z lewej dłoni) | 0,66 s z 1,20 s |
| `lesny_lucznik` | Leśny Łucznik | strzał + strzała (pocisk z `prop.R`) | 0,83 s z 1,33 s |
| `kamienny_rycerz_przebudzony` | Przebudzony Kamienny Rycerz (rzadki wariant) | jak Kamienny Rycerz | 0,83 s z 1,60 s |

### Klocki ataków do wykorzystania

| Ruch (`ataki/ruchy/`) | Opis | Skąd startuje pocisk |
|---|---|---|
| `ciecie` | cięcie mieczem z zamachu | – (wręcz) |
| `rzut` | chwyta rekwizyt z ziemi, rzuca znad głowy | `prop.R` (prawa dłoń) |
| `uderzenie` | uderzenie oburącz w ziemię | – (wręcz/obszar) |
| `czar` | skupienie przy piersi, wypchnięcie dłoni | `hand.L` (lewa dłoń) |
| `strzal` | nałożenie strzały, naciągnięcie łuku, strzał | `prop.R` (strzała w prawej dłoni) |

| Efekt (`ataki/efekty/`) | Typ | Plik w grze |
|---|---|---|
| `glaz` | pocisk (także rekwizyt w dłoni przy `rzut`) | `efekt_glaz.glb` |
| `krysztaly` | obszar: kolce z ziemi | `efekt_krysztaly.glb` |
| `kula_ognia` | pocisk (też w dłoni przy `rzut`) | `efekt_kula_ognia.glb` |
| `strzala` | pocisk (też na cięciwie przy `strzal`) | `efekt_strzala.glb` |
| `krysztaly_plonace` | obszar: kolce z rozżarzonymi końcami i płomieniami (Przebudzony Kamienny Rycerz) | `efekt_krysztaly_plonace.glb` |
| `podpalenie` | status: płomienie przyczepiane do płonącego wroga | `efekt_podpalenie.glb` |

Aktualne szkice wszystkich pól siatki: `szkice/siatka.png`.
