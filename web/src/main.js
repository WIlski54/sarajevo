/**
 * Verdrahtung: Tastatur -> keymap -> presenter -> Stage und Overlays.
 * Enthaelt selbst keine Regeln, nur Verbindungen.
 */

import { BEATS } from "./beats.js";
import { createPresenter } from "./presenter.js";
import { actionForKey } from "./keymap.js";
import { createVideoStage } from "./stage/videoStage.js";
import {
  createBoard,
  createChapterBar,
  createClock,
  createOverview,
  createStatusLayers,
} from "./ui/overlays.js";

const el = (id) => document.getElementById(id);

const presenter = createPresenter(BEATS);

const stage = createVideoStage({
  video: el("videolayer"),
  placeholder: el("placeholder"),
});
const board = createBoard(el("board"));
const clock = createClock(el("clock"), BEATS);
const chapters = createChapterBar(el("chapters"), BEATS, (i) => presenter.goTo(i));
const overview = createOverview(el("overview"), BEATS, (i) => presenter.goTo(i));
const status = createStatusLayers({
  blackout: el("blackout"),
  pausebadge: el("pausebadge"),
});

/* ---------- Fortschritt des laufenden Shots ---------- */
/* Treibt die historische Uhr und den automatischen Shot-Wechsel.
   Bewusst mit setInterval statt requestAnimationFrame: in
   Hintergrund-Tabs pausiert rAF, und die Uhr braucht nur 10 Hz. */

let ticker = null;
let shotStartedAt = 0;
let shotDuration = 0;

function stopTicker() {
  clearInterval(ticker);
  ticker = null;
}

function startTicker(duration) {
  stopTicker();
  shotStartedAt = performance.now();
  shotDuration = Math.max(0.1, duration);
  ticker = setInterval(() => {
    if (presenter.state.paused) return;
    const elapsed = (performance.now() - shotStartedAt) / 1000;
    presenter.setProgress(elapsed / shotDuration);
    if (elapsed >= shotDuration) {
      stopTicker();
      // Naechster Shot im Beat. Ist der Beat zu Ende, bleibt das Bild
      // stehen - der Vortragende entscheidet, wann es weitergeht.
      if (presenter.advanceShot()) showCurrentShot();
    }
  }, 100);
}

async function showCurrentShot() {
  const beat = presenter.beat();
  const shot = presenter.shot();
  const result = await stage.show(beat, shot, {
    onEnded: () => {
      stopTicker();
      if (presenter.advanceShot()) showCurrentShot();
    },
  });
  startTicker(result.duration);
}

/* ---------- Zustand -> Darstellung ---------- */

let lastIndex = -1;
let lastPaused = false;

presenter.subscribe((state) => {
  // beatProgress, nicht progress: die Uhr laeuft ueber den ganzen Beat.
  // Mit dem shot-relativen Wert spraenge sie bei jedem Shot-Wechsel zurueck.
  clock.update(state.index, state.beatProgress);
  chapters.update(state.index);
  overview.update(state.overview, state.index);
  status.update(state);

  if (state.index !== lastIndex) {
    lastIndex = state.index;
    board.show(presenter.beat());
    if (state.started) showCurrentShot();
  }
  // Ein Shot-Wechsel braucht hier nichts: er wird ausschliesslich von
  // showCurrentShot ausgeloest, das das Video selbst schon gesetzt hat.

  // Nur bei echtem Wechsel schalten - setProgress feuert zehnmal pro
  // Sekunde, und play() im Dauerlauf waere reine Verschwendung.
  if (state.paused !== lastPaused) {
    lastPaused = state.paused;
    if (state.paused) stage.pause();
    else stage.resume();
  }
});

/* ---------- Tastatur ---------- */

const ACTIONS = {
  next: () => presenter.next(),
  prev: () => presenter.prev(),
  pause: () => presenter.togglePause(),
  replay: () => {
    presenter.replay();
    showCurrentShot();
  },
  blackout: () => presenter.toggleBlackout(),
  overview: () => presenter.toggleOverview(),
  // Die fuenf Vertiefungsmodule kommen in Phase P6. Bis dahin oeffnet V
  // die Kapiteluebersicht, damit die Taste nie ins Leere greift.
  deepDive: () => presenter.toggleOverview(),
  fullscreen: () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => {});
  },
};

window.addEventListener("keydown", (event) => {
  if (event.repeat) return;
  const action = actionForKey(event.key);
  if (!action) return;
  event.preventDefault();

  if (typeof action === "object") {
    presenter.goTo(action.index);
    return;
  }
  ACTIONS[action]?.();
});

el("stage").addEventListener("click", (event) => {
  // Klicks auf Bedienelemente nicht als Weiterblaettern deuten.
  if (event.target.closest("button")) return;
  if (!presenter.state.started) return;
  presenter.next();
});

/* ---------- Start ---------- */

el("startbutton").addEventListener("click", () => {
  el("startscreen").hidden = true;
  presenter.start();
  board.show(presenter.beat());
  showCurrentShot();
});

// Der erste Zustandsanstoss, damit Uhr und Kapitelleiste stimmen,
// bevor gestartet wird.
presenter.setProgress(0);
