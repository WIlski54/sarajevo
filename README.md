# Sarajevo 1914 — Cinematic Live-Präsentation

Eine filmische, tongestützte Präsentation über das Attentat von Sarajevo am
**28. Juni 1914** für den Geschichtsunterricht der Klassen 8–9.

Konzipiert für den **Beamer im Klassenraum**: die Lehrkraft steuert jeden Beat
selbst, kann jederzeit anhalten, zurückspringen und erklären. Die Präsentation
läuft vollständig **offline** — kein Konto, keine Anmeldung, keine
Schülerdaten, keine Netzverbindung.

> **Status:** In Entwicklung. Die Spezifikation ist freigegeben, die
> Implementierung beginnt mit Phase P0.
> → [Design-Spezifikation](docs/superpowers/specs/2026-07-25-sarajevo-cinematic-design.md)

---

## Worum es geht

Die Schüler erleben den Vormittag des 28. Juni 1914 als zusammenhängende
Erfahrung — von der Ankunft am Bahnhof um 09:25 bis zu den Schüssen um 10:48.
Eine historische Uhr läuft dabei dauerhaft mit und wandert sichtbar auf den
Moment zu, dessen Ausgang die Klasse längst kennt. Genau daraus entsteht die
didaktische Spannung.

Drei Lernziele tragen das Ganze:

1. **Chronologie** — der Ablauf als Kette nachvollziehbarer Ereignisse
2. **Kontingenz** — wie eine Reihe kleiner Zufälle und Versäumnisse den Verlauf
   bestimmte: der Zünder, der Abprall, die nicht weitergegebene Routenänderung
3. **Anlass ≠ Ursache** — der Schuss löste den Krieg aus, verursachte ihn aber
   nicht. Das ist das eigentliche curriculare Ziel.

Die Darstellung des Attentats ist **bewusst andeutend**: Wirkung entsteht über
Kamera, Licht, Ton und Schnitt. Es gibt keine Wunden und kein Blut.

## Technik

Hybrid aus vorgerendertem Film und Echtzeit-3D:

- **Blender 5.1** (headless, prozedural aus Python) rendert die filmischen Shots
  mit Volumetrics, Motion Blur, DOF und prozeduralen PBR-Materialien
- **three.js** trägt die interaktiven Module — Routenvergleich, Europa-Karte mit
  zündenden Bündnislinien, die „Kette der Zufälle" als Dominoreihe, der
  orbitierbare Gräf & Stift — sowie alle Übergänge und Overlays
- **Ton** aus zwei Quellen: Erzählerstimme über OpenAI TTS, Score und Geräusche
  per numpy zur Bauzeit synthetisiert (keine Downloads, keine Lizenzfragen)

Alles Gerenderte entsteht aus Skripten. Es gibt kein handgeklicktes `.blend` als
Wahrheitsquelle — die Szenen sind jederzeit deterministisch reproduzierbar.

## Aufbau

```
blender/lib/      wiederverwendbare Bausteine (Material, Stadt, Props, FX, Kamera)
blender/shots/    je Shot eine Datei
web/src/          Presenter-Maschine, Stages, interaktive Szenen, Audio, UI
web/src/beats.js  ALLE Inhalte als Daten — Texte ohne 3D-Kenntnisse editierbar
audio/            Sprecherstimme (TTS) und Score-Synthese
tools/            Fotobeschaffung, lokaler Server, Vollständigkeitsprüfung
media/            Build-Ergebnisse, nicht versioniert
docs/             Spezifikation, Moderationsleitfaden, Bildnachweis
```

## Bauen und prüfen

Für Phase P0 genügen **Python 3 und Node ≥ 20** — es gibt keine npm-Abhängigkeiten
und keinen Build-Schritt. Für die späteren Phasen kommen Blender 5.1,
numpy/scipy/pillow und ffmpeg dazu.

```bash
npm test
```

Prüft die gesamte Logik: historische Uhr, Presenter-Zustandsmaschine,
Tastenbelegung, Video-Rückfall und die Beat-Daten. **Nach jeder Textänderung in
`web/src/beats.js` laufen lassen** — ein vergessenes `+` am Zeilenende ist ein
Syntaxfehler, der die ganze Präsentation lahmlegt, und der Test findet ihn sofort.

```bash
npm run check:media
```

Listet alle Video- und Tondateien, die noch fehlen. Solange Phase P1 bis P3 nicht
gelaufen sind, fehlen planmäßig alle 22 — die Präsentation zeigt dann statt eines
Shots die Texttafel des Beats. Vor dem Unterrichtseinsatz mit `--strict` prüfen,
dann meldet der Befehl einen Fehler, statt nur zu berichten.

```bash
npm run serve
```

Startet den lokalen Server ohne Browser (Port 8014) — nützlich zum Entwickeln.
Für den Unterricht ist `START_PRAESENTATION.bat` gedacht.

Die Sprachsynthese der Phase P1 braucht einen OpenAI-Key. Dafür `.env.example`
nach `.env` **kopieren** (nicht umbenennen — die Vorlage soll bleiben) und den
Schlüssel eintragen. Er wird ausschließlich zur Bauzeit gebraucht; die fertige
Präsentation läuft offline.

## Verwenden

Doppelklick auf `START_PRAESENTATION.bat` — startet einen lokalen Server und
öffnet den Browser im Vollbild.

| Taste | Wirkung |
|---|---|
| `Leertaste` / `→` | nächster Beat |
| `←` | zurück |
| `P` | Pause (Bild und Ton friert) |
| `R` | Beat wiederholen |
| `0`–`7` | direkt zu einem Beat |
| `V` | Vertiefungen |
| `B` | Blackout — zum ungestörten Sprechen |
| `Esc` | Kapitelübersicht |

## Historische Genauigkeit

Abschnitt 4 der Spezifikation führt eine **verbindliche Faktenliste**, an die
alle Texte gebunden sind. Enthalten sind unter anderem die Korrektur eines
Übertragungsfehlers der Textvorlage, die Einordnung der Kennzeichen-Legende
„A III 118" als nachträglicher Mythos, und ein bewusster
Quellenkritik-Moment: das weltbekannte „Verhaftungsfoto Princips" gilt heute als
zweifelhaft.

## Bildmaterial

Ausschließlich gemeinfreie Aufnahmen. Quelle, Urheber und Lizenzstatus jeder
einzelnen Datei stehen in [docs/bildnachweis.md](docs/bildnachweis.md) — bewusst
versioniert und ausdruckbar.

---

Unterrichtsmaterial für die Gesamtschule Meiderich.
