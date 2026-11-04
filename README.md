# 🏰 Pogranicza: Droga do Korony

Średniowieczna gra strategiczna w przeglądarce, zbudowana na podstawie dokumentu
„Koncepcja średniowiecznej gry strategicznej” (wersja 1.3, 4 listopada 2026).

To **prototyp do testów**. Gra jest jednoosobowa: inni gracze, sojusze, arena, wojny
o forty i koronę są symulowane przez postacie komputerowe. Docelowa gra online
wymaga serwera, kont i płatności. Ten prototyp ich nie ma.

## Uruchomienie

Otwórz `index.html` w przeglądarce (komputer lub telefon). Możesz też uruchomić
lokalny serwer:

```bash
python3 -m http.server 8000   # potem http://localhost:8000
```

Postęp zapisuje się automatycznie w przeglądarce. Po powrocie gra nadrabia czas
nieobecności (produkcja, budowy, napady, marsze).

**Tempo testowe:** kliknij zegar w prawym górnym rogu (×1 / ×10 / ×60 / ×360).
W *Więcej → Ustawienia* można też przewinąć czas o 1 h, 8 h, dzień lub tydzień.

## Co jest w grze (odniesienia do rozdziałów koncepcji)

| Obszar | Zakres w prototypie |
|---|---|
| Osada (3, 4, 37) | Taras pod skałą, wąwóz z rzeką, mury na zachodzie i południu, brama od szlaku. 23 budynki. Siedziba, stajnia i trzy budynki piechoty mają 30 poziomów i 6 etapów wyglądu (1, 6, 11, 16, 21, 26). Widać rusztowania, dzień i noc, mieszkańców w ruchu. |
| Samouczek (2) | 7 zadań: od studni do otwarcia drogi, uratowanie zwiadowcy Wita, pierwszy napad. |
| Surowce (6) | Jedzenie, drewno, kamień, żelazo, srebro. Mieszkańcy jako pracownicy, utrzymanie armii, chroniona część magazynu. |
| Władca (7) | Postać obracana przeciągnięciem, 6 miejsc wyposażenia, zestawy wojenny i gospodarczy, tytuły od przywódcy ocalałych do księcia. |
| Towarzysze (8) | 6 postaci zdobywanych z historii, zleceń i wydarzeń. Doświadczenie, specjalizacje, próby awansu z kamieniami hartu, skupienia i ducha. Własne wyposażenie. |
| Wojsko (9, 16) | Miecznicy, pikinierzy, łucznicy, kawaleria i tarany. Stopnie I–VI, przeszkalanie, lazaret i ranni. Sześć jednostek fortowych z limitami. |
| Bitwy (10) | Automatyczny silnik rund: przewagi jednostek, linie (front, strzelcy, kawaleria), teren, taktyki, dowódca i pomocnik, mury, wieże i tarany. Raport z przyczynami wyniku, np. „Pikinierzy zatrzymali szarżę kawalerii”. |
| Obrona (11) | Napady także offline, ostrzeżenie przed atakiem, dowódca obrony, tryby wież, posiłki sojuszu, rabunek niechronionych zasobów, uszkodzenia murów, ochrona początkowa. |
| Mapa (12, 13) | 48×48 pól, 9 regionów, mgła i zwiad, przeciwnicy 6 rodzajów, złoża do zbierania, znaleziska, mosty do odbudowy (skracają marsze), wielka bestia. |
| Tablica (14) i energia (15) | 3 zlecenia co 8 h (limit 9), 4 rodzaje zadań, łańcuchy fabularne. Pasek 240 punktów, 1 punkt co 6 minut, rezerwacja i zwrot przy zawróceniu. |
| Forty i korona (16, 17) | 3 forty w oknach walk, centralny zamek, Wojna o Koronę co 14 dni, tytuł króla na 7 dni. |
| Sojusz (18–22) | Dołączenie lub własny sojusz, role, limit 40→100, 9 badań po 5 poziomów, wkład i monety, pomoc, posiłki, zgrupowania, terytorium ze strażnicami, sklep z limitami. |
| Badania (23) | Akademia: Wojsko, Surowce oraz Ekonomia i administracja (30 badań). |
| Wydarzenia (24) | Obrona Pogranicza (fale), Wyprawa Zakonu (wiwerna), Wojna o Koronę, Szlaki Karawan. Tygodniowy budżet 80 rubinów. |
| VIP (25) | 15 poziomów według tabeli (łącznie 3 165 000), 500 dziennie, nagrody wyłącznie kosmetyczne. |
| Sklepy (26, 32–36) | Tryb testowy bez płatności: rubiny, przepustka, energia (30/dzień, 210/tydzień), wyglądy osady. Łupy z potworów według tabel z rozdziału 33. |
| Arena (35) | Od siedziby 10. Drużyny do 1000 jednostek, 5 prób dziennie plus 3 dokupione na sezon, ligi, tygodniowy sezon, nagrody, sklep żetonów. |
| Chwała (31) | Pula za walki PvP, podział 70/30, malejące nagrody za powtórki, spadek 0,05% dziennie, 6 tytułów. |
| Komunikacja (27) | Czat ogólny, sojuszniczy, prywatny i grupy, blokowanie i zgłaszanie, ograniczenie spamu. |

## Balans

Wszystkie wartości oznaczone w koncepcji jako **Otwarte** zostały dobrane roboczo
i zebrane w jednym pliku: **`js/config.js`**. Wartości przyjęte w dokumencie
(energia, VIP, sojusz, arena, chwała, łupy) są przeniesione bez zmian.
Wzory produkcji, pojemności i mieszkańców są w `js/core.js` (`P.eco`).

## Struktura

```
index.html      – szkielet strony
css/style.css   – wygląd (telefon i komputer)
js/config.js    – balans i dane (budynki, jednostki, badania, tabele)
js/core.js      – stan gry, czas, gospodarka, budowa, badania, zapis
js/combat.js    – silnik automatycznych bitew i raporty przyczyn
js/army.js      – wojsko, lazaret, towarzysze, kuźnia, władca
js/world.js     – mapa, marsze, przeciwnicy, napady, forty, korona
js/systems.js   – tablica, zadania, sojusz, arena, VIP, chwała, wydarzenia, sklep, czat
js/city.js      – rysunek osady (SVG) z etapami budynków
js/mapview.js   – rysunek mapy świata (canvas)
js/ui.js        – interfejs: pasek, osada, okna budynków, mapa, marsze
js/pages.js     – pozostałe ekrany
js/main.js      – start gry i pętla czasu
```

## Publikacja

Workflow `.github/workflows/pages.yml` publikuje grę na GitHub Pages po każdym
pushu na `main` (włącz *Settings → Pages → Source: GitHub Actions*). Na Androida
grę można później zapakować w Capacitor.
