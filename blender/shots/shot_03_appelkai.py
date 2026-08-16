"""Shot 03 - Die Kolonne fährt über den Appelkai.

Erster von drei Shots in Beat 2. Etabliert Ort und Personen: die
Uferstrasse, die Menge, und den Wagen des Thronfolgerpaars, das hier zum
ersten Mal deutlich zu sehen ist.

17 Sekunden bei 30 Bildern.
"""

from __future__ import annotations

import math

import bpy

from lib import anim, orte, props

DAUER_S = 17
FPS = 30

# Die Kolonne faehrt AUF DIE KAMERA ZU (von +X nach -X).
#
# Im ersten Entwurf fuhr sie weg - man sah drei Wagen von hinten und vom
# Thronfolgerpaar nichts. Genau darauf kommt es hier aber an: dass man
# sieht, WESSEN Wagen das Ziel ist.
KOLONNE_VON = 55.0
KOLONNE_BIS = -25.0

KAMERA_XY = (-34.0, -4.6)


def _kolonne(m, frames):
    """Drei offene Wagen, entgegenkommend. Der mittlere traegt das Paar.

    Der Abstand zwischen den Wagen ist bewusst gross: auf historischen
    Aufnahmen liegen mehrere Laengen dazwischen, und genau dieser Abstand
    ist der Grund, warum die Granate unter dem NACHFOLGENDEN Wagen
    detonierte statt unter dem des Thronfolgers.
    """
    konvoi, wagen = props.kolonne("Kolonne", m)
    konvoi.location = (KOLONNE_VON, 0, 0)
    konvoi.keyframe_insert("location", frame=1)
    konvoi.location = (KOLONNE_BIS, 0, 0)
    konvoi.keyframe_insert("location", frame=frames)
    # LINEAR: konstante Geschwindigkeit. 80 m in 17 s sind 4,7 m/s, also
    # rund 17 km/h - Schritttempo einer Kolonne, die von einer Menge
    # gesaeumt wird. Ein Bezier-Auslauf wuerde sie am Bildrand
    # unnatuerlich abbremsen lassen.
    anim.set_interpolation(konvoi, "LINEAR")
    return konvoi, wagen


def _kamera(scene, frames):
    """Leichte Mitfahrt auf Augenhoehe eines Zuschauers am Kai.

    Kein Kran, kein Drohnenblick: der Beat soll wirken, als staende man
    selbst in der Menge.
    """
    # 2,05 m statt 1,75: von Augenhoehe schaute man dem Wagen frontal auf
    # die Bordwand, von hier leicht hinein - und dort sitzt das Paar.
    bpy.ops.object.camera_add(location=(KAMERA_XY[0], KAMERA_XY[1], 2.05))
    kamera = bpy.context.active_object
    kamera.name = "Kamera"
    scene.camera = kamera
    # 55 statt 42 mm: bei 42 mm blieb das Paar auch beim naechsten
    # Vorbeifahren zu klein. Die laengere Brennweite verdichtet ausserdem
    # die Fassadenzeile, was der Strasse gut steht.
    kamera.data.lens = 55
    kamera.data.dof.use_dof = True
    kamera.data.dof.aperture_fstop = 2.8

    ziel = bpy.data.objects.new("Kameraziel", None)
    bpy.context.collection.objects.link(ziel)
    ziel.location = (30, 1.2, 1.5)

    schauen = kamera.constraints.new("TRACK_TO")
    schauen.target = ziel
    schauen.track_axis = "TRACK_NEGATIVE_Z"
    schauen.up_axis = "UP_Y"
    kamera.data.dof.focus_object = ziel

    kamera.location = (KAMERA_XY[0], KAMERA_XY[1], 2.05)
    kamera.keyframe_insert("location", frame=1)
    kamera.location = (KAMERA_XY[0] + 10, KAMERA_XY[1] - 0.4, 2.02)
    kamera.keyframe_insert("location", frame=frames)
    anim.ease(kamera)
    anim.handheld(kamera)

    # Das Ziel wandert der Kolonne entgegen: erst weit die Strasse hinauf,
    # dann mit dem Thronfolgerwagen heran und an der Kamera vorbei.
    ziel.location = (30, 1.2, 1.5)
    ziel.keyframe_insert("location", frame=1)
    ziel.location = (2, 1.2, 1.5)
    ziel.keyframe_insert("location", frame=int(frames * 0.72))
    ziel.location = (-14, 1.2, 1.5)
    ziel.keyframe_insert("location", frame=frames)
    anim.ease(ziel)


def build(scene: bpy.types.Scene) -> None:
    frames = DAUER_S * FPS
    scene.frame_start = 1
    scene.frame_end = frames

    m = orte.standard_materialien()
    orte.appelkai(scene, m, kamera_xy=KAMERA_XY)
    _kolonne(m, frames)
    _kamera(scene, frames)
