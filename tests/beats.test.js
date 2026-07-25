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
