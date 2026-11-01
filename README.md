# 🐝 Nectar Kingdom / Królestwo Nektaru

Prosta, wciągająca gra **idle / incremental** w przeglądarce. Gracz klika ul, zatrudnia pszczoły i rozbudowuje imperium miodu: od jednej robotnicy aż po galaktyczny rój. Gra działa także, gdy gracz jest offline.

Napisana w czystym HTML, CSS i JavaScript, bez bibliotek i bez kroku budowania. Wystarczy otworzyć `index.html`.

## Co jest w grze

| Mechanika | Po co jest |
|---|---|
| Klikanie ula | Szybki start i satysfakcja na początku gry |
| 12 rodzajów producentów (koszt rośnie o 14% za sztukę) | Główna pętla „kup, produkuj więcej, kup więcej” |
| ok. 90 ulepszeń (×2 dla producentów, kliknięć i całej produkcji) | Stałe cele i skoki mocy |
| 68 trofeów (+1% produkcji za każde) | Kolekcjonowanie |
| Złote pszczoły (losowo co 1–3 minuty: bonus, szał ×7 albo szał klikania ×10) | Powód, żeby zaglądać do gry |
| **Mleczko Pszczele (prestiż)**: reset za trwały bonus +3% za sztukę | Gra na tygodnie, a nie na godzinę |
| Przywileje Królowej (5 trwałych drzewek za Mleczko) | Decyzje: wydać czy trzymać dla bonusu |
| Postęp offline (do 8 h, 50% wydajności, rozszerzane przywilejami) | Gracz wraca, żeby odebrać miód |
| Zapis automatyczny co 10 s, eksport i import zapisu | Gracz nie traci postępu |
| Język EN / PL (wykrywany automatycznie) | Rynek globalny |
| Responsywny układ | Telefon i komputer |

Balans gry (ceny, produkcja, progi) jest w jednym pliku: `js/data.js`.

## 💰 Jak zarabia: reklamy z nagrodą

W grze są dwa miejsca na reklamy z nagrodą, czyli reklamy, które gracz **sam chce** obejrzeć:
1. **„📺 x2 na 10 min”**: podwaja produkcję (przycisk na górze ekranu).
2. **„📺 Podwój!”**: podwaja zarobek offline po powrocie do gry.

Do tego dochodzi reklama przerywnikowa (interstitial) po prestiżu, najwyżej raz na 3 minuty.

Cała obsługa reklam jest w `js/ads.js`. Bez podłączonego SDK gra symuluje 3-sekundową reklamę, więc możesz przetestować cały przebieg.

### Plan publikacji (od najłatwiejszego)

1. **GitHub Pages** (darmowy hosting, do testów i pokazywania znajomym)
   W repozytorium jest workflow `.github/workflows/pages.yml`. Włącz *Settings → Pages → Source: GitHub Actions*. Każdy push na `main` opublikuje grę.
2. **CrazyGames** (crazygames.com/developers): duży ruch, podział przychodu z reklam.
   Dodaj w `index.html` przed `js/ads.js`:
   ```html
   <script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>
   ```
   `ads.js` sam wykryje SDK i zacznie wyświetlać prawdziwe reklamy.
3. **Poki** (poki.com/developers) i **GameDistribution**: podobny model. Dopisz nową gałąź w `ads.js`.
4. **itch.io**: spakuj folder do ZIP i wgraj jako grę HTML. Dochód z dobrowolnych wpłat.
5. **Android (Google Play)**: zapakuj grę w Capacitor i podłącz AdMob (reklamy z nagrodą). To zwykle najbardziej dochodowa opcja dla gier idle.

> Realnie: dochód pasywny zależy od liczby graczy. Gra jest gotowym fundamentem. Największy wpływ na zarobki mają publikacja na portalach z ruchem i dopracowanie balansu na podstawie tego, jak długo gracze zostają w grze.

## Uruchomienie lokalne

```bash
# wystarczy otworzyć index.html, albo:
python3 -m http.server 8000   # → http://localhost:8000
```

## Struktura

```
index.html        – układ strony
css/style.css     – wygląd
js/i18n.js        – tłumaczenia EN/PL
js/ads.js         – warstwa reklam (CrazyGames / tryb dev)
js/data.js        – balans: producenci, ulepszenia, przywileje, trofea
js/game.js        – logika gry, zapis, offline, render
```

## Pomysły na kolejne wersje
- Dźwięki i muzyka (z opcją wyciszenia)
- Codzienna nagroda za logowanie
- Sezonowe wydarzenia (np. zimowy ul)
- Drugi poziom prestiżu
- Tabela wyników
