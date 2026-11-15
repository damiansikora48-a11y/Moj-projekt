# Modele 3D jednostek (Godot, styl chunky)

Modele są generowane kodem w Blenderze (`src/`) i eksportowane jako `.glb` do `export/`.

| Plik | Jednostka | Atak | Sloty (części) |
|---|---|---|---|
| `soldier.glb` | Żołnierz, ok. 1,9 m | `Attack`: cięcie mieczem | Head, Helmet, Torso, Cape, Arms, Legs, Weapon, Shield |
| `golem.glb` | Golem, ok. 2,3 m | `Throw`: rzut głazem | Body, Head, Arms, Legs, Rock |
| `hybrid.glb` | **Kamienny Rycerz** (fuzja), ok. 2,1 m | `Slam`: uderzenie w ziemię + kryształowe kolce | Body, Head, Cape, Arms, Legs, Weapon |
| `golem_rock.glb` | pocisk golema (bez szkieletu) | | |
| `hybrid_spikes.glb` | efekt ataku hybrydy (bez szkieletu) | | |
| `units.json` | czasy ataków, nazwy animacji, pliki pocisków i efektów | | |

Każda jednostka ma animacje `Idle_loop`, `Walk_loop` i swój atak. Podglądy z kamery 52°, w chodzie i w fazach ataku są w `podglad/`.

## Kamienny Rycerz: jak powstała fuzja

`src/fusion.py`:
1. **Proporcje** wyliczone automatycznie: 45% drogi od żołnierza do golema (`fuse_skeleton`).
2. **Materiały** z obu rodziców (`fuse_palette`): stal, złoto i tabard żołnierza oraz kamień, mech, runy i kryształy golema.
3. **Części mieszane**:
   - kamienna głowa golema w hełmie rycerza, z pęknięciem, przez które świeci runa, i grzebieniem z kryształów zamiast pióropusza;
   - kamienny tors z wtopionym napierśnikiem, popękanym runami, herb z kryształem;
   - prawe ramię rycerskie (stalowy naramiennik, kolczuga), lewe ramię golemowe (głaz z mchem spięty stalową obręczą); oba przedramiona kamienne;
   - nogi golema ze stalowymi nakolannikami i nagolennikami;
   - **Runiczne Ostrze**: kamienny miecz z kryształowymi krawędziami.
4. **Atak mieszany `Slam`**: rycerskie uderzenie mieczem oburącz (styl żołnierza), po którym z ziemi wyrastają kryształowe kolce (moc golema).

## Import do Godot 4

1. Skopiuj pliki `.glb` do projektu, np. do `res://units/`.
2. Przeciągnij `.glb` na scenę. Animacje są w `AnimationPlayer`. Godot rozpoznaje `loop` w nazwie i zapętla `Idle_loop` i `Walk_loop`, a ataki odtwarzają się raz.
3. Animacje są „w miejscu”: ruch robisz w kodzie, np. przez `CharacterBody3D`.
4. Kamera z gry: `Camera3D` z rotacją X = -52°.

### Moment trafienia (z `units.json`)

| Jednostka | Animacja | Długość | Zdarzenie | Czas |
|---|---|---|---|---|
| Żołnierz | `Attack` | 1,00 s | `hit`: zadaj obrażenia | 0,45 s |
| Golem | `Throw` | 2,00 s | `release`: wystrzel `golem_rock.glb` z kości `prop.R` | 1,24 s |
| Kamienny Rycerz | `Slam` | 1,60 s | `impact`: postaw `hybrid_spikes.glb` przed jednostką | 0,83 s |

Kamień w dłoni golema jest przypięty do kości `prop.R`. Animacja sama go pokazuje (gdy golem chwyta) i chowa w chwili rzutu, więc pocisk wystarczy wystrzelić w tym samym momencie.

```gdscript
# Przykład: atak golema
@onready var anim: AnimationPlayer = $Golem/AnimationPlayer
@onready var skel: Skeleton3D = $Golem/Golem_Rig/Skeleton3D
const ROCK := preload("res://units/golem_rock.glb")

func attack(target: Vector3) -> void:
    anim.play("Throw")
    await get_tree().create_timer(1.24).timeout   # units.json: attack_event_time_s
    var rock := ROCK.instantiate()
    get_tree().current_scene.add_child(rock)
    var bone := skel.find_bone("prop.R")
    rock.global_transform = skel.global_transform * skel.get_bone_global_pose(bone)
    # ...nadaj prędkość w stronę `target` (np. RigidBody3D albo własny tween po łuku)
```

```gdscript
# Przykład: efekt hybrydy - 3 kępy kolców w linii, wyrastające jedna po drugiej
const SPIKES := preload("res://units/hybrid_spikes.glb")

func slam() -> void:
    anim.play("Slam")
    await get_tree().create_timer(0.83).timeout
    for i in 3:
        var s := SPIKES.instantiate()
        get_tree().current_scene.add_child(s)
        s.global_position = global_position - global_basis.z * (1.2 + 0.8 * i)
        s.scale = Vector3(1, 0.01, 1)
        create_tween().tween_property(s, "scale", Vector3.ONE, 0.15)
        await get_tree().create_timer(0.08).timeout
```

Uwaga: przód postaci w Godot to oś +Z modelu. Jeśli węzeł postaci jest obrócony inaczej, dopasuj kierunek w przykładzie.

## Wspólny szkielet

Każda jednostka ma **te same nazwy kości** (21 kości). Różnią się tylko proporcje:

```
root ─ hips ─ spine ─ chest ─ neck ─ head
                 │       └─ shoulder.L/R ─ upper_arm ─ forearm ─ hand  (hand.R ─ prop.R)
                 └─ thigh.L/R ─ shin ─ foot
```

Każda część (slot) to osobny `MeshInstance3D`, przypięty sztywno do kości. Kolejne fuzje robi się tak samo jak Kamiennego Rycerza: `fuse_skeleton` + `fuse_palette` + wybór slotów od rodziców lub nowe części mieszane + własny atak z pozami kluczowymi (`keys` w definicji ataku).

## Przebudowa modeli

```bash
python3.11 -m venv venv && ./venv/bin/pip install bpy pillow
cd src
../venv/bin/python build.py               # wszystko + rendery
../venv/bin/python build.py hybrid --quick # jedna jednostka, szybki podgląd
../venv/bin/python build.py --no-render    # tylko eksport .glb
python3 pack_viewer.py podglad.html        # samodzielny podgląd 3D z osadzonymi modelami
```

- `src/kit.py`: narzędzia (prymitywy, szkielet, animacje, pozy kluczowe, eksport, render)
- `src/units.py`: żołnierz i golem (proporcje, kolory, części, chód, ataki)
- `src/fusion.py`: mechanizm fuzji i Kamienny Rycerz
- `src/build.py`: budowa, eksport, `units.json` i podglądy
