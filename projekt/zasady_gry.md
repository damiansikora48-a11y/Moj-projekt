# Zasady gry: ustalenia projektowe

Dokument zbiera decyzje o rozgrywce. Liczby oznaczone **(propozycja)** są punktem wyjścia do balansu, nie ostateczną wartością.

---

## 1. Pętla gry

1. Gracz rozbudowuje **miasto**: budynki do ulepszania, w tym **mury**.
2. Na murach i przy bramie stawia **obrońców** (jednostki).
3. Obrona i bitwy dają **złoto** oraz **doświadczenie** jednostek.
4. Jednostki z wystarczającym doświadczeniem są **gotowe do fuzji**.
5. W **budynku fuzji** łączy dwie gotowe jednostki w silniejszą.
6. Złoto idzie na fuzje, ulepszenia budynków i naprawę murów, więc gracz musi dalej walczyć.

## 2. Jednostki podstawowe

Każda jednostka ma **rolę** (jak walczy) i **żywioł** (z czego jest, jaką ma moc). To pomaga projektować, ale nie wyznacza fuzji (patrz punkt 3).

| Rola | Miejsce w obronie |
|---|---|
| Wojownik | przy bramie, walka wręcz |
| Kolos | blokowanie wyłomów, tank |
| Mag | na murach, czary z dystansu |
| Strzelec | na murach, dystans fizyczny |

Żywioły (robocze): **Stal, Kamień, Ogień, Natura**. Żywioł może dawać przewagę nad określonymi wrogami (np. ogień przeciw wrogom natury).

Jednostki podstawowe (stan obecny):

| Jednostka | Rola | Żywioł |
|---|---|---|
| Żołnierz | Wojownik | Stal |
| Golem | Kolos | Kamień |
| Mag ognia | Mag | Ogień |
| Leśny Łucznik | Strzelec | Natura |

## 3. Fuzje

### Zasada: zamknięta lista wyjątkowych fuzji (księga przepisów)
Nie łączymy wszystkiego ze wszystkim. Fuzje **wymyślamy i wybieramy ręcznie**. Każda to **nowa postać**, a nie przebarwienie rodzica.

Kryteria, które musi spełnić każda fuzja:
1. **Nowa sylwetka:** z kamery 52° wygląda inaczej niż oboje rodzice.
2. **Nowa rola w obronie:** robi coś, czego nie umie żadna jednostka podstawowa.
3. **Każda jednostka podstawowa wchodzi w najwyżej 2 fuzje** (żadnych „pięciu odsłon maga”).
4. **Nowa jednostka podstawowa dodaje 1–2 fuzje,** a nie fuzje ze wszystkimi.
5. **Nazwa brzmi mocniej niż rodzice,** bo fuzja jest od nich silniejsza.

A + B = B + A: kolejność wybierania jednostek w budynku nie ma znaczenia.

Dla gracza: w budynku fuzji jest **księga przepisów**, czyli lista dostępnych fuzji, która rośnie z poziomem budynku. Pary spoza listy się nie łączą.

Rola i żywioł jednostek (`modele3d/src/siatka.py`, `zywioly/`) to tylko narzędzie projektowe: kolory, ozdoby i efekty. Nie decydują o tym, co powstaje, i nie są pokazywane graczowi.

### Lista fuzji

| Fuzja | Z czego | Rola w obronie | Status |
|---|---|---|---|
| **Kamienny Rycerz** | Żołnierz + Golem | ciężki obrońca bramy | ✅ gotowa; Przebudzony: kryształowe kolce z czerwonymi końcami, atak z płonącymi kolcami i **podpaleniem** wrogów na 4–6 s (losowo przy każdym trafieniu) |
| Magmowy Golem | Golem + Mag ognia | niszczyciel oblężeń, płonąca ziemia | propozycja |
| Strażnik Murów | Żołnierz + Łucznik | ciężki strzelec: kusza i pawęż | propozycja |
| Golem-Balista | Golem + Łucznik | chodząca wieża, daleki zasięg | propozycja |
| Łowca Run | Mag ognia + Łucznik | strzały wybuchające czarem | pomysł na później |
| – | Żołnierz + Mag ognia | brak pomysłu na nową rolę | nie robimy na razie |

Cel na premierę **(propozycja)**: 4 jednostki podstawowe + 3–4 fuzje.

