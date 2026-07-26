"""Score und Geraeuschkulisse je Beat, zur Bauzeit synthetisiert.

    python audio/score.py --all         Alle acht Klangbetten
    python audio/score.py --beat 2      Nur einen Beat neu bauen
    python audio/score.py --list        Zeigen, was gebaut wuerde
    python audio/score.py --cues        Zeigen, wann welcher Klang einsetzt

Zwei Grundsaetze:

1. Die Laenge jedes Betts kommt aus beats.js - dieselbe Quelle wie die
   Shot-Dauern. Aendert sich dort etwas, zieht der Ton beim naechsten Lauf
   automatisch nach.

2. WAS DER TEXT BESCHREIBT, SOLL MAN HOEREN - auch das, was nicht im Bild
   ist. Eine erwaehnte Schlacht kann als Klang praesent sein, ohne dass ein
   Bild davon noetig waere. Die Einsatzzeiten werden dafuer nicht geraten,
   sondern aus der Zeichenposition der Phrase im Sprechertext geschaetzt
   (siehe wortzeit).

Bewusst flaechig komponiert: Drones, Glocken, Perkussion, Texturen. Das kann
Synthese wirklich gut, melodische Orchestrierung nicht - und es passt zum
Stoff besser als Filmmusik-Pathos. Die Musik traegt, sie erzaehlt nicht.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import synth as s  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEATS_JS = PROJECT_ROOT / "web" / "src" / "beats.js"
OUT_DIR = PROJECT_ROOT / "media" / "audio"

# Tonartzentrum d-moll: dunkel, ohne larmoyant zu sein.
D1, A1, D2, F2, A2, D3, F3, A3 = 36.71, 55.0, 73.42, 87.31, 110.0, 146.83, 174.61, 220.0


# --------------------------------------------------------------------------
# Beat-Daten und Wort-Timing
# --------------------------------------------------------------------------


def beat_daten() -> list[dict]:
    """Beats aus beats.js: Laenge, Titel, Sprechertext, Sprechdauer.

    Die Bettlaenge ist Video PLUS Modulzeit, mindestens aber die Sprechdauer
    plus zwei Sekunden - bei den Beats mit interaktivem Modul traegt das
    Modul einen Teil der Zeit, und der Ton muss dort weiterlaufen. Rechnet
    man nur mit den Shots, bricht der Score in Beat 7 nach 14 von 50
    Sekunden ab.
    """
    script = (
        "import('file:///' + process.argv[1].replace(/\\\\/g, '/'))"
        ".then(m => console.log(JSON.stringify(m.BEATS.map(b => ({"
        "id: b.id, titel: b.title,"
        "dauer: Math.max("
        "  b.shots.reduce((a,x)=>a+x.duration,0) + (b.module?.seconds ?? 0),"
        "  Math.ceil(b.narration.seconds) + 2),"
        "text: b.narration.text, sprechdauer: b.narration.seconds"
        "})))))"
    )
    result = subprocess.run(
        ["node", "-e", script, str(BEATS_JS)],
        capture_output=True, text=True, encoding="utf-8", cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        sys.exit(f"beats.js konnte nicht gelesen werden:\n{result.stderr}")
    return json.loads(result.stdout)


def _pausen(text: str) -> float:
    """Gewichtete Zahl der Sprechpausen. Punkte trennen mehr als Kommas."""
    return (
        text.count(".") + text.count("!") + text.count("?")
        + 0.5 * text.count(",") + 0.8 * text.count("—")
    )


def wortzeit(text: str, phrase: str, sprechdauer: float, pause: float = 0.32) -> float | None:
    """Geschaetzte Sekunde, in der `phrase` gesprochen wird.

    Modell: die Sprechzeit verteilt sich gleichmaessig auf die Zeichen, plus
    eine feste Pause je Satzzeichen. Reine Zeichenzaehlung waere zu
    optimistisch, weil die Sprachsynthese an Punkten deutlich innehaelt und
    spaetere Phrasen dadurch nach hinten wandern.

    Genauigkeit etwa eine Sekunde - genug, damit ein Klang auf seinem Wort
    liegt und nicht daneben. Liefert None, wenn die Phrase nicht vorkommt;
    die Aufrufer muessen damit rechnen, denn Texte werden redigiert.
    """
    i = text.find(phrase)
    if i < 0:
        return None
    vor = text[:i]
    pausen_gesamt = _pausen(text)
    pausen_vor = _pausen(vor)
    rein_gesprochen = max(1.0, sprechdauer - pausen_gesamt * pause)
    anteil = len(vor) / max(1, len(text))
    return anteil * rein_gesprochen + pausen_vor * pause


def _cue(beat: dict, phrase: str, rueckfall: float) -> float:
    """Wortzeit mit Rueckfall, damit ein redigierter Text nichts zerstoert."""
    zeit = wortzeit(beat["text"], phrase, beat["sprechdauer"])
    return rueckfall if zeit is None else zeit


# --------------------------------------------------------------------------
# Die acht Klangbetten
# --------------------------------------------------------------------------


def beat_0_prolog(beat: dict) -> np.ndarray:
    """Morgen ueber Sarajevo - und darunter, bei der Erwaehnung des Kosovo
    Polje, eine ferne Schlacht als Erinnerung."""
    dur = beat["dauer"]
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(A1, dur, detune=0.35), dur), 0, 0.5)
    s.place(bed, s.pad_to(s.drone(D2, dur * 0.8, detune=0.5), dur * 0.8), dur * 0.15, 0.22)

    # Erwachende Stadt
    s.place(bed, s.pad_to(s.voegel(dur * 0.75), dur * 0.75), 0.5, 0.55)
    s.place(bed, s.bell(196.0, 7.0), 1.5, 0.30)
    s.place(bed, s.bell(196.0, 7.0), 3.1, 0.16)

    # Die Schlacht auf dem Kosovo Polje, 1389 - weit weg, wie eine Erinnerung
    kosovo = _cue(beat, "Kosovo Polje", dur * 0.55)
    s.place(bed, s.schlacht_fern(11.0), max(0.0, kosovo - 3.0), 0.85)

    for at, f, seed in ((6.0, D3, 21), (13.0, A2, 23), (dur - 12, D3, 24)):
        s.place(bed, s.karplus(f, 4.0, seed=seed), max(0.0, at), 0.26)
    s.place(bed, s.bell(146.83, 8.0), dur - 9, 0.20)
    return bed


def beat_1_ankunft(beat: dict) -> np.ndarray:
    """Bahnhof: Dampf, Pfiff, Schritte, Menge, Militaerkapelle, dann der Wagen."""
    dur = beat["dauer"]
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(D2, dur, detune=0.3), dur), 0, 0.20)

    zug = _cue(beat, "Der Zug hält", 1.0)
    s.place(bed, s.steam(16.0), max(0.0, zug - 1.5), 0.85)
    s.place(bed, s.pfiff(), max(0.0, zug + 0.6), 0.5)

    s.place(bed, s.pad_to(s.crowd(dur - 2), dur - 2), 2.0, 0.55)
    s.place(bed, s.schritte(9.0), zug + 6.0, 0.45)

    s.place(bed, s.reverb(s.fanfare(2.4), 2.0, 0.35), dur * 0.42, 0.55)
    s.place(bed, s.reverb(s.fanfare(2.4, root=261.63, seed=5), 2.0, 0.35), dur * 0.48, 0.42)
    s.place(bed, s.engine(max(2.0, dur - dur * 0.72)), dur * 0.72, 0.5)
    return bed


def beat_2_granate(beat: dict) -> np.ndarray:
    """Der erste Anschlag.

    Die drei Marken sitzen auf ihren Woertern: das metallische Klacken am
    Laternenpfahl, danach der Zuender, dann die Detonation. Der Abstand
    zwischen Klacken und Knall ergibt sich aus dem Text und ist damit
    automatisch die dramatische Uhr, die die Erzaehlung ankuendigt.
    """
    dur = beat["dauer"]
    bed = s.silence(dur)

    pfahl = _cue(beat, "Laternenpfahl", dur * 0.35)
    zehn = _cue(beat, "zehn Sekunden", dur * 0.42)
    knall = _cue(beat, "detoniert", dur * 0.55)
    sprung = _cue(beat, "springt in die Miljacka", dur * 0.78)

    s.place(bed, s.pad_to(s.drone(D2, knall + 2, detune=0.6), knall + 2), 0, 0.28)
    s.place(bed, s.engine(max(2.0, knall)), 0.0, 0.55)
    s.place(bed, s.crowd(max(2.0, knall - 1)), 0.5, 0.45)
    s.place(bed, s.pad_to(s.fluss(dur), dur), 0, 0.5)

    # Metall gegen Metall, genau auf dem Wort
    s.place(bed, s.klacken(), pfahl, 0.9)

    # GENAU ZEHN TICKS, beginnend auf dem Wort "zehn Sekunden".
    #
    # Chronologisch startet der Zuender schon am Laternenpfahl, aber
    # zwischen Anschlag und Detonation liegen im Sprechertext knapp 18
    # Sekunden. Wuerde der Zuender die ganze Strecke ticken, zaehlte ein
    # mitzaehlender Schueler achtzehn - waehrend der Erzaehler von zehn
    # spricht. Die Ticks liegen deshalb auf dem Wort, nicht auf der
    # Chronologie. Der Rest bis zum Knall ist Stille: die angehaltene Luft
    # nach dem letzten Tick wirkt staerker als weitere Ticks es koennten.
    s.place(bed, s.fuse_ticks(10.0, rate=1.0), zehn, 0.85)

    s.place(bed, s.blast(3.6), knall, 1.0)
    s.place(bed, s.tinnitus(max(2.0, dur - knall - 1), 3900), knall + 0.05, 0.55)

    # Nach dem Knall: die Welt gedaempft
    rest = dur - knall - 2
    if rest > 1:
        s.place(bed, s.lowpass(s.crowd(rest, seed=31), 700), knall + 2, 0.5)
        s.place(bed, s.lowpass(s.drone(D1, rest, detune=0.8), 200), knall + 2, 0.35)

    # Zyankali wirkt nicht, der Fluss ist zentimetertief
    s.place(bed, s.platschen(), sprung, 0.75)
    return bed


def beat_3_rathaus(beat: dict) -> np.ndarray:
    """Halle: wenig Klang, viel Raum. Der Nachhall macht den Saal."""
    dur = beat["dauer"]
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(A1, dur, detune=0.25, cutoff=260), dur), 0, 0.34)
    s.place(bed, s.reverb(s.crowd(dur - 4, seed=32), 2.4, 0.55), 1.0, 0.28)
    s.place(bed, s.reverb(s.schritte(7.0), 2.6, 0.5), 0.8, 0.4)
    for at, f, seed in ((4.0, F3, 25), (14.0, D3, 26), (28.0, A2, 27)):
        if at < dur - 5:
            s.place(bed, s.reverb(s.karplus(f, 5.0, seed=seed), 2.2, 0.4), at, 0.24)
    # Ein einzelner Paukenschlag, als die Entscheidung faellt
    s.place(bed, s.thump(D1, 2.5), dur - 8, 0.4)
    return bed


def beat_4_route(beat: dict) -> np.ndarray:
    """Die Fahrt in die falsche Strasse. Der Ruf, dann das Anhalten."""
    dur = beat["dauer"]
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(D2, dur, detune=0.7), dur), 0, 0.38)
    s.place(bed, s.engine(max(2.0, dur - 4)), 0.0, 0.5)
    s.place(bed, s.crowd(max(2.0, dur - 6), seed=33), 1.0, 0.3)
    s.place(bed, s.snare_roll(max(3.0, dur - 18)), 16.0, 0.35)

    # Graf Harrach ruft dem Chauffeur zu, er sei falsch abgebogen
    zuruf = _cue(beat, "falsch abgebogen", dur * 0.62)
    s.place(bed, s.ruf(), max(0.0, zuruf - 0.4), 0.7)
    s.place(bed, s.ruf(1.3, seed=44), max(0.0, zuruf + 1.2), 0.45)

    # Der Wagen haelt: Motor faellt weg, ein Schlag bleibt
    s.place(bed, s.thump(A1, 3.0), dur - 4.5, 0.55)
    return bed


def beat_5_schuesse(beat: dict) -> np.ndarray:
    """Alles faellt weg bis auf den Herzschlag. Zwei Zeichen. Dann nichts.

    Bewusst KEINE Musik nach den Schuessen: die Stille traegt mehr als jede
    Streicherflaeche es koennte.
    """
    dur = beat["dauer"]
    bed = s.silence(dur)
    schuss = _cue(beat, "gibt zwei Schüsse ab", dur * 0.62)

    s.place(bed, s.engine(9.0), 0.0, 0.4)
    s.place(bed, s.crowd(8.0, seed=34), 0.0, 0.28)
    s.place(bed, s.pad_to(s.drone(D1, schuss, detune=0.9, cutoff=180), schuss), 0, 0.34)

    # Ab hier nur noch der eigene Puls
    s.place(bed, s.heartbeat(max(3.0, schuss - 7), bpm=54), 7.0, 0.6)

    s.place(bed, s.shot(seed=41), schuss, 0.9)
    s.place(bed, s.shot(seed=42), schuss + 0.7, 0.85)

    nach = dur - schuss - 2
    if nach > 2:
        s.place(bed, s.pad_to(s.drone(D1, nach, detune=0.2, cutoff=120), nach), schuss + 2, 0.20)
    return bed


def beat_6_epilog(beat: dict) -> np.ndarray:
    """Der Funke greift ueber.

    Telegrafenklicken unter den Julikrise-Daten - die Ultimaten gingen per
    Telegraf. Am Ende ferner Artilleriedonner als Bruecke zur Westfront.
    """
    dur = beat["dauer"]
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(A1, dur, detune=0.5), dur), 0, 0.42)
    s.place(bed, s.pad_to(s.drone(F2, dur * 0.7, detune=0.4), dur * 0.7), dur * 0.3, 0.26)

    daten_start = _cue(beat, "23. Juli", dur * 0.18)
    krieg = _cue(beat, "vier Jahre dauern", dur * 0.86)

    # Depeschen zwischen den Hauptstaedten
    s.place(bed, s.telegraf(max(4.0, krieg - daten_start - 2)), daten_start, 0.55)

    # Fuenf Schlaege fuer die fuenf Kriegserklaerungen
    spanne = max(6.0, (krieg - daten_start) * 0.85)
    for k in range(5):
        at = daten_start + k * spanne / 5
        s.place(bed, s.thump(D1 * (1 + 0.04 * k), 3.0), at, 0.5 + 0.09 * k)
        s.place(bed, s.bell(146.83 * (1 + 0.02 * k), 6.0, seed=50 + k), at + 0.15, 0.28)

    # Uebergang zur Westfront
    s.place(bed, s.artillerie_fern(max(4.0, dur - krieg + 2)), max(0.0, krieg - 2), 0.6)
    s.place(bed, s.snare_roll(7.0), max(0.0, dur - 8), 0.35)
    return bed


def beat_7_auswertung(beat: dict) -> np.ndarray:
    """Die Frage bleibt offen. Kein Schluss-Akkord."""
    dur = beat["dauer"]
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(D2, dur, detune=0.3, cutoff=280), dur), 0, 0.36)
    s.place(bed, s.karplus(D3, 5.0, seed=28), 1.0, 0.3)
    s.place(bed, s.karplus(A2, 5.0, seed=29), dur * 0.3, 0.26)
    # Letzter Ton bewusst ohne Aufloesung
    s.place(bed, s.karplus(F3, 6.0, seed=30), dur * 0.62, 0.22)
    return bed


BEDS = {
    0: beat_0_prolog,
    1: beat_1_ankunft,
    2: beat_2_granate,
    3: beat_3_rathaus,
    4: beat_4_route,
    5: beat_5_schuesse,
    6: beat_6_epilog,
    7: beat_7_auswertung,
}

# Phrasen, deren Einsatzzeit gemeldet werden soll (--cues)
CUES = {
    0: ["Kosovo Polje"],
    1: ["Der Zug hält"],
    2: ["Laternenpfahl", "zehn Sekunden", "detoniert", "springt in die Miljacka"],
    4: ["falsch abgebogen"],
    5: ["gibt zwei Schüsse ab"],
    6: ["23. Juli", "vier Jahre dauern"],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Score und Geraeusche bauen")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--beat", type=int)
    group.add_argument("--list", action="store_true")
    group.add_argument("--cues", action="store_true")
    args = parser.parse_args()

    beats = beat_daten()

    if args.list:
        print(f"{'Beat':>4s} {'Bett':>7s} {'Sprache':>9s}  Titel")
        for b in beats:
            print(f"{b['id']:4d} {b['dauer']:6.0f}s {b['sprechdauer']:8.1f}s  {b['titel']}")
        return

    if args.cues:
        print("Geschaetzte Einsatzzeiten (aus Zeichenposition im Sprechertext):\n")
        for b in beats:
            if b["id"] not in CUES:
                continue
            print(f"  Beat {b['id']}  ({b['sprechdauer']:.1f}s Sprache)")
            for phrase in CUES[b["id"]]:
                zeit = wortzeit(b["text"], phrase, b["sprechdauer"])
                wert = f"{zeit:6.1f}s" if zeit is not None else " nicht gefunden"
                print(f"    {wert}  {phrase}")
        return

    for b in beats:
        if args.beat is not None and b["id"] != args.beat:
            continue
        bed = BEDS[b["id"]](b)
        path = OUT_DIR / f"score_{b['id']:02d}.mp3"
        groesse = s.write_mp3(bed, path)
        print(
            f"Beat {b['id']}  {b['dauer']:5.0f}s  {b['titel'][:30]:30s} "
            f"{groesse // 1024:5d} KB  Peak {float(np.max(np.abs(bed))):4.2f}  "
            f"RMS {float(np.sqrt(np.mean(bed**2))):.3f}"
        )


if __name__ == "__main__":
    main()
