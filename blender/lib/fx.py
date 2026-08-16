"""Sichtbare Effekte: Funken, Rauch, Staub, Blitze.

Grundsatz dieser Datei: die Aktion muss LESBAR sein. Eine geworfene
Granate, die nur ein dunkler Punkt vor einer dunklen Strasse ist, erzaehlt
nichts - erst die Rauchfahne macht die Flugbahn sichtbar. Deshalb sind
alle Effekte hier eher zu deutlich als zu subtil.

Technik: keine Partikelsysteme, sondern animierte Einzelobjekte mit
Emission oder Volumen. Das ist in Eevee schneller, deterministisch und
laesst sich Bild fuer Bild genau setzen - bei einer Detonation, die auf
einem Ton sitzen muss, ist das entscheidend.
"""

from __future__ import annotations

import math
import random

import bpy


def _emission(name: str, farbe, staerke: float) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    em = tree.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*farbe, 1)
    em.inputs["Strength"].default_value = staerke
    aus = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(em.outputs["Emission"], aus.inputs["Surface"])
    return mat


def _rauch_material(name: str, farbe=(0.42, 0.40, 0.38), dichte: float = 3.0):
    """Volumen. NUR fuer grosse Wolken - siehe _puff_material.

    Grosse BLENDED-Flaechen verschleiern in Eevee den ganzen Himmel, auch
    bei kleinem Alpha; ein Volumen-Shader hat das Problem nicht.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    vol = tree.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (*farbe, 1)
    vol.inputs["Density"].default_value = dichte
    vol.inputs["Anisotropy"].default_value = 0.2
    aus = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(vol.outputs["Volume"], aus.inputs["Volume"])
    return mat


def _puff_material(name: str, farbe=(0.30, 0.29, 0.27), alpha: float = 0.22):
    """Opakes Material fuer KLEINE Rauchbaellchen.

    Eevee berechnet Volumen in grober Froxel-Aufloesung. Bei einer Kugel
    von 30 cm Durchmesser sieht man genau dieses Raster: die Rauchfahne der
    geworfenen Granate rendert als gepunktetes Kloetzchenmuster statt als
    Rauch. Kleine opake Kugeln haben das Problem nicht und lesen sich aus
    jeder Entfernung als Rauch, solange sie in Gruppen auftreten.

    Volumen bleibt den grossen Wolken vorbehalten, wo das Raster im
    Verhaeltnis zur Groesse nicht auffaellt.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*farbe, 1)
    bsdf.inputs["Roughness"].default_value = 1.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.0

    # Durchscheinend, sonst liest sich die Fahne als weisser Festkoerper -
    # im ersten Versuch lag eine massive Wurst ueber dem halben Bild.
    bsdf.inputs["Alpha"].default_value = alpha
    # Die Eigenschaft heisst je nach Version anders; beide Wege versuchen.
    for attr, wert in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        if hasattr(mat, attr):
            try:
                setattr(mat, attr, wert)
            except (TypeError, ValueError):
                pass
    if hasattr(mat, "show_transparent_back"):
        mat.show_transparent_back = False
    return mat


def _skaliere(ob, frame_an, frame_voll, frame_aus, gross: float, klein: float = 0.001):
    """Einblenden ueber die Groesse. Vorher und nachher unsichtbar klein.

    Ueber die Skalierung statt ueber Alpha: ein Objekt mit Groesse 0 kostet
    nichts und kann nichts verschleiern.
    """
    ob.scale = (klein, klein, klein)
    ob.keyframe_insert("scale", frame=max(1, frame_an - 1))
    ob.scale = (gross, gross, gross)
    ob.keyframe_insert("scale", frame=frame_voll)
    ob.scale = (gross * 1.5, gross * 1.5, gross * 1.5)
    ob.keyframe_insert("scale", frame=frame_aus)
    ob.scale = (klein, klein, klein)
    ob.keyframe_insert("scale", frame=frame_aus + 1)


