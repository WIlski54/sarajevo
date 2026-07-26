/**
 * Tonwiedergabe der Praesentation.
 *
 * Vier Busse - Stimme, Score, Geraeusche, Atmosphaere - auf einen Master.
 * Der Score duckt sich unter die Sprecherstimme, damit der Text immer
 * verstaendlich bleibt. Pause haelt Bild und Ton im selben Moment an.
 *
 * Zwei Regeln, die den Aufbau bestimmen:
 *
 *  1. Fehlender Ton darf die Praesentation NIE anhalten. Jede Datei, die
 *     nicht laedt, wird still uebersprungen - vor einer Klasse ist eine
 *     stumme Stelle aergerlich, ein Absturz eine Katastrophe.
 *  2. Der AudioContext entsteht erst beim Klick auf "Praesentation
 *     starten". Browser verweigern Ton vor einer Nutzerinteraktion; das
 *     ist der Grund fuer den Startbildschirm.
 */

import { mediaUrl } from "../mediaBase.js";

/** Pegel der Busse zueinander. Score bewusst leise - er traegt, er erzaehlt nicht. */
const BUS_GAIN = {
  voice: 1.0,
  score: 0.5,
  sfx: 0.8,
  ambience: 0.6,
};

/** Wie weit sich der Score unter die Stimme duckt (Faktor, nicht dB). */
const DUCK = 0.4;
const DUCK_TIME = 0.45;

/**
 * Welche Tonspuren ein Beat mitbringt. Rein, ohne DOM - damit testbar.
 * @returns {{bus: string, file: string, after?: string}[]}
 */
export function tracksForBeat(beat) {
  const tracks = [];
  if (beat.narration?.score) {
    tracks.push({ bus: "score", file: beat.narration.score });
  }
  if (beat.narration?.file) {
    tracks.push({ bus: "voice", file: beat.narration.file });
  }
  if (beat.narration?.quoteAfter && beat.narration?.quoteFile) {
    // Das Zitat folgt der Erzaehlung, es ueberlagert sie nicht.
    tracks.push({ bus: "voice", file: beat.narration.quoteFile, after: "voice" });
  }
  return tracks;
}

export function createAudioEngine() {
  let ctx = null;
  let master = null;
  const buses = {};
  let playing = [];
  let muted = false;

  const build = () => {
    if (ctx) return;
    const Ctor = window.AudioContext || window.webkitAudioContext;
    if (!Ctor) return; // Kein Web Audio: die Praesentation laeuft stumm weiter.
    ctx = new Ctor();
    master = ctx.createGain();
    master.gain.value = 0.9;
    master.connect(ctx.destination);
    for (const [name, gain] of Object.entries(BUS_GAIN)) {
      const node = ctx.createGain();
      node.gain.value = gain;
      node.connect(master);
      buses[name] = node;
    }
  };

  const duck = (on) => {
    if (!ctx || !buses.score) return;
    const ziel = BUS_GAIN.score * (on ? DUCK : 1);
    buses.score.gain.cancelScheduledValues(ctx.currentTime);
    buses.score.gain.setTargetAtTime(ziel, ctx.currentTime, DUCK_TIME);
  };

  /** Haengt ein <audio> an einen Bus. Liefert null, wenn Ton nicht geht. */
  const attach = (file, bus) => {
    if (!ctx) return null;
    const el = new Audio(mediaUrl(file));
    el.preload = "auto";
    el.crossOrigin = "anonymous";
    try {
      const src = ctx.createMediaElementSource(el);
      src.connect(buses[bus] ?? master);
    } catch {
      return null;
    }
    return el;
  };

  const stopAll = () => {
    for (const el of playing) {
      el.pause();
      el.removeAttribute("src");
      el.load();
    }
    playing = [];
    duck(false);
  };

  return {
    /** Beim Klick auf "Praesentation starten" aufrufen. */
    unlock() {
      build();
      ctx?.resume?.();
      return Boolean(ctx);
    },

    get available() {
      return Boolean(ctx);
    },

    /**
     * Spielt alle Spuren eines Beats. Fehlende Dateien werden still
     * uebersprungen - die Praesentation laeuft weiter.
     */
    playBeat(beat) {
      stopAll();
      if (!ctx) return;

      const tracks = tracksForBeat(beat);
      let voiceEl = null;
      let nachspann = null;

      for (const track of tracks) {
        const el = attach(track.file, track.bus);
        if (!el) continue;

        // Eine fehlende Datei ist hier der Normalfall, solange Phase P2
        // und P3 laufen. Kein Fehler, kein Abbruch, kein Konsolenrauschen.
        el.addEventListener("error", () => {
          if (track.bus === "voice" && !track.after) duck(false);
        });

        if (track.after) {
          nachspann = el;
          continue;
        }

        playing.push(el);
        el.muted = muted;
        el.play().catch(() => {});

        if (track.bus === "voice") {
          voiceEl = el;
          duck(true);
        }
      }

      if (voiceEl) {
        voiceEl.addEventListener("ended", () => {
          if (nachspann) {
            playing.push(nachspann);
            nachspann.muted = muted;
            nachspann.play().catch(() => {});
            nachspann.addEventListener("ended", () => duck(false), { once: true });
          } else {
            duck(false);
          }
        }, { once: true });
      }
    },

    pause() {
      for (const el of playing) el.pause();
      ctx?.suspend?.();
    },

    resume() {
      ctx?.resume?.();
      for (const el of playing) el.play().catch(() => {});
    },

    setMuted(value) {
      muted = Boolean(value);
      for (const el of playing) el.muted = muted;
    },

    get muted() {
      return muted;
    },

    stopAll,

    /**
     * Lesbarer Zustand fuer die Verifikation. Die Spuren haengen nicht im
     * DOM, also gibt es sonst keine Moeglichkeit zu pruefen, ob wirklich
     * Ton laeuft. Reine Auskunft, keine Steuerung.
     */
    debug() {
      return {
        kontext: ctx ? ctx.state : "nicht gebaut",
        scorePegel: buses.score ? Number(buses.score.gain.value.toFixed(3)) : null,
        spuren: playing.map((el) => ({
          datei: el.src.split("/").pop(),
          laeuft: !el.paused,
          position: Number(el.currentTime.toFixed(1)),
          dauer: Number.isFinite(el.duration) ? Number(el.duration.toFixed(1)) : null,
          fehler: el.error ? el.error.code : null,
        })),
      };
    },
  };
}
