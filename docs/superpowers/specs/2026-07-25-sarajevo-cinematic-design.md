# Design: „Sarajevo 1914" — Cinematic Live-Präsentation

**Datum:** 2026-07-25
**Status:** Entwurf zur Freigabe
**Projektpfad:** `D:\KI Projekte\Sarajevo 1914`
**Zielgruppe:** Klasse 8–9, Gesamtschule Meiderich
**Einsatzform:** Lehrer präsentiert vorne am Beamer, ein starker PC (RTX 4090)
**Fach:** Geschichte — Attentat von Sarajevo, 28. Juni 1914

---

## 1. Ziel

Eine hochwertig gerenderte, tongestützte Präsentation, die den Vormittag des
28. Juni 1914 als zusammenhängende filmische Erfahrung erzählt und dabei drei
Lernziele trägt:

1. **Chronologie** — der Ablauf des Attentats als Kette nachvollziehbarer Ereignisse
2. **Kontingenz** — die Erkenntnis, dass eine Reihe kleiner Zufälle und Fehler den
   Verlauf bestimmte (Zünder, Abprall, nicht weitergegebene Routenänderung)
3. **Anlass ≠ Ursache** — der Schuss löste den Krieg aus, verursachte ihn aber nicht.
   Dies ist das eigentliche curriculare Ziel.

Der Wow-Effekt ist Mittel, nicht Zweck: die Immersion soll die Schüler in eine
Situation ziehen, deren Ausgang sie kennen — genau daraus entsteht die
didaktische Spannung.

### Abgrenzung zum bestehenden Projekt

`D:\KI Projekte\Sarajevo` (13.07.2026) bleibt unverändert bestehen: Flask,
three.js r128, low-poly, iPad-first, mit KI-Tutor, für selbstständiges Erkunden.
Dieses Projekt ist ein eigenständiges Gegenstück für die Lehrerpräsentation. Kein
gemeinsamer Code, keine Abhängigkeit in beide Richtungen.

## 2. Entschiedene Optionen

| Frage | Entscheidung |
|---|---|
| Verhältnis zum Altprojekt | Neues eigenständiges Projekt |
| Endgerät | Beamer / starker PC |
| Technik | Hybrid **A1 — Video-Rückgrat**: Blender-Shots als mp4, three.js für interaktive Module, Übergänge, Overlays |
| Darstellung des Attentats | Cinematisch andeutend — keine Wunden, kein Blut |
| Steuerung | Presenter-Modus, Lehrer treibt jeden Beat |
| Ton | Voller Ton: Sprecherstimme + Score + Geräusche |
| Sprecherstimme | OpenAI TTS (neuestes verfügbares Modell), zur Bauzeit gebacken |
| Historische Fotos | Ja, an Schlüsselmomenten als deckungsgleiche Überblendung |
| Umfang | Modular: Kern ~8–10 Minuten + fünf abrufbare Vertiefungen |
| Auslieferung | Lokaler Server per `START_PRAESENTATION.bat`, offline lauffähig |

## 3. Dramaturgie — acht Beats

Grundlage ist das vom Nutzer gelieferte Zeitprotokoll. Die historische Uhr ist
dauerhaft im Bild und wandert von 09:25 auf 10:48.

**Beats und Shots sind nicht deckungsgleich.** Ein Beat ist eine
Erzähleinheit, die der Presenter am Stück auslöst; er kann aus mehreren
Blender-Shots bestehen (Beat 2 etwa aus Anfahrt, Wurf, Detonation, Nachhall).
Die vierzehn Shots verteilen sich auf die acht Beats. Daraus ergibt sich auch die
Zeitrechnung: **rund 4:30–6:00 gerendertes Filmmaterial** (redaktioneller Stand
nach Phase P0: 4:38), das zusammen mit den interaktiven Modulen, den Texttafeln
und den Sprechpausen ein Gesamterlebnis von **8–10 Minuten** ergibt — ohne die
Zeit, die der Lehrer selbst durch Anhalten und Erklären hinzufügt.

### Beat 0 — Prolog: Vidovdan

Kranfahrt über das dämmrige Sarajevo, Höhenrauch über der Miljacka, Minarette
und Kirchtürme, die Sonne bricht durch. Bild und Ton bauen auf.

**Inhalt:** Warum dieser Tag kein beliebiger war — 28. Juni ist Vidovdan, der
serbische Nationalfeiertag zur Erinnerung an die Schlacht auf dem Kosovo Polje
1389. Bosnien-Herzegowina war 1908 von Österreich-Ungarn annektiert worden. Der
Thronfolger inspiziert an diesem Tag Truppen in einer Provinz, in der ein Teil
der Bevölkerung den Anschluss an Serbien will.