def funke(name, mitte, frame, dauer=4, groesse=0.22, farbe=(1.0, 0.75, 0.35)):
    """Kurzer heller Funke - Metall auf Metall.

    Fuer den Moment, in dem Cabrinovic die Granate am Laternenpfahl
    anschlaegt. Ohne diesen Funken ist die Bewegung nur ein Zucken; mit ihm
    versteht man, dass etwas ausgeloest wurde.
    """
    bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=1.0,
                                         location=mitte)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(_emission(f"{name}_Mat", farbe, 45.0))
    _skaliere(ob, frame, frame + 1, frame + dauer, groesse)
    return ob


def blitz(name, mitte, frame, dauer=3, groesse=2.2, staerke=90.0):
    """Muendungsfeuer oder Detonationsblitz. Sehr kurz, sehr hell."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=7, radius=1.0,
                                         location=mitte)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(_emission(f"{name}_Mat", (1.0, 0.86, 0.62), staerke))
    _skaliere(ob, frame, frame + 1, frame + dauer, groesse)
    return ob


def rauchpuff(name, mitte, frame_an, dauer=70, groesse=1.1, mat=None, aufsteigen=1.4):
    """Eine Rauchwolke, die waechst, aufsteigt und verschwindet."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=7, radius=1.0,
                                         location=mitte)
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat or _puff_material(f"{name}_Mat"))
    _skaliere(ob, frame_an, frame_an + int(dauer * 0.35), frame_an + dauer, groesse)
    ob.location = mitte
    ob.keyframe_insert("location", frame=frame_an)
    ob.location = (mitte[0], mitte[1], mitte[2] + aufsteigen)
    ob.keyframe_insert("location", frame=frame_an + dauer)
    return ob


def rauchfahne(name, bahn, frame_von, frame_bis, abstand=6, groesse=0.32):
    """Rauchfahne entlang einer Flugbahn.

    `bahn` ist eine Funktion frame -> (x, y, z). Alle `abstand` Bilder wird
    ein Puff gesetzt, der von dort an waechst und verweht. Dadurch bleibt
    die Bahn im Bild stehen, nachdem das Objekt weitergeflogen ist - genau
    das macht einen Wurf ueberhaupt erst nachvollziehbar.
    """
    mat = _puff_material(f"{name}_Mat")
    puffs = []
    for f in range(frame_von, frame_bis + 1, abstand):
        puffs.append(
            rauchpuff(f"{name}_{f}", bahn(f), f, dauer=55, groesse=groesse,
                      mat=mat, aufsteigen=0.5)
        )
    return puffs


def staubwand(name, mitte, frame, radius=9.0, dauer=90, saat=7):
    """Detonation: eine Wand aus Staub, die sich ausbreitet.

    Mehrere versetzte Volumenkugeln statt einer - eine einzelne Kugel liest
    sich als Ballon, mehrere als Wolke.
    """
    zufall = random.Random(saat)
    mat = _rauch_material(f"{name}_Mat", (0.50, 0.46, 0.40), 4.5)
    teile = []
    for k in range(9):
        winkel = zufall.uniform(0, math.tau)
        weite = zufall.uniform(0.2, 1.0) * radius
        ziel = (
            mitte[0] + math.cos(winkel) * weite,
            mitte[1] + math.sin(winkel) * weite * 0.6,
            mitte[2] + zufall.uniform(0.2, 1.0) * radius * 0.5,
        )
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=7, radius=1.0,
                                             location=mitte)
        ob = bpy.context.active_object
        ob.name = f"{name}_{k}"
        ob.data.materials.append(mat)
        versatz = zufall.randint(0, 5)
        _skaliere(ob, frame + versatz, frame + versatz + 12,
                  frame + dauer, zufall.uniform(0.5, 1.0) * radius * 0.45)
        ob.location = mitte
        ob.keyframe_insert("location", frame=frame + versatz)
        ob.location = ziel
        ob.keyframe_insert("location", frame=frame + dauer)
        teile.append(ob)
    return teile


