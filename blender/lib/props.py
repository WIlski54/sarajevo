"""Wiederkehrende Objekte: Wagen, Figuren, Laternen.

Der Graef & Stift kommt in neun der vierzehn Shots vor, Figuren in fast
allen. Deshalb stehen sie hier und nicht im Shot - eine Aenderung an der
Silhouette des Thronfolgerwagens muss an einer Stelle passieren, nicht an
neun.

Gestaltungsgrundsatz, aus der Spec: Figuren bleiben GESICHTSLOS. Erkennbar
werden sie ueber die Silhouette, nicht ueber Zuege. Franz Ferdinand am
Federbusch des Generalshelms, Sophie am hellen Kleid und dem
breitkrempigen Hut - beides auf hundert Meter lesbar und historisch
zutreffend, ohne ins Uncanny Valley zu geraten.
"""

from __future__ import annotations

import math
import random

import bpy


def quader(name, mitte, groesse, material=None):
    """Achsenparalleler Kasten mit den AUSSENMASSEN `groesse`.

    `primitive_cube_add(size=1)` erzeugt einen Wuerfel von einer Einheit -
    die Skalierung ist deshalb `groesse`, nicht `groesse / 2`. Die
    Halbierung war der Fehler, der die halbe Stadt schweben liess.
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=mitte)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = groesse
    if material:
        ob.data.materials.append(material)
    return ob


def _zylinder(name, mitte, radius, hoehe, material=None, ecken=12, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=ecken, radius=radius, depth=hoehe, location=mitte, rotation=rotation
    )
    ob = bpy.context.active_object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def _kugel(name, mitte, radius, material=None):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=12, ring_count=8, radius=radius, location=mitte
    )
    ob = bpy.context.active_object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


def _kegel(name, mitte, unten, oben, hoehe, material=None, ecken=10):
    bpy.ops.mesh.primitive_cone_add(
        vertices=ecken, radius1=unten, radius2=oben, depth=hoehe, location=mitte
    )
    ob = bpy.context.active_object
    ob.name = name
    if material:
        ob.data.materials.append(material)
    return ob


# --------------------------------------------------------------------------
# Figuren
# --------------------------------------------------------------------------


def stehende_figur(name, x, y, hoehe, mat_kleidung, mat_hut, boden=0.44, drehung=0.0):
    """Zuschauer. Koerper, Schultern, Kopf mit Hut.

    Drei Teile genuegen, damit das Auge einen Menschen erkennt - als reine
    Zylinder lasen die Figuren im ersten Render als Poller.
    """
    teile = [
        _kegel(f"{name}_Koerper", (x, y, boden + hoehe * 0.36),
               0.19, 0.15, hoehe * 0.72, mat_kleidung),
        quader(f"{name}_Schultern", (x, y, boden + hoehe * 0.78),
               (0.44, 0.22, 0.16), mat_kleidung),
        _kugel(f"{name}_Kopf", (x, y, boden + hoehe * 0.94), 0.105, mat_hut),
    ]
    for t in teile:
        if t.name.endswith(("Koerper", "Schultern")):
            t.rotation_euler = (0, 0, drehung)
    return teile


def sitzende_figur(name, mitte, mat_kleidung, mat_kopf, hoehe=1.15, breite=0.46):
    """Sitzende Person: Beine, Rumpf, Schultern, Kopf.

    `mitte` ist der Sitzpunkt am Boden des Sitzes. Bewusst kompakt - im
    offenen Wagen sieht man von aussen Rumpf und Kopf ueber der Bordwand.
    """
    x, y, z = mitte
    return [
        quader(f"{name}_Beine", (x + 0.24, y, z + 0.16), (0.62, breite, 0.30), mat_kleidung),
        _kegel(f"{name}_Rumpf", (x, y, z + hoehe * 0.42),
               breite * 0.46, breite * 0.38, hoehe * 0.62, mat_kleidung),
        quader(f"{name}_Schultern", (x, y, z + hoehe * 0.76),
               (0.24, breite * 1.05, 0.17), mat_kleidung),
        _kugel(f"{name}_Kopf", (x, y, z + hoehe * 0.92), 0.108, mat_kopf),
    ]


def federbusch_helm(name, mitte, mat_helm, mat_federn):
    """Generalshelm mit Federbusch - Franz Ferdinands Erkennungszeichen.

    Der Federbusch ist der Grund, warum man ihn auf historischen Aufnahmen
    sofort findet: eine hohe, hellgruene Feder ueber dem Kopf, die aus
    jeder Entfernung aus der Silhouette heraussticht. Genau deshalb braucht
    dieser Shot kein Gesicht.
    """
    x, y, z = mitte
    teile = [
        _zylinder(f"{name}_Helm", (x, y, z + 0.05), 0.115, 0.12, mat_helm),
        _zylinder(f"{name}_Krempe", (x, y, z - 0.01), 0.15, 0.03, mat_helm),
    ]
    # Federbusch: mehrere schmale Kegel, leicht gefaechert
    zufall = random.Random(1863)
    for k in range(7):
        neigung = zufall.uniform(-0.30, 0.30)
        laenge = zufall.uniform(0.30, 0.44)
        feder = _kegel(
            f"{name}_Feder{k}", (x + neigung * 0.10, y + neigung * 0.06, z + 0.14 + laenge / 2),
            0.035, 0.008, laenge, mat_federn, ecken=6,
        )
        feder.rotation_euler = (neigung * 0.5, neigung * 0.4, 0)
        teile.append(feder)
    return teile


def breiter_hut(name, mitte, mat_hut):
    """Sophies Hut: breite Krempe, flache Krone.

    Die Damenmode von 1914 kannte sehr grosse Hutkrempen - im Profil ist
    das eine unverwechselbare waagerechte Scheibe und damit das zweite
    Erkennungszeichen des Wagens.
    """
    x, y, z = mitte
    return [
        _zylinder(f"{name}_Krempe", (x, y, z + 0.02), 0.30, 0.025, mat_hut, ecken=20),
        _zylinder(f"{name}_Krone", (x, y, z + 0.09), 0.135, 0.13, mat_hut, ecken=16),
    ]


# --------------------------------------------------------------------------
# Der Wagen
# --------------------------------------------------------------------------


def graef_stift(
    name, x, y, materialien, mit_paar: bool = False, mit_standarte: bool = False
):
    """Graef & Stift Double Phaeton, stilisiert.

    materialien: dict mit lack, gummi, glas, messing, uniform, general,
                 kleid, haut, federn, standarte

    `mit_paar=True` besetzt den Wagen mit dem Thronfolgerpaar auf der
    Ruecksitzbank, dem Chauffeur Leopold Lojka am Steuer und Graf Harrach
    auf dem linken Trittbrett - so ist es fuer den 28. Juni belegt.

    Das Verdeck ist zurueckgeschlagen. Das ist nicht Dekoration: genau daran
    prallt die Granate ab, und genau deshalb sass das Paar frei sichtbar.
    """
    m = materialien
    teile = [
        quader(f"{name}_Kasten", (x, y, 0.95), (4.6, 1.9, 0.95), m["lack"]),
        quader(f"{name}_Haube", (x + 2.6, y, 1.15), (1.6, 1.7, 0.8), m["lack"]),
        # Niedrige Windschutzscheibe. Mit 0,70 m Hoehe reichte sie bis 2,10 m
        # und verdeckte von vorn genau die Koepfe des Paares - der Wagen kam
        # entgegen, und man sah durch die Scheibe hindurch nichts. Ein
        # Double Phaeton von 1914 hatte ohnehin nur ein flaches Windblech.
        quader(f"{name}_Scheibe", (x + 1.6, y, 1.62), (0.12, 1.5, 0.44), m["glas"]),
        quader(f"{name}_Verdeck", (x - 2.3, y, 1.55), (1.1, 1.8, 0.5), m["lack"]),
        # Trittbretter - Harrach stand auf dem linken
        quader(f"{name}_Trittbrett_L", (x, y + 1.02, 0.62), (3.4, 0.34, 0.10), m["lack"]),
        quader(f"{name}_Trittbrett_R", (x, y - 1.02, 0.62), (3.4, 0.34, 0.10), m["lack"]),
        # Scheinwerfer aus Messing
        _zylinder(f"{name}_Lampe_L", (x + 3.3, y + 0.62, 1.15), 0.20, 0.16,
                  m["messing"], rotation=(0, math.pi / 2, 0)),
        _zylinder(f"{name}_Lampe_R", (x + 3.3, y - 0.62, 1.15), 0.20, 0.16,
                  m["messing"], rotation=(0, math.pi / 2, 0)),
    ]
    for vx, vy in ((2.0, 1.0), (2.0, -1.0), (-1.9, 1.0), (-1.9, -1.0)):
        teile.append(
            _zylinder(
                f"{name}_Rad{vx:+.0f}{vy:+.0f}",
                (x + vx, y + vy * 0.95, 0.46), 0.46, 0.22, m["gummi"],
                ecken=16, rotation=(math.pi / 2, 0, 0),
            )
        )

    if mit_paar:
        # Ruecksitzbank: Franz Ferdinand rechts, Sophie links - so sassen sie.
        #
        # SITZHOEHE, nachgerechnet: die Bordwand endet bei 1,425 m. Eine
        # sitzende Person hat vom Sitz bis zum Scheitel etwa 1,06 m. Bei
        # Sitzhoehe 1,00 liegen die Schultern bei 1,87 und der Kopf bei 2,06 -
        # also gut dreissig Zentimeter Rumpf und der ganze Kopf ueber der
        # Bordwand, der Rest verdeckt. Das ist die Silhouette, die man auf
        # den historischen Aufnahmen sieht.
        #
        # Mit 1,52 (erster Versuch) sassen die beiden nicht im Wagen, sondern
        # standen sichtbar darauf.
        ff = (x - 1.05, y - 0.45, 1.12)
        so = (x - 1.05, y + 0.48, 1.12)
        teile += sitzende_figur(f"{name}_FranzFerdinand", ff, m["general"], m["haut"])
        teile += federbusch_helm(
            f"{name}_FF_Helm", (ff[0], ff[1], ff[2] + 1.15 * 0.92 + 0.09),
            m["general"], m["federn"],
        )
        teile += sitzende_figur(f"{name}_Sophie", so, m["kleid"], m["haut"])
        teile += breiter_hut(
            f"{name}_Sophie_Hut", (so[0], so[1], so[2] + 1.15 * 0.92 + 0.08), m["kleid"]
        )

        # Chauffeur Leopold Lojka am Steuer, etwas tiefer als die Herrschaft
        teile += sitzende_figur(
            f"{name}_Lojka", (x + 0.85, y - 0.42, 0.92), m["uniform"], m["haut"], hoehe=1.05
        )
        # Graf Harrach auf dem linken Trittbrett - er berichtete spaeter
        # die letzten Worte des Thronfolgers
        teile += stehende_figur(
            f"{name}_Harrach", x - 0.2, y + 1.02, 1.72,
            m["uniform"], m["haut"], boden=0.67,
        )

    if mit_standarte:
        # Kleiner Wimpel am Kotfluegel - zusaetzliche Kennzeichnung
        teile.append(
            _zylinder(f"{name}_Fahnenstock", (x + 3.05, y + 0.9, 1.55), 0.022, 0.7,
                      m["messing"])
        )
        teile.append(
            quader(f"{name}_Wimpel", (x + 3.05, y + 1.12, 1.82), (0.03, 0.42, 0.26),
                   m["standarte"])
        )

    leer = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(leer)
    for t in teile:
        t.parent = leer
    return leer


def laterne(name, x, y, mat_mast, mat_glas):
    """Gaslaterne. Gibt der Perspektive ihren Takt."""
    return [
        quader(f"{name}_Mast", (x, y, 2.1), (0.16, 0.16, 4.2), mat_mast),
        quader(f"{name}_Kopf", (x, y, 4.45), (0.6, 0.6, 0.75), mat_glas),
    ]
