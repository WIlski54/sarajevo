# Sarajevo 1914 — P0: Präsentations-Skelett — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ein per Doppelklick startbares Präsentations-Skelett, in dem alle acht Beats mit ihren echten Texten und der historischen Uhr durchlaufen, vollständig per Tastatur gesteuert — bevor ein einziger Frame gerendert wird.

**Architecture:** Reine ESM-Web-App ohne Build-Schritt, ausgeliefert über einen Python-Server aus der Standardbibliothek. Die Logik (Beat-Zustandsmaschine, Tastenzuordnung, historische Uhr, Datenvalidierung) ist DOM-frei und damit mit `node --test` ohne jede Abhängigkeit prüfbar. Die DOM-Schicht (Tafeln, Uhr, Kapitelleiste, Video-Stage) wird im Browser verifiziert. Fehlende Mediendateien fallen auf die Texttafel des Beats zurück — dieser von Spec §11 geforderte Pfad dient in P0 gleichzeitig als Platzhalter-Darstellung.

**Tech Stack:** JavaScript ESM (kein Bundler, kein three.js in P0), Node ≥ 20 mit eingebautem `node:test`, Python 3 `http.server`. Keine npm-Abhängigkeiten.

**Spec:** [2026-07-25-sarajevo-cinematic-design.md](../specs/2026-07-25-sarajevo-cinematic-design.md)

---

## Was P0 ausdrücklich NICHT enthält

Kein three.js, kein Blender, kein Ton, keine Fotos, keine interaktiven Module. Die Beats verweisen bereits auf ihre späteren Mediendateien; die fehlen nur noch. Vertiefungen (`V`) sind in P0 auf die Kapitelübersicht reduziert — die fünf Module kommen in P6.

Auch der von Spec §11 geforderte **WebGL-Rückfall gehört nicht in P0**: P0 verwendet gar kein WebGL, es gibt also nichts zu erkennen. Er kommt mit P4, wenn three.js einzieht. P0 deckt nur den verwandten Fall „kein JavaScript" über `<noscript>` ab.

Der von Spec §12 genannte **Ton-Dauer-Abgleich** entfällt ebenfalls — er kommt mit P1, sobald Tondateien existieren.

## Dateistruktur

| Datei | Verantwortung |
|---|---|
| `package.json` | `"type": "module"`, Test-Skript. Keine Abhängigkeiten. |
| `web/src/beats.js` | **Nur Daten.** Alle acht Beats: Uhrzeit, Titel, Shots mit Dauer, Erzähltext, Tafeltext, Zitate, Modulverweise. Einzige Inhaltsquelle. |
| `web/src/clock.js` | Reine Funktionen: `"09:25"` ↔ Minuten, Interpolation der historischen Uhr über den Beat-Fortschritt. Kein DOM. |
| `web/src/presenter.js` | Zustandsmaschine über die Beats: Index, Pause, Blackout, Übersicht. Kein DOM, kein Wissen über Darstellung. |
| `web/src/keymap.js` | Reine Abbildung Tastenname → Aktionsname. Kein DOM. |
| `web/src/stage/videoStage.js` | Video-Element plus Rückfall auf die Texttafel bei fehlender Datei. |
| `web/src/ui/overlays.js` | DOM: Tafel, historische Uhr, Kapitelleiste, Fortschritt, Blackout, Startbildschirm. |
| `web/src/main.js` | Verdrahtung: Tastatur → keymap → presenter → overlays + stage. |
| `web/index.html`, `web/src/style.css` | Gerüst und Gestaltung, 1920×1080-first. |
| `tools/serve.py` | Lokaler Server, korrekte MIME-Typen, öffnet den Browser. |
| `tools/check_media.js` | Läuft `beats.js` ab, meldet vorhandene und fehlende Mediendateien. `--strict` für die Abnahme. |
| `START_PRAESENTATION.bat` | Doppelklick-Einstieg. |
| `tests/*.test.js` | Unit-Tests der DOM-freien Logik. |

**Grenzen:** `presenter.js` kennt weder DOM noch Dateien — es liefert nur Zustand und benachrichtigt Abonnenten. `overlays.js` und `videoStage.js` lesen Zustand, schreiben aber nie hinein. `beats.js` enthält keine Logik.

---

## Task 1: Projektgerüst und Test-Läufer

**Files:**
- Create: `package.json`
- Create: `tests/smoke.test.js`

- [ ] **Step 1: Write the failing test**

`tests/smoke.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";

test("Test-Läufer und ESM funktionieren", () => {
  assert.equal(typeof import.meta.url, "string");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/`
Expected: FAIL — `Error: Cannot find module '<projekt>\tests'`.

**Verifiziert auf Node v25.9.0:** Ein Verzeichnis als Argument von `--test` wird
nicht als Testverzeichnis durchsucht, sondern als Modul aufzulösen versucht — das
scheitert unabhängig von `package.json`. Ohne Argument (`node --test`) findet Node
die Tests rekursiv, mit explizitem Glob ebenfalls. Deshalb verwendet das
`test`-Skript unten den Glob und nicht das Verzeichnis.

Nebenbefund derselben Prüfung: Node 25 erkennt ESM in `.js`-Dateien automatisch,
auch ohne `"type": "module"`. Der Eintrag bleibt trotzdem — er ist korrekt und wird
gebraucht, sobald echte Module dazukommen.

- [ ] **Step 3: Write minimal implementation**

`package.json`:

```json
{
  "name": "sarajevo-1914",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Cinematic Live-Praesentation zum Attentat von Sarajevo, 28. Juni 1914",
  "scripts": {
    "test": "node --test \"tests/**/*.test.js\"",
    "check:media": "node tools/check_media.js",
    "serve": "python tools/serve.py"
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test`
Expected: PASS — `# pass 1`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add package.json tests/smoke.test.js
git commit -m "chore: Projektgeruest mit abhaengigkeitsfreiem Test-Laeufer"
```

---

## Task 2: Historische Uhr

Die Uhr ist der Orientierungsanker der Präsentation (Spec §9). Sie interpoliert innerhalb eines Beats, damit sie sichtbar auf 10:48 zuläuft statt zu springen.

**Files:**
- Create: `web/src/clock.js`
- Test: `tests/clock.test.js`

- [ ] **Step 1: Write the failing test**

`tests/clock.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { parseClock, formatClock, interpolateClock } from "../web/src/clock.js";

test("parseClock wandelt Uhrzeit in Minuten seit Mitternacht", () => {
  assert.equal(parseClock("09:25"), 565);
  assert.equal(parseClock("10:48"), 648);
  assert.equal(parseClock("00:00"), 0);
});

test("parseClock lehnt Unsinn ab", () => {
  assert.throws(() => parseClock("25:00"), /ungueltig/i);
  assert.throws(() => parseClock("09:60"), /ungueltig/i);
  assert.throws(() => parseClock("halb zehn"), /ungueltig/i);
});

test("formatClock ist die Umkehrung und fuellt mit Nullen", () => {
  assert.equal(formatClock(565), "09:25");
  assert.equal(formatClock(648), "10:48");
  assert.equal(formatClock(0), "00:00");
});

test("interpolateClock steht am Beat-Anfang auf der Beat-Zeit", () => {
  assert.equal(interpolateClock("10:10", "10:15", 0), "10:10");
});

test("interpolateClock erreicht am Beat-Ende die naechste Zeit", () => {
  assert.equal(interpolateClock("10:10", "10:15", 1), "10:15");
});

test("interpolateClock laeuft dazwischen sichtbar mit", () => {
  assert.equal(interpolateClock("10:10", "10:20", 0.5), "10:15");
});

test("interpolateClock haelt still, wenn keine naechste Zeit folgt", () => {
  assert.equal(interpolateClock("10:48", null, 0.7), "10:48");
});

