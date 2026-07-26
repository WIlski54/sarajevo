"""Animationshelfer.

Grund fuer diese Datei: seit Blender 4.4 sind Actions "slotted". Die
F-Curves haengen nicht mehr direkt an der Action, sondern in Channelbags
innerhalb von Strips innerhalb von Layers. `action.fcurves` existiert je
nach Version gar nicht mehr und wirft AttributeError.

Weil jeder Shot Keyframes setzt und deren Interpolation kontrolliert,
steht der Zugriff genau einmal hier.
"""

from __future__ import annotations

import bpy


def fcurves(action: bpy.types.Action) -> list:
    """Alle F-Curves einer Action, egal ob klassisch oder slotted."""
    if hasattr(action, "fcurves"):
        return list(action.fcurves)

    gesammelt: list = []
    for layer in getattr(action, "layers", []):
        for strip in getattr(layer, "strips", []):
            for bag in getattr(strip, "channelbags", []):
                gesammelt.extend(bag.fcurves)
    return gesammelt


def object_fcurves(ob: bpy.types.Object) -> list:
    if not ob.animation_data or not ob.animation_data.action:
        return []
    return fcurves(ob.animation_data.action)


def set_interpolation(ob: bpy.types.Object, mode: str = "BEZIER") -> int:
    """Interpolation aller Keyframes eines Objekts. Liefert die Anzahl.

    LINEAR fuer gleichmaessige Fahrten (ein Wagen von 1914 haelt seine
    Geschwindigkeit), BEZIER fuer Kamerabewegungen, die weich an- und
    auslaufen sollen.
    """
    anzahl = 0
    for fc in object_fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = mode
            anzahl += 1
        fc.update()
    return anzahl


def ease(ob: bpy.types.Object, easing: str = "EASE_IN_OUT") -> None:
    """Weiches An- und Auslaufen - Kamerafahrten wirken sonst mechanisch."""
    for fc in object_fcurves(ob):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = easing
        fc.update()


def handheld(ob: bpy.types.Object, staerke: float = 0.012, tempo: float = 1.7) -> None:
    """Gebackenes Handkamera-Rauschen ueber Noise-Modifikatoren.

    Ohne dieses Zittern wirkt jede Kamerafahrt wie ein Industrieroboter.
    Bewusst schwach: es soll unterschwellig bleiben, nicht auffallen.
    """
    for index, fc in enumerate(object_fcurves(ob)):
        if not fc.data_path.endswith(("location", "rotation_euler")):
            continue
        mod = fc.modifiers.new("NOISE")
        mod.strength = staerke * (1.0 if "location" in fc.data_path else 0.6)
        mod.scale = tempo
        mod.phase = index * 7.31  # entkoppelt die Achsen
        mod.depth = 2