### Beat 1 — 09:25 Ankunft

Dampflok fährt ein, volumetrischer Dampf durch das Bahnhofsglas, Gegenlicht,
Ehrenformation, Blaskapelle. Franz Ferdinand und Sophie steigen aus, der
Gräf & Stift Double Phaeton fährt vor, Verdeck zurückgeschlagen.

**Inhalt:** Anlass ist ein Truppenmanöver. **Warum Sophie mitfuhr:** Die Ehe war
morganatisch — in Wien durfte sie nicht neben ihm auftreten, ihre Kinder waren
von der Erbfolge ausgeschlossen. In Bosnien, bei einer Militärinspektion in
seiner Funktion als Generalinspektor, durfte sie an seiner Seite sein. Der
28. Juni 1914 war zugleich ihr 14. Hochzeitstag.

**Vorausdeutung:** Die Route stand seit Wochen in der Zeitung. Eine Gruppe junger
Verschwörer der Mlada Bosna hat sich entlang der Strecke verteilt.

### Beat 2 — 10:10 Der erste Anschlag

Die Kolonne fährt über den Appelkai. Nedeljko Čabrinović schlägt die Granate am
Laternenpfahl an, um den Zünder zu aktivieren — **zehn Sekunden Laufzeit**, im Ton
als tickende Uhr geführt. Zeitlupe, Rauchfahne, der Wurf. Der Chauffeur Leopold
Lojka beschleunigt, die Granate prallt vom zurückgeschlagenen Verdeck ab und
detoniert unter dem nachfolgenden Wagen.

Harter Schnitt in die Detonation: Staubwand, Trümmer, aufstiebende Tauben.
Danach Tinnitus-Ton, die Welt im Lowpass — Schockwirkung ohne Gewaltbild.
Etwa zwanzig Verletzte.

**Inhalt:** Čabrinović schluckt Zyankali, das nicht wirkt, und springt in die
Miljacka — die an dieser Stelle nur wenige Zentimeter tief war. Er wird
herausgezogen und festgenommen. Der erste Versuch ist gescheitert.

### Beat 3 — 10:15 Empfang im Rathaus

Vijećnica, maurische Bögen, farbige Lichtschäfte durch Buntglas, Staubpartikel in
der Luft. Bürgermeister Fehim Effendi Čurčić beginnt seine vorbereitete
Begrüßungsrede — er hat den Text nicht angepasst.

**Inhalt:** Franz Ferdinands Empörung. Er setzt das Programm dennoch fort. Die
geplante Weiterfahrt durch die enge, überfüllte Altstadt wird aus
Sicherheitsgründen gestrichen; stattdessen soll es über den breiten Appelkai
direkt ins Krankenhaus zu den Verletzten gehen.

**Didaktischer Kern:** Der Plan war da. Er war richtig. Er wurde nur nicht
weitergegeben.

### Beat 4 — 10:45 Die fatale Routenänderung

Die Kamera hebt von der Straße ab, die Straße wird zur Karte: geplante Route
grün, gefahrene Route rot. Die vorderen Wagen biegen in die Franz-Joseph-Straße
ein. Der Irrtum wird bemerkt, die Fahrzeuge halten und müssen zurücksetzen.

**Interaktives Modul:** Routenvergleich in three.js, vom Presenter aufrufbar.

### Beat 5 — 10:48 Die Schüsse

Der Wagen steht vor dem Delikatessenladen von Moritz Schiller. Gavrilo Princip,
19 Jahre alt, steht wenige Schritte entfernt. Er tritt an das offene Auto heran.

**Darstellung, andeutend:** Der Ton fällt weg bis auf den Herzschlag. Die Welt
entsättigt. Die Kamera gleitet an Princips Schulter vorbei. Zwei Weißblitze, ein
Ruck im Bild, Schnitt auf Schwarz. Zwei Sekunden Stille. Kein Blut, keine Wunden,
keine Einschüsse im Bild.

Dann, auf Schwarz, nur die dokumentierten Worte an Sophie, gesprochen von der
Zitatstimme:

> „Sopherl, Sopherl, stirb nicht! Bleibe am Leben für unsere Kinder!"
> *(überliefert von Graf Franz von Harrach, der auf dem Trittbrett stand)*

