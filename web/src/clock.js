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
