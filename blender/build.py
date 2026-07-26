"""Einstieg der Blender-Pipeline. Headless, deterministisch.

    blender -b --factory-startup -P blender/build.py -- --shot 03 --still
    blender -b --factory-startup -P blender/build.py -- --shot 03 --final
    blender -b --factory-startup -P blender/build.py -- --all --still
    blender -b --factory-startup -P blender/build.py -- --list

Es gibt kein handgepflegtes .blend als Wahrheitsquelle. Jede Szene entsteht
aus Python, ist damit reproduzierbar und in Iterationen pruefbar: Still
rendern, ansehen, korrigieren.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from lib import render as render_lib  # noqa: E402

SHOT_DIR = HERE / "shots"
STILL_DIR = PROJECT_ROOT / "renders" / "stills"
VIDEO_DIR = PROJECT_ROOT / "media" / "video"


def argv_after_dashes() -> list[str]:
    """Blender gibt alles nach `--` an das Skript weiter."""
    return sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []


def available_shots() -> dict[str, Path]:
    return {p.name.split("_")[1]: p for p in sorted(SHOT_DIR.glob("shot_*.py"))}


def clear_scene() -> None:
    """Leere Szene. --factory-startup laesst den Wuerfel stehen."""
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build_shot(nummer: str, quality: str, post: bool = True) -> object:
    shots = available_shots()
    if nummer not in shots:
        raise SystemExit(
            f"Shot {nummer} nicht gefunden. Vorhanden: {', '.join(sorted(shots)) or 'keiner'}"
        )

    clear_scene()
    modul = importlib.import_module(f"shots.{shots[nummer].stem}")
    importlib.reload(modul)

    scene = bpy.context.scene
    render_lib.setup_scene(scene, quality)
    if post:
        render_lib.setup_compositor(scene)
    modul.build(scene)
    return modul


def main() -> None:
    parser = argparse.ArgumentParser(description="Sarajevo 1914 - Blender-Pipeline")
    parser.add_argument("--shot", help="Shot-Nummer, z. B. 03")
    parser.add_argument("--all", action="store_true", help="alle Shots")
    parser.add_argument("--list", action="store_true", help="Shots auflisten")
    parser.add_argument("--still", action="store_true", help="ein Standbild")
    parser.add_argument("--preview", action="store_true", help="Video, halbe Qualitaet")
    parser.add_argument("--final", action="store_true", help="Video, Endqualitaet")
    parser.add_argument("--frame", type=int, help="Bildnummer fuer --still")
    parser.add_argument(
        "--raw", action="store_true",
        help="ohne Compositor rendern - trennt Szenenfehler von Post-Fehlern",
    )
    args = parser.parse_args(argv_after_dashes())

    if args.list:
        shots = available_shots()
        print(f"{len(shots)} Shot(s):")
        for nummer, pfad in shots.items():
            print(f"  {nummer}  {pfad.name}")
        return

    quality = "final" if args.final else "preview" if args.preview else "still"
    nummern = sorted(available_shots()) if args.all else [args.shot]
    if not nummern or nummern == [None]:
        raise SystemExit("Bitte --shot NN, --all oder --list angeben.")

    for nummer in nummern:
        t0 = time.perf_counter()
        modul = build_shot(nummer, quality, post=not args.raw)
        scene = bpy.context.scene
        aufbau = time.perf_counter() - t0

        if args.still or not (args.preview or args.final):
            if args.frame is not None:
                scene.frame_set(args.frame)
            else:
                # Bildmitte: dort steht die Komposition, nicht am Anfang.
                scene.frame_set((scene.frame_start + scene.frame_end) // 2)
            ziel = STILL_DIR / f"shot_{nummer}_f{scene.frame_current:04d}.png"
            ziel.parent.mkdir(parents=True, exist_ok=True)
            t1 = time.perf_counter()
            render_lib.write_still(scene, str(ziel))
            print(
                f"Shot {nummer}: Aufbau {aufbau:.1f}s, Render "
                f"{time.perf_counter() - t1:.1f}s -> {ziel}"
            )
        else:
            ziel = VIDEO_DIR / f"shot_{nummer}.mp4"
            ziel.parent.mkdir(parents=True, exist_ok=True)
            frames = scene.frame_end - scene.frame_start + 1
            print(
                f"Shot {nummer}: {frames} Bilder ({frames / render_lib.FPS:.1f}s), "
                f"Aufbau {aufbau:.1f}s -> {ziel}"
            )
            t1 = time.perf_counter()
            render_lib.write_video(scene, str(ziel.with_suffix("")))
            dauer = time.perf_counter() - t1
            print(f"  fertig in {dauer / 60:.1f} min ({dauer / frames:.2f}s pro Bild)")


if __name__ == "__main__":
    main()