**Inhalt:** Franz Ferdinand wird am Hals getroffen, Sophie am Unterleib. Beide
sterben etwa eine halbe Stunde später im Konak, der Residenz des Statthalters.

**Korrektur der Vorlage:** Der gelieferte Text sagt „Sophie in den Untergang" —
ein Übertragungsfehler für „in den Unterleib". Die Präsentation formuliert
altersgerecht „schwer verletzt".

### Beat 6 — Epilog: Der Funke

Die Kamera fährt von der Straßenecke nach oben, unter der Szene entfaltet sich
Europa. Bündnislinien zünden wie Lunten durch die Julikrise:
23.7. Ultimatum an Serbien → 28.7. Kriegserklärung Österreich-Ungarns →
1.8. Deutschland an Russland → 3.8. an Frankreich → 4.8. Kriegseintritt
Großbritanniens.

Überblendung vom Sommerlicht 1914 ins Grau der Westfront.

**Interaktives Modul:** Europa-Zündschnur in three.js.

### Beat 7 — Anlass ≠ Ursache

Die Kette der Zufälle als kippende Dominoreihe: Datum Vidovdan gewählt · Route
vorab veröffentlicht · kaum Absperrung und wenig Polizei · Granate prallt ab ·
Routenänderung nicht weitergegeben · Princip steht genau dort. Jeder Stein
einzeln vom Presenter auslösbar.

Daneben die strukturellen Ursachen, die unabhängig von diesem Tag bestanden:
Imperialismus, Bündnissysteme, Wettrüsten, Nationalismus, Interessen in
Südosteuropa.

**Die Frage an die Klasse:** Wäre der Krieg ohne diesen Tag ausgeblieben?

### Vertiefungen (jederzeit per `V` abrufbar, unterbrechen den Ablauf nicht)

1. **Personen** — Franz Ferdinand, Sophie Chotek, Gavrilo Princip, Nedeljko
   Čabrinović, Leopold Lojka, Oskar Potiorek, Franz von Harrach
2. **Die Verschwörer an der Strecke** — wer wo stand und warum die meisten nicht
   handelten
3. **Warum Vidovdan?** — Kosovo 1389, serbischer Nationalmythos, Annexion 1908
4. **Julikrise** — die 37 Tage als Zeitleiste
5. **Anlass und Ursache** — die Unterscheidung als eigenes Modul

## 4. Historische Präzision

Verbindlich für alle Texte:

- **Princips Alter:** 19 Jahre, damit nach österreichischem Recht zu jung für die
  Todesstrafe. Zwanzig Jahre Haft, gestorben 1918 an Tuberkulose in Theresienstadt.
- **Sophies Verletzung:** Unterleib, nicht „Untergang" (Vorlagenfehler).
- **Todesort:** Konak des Statthalters, nicht das Krankenhaus.
- **Das Kennzeichen A III 118:** Die verbreitete Deutung als Vorzeichen des
  Waffenstillstands vom 11.11.1918 ist eine nachträgliche Legende, keine
  historische Tatsache. Wird, wenn erwähnt, ausdrücklich als Legende markiert.
- **Medienkompetenz-Moment:** Das weltbekannte „Verhaftungsfoto Princips" zeigt
  nach heutigem Forschungsstand mit hoher Wahrscheinlichkeit nicht Princip,
  sondern einen unbeteiligten Passanten. Dies wird bewusst thematisiert als
  Quellenkritik am konkreten Fall. Formulierung mit Vorsicht: „gilt heute als
  zweifelhaft", keine falsche Gewissheit in die andere Richtung.
- **Zahl der Verschwörer:** Die Quellen schwanken. Formulierung „eine Gruppe von
  etwa sieben jungen Verschwörern, mehrere davon entlang der Strecke verteilt".

## 5. Architektur

