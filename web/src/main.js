/**
 * Verdrahtung: Tastatur -> keymap -> presenter -> Stage und Overlays.
 * Enthaelt selbst keine Regeln, nur Verbindungen.
 */

import { BEATS } from "./beats.js";
import { createPresenter } from "./presenter.js";
import { actionForKey } from "./keymap.js";
import { createVideoStage } from "./stage/videoStage.js";
import { createAudioEngine } from "./audio/engine.js";
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
const audio = createAudioEngine();
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
    if (state.started) {
      showCurrentShot();
      // Ton haengt am Beat, nicht am Shot: die Erzaehlung laeuft ueber
      // alle Shots eines Beats hinweg durch.
      audio.playBeat(presenter.beat());
    }
  }
  // Ein Shot-Wechsel braucht hier nichts: er wird ausschliesslich von
  // showCurrentShot ausgeloest, das das Video selbst schon gesetzt hat.

  // Nur bei echtem Wechsel schalten - setProgress feuert zehnmal pro
  // Sekunde, und play() im Dauerlauf waere reine Verschwendung.
  if (state.paused !== lastPaused) {
    lastPaused = state.paused;
    if (state.paused) {
      stage.pause();
      audio.pause();
    } else {
      stage.resume();
      audio.resume();
    }
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
    audio.playBeat(presenter.beat());
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

  // VOR dem Start reagiert nur der Start selbst.
  //
  // Ohne diese Sperre war die Praesentation nicht bedienbar: `Esc` oder `V`
  // oeffneten die Kapiteluebersicht, die im DOM nach dem Startbildschirm
  // liegt und ihn deshalb verdeckt. Der Startknopf war damit unerreichbar,
  // und weil er nie geklickt wurde, blieb auch der AudioContext gesperrt -
  // kein Bild UND kein Ton, obwohl beides fertig war. Genau dieser Zustand
  // ist einem Nutzer passiert.
  if (!presenter.state.started) {
    if ([" ", "Enter", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      starten();
    }
    return;
  }

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
  // Ein Klick ins Bild startet, wenn noch nicht gestartet wurde - der
  // Vortragende soll nie in einen Zustand geraten, in dem nichts reagiert.
  if (!presenter.state.started) {
    starten();
    return;
  }
  presenter.next();
});

/* ---------- Rueckkehr aus dem Hintergrund ---------- */

// Chrome pausiert stummes Video in unsichtbaren Tabs, um Strom zu sparen:
//   AbortError: video-only background media was paused to save power
// Ohne diesen Handler bleibt das Bild stehen, sobald der Vortragende einmal
// das Fenster wechselt - und kommt nicht von selbst zurueck. Der Ton laeuft
// weiter (er hat eine Tonspur und ist davon nicht betroffen), Bild und Ton
// wuerden also auseinanderlaufen.
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState !== "visible") return;
  if (!presenter.state.started) return;
  // Eine bewusst gesetzte Pause bleibt eine Pause.
  if (presenter.state.paused) return;
  stage.resume();
  audio.resume();
});

/* ---------- Start ---------- */

/**
 * Startet die Praesentation. Erreichbar ueber den Knopf, die Leertaste,
 * Enter, Pfeil rechts und einen Klick ins Bild - absichtlich mehrfach, damit
 * niemand vor einer Klasse nach dem richtigen Weg suchen muss.
 *
 * Genau hier - und nur hier - darf der AudioContext entstehen: Browser geben
 * Ton erst nach einer Nutzerinteraktion frei. Das ist der eigentliche Zweck
 * des Startbildschirms.
 */
function starten() {
  if (presenter.state.started) return;
  audio.unlock();
  el("startscreen").hidden = true;
  presenter.start();
  board.show(presenter.beat());
  showCurrentShot();
  audio.playBeat(presenter.beat());
}

el("startbutton").addEventListener("click", starten);

// Der erste Zustandsanstoss, damit Uhr und Kapitelleiste stimmen,
// bevor gestartet wird.
presenter.setProgress(0);

// Lesbarer Zustand fuer die Verifikation. Die Tonspuren haengen absichtlich
// nicht im DOM (new Audio() erzeugt lose Elemente), und der Browser-Pane
// dieser Entwicklungsumgebung liefert keine Screenshots - ohne diesen Haken
// laesst sich nicht pruefen, ob wirklich Ton laeuft. Nur lesen, kein Steuern.
window.__zustand = () => ({
  beat: presenter.state.index,
  shot: presenter.state.shotIndex,
  pausiert: presenter.state.paused,
  uhr: el("clock").textContent,
  bild: stage.debug(),
  ton: audio.debug(),
});
