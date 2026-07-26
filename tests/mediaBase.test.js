import { test } from "node:test";
import assert from "node:assert/strict";
import { mediaUrl } from "../web/src/mediaBase.js";
import { BEATS } from "../web/src/beats.js";

test("mediaUrl fuehrt aus dem web-Verzeichnis heraus zur Projektwurzel", () => {
  // Regressionstest. Ohne das "../" laedt der Browser /web/media/... -
  // dort liegt nichts. Es fiel lange nicht auf, weil die Videos noch
  // fehlten und der Platzhalter-Rueckfall es richtig aussehen liess.
  assert.equal(mediaUrl("media/video/shot_00.mp4"), "../media/video/shot_00.mp4");
  assert.equal(mediaUrl("media/audio/vo_00.mp3"), "../media/audio/vo_00.mp3");
});

test("aufgeloest gegen die Seite landet jede Datei unter /media/", () => {
  const seite = "http://127.0.0.1:8014/web/index.html";
  for (const beat of BEATS) {
    for (const shot of beat.shots) {
      const url = new URL(mediaUrl(shot.file), seite);
      assert.equal(
        url.pathname,
        `/${shot.file}`,
        `Beat ${beat.id}: ${shot.file} landet bei ${url.pathname}`,
      );
    }
    for (const datei of [beat.narration.file, beat.narration.score, beat.narration.quoteFile]) {
      if (!datei) continue;
      assert.equal(new URL(mediaUrl(datei), seite).pathname, `/${datei}`);
    }
  }
});