```
Sarajevo 1914/
├── START_PRAESENTATION.bat        # startet tools/serve.py + Browser im Vollbild
├── .env                           # OPENAI_API_KEY (nie committen)
├── .env.example
├── .gitignore                     # .env, media/, node_modules, __pycache__
│                                  # media/ ist bewusst nicht versioniert: alles darin
│                                  # ist per Build-Skript reproduzierbar. Der Lizenz-
│                                  # nachweis liegt deshalb in docs/, nicht in media/.
│                                  # Wichtig: media/ separat sichern, ein Neurender
│                                  # kostet Stunden.
├── docs/
│   ├── superpowers/specs/         # dieses Dokument
│   ├── superpowers/plans/
│   ├── moderationsleitfaden.md    # ausdruckbar, pro Beat
│   └── bildnachweis.md            # Quelle/Urheber/Lizenz jedes Fotos (versioniert)
├── blender/
│   ├── lib/
│   │   ├── materials.py           # prozedurale PBR-Shader
│   │   ├── city.py                # Straßenzüge, Fassaden-Generator, Miljacka, Brücken
│   │   ├── props.py               # Gräf & Stift, Laternen, Dampflok, Fahnen, Figuren
│   │   ├── fx.py                  # Rauch, Staub, Dampf, Tauben, Volumetrics
│   │   ├── camera.py              # Splines, Easing, Handheld-Rauschen, DOF
│   │   └── render.py              # Eevee-Preset, Compositor, Ausgabe
│   ├── shots/shot_00_prolog.py … shot_13_epilog.py
│   └── build.py                   # CLI-Einstieg
├── web/
│   ├── index.html
│   ├── src/
│   │   ├── main.js                # Bootstrap, Renderer, EffectComposer
│   │   ├── presenter.js           # Beat-Maschine, Tastatur, Pause, Blackout
│   │   ├── beats.js               # NUR Daten
│   │   ├── stage/videoStage.js
│   │   ├── stage/photoStage.js
│   │   ├── scenes/routeMap.js
│   │   ├── scenes/europeFuse.js
│   │   ├── scenes/dominoes.js
│   │   ├── scenes/carViewer.js
│   │   ├── fx/transitions.js
│   │   ├── fx/particles.js
│   │   ├── audio/engine.js
│   │   └── ui/overlays.js
│   └── vendor/three-bundle.js     # esbuild-IIFE
├── media/                         # ausschließlich Build-Ergebnisse
│   ├── video/shot_XX.mp4
│   ├── audio/vo_XX.mp3, score_XX.mp3, sfx_*.mp3
│   ├── photos/*.jpg
│   └── models/graef_stift.glb
├── audio/
│   ├── narration.py               # Sprechertexte → OpenAI TTS → mp3
│   └── score.py                   # numpy-Synthese: Score-Layer und Geräusche
└── tools/
    ├── fetch_photos.py            # gemeinfreie Fotos + Lizenznachweis
    ├── serve.py                   # lokaler Server für die .bat
    └── check_media.js             # prüft: jede in beats.js referenzierte Datei existiert
```

### Verantwortlichkeiten

- **`beats.js`** — einzige Quelle aller Inhalte: Beat-Reihenfolge, Uhrzeiten,
  Erzähltexte, Zitate, Zuordnung von Shot-, Ton- und Fotodateien, Verweise auf
  interaktive Module. Ohne 3D-Kenntnisse editierbar. Enthält keine Logik.
- **`presenter.js`** — Zustandsmaschine über die Beats. Kennt weder three.js noch
  Blender, spricht nur mit Stage- und Scene-Modulen über deren Schnittstelle.
  Besitzt den Pause-Zustand.
- **`stage/*`, `scenes/*`** — einheitliche Schnittstelle `mount(container)`,
  `play()`, `pause()`, `dispose()`. Jedes Modul ist unabhängig testbar und
  austauschbar; ein defektes Modul darf nur seinen eigenen Beat betreffen.
- **`audio/engine.js`** — vier Busse, Ducking, Kopplung an den Pause-Zustand.
  Kennt keine Inhalte, nur Dateinamen und Buszuordnung.
- **`blender/lib/*`** — wiederverwendbare Bausteine ohne Wissen über einzelne
  Shots. **`blender/shots/*`** — je Shot eine Datei, konsumiert `lib/`.
- **`audio/*.py`, `tools/*.py`** — Bauzeit-Werkzeuge. Laufen nie im Browser.

### Abweichung von der bisherigen Offline-Konvention

Frühere Projekte liefen per Doppelklick über `file://`. Das ist hier nicht
sinnvoll: bei etwa sechs Minuten 1080p-Video wären Base64-Einbettungen
unpraktikabel, und `file://` blockiert `fetch`, ES-Module und damit den
GLB-Loader. Stattdessen startet `START_PRAESENTATION.bat` einen lokalen
Python-Server und öffnet den Browser im Vollbild. Ein Doppelklick für den
Nutzer, aber ohne die `file://`-Einschränkungen. Die Präsentation bleibt dabei
vollständig offline — es wird nichts aus dem Netz geladen.

## 6. Blender-Pipeline

Headless-CLI nach dem im Dinos-Projekt bewährten Muster:

```
blender -b --factory-startup -P blender/build.py -- --shot 04 --still
blender -b --factory-startup -P blender/build.py -- --shot 04 --final
blender -b --factory-startup -P blender/build.py -- --all --still
```

