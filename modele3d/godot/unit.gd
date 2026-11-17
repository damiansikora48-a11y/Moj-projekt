# Jeden skrypt dla KAŻDEJ jednostki. Wszystko, co różni jednostki (plik modelu, nazwy
# animacji, moment trafienia, pocisk/efekt), czyta z units.json – nowa jednostka nie
# wymaga nowego kodu.
#
# Użycie: dodaj węzeł Node3D, podepnij ten skrypt, ustaw `unit_id` (np. "golem").
# Pliki z modele3d/export/ (lub wydanie/<wersja>/) skopiuj do `units_dir`.
#
# UWAGA: skrypt napisany pod Godot 4.x, ale nie był uruchamiany w edytorze –
# sprawdź go przy pierwszym imporcie (zwłaszcza ścieżkę do Skeleton3D).
class_name Unit
extends Node3D

## Emitowany w chwili trafienia / wyrzutu / uderzenia (zdarzenie z units.json: hit, release, impact).
signal attack_event(unit: Unit, event_name: String)

@export var unit_id: String = "zolnierz"
@export var units_dir: String = "res://units"

var data: Dictionary
var model: Node3D
var anim: AnimationPlayer
var skeleton: Skeleton3D
var attacking := false

static var _all_units: Dictionary = {}


static func load_units(dir: String) -> Dictionary:
	if _all_units.is_empty():
		var f := FileAccess.open(dir + "/units.json", FileAccess.READ)
		_all_units = JSON.parse_string(f.get_as_text())
	return _all_units


func _ready() -> void:
	data = load_units(units_dir)[unit_id]
	model = (load(units_dir + "/" + data["plik"]) as PackedScene).instantiate()
	add_child(model)
	anim = model.find_child("AnimationPlayer", true, false)
	skeleton = model.find_child("Skeleton3D", true, false)
	idle()


func idle() -> void:
	anim.play(data["animacje"]["idle"])


func walk() -> void:
	if not attacking and not dead:
		anim.play(data["animacje"]["walk"])


var dead := false

## Krótka reakcja na trafienie (nie przerywa ataku).
func take_hit() -> void:
	if dead or attacking:
		return
	anim.play(data["animacje"]["hit"])
	await anim.animation_finished
	if not dead and not attacking:
		idle()


## Śmierć: animacja kończy się na leżącej postaci (nie jest zapętlona).
func die() -> void:
	if dead:
		return
	dead = true
	attacking = false
	anim.play(data["animacje"]["death"])


## Atak w stronę punktu `target` (pozycja globalna).
func attack(target: Vector3) -> void:
	if attacking or dead:
		return
	attacking = true
	var a: Dictionary = data["atak"]
	look_at(Vector3(target.x, global_position.y, target.z), Vector3.UP, true)
	anim.play(data["animacje"]["attack"])
	await get_tree().create_timer(a["moment_s"]).timeout
	attack_event.emit(self, a["zdarzenie"])
	match a["typ"]:
		"pocisk":
			_spawn_projectile(a, target)
		"obszar":
			_spawn_area(a)
		_:
			pass  # atak wręcz: obrażenia zadaje gra w reakcji na attack_event
	await anim.animation_finished
	attacking = false
	idle()


func _spawn_projectile(a: Dictionary, target: Vector3) -> void:
	var rock: Node3D = (load(units_dir + "/" + a["plik_efektu"]) as PackedScene).instantiate()
	get_tree().current_scene.add_child(rock)
	var bone := skeleton.find_bone(a["kosc_startowa"])
	rock.global_position = (skeleton.global_transform * skeleton.get_bone_global_pose(bone)).origin
	rock.look_at(target, Vector3.UP, true)  # przód pocisku (+Z) w stronę celu – np. ogon kuli ognia z tyłu
	# Prosty lot po łuku; w grze podmień na RigidBody3D albo własny pocisk z kolizją.
	var start := rock.global_position
	var t := create_tween()
	t.tween_method(func(k: float):
		rock.global_position = start.lerp(target, k) + Vector3.UP * sin(k * PI) * 1.5,
		0.0, 1.0, 0.7)
	t.tween_callback(rock.queue_free)


func _spawn_area(a: Dictionary) -> void:
	# 3 kępy w linii przed jednostką, jedna po drugiej (patrz "uwagi" w units.json).
	var scene := load(units_dir + "/" + a["plik_efektu"]) as PackedScene
	var forward := global_basis.z  # przód modelu to +Z
	for i in 3:
		var fx: Node3D = scene.instantiate()
		get_tree().current_scene.add_child(fx)
		fx.global_position = global_position + forward * (1.2 + 0.8 * i)
		fx.scale = Vector3(1, 0.01, 1)
		var t := create_tween()
		t.tween_property(fx, "scale", Vector3.ONE, 0.15)
		t.tween_interval(1.2)
		t.tween_property(fx, "scale", Vector3(1, 0.01, 1), 0.3)
		t.tween_callback(fx.queue_free)
		await get_tree().create_timer(0.08).timeout
