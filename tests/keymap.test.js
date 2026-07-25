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
