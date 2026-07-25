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
