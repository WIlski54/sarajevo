/**
 * Zustandsmaschine ueber die Beats.
 *
 * Kennt kein DOM, kein Video, keine Dateien - nur Zustand und Abonnenten.
 * Dadurch vollstaendig unit-testbar und unabhaengig von der Darstellung.
 */

export function createPresenter(beats) {
  if (!Array.isArray(beats) || beats.length === 0) {
    throw new Error("createPresenter braucht mindestens einen Beat");
  }

  let index = 0;
  let shotIndex = 0;
  let progress = 0;
  let started = false;
  let paused = false;
  let blackout = false;
  let overview = false;

  const listeners = new Set();

  /**
   * Fortschritt ueber den GANZEN Beat, nicht nur den laufenden Shot.
   *
   * Das ist die Groesse, die die historische Uhr braucht: sie interpoliert
   * von der Zeit dieses Beats zur Zeit des naechsten. Wuerde man ihr den
   * shot-relativen `progress` geben, liefe sie in jedem Shot die volle
   * Strecke ab und spraenge beim Shot-Wechsel zurueck - und alle fuenf
   * Beats mit sichtbarer Uhr haben mehr als einen Shot.
   */
  const beatProgress = () => {
    const shots = beats[index].shots;
    const total = shots.reduce((sum, shot) => sum + shot.duration, 0);
    if (total <= 0) return 0;
    const done = shots
      .slice(0, shotIndex)
      .reduce((sum, shot) => sum + shot.duration, 0);
    return Math.min(1, (done + shots[shotIndex].duration * progress) / total);
  };

  const snapshot = () => ({
    index,
    shotIndex,
    progress,
    beatProgress: beatProgress(),
    started,
    paused,
    blackout,
    overview,
    beatCount: beats.length,
    isFirst: index === 0,
    isLast: index === beats.length - 1,
  });

  const notify = () => {
    const state = snapshot();
    for (const fn of listeners) fn(state);
  };

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));

  /** Wechselt den Beat und setzt alles Beat-Lokale zurueck. */
  const moveTo = (target) => {
    const next = clamp(target, 0, beats.length - 1);
    index = next;
    shotIndex = 0;
    progress = 0;
    // Ein bewusster Beat-Wechsel hebt Pause und Uebersicht auf: der
    // Vortragende will weiter, nicht erst zweimal eine Taste druecken.
    paused = false;
    overview = false;
    notify();
  };

  return {
    get state() {
      return snapshot();
    },

    beat() {
      return beats[index];
    },

    shot() {
      return beats[index].shots[shotIndex];
    },

    start() {
      started = true;
      notify();
    },

    next() {
      moveTo(index + 1);
    },

    prev() {
      moveTo(index - 1);
    },

    goTo(target) {
      moveTo(target);
    },

    /** Naechster Shot im selben Beat. false, wenn der Beat erschoepft ist. */
    advanceShot() {
      if (shotIndex >= beats[index].shots.length - 1) return false;
      shotIndex += 1;
      progress = 0;
      notify();
      return true;
    },

    setProgress(value) {
      progress = clamp(Number(value) || 0, 0, 1);
      notify();
    },

    togglePause() {
      paused = !paused;
      notify();
    },

    toggleBlackout() {
      blackout = !blackout;
      notify();
    },

    toggleOverview() {
      overview = !overview;
      notify();
    },

    replay() {
      shotIndex = 0;
      progress = 0;
      paused = false;
      notify();
    },

    subscribe(fn) {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
  };
}
