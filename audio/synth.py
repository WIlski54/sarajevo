"""Klangbausteine, zur Bauzeit synthetisiert.

Kein Download, keine Samplebibliothek, keine Lizenzfrage - und
deterministisch: derselbe Aufruf ergibt denselben Klang.

Bewusste Beschraenkung: Synthese traegt Flaechen, Glocken, Perkussion und
Texturen gut, melodische Orchestrierung nicht. Der Score ist deshalb
flaechig und sparsam angelegt - was zum Stoff ohnehin besser passt als
Filmmusik-Pathos.

Alle Funktionen geben float32-Arrays in [-1, 1] zurueck, mono, SR = 44100.
Stereo entsteht erst beim Schreiben (siehe to_stereo).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from scipy import signal

SR = 44_100


# --------------------------------------------------------------------------
# Grundlagen
# --------------------------------------------------------------------------


def t(dur: float) -> np.ndarray:
    """Zeitachse in Sekunden."""
    return np.arange(int(SR * dur), dtype=np.float32) / SR


def silence(dur: float) -> np.ndarray:
    return np.zeros(int(SR * dur), dtype=np.float32)


def rng(seed: int) -> np.random.Generator:
    """Fester Zufallsstrom - gleiche Saat, gleicher Klang."""
    return np.random.default_rng(seed)


def adsr(
    n: int, attack: float, decay: float, sustain: float, release: float
) -> np.ndarray:
    """Huellkurve ueber n Samples. Zeiten in Sekunden, sustain als Pegel."""
    a, d, r = int(SR * attack), int(SR * decay), int(SR * release)
    s = max(0, n - a - d - r)
    return np.concatenate(
        [
            np.linspace(0, 1, a, dtype=np.float32),
            np.linspace(1, sustain, d, dtype=np.float32),
            np.full(s, sustain, dtype=np.float32),
            np.linspace(sustain, 0, r, dtype=np.float32),
        ]
    )[:n]


def fade(x: np.ndarray, sec_in: float = 0.02, sec_out: float = 0.05) -> np.ndarray:
    """Kanten entschaerfen - ohne das knackt jeder Schnitt."""
    y = x.copy()
    n_in, n_out = int(SR * sec_in), int(SR * sec_out)
    if n_in > 0:
        y[:n_in] *= np.linspace(0, 1, n_in, dtype=np.float32)
    if n_out > 0:
        y[-n_out:] *= np.linspace(1, 0, n_out, dtype=np.float32)
    return y


def lowpass(x: np.ndarray, cutoff: float, order: int = 4) -> np.ndarray:
    b, a = signal.butter(order, min(cutoff, SR / 2 - 100) / (SR / 2), btype="low")
    return signal.filtfilt(b, a, x).astype(np.float32)


def highpass(x: np.ndarray, cutoff: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(order, max(cutoff, 20) / (SR / 2), btype="high")
    return signal.filtfilt(b, a, x).astype(np.float32)


def bandpass(x: np.ndarray, low: float, high: float, order: int = 2) -> np.ndarray:
    b, a = signal.butter(
        order, [max(low, 20) / (SR / 2), min(high, SR / 2 - 100) / (SR / 2)], btype="band"
    )
    return signal.filtfilt(b, a, x).astype(np.float32)


def normalize(x: np.ndarray, peak: float = 0.9) -> np.ndarray:
    m = float(np.max(np.abs(x))) or 1.0
    return (x * (peak / m)).astype(np.float32)


def pad_to(x: np.ndarray, dur: float) -> np.ndarray:
    n = int(SR * dur)
    if len(x) >= n:
        return x[:n]
    return np.concatenate([x, np.zeros(n - len(x), dtype=np.float32)])


def place(bed: np.ndarray, x: np.ndarray, at: float, gain: float = 1.0) -> None:
    """Mischt x ab Sekunde `at` in das Bett. Aendert bed in place."""
    i = int(SR * at)
    j = min(len(bed), i + len(x))
    if i >= len(bed):
        return
    bed[i:j] += x[: j - i] * gain


def reverb(x: np.ndarray, seconds: float = 1.6, mix: float = 0.3, seed: int = 7) -> np.ndarray:
    """Einfacher Faltungshall mit abklingendem Rauschen als Impulsantwort.

    Reicht voellig: gebraucht wird Raumgefuehl (Bahnhofshalle, Rathaus),
    keine akustische Simulation.
    """
    g = rng(seed)
    n = int(SR * seconds)
    ir = g.normal(0, 1, n).astype(np.float32) * np.exp(-np.linspace(0, 6, n, dtype=np.float32))
    ir = lowpass(ir, 4500)
    ir /= np.max(np.abs(ir)) or 1.0
    wet = signal.fftconvolve(x, ir)[: len(x)].astype(np.float32)
    wet /= np.max(np.abs(wet)) or 1.0
    return ((1 - mix) * x + mix * wet * float(np.max(np.abs(x)))).astype(np.float32)


# --------------------------------------------------------------------------
# Tonale Bausteine
# --------------------------------------------------------------------------


def karplus(freq: float, dur: float, damping: float = 0.996, seed: int = 1) -> np.ndarray:
    """Karplus-Strong: gezupfte Saite.

    Traegt die Tambura-/Cimbalom-Farbe, die den Ort und die Zeit setzt,
    ohne dass ein Orchester noetig waere.
    """
    g = rng(seed)
    n = int(SR * dur)
    L = max(2, int(SR / freq))
    # Anregung tiefpassgefiltert: weisses Rauschen klingt im Anschlag nach
    # "tsch" statt nach Saite, weil der Schleifenfilter Dutzende Umlaeufe
    # braucht, um die Hoehen zu glaetten. Gemessen stieg der Anteil unter
    # 1 kHz in den ersten 0,3 s dadurch von 22 % auf ein Vielfaches.
    buf = g.uniform(-1, 1, L).astype(np.float32)
    if L > 8:
        buf = lowpass(buf, 2600, order=2).astype(np.float32)
    # Gleichanteil zwingend entfernen: der Mittelungsfilter der Schleife hat
    # bei 0 Hz Verstaerkung 1, ein Offset klingt also NIE ab, frisst
    # Aussteuerung und wandert in die Summe. Gemessen als Spektralspitze
    # bei 0 Hz, bevor diese Zeile da war.
    buf -= float(np.mean(buf))
    buf /= np.max(np.abs(buf)) or 1.0
    out = np.empty(n, dtype=np.float32)
    idx = 0
    for i in range(n):
        out[i] = buf[idx]
        buf[idx] = damping * 0.5 * (buf[idx] + buf[(idx + 1) % L])
        idx = (idx + 1) % L
    return fade(out * adsr(n, 0.001, 0.05, 0.7, dur * 0.5), 0.001, 0.05)


def drone(freq: float, dur: float, detune: float = 0.4, cutoff: float = 320.0,
          seed: int = 2) -> np.ndarray:
    """Tiefe Streicherflaeche aus verstimmten Saegezaehnen.

    Der Spannungsteppich unter fast allen Beats.
    """
    g = rng(seed)
    time = t(dur)
    out = np.zeros(len(time), dtype=np.float32)
    for k, cents in enumerate((-detune, 0.0, detune, detune * 2.1)):
        f = freq * (2 ** (cents / 12))
        # Langsames Vibrato, damit die Flaeche nicht steht
        vib = 1 + 0.0015 * np.sin(2 * np.pi * (0.13 + 0.05 * k) * time + g.uniform(0, 6))
        phase = 2 * np.pi * f * np.cumsum(vib) / SR
        out += signal.sawtooth(phase).astype(np.float32) * (0.8 ** k)
    out = lowpass(out, cutoff)
    return fade(normalize(out, 0.55), 1.2, 1.6)


def bell(freq: float, dur: float, seed: int = 3) -> np.ndarray:
    """FM-Glocke mit unharmonischen Teiltoenen.

    Kirchenglocke im Prolog, Trauerglocke im Epilog.
    """
    time = t(dur)
    env = np.exp(-time * 1.1).astype(np.float32)
    mod = np.sin(2 * np.pi * freq * 1.41 * time) * np.exp(-time * 3.0)
    out = np.sin(2 * np.pi * freq * time + 6.0 * mod).astype(np.float32) * env
    for ratio, amp in ((2.76, 0.35), (5.4, 0.16), (8.9, 0.07)):
        out += (
            np.sin(2 * np.pi * freq * ratio * time).astype(np.float32)
            * np.exp(-time * (1.4 + ratio * 0.12)).astype(np.float32)
            * amp
        )
    return fade(normalize(out, 0.8), 0.002, 0.3)


def thump(freq: float, dur: float, bend: float = 0.45) -> np.ndarray:
    """Timpani- oder Herzschlag: Sinus mit Tonhoehensturz plus Anschlag."""
    time = t(dur)
    f = freq * (1 + bend * np.exp(-time * 22))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)
    env = np.exp(-time * 7.5).astype(np.float32)
    click = rng(9).normal(0, 1, len(time)).astype(np.float32) * np.exp(-time * 220)
    return fade(normalize(body * env + click * 0.25, 0.85), 0.001, 0.05)


def fanfare(dur: float, root: float = 233.08, seed: int = 4) -> np.ndarray:
    """Knappe Blaskapellen-Figur. Bewusst schlicht und leicht verstimmt -
    eine Militaerkapelle auf einem Bahnsteig, kein Konzertorchester."""
    g = rng(seed)
    out = silence(dur)
    # Naturtonfolge, wie sie eine Signaltrompete spielen kann
    notes = [(0.0, 1.0), (0.34, 1.5), (0.68, 2.0), (1.16, 1.5), (1.5, 2.0)]
    for at, mult in notes:
        n = int(SR * 0.42)
        time = t(0.42)
        f = root * mult * g.uniform(0.997, 1.003)
        tone = np.zeros(n, dtype=np.float32)
        for h, amp in ((1, 1.0), (2, 0.5), (3, 0.28), (4, 0.14), (5, 0.07)):
            tone += np.sin(2 * np.pi * f * h * time).astype(np.float32) * amp
        tone *= adsr(n, 0.02, 0.08, 0.7, 0.16)
        place(out, bandpass(tone, 180, 3200), at, 0.5)
    return fade(normalize(out, 0.7))


# --------------------------------------------------------------------------
# Geraeusche
# --------------------------------------------------------------------------


def crowd(dur: float, seed: int = 11) -> np.ndarray:
    """Menschenmenge: gefiltertes Rauschen mit wandernden Formanten."""
    g = rng(seed)
    base = g.normal(0, 1, int(SR * dur)).astype(np.float32)
    out = bandpass(base, 220, 1900)
    time = t(dur)
    # Langsame Dichteschwankung - eine Menge atmet
    out *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * time + 1.3)).astype(np.float32)
    for f0 in (420.0, 780.0, 1350.0):
        out += bandpass(base, f0 * 0.9, f0 * 1.1) * 0.35
    return fade(normalize(out, 0.32), 0.8, 0.8)


def steam(dur: float, seed: int = 12) -> np.ndarray:
    """Dampflok: Zischen plus Auspuffschlaege, die langsamer werden."""
    g = rng(seed)
    hiss = highpass(g.normal(0, 1, int(SR * dur)).astype(np.float32), 1800)
    out = hiss * 0.25
    at, interval = 0.0, 0.42
    while at < dur - 0.5:
        n = int(SR * 0.3)
        chuff = highpass(g.normal(0, 1, n).astype(np.float32), 400)
        chuff *= np.exp(-t(0.3) * 11).astype(np.float32)
        place(out, chuff, at, 0.8)
        at += interval
        interval *= 1.14  # Die Lok laeuft aus
    return fade(normalize(out, 0.45), 0.3, 1.0)


def engine(dur: float, rpm: float = 8.5, seed: int = 13) -> np.ndarray:
    """Offener Wagen der Epoche: langsam laufender Motor."""
    g = rng(seed)
    time = t(dur)
    wobble = 1 + 0.05 * np.sin(2 * np.pi * 0.6 * time) + 0.02 * g.normal(0, 1, len(time))
    phase = 2 * np.pi * rpm * np.cumsum(wobble) / SR
    out = signal.sawtooth(phase).astype(np.float32)
    for h, amp in ((2, 0.5), (3, 0.3), (5, 0.15)):
        out += signal.sawtooth(phase * h).astype(np.float32) * amp
    out = lowpass(out, 240)
    out += lowpass(g.normal(0, 1, len(time)).astype(np.float32), 900) * 0.12
    return fade(normalize(out, 0.4), 0.5, 0.6)


def fuse_ticks(dur: float, rate: float = 1.0, seed: int = 14) -> np.ndarray:
    """Der Zuender. Zehn Sekunden, hoerbar gemacht.

    Der staerkste Toneffekt der Praesentation: die Schueler zaehlen mit.
    """
    g = rng(seed)
    out = silence(dur)
    at = 0.0
    while at < dur:
        n = int(SR * 0.06)
        click = g.normal(0, 1, n).astype(np.float32) * np.exp(-t(0.06) * 130)
        click = bandpass(click, 1600, 5200)
        # Jeder Schlag etwas lauter - die Zeit wird knapper
        place(out, click, at, 0.55 + 0.45 * (at / max(dur, 0.001)))
        at += 1.0 / rate
    return normalize(out, 0.7)


def blast(dur: float = 3.2, seed: int = 15) -> np.ndarray:
    """Detonation: Knall, Druckwelle, abklingendes Rumpeln."""
    g = rng(seed)
    time = t(dur)
    crack = g.normal(0, 1, len(time)).astype(np.float32) * np.exp(-time * 26)
    body = g.normal(0, 1, len(time)).astype(np.float32) * np.exp(-time * 3.2)
    rumble_f = 46 * (1 + 1.6 * np.exp(-time * 5))
    rumble = np.sin(2 * np.pi * np.cumsum(rumble_f) / SR).astype(np.float32)
    rumble *= np.exp(-time * 1.5).astype(np.float32)
    out = highpass(crack, 900) * 0.8 + lowpass(body, 700) * 0.9 + rumble * 0.9
    return fade(normalize(out, 0.98), 0.0005, 0.4)


def tinnitus(dur: float, freq: float = 3900.0) -> np.ndarray:
    """Das Pfeifen nach dem Knall. Traegt den Schock ohne ein Bild davon."""
    time = t(dur)
    tone = np.sin(2 * np.pi * freq * time).astype(np.float32)
    tone += np.sin(2 * np.pi * freq * 1.006 * time).astype(np.float32) * 0.4
    env = np.exp(-time / (dur * 0.45)).astype(np.float32)
    return fade(normalize(tone * env, 0.3), 0.01, 0.8)


def heartbeat(dur: float, bpm: float = 58.0) -> np.ndarray:
    """Zwei Schlaege pro Zyklus. Der Ton von Beat 5, wenn alles andere weg ist."""
    out = silence(dur)
    period = 60.0 / bpm
    at = 0.0
    while at < dur:
        place(out, thump(52, 0.5, 0.3), at, 0.9)
        place(out, thump(44, 0.42, 0.25), at + 0.30, 0.6)
        at += period
    return normalize(lowpass(out, 180), 0.75)


def snare_roll(dur: float, seed: int = 16) -> np.ndarray:
    """Militaertrommel-Wirbel, anschwellend."""
    g = rng(seed)
    n = int(SR * dur)
    noise = g.normal(0, 1, n).astype(np.float32)
    time = t(dur)
    tremolo = 0.5 + 0.5 * signal.sawtooth(2 * np.pi * 34 * time, 0.15).astype(np.float32)
    out = bandpass(noise, 900, 6500) * tremolo
    out *= np.linspace(0.25, 1.0, n, dtype=np.float32)
    return fade(normalize(out, 0.5), 0.2, 0.3)


def shot(seed: int = 17) -> np.ndarray:
    """Zwei Schuesse, bewusst abstrahiert: kurzer Transient, Koerper, Nachhall
    im Strassenraum. Kein Realismus - ein Zeichen."""
    g = rng(seed)
    dur = 1.5
    time = t(dur)
    crack = g.normal(0, 1, len(time)).astype(np.float32) * np.exp(-time * 90)
    body = np.sin(2 * np.pi * 140 * time).astype(np.float32) * np.exp(-time * 24)
    out = highpass(crack, 1200) * 0.9 + body * 0.5
    return fade(reverb(normalize(out, 0.9), 1.4, 0.4), 0.0005, 0.3)


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------


def to_stereo(x: np.ndarray, width: float = 0.35) -> np.ndarray:
    """Leichte Verbreiterung ueber eine kurze Verzoegerung auf einem Kanal.

    Reicht fuer Raumgefuehl im Klassenraum, ohne echtes Stereo-Panning.
    """
    delay = int(SR * 0.011 * width)
    right = np.concatenate([np.zeros(delay, dtype=np.float32), x[: len(x) - delay]])
    right = lowpass(right, 9000)
    return np.stack([x, (1 - width) * x + width * right], axis=1).astype(np.float32)


def write_mp3(x: np.ndarray, path: Path, bitrate: str = "160k") -> int:
    """Schreibt ueber ffmpeg direkt nach mp3 - keine wav-Zwischendatei."""
    path.parent.mkdir(parents=True, exist_ok=True)
    stereo = to_stereo(normalize(x, 0.89))
    pcm = (np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes()
    proc = subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "pipe:0",
            "-codec:a", "libmp3lame", "-b:a", bitrate, str(path),
        ],
        input=pcm,
        capture_output=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg: {proc.stderr.decode('utf-8', 'replace')[:300]}")
    return path.stat().st_size
