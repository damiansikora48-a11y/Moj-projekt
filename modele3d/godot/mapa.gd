# Składa miasto z elementów w modele3d/export/mapa/ według uklad.json:
# teren, 3 mury (lewy, przod, prawy), brama i 6 wież – każdy element w swoim poziomie
# ulepszenia (1–15). Poziom wskazuje etap wyglądu (uklad.json: "poziomy"); wygląd zmienia się co 3 poziomy.
# Na etapie 1 (palisada, poziomy 1–3) mury nie mają miejsc dla obrońców.
#
# Użycie: węzeł Node3D z tym skryptem; pliki z export/mapa/ skopiuj do `mapa_dir`.
#   ustaw_poziom_muru("przod", 3)      # ulepszenie muru przedniego do poziomu 3
#   ustaw_poziom_bramy(2)
#   miejsca_obroncow("lewy")           # -> Array[Vector3] pozycji dla obrońców na murze
#   ustaw_uszkodzenie("przod", 0.35)   # wytrzymałość 0–1 -> widoczne uszkodzenia (gruz, dziury, wyłom)
#   wylom("przod")                     # -> Vector3 środka wyłomu albo null (gdy mur nie jest przebity)
#   ustaw_poziom_budynku_dzialki("kuznia", 5)   # kuznia / koszary / budynek_fuzji / magazyn / akademia: 1–20
#   tablica_ogloszen()                 # -> Node3D tablicy przy studni (np. do kliknięcia i dymka „!”)
#
# USZKODZENIA: każdy .glb muru/bramy/wieży ma warstwy (węzły) *_znika_k, *_pojawia_k, *_pokaz_a_b,
# które pokazujemy zależnie od stanu 0–3 (progi w uklad.json "uszkodzenia"). Dym w ruchu warto dodać
# cząsteczkami (GPUParticles3D) w miejscach ognia – modele mają tylko płonące szczątki.
#
# UWAGA: napisany pod Godot 4.x, nie był uruchamiany w edytorze – sprawdź przy pierwszym imporcie.
class_name Miasto
extends Node3D

@export var mapa_dir: String = "res://mapa"

var uklad: Dictionary
var poziom_murow := {"lewy": 1, "przod": 1, "prawy": 1}
var poziom_bramy := 1
var poziom_wiez := {}   # id wieży -> poziom (6 wież z uklad.json "wieze")
var poziom_budynku := 1
var poziom_budynkow := {}  # id budynku z działki (uklad.json "budynki") -> poziom 1–20
var stan_uszkodzen := {}   # klucz elementu -> stan 0 cały, 1 lekko, 2 mocno uszkodzony, 3 wyłom
var _wezly := {}   # klucz elementu -> instancja sceny


func _ready() -> void:
	var f := FileAccess.open(mapa_dir + "/uklad.json", FileAccess.READ)
	uklad = JSON.parse_string(f.get_as_text())
	add_child((load(mapa_dir + "/" + uklad["teren"]["plik"]) as PackedScene).instantiate())
	for w in uklad["wieze"]:
		poziom_wiez[w["id"]] = 1
	for strona in uklad["mury"]:
		_postaw("mur_" + strona, uklad["mury"][strona], poziom_murow[strona])
	_postaw("brama", uklad["brama"], poziom_bramy)
	_odswiez_narozniki()
	ustaw_poziom_budynku(poziom_budynku)
	for b in uklad["budynki"]:
		ustaw_poziom_budynku_dzialki(b["id"], 1)
	var t: Dictionary = uklad["tablica_ogloszen"]
	_postaw("tablica_ogloszen", t, 1)


func _postaw(klucz: String, opis: Dictionary, poziom: int) -> Node3D:
	if _wezly.has(klucz):
		_wezly[klucz].queue_free()
	var plik: String = opis["plik"]
	if plik.contains("{etap}"):
		plik = plik.replace("{etap}", str(uklad["poziomy"][str(poziom)]["etap"]))
	elif plik.contains("{poziom:02}"):
		plik = plik.replace("{poziom:02}", "%02d" % poziom)
	var n: Node3D = (load(mapa_dir + "/" + plik) as PackedScene).instantiate()
	var p: Array = opis["pozycja"]
	n.position = Vector3(p[0], p[1], p[2])
	n.rotation_degrees.y = opis["obrot_y_stopnie"]
	add_child(n)
	_wezly[klucz] = n
	_pokaz_uszkodzenia(klucz)   # po ulepszeniu nowy model dostaje ten sam stan uszkodzeń
	return n


func _odswiez_narozniki() -> void:
	for w in uklad["wieze"]:
		_postaw(w["id"], w, poziom_wiez[w["id"]])


## Ulepszenie (lub zmiana) poziomu jednego muru: "lewy", "przod" albo "prawy" (poziom 1–15).
func ustaw_poziom_muru(strona: String, poziom: int) -> void:
	poziom_murow[strona] = poziom
	_postaw("mur_" + strona, uklad["mury"][strona], poziom)


