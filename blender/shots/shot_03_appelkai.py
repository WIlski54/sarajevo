"""Shot 03 - Die Kolonne fährt über den Appelkai.

REFERENZ-SHOT der Pipeline. An diesem Bild entscheidet sich, ob die Optik
traegt, bevor dreizehn weitere Shots entstehen. Er enthaelt alles, was die
uebrigen wiederverwenden: Kopfsteinpflaster, geschlossene Fassadenzeile,
Fluss, Morgenlicht, Hoehenrauch, Menge, Wagen.

Beat 2, erster von drei Shots. 17 Sekunden bei 30 Bildern.
"""

from __future__ import annotations

import math
import random

import bpy

from lib import anim, licht, materials

DAUER_S = 17
FPS = 30


def _quader(name, mitte, groesse, material=None):
    """Achsenparalleler Kasten mit den Aussenmassen `groesse`, zentriert auf
    `mitte`. Fast die ganze Stadt besteht daraus - Fassaden von 1914 sind
    Kastenformen mit Gliederung, kein Freiform-Design.

    ACHTUNG, teuer gelernt: `primitive_cube_add(size=1)` erzeugt einen
    Wuerfel von EINER Einheit Kantenlaenge (-0,5 bis +0,5). Die Skalierung
    ist deshalb `groesse`, NICHT `groesse / 2`. Mit der Halbierung war jeder
    Baukoerper der Szene halb so gross wie beabsichtigt, sass aber auf
    Koordinaten fuer die volle Groesse: Haeuser schwebten 3,6 m ueber dem
    Boden und ihre Fenster hingen neben der Fassade in der Luft. Gefunden
    wurde das nicht am Bild, sondern durch Messen der Bounding-Boxen.
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=mitte)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = groesse
    if material:
        ob.data.materials.append(material)
    return ob


def _strasse(mat_stein, mat_kalk):
    """Uferstrasse: Fahrbahn, zwei Gehwege, Bruestung zum Fluss."""
    _quader("Fahrbahn", (0, 0, 0), (240, 14, 0.3), mat_stein)
    _quader("Gehweg_Haus", (0, 8.6, 0.22), (240, 3.2, 0.44), mat_kalk)
    _quader("Gehweg_Fluss", (0, -8.4, 0.22), (240, 2.8, 0.44), mat_kalk)
    # Die Bruestung haelt den Blick auf der Strasse und faengt das Streiflicht
    _quader("Bruestung", (0, -9.9, 0.62), (240, 0.5, 1.05), mat_kalk)


def _fluss(mat_wasser, mat_kalk):
    """Die Miljacka. Wichtig aus zwei Gruenden: sie spiegelt die Fassaden,
    und sie ist an dieser Stelle nur wenige Zentimeter tief - darin
    scheitert Cabrinovics Selbstmordversuch."""
    _quader("Kaimauer", (0, -13.5, -1.4), (240, 0.7, 3.4), mat_kalk)
    _quader("Miljacka", (0, -22, -2.05), (240, 17, 0.1), mat_wasser)
    _quader("Ufer_fern", (0, -34, -1.2), (240, 8, 2.2), mat_kalk)


def _fassadenzeile(putze, mat_glas, mat_kalk):
    """Geschlossene Haeuserzeile.

    Der Rhythmus entsteht aus wechselnden Breiten, Hoehen und Putztoenen -
    gleich breite Haeuser sehen sofort nach Computer aus. Sockel und Gesims
    geben jedem Haus Gewicht, Sohlbaenke unter den Fenstern brechen das
    Licht und verhindern den Pappwand-Eindruck.
    """
    x = -120.0
    i = 0
    while x < 120:
        breite = 11.0 + (i % 4) * 3.5
        geschosse = 3 + (i % 3)
        hoehe = 4.2 + geschosse * 3.4
        mat = putze[i % len(putze)]
        mitte_x = x + breite / 2

        _quader(f"Haus_{i:02d}", (mitte_x, 16.0, hoehe / 2), (breite, 12.0, hoehe), mat)
        _quader(f"Sockel_{i:02d}", (mitte_x, 9.94, 1.1), (breite, 0.35, 2.2), mat_kalk)
        _quader(f"Gesims_{i:02d}", (mitte_x, 9.8, hoehe + 0.2), (breite + 0.6, 0.9, 0.5), mat_kalk)

        spalten = max(2, int(breite / 3.6))
        for g in range(geschosse):
            z = 3.6 + g * 3.4
            for sp in range(spalten):
                fx = x + (sp + 0.5) * (breite / spalten)
                _quader(f"Fenster_{i:02d}_{g}_{sp}", (fx, 9.88, z), (1.25, 0.3, 2.0), mat_glas)
                _quader(f"Bank_{i:02d}_{g}_{sp}", (fx, 9.8, z - 1.08), (1.7, 0.45, 0.16), mat_kalk)

        x += breite
        i += 1


def _berge(mat_berg):
    """Die Haenge des Talkessels.

    Sarajevo liegt in einem Tal - ohne die Berge endet die Strasse im
    Nichts und das Bild verliert seinen Ort. Drei versetzte Ruecken in
    grosser Entfernung genuegen; die Luftperspektive macht den Rest.
    """
    zufall = random.Random(28061914)

    # Wichtig: die Ruecken muessen SUEDLICH des Flusses (-Y) und am Talende
    # (+X) stehen. Im ersten Versuch lagen sie bei +Y, also hinter der
    # Haeuserzeile - vollstaendig verdeckt und damit wirkungslos.
    # Entfernungen in KILOMETERN denken, nicht in Hausbreiten. Im zweiten
    # Versuch standen 285 m hohe Kegel 340 m entfernt: das sind 40 Grad
    # Bildwinkel, das Objektiv hat 27 Grad vertikal - eine blaue Wand vor
    # dem Fluss, die zusaetzlich die ganze Strasse verschattete.
    # Die Haenge des Sarajevoer Talkessels steigen ueber ein bis drei
    # Kilometer hinweg an. Bei 2,2 km Abstand ergibt ein 420 m hoher Ruecken
    # etwa 11 Grad - eine Silhouette ueber den Daechern, kein Vorhang.
    # Bereiche statt zentrierter Streuung. Zentriert gestreut landete ein
    # Kegel des Talend-Ruecken bei x = 450, also 620 m vor der Kamera - das
    # war die dunkle Wand im Bild und der Grund fuer die verschattete
    # Strasse. Mit expliziten Bereichen ist der Mindestabstand garantiert.
    reihen = [
        # (x von, x bis, y, Anzahl, Hoehe, Breite)
        (-4200, 3200, -2400, 5, 420, 1800),   # Sued-Hang gegenueber
        (-3000, 4500, -3900, 4, 640, 2500),   # dahinter, hoeher
        (2800, 6200, -900, 3, 520, 2100),     # Talende in Blickrichtung
    ]

    kamera_xy = (-34.0, -6.2)
    naechster = float("inf")

    for reihe, (x_von, x_bis, y, anzahl, hoehe_basis, breite_basis) in enumerate(reihen):
        for k in range(anzahl):
            t = (k + 0.5) / anzahl
            x = x_von + t * (x_bis - x_von) + zufall.uniform(-250, 250)
            y_k = y + zufall.uniform(-350, 350)
            hoehe = hoehe_basis * zufall.uniform(0.75, 1.3)
            breite = breite_basis * zufall.uniform(0.8, 1.25)
            bpy.ops.mesh.primitive_cone_add(
                vertices=7, radius1=breite / 2, radius2=breite * 0.16,
                depth=hoehe, location=(x, y_k, hoehe / 2 - 90),
            )
            ob = bpy.context.active_object
            ob.name = f"Berg_{reihe}_{k}"
            ob.rotation_euler = (0, 0, zufall.uniform(0, math.tau))
            ob.data.materials.append(mat_berg)

            abstand = math.dist((x, y_k), kamera_xy) - breite / 2
            naechster = min(naechster, abstand)

    # Messung statt Augenmass: unter 1,2 km wird ein Ruecken zur Wand und
    # verschattet die Strasse. Lieber eine laute Warnung im Bau-Log als ein
    # nachtblaues Bild, dessen Ursache man im Licht sucht.
    print(f"  Berge: naechster Rand {naechster:.0f} m vor der Kamera")
    if naechster < 1200:
        print("  WARNUNG: Berg zu nah - er verdeckt den Himmel und wirft "
              "Schatten auf die Strasse.")


def _laternen(mat_messing, mat_glas):
    """Gaslaternen am Ufer. Sie geben der Perspektive ihren Takt - und an
    einer von ihnen schlaegt Cabrinovic in Shot 04 die Granate an."""
    for k in range(-6, 7):
        x = k * 18.0
        _quader(f"Laterne_Mast_{k}", (x, -9.2, 2.1), (0.16, 0.16, 4.2), mat_messing)
        _quader(f"Laterne_Kopf_{k}", (x, -9.2, 4.45), (0.6, 0.6, 0.75), mat_glas)


def _menge(mat_stoff, mat_haut, anzahl: int = 170):
    """Zuschauer als Silhouetten in mittlerer Distanz.

    Bewusst gesichtslos - das umgeht das Uncanny Valley vollstaendig und
    entspricht der andeutenden Erzaehlweise des Projekts. Aber nicht
    formlos: als reine Zylinder lasen die Figuren im ersten Render als
    Poller. Drei Teile genuegen, damit das Auge einen Menschen erkennt -
    schmaler Koerper, angedeutete Schultern, Kopf.

    Feste Saat, damit dieselbe Menge reproduzierbar ist.
    """
    zufall = random.Random(1914)
    for k in range(anzahl):
        x = zufall.uniform(-115, 115)
        haus_seite = zufall.random() < 0.72  # mehr Publikum vor den Haeusern
        y = (9.0 if haus_seite else -8.6) + zufall.uniform(-1.0, 1.3)
        hoehe = zufall.uniform(1.58, 1.86)
        boden = 0.44
        drehung = zufall.uniform(0, math.tau)

        # Koerper: schmal und leicht konisch, nicht zylindrisch
        bpy.ops.mesh.primitive_cone_add(
            vertices=10, radius1=0.19, radius2=0.15,
            depth=hoehe * 0.72, location=(x, y, boden + hoehe * 0.36),
        )
        koerper = bpy.context.active_object
        koerper.name = f"Figur_{k:03d}_Koerper"
        koerper.rotation_euler = (0, 0, drehung)
        koerper.data.materials.append(mat_stoff)

        # Schultern: flacher, breiter Quader - erst er macht die Silhouette
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, boden + hoehe * 0.78))
        schultern = bpy.context.active_object
        schultern.name = f"Figur_{k:03d}_Schultern"
        schultern.scale = (0.44, 0.22, 0.16)
        schultern.rotation_euler = (0, 0, drehung)
        schultern.data.materials.append(mat_stoff)

        # Kopf mit Hut - 1914 traegt jeder auf der Strasse Kopfbedeckung
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=10, ring_count=6, radius=0.105,
            location=(x, y, boden + hoehe * 0.94),
        )
        kopf = bpy.context.active_object
        kopf.name = f"Figur_{k:03d}_Kopf"
        kopf.data.materials.append(mat_haut)


def _wagen(mat_lack, mat_gummi, mat_glas):
    """Drei offene Wagen der Kolonne, stilisiert nach dem Graef & Stift
    Double Phaeton. Das Verdeck ist zurueckgeschlagen - genau daran prallt
    in Shot 05 die Granate ab."""
    wagen = []
    for k, x in enumerate((-16.0, 0.0, 16.0)):
        teile = [
            _quader(f"Wagen{k}_Kasten", (x, 1.2, 0.95), (4.6, 1.9, 0.95), mat_lack),
            _quader(f"Wagen{k}_Haube", (x + 2.6, 1.2, 1.15), (1.6, 1.7, 0.8), mat_lack),
            _quader(f"Wagen{k}_Scheibe", (x + 1.6, 1.2, 1.75), (0.12, 1.5, 0.7), mat_glas),
            _quader(f"Wagen{k}_Verdeck", (x - 2.3, 1.2, 1.55), (1.1, 1.8, 0.5), mat_lack),
        ]
        for vx, vy in ((2.0, 1.0), (2.0, -1.0), (-1.9, 1.0), (-1.9, -1.0)):
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=16, radius=0.46, depth=0.22,
                rotation=(math.pi / 2, 0, 0),
                location=(x + vx, 1.2 + vy * 0.95, 0.46),
            )
            rad = bpy.context.active_object
            rad.name = f"Wagen{k}_Rad{vx:+.0f}{vy:+.0f}"
            rad.data.materials.append(mat_gummi)
            teile.append(rad)

        leer = bpy.data.objects.new(f"Wagen{k}", None)
        bpy.context.collection.objects.link(leer)
        for t in teile:
            t.parent = leer
        wagen.append(leer)
    return wagen


def _fahrt(wagen, frames):
    """Die Kolonne rollt durch das Bild."""
    for leer in wagen:
        leer.location = (-70, 0, 0)
        leer.keyframe_insert("location", frame=1)
        leer.location = (58, 0, 0)
        leer.keyframe_insert("location", frame=frames)
        # LINEAR, nicht BEZIER: konstante Geschwindigkeit. Ein Wagen von
        # 1914 beschleunigt auf einer Uferstrasse nicht, und ein
        # Bezier-Auslauf wuerde ihn am Bildrand abbremsen lassen.
        anim.set_interpolation(leer, "LINEAR")


def _kamera(scene, frames):
    """Leichte Mitfahrt auf Augenhoehe eines Zuschauers.

    Kein Kran, kein Drohnenblick: der Beat soll wirken, als staende man
    selbst in der Menge am Kai. Die Seitfahrt erzeugt Parallaxe zwischen
    Laternen und Fassaden - erst dadurch bekommt die Strasse Tiefe.
    """
    bpy.ops.object.camera_add(location=(-34, -6.2, 1.75))
    kamera = bpy.context.active_object
    kamera.name = "Kamera"
    scene.camera = kamera
    kamera.data.lens = 42
    kamera.data.dof.use_dof = True
    kamera.data.dof.aperture_fstop = 2.5

    ziel = bpy.data.objects.new("Kameraziel", None)
    bpy.context.collection.objects.link(ziel)
    ziel.location = (6, 1.2, 1.4)

    schauen = kamera.constraints.new("TRACK_TO")
    schauen.target = ziel
    schauen.track_axis = "TRACK_NEGATIVE_Z"
    schauen.up_axis = "UP_Y"
    kamera.data.dof.focus_object = ziel

    kamera.location = (-34, -6.2, 1.75)
    kamera.keyframe_insert("location", frame=1)
    kamera.location = (-8, -6.6, 1.72)
    kamera.keyframe_insert("location", frame=frames)
    anim.ease(kamera)
    anim.handheld(kamera)

    ziel.location = (6, 1.2, 1.4)
    ziel.keyframe_insert("location", frame=1)
    ziel.location = (34, 1.2, 1.4)
    ziel.keyframe_insert("location", frame=frames)
    anim.ease(ziel)


def build(scene: bpy.types.Scene) -> None:
    frames = DAUER_S * FPS
    scene.frame_start = 1
    scene.frame_end = frames

    mat_stein = materials.kopfstein()
    mat_kalk = materials.kalkstein()
    mat_wasser = materials.wasser()
    mat_glas = materials.glas_dunkel()
    mat_messing = materials.messing()
    mat_gummi = materials.gummi()
    mat_lack = materials.lack()
    mat_stoff = materials.stoff()
    # Deutlich waermer und dunkler als der erste Versuch: das blaue
    # Himmelsfuelllicht entsaettigt jede Fassade, hellgraue Toene wurden
    # dadurch zu weissen Flaechen. Historische Vorbilder am Appelkai sind
    # Ocker, warmes Grau und ein gebrochenes Rosa, alle eher gedeckt.
    # Dritter Anlauf. 0,55 bis 0,68 war zu hell (alles weiss), 0,27 bis 0,38
    # zu dunkel (Fassaden fielen gegen die Gehwege ab). Diese Werte liegen
    # dazwischen und behalten den warmen Grundton: Ocker, warmes Grau,
    # gebrochenes Rosa, Sand und ein gedecktes Oliv.
    putze = [
        materials.putz("Putz_Ocker", (0.50, 0.40, 0.25)),
        materials.putz("Putz_Grau", (0.42, 0.40, 0.36)),
        materials.putz("Putz_Rosa", (0.48, 0.35, 0.31)),
        materials.putz("Putz_Sand", (0.54, 0.47, 0.34)),
        materials.putz("Putz_Oliv", (0.41, 0.41, 0.30)),
    ]

    _berge(materials.berg())
    _strasse(mat_stein, mat_kalk)
    _fluss(mat_wasser, mat_kalk)
    _fassadenzeile(putze, mat_glas, mat_kalk)
    _laternen(mat_messing, mat_glas)
    _menge(mat_stoff, materials.stoff("Hut", (0.045, 0.042, 0.040)))
    _fahrt(_wagen(mat_lack, mat_gummi, mat_glas), frames)

    licht.sonne()
    licht.himmel(scene)
    # Nebel NUR ueber dem Wasser (y von -36 bis -12). Die Kamera steht bei
    # y = -6,2 und darf nicht im Volumenkoerper sitzen - von innen ist ein
    # Volumen keine Atmosphaere, sondern ein Vorhang vor dem Objektiv.
    licht.hoehenrauch(mitte=(0, -24, 2.5), groesse=(240, 24, 5))

    _kamera(scene, frames)