Alles wird prozedural aus Python aufgebaut. Es gibt kein handgepflegtes `.blend`
als Wahrheitsquelle — die Szene ist jederzeit deterministisch reproduzierbar, und
jede Iteration wird über ein Test-Still visuell geprüft.

**Fünf Locations** speisen alle Shots: Bahnhof · Appelkai mit Miljacka und
Lateinerbrücke · Vijećnica außen und innen · Ecke Franz-Joseph-Straße mit
Schillers Laden · Europa-Tableau (nur als gerenderter Hintergrund; die
interaktive Karte lebt in three.js).

**Engine:** Eevee Next, 1920×1080, 30 fps. Cycles wird nicht verwendet — bei
diesem Bildstil (Volumetrics, Bloom, DOF) ist der Qualitätsgewinn gering, die
Renderzeit aber ein bis zwei Größenordnungen höher.

**Renderbudget, gemessen statt geschätzt:** Der Referenz-Shot (510 Frames,
1920×1080, Endqualität mit Volumetrics und Motion Blur) brauchte **0,44 s pro
Frame**, insgesamt 3,7 Minuten. Hochgerechnet auf die 318 s Film ≈ 9.540 Frames
ergibt das **rund 70 Minuten** für den kompletten Endrender.

Das ist deutlich weniger als die ursprünglich geschätzten 1,5–4,5 Stunden. Die
Konsequenz ist keine Zeitersparnis, sondern mehr Freiheit: ein kompletter
Neurender aller Shots ist damit eine Kaffeepause und kein Nachtlauf — Änderungen
am Look sind also billiger als geplant. Die Schätzung stand vor dem ersten
echten Render und war zu pessimistisch.

### Bekannte API-Fallen Blender 5.1 (aus der Dinos-Pipeline)

- Videoausgabe: erst `image_settings.media_type = "VIDEO"`, dann
  `file_format = "FFMPEG"`, sonst Enum-Fehler.
- Engine-Kennung `BLENDER_EEVEE`. Compositor hängt an
  `scene.compositing_node_group`; `use_nodes` ist deprecated.
- Glare-Node ist socket-basiert: `glare.inputs["Type"].default_value = "Bloom"`.
  Defaults fluten das Bild — Threshold ~10, Strength ~0,12, Size ~0,15.
- Große Emissionsflächen mit BLENDED-Blend-Mode verschleiern in Eevee den ganzen
  Himmel, auch bei kleinem Alpha. Nur kurz einblenden oder vermeiden.
- Volumen-Boxkanten: Dichte-Falloff über Objekt-Z per MapRange SMOOTHSTEP.
- `scene.eevee.shadow_pool_size = "1024"` gegen „Shadow buffer full".
- Keyframes auf Node-Sockets über `sock.keyframe_insert("default_value", frame=f)`.

## 7. Effekt-Katalog

| Kategorie | Umsetzung |
|---|---|
| **Texturen** | Prozedurale PBR-Shader statt Downloads: Kopfsteinpflaster mit Pfützen-Roughness, Putzfassaden mit Höhen-Grime, Kalkstein, Messing, Autolack mit Clearcoat, Uniformtuch mit Sheen, Glas, maurische Kachelmuster als Node-Geometrie. Auflösungsunabhängig, lizenzfrei. |
| **Licht** | Sonnenstand plausibel für 28.6., 10 Uhr, Sarajevo. God Rays durch Bahnhofsglas, volumetrischer Höhenrauch über der Miljacka, warmes Bounce-Licht von Kalksteinfassaden, Buntglas-Farbschäfte im Rathaus, Mündungsfeuer als kurzer Lichtimpuls. |
| **Partikel** | Lokdampf, Straßenstaub hinter den Rädern, Rauchfahne der Granate, Detonation als Staubwand mit Trümmern, Staubflusen in Lichtschäften, aufstiebende Tauben beim Knall, wehende Fahnen, Zigarettenrauch. |
| **Post (Blender)** | Bloom mit gezähmten Werten, Motion Blur, DOF mit Fokus-Racking, dezente Halation, Filmkorn, Vignette. |
| **Post (three.js)** | EffectComposer: UnrealBloom, SSAO, SMAA, eigener Entsättigungs- und Vignetten-Pass, Filmkorn — abgestimmt auf den Blender-Look, damit der Übergang zwischen Film und Echtzeit nicht auffällt. |
| **Bewegung** | Kamera auf Bezier-Splines mit Ease-Kurven plus gebackenes Handheld-Rauschen. Räder per Driver an die Wegstrecke gekoppelt. Zeitlupe über Frame-Mapping. |
| **Figuren** | Bewusst gesichtslos-nah: Schultern, Handschuhe, Hutrand, ein Fuß auf dem Trittbrett. Umgeht das Uncanny Valley und entspricht der andeutenden Erzählweise. Menge als instanzierte Silhouetten mit leichtem Sway. |
| **Übergänge** | Shader-basiert: Kreuzblende, Ausbrennen zu Weiß, Tintenlauf, Entsättigung. Video → Foto → Echtzeit-3D laufen über denselben Übergangs-Layer, damit der Rhythmus einheitlich bleibt. |

