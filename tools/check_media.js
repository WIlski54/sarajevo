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
      items.push({ file: beat.narration.file, kind: "stimme", beat: beat.id });
    }
    if (beat.narration?.score) {
      items.push({ file: beat.narration.score, kind: "score", beat: beat.id });
    }
    if (beat.narration?.quoteFile) {
      items.push({ file: beat.narration.quoteFile, kind: "zitat", beat: beat.id });
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
