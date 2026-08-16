"""Die Schauplaetze. Einmal gebaut, von mehreren Shots benutzt.

Der Appelkai traegt die Shots 03, 04 und 05, die Ecke Franz-Joseph-Strasse
die Shots 09, 10 und 11. Wuerde jeder Shot seine Strasse selbst bauen,
saehe dieselbe Strasse in aufeinanderfolgenden Einstellungen
unterschiedlich aus - im Schnitt faellt das sofort auf.

Alle Masse in Metern. Die Fahrbahn liegt auf z = 0, die Haeuserzeile
noerdlich (+Y), der Fluss suedlich (-Y).
"""

from __future__ import annotations

import math
import random

import bpy

from lib import licht, materials, props


def standard_materialien() -> dict:
    """Ein Satz Materialien fuer alle Aussenshots.

    Gemeinsam, damit Putz und Pflaster zwischen den Einstellungen nicht
    springen. Die Putztoene sind das Ergebnis von drei Anlaeufen: zu hell
    brannte alles weiss aus, zu dunkel fielen die Fassaden gegen die
    Gehwege ab.
    """
    return {
        "stein": materials.kopfstein(),
        "kalk": materials.kalkstein(),
        "wasser": materials.wasser(),
        "glas": materials.glas_dunkel(),
        "messing": materials.messing(),
        "gummi": materials.gummi(),
        "lack": materials.lack(),
        "uniform": materials.stoff(),
        "general": materials.generalsuniform(),
        "kleid": materials.kleid(),
        "haut": materials.stoff("Hut", (0.045, 0.042, 0.040)),
        "federn": materials.federn(),
        "standarte": materials.standarte(),
        "berg": materials.berg(),
        "putze": [
            materials.putz("Putz_Ocker", (0.50, 0.40, 0.25)),
            materials.putz("Putz_Grau", (0.42, 0.40, 0.36)),
            materials.putz("Putz_Rosa", (0.48, 0.35, 0.31)),
            materials.putz("Putz_Sand", (0.54, 0.47, 0.34)),
            materials.putz("Putz_Oliv", (0.41, 0.41, 0.30)),
        ],
    }


# --------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------


def fassadenzeile(m, x_von=-120.0, x_bis=120.0, y_front=10.0, tiefe=12.0, saat=0):
    """Geschlossene Haeuserzeile.

    Der Rhythmus entsteht aus wechselnden Breiten, Hoehen und Putztoenen -
    gleich breite Haeuser sehen sofort nach Computer aus. Sockel und Gesims
    geben jedem Haus Gewicht, Sohlbaenke brechen das Licht.
    """
    x = x_von
    i = saat
    while x < x_bis:
        breite = 11.0 + (i % 4) * 3.5
        geschosse = 3 + (i % 3)
        hoehe = 4.2 + geschosse * 3.4
        mat = m["putze"][i % len(m["putze"])]
        mitte_x = x + breite / 2
        y_mitte = y_front + tiefe / 2

        props.quader(f"Haus_{i:02d}", (mitte_x, y_mitte, hoehe / 2),
                     (breite, tiefe, hoehe), mat)
        props.quader(f"Sockel_{i:02d}", (mitte_x, y_front - 0.06, 1.1),
                     (breite, 0.35, 2.2), m["kalk"])
        props.quader(f"Gesims_{i:02d}", (mitte_x, y_front - 0.2, hoehe + 0.2),
                     (breite + 0.6, 0.9, 0.5), m["kalk"])

        spalten = max(2, int(breite / 3.6))
        for g in range(geschosse):
            z = 3.6 + g * 3.4
            for sp in range(spalten):
                fx = x + (sp + 0.5) * (breite / spalten)
                props.quader(f"Fenster_{i:02d}_{g}_{sp}", (fx, y_front - 0.12, z),
                             (1.25, 0.3, 2.0), m["glas"])
                props.quader(f"Bank_{i:02d}_{g}_{sp}", (fx, y_front - 0.2, z - 1.08),
                             (1.7, 0.45, 0.16), m["kalk"])
        x += breite
        i += 1