## 8. Ton

### Sprecherstimme

OpenAI TTS, zur Bauzeit in mp3 gebacken. Zwei Stimmen: ein sachlicher Erzähler
und eine getrennte Stimme für historische Zitate, damit Quelle und Erzählung
hörbar unterscheidbar sind. Der `instructions`-Parameter steuert die
Sprechhaltung pro Beat (dokumentarisch-ruhig mit langen Pausen; für Beat 5 leise
und gebrochen).

- **Modellwahl:** `narration.py` fragt `/v1/models` ab, filtert TTS-fähige
  Modelle und nimmt das neueste verfügbare. Default `gpt-4o-mini-tts`,
  überschreibbar per `OPENAI_TTS_MODEL`. Grund: der Wissensstand über „das
  neueste Modell" veraltet, die Abfrage bleibt korrekt.
- **Key:** ausschließlich aus `os.environ["OPENAI_API_KEY"]`, geladen aus `.env`.
  Der Key wird nie in Code, Logs oder Repository geschrieben.
- **Eine mp3 pro Beat** (`vo_00.mp3` … `vo_07.mp3` plus Vertiefungen). Damit ist
  die Presenter-Steuerung möglich: ein Beat, eine Tonspur.
- **Stimmauswahl in P1:** derselbe Satz mit drei Kandidaten (`onyx`, `ash`,
  `ballad`) zum Anhören und Entscheiden.
- Die fertige Präsentation braucht weder API-Key noch Internet.

### Score und Geräusche

Zur Bauzeit mit numpy/scipy synthetisiert, danach per ffmpeg zu mp3. Keine
Downloads, keine Lizenzfragen, deterministisch reproduzierbar.

- Karplus-Strong-Saiten für Tambura-/Cimbalom-Farbe
- Tiefer Streicher-Drone (verstimmte Sägezähne, Lowpass, langsames Vibrato)
- FM-Glocken mit unharmonischen Teiltönen (Prolog, Epilog)
- Militärtrommel-Wirbel, Timpani-Schläge, Blaskapellen-Fanfare
- Tickender Zünder für die zehn Sekunden in Beat 2
- Detonation: Rauschstoß mit heruntergezogenem Rumpeln, danach Tinnitus-Sinus und
  Lowpass auf allen anderen Bussen
- Herzschlag, Menschenmenge, Motorenlauf, Schritte, Lokdampf

**Bekannte Grenze:** Synthese trägt Drones, Glocken, Perkussion und Texturen gut,
melodische Orchestrierung nicht. Der Score ist deshalb bewusst flächig und
sparsam angelegt. Wenn später mehr gewünscht ist, können CC0-Samples ergänzt
werden — mit ausdrücklicher Zustimmung und Lizenznachweis.

### Diegetische Geräuschkulisse (verbindlich)

Der Ton ist nicht nur Musik und Stimme. **Was der Text beschreibt, soll man
hören** — auch das, was gar nicht im Bild ist. Eine erwähnte Schlacht kann als
Klang präsent sein, ohne dass ein Bild davon nötig wäre. Das ist die
konsequente Fortsetzung der andeutenden Erzählweise aus §3.

Verbindlich umzusetzende Stellen:

