"""Shot 04 - Čabrinović schlägt die Granate an und wirft.

Der Shot muss DREI Dinge lesbar machen, sonst erzählt er nichts:

  1. dass jemand aus der Menge heraustritt und etwas in der Hand hat
  2. dass er es gegen den Laternenpfahl schlägt - der Funke macht sichtbar,
     dass damit etwas ausgelöst wurde
  3. dass er es wirft, und wohin - die Rauchfahne zeichnet die Flugbahn
     nach und bleibt stehen, wenn die Granate längst weiter ist

Ohne die Rauchfahne wäre die Granate ein dunkler Punkt vor dunkler
Strasse. Sie ist hier kein Effekt, sondern der Träger der Information.

29 Sekunden bei 30 Bildern. Die eigentliche Handlung dauert Sekunden -
die Zeitlupe ab dem Wurf dehnt sie.
"""

from __future__ import annotations

import math

import bpy

from lib import anim, fx, materials, orte, props

DAUER_S = 29
FPS = 30

# Der Laternenpfahl, an dem angeschlagen wird. Shot 05 braucht dieselbe
# Stelle, deshalb steht sie in orte.py und nicht hier.
PFAHL_X = orte.laternenpfahl_x(-1)
PFAHL_Y = -9.2

# Cabrinovic steht an der Bruestung, also auf der Flussseite
WERFER = (PFAHL_X + 1.4, PFAHL_Y + 0.9)

# Kameraabstand, zweimal korrigiert:
#   5,5 m  -> der 4,2 m hohe Laternenpfahl fuellte bei 62 mm die Bildmitte
#  14,0 m  -> Werfer und Granate waren zu klein, um die Handlung zu lesen
#   6,3 m  -> ein Mensch fuellt bei 40 mm rund ein Drittel der Bildhoehe.
# Erst damit sieht man, dass jemand etwas anschlaegt und wirft. Der
# Laternenpfahl steht 1,4 m neben dem Werfer und kommt mit ins Bild -
# er wird ja gebraucht.
# Kamera auf der STRASSENSEITE, nicht ueber dem Fluss. Bei y = -14 lag die
# Bruestung (y = -9,9) zwischen Objektiv und Werfer und verdeckte ihn bis
# zur Brust. Jetzt steht sie auf der Fahrbahn, 5,6 m schraeg vor ihm - die
# Bruestung liegt damit HINTER ihm und rahmt ihn, statt ihn zu verstellen.
KAMERA_XY = (PFAHL_X - 3.5, PFAHL_Y + 3.7)
KAMERA_Z = 2.2

# Kein Zuschauer vor dem Objektiv - im ersten Render verdeckte ein Kopf ein
# Viertel des Bildes.
KAMERA_FREI = (KAMERA_XY[0] - 6, KAMERA_XY[0] + 4, -8.0, -2.0)

# Zeitmarken in Sekunden
T_ANSCHLAG = 7.0    # Granate gegen den Pfahl
T_WURF = 11.0       # Abwurf
T_ENDE_FLUG = 26.0  # die Granate erreicht den Wagen

KOLONNE_VON = 62.0
KOLONNE_BIS = -6.0


def _flugbahn(frames):
    """Wurfparabel vom Werfer zum Wagen. Liefert eine Funktion frame -> Ort.

    Bewusst hoch und langsam: eine flache, schnelle Bahn waere physikalisch
    plausibler, aber im Bild nicht zu verfolgen. Der Zuschauer soll dem
    Ding mit den Augen folgen koennen.
    """
    f_von = int(T_WURF * FPS)
    f_bis = int(T_ENDE_FLUG * FPS)
    start = (WERFER[0], WERFER[1], 1.55)
    # Ziel: der Thronfolgerwagen, wo er zum Wurfzeitpunkt etwa steht
    ziel = (WERFER[0] + 9.0, 1.2, 1.7)
    scheitel = 4.6

    def bahn(f):
        t = min(1.0, max(0.0, (f - f_von) / max(1, f_bis - f_von)))
        x = start[0] + (ziel[0] - start[0]) * t
        y = start[1] + (ziel[1] - start[1]) * t
        z = start[2] + (ziel[2] - start[2]) * t + scheitel * math.sin(math.pi * t)
        return (x, y, z)

    return bahn, f_von, f_bis