### Gotowość do fuzji
- Jednostka musi zdobyć **wymagane doświadczenie** (np. poziom 5 **(propozycja)**).
- Fuzja **zużywa oba rodzaje jednostek**. Wynik zachowuje część ich doświadczenia (np. 25% **(propozycja)**).

### Budynek fuzji
- Kolejne poziomy budynku odblokowują nowe pola siatki, zwiększają szansę na Przebudzenie i skracają czas fuzji.
- Ulepszanie kosztuje złoto i czas.

### Przebudzenie (rzadki wynik)
- Każda fuzja ma szansę dać **wersję Przebudzoną** tej samej jednostki: złocona zbroja, mocniejsze świecenie i **własny, wyjątkowy dodatek** tej fuzji (np. Kamienny Rycerz: kryształowe kolce ze świecącymi czerwonymi końcami na barkach i nogach), do tego mocniejszy atak lub dodatkowa zdolność. Bez poświat na ziemi, bo gracze kojarzą je z zaznaczeniem jednostki.
- Rzadki wynik nigdy nie jest gorszy od zwykłego. Gracz nie traci na losowaniu.
- Szansa jest **zawsze pokazana** przed fuzją.

| Źródło szansy | Wartość **(propozycja)** |
|---|---|
| Bazowa | 3% |
| Poziom budynku fuzji | +1% za poziom |
| Doświadczenie ponad minimum | do +5% |
| Katalizator (runa żywiołu z obrony murów) | +10% |

**Gwarancja:** licznik zwykłych fuzji bez Przebudzenia.
- Od 15. fuzji (miękki próg) szansa rośnie o +5% z każdą kolejną **(propozycja)**.
- Przy 25. fuzji (twardy próg) Przebudzenie jest pewne **(propozycja)**.
- Po Przebudzeniu licznik się zeruje.

**Później (aktualizacja):** 2–3 sekretne fuzje dla wybranych par, z małą szansą przy jednostkach na maksymalnym poziomie.

## 4. Miasto i mury

- Miasto stoi pod wysoką kamienną górą (z tyłu). Mury są z 3 stron: **lewy, przedni (z bramą), prawy**.
- **Każdy mur ulepsza się osobno.** **Brama** na środku muru przedniego ulepsza się osobno.
- **15 poziomów ulepszeń** dla każdego muru i dla bramy. Wygląd zmienia się co 3 poziomy:
  - 1–3 Palisada: **brak obrońców na murach** (nie ma pomostu),
  - 4–6 Mur drewniany: mało miejsc dla obrońców (3 na murze bocznym, 4 na przednim),
  - 7–9 Słaby mur kamienny (4 / 6),
  - 10–12 Lepszy mur kamienny (7 / 9),
  - 13–15 Warownia (9 / 11).
- **Brama** i **6 wież** ulepszają się osobno, w tych samych 15 poziomach i progach wyglądu: 2 przednie narożne, 2 tylne na końcach murów przy górze i 2 przy bramie.
- **Uszkodzenia po ataku widać na modelach.** Każdy mur, brama i wieża ma 4 stany zależne od wytrzymałości:
  - 100–70% cały,
  - 70–40% lekko uszkodzony: rysy, strącone blanki, kamienie pod murem,
  - 40–1% mocno uszkodzony: dziury, sterty gruzu, płonące szczątki; część miejsc dla obrońców znika razem z zawalonym pomostem,
  - 0% wyłom: mur jest przebity do ziemi i wrogowie mogą tędy wejść; brama traci wrota; wieża zostaje ruiną.

  Naprawa za złoto przywraca wytrzymałość i wygląd.