## Ulepszenie jednej z 6 wież (poziom 1–15), niezależnie od murów: "wieza_przod_lewa", "wieza_przod_prawa",
## "wieza_tyl_lewa", "wieza_tyl_prawa", "wieza_brama_lewa", "wieza_brama_prawa".
func ustaw_poziom_wiezy(id: String, poziom: int) -> void:
	poziom_wiez[id] = poziom
	_odswiez_narozniki()


func ustaw_poziom_bramy(poziom: int) -> void:
	poziom_bramy = poziom
	_postaw("brama", uklad["brama"], poziom)


## Budynek główny na skalnej półce: poziom 1–20, każdy poziom coś zmienia (opis: uklad.json "zmiany").
func ustaw_poziom_budynku(poziom: int) -> void:
	poziom_budynku = poziom
	var b: Dictionary = uklad["budynek_glowny"]
	if _wezly.has("budynek_glowny"):
		_wezly["budynek_glowny"].queue_free()
	var plik: String = "budynek_glowny_poz%02d.glb" % poziom
	var n: Node3D = (load(mapa_dir + "/" + plik) as PackedScene).instantiate()
	var p: Array = b["pozycja"]
	n.position = Vector3(p[0], p[1], p[2])
	add_child(n)
	_wezly["budynek_glowny"] = n


## Budynek na działce ("kuznia", "koszary", "budynek_fuzji"): poziom 1–20, każdy poziom coś zmienia
## (opis zmian: uklad.json "budynki"[...]["zmiany"]). Budynek stoi przodem do placu.
func ustaw_poziom_budynku_dzialki(id: String, poziom: int) -> void:
	for b in uklad["budynki"]:
		if b["id"] == id:
			poziom_budynkow[id] = poziom
			_postaw(id, b, poziom)
			return
	push_warning("Nie ma budynku: " + id)


## Tablica ogłoszeń przy studni – węzeł "tablica_info" w środku tablicy (np. na dymek przy aktualizacji).
func tablica_ogloszen() -> Node3D:
	return _wezly.get("tablica_ogloszen")


func _klucz(element: String) -> String:
	return element if (element == "brama" or poziom_wiez.has(element)) else "mur_" + element


## Pozycje (globalne) miejsc dla obrońców: "lewy", "przod", "prawy", "brama" albo id wieży.
## Miejsca na zawalonych fragmentach (uszkodzenia) są pomijane.
func miejsca_obroncow(element: String) -> Array[Vector3]:
	var out: Array[Vector3] = []
	for dziecko in _wezly[_klucz(element)].find_children("obronca_*", "", true, false):
		if (dziecko as Node3D).is_visible_in_tree():
			out.append((dziecko as Node3D).global_position)
	return out


## Uszkodzenie elementu ("lewy", "przod", "prawy", "brama" albo id wieży) z wytrzymałości 0–1:
## 100–70% cały, 70–40% lekko, 40–1% mocno uszkodzony, 0% wyłom. Naprawa = wyższa wytrzymałość.
func ustaw_uszkodzenie(element: String, wytrzymalosc: float) -> int:
	var stan := 3
	for p in uklad["uszkodzenia"]["progi"]:
		if wytrzymalosc >= float(p["od_wytrzymalosci"]):
			stan = int(p["stan"])
			break
	var klucz := _klucz(element)
	stan_uszkodzen[klucz] = stan
	_pokaz_uszkodzenia(klucz)
	return stan


## Środek wyłomu (globalnie) – tędy wrogowie wchodzą do miasta; null, gdy element nie jest przebity.
func wylom(element: String) -> Variant:
	var klucz := _klucz(element)
	if stan_uszkodzen.get(klucz, 0) < 3:
		return null
	var w := _wezly[klucz].find_child("wylom", true, false) as Node3D
	return w.global_position if w else null


func _pokaz_uszkodzenia(klucz: String) -> void:
	if not _wezly.has(klucz):
		return
	var stan: int = stan_uszkodzen.get(klucz, 0)
	for n in _wezly[klucz].find_children("*", "Node3D", true, false):
		var nazwa := String(n.name)
		if nazwa.contains("_znika_") or nazwa.contains("_pojawia_") or nazwa.contains("_pokaz_"):
			n.visible = _widoczna(nazwa, stan)


static func _widoczna(nazwa: String, stan: int) -> bool:
	if nazwa.contains("_pokaz_"):
		return int(nazwa.right(3).left(1)) <= stan and stan < int(nazwa.right(1))
	var k := int(nazwa.right(1))
	return stan < k if nazwa.contains("_znika_") else stan >= k


## Działka pod budynek po id (np. "D1"): pozycja i rozmiar z uklad.json.
func dzialka(id: String) -> Dictionary:
	for d in uklad["dzialki"]:
		if d["id"] == id:
			return d
	return {}
