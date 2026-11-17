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

## 2. Jednostki: rola + żywioł

Każda jednostka podstawowa ma **rolę** (jak walczy) i **żywioł** (z czego jest, jaką ma moc).

| Rola | Miejsce w obronie |
|---|---|
| Wojownik | przy bramie, walka wręcz |
| Kolos | blokowanie wyłomów, tank |
| Mag | na murach, czary z dystansu |
| Strzelec | na murach, dystans fizyczny |

Żywioły (robocze): **Stal, Kamień, Ogień, Natura**. Żywioł daje przewagę nad określonymi wrogami (np. ogień przeciw wrogom natury), więc warto mieć różne fuzje.

Jednostki podstawowe (stan obecny):

| Jednostka | Rola | Żywioł |
|---|---|---|
| Żołnierz | Wojownik | Stal |
| Golem | Kolos | Kamień |
| Mag ognia | Mag | Ogień |
| *(planowana)* Leśny Łucznik | Strzelec | Natura |

## 3. Fuzje

### Reguła
- Fuzja dwóch jednostek daje jednostkę o **roli jednego rodzica i żywiole drugiego**.
- **Kolejność nie ma znaczenia:** A + B = B + A. Każda para daje **jedną** fuzję. Dla każdej pary ustalamy raz, który rodzic daje rolę.
- Wynik jest **przewidywalny**: gracz przed fuzją widzi, co dostanie.

Siatka (role × żywioły) pokazuje wszystkie możliwe jednostki. Do gry trafiają tylko wybrane pola, kolejne wchodzą w aktualizacjach.

| | Stal | Kamień | Ogień | Natura |
|---|---|---|---|---|
| **Wojownik** | Żołnierz | **Kamienny Rycerz** ✅ | Płomienny Rycerz | Rycerz Cierni |
| **Kolos** | Stalowy Kolos | Golem | Magmowy Golem | Kamienny Ent |
| **Mag** | Mag Bitewny | Geomanta | Mag ognia | Druid |
| **Strzelec** | Kusznik | Procarz | Ognisty Łucznik | Leśny Łucznik |

Przy jednej fuzji na parę, 4 jednostki podstawowe dają 6 fuzji. Które pole siatki wypełnia dana para, ustalamy przy projektowaniu tej fuzji.

### Gotowość do fuzji
- Jednostka musi zdobyć **wymagane doświadczenie** (np. poziom 5 **(propozycja)**).
- Fuzja **zużywa oba rodzaje jednostek**. Wynik zachowuje część ich doświadczenia (np. 25% **(propozycja)**).

### Budynek fuzji
- Kolejne poziomy budynku odblokowują nowe pola siatki, zwiększają szansę na Przebudzenie i skracają czas fuzji.
- Ulepszanie kosztuje złoto i czas.

### Przebudzenie (rzadki wynik)
- Każda fuzja ma szansę dać **wersję Przebudzoną** tej samej jednostki: złote zdobienia, aura, mocniejszy atak lub dodatkowa zdolność.
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

## 4. Ekonomia

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

## 5. Otwarte pytania
- [ ] Ostateczna lista żywiołów (Natura czy np. Lód lub Cień?).
- [ ] Które pola siatki są na premierę (propozycja: 4 podstawowe + 4–6 fuzji)?
- [ ] Wymagany poziom doświadczenia do fuzji i koszt fuzji w złocie.
- [ ] Czy rubiny mogą kupić złoto (i z jakim limitem)?
- [ ] Rodzaje wrogów i ich słabości na żywioły.
- [ ] Poziomy murów i liczba miejsc dla obrońców na każdym poziomie.