def menge(m, anzahl=170, x_von=-115.0, x_bis=115.0, y_haus=9.0, y_fluss=-8.6,
          saat=1914, frei=None):
    """Zuschauer als gesichtslose Silhouetten.

    Erkennbar als Mensch ueber Koerper, Schultern und Kopf - als reine
    Zylinder lasen sie im ersten Render als Poller. Feste Saat, damit
    dieselbe Menge in allen Einstellungen an denselben Stellen steht.

    `frei` ist ein Rechteck (x_min, x_max, y_min, y_max), in dem KEINE
    Figur gesetzt wird. Gebraucht wird das vor der Kamera: im ersten Render
    von Shot 04 stand ein Zuschauer direkt vor dem Objektiv und sein Kopf
    verdeckte ein Viertel des Bildes.
    """
    zufall = random.Random(saat)
    gesetzt = 0
    versuche = 0
    while gesetzt < anzahl and versuche < anzahl * 6:
        versuche += 1
        x = zufall.uniform(x_von, x_bis)
        haus_seite = zufall.random() < 0.72
        y = (y_haus if haus_seite else y_fluss) + zufall.uniform(-1.0, 1.3)
        if frei and frei[0] <= x <= frei[1] and frei[2] <= y <= frei[3]:
            continue
        props.stehende_figur(
            f"Figur_{gesetzt:03d}", x, y, zufall.uniform(1.58, 1.86),
            m["uniform"], m["haut"], drehung=zufall.uniform(0, math.tau),
        )
        gesetzt += 1


def berge(m, kamera_xy=(0.0, 0.0), saat=28061914):
    """Die Haenge des Talkessels.

    Entfernungen in KILOMETERN. Ein 285 m hoher Kegel in 340 m Abstand
    fuellt 40 Grad Bildwinkel - das Objektiv hat 27 Grad vertikal. Das
    Ergebnis war eine blaue Wand, die zusaetzlich die Strasse verschattete.
    Der Mindestabstand wird deshalb gemessen und gemeldet.
    """
    zufall = random.Random(saat)
    reihen = [
        (-4200, 3200, -2400, 5, 420, 1800),
        (-3000, 4500, -3900, 4, 640, 2500),
        (2800, 6200, -900, 3, 520, 2100),
    ]
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
            ob.data.materials.append(m["berg"])
            naechster = min(naechster, math.dist((x, y_k), kamera_xy) - breite / 2)

    print(f"  Berge: naechster Rand {naechster:.0f} m vor der Kamera")
    if naechster < 1200:
        print("  WARNUNG: Berg zu nah - er verdeckt den Himmel und wirft "
              "Schatten auf die Strasse.")


# --------------------------------------------------------------------------
# Appelkai - Shots 03, 04, 05
# --------------------------------------------------------------------------


def appelkai(scene, m, kamera_xy=(-34.0, -4.6), mit_menge=True, frei=None):
    """Die Uferstrasse an der Miljacka.

    Fahrbahn, zwei Gehwege, Bruestung, Fluss, Haeuserzeile im Norden,
    Gaslaternen am Ufer. An einer dieser Laternen schlaegt Cabrinovic in
    Shot 04 die Granate an.
    """
    props.quader("Fahrbahn", (0, 0, 0), (260, 14, 0.3), m["stein"])
    props.quader("Gehweg_Haus", (0, 8.6, 0.22), (260, 3.2, 0.44), m["kalk"])
    props.quader("Gehweg_Fluss", (0, -8.4, 0.22), (260, 2.8, 0.44), m["kalk"])
    props.quader("Bruestung", (0, -9.9, 0.62), (260, 0.5, 1.05), m["kalk"])

    props.quader("Kaimauer", (0, -13.5, -1.4), (260, 0.7, 3.4), m["kalk"])
    props.quader("Miljacka", (0, -22, -2.05), (260, 17, 0.1), m["wasser"])
    props.quader("Ufer_fern", (0, -34, -1.2), (260, 8, 2.2), m["kalk"])

    berge(m, kamera_xy)
    fassadenzeile(m)
    for k in range(-7, 8):
        props.laterne(f"Laterne_{k}", k * 18.0, -9.2, m["messing"], m["glas"])
    if mit_menge:
        menge(m, frei=frei)

    licht.sonne()
    licht.himmel(scene)
    # Nebel NUR ueber dem Wasser. Steht die Kamera im Volumenkoerper, ist er
    # keine Atmosphaere mehr, sondern ein Vorhang vor dem Objektiv.
    licht.hoehenrauch(mitte=(0, -24, 2.5), groesse=(260, 24, 5))


def laternenpfahl_x(index: int = -1) -> float:
    """X-Position einer Laterne. Shot 04 braucht genau die, an der die
    Granate angeschlagen wird - Shot 05 muss dieselbe treffen."""
    return index * 18.0


