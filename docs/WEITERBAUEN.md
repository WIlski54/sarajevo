# Weiterbauen — Übergabe an die nächste Sitzung

Stand: 2026-08-16. Branch `p0-praesentations-skelett`, alles gepusht.

## Wo das Projekt steht

| | Stand |
|---|---|
| Präsentation | Läuft. Acht Beats, Presenter-Steuerung, historische Uhr, Texttafeln. |
| Ton | **Fertig.** Erzählstimme (OpenAI TTS, Stimme `ballad`), acht Klangbetten, diegetische Geräuschkulisse. |
| Video | **2 von 14 Shots.** `shot_03` (Kolonne am Appelkai), `shot_04` (der Wurf). |
| Medien | 19 von 31 Dateien. Die 12 fehlenden sind Blender-Shots. |
| Tests | 78, alle grün. |

```bash
npm test                 # Logik-Tests
npm run check:media      # zeigt, welche Medien fehlen
.\START_PRAESENTATION.bat
```

## Was als Nächstes zu tun ist

Die restlichen zwölf Shots, Beat für Beat. Reihenfolge nach Nutzen:

1. **`shot_05`** — Abprall vom Verdeck und Detonation. Damit ist Beat 2
   vollständig und man erlebt einen Beat einmal ganz. Die Bausteine dafür
   stehen alle in `lib/fx.py` (`staubwand`, `truemmer`, `tauben`, `blitz`).
2. **Beat 4** (`shot_08`, `shot_09`) — das falsche Abbiegen. Der Ort ist in
   `orte.franz_joseph_ecke()` schon gebaut, inklusive Schillers Laden.
3. **Beat 5** (`shot_10`, `shot_11`) — gleicher Ort, deshalb billig.
4. **Beat 1** (`shot_01`, `shot_02`) — Bahnhof. Neue Location.
5. **Beat 3** (`shot_06`, `shot_07`) — Rathaus, innen und außen. Neue Location.
6. **Beats 0, 6, 7** (`shot_00`, `shot_12`, `shot_13`) — Prolog, Epilog,
   Auswertung.

**Die Anforderung des Auftraggebers: man muss die Aktionen erkennen.** Nicht
„es ist dargestellt", sondern „ein Achtklässler sieht, was passiert".

## Wie hier gearbeitet wird

```bash
blender -b --factory-startup -P blender/build.py -- --shot 05 --still --frame 300
blender -b --factory-startup -P blender/build.py -- --shot 05 --final
blender -b --factory-startup -P blender/build.py -- --shot 05 --preview --frames 45
```

`--raw` rendert ohne Compositor (trennt Szenen- von Post-Fehlern).
`--frames N` schreibt nach `renders/`, nie über die echte Datei.

**Testbild ansehen, korrigieren, wiederholen.** Rechnen schlägt Hinsehen: Die
teuersten Fehler dieses Projekts wurden am Bild dreimal falsch gedeutet und
erst durch Messen gefunden.

## Fallen, die schon Zeit gekostet haben

**Blender 5.1**

- `primitive_cube_add(size=1)` erzeugt einen Würfel von **einer** Einheit.
  Skalierung ist `groesse`, nicht `groesse / 2`. Sonst ist die halbe Stadt
  halb so groß und schwebt.
- Gruppen müssen um den **lokalen** Ursprung gebaut sein, das Empty trägt die
  Position (`props.gruppe`). Sonst rotiert eine Gruppe um den Weltursprung.
- Texturen brauchen **Weltkoordinaten** (`materials._coords`), sonst skaliert
  jedes Muster mit der Objektgröße statt in Metern.
- F-Curves liegen in Channelbags, nicht an der Action → `lib/anim.py`.
- Kein `CompositorNodeComposite` mehr. Der Compositor braucht
  `CompositorNodeRLayers` **innerhalb** der Gruppe und `NodeGroupOutput` als
  Senke. Der Gruppeneingang wird nicht vom Render gefüttert und rendert
  schwarz — ohne Fehlermeldung.
- Glare-Typ heißt `Bloom`, nicht `BLOOM`. Menü-Sockets werden in
  `render._menu_or_value` schreibweise-unempfindlich gesetzt.
- Sky-Typ ist `MULTIPLE_SCATTERING`, `NISHITA` existiert nicht mehr.
- Videoausgabe: der Pfad **muss** die Endung `.mp4` tragen, sonst hängt
  Blender den Bildbereich an und die Präsentation findet die Datei nicht.
- Volumen nur für **große** Wolken. Bei kleinen Objekten sieht man das
  Froxel-Raster als Klötzchenmuster — dafür `fx._puff_material` (opakes Mesh
  mit Alpha).

**Licht und Kadrierung**

- Himmel ist Fülllicht (0,14), die Sonne macht das Licht (5,5), die
  Belichtung nimmt zurück (−2,1). Beides voll aufgedreht brennt das Bild weiß.
- Sonnenazimut ist nachgerechnet: Fassaden zeigen nach −Y, ihre Beleuchtung
  ist `sin(90−h)·cos(a)`. Bei −64° waren das 0,26 — streifendes Licht, die
  Zeile blieb flach.
- Berge in **Kilometern** denken. `orte.berge()` meldet den Mindestabstand;
  unter 1,2 km wird ein Hang zur Wand und verschattet die Straße.
- Ein Mensch ist bei 40 mm erst ab etwa 6 m Abstand als Handelnder lesbar.
- `orte.menge(frei=...)` freihalten, wo die Kamera steht.

**Werkzeuge**

- Quelldateien **nie** mit PowerShell `Get-Content`/`Set-Content` bearbeiten —
  das zerstört die UTF-8-Kodierung. Nur Edit/Write benutzen.
- Hintergrundprozesse sterben mit der Sitzung. Für den Server die `.bat`
  benutzen; Endrender im Vordergrund, sonst bleibt eine 0-Byte-Datei zurück.

## Inhaltliche Bindungen

- **Spec §4** ist die verbindliche Faktenliste. Texte sind daran gebunden.
- Figuren bleiben **gesichtslos**. Erkennbar über Silhouetten: Franz Ferdinand
  am Federbusch, Sophie am hellen Kleid mit breiter Hutkrempe.
- Das Attentat wird **andeutend** gezeigt — keine Wunden, kein Blut. Für die
  Schüsse: Weißblitze, Entsättigung, Tonabriss.
- Entsättigung, Vignette und Filmkorn gehören in die **Web-Schicht**, nicht in
  Blender. Dort kostet eine Änderung Sekunden statt eines Neurenders.

## Was noch offen ist, außer Shots

- Die fünf Vertiefungsmodule (Phase P6) und die vier interaktiven
  three.js-Module (P4): Routenkarte, Europa-Zündschnur, Dominokette,
  3D-Wagen. `beats.js` verweist bereits darauf.
- `docs/moderationsleitfaden.md` — ausdruckbar, pro Beat.
- Historische Fotos (Phase P5). **Vor dem Download die Liste mit Quelle,
  Größe und Lizenz vorlegen** — nichts ungefragt laden.
