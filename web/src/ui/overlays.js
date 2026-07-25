/**
 * DOM-Schicht. Liest Zustand, schreibt nie hinein.
 * Jede Funktion nimmt ihre Elemente entgegen - kein globales Suchen.
 */

import { interpolateClock } from "../clock.js";
import { nextClockAfter } from "../beats.js";

/** Texttafel eines Beats. */
export function createBoard(element) {
  return {
    show(beat) {
      element.replaceChildren();

      const heading = document.createElement("h2");
      heading.className = "board__heading";
      heading.textContent = beat.board.heading;

      const text = document.createElement("p");
      text.className = "board__text";
      text.textContent = beat.board.text;

      element.append(heading, text);

      if (beat.board.quote) {
        const quote = document.createElement("blockquote");
        quote.className = "board__quote";
        quote.textContent = `„${beat.board.quote}"`;

        const source = document.createElement("cite");
        source.className = "board__source";
        source.textContent = beat.board.source;

        quote.append(source);
        element.append(quote);
      }

      element.hidden = false;
      // Reflow erzwingen, damit der Browser den Startzustand uebernimmt und
      // die Transition wirklich laeuft. Bewusst NICHT requestAnimationFrame:
      // in Hintergrund-Tabs feuert rAF nicht, und die Texttafel ist der
      // Inhalt - sie darf nie an der Sichtbarkeit des Tabs haengen.
      void element.offsetWidth;
      element.classList.add("is-visible");
    },

    hide() {
      element.classList.remove("is-visible");
      element.hidden = true;
    },
  };
}

/** Historische Uhr. */
export function createClock(element, beats) {
  const label = document.createElement("span");
  label.className = "clock__label";
  label.textContent = "28. Juni 1914";
  const time = document.createElement("span");
  element.replaceChildren(label, time);

  return {
    update(index, progress) {
      const beat = beats[index];
      if (!beat.clock) {
        element.hidden = true;
        return;
      }
      time.textContent = interpolateClock(beat.clock, nextClockAfter(index), progress);
      element.hidden = false;
    },
  };
}

/** Kapitelleiste am unteren Rand, erscheint nur bei Mausbewegung. */
export function createChapterBar(element, beats, onSelect) {
  const buttons = beats.map((beat, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chapters__item";

    const time = document.createElement("span");
    time.className = "chapters__time";
    time.textContent = beat.clock ?? "—";

    const title = document.createElement("span");
    title.textContent = beat.title;

    button.append(time, title);
    button.addEventListener("click", () => onSelect(index));
    return button;
  });

  element.replaceChildren(...buttons);
  element.hidden = false;

  let timer = null;
  const reveal = () => {
    element.classList.add("is-visible");
    clearTimeout(timer);
    timer = setTimeout(() => element.classList.remove("is-visible"), 2600);
  };
  window.addEventListener("mousemove", reveal, { passive: true });

  return {
    update(index) {
      buttons.forEach((button, i) => {
        button.classList.toggle("is-current", i === index);
      });
    },
  };
}

/** Kapiteluebersicht, aufgerufen mit Esc. */
export function createOverview(element, beats, onSelect) {
  const heading = document.createElement("h2");
  heading.className = "overview__heading";
  heading.textContent = "Kapitel";

  const buttons = beats.map((beat, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "overview__item";

    const time = document.createElement("span");
    time.className = "overview__time";
    time.textContent = beat.clock ?? "—";

    const title = document.createElement("span");
    title.textContent = beat.title;

    button.append(time, title);
    button.addEventListener("click", () => onSelect(index));
    return button;
  });

  element.replaceChildren(heading, ...buttons);

  return {
    update(open, index) {
      element.hidden = !open;
      buttons.forEach((button, i) => {
        button.classList.toggle("is-current", i === index);
      });
    },
  };
}

/** Schwarzbild und Pause-Marke. */
export function createStatusLayers({ blackout, pausebadge }) {
  return {
    update(state) {
      blackout.hidden = false;
      blackout.classList.toggle("is-visible", state.blackout);
      pausebadge.hidden = !state.paused;
    },
  };
}
