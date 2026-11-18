# Składa miasto z elementów w modele3d/export/mapa/ według uklad.json:
# teren, 3 mury (lewy, przod, prawy), brama i 2 wieże narożne – każdy element w swoim poziomie.
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
var _wezly := {}   # klucz elementu -> instancja sceny


func _ready() -> void:
	var f := FileAccess.open(mapa_dir + "/uklad.json", FileAccess.READ)
	uklad = JSON.parse_string(f.get_as_text())
	add_child((load(mapa_dir + "/" + uklad["teren"]["plik"]) as PackedScene).instantiate())
	for strona in uklad["mury"]:
		_postaw("mur_" + strona, uklad["mury"][strona], poziom_murow[strona])
	_postaw("brama", uklad["brama"], poziom_bramy)
	_odswiez_narozniki()


func _postaw(klucz: String, opis: Dictionary, poziom: int) -> Node3D:
	if _wezly.has(klucz):
		_wezly[klucz].queue_free()
	var plik: String = opis["plik"].replace("{poziom}", str(poziom))
	var n: Node3D = (load(mapa_dir + "/" + plik) as PackedScene).instantiate()
	var p: Array = opis["pozycja"]
	n.position = Vector3(p[0], p[1], p[2])
	n.rotation_degrees.y = opis["obrot_y_stopnie"]
	add_child(n)
	_wezly[klucz] = n
	return n


func _odswiez_narozniki() -> void:
	var i := 0
	for nz in uklad["narozniki"]:
		var poz := 1
		for s in nz["poziom_jak_wyzszy_z"]:
			poz = max(poz, poziom_murow[s])
		_postaw("naroznik_%d" % i, nz, poz)
		i += 1


## Ulepszenie (lub zmiana) poziomu jednego muru: "lewy", "przod" albo "prawy".
func ustaw_poziom_muru(strona: String, poziom: int) -> void:
	poziom_murow[strona] = poziom
	_postaw("mur_" + strona, uklad["mury"][strona], poziom)
	_odswiez_narozniki()


func ustaw_poziom_bramy(poziom: int) -> void:
	poziom_bramy = poziom
	_postaw("brama", uklad["brama"], poziom)


## Pozycje (globalne) miejsc dla obrońców na danym elemencie: "lewy", "przod", "prawy", "brama".
func miejsca_obroncow(element: String) -> Array[Vector3]:
	var klucz := "brama" if element == "brama" else "mur_" + element
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