| Beat | Anlass im Text | Klang |
|---|---|---|
| 0 | „die Schlacht auf dem Kosovo Polje" | Ferne, gespenstische Schlachtentextur: Hufe, Metall, gedämpfte Rufe — weit weg, wie eine Erinnerung |
| 0 | Morgen über der Stadt | Erwachende Stadt: einzelne Vögel, ein Karren, eine ferne Glocke |
| 1 | Bahnhof, Zug hält | Lokdampf, Pfiff, Schritte auf dem Bahnsteig, Blaskapelle |
| 2 | „schlägt eine Handgranate gegen einen Laternenpfahl" | **Metallisches Klacken** — genau auf das Wort, vor dem Ticken |
| 2 | „zehn Sekunden" | Der tickende Zünder (bereits umgesetzt) |
| 2 | „springt in die Miljacka" | Wasser, flach und platschend — der Fluss ist nur zentimetertief |
| 3 | Rathaus, Begrüßungsrede | Halliger Saal, Papier, Schritte auf Stein, Gemurmel |
| 4 | „er sei falsch abgebogen" | Rufen im Freien, Bremsen, Rückwärtsrollen |
| 5 | Der Wagen steht | Motor im Standgas, dann Abstellen — danach nur Herzschlag |
| 6 | Die Julikrise-Daten | **Telegrafenklicken** — die Ultimaten gingen per Telegraf. Historisch präzise und akustisch prägnant |
| 6 | Übergang zur Westfront | Ferner Artilleriedonner, Marschtritt |

**Umsetzungsregel:** Die Einsatzzeiten werden nicht geraten. `score.py`
schätzt sie aus der Zeichenposition der Phrase im Sprechertext, skaliert mit
der gemessenen Sprechdauer. Das trifft auf etwa eine Sekunde genau — genug,
damit ein Klang auf seinem Wort liegt und nicht daneben.

### Mischung

Vier Web-Audio-Busse: Stimme, Score, Geräusche, Atmosphäre, dazu ein Master. Der
Score duckt sich etwa 6 dB unter die Sprecherstimme. Pause hält Video und
`AudioContext` im selben Frame an.

## 9. Presenter-Steuerung

| Taste | Wirkung |
|---|---|
| `Leertaste` / `→` / Klick | nächster Beat |
| `←` | vorheriger Beat |
| `P` | Pause: Standbild und Ton friert |
| `R` | aktuellen Beat wiederholen |
| `0`–`7` | direkt zu einem Beat springen |
| `V` | Vertiefungen öffnen |
| `B` | Blackout — Bild auf Schwarz, um ungestört zu sprechen |
| `Esc` | Kapitelübersicht |
| `F` | Vollbild |

**Dauerhaft im Bild:** die historische Uhr, die von 09:25 auf 10:48 wandert. Sie
ist der Orientierungsanker der ganzen Erfahrung. Die Fortschrittsleiste am
unteren Rand erscheint nur bei Mausbewegung.

Kein Zweitbildschirm-System — am Beamer wird gespiegelt, ein Presenter-Display
brächte nichts. Stattdessen `docs/moderationsleitfaden.md`: ausdruckbar, pro Beat
was gesagt wird, wo angehalten wird, welche Rückfrage sich anbietet.

## 10. Historische Fotos

Gemeinfreie Aufnahmen von 1914 aus Wikimedia Commons. `tools/fetch_photos.py`
lädt sie und schreibt zu jeder Datei Quelle, Urheber und Lizenz nach
`docs/bildnachweis.md` — bewusst außerhalb von `media/`, damit der
Lizenznachweis versioniert bleibt und für den Schulgebrauch ausdruckbar ist.

**Verbindlich:** Vor dem Herunterladen wird dem Nutzer die vollständige Liste mit
Dateinamen, Quell-URLs, Größen und Lizenzstatus zur Freigabe vorgelegt. Ohne
Freigabe wird nichts geladen.

**Einsatz:** deckungsgleiche Überblendung. Der 3D-Shot friert auf einer
Komposition, die der Perspektive des echten Fotos entspricht, und blendet
hinüber. Dezenter Ken-Burns-Effekt. Quellenangabe klein unten rechts, immer
sichtbar.

## 11. Fehlertoleranz

- **Fehlende Mediendatei:** `tools/check_media.js` prüft vor dem Einsatz jede in
  `beats.js` referenzierte Datei. Zur Laufzeit fängt der Stage-Layer einen
  Ladefehler ab und zeigt statt eines schwarzen Lochs die Texttafel des Beats —
  die Präsentation läuft weiter.
- **Kein WebGL:** Hinweisseite mit dem vollständigen Zeitprotokoll als Text. Die
  Inhalte bleiben erreichbar.
