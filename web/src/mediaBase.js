/**
 * Wandelt einen Medienpfad aus beats.js in eine URL, die der Browser findet.
 *
 * Die Pfade in beats.js sind relativ zur PROJEKTWURZEL ("media/video/..."),
 * weil sie auch von Werkzeugen im Dateisystem benutzt werden
 * (tools/check_media.js, audio/narration.py, audio/score.py).
 *
 * Die Seite liegt aber unter /web/index.html. Ein relativer Pfad loest
 * daher gegen /web/ auf und landet bei /web/media/... - genau dort liegt
 * nichts. Das fiel lange nicht auf, weil die Videos ohnehin noch fehlten
 * und der Platzhalter-Rueckfall greift: es sah richtig aus, war es aber
 * nicht. Ab Phase P2 waere kein einziger gerenderter Shot gefunden worden.
 *
 * `../` ist dokumentrelativ und bleibt richtig, auch wenn das Projekt
 * einmal unter einem Unterpfad ausgeliefert wird.
 */
export function mediaUrl(file) {
  return `../${file}`;
}