- **Atakujący wybiera stronę ataku** (lewa, przód, prawa). Przed każdym murem jest wolna łąka na rozstawienie wojsk.
- Wnętrze miasta: 52 × 40 m.
- **Budynki w środku stoją na stałych działkach** (D1–D11). **Budynek główny** stoi na skalnej półce (podwyższeniu) D1 przy ścianie góry, ze schodami na plac i wolnym miejscem wokół. Ma **20 poziomów** i każdy poziom coś widocznie zmienia: od małej drewnianej chaty po okazałą kamienną rezydencję ze zdobieniami. Na środku miasta jest plac ze studnią. Co stoi na pozostałych działkach, ustalamy razem; część zostaje wolna na przyszłe budynki.
- **Budynki na działkach** (każdy ma **20 poziomów**, każdy poziom coś widocznie zmienia; wygląd: drewno → mur pruski → kamień → okazała budowla):
  - **Budynek fuzji** (D3): łączenie jednostek, księga przepisów, szansa na Przebudzenie; od kręgu kamieni z ołtarzem po świątynię z unoszącym się kryształem,
  - **Koszary** (D6): szkolenie jednostek i zdobywanie doświadczenia; od namiotu z ogniskiem po okazałe koszary z wieżą,
  - **Kuźnia** (D2): ulepszanie broni i pancerzy; od szopy z kowadłem po kamienną kuźnię z piecem hutniczym.
  - **Magazyn** (D5): przechowuje złoto i zapasy (wyższy poziom = większa pojemność); od wiaty ze skrzyniami po kamienny magazyn ze złotą kopułą skarbca,
  - **Akademia** (D4): badania i odkrycia, czyli ulepszenia działające na całe miasto (szczegóły w punkcie 4a); od chatki uczonego po akademię z obserwatorium.
  Wolne działki: D7–D11 (na przyszłe budynki; oznaczone palikami ze sznurkiem).
- **Drogi:** brukowana droga od bramy do placu, a od placu wijące się ścieżki z płyt do wejść budynków. Zabudowane działki nie mają widocznego prostokąta: podwórze jest częścią budynku i zmienia się z poziomem (ubita ziemia → żwir → płyty → bruk z krzewami).
- **Tablica ogłoszeń** przy studni na placu: aktualizacje, wydarzenia i wiadomości dla graczy (np. dymek „!” przy nowej aktualizacji).
- Klimat: dużo zieleni (łąki, lasy, staw z wodospadem), a góra ma trawiaste zbocza, półki skalne z sosnami, głazy, śnieżny szczyt i duży wodospad po prawej z jeziorem i rzeką.

## 4a. Badania (Akademia)

**Nazwa:** Akademia. Krótka, od razu kojarzy się z badaniami i pasuje do wyglądu budynku: biblioteka, obserwatorium, alchemia.

### Zasady
- **Każdy poziom Akademii odblokowuje 1–2 nowe badania.** Dalsze badania wymagają wyższego poziomu budynku.
- **Każdy poziom Akademii przyspiesza badania o 1%** **(propozycja)**: czas = czas bazowy / (1 + 0,01 × poziom Akademii), czyli na poziomie 20 badania idą o 20% szybciej.
- **Im dalsze badanie, tym dłużej trwa i więcej kosztuje.** Czas bazowy rośnie o ok. 30% na każdy próg **(propozycja)**: od ok. 10 min (próg 1) do ok. 24 h (próg 20). Koszt w złocie rośnie podobnie.
- **Jedno badanie naraz.** Zbadane badanie działa na stałe.
- **Rubiny** mogą tylko skrócić czas badania, tak jak budowę. Nie odblokowują badań wcześniej.
- Efekty badań są **małe, ale się sumują**. Nie dają nic, czego nie dałoby się zdobyć grą: żadnych dodatkowych kolejek ani szansy na Przebudzenie (te zostają przy budynku fuzji i katalizatorach).

### Lista badań **(propozycja: nazwy i wartości do balansu)**
Kategorie: 🏗️ Budownictwo, 🛡️ Obrona, ⚔️ Wojsko, ✨ Fuzje, 💰 Gospodarka.