- **Ton stumm oder blockiert:** Browser blockieren Autoplay mit Ton bis zur ersten
  Nutzerinteraktion. Der Startbildschirm ist deshalb ein bewusster Klick
  („Präsentation starten"), der den `AudioContext` freigibt. Zusätzlich zeigt
  jeder Beat seinen Text als Tafel, sodass die Präsentation auch stumm tragfähig
  bleibt.
- **Defektes interaktives Modul:** Der Beat fällt auf seinen Video-Shot und die
  Texttafel zurück.

## 12. Prüfung

- **`tools/check_media.js`** — läuft `beats.js` ab, prüft die Existenz jeder
  referenzierten Video-, Ton- und Fotodatei. Der wichtigste Test überhaupt: eine
  fehlende Datei vor der Klasse ist der einzige echte Worst Case.
- **`beats.js`-Datenvalidierung** — acht Beats, Pflichtfelder vorhanden,
  Uhrzeiten monoton, jedes referenzierte Modul existiert.
- **Blender-Rauchtest** — `build.py --all --still` muss für jeden Shot ein
  Standbild ohne Fehler liefern.
- **Ton-Dauer-Abgleich** — die Sprecherstimme eines Beats darf nicht länger sein
  als die Summe seiner Shots; andernfalls hält der letzte Shot des Beats auf
  seinem Schlussframe stehen, bis die Stimme endet.
- **Browser-Verifikation** — Konsolenfehler und 404-Prüfung, danach ein
  vollständiger Durchlauf.
- **Beamer-Abnahme** — echter Durchlauf in 1920×1080 im Vollbild: Tastatur,
  Ton über HDMI, keine Bildlaufleisten, kein Ruckeln an Übergängen.

Hinweis zur Verifikation in dieser Umgebung: Browser-Pane-Tabs laufen häufig mit
`document.hidden === true`; dort pausieren rAF, CSS-Transitions,
IntersectionObserver und Screenshots. Verifikation daher primär über
`javascript_tool` (Werte und Zustände lesen) und über die `__shot`-Pipeline;
`window.scrollTo` löst im Pane kein `scroll`-Event aus.

## 13. Bauphasen

| | Phase | Ergebnis |
|---|---|---|
| **P0** | Skelett | Presenter-Shell, alle acht Beats mit Platzhalterflächen, Uhr, Kapitelleiste. Der komplette Ablauf läuft durch, das Timing sitzt — bevor ein Frame gerendert wird. Wichtigster Schritt zur Risikominimierung. |
| **P1** | Ton | `narration.py` und `score.py`, alle Beats vertont, Stimmauswahl getroffen. Ab hier wirkt die Präsentation bereits ohne Bilder. |
| **P2** | Referenz-Shot | `blender/lib/` plus Location Appelkai plus Shot 02 (Granate) in Endqualität. Beweist die Optik an einem Shot, bevor dreizehn weitere entstehen. |
| **P3** | Restliche Shots | Location für Location, Beat für Beat. |
| **P4** | Interaktive Module | Routenvergleich, Europa-Zündschnur, Dominokette, 3D-Wagen. |
| **P5** | Fotos und Feinschliff | Überblendungen, Post-Processing, Übergangs-Shader. |
| **P6** | Vertiefungen | Fünf Zusatzmodule, Moderationsleitfaden. |
| **P7** | Abnahme | Vollständigkeitstest, `.bat`, Beamer-Durchlauf. |

## 14. Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Figurenanimation ist headless in Blender aufwendig | Gesichtslos-nahe Bildsprache, Silhouetten in mittlerer Distanz, keine komplexen Gangzyklen. Der Stil ist so gewählt, dass die Schwäche zur Stärke wird. |
| Score-Qualität durch Synthese begrenzt | Komposition auf Drones, Glocken, Perkussion und Texturen ausgelegt statt auf Melodie. Optionale CC0-Ergänzung später. |
| Renderzeit | P0 legt das Timing mit Platzhaltern fest; Endrender erst, wenn nichts mehr am Schnitt geändert wird. |
| Umfang über mehrere Sitzungen | Jede Phase endet mit einem zeigbaren Zustand. |
| TTS-Modellname veraltet | Abfrage über `/v1/models` statt harter Verdrahtung. |
| Historische Fehler in den Texten | Abschnitt 4 als verbindliche Faktenliste; Vorlagenfehler dokumentiert korrigiert. |

## 15. Bewusst nicht enthalten

Kein Login, kein Lehrer-Dashboard, keine Schülerdaten, kein SocketIO. Kein
KI-Tutor — das leistet das bestehende iPad-Projekt; hier steht der Lehrer vorne.
Kein VR. Keine Aufgaben oder Quizfragen im Ablauf: die Auswertung erfolgt im
Unterrichtsgespräch, dafür der Moderationsleitfaden. Keine iPad-Optimierung —
das Ziel ist ausdrücklich der Beamer an einem starken PC.