def truemmer(name, mitte, frame, anzahl=14, weite=7.0, mat=None, saat=11):
    """Herausgeschleuderte Bruchstuecke. Kleine Quader auf Wurfparabeln."""
    zufall = random.Random(saat)
    stuecke = []
    for k in range(anzahl):
        winkel = zufall.uniform(0, math.tau)
        reichweite = zufall.uniform(0.35, 1.0) * weite
        hoehe = zufall.uniform(1.5, 4.5)
        flugzeit = zufall.randint(22, 45)
        bpy.ops.mesh.primitive_cube_add(size=1, location=mitte)
        ob = bpy.context.active_object
        ob.name = f"{name}_{k}"
        s = zufall.uniform(0.06, 0.20)
        ob.scale = (s, s, s * zufall.uniform(0.4, 1.0))
        if mat:
            ob.data.materials.append(mat)

        ob.location = mitte
        ob.keyframe_insert("location", frame=frame)
        ob.location = (
            mitte[0] + math.cos(winkel) * reichweite * 0.5,
            mitte[1] + math.sin(winkel) * reichweite * 0.5,
            mitte[2] + hoehe,
        )
        ob.keyframe_insert("location", frame=frame + flugzeit // 2)
        ob.location = (
            mitte[0] + math.cos(winkel) * reichweite,
            mitte[1] + math.sin(winkel) * reichweite,
            0.25,
        )
        ob.keyframe_insert("location", frame=frame + flugzeit)

        ob.rotation_euler = (0, 0, 0)
        ob.keyframe_insert("rotation_euler", frame=frame)
        ob.rotation_euler = (zufall.uniform(2, 9), zufall.uniform(2, 9), zufall.uniform(2, 9))
        ob.keyframe_insert("rotation_euler", frame=frame + flugzeit)

        # Vor dem Knall unsichtbar
        ob.scale = (0.001, 0.001, 0.001)
        ob.keyframe_insert("scale", frame=max(1, frame - 1))
        ob.scale = (s, s, s * 0.7)
        ob.keyframe_insert("scale", frame=frame)
        stuecke.append(ob)
    return stuecke


def tauben(name, mitte, frame, anzahl=16, mat=None, saat=13):
    """Aufstiebende Tauben.

    Der klassische Reflex auf einen Knall - und ein Effekt, der die Wucht
    einer Detonation vermittelt, ohne dass man Verletzte zeigen muss.
    """
    zufall = random.Random(saat)
    voegel = []
    for k in range(anzahl):
        start = (
            mitte[0] + zufall.uniform(-8, 8),
            mitte[1] + zufall.uniform(-4, 4),
            zufall.uniform(0.4, 1.2),
        )
        bpy.ops.mesh.primitive_cube_add(size=1, location=start)
        ob = bpy.context.active_object
        ob.name = f"{name}_{k}"
        ob.scale = (0.20, 0.09, 0.05)
        if mat:
            ob.data.materials.append(mat)
        los = frame + zufall.randint(0, 8)
        ob.location = start
        ob.keyframe_insert("location", frame=los)
        ob.location = (
            start[0] + zufall.uniform(-14, 14),
            start[1] + zufall.uniform(-10, 10),
            start[2] + zufall.uniform(7, 15),
        )
        ob.keyframe_insert("location", frame=los + zufall.randint(40, 70))
        voegel.append(ob)
    return voegel


# Entsaettigung fuer den Moment der Schuesse steht BEWUSST nicht hier.
#
# Sie gehoert in die Web-Schicht: dort ist sie ein CSS-Filter auf dem
# Video-Element, in Sekunden justierbar. In Blender gebacken kostet jede
# Korrektur an Zeitpunkt oder Staerke einen kompletten Neurender des Shots.
# Dieselbe Ueberlegung wie bei Vignette und Filmkorn.
