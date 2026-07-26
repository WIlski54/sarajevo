import { test } from "node:test";
import assert from "node:assert/strict";
import { tracksForBeat } from "../web/src/audio/engine.js";
import { BEATS } from "../web/src/beats.js";

test("ein gewoehnlicher Beat hat Score und Stimme", () => {
  const tracks = tracksForBeat(BEATS[0]);
  assert.deepEqual(
    tracks.map((t) => t.bus),
    ["score", "voice"],
  );
  assert.equal(tracks[0].file, "media/audio/score_00.mp3");
  assert.equal(tracks[1].file, "media/audio/vo_00.mp3");
});

test("der Score steht vor der Stimme - er ist das Bett, nicht die Auflage", () => {
  for (const beat of BEATS) {
    const tracks = tracksForBeat(beat);
    const score = tracks.findIndex((t) => t.bus === "score");
    const voice = tracks.findIndex((t) => t.bus === "voice");
    assert.ok(score < voice, `Beat ${beat.id}: Reihenfolge stimmt nicht`);
  }
});

test("Beat 5 haengt das Zitat hinten an, statt es zu ueberlagern", () => {
  const tracks = tracksForBeat(BEATS[5]);
  const zitat = tracks.find((t) => t.file.includes("_zitat"));
  assert.ok(zitat, "Zitatspur fehlt");
  assert.equal(zitat.bus, "voice");
  assert.equal(zitat.after, "voice", "Zitat muss der Erzaehlung folgen");
});

test("nur Beat 5 hat eine Zitatspur", () => {
  const mitZitat = BEATS.filter((b) =>
    tracksForBeat(b).some((t) => t.after === "voice"),
  ).map((b) => b.id);
  assert.deepEqual(mitZitat, [5]);
});

test("jeder Beat bringt genau eine Erzaehlspur mit", () => {
  for (const beat of BEATS) {
    const stimmen = tracksForBeat(beat).filter((t) => t.bus === "voice" && !t.after);
    assert.equal(stimmen.length, 1, `Beat ${beat.id}`);
  }
});

test("ein Beat ohne Tondaten liefert keine Spuren statt zu werfen", () => {
  // Waehrend der Phasen P2 und P3 kann ein Beat voruebergehend ohne Ton
  // dastehen. Das darf nie eine Ausnahme ausloesen.
  assert.deepEqual(tracksForBeat({ id: 99, narration: {} }), []);
  assert.deepEqual(tracksForBeat({ id: 99 }), []);
});