# --------------------------------------------------------------------------
# Ecke Franz-Joseph-Strasse - Shots 09, 10, 11
# --------------------------------------------------------------------------


def franz_joseph_ecke(scene, m, kamera_xy=(-16.0, -12.0)):
    """Die Ecke, an der alles endet.

    Der Appelkai laeuft weiter nach Osten (+X); die Franz-Joseph-Strasse
    zweigt nach Norden (+Y) ab. Genau in diese Abzweigung biegen die
    Fahrer faelschlich ein. An der Ecke steht der Delikatessenladen von
    Moritz Schiller - er ist hell abgesetzt, damit man ihn wiedererkennt,
    wenn Shot 10 dort haelt.
    """
    props.quader("Fahrbahn", (0, 0, 0), (200, 14, 0.3), m["stein"])
    props.quader("Gehweg_Fluss", (0, -8.4, 0.22), (200, 2.8, 0.44), m["kalk"])
    props.quader("Bruestung", (0, -9.9, 0.62), (200, 0.5, 1.05), m["kalk"])
    props.quader("Kaimauer", (0, -13.5, -1.4), (200, 0.7, 3.4), m["kalk"])
    props.quader("Miljacka", (0, -22, -2.05), (200, 17, 0.1), m["wasser"])

    # Die abzweigende Strasse. Sie MUSS als Oeffnung lesbar sein - das
    # falsche Abbiegen ist der didaktische Kern des Beats.
    GASSE_X = 0.0
    GASSE_BREITE = 9.0
    props.quader("Gasse_Fahrbahn", (GASSE_X, 26, 0.02), (GASSE_BREITE, 40, 0.3), m["stein"])

    # Haeuserzeile links und rechts der Oeffnung
    fassadenzeile(m, x_von=-100, x_bis=GASSE_X - GASSE_BREITE / 2, saat=0)
    fassadenzeile(m, x_von=GASSE_X + GASSE_BREITE / 2, x_bis=100, saat=3)
    # Zeile entlang der Gasse, damit sie Tiefe bekommt
    _gassenzeile(m, GASSE_X - GASSE_BREITE / 2, 12.0, 46.0, links=True)
    _gassenzeile(m, GASSE_X + GASSE_BREITE / 2, 12.0, 46.0, links=False)

    _schillers_laden(m, GASSE_X + GASSE_BREITE / 2 + 5.0)

    berge(m, kamera_xy)
    for k in range(-5, 6):
        props.laterne(f"Laterne_{k}", k * 18.0, -9.2, m["messing"], m["glas"])
    menge(m, anzahl=120, x_von=-70, x_bis=70)

    licht.sonne()
    licht.himmel(scene)
    licht.hoehenrauch(mitte=(0, -24, 2.5), groesse=(200, 24, 5))
    return GASSE_X


def _gassenzeile(m, x_kante, y_von, y_bis, links: bool):
    """Haeuser entlang der abzweigenden Gasse, damit sie Tiefe hat."""
    y = y_von
    i = 40 if links else 60
    seite = -1 if links else 1
    while y < y_bis:
        tiefe = 9.0 + (i % 3) * 3.0
        hoehe = 12.0 + (i % 4) * 2.6
        props.quader(
            f"Gassenhaus_{i}", (x_kante + seite * 6.0, y + tiefe / 2, hoehe / 2),
            (12.0, tiefe, hoehe), m["putze"][i % len(m["putze"])],
        )
        y += tiefe
        i += 1


def _schillers_laden(m, x):
    """Der Delikatessenladen von Moritz Schiller an der Ecke.

    Bewusst hell und mit Markise abgesetzt: Shot 10 haelt genau davor, und
    der Zuschauer muss den Ort wiedererkennen, ohne dass ihn jemand nennt.
    """
    props.quader("Schiller_Front", (x, 10.6, 2.3), (11.0, 0.5, 4.6), m["kalk"])
    props.quader("Schiller_Schaufenster", (x, 10.28, 2.1), (7.2, 0.3, 2.8), m["glas"])
    props.quader("Schiller_Markise", (x, 9.0, 3.55), (8.4, 2.6, 0.18), m["standarte"])
    for k in (-1, 1):
        props.quader(f"Schiller_Stuetze{k}", (x + k * 4.0, 7.8, 1.9),
                     (0.12, 0.12, 3.8), m["messing"])