def _werfer(m, frames):
    """Cabrinovic. Gesichtslos wie alle Figuren - erkennbar wird er
    ausschliesslich durch seine HANDLUNG, nicht durch sein Aussehen.

    Das ist die einzige Figur im Film, die sich aus der Menge loest. Genau
    deshalb liest man sie: alle anderen stehen.
    """
    # Um den lokalen Ursprung bauen, das Empty traegt die Position -
    # sonst dreht sich die Figur um den Weltursprung und verschwindet.
    teile = props.stehende_figur("Werfer", 0.0, 0.0, 1.74, m["uniform"], m["haut"])
    leer = props.gruppe("Werfer", teile, (WERFER[0], WERFER[1] + 0.9, 0))

    f_an = int(T_ANSCHLAG * FPS)
    f_wurf = int(T_WURF * FPS)

    # Er tritt aus der Menge nach vorn, holt aus, wirft.
    leer.location = (WERFER[0], WERFER[1] + 0.9, 0)
    leer.keyframe_insert("location", frame=1)
    leer.location = (WERFER[0], WERFER[1], 0)
    leer.keyframe_insert("location", frame=f_an - 30)
    leer.keyframe_insert("location", frame=f_wurf + 40)
    anim.ease(leer)

    # Oberkoerper: Ausholen zum Anschlag, dann die Wurfbewegung
    leer.rotation_euler = (0, 0, 0)
    leer.keyframe_insert("rotation_euler", frame=f_an - 24)
    leer.rotation_euler = (0, 0, math.radians(-26))
    leer.keyframe_insert("rotation_euler", frame=f_an)
    leer.rotation_euler = (0, 0, math.radians(-34))
    leer.keyframe_insert("rotation_euler", frame=f_wurf - 10)
    leer.rotation_euler = (0, 0, math.radians(40))
    leer.keyframe_insert("rotation_euler", frame=f_wurf + 6)
    leer.rotation_euler = (0, 0, math.radians(14))
    leer.keyframe_insert("rotation_euler", frame=f_wurf + 30)
    anim.ease(leer)
    return leer


def _granate(m, frames):
    """Die Handgranate: erst in der Hand, dann auf der Flugbahn."""
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.075, depth=0.24, location=(WERFER[0], WERFER[1], 1.35)
    )
    ob = bpy.context.active_object
    ob.name = "Granate"
    ob.data.materials.append(materials.stoff("Granatenkoerper", (0.055, 0.052, 0.048)))

    bahn, f_von, f_bis = _flugbahn(frames)
    f_an = int(T_ANSCHLAG * FPS)

    # In der Hand: mitgefuehrt, beim Anschlag kurz an den Pfahl
    ob.location = (WERFER[0] + 0.3, WERFER[1] - 0.15, 1.30)
    ob.keyframe_insert("location", frame=1)
    ob.location = (PFAHL_X + 0.24, PFAHL_Y, 1.42)
    ob.keyframe_insert("location", frame=f_an)
    ob.location = (WERFER[0] - 0.35, WERFER[1] + 0.25, 1.50)
    ob.keyframe_insert("location", frame=f_von - 8)

    # Flug: alle vier Bilder ein Stuetzpunkt, damit die Parabel sauber liegt
    for f in range(f_von, f_bis + 1, 4):
        ob.location = bahn(f)
        ob.keyframe_insert("location", frame=f)
    anim.set_interpolation(ob, "LINEAR")

    # Taumeln im Flug
    ob.rotation_euler = (0, 0, 0)
    ob.keyframe_insert("rotation_euler", frame=f_von)
    ob.rotation_euler = (7.5, 3.2, 5.1)
    ob.keyframe_insert("rotation_euler", frame=f_bis)

    return ob, bahn, f_von, f_bis


