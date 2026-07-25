"""Score und Geraeusche je Beat, zur Bauzeit synthetisiert.

    python audio/score.py --all         Alle acht Klangbetten
    python audio/score.py --beat 2      Nur einen Beat neu bauen
    python audio/score.py --list        Nur zeigen, was gebaut wuerde

Die Laenge jedes Betts kommt aus beats.js - dieselbe Quelle, aus der auch
die Shot-Dauern stammen. Aendert sich dort eine Dauer, wird der Ton beim
naechsten Lauf automatisch mitgezogen.

Bewusst flaechig komponiert: Drones, Glocken, Perkussion, Texturen. Das
ist, was Synthese wirklich gut kann - und es passt zum Stoff besser als
Filmmusik-Pathos. Die Musik traegt, sie erzaehlt nicht.
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


def beat_durations() -> list[tuple[int, float, str]]:
    """(id, Sekunden, Titel) aus beats.js - die einzige Inhaltsquelle.

    Die Laenge ist Video PLUS Modulzeit, nicht nur Video: bei den Beats mit
    interaktivem Modul traegt das Modul einen Teil der Zeit, und der Ton
    muss auch dort weiterlaufen. Rechnet man nur mit den Shots, bricht der
    Score in Beat 7 nach 14 von 50 Sekunden ab.

    Zusaetzlich wird die gemessene Sprechdauer als Untergrenze genommen -
    der Ton darf nie vor der Stimme enden.
    """
    script = (
        "import('file:///' + process.argv[1].replace(/\\\\/g, '/'))"
        ".then(m => console.log(JSON.stringify(m.BEATS.map(b => ["
        "b.id,"
        "Math.max("
        "  b.shots.reduce((a,x)=>a+x.duration,0) + (b.module?.seconds ?? 0),"
        "  Math.ceil(b.narration.seconds) + 2"
        "),"
        "b.title]))))"
    )
    result = subprocess.run(
        ["node", "-e", script, str(BEATS_JS)],
        capture_output=True, text=True, encoding="utf-8", cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        sys.exit(f"beats.js konnte nicht gelesen werden:\n{result.stderr}")
    return [(int(a), float(b), c) for a, b, c in json.loads(result.stdout)]


# --------------------------------------------------------------------------
# Die acht Klangbetten
# --------------------------------------------------------------------------


def beat_0_prolog(dur: float) -> np.ndarray:
    """Morgen ueber Sarajevo. Weit, still, eine Glocke in der Ferne."""
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(A1, dur, detune=0.35), dur), 0, 0.5)
    s.place(bed, s.pad_to(s.drone(D2, dur * 0.8, detune=0.5), dur * 0.8), dur * 0.15, 0.22)
    s.place(bed, s.bell(196.0, 7.0), 1.5, 0.30)
    s.place(bed, s.bell(196.0, 7.0), 3.1, 0.16)
    s.place(bed, s.bell(146.83, 8.0), dur - 9, 0.20)
    # Tambura: einzelne Toene, viel Luft dazwischen
    for at, f, seed in ((6.0, D3, 21), (9.4, F3, 22), (13.0, A2, 23), (19.5, D3, 24)):
        s.place(bed, s.karplus(f, 4.0, seed=seed), at, 0.26)
    return bed


def beat_1_ankunft(dur: float) -> np.ndarray:
    """Bahnhof: Dampf, Menge, eine Militaerkapelle, dann der Wagen."""
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(D2, dur, detune=0.3), dur), 0, 0.20)
    s.place(bed, s.steam(14.0), 0.0, 0.85)
    s.place(bed, s.pad_to(s.crowd(dur - 2), dur - 2), 2.0, 0.55)
    s.place(bed, s.reverb(s.fanfare(2.4), 2.0, 0.35), 15.5, 0.55)
    s.place(bed, s.reverb(s.fanfare(2.4, root=261.63, seed=5), 2.0, 0.35), 18.4, 0.42)
    s.place(bed, s.engine(dur - 24), 24.0, 0.5)
    return bed


def beat_2_granate(dur: float) -> np.ndarray:
    """Der erste Anschlag. Der Zuender ist der Hauptdarsteller.

    Aufbau: Fahrt - zehn tickende Sekunden - Detonation - Tinnitus, und
    danach liegt alles unter einem Tiefpass, als haette man selbst danebengestanden.
    """
    bed = s.silence(dur)
    detonation = 30.0
    tick_start = detonation - 10.0

    s.place(bed, s.pad_to(s.drone(D2, detonation + 2, detune=0.6), detonation + 2), 0, 0.28)
    s.place(bed, s.engine(detonation), 0.0, 0.55)
    s.place(bed, s.crowd(detonation - 1), 0.5, 0.45)

    # Zehn Sekunden. Die Schueler zaehlen mit.
    s.place(bed, s.fuse_ticks(10.0, rate=1.0), tick_start, 0.85)

    s.place(bed, s.blast(3.6), detonation, 1.0)
    s.place(bed, s.tinnitus(dur - detonation - 1, 3900), detonation + 0.05, 0.55)

    # Nach dem Knall: die Welt gedaempft. Menge und Motor unter Tiefpass.
    rest = dur - detonation - 2
    if rest > 1:
        gedaempft = s.lowpass(s.crowd(rest, seed=31), 700)
        s.place(bed, gedaempft, detonation + 2, 0.5)
        s.place(bed, s.lowpass(s.drone(D1, rest, detune=0.8), 200), detonation + 2, 0.35)
    return bed


def beat_3_rathaus(dur: float) -> np.ndarray:
    """Halle: wenig Klang, viel Raum. Der Nachhall macht den Saal."""
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(A1, dur, detune=0.25, cutoff=260), dur), 0, 0.34)
    hall = s.reverb(s.crowd(dur - 4, seed=32), 2.4, 0.55)
    s.place(bed, hall, 1.0, 0.28)
    for at, f, seed in ((4.0, F3, 25), (12.0, D3, 26), (24.0, A2, 27)):
        s.place(bed, s.reverb(s.karplus(f, 5.0, seed=seed), 2.2, 0.4), at, 0.24)
    # Ein einzelner Timpani-Schlag, als die Entscheidung faellt
    s.place(bed, s.thump(D1, 2.5), dur - 8, 0.4)
    return bed


def beat_4_route(dur: float) -> np.ndarray:
    """Die Fahrt in die falsche Strasse. Der Wirbel zieht an."""
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(D2, dur, detune=0.7), dur), 0, 0.38)
    s.place(bed, s.engine(dur - 4), 0.0, 0.5)
    s.place(bed, s.crowd(dur - 6, seed=33), 1.0, 0.3)
    s.place(bed, s.snare_roll(dur - 18), 16.0, 0.35)
    # Der Wagen haelt: Motor faellt weg, ein Schlag bleibt
    s.place(bed, s.thump(A1, 3.0), dur - 4.5, 0.55)
    return bed


def beat_5_schuesse(dur: float) -> np.ndarray:
    """Alles faellt weg bis auf den Herzschlag. Zwei Zeichen. Dann nichts.

    Bewusst KEINE Musik nach den Schuessen: die Stille traegt mehr als
    jede Streicherflaeche es koennte.
    """
    bed = s.silence(dur)
    schuss = 26.0

    s.place(bed, s.engine(9.0), 0.0, 0.4)
    s.place(bed, s.crowd(8.0, seed=34), 0.0, 0.28)
    s.place(bed, s.pad_to(s.drone(D1, schuss, detune=0.9, cutoff=180), schuss), 0, 0.34)

    # Ab hier nur noch der eigene Puls
    s.place(bed, s.heartbeat(schuss - 7, bpm=54), 7.0, 0.6)

    s.place(bed, s.shot(seed=41), schuss, 0.9)
    s.place(bed, s.shot(seed=42), schuss + 0.7, 0.85)

    # Danach: sehr leise, sehr tief, fast nichts
    nach = dur - schuss - 2
    if nach > 2:
        s.place(bed, s.pad_to(s.drone(D1, nach, detune=0.2, cutoff=120), nach), schuss + 2, 0.20)
    return bed


def beat_6_epilog(dur: float) -> np.ndarray:
    """Der Funke greift ueber. Glocken und Paukenschlaege als Daten."""
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(A1, dur, detune=0.5), dur), 0, 0.42)
    s.place(bed, s.pad_to(s.drone(F2, dur * 0.7, detune=0.4), dur * 0.7), dur * 0.3, 0.26)

    # Fuenf Schlaege fuer die fuenf Kriegserklaerungen der Julikrise
    for k, at in enumerate((4.0, 8.5, 13.0, 17.5, 22.0)):
        s.place(bed, s.thump(D1 * (1 + 0.04 * k), 3.0), at, 0.5 + 0.09 * k)
        s.place(bed, s.bell(146.83 * (1 + 0.02 * k), 6.0, seed=50 + k), at + 0.15, 0.28)

    s.place(bed, s.snare_roll(8.0), dur - 9, 0.4)
    return bed


def beat_7_auswertung(dur: float) -> np.ndarray:
    """Die Frage bleibt offen. Kein Schluss-Akkord."""
    bed = s.silence(dur)
    s.place(bed, s.pad_to(s.drone(D2, dur, detune=0.3, cutoff=280), dur), 0, 0.36)
    s.place(bed, s.karplus(D3, 5.0, seed=28), 1.0, 0.3)
    s.place(bed, s.karplus(A2, 5.0, seed=29), 5.2, 0.26)
    # Letzter Ton bewusst ohne Aufloesung
    s.place(bed, s.karplus(F3, 6.0, seed=30), 9.0, 0.22)
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Score und Geraeusche bauen")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--beat", type=int)
    group.add_argument("--list", action="store_true")
    args = parser.parse_args()

    beats = beat_durations()

    if args.list:
        print(f"{'Beat':>4s} {'Dauer':>7s}  Titel")
        for bid, dur, title in beats:
            print(f"{bid:4d} {dur:6.0f}s  {title}")
        return

    for bid, dur, title in beats:
        if args.beat is not None and bid != args.beat:
            continue
        bed = BEDS[bid](dur)
        path = OUT_DIR / f"score_{bid:02d}.mp3"
        size = s.write_mp3(bed, path)
        peak = float(np.max(np.abs(bed)))
        rms = float(np.sqrt(np.mean(bed**2)))
        print(
            f"Beat {bid}  {dur:5.0f}s  {title[:32]:32s} "
            f"{size // 1024:5d} KB  Peak {peak:4.2f}  RMS {rms:.3f}"
        )


if __name__ == "__main__":
    main()