test("interpolateClock begrenzt den Fortschritt auf 0..1", () => {
  assert.equal(interpolateClock("10:10", "10:20", -3), "10:10");
  assert.equal(interpolateClock("10:10", "10:20", 9), "10:20");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/clock.test.js`
Expected: FAIL — `Cannot find module '../web/src/clock.js'`.

- [ ] **Step 3: Write minimal implementation**

`web/src/clock.js`:

```js
/**
 * Historische Uhr der Praesentation.
 * Reine Funktionen, kein DOM - damit vollstaendig unit-testbar.
 */

const CLOCK_PATTERN = /^([01]\d|2[0-3]):([0-5]\d)$/;

/** "09:25" -> 565 (Minuten seit Mitternacht) */
export function parseClock(text) {
  const match = CLOCK_PATTERN.exec(String(text));
  if (!match) throw new Error(`Ungueltige Uhrzeit: ${text}`);
  return Number(match[1]) * 60 + Number(match[2]);
}

/** 565 -> "09:25" */
export function formatClock(minutes) {
  const total = Math.round(minutes);
  const h = Math.floor(total / 60);
  const m = total % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

/**
 * Uhrzeit zwischen dem aktuellen und dem naechsten Beat, damit die Uhr
 * sichtbar mitlaeuft statt zu springen.
 * @param {string} from   Uhrzeit des aktuellen Beats
 * @param {string|null} to Uhrzeit des naechsten Beats, null wenn keiner folgt
 * @param {number} progress 0..1 Fortschritt im aktuellen Beat
 */
export function interpolateClock(from, to, progress) {
  const start = parseClock(from);
  if (to === null || to === undefined) return formatClock(start);
  const end = parseClock(to);
  const t = Math.min(1, Math.max(0, Number(progress) || 0));
  return formatClock(start + (end - start) * t);
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/clock.test.js`
Expected: PASS — `# pass 8`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add web/src/clock.js tests/clock.test.js
git commit -m "feat: historische Uhr mit Interpolation ueber den Beat-Fortschritt"
```

---

## Task 3: Beat-Daten

Die inhaltliche Grundlage. Texte gebunden an die verbindliche Faktenliste in Spec §4. Die Shot-Dauern sind der **redaktionelle Zielwert** und werden in P3 gegen die echten Renderlängen abgeglichen.

**Files:**
- Create: `web/src/beats.js`
- Test: `tests/beats.test.js`

- [ ] **Step 1: Write the failing test**

`tests/beats.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { BEATS, totalShotSeconds } from "../web/src/beats.js";
import { parseClock } from "../web/src/clock.js";

test("es gibt genau acht Beats mit luekenlosen IDs 0..7", () => {
  assert.equal(BEATS.length, 8);
  assert.deepEqual(BEATS.map((b) => b.id), [0, 1, 2, 3, 4, 5, 6, 7]);
});

test("jeder Beat hat Titel, Tafel und mindestens einen Shot", () => {
  for (const beat of BEATS) {
    assert.ok(beat.title?.length > 0, `Beat ${beat.id}: Titel fehlt`);
    assert.ok(beat.board?.heading?.length > 0, `Beat ${beat.id}: Tafel-Ueberschrift fehlt`);
    assert.ok(beat.board?.text?.length > 40, `Beat ${beat.id}: Tafeltext zu kurz`);
    assert.ok(Array.isArray(beat.shots) && beat.shots.length > 0, `Beat ${beat.id}: kein Shot`);
  }
});

test("jeder Shot hat einen eindeutigen Dateipfad und positive Dauer", () => {
  const seen = new Set();
  for (const beat of BEATS) {
    for (const shot of beat.shots) {
      assert.match(shot.file, /^media\/video\/shot_\d{2}\.mp4$/, `Beat ${beat.id}: ${shot.file}`);
      assert.ok(!seen.has(shot.file), `Shot doppelt verwendet: ${shot.file}`);
      seen.add(shot.file);
      assert.ok(shot.duration > 0, `Shot ${shot.file}: Dauer nicht positiv`);
    }
  }
});

test("jeder Beat hat einen Erzaehltext fuer die Sprachsynthese", () => {
  for (const beat of BEATS) {
    assert.ok(beat.narration?.text?.length > 80, `Beat ${beat.id}: Erzaehltext zu kurz`);
    assert.match(beat.narration.file, /^media\/audio\/vo_\d{2}\.mp3$/);
  }
});

test("die Uhrzeiten laufen monoton vorwaerts", () => {
  const times = BEATS.filter((b) => b.clock !== null).map((b) => parseClock(b.clock));
  for (let i = 1; i < times.length; i++) {
    assert.ok(times[i] >= times[i - 1], `Uhrzeit springt zurueck bei Index ${i}`);
  }
});

test("die Uhrzeiten entsprechen dem Zeitprotokoll", () => {
  const byId = Object.fromEntries(BEATS.map((b) => [b.id, b.clock]));
  assert.equal(byId[1], "09:25");
  assert.equal(byId[2], "10:10");
  assert.equal(byId[3], "10:15");
  assert.equal(byId[4], "10:45");
  assert.equal(byId[5], "10:48");
  assert.equal(byId[0], null, "Prolog hat keine Uhrzeit");
  assert.equal(byId[6], null, "Epilog hat keine Uhrzeit");
  assert.equal(byId[7], null, "Auswertung hat keine Uhrzeit");
});

test("Zitate tragen immer eine Quellenangabe", () => {
  for (const beat of BEATS) {
    if (beat.board.quote) {
      assert.ok(beat.board.source?.length > 0, `Beat ${beat.id}: Zitat ohne Quelle`);
    }
  }
});

test("quoteAfter setzt ein Zitat auf der Tafel voraus - kein Text doppelt gepflegt", () => {
  for (const beat of BEATS) {
    if (beat.narration.quoteAfter) {
      assert.ok(
        beat.board.quote?.length > 0,
        `Beat ${beat.id}: quoteAfter ohne board.quote`,
      );
    }
  }
});

test("die Uhrzeit auf der Tafel stimmt mit dem clock-Feld ueberein", () => {
  // Jede Uhrzeit steht pro Beat an drei Stellen: clock, am Anfang von
  // board.heading und als gesprochener Satz in narration.text. Die ersten
  // beiden sind maschinell pruefbar - der dritte nicht (deutsche Zahlwoerter).
  for (const beat of BEATS) {
    if (beat.clock === null) continue;
    const gefunden = /^(\d{2}:\d{2})/.exec(beat.board.heading);
    assert.ok(gefunden, `Beat ${beat.id}: board.heading beginnt nicht mit einer Uhrzeit`);
    assert.equal(
      gefunden[1],
      beat.clock,
      `Beat ${beat.id}: Tafel sagt ${gefunden[1]}, clock sagt ${beat.clock}`,
    );
  }
});

test("jeder Beat hat Stimme und Sprechanweisung fuer die Sprachsynthese", () => {
  // Phase P1 gibt instructions direkt an die Sprachsynthese weiter. Fehlt der
  // Wert, klingt der Beat still falsch statt laut zu scheitern.
  const stimmen = new Set(["narrator", "quote"]);
  for (const beat of BEATS) {
    assert.ok(stimmen.has(beat.narration.voice), `Beat ${beat.id}: unbekannte Stimme`);
    assert.ok(
      beat.narration.instructions?.length > 20,
      `Beat ${beat.id}: Sprechanweisung fehlt oder ist zu knapp`,
    );
  }
});

test("verwiesene Module stammen aus der bekannten Menge", () => {
  const known = new Set(["routeMap", "europeFuse", "dominoes", "carViewer"]);
  for (const beat of BEATS) {
    if (beat.module !== null) {
      assert.ok(known.has(beat.module), `Beat ${beat.id}: unbekanntes Modul ${beat.module}`);
    }
  }
});

test("die Filmlaenge liegt im geplanten Rahmen", () => {
  const seconds = totalShotSeconds();
  assert.ok(seconds >= 240 && seconds <= 360, `Filmlaenge ${seconds}s ausserhalb 240..360s`);
});

test("der Vorlagenfehler Untergang kommt nirgends vor", () => {
  const alleTexte = JSON.stringify(BEATS);
  assert.ok(!/in den Untergang/.test(alleTexte), "Vorlagenfehler nicht korrigiert");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/beats.test.js`
Expected: FAIL — `Cannot find module '../web/src/beats.js'`.

- [ ] **Step 3: Write minimal implementation**

`web/src/beats.js`:

```js
/**
 * ALLE Inhalte der Praesentation als Daten - plus zwei kleine
 * Auswertungshelfer am Dateiende. Keine Zustandslogik, kein DOM.
 *
 * Texte sind gebunden an die verbindliche Faktenliste in
 * docs/superpowers/specs/2026-07-25-sarajevo-cinematic-design.md, Abschnitt 4.
 * Wer hier Texte aendert, braucht keine 3D-Kenntnisse.
 *
 * WENN DU HIER TEXTE AENDERST:
 *  1. Danach `npm test` laufen lassen. Ein vergessenes `+` am Zeilenende
 *     oder ein fehlendes Anfuehrungszeichen ist ein Syntaxfehler, der die
 *     GANZE Praesentation lahmlegt - der Test faengt das sofort.
 *  2. Aenderst du eine Uhrzeit, dann an ALLEN DREI Stellen des Beats:
 *     `clock`, die Zeitangabe am Anfang von `board.heading` und den
 *     gesprochenen Zeit-Satz am Anfang von `narration.text`. Die ersten
 *     beiden prueft ein Test, den dritten kann keiner pruefen.
 *  3. Unterhalb des BEATS-Arrays nichts anfassen.
 *
 * clock:     historische Uhrzeit, null wo das Zeitprotokoll keine nennt
 * shots:     Blender-Shots in Abspielreihenfolge. duration = redaktioneller
 *            Zielwert in Sekunden, wird in Phase P3 gegen die echten
 *            Renderlaengen abgeglichen.
 * narration: Sprechertext fuer die Sprachsynthese in Phase P1
 * board:     Texttafel. Dient bei fehlender Videodatei auch als Rueckfall.
 * module:    interaktives three.js-Modul, kommt in Phase P4
 */

export const BEATS = [
  {
    id: 0,
    clock: null,
    title: "Prolog: Vidovdan",
    shots: [{ file: "media/video/shot_00.mp4", duration: 26 }],
    narration: {
      file: "media/audio/vo_00.mp3",
      voice: "narrator",
      instructions:
        "Ruhig, dokumentarisch, mit langen Pausen. Kein Pathos. Wie der Beginn " +
        "einer Geschichtsdokumentation, die weiss, wie sie ausgeht.",
      text:
        "Sonntag, der 28. Juni 1914. Über Sarajevo steht die Morgensonne. " +
        "Für die Verwaltung in Wien ist es ein Arbeitstag in einer unruhigen Provinz. " +
        "Für viele Serben ist es Vidovdan — der Tag, an dem sie an die Schlacht auf dem " +
        "Kosovo Polje erinnern, mehr als fünfhundert Jahre zuvor. " +
        "Sechs Jahre ist es her, dass Österreich-Ungarn Bosnien-Herzegowina annektiert hat. " +
        "Und an genau diesem Tag kommt der Thronfolger in die Stadt.",
    },
    board: {
      heading: "Sonntag, 28. Juni 1914",
      text:
        "Sarajevo ist die Hauptstadt von Bosnien-Herzegowina — einer Provinz, die " +
        "Österreich-Ungarn 1908 annektiert hatte. Der 28. Juni ist Vidovdan, ein " +
        "serbischer Nationalfeiertag zur Erinnerung an die Schlacht auf dem Kosovo " +
        "Polje von 1389. An diesem Tag besucht der österreichisch-ungarische " +
        "Thronfolger die Stadt.",
    },
    module: null,
  },

  {
    id: 1,
    clock: "09:25",
    title: "Ankunft am Bahnhof",
    shots: [
      { file: "media/video/shot_01.mp4", duration: 16 },
      { file: "media/video/shot_02.mp4", duration: 20 },
    ],
    narration: {
      file: "media/audio/vo_01.mp3",
      voice: "narrator",
      instructions: "Sachlich erzaehlend, leicht waermer als der Prolog.",
      text:
        "Neun Uhr fünfundzwanzig. Der Zug hält im Bahnhof von Sarajevo. " +
        "Erzherzog Franz Ferdinand, Thronfolger von Österreich-Ungarn, ist zu einem " +
        "Truppenmanöver angereist. An seiner Seite seine Frau Sophie. " +
        "Dass sie neben ihm sitzen darf, ist keine Selbstverständlichkeit. " +
        "Am Wiener Hof gilt die Ehe als nicht standesgemäß: Sophie muss hinter den " +
        "Erzherzoginnen zurücktreten, ihre Kinder sind von der Thronfolge ausgeschlossen. " +
        "Hier aber tritt Franz Ferdinand als Generalinspektor der Streitkräfte auf — " +
        "und da darf sie an seiner Seite fahren. " +
        "Es ist der achtundzwanzigste Juni. Ihr vierzehnter Hochzeitstag. " +
        "Was das Paar nicht weiß: Die Fahrtroute stand seit Wochen in der Zeitung. " +
        "Und entlang dieser Route haben sich junge Männer verteilt, die den Thronfolger " +
        "töten wollen.",
    },
    board: {
      heading: "09:25 — Ankunft am Bahnhof",
      text:
        "Franz Ferdinand kommt zur Inspektion eines Truppenmanövers. Seine Frau " +
        "Sophie Chotek begleitet ihn — möglich, weil er hier als Generalinspektor " +
        "der Streitkräfte auftritt und nicht als Thronfolger bei Hofe. Der 28. Juni " +
        "ist zugleich ihr 14. Hochzeitstag. Die Fahrtroute war vorab öffentlich " +
        "bekannt; eine Gruppe von etwa sieben jungen Verschwörern der Mlada Bosna " +
        "hatte sich entlang der Strecke verteilt.",
    },
    module: null,
  },

  {
    id: 2,
    clock: "10:10",
    title: "Der erste Anschlag am Appelkai",
    shots: [
      { file: "media/video/shot_03.mp4", duration: 14 },
      { file: "media/video/shot_04.mp4", duration: 24 },
      { file: "media/video/shot_05.mp4", duration: 16 },
    ],
    narration: {
      file: "media/audio/vo_02.mp3",
      voice: "narrator",
      instructions:
        "Zunehmend angespannt. Bei den zehn Sekunden knapper und schneller werden, " +
        "danach nach der Detonation deutlich zuruecknehmen, fast tonlos.",
      text:
        "Zehn Uhr zehn. Die Kolonne fährt über den Appelkai, die breite Uferstraße " +
        "an der Miljacka. Keine geschlossene Absperrung, wenige Polizisten, offene " +
        "Wagen mit zurückgeschlagenem Verdeck. " +
        "In der Menge steht Nedeljko Čabrinović. Er schlägt eine Handgranate gegen " +
        "einen Laternenpfahl, um den Zünder zu aktivieren. Von jetzt an bleiben ihm " +
        "zehn Sekunden. Er wirft. " +
        "Der Chauffeur Leopold Lojka sieht die Bewegung und gibt Gas. Die Granate " +
        "prallt vom zurückgeschlagenen Verdeck ab, fällt auf die Straße — und " +
        "detoniert unter dem nachfolgenden Wagen. " +
        "Etwa zwanzig Menschen werden verletzt. Der Thronfolger bleibt unversehrt. " +
        "Čabrinović schluckt Gift, das nicht wirkt, und springt in die Miljacka. " +
        "Der Fluss ist an dieser Stelle nur wenige Zentimeter tief. Man zieht ihn " +
        "heraus und nimmt ihn fest. " +
        "Der erste Anschlag ist gescheitert.",
    },
    board: {
      heading: "10:10 — Der erste Anschlag",
      text:
        "Nedeljko Čabrinović wirft eine Handgranate auf den Wagen des Thronfolgers. " +
        "Weil der Chauffeur beschleunigt, prallt sie ab und detoniert unter dem " +
        "nachfolgenden Fahrzeug. Etwa 20 Menschen werden verletzt, das Thronfolgerpaar " +
        "bleibt unverletzt. Čabrinovićs Selbstmordversuch scheitert: das Gift wirkt " +
        "nicht, und die Miljacka ist an dieser Stelle nur wenige Zentimeter tief.",
    },
    module: null,
  },

  {
    id: 3,
    clock: "10:15",
    title: "Empfang im Rathaus",
    shots: [
      { file: "media/video/shot_06.mp4", duration: 10 },
      { file: "media/video/shot_07.mp4", duration: 26 },
    ],
    narration: {
      file: "media/audio/vo_03.mp3",
      voice: "narrator",
      instructions:
        "Sachlich, mit einem Hauch Ironie beim Buergermeister, der seine Rede " +
        "unveraendert vorliest. Beim letzten Satz bewusst langsamer.",
      text:
        "Zehn Uhr fünfzehn. Die Kolonne erreicht das Rathaus, die Vijećnica. " +
        "Bürgermeister Fehim Effendi Čurčić beginnt seine vorbereitete Begrüßungsrede. " +
        "Er hat den Text nicht geändert. " +
        "Franz Ferdinand ist empört: Er sei in freundschaftlicher Absicht gekommen " +
        "und werde mit Bomben empfangen. Dann fasst er sich und lässt ihn ausreden. " +
        "Das Programm wird fortgesetzt — aber verändert. Die geplante Fahrt durch die " +
        "engen, überfüllten Gassen der Altstadt wird aus Sicherheitsgründen gestrichen. " +
        "Stattdessen soll es über den breiten Appelkai direkt ins Krankenhaus gehen, " +
        "zu den Verletzten des ersten Anschlags. " +
        "Der Plan war da. Er war richtig. Er wurde nur nicht weitergegeben.",
    },
    board: {
      heading: "10:15 — Empfang im Rathaus",
      text:
        "Franz Ferdinand zeigt sich empört über den Anschlag, setzt das Programm aber " +
        "fort. Die geplante Weiterfahrt durch die überfüllte Altstadt wird aus " +
        "Sicherheitsgründen gestrichen: Die Kolonne soll über den breiten Appelkai " +
        "direkt ins Krankenhaus fahren, um die Verletzten zu besuchen. Diese Änderung " +
        "erreicht die Fahrer der vorderen Wagen nicht.",
    },
    module: null,
  },

  {
    id: 4,
    clock: "10:45",
    title: "Die fatale Routenänderung",
    shots: [
      { file: "media/video/shot_08.mp4", duration: 12 },
      { file: "media/video/shot_09.mp4", duration: 24 },
    ],
    narration: {
      file: "media/audio/vo_04.mp3",
      voice: "narrator",
      instructions:
        "Nuechtern, praezise, wie ein Untersuchungsbericht. Die Nuechternheit " +
        "erzeugt hier die Spannung.",
      text:
        "Zehn Uhr fünfundvierzig. Die Kolonne fährt ab. " +
        "Doch die Fahrer der vorderen Wagen wissen nichts von der Änderung. Sie fahren " +
        "die Route, die sie gelernt haben — und biegen rechts in die Franz-Joseph-Straße " +
        "ein, genau in die Altstadt, die man vermeiden wollte. " +
        "Erst jetzt fällt der Irrtum auf. Man ruft dem Chauffeur zu, er sei falsch " +
        "abgebogen. Der Wagen hält an. Er muss zurücksetzen. " +
        "Und dabei kommt er zum Stehen.",
    },
    board: {
      heading: "10:45 — Die falsche Abzweigung",
      text:
        "Die Fahrer der ersten Wagen wurden nicht über die geänderte Route informiert " +
        "und biegen in die ursprünglich geplante Franz-Joseph-Straße ein. Als der " +
        "Irrtum bemerkt wird, müssen die Fahrzeuge anhalten und zurücksetzen.",
    },
    module: "routeMap",
  },

  {
    id: 5,
    clock: "10:48",
    title: "Die tödlichen Schüsse",
    shots: [
      { file: "media/video/shot_10.mp4", duration: 18 },
      { file: "media/video/shot_11.mp4", duration: 28 },
    ],
    narration: {
      file: "media/audio/vo_05.mp3",
      voice: "narrator",
      instructions:
        "Sehr leise, sehr langsam, lange Pausen. Nach den Schuessen fast fluesternd. " +
        "Keine Dramatisierung - die Zurueckhaltung traegt die Wirkung.",
      text:
        "Zehn Uhr achtundvierzig. Der Wagen steht. Vor dem Delikatessenladen von " +
        "Moritz Schiller. " +
        "Wenige Schritte entfernt steht Gavrilo Princip. Neunzehn Jahre alt. Er hatte " +
        "den Anschlag am Morgen für gescheitert gehalten und war stehen geblieben. " +
        "Jetzt steht der Wagen genau vor ihm. " +
        "Er tritt heran und gibt zwei Schüsse ab. " +
        "Franz Ferdinand wird am Hals getroffen, Sophie am Unterleib. " +
        "Etwa eine halbe Stunde später sterben beide im Konak, der Residenz des " +
        "Statthalters.",
      // Nach dem Erzaehltext wird board.quote mit der Zitatstimme gesprochen
      // (Phase P1). Der Text steht bewusst nur einmal, in board.quote.
      quoteAfter: true,
    },
    board: {
      heading: "10:48 — Die Schüsse",
      text:
        "Der Wagen kommt vor dem Delikatessenladen von Moritz Schiller zum Stehen. " +
        "Gavrilo Princip, 19 Jahre alt, steht wenige Schritte entfernt, tritt an das " +
        "offene Auto heran und gibt zwei Schüsse ab. Franz Ferdinand wird am Hals " +
        "getroffen, Sophie schwer am Unterleib verletzt. Beide sterben etwa eine halbe " +
        "Stunde später im Konak, der Residenz des Statthalters.",
      quote: "Sopherl, Sopherl, stirb nicht! Bleibe am Leben für unsere Kinder!",
      source: "Überliefert von Graf Franz von Harrach, der auf dem Trittbrett stand",
    },
    module: null,
  },

  {
    id: 6,
    clock: null,
    title: "Epilog: Der Funke",
    shots: [{ file: "media/video/shot_12.mp4", duration: 30 }],
    narration: {
      file: "media/audio/vo_06.mp3",
      voice: "narrator",
      instructions:
        "Aufziehend, weiter werdend. Die Datumsangaben klar und getaktet, wie " +
        "fallende Dominosteine.",
      text:
        "Zwei Schüsse in einer Seitenstraße. Und dann geht alles sehr schnell. " +
        "Am 23. Juli stellt Österreich-Ungarn ein Ultimatum an Serbien, das kaum " +
        "erfüllbar ist. Am 28. Juli erklärt es Serbien den Krieg. " +
        "Russland mobilisiert, weil es Serbien stützt. Deutschland erklärt Russland " +
        "am 1. August den Krieg, Frankreich am 3. August. Als deutsche Truppen in " +
        "das neutrale Belgien einmarschieren, tritt am 4. August Großbritannien in " +
        "den Krieg ein. " +
        "Siebenunddreißig Tage nach den Schüssen von Sarajevo steht Europa im Krieg. " +
        "Es wird vier Jahre dauern und Millionen Menschen das Leben kosten.",
    },
    board: {
      heading: "Die Julikrise — 37 Tage",
      text:
        "23. Juli: Ultimatum Österreich-Ungarns an Serbien. 28. Juli: Kriegserklärung " +
        "an Serbien. 30. Juli: russische Mobilmachung. 1. August: Deutschland erklärt " +
        "Russland den Krieg, 3. August Frankreich. 4. August: Großbritannien tritt in " +
        "den Krieg ein, nachdem deutsche Truppen in das neutrale Belgien einmarschiert " +
        "sind. Aus einem Attentat wird ein Weltkrieg.",
    },
    module: "europeFuse",
  },

  {
    id: 7,
    clock: null,
    title: "Anlass oder Ursache?",
    shots: [{ file: "media/video/shot_13.mp4", duration: 14 }],
    narration: {
      file: "media/audio/vo_07.mp3",
      voice: "narrator",
      instructions:
        "Offen, fragend, an die Klasse gerichtet. Am Ende nicht abschliessend " +
        "klingen - die Frage soll stehen bleiben.",
      text:
        "An diesem Vormittag ging sehr viel schief. Das Datum war ausgerechnet " +
        "Vidovdan. Die Route stand in der Zeitung. Es gab kaum Absperrungen. " +
        "Die Granate prallte ab. Die geänderte Route wurde nicht weitergegeben. " +
        "Und Princip stand genau an der Stelle, an der der Wagen zum Stehen kam. " +
        "Nimm einen dieser Zufälle weg, und der 28. Juni 1914 wäre ein Tag wie " +
        "jeder andere geblieben. " +
        "Aber: Die Bündnisse bestanden schon. Das Wettrüsten lief schon. Die " +
        "Interessengegensätze in Südosteuropa bestanden schon. " +
        "Das Attentat war der Anlass des Krieges. War es auch seine Ursache?",
    },
    board: {
      heading: "Anlass oder Ursache?",
      text:
        "Die Kette der Zufälle: Datum Vidovdan · Route vorab veröffentlicht · kaum " +
        "Absperrung · Granate prallt ab · Routenänderung nicht weitergegeben · Princip " +
        "steht genau dort. Daneben die strukturellen Ursachen, die unabhängig von " +
        "diesem Tag bestanden: Imperialismus, Bündnissysteme, Wettrüsten, " +
        "Nationalismus, Interessengegensätze in Südosteuropa. Das Attentat war der " +
        "Anlass. War es die Ursache?",
    },
    module: "dominoes",
  },
];

/** Summe aller Shot-Dauern in Sekunden. */
export function totalShotSeconds() {
  return BEATS.reduce(
    (sum, beat) => sum + beat.shots.reduce((s, shot) => s + shot.duration, 0),
    0,
  );
}

/** Uhrzeit des naechsten Beats, der eine nennt - fuer die Uhr-Interpolation. */
export function nextClockAfter(index) {
  for (let i = index + 1; i < BEATS.length; i++) {
    if (BEATS[i].clock !== null) return BEATS[i].clock;
  }
  return null;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/beats.test.js`
Expected: PASS — `# pass 13`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add web/src/beats.js tests/beats.test.js
git commit -m "feat: acht Beats mit Erzaehl- und Tafeltexten als Datenquelle"
```

---

## Task 4: Presenter-Zustandsmaschine

Kern der Steuerung, absichtlich DOM-frei. Spec §9.

**Files:**
- Create: `web/src/presenter.js`
- Test: `tests/presenter.test.js`

- [ ] **Step 1: Write the failing test**

`tests/presenter.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { createPresenter } from "../web/src/presenter.js";

const BEATS = [
  { id: 0, clock: null, shots: [{ file: "a.mp4", duration: 10 }] },
  { id: 1, clock: "09:25", shots: [{ file: "b.mp4", duration: 5 }, { file: "c.mp4", duration: 5 }] },
  { id: 2, clock: "10:10", shots: [{ file: "d.mp4", duration: 20 }] },
];

test("startet auf Beat 0, nicht laufend, nicht pausiert", () => {
  const p = createPresenter(BEATS);
  assert.equal(p.state.index, 0);
  assert.equal(p.state.started, false);
  assert.equal(p.state.paused, false);
  assert.equal(p.state.blackout, false);
});

test("start() setzt started und benachrichtigt", () => {
  const p = createPresenter(BEATS);
  let calls = 0;
  p.subscribe(() => calls++);
  p.start();
  assert.equal(p.state.started, true);
  assert.equal(calls, 1);
});

test("next() geht vorwaerts, prev() zurueck", () => {
  const p = createPresenter(BEATS);
  p.next();
  assert.equal(p.state.index, 1);
  p.prev();
  assert.equal(p.state.index, 0);
});

test("next() am Ende bleibt stehen statt zu ueberlaufen", () => {
  const p = createPresenter(BEATS);
  p.goTo(2);
  p.next();
  assert.equal(p.state.index, 2);
});

test("prev() am Anfang bleibt stehen", () => {
  const p = createPresenter(BEATS);
  p.prev();
  assert.equal(p.state.index, 0);
});

test("goTo() begrenzt auf gueltige Indizes", () => {
  const p = createPresenter(BEATS);
  p.goTo(99);
  assert.equal(p.state.index, 2);
  p.goTo(-5);
  assert.equal(p.state.index, 0);
});

test("Beat-Wechsel setzt den Shot-Index und den Fortschritt zurueck", () => {
  const p = createPresenter(BEATS);
  p.goTo(1);
  p.advanceShot();
  assert.equal(p.state.shotIndex, 1);
  p.goTo(2);
  assert.equal(p.state.shotIndex, 0);
  assert.equal(p.state.progress, 0);
});

test("advanceShot() laeuft innerhalb des Beats und meldet am Ende false", () => {
  const p = createPresenter(BEATS);
  p.goTo(1);
  assert.equal(p.advanceShot(), true, "Beat 1 hat zwei Shots");
  assert.equal(p.state.shotIndex, 1);
  assert.equal(p.advanceShot(), false, "danach kein weiterer Shot");
  assert.equal(p.state.shotIndex, 1, "Shot-Index laeuft nicht ueber");
});

test("togglePause() schaltet um und zurueck", () => {
  const p = createPresenter(BEATS);
  p.togglePause();
  assert.equal(p.state.paused, true);
  p.togglePause();
  assert.equal(p.state.paused, false);
});

test("Pause blockiert next() nicht - der Vortragende bleibt handlungsfaehig", () => {
  const p = createPresenter(BEATS);
  p.togglePause();
  p.next();
  assert.equal(p.state.index, 1);
  assert.equal(p.state.paused, false, "Beat-Wechsel hebt die Pause auf");
});

test("toggleBlackout() schaltet um, ohne den Beat zu verlieren", () => {
  const p = createPresenter(BEATS);
  p.goTo(1);
  p.toggleBlackout();
  assert.equal(p.state.blackout, true);
  assert.equal(p.state.index, 1);
  p.toggleBlackout();
  assert.equal(p.state.blackout, false);
});

test("replay() setzt den laufenden Beat auf Anfang zurueck", () => {
  const p = createPresenter(BEATS);
  p.goTo(1);
  p.advanceShot();
  p.setProgress(0.8);
  p.replay();
  assert.equal(p.state.index, 1);
  assert.equal(p.state.shotIndex, 0);
  assert.equal(p.state.progress, 0);
});

test("setProgress() begrenzt auf 0..1", () => {
  const p = createPresenter(BEATS);
  p.setProgress(2);
  assert.equal(p.state.progress, 1);
  p.setProgress(-1);
  assert.equal(p.state.progress, 0);
});

test("beatProgress startet bei 0 und erreicht am Beat-Ende 1", () => {
  const p = createPresenter(BEATS);
  p.goTo(1); // zwei Shots, je 5 s
  assert.equal(p.state.beatProgress, 0);
  p.setProgress(1);
  p.advanceShot();
  p.setProgress(1);
  assert.equal(p.state.beatProgress, 1);
});

test("beatProgress springt beim Shot-Wechsel NICHT zurueck", () => {
  // Regressionstest: shot-relativer Fortschritt liess die historische Uhr
  // beim Shot-Wechsel rueckwaerts springen. Sie muss monoton laufen.
  const p = createPresenter(BEATS);
  p.goTo(1);
  const verlauf = [];
  p.setProgress(0.5);
  verlauf.push(p.state.beatProgress); // 2,5 s von 10 s
  p.setProgress(1);
  verlauf.push(p.state.beatProgress); // 5 s von 10 s
  p.advanceShot();
  verlauf.push(p.state.beatProgress); // weiterhin 5 s von 10 s
  p.setProgress(0.5);
  verlauf.push(p.state.beatProgress); // 7,5 s von 10 s
  assert.deepEqual(verlauf, [0.25, 0.5, 0.5, 0.75]);
  for (let i = 1; i < verlauf.length; i++) {
    assert.ok(verlauf[i] >= verlauf[i - 1], `Ruecksprung bei Index ${i}`);
  }
});

test("beatProgress ist bei einem Beat mit nur einem Shot der Shot-Fortschritt", () => {
  const p = createPresenter(BEATS);
  p.goTo(2); // ein Shot, 20 s
  p.setProgress(0.4);
  assert.equal(p.state.beatProgress, 0.4);
});

test("toggleOverview() schaltet die Kapiteluebersicht", () => {
  const p = createPresenter(BEATS);
  p.toggleOverview();
  assert.equal(p.state.overview, true);
  p.toggleOverview();
  assert.equal(p.state.overview, false);
});

test("goTo() schliesst eine offene Uebersicht", () => {
  const p = createPresenter(BEATS);
  p.toggleOverview();
  p.goTo(2);
  assert.equal(p.state.overview, false);
});

test("beat und shot liefern die aktuellen Objekte", () => {
  const p = createPresenter(BEATS);
  p.goTo(1);
  assert.equal(p.beat().id, 1);
  assert.equal(p.shot().file, "b.mp4");
  p.advanceShot();
  assert.equal(p.shot().file, "c.mp4");
});

test("Abonnenten werden bei jeder Zustandsaenderung benachrichtigt", () => {
  const p = createPresenter(BEATS);
  const seen = [];
  p.subscribe((s) => seen.push(s.index));
  p.next();
  p.next();
  p.prev();
  assert.deepEqual(seen, [1, 2, 1]);
});

test("unsubscribe beendet die Benachrichtigung", () => {
  const p = createPresenter(BEATS);
  let calls = 0;
  const off = p.subscribe(() => calls++);
  p.next();
  off();
  p.next();
  assert.equal(calls, 1);
});

test("state ist eine Kopie - Abonnenten koennen nichts kaputt machen", () => {
  const p = createPresenter(BEATS);
  const s = p.state;
  s.index = 99;
  assert.equal(p.state.index, 0);
});

test("leere Beat-Liste wird abgelehnt", () => {
  assert.throws(() => createPresenter([]), /mindestens einen Beat/i);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/presenter.test.js`
Expected: FAIL — `Cannot find module '../web/src/presenter.js'`.

- [ ] **Step 3: Write minimal implementation**

`web/src/presenter.js`:

```js
/**
 * Zustandsmaschine ueber die Beats.
 *
 * Kennt kein DOM, kein Video, keine Dateien - nur Zustand und Abonnenten.
 * Dadurch vollstaendig unit-testbar und unabhaengig von der Darstellung.
 */

export function createPresenter(beats) {
  if (!Array.isArray(beats) || beats.length === 0) {
    throw new Error("createPresenter braucht mindestens einen Beat");
  }

  let index = 0;
  let shotIndex = 0;
  let progress = 0;
  let started = false;
  let paused = false;
  let blackout = false;
  let overview = false;

  const listeners = new Set();

  /**
   * Fortschritt ueber den GANZEN Beat, nicht nur den laufenden Shot.
   *
   * Das ist die Groesse, die die historische Uhr braucht: sie interpoliert
   * von der Zeit dieses Beats zur Zeit des naechsten. Wuerde man ihr den
   * shot-relativen `progress` geben, liefe sie in jedem Shot die volle
   * Strecke ab und spraenge beim Shot-Wechsel zurueck - und alle fuenf
   * Beats mit sichtbarer Uhr haben mehr als einen Shot.
   */
  const beatProgress = () => {
    const shots = beats[index].shots;
    const total = shots.reduce((sum, shot) => sum + shot.duration, 0);
    if (total <= 0) return 0;
    const done = shots
      .slice(0, shotIndex)
      .reduce((sum, shot) => sum + shot.duration, 0);
    return Math.min(1, (done + shots[shotIndex].duration * progress) / total);
  };

  const snapshot = () => ({
    index,
    shotIndex,
    progress,
    beatProgress: beatProgress(),
    started,
    paused,
    blackout,
    overview,
    beatCount: beats.length,
    isFirst: index === 0,
    isLast: index === beats.length - 1,
  });

  const notify = () => {
    const state = snapshot();
    for (const fn of listeners) fn(state);
  };

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  /** Wechselt den Beat und setzt alles Beat-Lokale zurueck. */
  const moveTo = (target) => {
    const next = clamp(target, 0, beats.length - 1);
    index = next;
    shotIndex = 0;
    progress = 0;
    // Ein bewusster Beat-Wechsel hebt Pause und Uebersicht auf: der
    // Vortragende will weiter, nicht erst zweimal eine Taste druecken.
    paused = false;
    overview = false;
    notify();
  };

  return {
    get state() {
      return snapshot();
    },

    beat() {
      return beats[index];
    },

    shot() {
      return beats[index].shots[shotIndex];
    },

    start() {
      started = true;
      notify();
    },

    next() {
      moveTo(index + 1);
    },

    prev() {
      moveTo(index - 1);
    },

    goTo(target) {
      moveTo(target);
    },

    /** Naechster Shot im selben Beat. false, wenn der Beat erschoepft ist. */
    advanceShot() {
      if (shotIndex >= beats[index].shots.length - 1) return false;
      shotIndex += 1;
      progress = 0;
      notify();
      return true;
    },

    setProgress(value) {
      progress = clamp(Number(value) || 0, 0, 1);
      notify();
    },

    togglePause() {
      paused = !paused;
      notify();
    },

    toggleBlackout() {
      blackout = !blackout;
      notify();
    },

    toggleOverview() {
      overview = !overview;
      notify();
    },

    replay() {
      shotIndex = 0;
      progress = 0;
      paused = false;
      notify();
    },

    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/presenter.test.js`
Expected: PASS — `# pass 23`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add web/src/presenter.js tests/presenter.test.js
git commit -m "feat: DOM-freie Presenter-Zustandsmaschine"
```

---

## Task 5: Tastenzuordnung

Spec §9. Reine Abbildung, damit die Belegung ohne Browser prüfbar ist.

**Files:**
- Create: `web/src/keymap.js`
- Test: `tests/keymap.test.js`

- [ ] **Step 1: Write the failing test**

`tests/keymap.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { actionForKey, BEAT_JUMP_KEYS } from "../web/src/keymap.js";

test("Vorwaerts liegt auf Leertaste und Pfeil rechts", () => {
  assert.equal(actionForKey(" "), "next");
  assert.equal(actionForKey("ArrowRight"), "next");
});

test("Pfeil links geht zurueck", () => {
  assert.equal(actionForKey("ArrowLeft"), "prev");
});

test("die Buchstabenbefehle aus der Spec stimmen", () => {
  assert.equal(actionForKey("p"), "pause");
  assert.equal(actionForKey("r"), "replay");
  assert.equal(actionForKey("v"), "deepDive");
  assert.equal(actionForKey("b"), "blackout");
  assert.equal(actionForKey("f"), "fullscreen");
  assert.equal(actionForKey("Escape"), "overview");
});

test("Grossbuchstaben wirken gleich - Shift oder Feststelltaste darf nichts brechen", () => {
  assert.equal(actionForKey("P"), "pause");
  assert.equal(actionForKey("B"), "blackout");
  assert.equal(actionForKey("V"), "deepDive");
});

test("die Zifferntasten 0 bis 7 springen zum jeweiligen Beat", () => {
  for (let i = 0; i <= 7; i++) {
    assert.deepEqual(actionForKey(String(i)), { action: "goTo", index: i });
  }
});

test("Ziffern jenseits der acht Beats loesen nichts aus", () => {
  assert.equal(actionForKey("8"), null);
  assert.equal(actionForKey("9"), null);
});

test("unbelegte Tasten liefern null", () => {
  assert.equal(actionForKey("q"), null);
  assert.equal(actionForKey("Tab"), null);
  assert.equal(actionForKey("Enter"), null);
});

test("BEAT_JUMP_KEYS dokumentiert die acht Sprungtasten", () => {
  assert.deepEqual(BEAT_JUMP_KEYS, ["0", "1", "2", "3", "4", "5", "6", "7"]);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/keymap.test.js`
Expected: FAIL — `Cannot find module '../web/src/keymap.js'`.

- [ ] **Step 3: Write minimal implementation**

`web/src/keymap.js`:

```js
/**
 * Tastenbelegung des Presenter-Modus (Spec Abschnitt 9).
 * Reine Abbildung Tastenname -> Aktion, ohne DOM.
 */

/** Ziffern, die direkt zu einem Beat springen. Acht Beats, also 0..7. */
export const BEAT_JUMP_KEYS = ["0", "1", "2", "3", "4", "5", "6", "7"];

const SIMPLE = {
  " ": "next",
  arrowright: "next",
  arrowleft: "prev",
  p: "pause",
  r: "replay",
  v: "deepDive",
  b: "blackout",
  f: "fullscreen",
  escape: "overview",
};

/**
 * @param {string} key Wert von KeyboardEvent.key
 * @returns {string | {action: "goTo", index: number} | null}
 */
export function actionForKey(key) {
  if (typeof key !== "string" || key.length === 0) return null;

  if (BEAT_JUMP_KEYS.includes(key)) {
    return { action: "goTo", index: Number(key) };
  }

  // Leertaste nicht kleinschreiben - " " bleibt " ".
  const normalized = key === " " ? " " : key.toLowerCase();
  return SIMPLE[normalized] ?? null;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/keymap.test.js`
Expected: PASS — `# pass 8`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add web/src/keymap.js tests/keymap.test.js
git commit -m "feat: Tastenbelegung des Presenter-Modus"
```

---

## Task 6: Vollständigkeitsprüfung der Medien

Spec §12 nennt das den wichtigsten Test: eine fehlende Datei vor der Klasse ist der einzige echte Worst Case. In P0 fehlt alles — das Werkzeug ist damit gleichzeitig die Arbeitsliste für P1–P3.

**Files:**
- Create: `tools/check_media.js`
- Test: `tests/check_media.test.js`

- [ ] **Step 1: Write the failing test**

`tests/check_media.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { collectExpectedMedia, report } from "../tools/check_media.js";

const BEATS = [
  {
    id: 0,
    shots: [{ file: "media/video/shot_00.mp4", duration: 10 }],
    narration: { file: "media/audio/vo_00.mp3", text: "x" },
  },
  {
    id: 1,
    shots: [
      { file: "media/video/shot_01.mp4", duration: 5 },
      { file: "media/video/shot_02.mp4", duration: 5 },
    ],
    narration: { file: "media/audio/vo_01.mp3", text: "y" },
  },
];

test("collectExpectedMedia sammelt Video- und Tondateien mit Beat-Bezug", () => {
  const items = collectExpectedMedia(BEATS);
  assert.equal(items.length, 5);
  assert.deepEqual(items[0], { file: "media/video/shot_00.mp4", kind: "video", beat: 0 });
  assert.deepEqual(items[4], { file: "media/audio/vo_01.mp3", kind: "audio", beat: 1 });
});

test("report zaehlt vorhandene und fehlende Dateien", () => {
  const items = collectExpectedMedia(BEATS);
  const exists = (file) => file === "media/video/shot_00.mp4";
  const result = report(items, exists);
  assert.equal(result.present.length, 1);
  assert.equal(result.missing.length, 4);
  assert.equal(result.total, 5);
});

test("report ist ohne jede Datei nicht kaputt - das ist der Zustand in Phase P0", () => {
  const items = collectExpectedMedia(BEATS);
  const result = report(items, () => false);
  assert.equal(result.present.length, 0);
  assert.equal(result.missing.length, 5);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/check_media.test.js`
Expected: FAIL — `Cannot find module '../tools/check_media.js'`.

- [ ] **Step 3: Write minimal implementation**

`tools/check_media.js`:

```js
/**
 * Prueft, ob jede in beats.js referenzierte Mediendatei existiert.
 *
 *   node tools/check_media.js            Bericht, Exit 0
 *   node tools/check_media.js --strict   Exit 1 bei fehlenden Dateien
 *
 * Ohne --strict absichtlich erfolgreich: in den Phasen P0 bis P3 fehlen
 * Dateien planmaessig, und der Bericht ist dann die Arbeitsliste.
 * --strict gehoert in die Abnahme (Phase P7).
 */

import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = resolve(HERE, "..");

/** Flache Liste aller erwarteten Mediendateien. */
export function collectExpectedMedia(beats) {
  const items = [];
  for (const beat of beats) {
    for (const shot of beat.shots) {
      items.push({ file: shot.file, kind: "video", beat: beat.id });
    }
    if (beat.narration?.file) {
      items.push({ file: beat.narration.file, kind: "audio", beat: beat.id });
    }
  }
  return items;
}

/** Teilt die Liste in vorhanden und fehlend. `exists` ist injizierbar. */
export function report(items, exists) {
  const present = [];
  const missing = [];
  for (const item of items) {
    (exists(item.file) ? present : missing).push(item);
  }
  return { present, missing, total: items.length };
}

async function main() {
  const { BEATS } = await import("../web/src/beats.js");
  const items = collectExpectedMedia(BEATS);
  const result = report(items, (file) => existsSync(join(PROJECT_ROOT, file)));

  console.log(`Medien: ${result.present.length} von ${result.total} vorhanden.`);
  if (result.missing.length > 0) {
    console.log("\nFehlt noch:");
    for (const item of result.missing) {
      console.log(`  Beat ${item.beat}  ${item.kind.padEnd(5)}  ${item.file}`);
    }
  }

  const strict = process.argv.includes("--strict");
  if (strict && result.missing.length > 0) {
    console.error(`\nFEHLER: ${result.missing.length} Mediendatei(en) fehlen (--strict).`);
    process.exit(1);
  }
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))) {
  await main();
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/check_media.test.js`
Expected: PASS — `# pass 3`, `# fail 0`.

- [ ] **Step 5: Run the tool against the real data**

Run: `npm run check:media`
Expected: `Medien: 0 von 22 vorhanden.` und eine Liste von 14 Video- plus 8 Tondateien. Exit-Code 0.

- [ ] **Step 6: Commit**

```bash
git add tools/check_media.js tests/check_media.test.js
git commit -m "feat: Vollstaendigkeitspruefung der Mediendateien"
```

---

## Task 7: Lokaler Server und Doppelklick-Start

Spec §5: kein `file://`. Reine Standardbibliothek, keine Installation.

**Files:**
- Create: `tools/serve.py`
- Create: `START_PRAESENTATION.bat`

- [ ] **Step 1: Write the implementation**

`tools/serve.py`:

```python
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
```

`START_PRAESENTATION.bat`:

```bat
@echo off
title Sarajevo 1914 - Praesentation
cd /d "%~dp0"
echo.
echo   Sarajevo 1914 - Cinematic Live-Praesentation
echo   ------------------------------------------------
echo   Der Browser oeffnet sich in wenigen Sekunden.
echo   Dieses Fenster bitte offen lassen.
echo   Beenden: dieses Fenster schliessen oder Strg+C.
echo.
python tools\serve.py
if errorlevel 1 (
  echo.
  echo   FEHLER: Python wurde nicht gefunden oder der Port ist belegt.
  echo   Pruefen mit:  python --version
  pause
)
```

- [ ] **Step 2: Verify the server starts and serves the project root**

Run: `python tools/serve.py --port 8014 --no-browser` in einem Hintergrundprozess, dann in einer zweiten Shell:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8014/web/src/beats.js
```

Expected: `200`. Und für eine noch fehlende Mediendatei:

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8014/media/video/shot_00.mp4
```

Expected: `404` — planmäßig, die Datei entsteht erst in P2. Danach den Server beenden.

- [ ] **Step 3: Commit**

```bash
git add tools/serve.py START_PRAESENTATION.bat
git commit -m "feat: lokaler Server und Doppelklick-Start"
```

---

## Task 8: Seitengerüst und Gestaltung

**Files:**
- Create: `web/index.html`
- Create: `web/src/style.css`

- [ ] **Step 1: Write the implementation**

`web/index.html`:

```html
<!doctype html>
<html lang="de">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Sarajevo, 28. Juni 1914</title>
    <link rel="stylesheet" href="src/style.css" />
  </head>
  <body>
    <noscript class="fallback">
      <h1>Sarajevo, 28. Juni 1914</h1>
      <p>Diese Präsentation braucht JavaScript. Das Zeitprotokoll in Kurzform:</p>
      <ul>
        <li><strong>09:25</strong> Ankunft des Thronfolgerpaars am Bahnhof</li>
        <li><strong>10:10</strong> Erster Anschlag am Appelkai: Čabrinović wirft eine Granate</li>
        <li><strong>10:15</strong> Empfang im Rathaus, die Route wird geändert</li>
        <li><strong>10:45</strong> Die Änderung erreicht die Fahrer nicht, falsche Abzweigung</li>
        <li><strong>10:48</strong> Die Schüsse vor Schillers Delikatessenladen</li>
      </ul>
    </noscript>

    <main id="stage" class="stage" aria-live="polite">
      <div id="startscreen" class="startscreen">
        <p class="startscreen__kicker">Gesamtschule Meiderich · Geschichte</p>
        <h1 class="startscreen__title">Sarajevo<span>28. Juni 1914</span></h1>
        <button id="startbutton" class="startscreen__button" type="button">
          Präsentation starten
        </button>
        <p class="startscreen__hint">
          Weiter mit <kbd>Leertaste</kbd> · Pause <kbd>P</kbd> ·
          Schwarzbild <kbd>B</kbd> · Übersicht <kbd>Esc</kbd>
        </p>
      </div>

      <div id="videolayer" class="videolayer" hidden></div>
      <div id="placeholder" class="placeholder" hidden></div>
      <aside id="board" class="board" hidden></aside>
      <div id="clock" class="clock" hidden></div>
      <div id="blackout" class="blackout" hidden></div>
      <nav id="chapters" class="chapters" hidden></nav>
      <div id="overview" class="overview" hidden></div>
      <div id="pausebadge" class="pausebadge" hidden>Pause</div>
    </main>

    <script type="module" src="src/main.js"></script>
  </body>
</html>
```

`web/src/style.css`:

```css
/* 1920x1080-first. Bewusst dunkel, damit das Bild traegt und der
   Beamer nicht die Wand aufhellt. */

:root {
  --ink: #f2ece1;
  --ink-dim: #b6ada0;
  --bg: #0a0908;
  --accent: #c8a24a; /* gedecktes Messing, Epoche 1914 */
  --board-bg: rgba(12, 11, 10, 0.86);
  --serif: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sans: "Segoe UI", system-ui, sans-serif;
}

* {
  box-sizing: border-box;
}

html,
body {
  margin: 0;
  height: 100%;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--sans);
  overflow: hidden;
}

.stage {
  position: relative;
  width: 100vw;
  height: 100vh;
}

/* ---------- Startbildschirm ---------- */
/* Der Klick ist fachlich noetig: Browser geben Ton erst nach einer
   Nutzerinteraktion frei (Spec Abschnitt 11). */

.startscreen {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 1.6rem;
  text-align: center;
  background: radial-gradient(ellipse at 50% 40%, #1b1712 0%, #0a0908 70%);
}

.startscreen__kicker {
  margin: 0;
  color: var(--ink-dim);
  font-size: 0.95rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
}

.startscreen__title {
  margin: 0;
  font-family: var(--serif);
  font-size: clamp(3rem, 7vw, 6.5rem);
  font-weight: 400;
  line-height: 1;
  letter-spacing: 0.02em;
}

.startscreen__title span {
  display: block;
  margin-top: 0.9rem;
  color: var(--accent);
  font-size: clamp(1rem, 1.8vw, 1.7rem);
  letter-spacing: 0.34em;
  text-transform: uppercase;
}

.startscreen__button {
  padding: 0.85rem 2.4rem;
  border: 1px solid var(--accent);
  border-radius: 2px;
  background: transparent;
  color: var(--accent);
  font-family: var(--sans);
  font-size: 1rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 220ms ease, color 220ms ease;
}

.startscreen__button:hover,
.startscreen__button:focus-visible {
  background: var(--accent);
  color: #0a0908;
}

.startscreen__hint {
  margin: 0;
  color: var(--ink-dim);
  font-size: 0.85rem;
}

.startscreen__hint kbd {
  padding: 0.1rem 0.4rem;
  border: 1px solid #443c31;
  border-radius: 3px;
  font-family: var(--sans);
  font-size: 0.8rem;
}

/* ---------- Videoschicht ---------- */

.videolayer,
.videolayer video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  background: #000;
}

/* ---------- Platzhalter bei fehlender Videodatei ---------- */
/* Derselbe Pfad dient in P0 als Platzhalter und spaeter als
   Laufzeit-Rueckfall (Spec Abschnitt 11). */

.placeholder {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 1rem;
  padding: 4rem;
  text-align: center;
  background: repeating-linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.014) 0 12px,
      transparent 12px 24px
    ),
    #14110d;
}

.placeholder__beat {
  color: var(--accent);
  font-size: 0.85rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

.placeholder__title {
  margin: 0;
  max-width: 22ch;
  font-family: var(--serif);
  font-size: clamp(2rem, 4.4vw, 4rem);
  font-weight: 400;
  line-height: 1.1;
}

.placeholder__file {
  color: #6d6459;
  font-family: ui-monospace, Consolas, monospace;
  font-size: 0.8rem;
}

/* ---------- Texttafel ---------- */

.board {
  position: absolute;
  right: 4vw;
  bottom: 12vh;
  width: min(38rem, 42vw);
  padding: 2rem 2.2rem;
  border-left: 2px solid var(--accent);
  background: var(--board-bg);
  backdrop-filter: blur(7px);
  opacity: 0;
  transform: translateY(14px);
  transition: opacity 420ms ease, transform 420ms ease;
}

.board.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.board__heading {
  margin: 0 0 0.9rem;
  font-family: var(--serif);
  font-size: 1.55rem;
  font-weight: 400;
  color: var(--accent);
}

.board__text {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.6;
  color: var(--ink);
}

.board__quote {
  margin: 1.3rem 0 0;
  padding-left: 1rem;
  border-left: 1px solid #4a4237;
  font-family: var(--serif);
  font-size: 1.2rem;
  font-style: italic;
  line-height: 1.5;
}

.board__source {
  display: block;
  margin-top: 0.6rem;
  color: var(--ink-dim);
  font-family: var(--sans);
  font-size: 0.8rem;
  font-style: normal;
}

/* ---------- Historische Uhr ---------- */

.clock {
  position: absolute;
  top: 3.4vh;
  left: 4vw;
  font-family: var(--serif);
  font-size: clamp(2rem, 3.4vw, 3.2rem);
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.06em;
  color: var(--ink);
  text-shadow: 0 2px 18px rgba(0, 0, 0, 0.85);
}

.clock__label {
  display: block;
  color: var(--ink-dim);
  font-family: var(--sans);
  font-size: 0.72rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
}

/* ---------- Schwarzbild ---------- */

.blackout {
  position: absolute;
  inset: 0;
  background: #000;
  opacity: 0;
  transition: opacity 280ms ease;
  pointer-events: none;
}

.blackout.is-visible {
  opacity: 1;
}

/* ---------- Kapitelleiste, nur bei Mausbewegung ---------- */

.chapters {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  gap: 1px;
  padding: 0.7rem 4vw 1.1rem;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  opacity: 0;
  transition: opacity 320ms ease;
}

.chapters.is-visible {
  opacity: 1;
}

.chapters__item {
  flex: 1;
  padding: 0.5rem 0.3rem;
  border: 0;
  border-top: 2px solid #3a342b;
  background: transparent;
  color: var(--ink-dim);
  font-family: var(--sans);
  font-size: 0.74rem;
  text-align: left;
  cursor: pointer;
  transition: color 200ms ease, border-color 200ms ease;
}

.chapters__item:hover {
  color: var(--ink);
}

.chapters__item.is-current {
  border-top-color: var(--accent);
  color: var(--accent);
}

.chapters__time {
  display: block;
  font-variant-numeric: tabular-nums;
}

/* ---------- Kapiteluebersicht ---------- */

.overview {
  position: absolute;
  inset: 0;
  display: grid;
  align-content: center;
  gap: 0.5rem;
  padding: 6vh 8vw;
  background: rgba(6, 5, 5, 0.95);
}

.overview__heading {
  margin: 0 0 1.4rem;
  font-family: var(--serif);
  font-size: 1.7rem;
  font-weight: 400;
  color: var(--accent);
}

.overview__item {
  display: grid;
  grid-template-columns: 6rem 1fr;
  gap: 1.5rem;
  padding: 0.7rem 0.4rem;
  border: 0;
  border-bottom: 1px solid #241f19;
  background: transparent;
  color: var(--ink);
  font-family: var(--sans);
  font-size: 1.05rem;
  text-align: left;
  cursor: pointer;
}

.overview__item:hover {
  background: rgba(200, 162, 74, 0.08);
}

.overview__item.is-current {
  color: var(--accent);
}

.overview__time {
  color: var(--ink-dim);
  font-variant-numeric: tabular-nums;
}

/* ---------- Pause-Marke ---------- */

.pausebadge {
  position: absolute;
  top: 3.6vh;
  right: 4vw;
  padding: 0.35rem 0.9rem;
  border: 1px solid var(--accent);
  color: var(--accent);
  font-size: 0.78rem;
  letter-spacing: 0.24em;
  text-transform: uppercase;
}

/* ---------- Rueckfall ohne JavaScript ---------- */

.fallback {
  display: block;
  max-width: 46rem;
  margin: 12vh auto;
  padding: 0 2rem;
  font-family: var(--serif);
  line-height: 1.65;
}

@media (prefers-reduced-motion: reduce) {
  .board,
  .blackout,
  .chapters {
    transition: none;
  }
}
```

- [ ] **Step 2: Verify the page loads without console errors**

Server starten, dann `http://127.0.0.1:8014/web/index.html` öffnen.
Expected: Startbildschirm mit Titel und Schaltfläche sichtbar. In der Konsole nur der erwartete Fehler zu `src/main.js` (existiert noch nicht) — sonst nichts.

- [ ] **Step 3: Commit**

```bash
git add web/index.html web/src/style.css
git commit -m "feat: Seitengeruest und Gestaltung, 1920x1080-first"
```

---

## Task 9: Video-Stage mit Rückfall auf die Texttafel

Der Kern des Platzhalter-Konzepts. `probe` ist injizierbar, damit die Auswahl-Logik ohne Netz und ohne DOM testbar bleibt.

**Files:**
- Create: `web/src/stage/videoStage.js`
- Test: `tests/videoStage.test.js`

- [ ] **Step 1: Write the failing test**

`tests/videoStage.test.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import { chooseSource, describePlaceholder } from "../web/src/stage/videoStage.js";

const BEAT = {
  id: 2,
  clock: "10:10",
  title: "Der erste Anschlag am Appelkai",
  shots: [{ file: "media/video/shot_03.mp4", duration: 14 }],
  board: { heading: "10:10 — Der erste Anschlag", text: "Langer Tafeltext." },
};

test("chooseSource nimmt das Video, wenn die Datei erreichbar ist", async () => {
  const result = await chooseSource(BEAT.shots[0], async () => true);
  assert.deepEqual(result, { kind: "video", file: "media/video/shot_03.mp4" });
});

test("chooseSource faellt auf den Platzhalter zurueck, wenn die Datei fehlt", async () => {
  const result = await chooseSource(BEAT.shots[0], async () => false);
  assert.deepEqual(result, { kind: "placeholder", file: "media/video/shot_03.mp4" });
});

test("chooseSource behandelt einen Fehler der Pruefung wie eine fehlende Datei", async () => {
  const result = await chooseSource(BEAT.shots[0], async () => {
    throw new Error("Netzfehler");
  });
  assert.equal(result.kind, "placeholder");
});

test("describePlaceholder nennt Beat, Titel und Dateiname", () => {
  const info = describePlaceholder(BEAT, BEAT.shots[0]);
  assert.equal(info.beatLabel, "Beat 2 · 10:10");
  assert.equal(info.title, "Der erste Anschlag am Appelkai");
  assert.equal(info.file, "media/video/shot_03.mp4");
});

test("describePlaceholder laesst die Uhrzeit weg, wo keine existiert", () => {
  const prolog = { id: 0, clock: null, title: "Prolog: Vidovdan", shots: [], board: {} };
  const info = describePlaceholder(prolog, { file: "media/video/shot_00.mp4" });
  assert.equal(info.beatLabel, "Beat 0");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/videoStage.test.js`
Expected: FAIL — `Cannot find module '../web/src/stage/videoStage.js'`.

- [ ] **Step 3: Write minimal implementation**

`web/src/stage/videoStage.js`:

```js
/**
 * Video-Stage mit Rueckfall auf die Texttafel.
 *
 * Ein Mechanismus, zwei Zwecke:
 *  - In Phase P0 existiert noch keine Videodatei, also zeigt jeder Beat
 *    seinen Platzhalter. Der Ablauf und das Timing sind trotzdem pruefbar.
 *  - Im Betrieb ist derselbe Pfad der von Spec Abschnitt 11 geforderte
 *    Rueckfall: eine fehlende Datei darf die Praesentation nie anhalten.
 *
 * chooseSource und describePlaceholder sind DOM-frei und damit testbar;
 * nur createVideoStage beruehrt das DOM.
 */

/** Prueft per HEAD, ob eine Datei ausgeliefert wird. */
export async function probeFile(file) {
  const response = await fetch(file, { method: "HEAD" });
  return response.ok;
}

/**
 * Entscheidet zwischen Video und Platzhalter.
 * @param {{file: string}} shot
 * @param {(file: string) => Promise<boolean>} probe
 */
export async function chooseSource(shot, probe = probeFile) {
  try {
    const ok = await probe(shot.file);
    return { kind: ok ? "video" : "placeholder", file: shot.file };
  } catch {
    // Netzfehler wie fehlende Datei behandeln - die Praesentation laeuft weiter.
    return { kind: "placeholder", file: shot.file };
  }
}

/** Beschreibungstexte des Platzhalters. */
export function describePlaceholder(beat, shot) {
  return {
    beatLabel: beat.clock ? `Beat ${beat.id} · ${beat.clock}` : `Beat ${beat.id}`,
    title: beat.title,
    file: shot.file,
  };
}

/**
 * @param {{video: HTMLElement, placeholder: HTMLElement}} elements
 */
export function createVideoStage(elements, probe = probeFile) {
  const { video: videoLayer, placeholder } = elements;
  let current = null;

  const clear = () => {
    if (current) {
      current.pause();
      current.removeAttribute("src");
      current.load();
      current.remove();
      current = null;
    }
    videoLayer.hidden = true;
    placeholder.hidden = true;
  };

  const showPlaceholder = (beat, shot) => {
    const info = describePlaceholder(beat, shot);
    placeholder.replaceChildren();

    const label = document.createElement("p");
    label.className = "placeholder__beat";
    label.textContent = info.beatLabel;

    const title = document.createElement("h2");
    title.className = "placeholder__title";
    title.textContent = info.title;

    const file = document.createElement("p");
    file.className = "placeholder__file";
    file.textContent = `${info.file} — noch nicht gerendert`;

    placeholder.append(label, title, file);
    placeholder.hidden = false;
  };

  return {
    /**
     * Zeigt den Shot. Liefert die Dauer in Sekunden, mit der der
     * Vortragsablauf weiterrechnet.
     * @returns {Promise<{kind: string, duration: number}>}
     */
    async show(beat, shot, { onEnded } = {}) {
      clear();
      const source = await chooseSource(shot, probe);

      if (source.kind === "placeholder") {
        showPlaceholder(beat, shot);
        return { kind: "placeholder", duration: shot.duration };
      }

      const element = document.createElement("video");
      element.src = source.file;
      element.preload = "auto";
      element.playsInline = true;
      // Ton kommt in Phase P1 aus der Web-Audio-Schicht, nicht aus dem Video.
      element.muted = true;
      if (onEnded) element.addEventListener("ended", onEnded, { once: true });
      videoLayer.replaceChildren(element);
      videoLayer.hidden = false;
      current = element;
      await element.play().catch(() => {
        // Autoplay verweigert: Standbild statt Absturz.
      });
      return { kind: "video", duration: shot.duration };
    },

    pause() {
      current?.pause();
    },

    resume() {
      current?.play().catch(() => {});
    },

    dispose: clear,
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/videoStage.test.js`
Expected: PASS — `# pass 5`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add web/src/stage/videoStage.js tests/videoStage.test.js
git commit -m "feat: Video-Stage mit Rueckfall auf die Texttafel"
```

---

## Task 10: Overlays

DOM-Schicht: Tafel, Uhr, Kapitelleiste, Übersicht, Schwarzbild, Pause-Marke. Wird im Browser verifiziert (Task 12).

**Files:**
- Create: `web/src/ui/overlays.js`

- [ ] **Step 1: Write the implementation**

`web/src/ui/overlays.js`:

```js
/**
 * DOM-Schicht. Liest Zustand, schreibt nie hinein.
 * Jede Funktion nimmt ihre Elemente entgegen - kein globales Suchen.
 */

import { interpolateClock } from "../clock.js";
import { nextClockAfter } from "../beats.js";

/** Texttafel eines Beats. */
export function createBoard(element) {
  return {
    show(beat) {
      element.replaceChildren();

      const heading = document.createElement("h2");
      heading.className = "board__heading";
      heading.textContent = beat.board.heading;

      const text = document.createElement("p");
      text.className = "board__text";
      text.textContent = beat.board.text;

      element.append(heading, text);

      if (beat.board.quote) {
        const quote = document.createElement("blockquote");
        quote.className = "board__quote";
        quote.textContent = `„${beat.board.quote}"`;

        const source = document.createElement("cite");
        source.className = "board__source";
        source.textContent = beat.board.source;

        quote.append(source);
        element.append(quote);
      }

      element.hidden = false;
      // Erst im naechsten Frame einblenden, sonst ueberspringt der
      // Browser die Transition.
      requestAnimationFrame(() => element.classList.add("is-visible"));
    },

    hide() {
      element.classList.remove("is-visible");
      element.hidden = true;
    },
  };
}

/** Historische Uhr. */
export function createClock(element, beats) {
  const label = document.createElement("span");
  label.className = "clock__label";
  label.textContent = "28. Juni 1914";
  const time = document.createElement("span");
  element.replaceChildren(label, time);

  return {
    update(index, progress) {
      const beat = beats[index];
      if (!beat.clock) {
        element.hidden = true;
        return;
      }
      time.textContent = interpolateClock(beat.clock, nextClockAfter(index), progress);
      element.hidden = false;
    },
  };
}

/** Kapitelleiste am unteren Rand, erscheint nur bei Mausbewegung. */
export function createChapterBar(element, beats, onSelect) {
  const buttons = beats.map((beat, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chapters__item";

    const time = document.createElement("span");
    time.className = "chapters__time";
    time.textContent = beat.clock ?? "—";

    const title = document.createElement("span");
    title.textContent = beat.title;

    button.append(time, title);
    button.addEventListener("click", () => onSelect(index));
    return button;
  });

  element.replaceChildren(...buttons);
  element.hidden = false;

  let timer = null;
  const reveal = () => {
    element.classList.add("is-visible");
    clearTimeout(timer);
    timer = setTimeout(() => element.classList.remove("is-visible"), 2600);
  };
  window.addEventListener("mousemove", reveal, { passive: true });

  return {
    update(index) {
      buttons.forEach((button, i) => {
        button.classList.toggle("is-current", i === index);
      });
    },
  };
}

/** Kapiteluebersicht, aufgerufen mit Esc. */
export function createOverview(element, beats, onSelect) {
  const heading = document.createElement("h2");
  heading.className = "overview__heading";
  heading.textContent = "Kapitel";

  const buttons = beats.map((beat, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "overview__item";

    const time = document.createElement("span");
    time.className = "overview__time";
    time.textContent = beat.clock ?? "—";

    const title = document.createElement("span");
    title.textContent = beat.title;

    button.append(time, title);
    button.addEventListener("click", () => onSelect(index));
    return button;
  });

  element.replaceChildren(heading, ...buttons);

  return {
    update(open, index) {
      element.hidden = !open;
      buttons.forEach((button, i) => {
        button.classList.toggle("is-current", i === index);
      });
    },
  };
}

/** Schwarzbild und Pause-Marke. */
export function createStatusLayers({ blackout, pausebadge }) {
  return {
    update(state) {
      blackout.hidden = false;
      blackout.classList.toggle("is-visible", state.blackout);
      pausebadge.hidden = !state.paused;
    },
  };
}
```

- [ ] **Step 2: Verify the module parses**

Run: `node --input-type=module -e "import('./web/src/ui/overlays.js').then(m => console.log(Object.keys(m).join(',')))"`
Expected: `createBoard,createClock,createChapterBar,createOverview,createStatusLayers` — der Import gelingt, weil auf Modulebene kein DOM angefasst wird.

- [ ] **Step 3: Commit**

```bash
git add web/src/ui/overlays.js
git commit -m "feat: Overlays fuer Tafel, Uhr, Kapitelleiste und Uebersicht"
```

---

## Task 11: Verdrahtung

**Files:**
- Create: `web/src/main.js`

- [ ] **Step 1: Write the implementation**

`web/src/main.js`:

```js
/**
 * Verdrahtung: Tastatur -> keymap -> presenter -> Stage und Overlays.
 * Enthaelt selbst keine Regeln, nur Verbindungen.
 */

import { BEATS } from "./beats.js";
import { createPresenter } from "./presenter.js";
import { actionForKey } from "./keymap.js";
import { createVideoStage } from "./stage/videoStage.js";
import {
  createBoard,
  createChapterBar,
  createClock,
  createOverview,
  createStatusLayers,
} from "./ui/overlays.js";

const el = (id) => document.getElementById(id);

const presenter = createPresenter(BEATS);

const stage = createVideoStage({
  video: el("videolayer"),
  placeholder: el("placeholder"),
});
const board = createBoard(el("board"));
const clock = createClock(el("clock"), BEATS);
const chapters = createChapterBar(el("chapters"), BEATS, (i) => presenter.goTo(i));
const overview = createOverview(el("overview"), BEATS, (i) => presenter.goTo(i));
const status = createStatusLayers({
  blackout: el("blackout"),
  pausebadge: el("pausebadge"),
});

/* ---------- Fortschritt des laufenden Shots ---------- */
/* Treibt die historische Uhr und den automatischen Shot-Wechsel.
   Bewusst mit setInterval statt requestAnimationFrame: in
   Hintergrund-Tabs pausiert rAF, und die Uhr braucht nur 10 Hz. */

let ticker = null;
let shotStartedAt = 0;
let shotDuration = 0;

function stopTicker() {
  clearInterval(ticker);
  ticker = null;
}

function startTicker(duration) {
  stopTicker();
  shotStartedAt = performance.now();
  shotDuration = Math.max(0.1, duration);
  ticker = setInterval(() => {
    if (presenter.state.paused) return;
    const elapsed = (performance.now() - shotStartedAt) / 1000;
    presenter.setProgress(elapsed / shotDuration);
    if (elapsed >= shotDuration) {
      stopTicker();
      // Naechster Shot im Beat. Ist der Beat zu Ende, bleibt das Bild
      // stehen - der Vortragende entscheidet, wann es weitergeht.
      if (presenter.advanceShot()) showCurrentShot();
    }
  }, 100);
}

async function showCurrentShot() {
  const beat = presenter.beat();
  const shot = presenter.shot();
  const result = await stage.show(beat, shot, {
    onEnded: () => {
      stopTicker();
      if (presenter.advanceShot()) showCurrentShot();
    },
  });
  startTicker(result.duration);
}

/* ---------- Zustand -> Darstellung ---------- */

let lastIndex = -1;
let lastPaused = false;

presenter.subscribe((state) => {
  // beatProgress, nicht progress: die Uhr laeuft ueber den ganzen Beat.
  // Mit dem shot-relativen Wert spraenge sie bei jedem Shot-Wechsel zurueck.
  clock.update(state.index, state.beatProgress);
  chapters.update(state.index);
  overview.update(state.overview, state.index);
  status.update(state);

  if (state.index !== lastIndex) {
    lastIndex = state.index;
    board.show(presenter.beat());
    if (state.started) showCurrentShot();
  }
  // Ein Shot-Wechsel braucht hier nichts: er wird ausschliesslich von
  // showCurrentShot ausgeloest, das das Video selbst schon gesetzt hat.

  // Nur bei echtem Wechsel schalten - setProgress feuert zehnmal pro
  // Sekunde, und play() im Dauerlauf waere reine Verschwendung.
  if (state.paused !== lastPaused) {
    lastPaused = state.paused;
    if (state.paused) stage.pause();
    else stage.resume();
  }
});

/* ---------- Tastatur ---------- */

const ACTIONS = {
  next: () => presenter.next(),
  prev: () => presenter.prev(),
  pause: () => presenter.togglePause(),
  replay: () => {
    presenter.replay();
    showCurrentShot();
  },
  blackout: () => presenter.toggleBlackout(),
  overview: () => presenter.toggleOverview(),
  // Die fuenf Vertiefungsmodule kommen in Phase P6. Bis dahin oeffnet V
  // die Kapiteluebersicht, damit die Taste nie ins Leere greift.
  deepDive: () => presenter.toggleOverview(),
  fullscreen: () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => {});
  },
};

window.addEventListener("keydown", (event) => {
  if (event.repeat) return;
  const action = actionForKey(event.key);
  if (!action) return;
  event.preventDefault();

  if (typeof action === "object") {
    presenter.goTo(action.index);
    return;
  }
  ACTIONS[action]?.();
});

el("stage").addEventListener("click", (event) => {
  // Klicks auf Bedienelemente nicht als Weiterblaettern deuten.
  if (event.target.closest("button")) return;
  if (!presenter.state.started) return;
  presenter.next();
});

/* ---------- Start ---------- */

el("startbutton").addEventListener("click", () => {
  el("startscreen").hidden = true;
  presenter.start();
  board.show(presenter.beat());
  showCurrentShot();
});

// Der erste Zustandsanstoss, damit Uhr und Kapitelleiste stimmen,
// bevor gestartet wird.
presenter.setProgress(0);
```

- [ ] **Step 2: Commit**

```bash
git add web/src/main.js
git commit -m "feat: Verdrahtung von Tastatur, Presenter, Stage und Overlays"
```

---

## Task 12: Browser-Verifikation und vollständiger Durchlauf

Spec §12. Achtung: Browser-Pane-Tabs laufen in dieser Umgebung häufig mit `document.hidden === true` — dort pausieren rAF, CSS-Transitions und Screenshots. Deshalb wird primär über `javascript_tool` verifiziert, also über gelesene Werte statt über Bilder.

**Files:** keine neuen — nur Prüfung und ggf. Korrekturen.

- [ ] **Step 1: Run the full test suite**

Run: `npm test`
Expected: PASS, insgesamt 56 Tests über sieben Dateien, `# fail 0`.

- [ ] **Step 2: Start the server and open the page**

`.claude/launch.json` anlegen, damit die Vorschau den Server startet:

```json
{
  "version": "0.0.1",
  "configurations": [
    {
      "name": "sarajevo",
      "runtimeExecutable": "python",
      "runtimeArgs": ["tools/serve.py", "--port", "8014", "--no-browser"],
      "port": 8014
    }
  ]
}
```

Vorschau über `preview_start` mit `{name: "sarajevo"}` starten, dann zu
`http://127.0.0.1:8014/web/index.html` navigieren.

- [ ] **Step 3: Check the console for errors**

`read_console_messages` mit `onlyErrors: true`.
Expected: keine Fehler. 404-Meldungen zu `media/video/*.mp4` sind **erwartet** und erscheinen als Netzwerk-, nicht als Konsolenfehler.

- [ ] **Step 4: Verify the presenter logic in the live page**

Über `javascript_tool` prüfen — Zustand lesen statt Bilder machen:

```js
(() => {
  const press = (key) => window.dispatchEvent(new KeyboardEvent("keydown", { key }));
  document.getElementById("startbutton").click();
  const clockText = () => document.getElementById("clock").textContent;
  const out = { start: clockText() };
  press(" "); out.nachEinmalWeiter = clockText();
  press("2"); out.sprungZuBeat2 = clockText();
  press("b"); out.blackout = document.getElementById("blackout").classList.contains("is-visible");
  press("b");
  press("p"); out.pauseSichtbar = !document.getElementById("pausebadge").hidden;
  press("p");
  press("Escape"); out.uebersichtOffen = !document.getElementById("overview").hidden;
  press("Escape");
  out.platzhalterSichtbar = !document.getElementById("placeholder").hidden;
  out.tafelText = document.querySelector(".board__heading")?.textContent;
  return out;
})();
```

Expected: `nachEinmalWeiter` enthält `09:25`, `sprungZuBeat2` enthält `10:10`,
`blackout` ist `true`, `pauseSichtbar` ist `true`, `uebersichtOffen` ist `true`,
`platzhalterSichtbar` ist `true`, `tafelText` beginnt mit `10:10`.

- [ ] **Step 5: Verify every beat is reachable and shows its board**

```js
(() => {
  const press = (key) => window.dispatchEvent(new KeyboardEvent("keydown", { key }));
  const result = [];
  for (let i = 0; i <= 7; i++) {
    press(String(i));
    result.push({
      beat: i,
      tafel: document.querySelector(".board__heading")?.textContent ?? null,
      uhr: document.getElementById("clock").hidden ? null : document.getElementById("clock").textContent,
      platzhalter: document.querySelector(".placeholder__title")?.textContent ?? null,
    });
  }
  return result;
})();
```

Expected: acht Einträge, jeder mit gefüllter `tafel` und `platzhalter`. `uhr` ist
`null` bei den Beats 0, 6 und 7 und gesetzt bei 1 bis 5.

- [ ] **Step 6: Verify the quote appears only in Beat 5**

```js
(() => {
  const press = (key) => window.dispatchEvent(new KeyboardEvent("keydown", { key }));
  const withQuote = [];
  for (let i = 0; i <= 7; i++) {
    press(String(i));
    if (document.querySelector(".board__quote")) withQuote.push(i);
  }
  return { withQuote, source: document.querySelector(".board__source")?.textContent };
})();
```

Expected: `withQuote` ist `[5]`, `source` nennt Graf Franz von Harrach.

- [ ] **Step 7: Fix anything the checks surfaced, then re-run**

Bei Abweichung: Quelldatei korrigieren, `npm test` erneut laufen lassen, Seite neu laden und ab Schritt 3 wiederholen.

- [ ] **Step 8: Commit**

```bash
git add .claude/launch.json
git commit -m "chore: Vorschau-Konfiguration fuer den lokalen Server"
```

---

## Task 13: Timing-Abnahme und Übergabe an P1

- [ ] **Step 1: Record the editorial timing**

Run: `node -e "import('./web/src/beats.js').then(m => { const t = m.totalShotSeconds(); console.log('Filmlaenge:', Math.floor(t/60) + ':' + String(t%60).padStart(2,'0')); for (const b of m.BEATS) console.log('  Beat', b.id, b.shots.reduce((s,x)=>s+x.duration,0) + 's', b.title); })"`

Expected: Gesamtlänge `4:38`, danach acht Zeilen mit den Beat-Längen.

- [ ] **Step 2: Walk the presentation once end to end, as in class**

`START_PRAESENTATION.bat` doppelklicken, `F` für Vollbild, dann mit der
Leertaste durch alle acht Beats. Dabei notieren: Fühlt sich ein Beat zu lang
oder zu kurz an? Reicht die Standzeit der Tafeln zum Lesen?

Expected: Der Durchlauf gelingt ohne Eingriff. Auffälligkeiten werden als
Änderung der `duration`-Werte in `beats.js` festgehalten — **jetzt**, wo eine
Änderung nichts kostet, und nicht nach dem Rendern.

- [ ] **Step 3: Commit any timing corrections**

```bash
git add web/src/beats.js
git commit -m "tune: Shot-Dauern nach dem ersten vollstaendigen Durchlauf"
```

- [ ] **Step 4: Update the README build section**

In `README.md` den Abschnitt „Bauen" um die nun echten Befehle ergänzen:

```markdown
## Bauen

Voraussetzungen: Python 3, Node ≥ 20. Für die späteren Phasen zusätzlich
Blender 5.1, numpy/scipy/pillow und ffmpeg.

```bash
npm test              # Logik-Tests, ohne Abhängigkeiten
npm run check:media   # zeigt, welche Medien noch fehlen
npm run serve         # lokaler Server auf Port 8014
```
```

- [ ] **Step 5: Commit and push**

```bash
git add README.md
git commit -m "docs: Bau- und Pruefbefehle im README"
git push
```

---

## Definition of Done für P0

- `npm test` läuft grün, 56 Tests über sieben Dateien.
- `npm run check:media` meldet 22 erwartete Dateien und listet die fehlenden auf.
- `START_PRAESENTATION.bat` öffnet die Präsentation; alle acht Beats sind per
  Leertaste und per Ziffer erreichbar.
- Jeder Beat zeigt Platzhalter und Texttafel; die historische Uhr läuft in den
  Beats 1 bis 5 sichtbar von 09:25 auf 10:48.
- Pause, Schwarzbild, Wiederholen, Übersicht und Vollbild funktionieren.
- Die Shot-Dauern sind nach einem echten Durchlauf justiert.
- Alles committet und nach GitHub gepusht.

## Anschluss

**P1 (Ton)** baut auf `beats.js` auf: die `narration.text`- und
`narration.instructions`-Felder sind bereits die Vorlage für `audio/narration.py`.
Die 22 von `check_media.js` gemeldeten Dateien sind die Arbeitsliste — acht
Tondateien entstehen in P1, vierzehn Videodateien in P2 und P3. Jede erscheint
automatisch, sobald sie existiert; am Code muss dafür nichts geändert werden.
