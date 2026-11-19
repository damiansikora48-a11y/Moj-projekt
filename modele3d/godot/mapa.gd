# Składa miasto z elementów w modele3d/export/mapa/ według uklad.json:
# teren, 3 mury (lewy, przod, prawy), brama i 2 wieże narożne – każdy element w swoim poziomie
# ulepszenia (1–15). Poziom wskazuje etap wyglądu (uklad.json: "poziomy"); wygląd zmienia się co 3 poziomy.
# Na etapie 1 (palisada, poziomy 1–3) mury nie mają miejsc dla obrońców.
#
# Użycie: węzeł Node3D z tym skryptem; pliki z export/mapa/ skopiuj do `mapa_dir`.
#   ustaw_poziom_muru("przod", 3)      # ulepszenie muru przedniego do poziomu 3
#   ustaw_poziom_bramy(2)
#   miejsca_obroncow("lewy")           # -> Array[Vector3] pozycji dla obrońców na murze
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


func _postaw(klucz: String, opis: Dictionary, poziom: int) -> Node3D:
	if _wezly.has(klucz):
		_wezly[klucz].queue_free()
	var etap: int = uklad["poziomy"][str(poziom)]["etap"]
	var plik: String = opis["plik"].replace("{etap}", str(etap))
	var n: Node3D = (load(mapa_dir + "/" + plik) as PackedScene).instantiate()
	var p: Array = opis["pozycja"]
	n.position = Vector3(p[0], p[1], p[2])
	n.rotation_degrees.y = opis["obrot_y_stopnie"]
	add_child(n)
	_wezly[klucz] = n
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


## Pozycje (globalne) miejsc dla obrońców: "lewy", "przod", "prawy", "brama" albo id wieży.
func miejsca_obroncow(element: String) -> Array[Vector3]:
	var klucz := element if (element == "brama" or poziom_wiez.has(element)) else "mur_" + element
	var out: Array[Vector3] = []
	for dziecko in _wezly[klucz].find_children("obronca_*", "", true, false):
		out.append((dziecko as Node3D).global_position)
	return out


## Działka pod budynek po id (np. "D1"): pozycja i rozmiar z uklad.json.
func dzialka(id: String) -> Dictionary:
	for d in uklad["dzialki"]:
		if d["id"] == id:
			return d
	return {}
