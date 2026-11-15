# Modele 3D jednostek (Godot, styl chunky)

Modele są generowane kodem w Blenderze (`src/`) i eksportowane jako `.glb` do `export/`.

| Plik | Jednostka | Trójkąty | Sloty (części) |
|---|---|---|---|
| `export/soldier.glb` | Żołnierz, ok. 1,9 m | ~22 300 | Head, Helmet, Torso, Cape, Arms, Legs, Weapon, Shield |
| `export/golem.glb` | Golem, ok. 2,3 m | ~5 400 | Body, Head, Arms, Legs |

Podglądy z kamery 52° i innych ujęć są w `podglad/`.

## Import do Godot 4

1. Skopiuj pliki `.glb` do projektu, np. do `res://units/`.
2. Kliknij dwukrotnie plik `.glb` (*Advanced Import Settings*) albo po prostu przeciągnij go na scenę.
3. Animacje `Idle_loop` i `Walk_loop` są w `AnimationPlayer`. Godot rozpoznaje końcówkę `loop` w nazwie i ustawia zapętlenie automatycznie.
4. Animacje są „w miejscu”: postać nie przesuwa się w animacji, ruch robisz w kodzie, np. przez `CharacterBody3D`.

```gdscript
@onready var anim: AnimationPlayer = $Soldier/AnimationPlayer

func _physics_process(delta):
    anim.play("Walk_loop" if velocity.length() > 0.1 else "Idle_loop")
```

Kamera z gry: `Camera3D` z rotacją X = -52°, ustawiona za postacią i nad nią.

## Wspólny szkielet: podstawa pod fuzje jednostek

Każda jednostka ma **te same nazwy kości** (20 kości):

```
root ─ hips ─ spine ─ chest ─ neck ─ head
                 │       └─ shoulder.L/R ─ upper_arm ─ forearm ─ hand
                 └─ thigh.L/R ─ shin ─ foot
```

Różnią się tylko proporcje. Każda część (slot) to osobny `MeshInstance3D`, przypięty sztywno do kości. Dzięki temu:

- animacje mają te same tory dla każdej jednostki, więc można je przenosić między postaciami;
- w Godot można włączać i wyłączać sloty (`visible`) albo podmieniać części, np. broń w `hand.R` przez `BoneAttachment3D`;
- **fuzja** (np. żołnierz + golem) powstanie w generatorze tak: proporcje szkieletu pośrednie, a każdy slot brany od jednego z rodziców, z mieszaną paletą materiałów. Każda nowa jednostka automatycznie daje kombinacje ze wszystkimi poprzednimi.

## Przebudowa modeli

```bash
python3.11 -m venv venv && ./venv/bin/pip install bpy pillow
cd src
../venv/bin/python build.py              # wszystkie jednostki + rendery
../venv/bin/python build.py golem --quick # jedna jednostka, szybki podgląd
../venv/bin/python build.py --no-render   # tylko eksport .glb
```

- `src/kit.py`: narzędzia (prymitywy, szkielet, animacje, eksport, render)
- `src/units.py`: definicje jednostek (proporcje, kolory, części, parametry chodu)
- `src/build.py`: budowa, eksport i podglądy
