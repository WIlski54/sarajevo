/**
 * Video-Stage mit Rueckfall auf die Texttafel.
 *
 * Ein Mechanismus, zwei Zwecke:
 *  - In Phase P0 existiert noch keine Videodatei, also zeigt jeder Beat
 *    seinen Platzhalter. Der Ablauf und das Timing sind trotzdem pruefbar.
 *  - Im Betrieb ist derselbe Pfad der von Spec Abschnitt 11 geforderte
 *    Rueckfall: eine fehlende Datei darf die Praesentation nie anhalten.
 *
 * chooseSource und describePlaceholder sind DOM-frei und damit testbar;
 * nur createVideoStage beruehrt das DOM.
 */

/** Prueft per HEAD, ob eine Datei ausgeliefert wird. */
export async function probeFile(file) {
  const response = await fetch(file, { method: "HEAD" });
  return response.ok;
}

/**
 * Entscheidet zwischen Video und Platzhalter.
 * @param {{file: string}} shot
 * @param {(file: string) => Promise<boolean>} probe
 */
export async function chooseSource(shot, probe = probeFile) {
  try {
    const ok = await probe(shot.file);
    return { kind: ok ? "video" : "placeholder", file: shot.file };
  } catch {
    // Netzfehler wie fehlende Datei behandeln - die Praesentation laeuft weiter.
    return { kind: "placeholder", file: shot.file };
  }
}

/** Beschreibungstexte des Platzhalters. */
export function describePlaceholder(beat, shot) {
  return {
    beatLabel: beat.clock ? `Beat ${beat.id} · ${beat.clock}` : `Beat ${beat.id}`,
    title: beat.title,
    file: shot.file,
  };
}

/**
 * @param {{video: HTMLElement, placeholder: HTMLElement}} elements
 */
export function createVideoStage(elements, probe = probeFile) {
  const { video: videoLayer, placeholder } = elements;
  let current = null;

  const clear = () => {
    if (current) {
      current.pause();
      current.removeAttribute("src");
      current.load();
      current.remove();
      current = null;
    }
    videoLayer.hidden = true;
    placeholder.hidden = true;
  };

  const showPlaceholder = (beat, shot) => {
    const info = describePlaceholder(beat, shot);
    placeholder.replaceChildren();

    const label = document.createElement("p");
    label.className = "placeholder__beat";
    label.textContent = info.beatLabel;

    const title = document.createElement("h2");
    title.className = "placeholder__title";
    title.textContent = info.title;

    const file = document.createElement("p");
    file.className = "placeholder__file";
    file.textContent = `${info.file} — noch nicht gerendert`;

    placeholder.append(label, title, file);
    placeholder.hidden = false;
  };

  return {
    /**
     * Zeigt den Shot. Liefert die Dauer in Sekunden, mit der der
     * Vortragsablauf weiterrechnet.
     * @returns {Promise<{kind: string, duration: number}>}
     */
    async show(beat, shot, { onEnded } = {}) {
      clear();
      const source = await chooseSource(shot, probe);

      if (source.kind === "placeholder") {
        showPlaceholder(beat, shot);
        return { kind: "placeholder", duration: shot.duration };
      }

      const element = document.createElement("video");
      element.src = source.file;
      element.preload = "auto";
      element.playsInline = true;
      // Ton kommt in Phase P1 aus der Web-Audio-Schicht, nicht aus dem Video.
      element.muted = true;
      if (onEnded) element.addEventListener("ended", onEnded, { once: true });
      videoLayer.replaceChildren(element);
      videoLayer.hidden = false;
      current = element;
      await element.play().catch(() => {
        // Autoplay verweigert: Standbild statt Absturz.
      });
      return { kind: "video", duration: shot.duration };
    },

    pause() {
      current?.pause();
    },

    resume() {
      current?.play().catch(() => {});
    },

    dispose: clear,
  };
}
