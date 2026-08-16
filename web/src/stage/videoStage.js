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

import { mediaUrl } from "../mediaBase.js";

/**
 * Kleinste Groesse, ab der eine Videodatei als brauchbar gilt.
 * Ein abgebrochener Render hinterlaesst eine 0-Byte- oder Rumpfdatei;
 * ein echter Shot liegt bei mehreren Megabyte.
 */
const MINDESTGROESSE = 64 * 1024;

/**
 * Prueft per HEAD, ob eine Datei ausgeliefert wird UND Inhalt hat.
 *
 * Die Groessenpruefung ist nicht ueberfluessig: ein abgebrochener Blender-
 * Render hinterlaesst eine 0-Byte-Datei, und die liefert brav HTTP 200.
 * Ohne diese Pruefung haelt die Praesentation sie fuer ein gueltiges Video,
 * zeigt schwarz und faellt NICHT auf die Texttafel zurueck - der Rueckfall,
 * der als Sicherheitsnetz gedacht ist, wuerde den Fehler also verdecken.
 * Genau so eine Datei ist beim Abbruch eines Hintergrundrenders entstanden.
 */
export async function probeFile(file) {
  const response = await fetch(mediaUrl(file), { method: "HEAD" });
  if (!response.ok) return false;
  const groesse = Number(response.headers.get("content-length"));
  // Fehlt der Header, wird die Datei akzeptiert - lieber ein Versuch als
  // ein falscher Rueckfall.
  if (!Number.isFinite(groesse) || groesse === 0) {
    return response.headers.get("content-length") === null;
  }
  return groesse >= MINDESTGROESSE;
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
  // Grund des letzten fehlgeschlagenen play(). Ein verschluckter Fehler ist
  // hier fatal: "das Video laeuft nicht" ohne Ursache ist nicht
  // diagnostizierbar, und der Platzhalter-Rueckfall laesst es harmlos
  // aussehen. Wird ueber debug() lesbar gemacht.
  let letzterFehler = null;

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
      element.src = mediaUrl(source.file);
      element.preload = "auto";
      element.playsInline = true;
      // Ton kommt in Phase P1 aus der Web-Audio-Schicht, nicht aus dem Video.
      element.muted = true;
      if (onEnded) element.addEventListener("ended", onEnded, { once: true });
      videoLayer.replaceChildren(element);
      videoLayer.hidden = false;
      current = element;
      letzterFehler = null;
      try {
        await element.play();
      } catch (err) {
        // Autoplay verweigert oder Tab im Hintergrund: Standbild statt
        // Absturz - aber der Grund wird festgehalten, nicht verschluckt.
        letzterFehler = `${err.name}: ${err.message}`;
      }
      return { kind: "video", duration: shot.duration };
    },

    pause() {
      current?.pause();
    },

    resume() {
      current?.play().catch((err) => {
        letzterFehler = `${err.name}: ${err.message}`;
      });
    },

    /** Lesbarer Zustand fuer die Verifikation. Reine Auskunft. */
    debug() {
      return {
        quelle: current ? current.src.split("/").pop() : null,
        laeuft: current ? !current.paused : null,
        position: current ? Number(current.currentTime.toFixed(2)) : null,
        bereit: current ? current.readyState : null,
        netz: current ? current.networkState : null,
        mediaFehler: current?.error ? current.error.code : null,
        playFehler: letzterFehler,
      };
    },

    dispose: clear,
  };
}
