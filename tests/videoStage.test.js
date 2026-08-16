import { test } from "node:test";
import assert from "node:assert/strict";
import { chooseSource, describePlaceholder, probeFile } from "../web/src/stage/videoStage.js";

/** Ersetzt fetch fuer die Dauer eines Tests. */
async function mitFetch(antwort, fn) {
  const vorher = globalThis.fetch;
  globalThis.fetch = async () => antwort;
  try {
    return await fn();
  } finally {
    globalThis.fetch = vorher;
  }
}

const antwort = (ok, contentLength) => ({
  ok,
  headers: { get: (name) => (name === "content-length" ? contentLength : null) },
});

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

test("probeFile lehnt eine 0-Byte-Datei ab, obwohl sie HTTP 200 liefert", async () => {
  // Ein abgebrochener Blender-Render hinterlaesst genau so eine Datei.
  // Wuerde sie als gueltig durchgehen, zeigte die Praesentation schwarz -
  // und der Platzhalter-Rueckfall, der als Sicherheitsnetz gedacht ist,
  // wuerde den Fehler verdecken statt ihn aufzufangen.
  const ok = await mitFetch(antwort(true, "0"), () => probeFile("media/video/x.mp4"));
  assert.equal(ok, false);
});

test("probeFile lehnt eine Rumpfdatei ab", async () => {
  const ok = await mitFetch(antwort(true, "4096"), () => probeFile("media/video/x.mp4"));
  assert.equal(ok, false);
});

test("probeFile akzeptiert eine Datei normaler Groesse", async () => {
  const ok = await mitFetch(antwort(true, "8460000"), () => probeFile("media/video/x.mp4"));
  assert.equal(ok, true);
});

test("probeFile akzeptiert, wenn der Server keine Groesse meldet", async () => {
  // Lieber ein Versuch als ein falscher Rueckfall.
  const ok = await mitFetch(antwort(true, null), () => probeFile("media/video/x.mp4"));
  assert.equal(ok, true);
});

test("probeFile lehnt ab, wenn die Datei fehlt", async () => {
  const ok = await mitFetch(antwort(false, null), () => probeFile("media/video/x.mp4"));
  assert.equal(ok, false);
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