def _kamera(scene, frames, bahn, f_von, f_bis):
    """Ueber die Schulter des Werfers, dann der Granate nach.

    Die Kamera bleibt beim Werfer und schwenkt mit dem Wurf - so bleibt
    beides im Bild: wer wirft, und wohin.
    """
    bpy.ops.object.camera_add(location=(KAMERA_XY[0], KAMERA_XY[1], KAMERA_Z))
    kamera = bpy.context.active_object
    kamera.name = "Kamera"
    scene.camera = kamera
    # 40 mm: nah genug fuer die Handlung, weit genug, dass die Kolonne im
    # Hintergrund noch als Ziel des Wurfs erkennbar bleibt.
    kamera.data.lens = 40
    kamera.data.dof.use_dof = True
    kamera.data.dof.aperture_fstop = 2.4

    ziel = bpy.data.objects.new("Kameraziel", None)
    bpy.context.collection.objects.link(ziel)
    schauen = kamera.constraints.new("TRACK_TO")
    schauen.target = ziel
    schauen.track_axis = "TRACK_NEGATIVE_Z"
    schauen.up_axis = "UP_Y"
    kamera.data.dof.focus_object = ziel

    f_an = int(T_ANSCHLAG * FPS)

    # Bis zum Wurf auf den Werfer und den Pfahl
    ziel.location = (WERFER[0] + 0.4, WERFER[1], 1.5)
    ziel.keyframe_insert("location", frame=1)
    ziel.location = (PFAHL_X + 0.5, PFAHL_Y + 0.4, 1.45)
    ziel.keyframe_insert("location", frame=f_an)
    ziel.location = (WERFER[0], WERFER[1], 1.6)
    ziel.keyframe_insert("location", frame=f_von)
    # Danach der Granate nach
    for f in range(f_von, f_bis + 1, 10):
        ziel.location = bahn(f)
        ziel.keyframe_insert("location", frame=f)
    ziel.location = bahn(f_bis)
    ziel.keyframe_insert("location", frame=frames)
    anim.ease(ziel)

    kamera.location = (KAMERA_XY[0], KAMERA_XY[1], KAMERA_Z)
    kamera.keyframe_insert("location", frame=1)
    kamera.location = (KAMERA_XY[0] - 1.6, KAMERA_XY[1] - 0.8, KAMERA_Z + 0.15)
    kamera.keyframe_insert("location", frame=frames)
    anim.ease(kamera)
    anim.handheld(kamera, staerke=0.016)


def build(scene: bpy.types.Scene) -> None:
    frames = DAUER_S * FPS
    scene.frame_start = 1
    scene.frame_end = frames

    m = orte.standard_materialien()
    orte.appelkai(scene, m, kamera_xy=KAMERA_XY, frei=KAMERA_FREI)

    # Die Kolonne faehrt weiter heran - sie ist das Ziel des Wurfs
    konvoi, _ = props.kolonne("Kolonne", m)
    konvoi.location = (KOLONNE_VON, 0, 0)
    konvoi.keyframe_insert("location", frame=1)
    konvoi.location = (KOLONNE_BIS, 0, 0)
    konvoi.keyframe_insert("location", frame=frames)
    anim.set_interpolation(konvoi, "LINEAR")

    _werfer(m, frames)
    granate, bahn, f_von, f_bis = _granate(m, frames)

    # Der Funke am Pfahl: ohne ihn ist der Anschlag nur ein Zucken
    f_an = int(T_ANSCHLAG * FPS)
    fx.funke("Anschlagfunke", (PFAHL_X + 0.2, PFAHL_Y, 1.42), f_an, dauer=5, groesse=0.28)
    fx.funke("Anschlagfunke2", (PFAHL_X + 0.28, PFAHL_Y - 0.1, 1.36), f_an + 2,
             dauer=4, groesse=0.16)

    # Die Rauchfahne zeichnet die Flugbahn nach und bleibt stehen, wenn die
    # Granate laengst weiter ist. Sie ist hier kein Schmuck, sondern das,
    # was den Wurf ueberhaupt nachvollziehbar macht.
    fx.rauchfahne("Wurfspur", bahn, f_von, f_bis, abstand=7, groesse=0.16)

    _kamera(scene, frames, bahn, f_von, f_bis)
