"""Prozedurale PBR-Materialien. Keine Texturdateien, keine Lizenzfragen.

Alles aus Shader-Nodes: damit auflösungsunabhaengig, beliebig skalierbar
und deterministisch reproduzierbar. Der Preis ist, dass jedes Material
gebaut statt geladen wird - dafuer gibt es diese Datei.
"""

from __future__ import annotations

import bpy


def _new(name: str) -> tuple[bpy.types.Material, bpy.types.NodeTree, object]:
    """Material mit Principled BSDF. Liefert (Material, Baum, BSDF)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes["Principled BSDF"]
    return mat, tree, bsdf


def _coords(tree, scale: float = 1.0):
    """WELTKOORDINATEN als Texturbasis - Einheit ist der Meter.

    Nicht Objektkoordinaten, und das ist der wichtigste Punkt dieser Datei:
    Objektkoordinaten reichen bei jedem Wuerfel von -0,5 bis +0,5,
    unabhaengig von seiner tatsaechlichen Groesse. Bei einer 240 m langen
    Strasse verteilen sich dann 14 Voronoi-Zellen ueber 240 Meter - jeder
    "Pflasterstein" wird 17 Meter breit und die Strasse sieht aus wie
    verschmierter Marmor. Genau das war der erste Testrender.

    Mit der Weltposition bedeutet Scale = 8 schlicht "acht Zellen pro
    Meter", egal wie gross oder klein das Objekt ist. Nebenwirkung: die
    Textur klebt am Raum statt am Objekt - fuer Architektur ideal, weil
    benachbarte Haeuser dadurch nahtlos zusammenpassen.
    """
    geo = tree.nodes.new("ShaderNodeNewGeometry")
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    tree.links.new(geo.outputs["Position"], mapping.inputs["Vector"])
    return mapping.outputs["Vector"]


def _hoehe(tree):
    """Weltweite Z-Hoehe in Metern - fuer Schmutzverlaeufe an Fassaden."""
    geo = tree.nodes.new("ShaderNodeNewGeometry")
    trenn = tree.nodes.new("ShaderNodeSeparateXYZ")
    tree.links.new(geo.outputs["Position"], trenn.inputs["Vector"])
    return trenn.outputs["Z"]


def kopfstein(name: str = "Kopfstein") -> bpy.types.Material:
    """Kopfsteinpflaster: Voronoi als Steine, Rauheit nach Feuchte.

    Die Miljacka liegt daneben, der Morgen ist frisch - die Strasse ist
    nicht staubtrocken. Genau diese leichte Feuchte macht das
    Streiflicht am Morgen sichtbar.
    """
    mat, tree, bsdf = _new(name)
    vector = _coords(tree, 1.0)

    steine = tree.nodes.new("ShaderNodeTexVoronoi")
    steine.feature = "DISTANCE_TO_EDGE"
    # 7 Zellen pro Meter = Steine von etwa 14 cm. Das ist die Groesse,
    # die auf historischen Aufnahmen des Appelkai zu sehen ist.
    steine.inputs["Scale"].default_value = 7.0
    tree.links.new(vector, steine.inputs["Vector"])

    fugen = tree.nodes.new("ShaderNodeMapRange")
    fugen.inputs["From Min"].default_value = 0.0
    fugen.inputs["From Max"].default_value = 0.055
    fugen.clamp = True
    tree.links.new(steine.outputs["Distance"], fugen.inputs["Value"])

    farbe = tree.nodes.new("ShaderNodeValToRGB")
    farbe.color_ramp.elements[0].color = (0.045, 0.042, 0.040, 1)  # Fuge, dunkel
    farbe.color_ramp.elements[1].color = (0.20, 0.19, 0.175, 1)  # Stein
    tree.links.new(fugen.outputs["Result"], farbe.inputs["Fac"])
    tree.links.new(farbe.outputs["Color"], bsdf.inputs["Base Color"])

    # Pfuetzen: grosse weiche Flecken senken die Rauheit. 0,12 pro Meter
    # ergibt Flecken von etwa 8 Metern - Pfuetzen, keine Tropfen.
    feuchte = tree.nodes.new("ShaderNodeTexNoise")
    feuchte.inputs["Scale"].default_value = 0.12
    feuchte.inputs["Detail"].default_value = 2.0
    tree.links.new(vector, feuchte.inputs["Vector"])

    rauheit = tree.nodes.new("ShaderNodeMapRange")
    rauheit.inputs["From Min"].default_value = 0.35
    rauheit.inputs["From Max"].default_value = 0.62
    rauheit.inputs["To Min"].default_value = 0.82
    rauheit.inputs["To Max"].default_value = 0.18
    rauheit.clamp = True
    tree.links.new(feuchte.outputs["Fac"], rauheit.inputs["Value"])
    tree.links.new(rauheit.outputs["Result"], bsdf.inputs["Roughness"])

    relief = tree.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = 0.35
    tree.links.new(fugen.outputs["Result"], relief.inputs["Height"])
    tree.links.new(relief.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def putz(name: str = "Putz", ton=(0.62, 0.57, 0.48)) -> bpy.types.Material:
    """Fassadenputz mit Hoehen-Grime: unten dunkler, oben ausgewaschen.

    Der Schmutzverlauf ueber die Hoehe ist der einzige Grund, warum eine
    Fassade nicht wie eine Pappwand aussieht.
    """
    mat, tree, bsdf = _new(name)
    vector = _coords(tree, 1.0)

    korn = tree.nodes.new("ShaderNodeTexNoise")
    korn.inputs["Scale"].default_value = 26.0
    korn.inputs["Detail"].default_value = 6.0
    korn.inputs["Roughness"].default_value = 0.6
    tree.links.new(vector, korn.inputs["Vector"])

    # Schmutzverlauf ueber die WELT-Hoehe in Metern: unten dunkel vom
    # Spritzwasser der Strasse, ab etwa 6 m ausgewaschen und hell. Genau
    # dieser Verlauf unterscheidet eine Fassade von einer Pappwand.
    grime = tree.nodes.new("ShaderNodeMapRange")
    grime.inputs["From Min"].default_value = 0.0
    grime.inputs["From Max"].default_value = 6.0
    grime.inputs["To Min"].default_value = 0.42
    grime.inputs["To Max"].default_value = 1.0
    grime.clamp = True
    tree.links.new(_hoehe(tree), grime.inputs["Value"])

    mix = tree.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*[c * 0.55 for c in ton], 1)
    mix.inputs["B"].default_value = (*ton, 1)
    tree.links.new(grime.outputs["Result"], mix.inputs["Factor"])
    tree.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])

    rau = tree.nodes.new("ShaderNodeMapRange")
    rau.inputs["To Min"].default_value = 0.62
    rau.inputs["To Max"].default_value = 0.88
    tree.links.new(korn.outputs["Fac"], rau.inputs["Value"])
    tree.links.new(rau.outputs["Result"], bsdf.inputs["Roughness"])

    relief = tree.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = 0.12
    tree.links.new(korn.outputs["Fac"], relief.inputs["Height"])
    tree.links.new(relief.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def kalkstein(name: str = "Kalkstein") -> bpy.types.Material:
    """Heller Werkstein fuer Sockel und Bruestungen. Wirft warmes Bounce-Licht."""
    mat, tree, bsdf = _new(name)
    vector = _coords(tree, 1.0)

    # 1,2 pro Meter: Adern und Blockwechsel im Bereich von etwa 80 cm.
    adern = tree.nodes.new("ShaderNodeTexNoise")
    adern.inputs["Scale"].default_value = 1.2
    adern.inputs["Detail"].default_value = 8.0
    tree.links.new(vector, adern.inputs["Vector"])

    # Deutlich dunkler als der erste Ansatz. Mit 0,52 bis 0,70 brannten
    # Gehwege und Sohlbaenke zu weissen Flaechen aus und zogen den Blick
    # von den Fassaden weg - Werkstein ist heller als Putz, aber nicht weiss.
    farbe = tree.nodes.new("ShaderNodeValToRGB")
    farbe.color_ramp.elements[0].color = (0.30, 0.28, 0.25, 1)
    farbe.color_ramp.elements[1].color = (0.42, 0.39, 0.34, 1)
    tree.links.new(adern.outputs["Fac"], farbe.inputs["Fac"])
    tree.links.new(farbe.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.72
    return mat


def wasser(name: str = "Miljacka") -> bpy.types.Material:
    """Flaches, langsames Wasser. Spiegelt die Fassaden - deshalb wichtig."""
    mat, tree, bsdf = _new(name)
    vector = _coords(tree, 1.0)

    # 3 pro Meter: Kraeuselwellen von etwa 30 cm auf langsamem Wasser.
    wellen = tree.nodes.new("ShaderNodeTexNoise")
    wellen.inputs["Scale"].default_value = 3.0
    wellen.inputs["Detail"].default_value = 3.0
    tree.links.new(vector, wellen.inputs["Vector"])

    bsdf.inputs["Base Color"].default_value = (0.055, 0.075, 0.070, 1)
    bsdf.inputs["Roughness"].default_value = 0.12
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.33

    relief = tree.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = 0.06
    tree.links.new(wellen.outputs["Fac"], relief.inputs["Height"])
    tree.links.new(relief.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def lack(name: str = "Autolack", ton=(0.014, 0.028, 0.020)) -> bpy.types.Material:
    """Dunkelgruener Lack - der Graef & Stift Double Phaeton.

    Klarlack bewusst schwach: mit Coat 0,9 und Metallic 0,1 sah der Wagen
    wie gebuerstetes Aluminium aus, nicht wie lackiertes Blech von 1914.
    Ein Wagen dieser Zeit hat einen tiefen, satten Lack mit einem
    schmalen Glanzstreifen, keine Spiegelflaeche.
    """
    mat, tree, bsdf = _new(name)
    bsdf.inputs["Base Color"].default_value = (*ton, 1)
    bsdf.inputs["Roughness"].default_value = 0.34
    bsdf.inputs["Metallic"].default_value = 0.0
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.3
        bsdf.inputs["Coat Roughness"].default_value = 0.12
    return mat


def berg(name: str = "Berghang") -> bpy.types.Material:
    """Die Haenge des Talkessels. Stark entsaettigt und aufgehellt -
    Luftperspektive macht ferne Berge blaugrau, nicht gruen."""
    mat, tree, bsdf = _new(name)
    vector = _coords(tree, 1.0)

    struktur = tree.nodes.new("ShaderNodeTexNoise")
    struktur.inputs["Scale"].default_value = 0.03
    struktur.inputs["Detail"].default_value = 6.0
    tree.links.new(vector, struktur.inputs["Vector"])

    farbe = tree.nodes.new("ShaderNodeValToRGB")
    farbe.color_ramp.elements[0].color = (0.16, 0.19, 0.22, 1)
    farbe.color_ramp.elements[1].color = (0.24, 0.27, 0.29, 1)
    tree.links.new(struktur.outputs["Fac"], farbe.inputs["Fac"])
    tree.links.new(farbe.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.95
    return mat


def gummi(name: str = "Reifen") -> bpy.types.Material:
    """Vollgummireifen und dunkle Speichenraeder.

    Wichtig, weil Raeder aus Messing wie Goldmuenzen aussehen - im ersten
    Testrender lagen vier leuchtend gelbe Scheiben im Vordergrund.
    """
    mat, tree, bsdf = _new(name)
    bsdf.inputs["Base Color"].default_value = (0.022, 0.020, 0.019, 1)
    bsdf.inputs["Roughness"].default_value = 0.85
    return mat


def messing(name: str = "Messing") -> bpy.types.Material:
    mat, tree, bsdf = _new(name)
    bsdf.inputs["Base Color"].default_value = (0.62, 0.47, 0.20, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.28
    return mat


def glas_dunkel(name: str = "Fensterglas") -> bpy.types.Material:
    """Fensterscheiben. Dunkel und leicht spiegelnd statt durchsichtig -
    Innenraeume gibt es nicht, und leere Zimmer waeren schlimmer als dunkle."""
    mat, tree, bsdf = _new(name)
    bsdf.inputs["Base Color"].default_value = (0.020, 0.024, 0.028, 1)
    bsdf.inputs["Roughness"].default_value = 0.08
    bsdf.inputs["Metallic"].default_value = 0.35
    return mat


def stoff(name: str = "Uniformtuch", ton=(0.09, 0.10, 0.12)) -> bpy.types.Material:
    mat, tree, bsdf = _new(name)
    bsdf.inputs["Base Color"].default_value = (*ton, 1)
    bsdf.inputs["Roughness"].default_value = 0.92
    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.25
    return mat
