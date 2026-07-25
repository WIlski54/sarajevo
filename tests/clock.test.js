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
