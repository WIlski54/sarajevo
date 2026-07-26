"""Sonne, Himmel und Nebel. Einmal definiert, von allen Shots benutzt.

Alle Aussenshots spielen am selben Vormittag - der Sonnenstand muss
zwischen ihnen zusammenpassen, sonst springt das Licht im Schnitt.

Aufzaehlungen und Eigenschaften werden GEFRAGT, nicht geraten: Blender
hat den Himmel zwischen den Versionen mehrfach umbenannt (der frueher
uebliche Typ "NISHITA" existiert in 5.1 nicht mehr). Ein hart verdrahteter
Name wirft entweder einen Fehler oder greift still ins Leere.
"""

from __future__ import annotations

import math

import bpy

# Plausibel fuer den 28. Juni, 10 Uhr, Sarajevo (43,9 Grad Nord, 18,4 Ost):
# hoch stehende Sonne, flaches Morgenlicht waere um 10 Uhr falsch.
#
# Der Azimut ist so gewaehlt, dass das Licht von der Flussseite (-Y) kommt.
# Das ist keine Kosmetik, sondern historisch richtig: die Haeuserzeile des
# Appelkai stand am NORDufer der Miljacka, ihre Fassaden zeigten nach Sueden
# und lagen an einem Junivormittag in der Sonne. Mit dem ersten Wert lag die
# ganze Zeile im Schatten und das Bild wirkte kalt und abendlich.
# Der Azimut ist nachgerechnet, nicht geschaetzt. Der Lichtvektor einer
# SUN mit rotation_euler (90-h, 0, a) ist
#     (-sin(90-h)*sin(a), sin(90-h)*cos(a), -cos(90-h)).
# Die Fassaden zeigen nach -Y, ihre Beleuchtung ist also sin(90-h)*cos(a).
# Bei a = -64 Grad ergibt das nur 0,26 - streifendes Licht, die Zeile blieb
# flach, egal wie stark die Sonne war. Bei a = -30 Grad sind es 0,51:
# deutliche Modellierung, und die Richtung bleibt Suedost, wie es fuer
# 10 Uhr vormittags richtig ist.
SONNE_HOEHE = math.radians(54)
SONNE_AZIMUT = math.radians(-30)
HOEHE_UEBER_MEER = 500  # Sarajevo liegt in einem Talkessel


def _enum_werte(node, eigenschaft: str) -> list[str]:
    try:
        return [e.identifier for e in node.bl_rna.properties[eigenschaft].enum_items]
    except (KeyError, AttributeError):
        return []


def _setze(ziel, name: str, wert) -> bool:
    """Setzt eine Eigenschaft nur, wenn sie existiert. Liefert Erfolg."""
    if not hasattr(ziel, name):
        return False
    try:
        setattr(ziel, name, wert)
        return True
    except (TypeError, ValueError):
        return False


def sonne(staerke: float = 5.5) -> bpy.types.Object:
    """Die Morgensonne. Weiche Kante, leicht warm."""
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 40))
    ob = bpy.context.active_object
    ob.name = "Morgensonne"
    ob.data.energy = staerke
    # 0,9 Grad statt der physikalischen 0,53: etwas weichere Schattenkanten
    # sehen in Eevee natuerlicher aus als messerscharfe.
    ob.data.angle = math.radians(0.9)
    ob.data.color = (1.0, 0.945, 0.86)
    ob.rotation_euler = (math.pi / 2 - SONNE_HOEHE, 0, SONNE_AZIMUT)
    return ob


