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