| Poziom Akademii | Odblokowane badania | Efekt |
|---|---|---|
| 1 | 🏗️ Narzędzia budowlane | −5% czasu budowy |
| 1 | ⚔️ Zwiad | podgląd siły wroga przed obroną |
| 2 | 🛡️ Ciosany kamień | −5% kosztu ulepszeń murów, bramy i wież |
| 3 | ⚔️ Musztra | +5% doświadczenia jednostek z bitew |
| 4 | 🛡️ Smoła i wrzący olej | obrońcy na murach +5% obrażeń |
| 5 | 💰 Spis zapasów | +10% pojemności magazynu |
| 6 | 🛡️ Zaprawa murarska | −10% kosztu naprawy murów |
| 7 | ⚔️ Hartowanie stali | +3% obrażeń jednostek walczących wręcz |
| 8 | ✨ Wiedza o runach | −10% czasu fuzji |
| 9 | 🛡️ Strzelnice w wieżach | +10% zasięgu obrońców w wieżach |
| 10 | 💰 Szlaki kupieckie | +5% złota z bitew |
| 10 | 🏗️ Rusztowania | −10% czasu napraw |
| 11 | 🛡️ Okute wrota | +10% wytrzymałości bramy |
| 12 | ⚔️ Medycyna polowa | −15% czasu leczenia rannych jednostek |
| 13 | ⚔️ Zbrojmistrzostwo | +5% pancerza jednostek |
| 14 | ✨ Alchemia żywiołów | fuzja zachowuje 30% doświadczenia zamiast 25% |
| 15 | 🛡️ Fundamenty warowni | +10% wytrzymałości murów i wież |
| 16 | ⚔️ Taktyka | wszystkie jednostki +3% obrażeń |
| 17 | 💰 Skarbiec królewski | +15% pojemności magazynu |
| 18 | 🛡️ Runy ochronne | mury i wieże −10% obrażeń od czarów |
| 19 | ✨ Mistrzostwo fuzji | −20% czasu fuzji |
| 20 | 🏗️ Złoty wiek | −10% czasu budowy i badań |

Nowe badania w aktualizacjach: dopisujemy je do istniejących poziomów (np. drugie badanie na poziomie 5) albo do nowych poziomów Akademii, jeśli kiedyś podniesiemy limit ponad 20. Gracze dowiedzą się o nich z tablicy ogłoszeń.

## 5. Ekonomia

### Waluty

| Waluta | Skąd | Na co |
|---|---|---|
| **Złoto** | bitwy, obrona murów, zadania | fuzje, ulepszenia budynków, naprawa murów, szkolenie |
| **Rubiny** (premium) | zakup za prawdziwe pieniądze; mało: osiągnięcia, codzienne zadania | wyłącznie przyspieszenia i wygoda (lista niżej) |

### Za rubiny MOŻNA
- przyspieszyć budowę i ulepszenie budynków,
- przyspieszyć zdobywanie doświadczenia (np. „księga treningu”), czyli szybszą gotowość do fuzji,
- skrócić czas samej fuzji,
- dodatkową kolejkę budowy,
- kosmetykę (np. wygląd murów lub sztandarów).

### Za rubiny NIE MOŻNA
- zwiększyć szansy na Przebudzenie: **żadnych katalizatorów ani run za rubiny**, także w paczkach,
- kupić jednostek ani fuzji niedostępnych w zwykłej grze,
- kupić złota w ilościach, które omijają bitwy (do decyzji: całkowity zakaz albo mały dzienny limit).

### Balans złota
- Złoto ma pochodzić **głównie z bitew**, więc koszty fuzji, ulepszeń i naprawy murów muszą wymagać regularnej walki.
- **Naprawa murów po ataku** to stały wydatek, który utrzymuje gracza w walce.
- Cel tempa **(propozycja)**: jedno ważne ulepszenie lub fuzja na 1–2 sesje gry. Przy rzadszym tempie gracz się nudzi, przy częstszym ekonomia nie ma znaczenia.
- Balans ustalamy na **modelu ekonomii** (symulacja dzień po dniu: przychody, wydatki, postęp), nie na oko.

### Uwagi prawne i sklepowe
- Rubiny nie kupują losowych nagród, więc nie dotyczą ich zasady skrzynek z nagrodami (loot boxów). Trzeba to utrzymać przy każdej nowej ofercie w sklepie.
- Cena w prawdziwych pieniądzach musi być jasno pokazana przy zakupie rubinów.

---

## 6. Otwarte pytania
- [ ] Które fuzje z listy wchodzą na premierę (propozycja: 4 podstawowe + 3–4 fuzje)?
- [ ] Wymagany poziom doświadczenia do fuzji i koszt fuzji w złocie.
- [ ] Czy rubiny mogą kupić złoto (i z jakim limitem)?
- [ ] Rodzaje wrogów i ich słabości na żywioły.
- [ ] Koszty ulepszeń murów i bramy na każdym z 15 poziomów (oraz co poza wyglądem daje każdy poziom, np. wytrzymałość).
- [ ] Co dają kolejne poziomy budynku fuzji, koszar, kuźni i magazynu (koszty, czasy, bonusy).
- [ ] Balans badań: czasy, koszty i wartości efektów (punkt 4a).
- [ ] Co stanie na wolnych działkach D7–D11.
