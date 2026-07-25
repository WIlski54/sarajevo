/**
 * Tastenbelegung des Presenter-Modus (Spec Abschnitt 9).
 * Reine Abbildung Tastenname -> Aktion, ohne DOM.
 */

/** Ziffern, die direkt zu einem Beat springen. Acht Beats, also 0..7. */
export const BEAT_JUMP_KEYS = ["0", "1", "2", "3", "4", "5", "6", "7"];

const SIMPLE = {
  " ": "next",
  arrowright: "next",
  arrowleft: "prev",
  p: "pause",
  r: "replay",
  v: "deepDive",
  b: "blackout",
  f: "fullscreen",
  escape: "overview",
};

/**
 * @param {string} key Wert von KeyboardEvent.key
 * @returns {string | {action: "goTo", index: number} | null}
 */
export function actionForKey(key) {
  if (typeof key !== "string" || key.length === 0) return null;

  if (BEAT_JUMP_KEYS.includes(key)) {
    return { action: "goTo", index: Number(key) };
  }

  // Leertaste nicht kleinschreiben - " " bleibt " ".
  const normalized = key === " " ? " " : key.toLowerCase();
  return SIMPLE[normalized] ?? null;
}