def himmel(scene: bpy.types.Scene, staerke: float = 0.14, dunst: float = 0.25) -> None:
    """Physikalischer Himmel als FUELLLICHT, nicht als Hauptlicht.

    Achtung, teuer gelernt: der Himmel liefert bei Staerke 1,0 schon
    volles Tageslicht. Zusammen mit einer SUN-Lampe wird das Licht doppelt
    gezaehlt, und selbst AgX kann das nicht mehr retten - das ganze Bild
    laeuft in die Schulter und wird weiss. Der Himmel bleibt deshalb
    niedrig; die Sonne macht das Licht, der Himmel nur die blauen Schatten.

    `dunst` ebenfalls sparsam: hoher Staubgehalt macht den Horizont weiss
    und frisst die Tiefenwirkung, die die Fassadenzeile erst erzeugt.
    """
    welt = bpy.data.worlds.new("Himmel")
    scene.world = welt
    welt.use_nodes = True
    tree = welt.node_tree
    tree.nodes.clear()

    sky = tree.nodes.new("ShaderNodeTexSky")
    typen = _enum_werte(sky, "sky_type")
    for kandidat in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "HOSEK_WILKIE", "PREETHAM"):
        if kandidat in typen:
            sky.sky_type = kandidat
            break

    _setze(sky, "sun_elevation", SONNE_HOEHE)
    _setze(sky, "sun_rotation", SONNE_AZIMUT)
    _setze(sky, "altitude", HOEHE_UEBER_MEER)
    _setze(sky, "dust_density", dunst)
    _setze(sky, "air_density", 1.0)
    # Die Sonnenscheibe selbst kommt vom SUN-Licht, nicht vom Himmel -
    # sonst gibt es zwei Sonnen mit unterschiedlicher Richtung.
    _setze(sky, "sun_disc", False)

    hintergrund = tree.nodes.new("ShaderNodeBackground")
    hintergrund.inputs["Strength"].default_value = staerke
    ausgang = tree.nodes.new("ShaderNodeOutputWorld")
    tree.links.new(sky.outputs["Color"], hintergrund.inputs["Color"])
    tree.links.new(hintergrund.outputs["Background"], ausgang.inputs["Surface"])


def hoehenrauch(
    mitte=(0, -14, 3), groesse=(130, 30, 5), dichte: float = 0.022, name: str = "Hoehenrauch"
) -> bpy.types.Object:
    """Duenner Nebel, unten dichter, nach oben ausklingend.

    Der Dichteverlauf ueber die Objekt-Z-Achse ist nicht Kosmetik: ohne ihn
    zeichnet Eevee die Kanten des Volumenkoerpers als sichtbares Rechteck
    in den Himmel.
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=mitte)
    box = bpy.context.active_object
    box.name = name
    box.scale = groesse

    mat = bpy.data.materials.new(f"{name}_Volumen")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    koord = tree.nodes.new("ShaderNodeTexCoord")
    trenn = tree.nodes.new("ShaderNodeSeparateXYZ")
    tree.links.new(koord.outputs["Object"], trenn.inputs["Vector"])

    falloff = tree.nodes.new("ShaderNodeMapRange")
    falloff.interpolation_type = "SMOOTHSTEP"
    falloff.inputs["From Min"].default_value = -0.5
    falloff.inputs["From Max"].default_value = 0.5
    falloff.inputs["To Min"].default_value = 1.0
    falloff.inputs["To Max"].default_value = 0.0
    falloff.clamp = True
    tree.links.new(trenn.outputs["Z"], falloff.inputs["Value"])

    schwaden = tree.nodes.new("ShaderNodeTexNoise")
    schwaden.inputs["Scale"].default_value = 1.1
    schwaden.inputs["Detail"].default_value = 4.0
    tree.links.new(koord.outputs["Object"], schwaden.inputs["Vector"])

    mal_dichte = tree.nodes.new("ShaderNodeMath")
    mal_dichte.operation = "MULTIPLY"
    mal_dichte.inputs[1].default_value = dichte
    tree.links.new(falloff.outputs["Result"], mal_dichte.inputs[0])

    mal_schwaden = tree.nodes.new("ShaderNodeMath")
    mal_schwaden.operation = "MULTIPLY"
    tree.links.new(mal_dichte.outputs["Value"], mal_schwaden.inputs[0])
    tree.links.new(schwaden.outputs["Fac"], mal_schwaden.inputs[1])

    vol = tree.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.80, 0.83, 0.88, 1)
    vol.inputs["Anisotropy"].default_value = 0.35
    tree.links.new(mal_schwaden.outputs["Value"], vol.inputs["Density"])

    ausgang = tree.nodes.new("ShaderNodeOutputMaterial")
    tree.links.new(vol.outputs["Volume"], ausgang.inputs["Volume"])
    box.data.materials.append(mat)
    return box
