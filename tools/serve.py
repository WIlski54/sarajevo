"""Lokaler Server fuer die Praesentation.

Nur Standardbibliothek, keine Installation. Liefert das Projektwurzel-
verzeichnis aus, damit web/ und media/ mit denselben relativen Pfaden
erreichbar sind, die beats.js verwendet.

    python tools/serve.py [--port 8014] [--no-browser]
"""

from __future__ import annotations

import argparse
import http.server
import socketserver
import threading
import webbrowser
from functools import partial
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PORT = 8014  # 1914, damit der Port nicht mit anderen Projekten kollidiert


class Handler(http.server.SimpleHTTPRequestHandler):
    """Ergaenzt fehlende MIME-Typen und schaltet Caching ab."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".mp4": "video/mp4",
        ".mp3": "audio/mpeg",
        ".glb": "model/gltf-binary",
        ".webp": "image/webp",
    }

    def end_headers(self) -> None:
        # Ohne das zeigt der Browser nach einem Neu-Render alte Shots.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        # 404 auf noch fehlende Medien sind in P0 bis P3 der Normalfall
        # und wuerden die Konsole zumuellen. Fehler ab 500 bleiben sichtbar.
        status = args[1] if len(args) > 1 else ""
        if str(status).startswith("5"):
            super().log_message(fmt, *args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Server fuer Sarajevo 1914")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    handler = partial(Handler, directory=str(PROJECT_ROOT))
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        url = f"http://127.0.0.1:{args.port}/web/index.html"
        print(f"Sarajevo 1914 laeuft auf {url}")
        print("Beenden mit Strg+C.")
        if not args.no_browser:
            threading.Timer(0.6, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nBeendet.")


if __name__ == "__main__":
    main()
