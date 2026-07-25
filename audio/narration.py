"""Sprecherstimme fuer die Praesentation, gebacken zur Bauzeit.

Nur Standardbibliothek - kein openai-Paket, keine Installation. Die
Sprachsynthese ist ein einzelner POST; das rechtfertigt keine Abhaengigkeit.

    python audio/narration.py --models        Verfuegbare TTS-Modelle zeigen
    python audio/narration.py --audition      Drei Stimmproben zum Vergleich
    python audio/narration.py --all           Alle acht Beats vertonen
    python audio/narration.py --beat 5        Einen Beat neu vertonen

Der Schluessel kommt ausschliesslich aus .env bzw. der Umgebung und wird
nirgends ausgegeben oder protokolliert. Die fertige Praesentation braucht
weder Schluessel noch Internet - sie spielt die gebackenen mp3s ab.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BEATS_JS = PROJECT_ROOT / "web" / "src" / "beats.js"
AUDIO_OUT = PROJECT_ROOT / "media" / "audio"

API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini-tts"

# Kandidaten fuer die Stimmprobe. Erzaehler tief und ruhig, Zitatstimme
# mit mehr Ausdruck - sie spricht die ueberlieferten Worte in Beat 5.
AUDITION_VOICES = ("onyx", "ash", "ballad")

AUDITION_TEXT = (
    "Sonntag, der 28. Juni 1914. Über Sarajevo steht die Morgensonne. "
    "Für viele Serben ist es Vidovdan — der Tag, an dem sie an die Schlacht "
    "auf dem Kosovo Polje erinnern, mehr als fünfhundert Jahre zuvor."
)

AUDITION_INSTRUCTIONS = (
    "Ruhig, dokumentarisch, mit langen Pausen. Kein Pathos. Wie der Beginn "
    "einer Geschichtsdokumentation, die weiss, wie sie ausgeht."
)


# --------------------------------------------------------------------------
# Schluessel und Konfiguration
# --------------------------------------------------------------------------


def read_env_file(path: Path) -> dict[str, str]:
    """Minimaler .env-Leser. Kein python-dotenv noetig."""
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY") or read_env_file(PROJECT_ROOT / ".env").get(
        "OPENAI_API_KEY", ""
    )
    if not key or key.startswith("sk-..."):
        sys.exit(
            "Kein OPENAI_API_KEY gefunden.\n"
            "  .env.example nach .env kopieren und den Schluessel eintragen.\n"
            "  Er wird nur zur Bauzeit gebraucht."
        )
    return key


def request_json(path: str, key: str) -> dict:
    req = urllib.request.Request(
        f"{API_BASE}{path}", headers={"Authorization": f"Bearer {key}"}
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def pick_model(key: str, override: str | None) -> str:
    """Neuestes verfuegbares TTS-Modell.

    Bewusst abgefragt statt hart verdrahtet: welches Modell "das neueste"
    ist, veraltet schneller als dieser Code.
    """
    if override:
        return override

    try:
        data = request_json("/models", key).get("data", [])
    except urllib.error.URLError as err:
        print(f"  Modellabfrage fehlgeschlagen ({err}), nehme {DEFAULT_MODEL}.")
        return DEFAULT_MODEL

    candidates = [m for m in data if "tts" in m.get("id", "")]
    if not candidates:
        return DEFAULT_MODEL

    # Neuester datierter Snapshot vor dem gleitenden Alias. Zwei Gruende:
    # der Nutzer wollte ausdruecklich das neueste Modell, und die mp3s
    # werden einmal gebacken - ein Snapshot garantiert denselben
    # Stimmcharakter, falls spaeter einzelne Beats nachgebacken werden.
    # Ein Alias kann sich unter uns aendern, und dann klingt Beat 4
    # anders als Beat 3.
    snapshots = [m for m in candidates if any(c.isdigit() for c in m.get("id", ""))]
    pool = snapshots or candidates
    pool.sort(key=lambda m: m.get("created", 0), reverse=True)
    return pool[0]["id"]


# --------------------------------------------------------------------------
# Sprachsynthese
# --------------------------------------------------------------------------


def synthesize(
    key: str, model: str, voice: str, text: str, instructions: str, out_path: Path
) -> int:
    """Erzeugt eine mp3. Gibt die Groesse in Bytes zurueck."""
    payload = {
        "model": model,
        "voice": voice,
        "input": text,
        "response_format": "mp3",
    }
    if instructions:
        payload["instructions"] = instructions

    def post(body: dict) -> bytes:
        req = urllib.request.Request(
            f"{API_BASE}/audio/speech",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as response:
            return response.read()

    try:
        audio = post(payload)
    except urllib.error.HTTPError as err:
        detail = err.read().decode("utf-8", "replace")[:400]
        # Aeltere Modelle kennen instructions nicht - dann ohne erneut versuchen.
        if instructions and "instructions" in detail:
            print("  Modell kennt 'instructions' nicht - erneut ohne Sprechhaltung.")
            payload.pop("instructions")
            audio = post(payload)
        else:
            sys.exit(f"Sprachsynthese fehlgeschlagen ({err.code}): {detail}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(audio)
    return len(audio)


# --------------------------------------------------------------------------
# Beat-Daten aus beats.js lesen
# --------------------------------------------------------------------------


def load_beats() -> list[dict]:
    """Liest die Sprechertexte aus beats.js.

    beats.js ist die einzige Inhaltsquelle. Statt die Texte hier zu
    doppeln, wird die Datei mit node ausgewertet - node ist ohnehin
    Voraussetzung des Projekts.
    """
    import subprocess

    script = (
        "import('file:///' + process.argv[1].replace(/\\\\/g, '/'))"
        ".then(m => console.log(JSON.stringify(m.BEATS.map(b => ({"
        "id: b.id, title: b.title, file: b.narration.file,"
        "voice: b.narration.voice, instructions: b.narration.instructions,"
        "text: b.narration.text, quote: b.board.quote ?? null,"
        "quoteAfter: b.narration.quoteAfter ?? false})))))"
    )
    result = subprocess.run(
        ["node", "-e", script, str(BEATS_JS)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        sys.exit(f"beats.js konnte nicht gelesen werden:\n{result.stderr}")
    return json.loads(result.stdout)


# --------------------------------------------------------------------------
# Befehle
# --------------------------------------------------------------------------


def cmd_models(key: str) -> None:
    data = request_json("/models", key).get("data", [])
    tts = sorted(
        (m for m in data if "tts" in m.get("id", "")),
        key=lambda m: m.get("created", 0),
        reverse=True,
    )
    if not tts:
        print("Keine TTS-Modelle im Konto gefunden.")
        return
    print("Verfuegbare TTS-Modelle, neueste zuerst:")
    for m in tts:
        marker = "  <- Standard" if m["id"] == DEFAULT_MODEL else ""
        print(f"  {m['id']}{marker}")


def cmd_audition(key: str, model: str) -> None:
    out_dir = AUDIO_OUT / "audition"
    print(f"Stimmprobe mit Modell {model}")
    print(f"Text: {AUDITION_TEXT[:60]}...\n")
    for voice in AUDITION_VOICES:
        path = out_dir / f"stimme_{voice}.mp3"
        size = synthesize(
            key, model, voice, AUDITION_TEXT, AUDITION_INSTRUCTIONS, path
        )
        print(f"  {voice:8s} -> {path.relative_to(PROJECT_ROOT)}  ({size // 1024} KB)")
    print("\nAnhoeren und entscheiden. Die Wahl kommt dann in .env:")
    print("  OPENAI_TTS_VOICE_NARRATOR=<stimme>")


def cmd_beats(
    key: str, model: str, only: int | None,
    voice: str | None = None, quote: str | None = None,
) -> None:
    beats = load_beats()
    env = read_env_file(PROJECT_ROOT / ".env")
    narrator = (
        voice or os.environ.get("OPENAI_TTS_VOICE_NARRATOR")
        or env.get("OPENAI_TTS_VOICE_NARRATOR") or "ballad"
    )
    quote_voice = (
        quote or os.environ.get("OPENAI_TTS_VOICE_QUOTE")
        or env.get("OPENAI_TTS_VOICE_QUOTE") or "onyx"
    )

    print(f"Modell {model} | Erzaehler {narrator} | Zitatstimme {quote_voice}\n")
    for beat in beats:
        if only is not None and beat["id"] != only:
            continue
        path = PROJECT_ROOT / beat["file"]
        size = synthesize(
            key, model, narrator, beat["text"], beat["instructions"], path
        )
        print(f"  Beat {beat['id']}  {beat['title'][:34]:34s} {size // 1024:5d} KB")

        if beat["quoteAfter"] and beat["quote"]:
            quote_path = path.with_name(path.stem + "_zitat.mp3")
            size = synthesize(
                key,
                model,
                quote_voice,
                beat["quote"],
                "Leise, gebrochen, verzweifelt. Sehr langsam. Kaum Stimme.",
                quote_path,
            )
            print(f"           Zitat mit Stimme {quote_voice:8s}      {size // 1024:5d} KB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sprecherstimme backen")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--models", action="store_true", help="TTS-Modelle auflisten")
    group.add_argument("--audition", action="store_true", help="Drei Stimmproben")
    group.add_argument("--all", action="store_true", help="Alle Beats vertonen")
    group.add_argument("--beat", type=int, help="Nur diesen Beat vertonen")
    parser.add_argument("--model", help="Modell erzwingen statt abzufragen")
    parser.add_argument("--voice", help="Erzaehlerstimme (Vorgabe: ballad)")
    parser.add_argument("--quote-voice", dest="quote_voice",
                        help="Stimme fuer die historischen Zitate (Vorgabe: onyx)")
    args = parser.parse_args()

    key = api_key()

    if args.models:
        cmd_models(key)
        return

    env_model = read_env_file(PROJECT_ROOT / ".env").get("OPENAI_TTS_MODEL")
    model = pick_model(key, args.model or os.environ.get("OPENAI_TTS_MODEL") or env_model)

    if args.audition:
        cmd_audition(key, model)
    else:
        cmd_beats(
            key, model, None if args.all else args.beat,
            args.voice, args.quote_voice,
        )


if __name__ == "__main__":
    main()
