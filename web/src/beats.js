/**
 * ALLE Inhalte der Praesentation als Daten - plus zwei kleine
 * Auswertungshelfer am Dateiende. Keine Zustandslogik, kein DOM.
 *
 * Texte sind gebunden an die verbindliche Faktenliste in
 * docs/superpowers/specs/2026-07-25-sarajevo-cinematic-design.md, Abschnitt 4.
 * Wer hier Texte aendert, braucht keine 3D-Kenntnisse.
 *
 * WENN DU HIER TEXTE AENDERST:
 *  1. Danach `npm test` laufen lassen. Ein vergessenes `+` am Zeilenende
 *     oder ein fehlendes Anfuehrungszeichen ist ein Syntaxfehler, der die
 *     GANZE Praesentation lahmlegt - der Test faengt das sofort.
 *  2. Aenderst du eine Uhrzeit, dann an ALLEN DREI Stellen des Beats:
 *     `clock`, die Zeitangabe am Anfang von `board.heading` und den
 *     gesprochenen Zeit-Satz am Anfang von `narration.text`. Die ersten
 *     beiden prueft ein Test, den dritten kann keiner pruefen.
 *  3. Unterhalb des BEATS-Arrays nichts anfassen.
 *
 * clock:     historische Uhrzeit, null wo das Zeitprotokoll keine nennt
 * shots:     Blender-Shots in Abspielreihenfolge. duration = Sekunden Video,
 *            die tatsaechlich gerendert werden muessen.
 * narration: Sprechertext plus `seconds` - die an der fertigen mp3
 *            GEMESSENE Dauer, kein Schaetzwert.
 * board:     Texttafel. Dient bei fehlender Videodatei auch als Rueckfall.
 * module:    interaktives three.js-Modul mit dem Zeitanteil, den es im
 *            Ablauf traegt. Modulzeit kostet keine Renderzeit - Beats mit
 *            Modul brauchen deshalb weniger Video.
 *
 * INVARIANTE: shots + module.seconds >= narration.seconds.
 * Sonst spricht die Stimme weiter, waehrend das Bild schon zu Ende ist.
 * Genau das war nach dem ersten Vertonen in sechs von acht Beats der Fall -
 * die urspruenglichen Dauern waren Schaetzungen aus einer Zeit, in der es
 * die Stimme noch nicht gab. Ein Test wacht jetzt darueber.
 */

export const BEATS = [
  {
    id: 0,
    clock: null,
    title: "Prolog: Vidovdan",
    shots: [{ file: "media/video/shot_00.mp4", duration: 37 }],
    narration: {
      file: "media/audio/vo_00.mp3",
      score: "media/audio/score_00.mp3",
      seconds: 33.8,
      voice: "narrator",
      instructions:
        "Ruhig, dokumentarisch, mit langen Pausen. Kein Pathos. Wie der Beginn " +
        "einer Geschichtsdokumentation, die weiss, wie sie ausgeht.",
      text:
        "Sonntag, der 28. Juni 1914. Über Sarajevo steht die Morgensonne. " +
        "Für die Verwaltung in Wien ist es ein Arbeitstag in einer unruhigen Provinz. " +
        "Für viele Serben ist es Vidovdan — der Tag, an dem sie an die Schlacht auf dem " +
        "Kosovo Polje erinnern, mehr als fünfhundert Jahre zuvor. " +
        "Sechs Jahre ist es her, dass Österreich-Ungarn Bosnien-Herzegowina annektiert hat. " +
        "Und an genau diesem Tag kommt der Thronfolger in die Stadt.",
    },
    board: {
      heading: "Sonntag, 28. Juni 1914",
      text:
        "Sarajevo ist die Hauptstadt von Bosnien-Herzegowina — einer Provinz, die " +
        "Österreich-Ungarn 1908 annektiert hatte. Der 28. Juni ist Vidovdan, ein " +
        "serbischer Nationalfeiertag zur Erinnerung an die Schlacht auf dem Kosovo " +
        "Polje von 1389. An diesem Tag besucht der österreichisch-ungarische " +
        "Thronfolger die Stadt.",
    },
    module: null,
  },

  {
    id: 1,
    clock: "09:25",
    title: "Ankunft am Bahnhof",
    shots: [
      { file: "media/video/shot_01.mp4", duration: 26 },
      { file: "media/video/shot_02.mp4", duration: 32 },
    ],
    narration: {
      file: "media/audio/vo_01.mp3",
      score: "media/audio/score_01.mp3",
      seconds: 55.4,
      voice: "narrator",
      instructions: "Sachlich erzaehlend, leicht waermer als der Prolog.",
      text:
        "Neun Uhr fünfundzwanzig. Der Zug hält im Bahnhof von Sarajevo. " +
        "Erzherzog Franz Ferdinand, Thronfolger von Österreich-Ungarn, ist zu einem " +
        "Truppenmanöver angereist. An seiner Seite seine Frau Sophie. " +
        "Dass sie neben ihm sitzen darf, ist keine Selbstverständlichkeit. " +
        "Am Wiener Hof gilt die Ehe als nicht standesgemäß: Sophie muss hinter den " +
        "Erzherzoginnen zurücktreten, ihre Kinder sind von der Thronfolge ausgeschlossen. " +
        "Hier aber tritt Franz Ferdinand als Generalinspektor der Streitkräfte auf — " +
        "und da darf sie an seiner Seite fahren. " +
        "Es ist der achtundzwanzigste Juni. Ihr vierzehnter Hochzeitstag. " +
        "Was das Paar nicht weiß: Die Fahrtroute stand seit Wochen in der Zeitung. " +
        "Und entlang dieser Route haben sich junge Männer verteilt, die den Thronfolger " +
        "töten wollen.",
    },
    board: {
      heading: "09:25 — Ankunft am Bahnhof",
      text:
        "Franz Ferdinand kommt zur Inspektion eines Truppenmanövers. Seine Frau " +
        "Sophie Chotek begleitet ihn — möglich, weil er hier als Generalinspektor " +
        "der Streitkräfte auftritt und nicht als Thronfolger bei Hofe. Der 28. Juni " +
        "ist zugleich ihr 14. Hochzeitstag. Die Fahrtroute war vorab öffentlich " +
        "bekannt; eine Gruppe von etwa sieben jungen Verschwörern der Mlada Bosna " +
        "hatte sich entlang der Strecke verteilt.",
    },
    module: null,
  },

  {
    id: 2,
    clock: "10:10",
    title: "Der erste Anschlag am Appelkai",
    shots: [
      { file: "media/video/shot_03.mp4", duration: 17 },
      { file: "media/video/shot_04.mp4", duration: 29 },
      { file: "media/video/shot_05.mp4", duration: 19 },
    ],
    narration: {
      file: "media/audio/vo_02.mp3",
      score: "media/audio/score_02.mp3",
      seconds: 62.2,
      voice: "narrator",
      instructions:
        "Zunehmend angespannt. Bei den zehn Sekunden knapper und schneller werden, " +
        "danach nach der Detonation deutlich zuruecknehmen, fast tonlos.",
      text:
        "Zehn Uhr zehn. Die Kolonne fährt über den Appelkai, die breite Uferstraße " +
        "an der Miljacka. Keine geschlossene Absperrung, wenige Polizisten, offene " +
        "Wagen mit zurückgeschlagenem Verdeck. " +
        "In der Menge steht Nedeljko Čabrinović. Er schlägt eine Handgranate gegen " +
        "einen Laternenpfahl, um den Zünder zu aktivieren. Von jetzt an bleiben ihm " +
        "zehn Sekunden. Er wirft. " +
        "Der Chauffeur Leopold Lojka sieht die Bewegung und gibt Gas. Die Granate " +
        "prallt vom zurückgeschlagenen Verdeck ab, fällt auf die Straße — und " +
        "detoniert unter dem nachfolgenden Wagen. " +
        "Etwa zwanzig Menschen werden verletzt. Der Thronfolger bleibt unversehrt. " +
        "Čabrinović schluckt Gift, das nicht wirkt, und springt in die Miljacka. " +
        "Der Fluss ist an dieser Stelle nur wenige Zentimeter tief. Man zieht ihn " +
        "heraus und nimmt ihn fest. " +
        "Der erste Anschlag ist gescheitert.",
    },
    board: {
      heading: "10:10 — Der erste Anschlag",
      text:
        "Nedeljko Čabrinović wirft eine Handgranate auf den Wagen des Thronfolgers. " +
        "Weil der Chauffeur beschleunigt, prallt sie ab und detoniert unter dem " +
        "nachfolgenden Fahrzeug. Etwa 20 Menschen werden verletzt, das Thronfolgerpaar " +
        "bleibt unverletzt. Čabrinovićs Selbstmordversuch scheitert: das Gift wirkt " +
        "nicht, und die Miljacka ist an dieser Stelle nur wenige Zentimeter tief.",
    },
    module: null,
  },

  {
    id: 3,
    clock: "10:15",
    title: "Empfang im Rathaus",
    shots: [
      { file: "media/video/shot_06.mp4", duration: 14 },
      { file: "media/video/shot_07.mp4", duration: 36 },
    ],
    narration: {
      file: "media/audio/vo_03.mp3",
      score: "media/audio/score_03.mp3",
      seconds: 47.4,
      voice: "narrator",
      instructions:
        "Sachlich, mit einem Hauch Ironie beim Buergermeister, der seine Rede " +
        "unveraendert vorliest. Beim letzten Satz bewusst langsamer.",
      text:
        "Zehn Uhr fünfzehn. Die Kolonne erreicht das Rathaus, die Vijećnica. " +
        "Bürgermeister Fehim Effendi Čurčić beginnt seine vorbereitete Begrüßungsrede. " +
        "Er hat den Text nicht geändert. " +
        "Franz Ferdinand ist empört: Er sei in freundschaftlicher Absicht gekommen " +
        "und werde mit Bomben empfangen. Dann fasst er sich und lässt ihn ausreden. " +
        "Das Programm wird fortgesetzt — aber verändert. Die geplante Fahrt durch die " +
        "engen, überfüllten Gassen der Altstadt wird aus Sicherheitsgründen gestrichen. " +
        "Stattdessen soll es über den breiten Appelkai direkt ins Krankenhaus gehen, " +
        "zu den Verletzten des ersten Anschlags. " +
        "Der Plan war da. Er war richtig. Er wurde nur nicht weitergegeben.",
    },
    board: {
      heading: "10:15 — Empfang im Rathaus",
      text:
        "Franz Ferdinand zeigt sich empört über den Anschlag, setzt das Programm aber " +
        "fort. Die geplante Weiterfahrt durch die überfüllte Altstadt wird aus " +
        "Sicherheitsgründen gestrichen: Die Kolonne soll über den breiten Appelkai " +
        "direkt ins Krankenhaus fahren, um die Verletzten zu besuchen. Diese Änderung " +
        "erreicht die Fahrer der vorderen Wagen nicht.",
    },
    module: null,
  },

  {
    id: 4,
    clock: "10:45",
    title: "Die fatale Routenänderung",
    shots: [
      { file: "media/video/shot_08.mp4", duration: 12 },
      { file: "media/video/shot_09.mp4", duration: 16 },
    ],
    narration: {
      file: "media/audio/vo_04.mp3",
      score: "media/audio/score_04.mp3",
      seconds: 33.9,
      voice: "narrator",
      instructions:
        "Nuechtern, praezise, wie ein Untersuchungsbericht. Die Nuechternheit " +
        "erzeugt hier die Spannung.",
      text:
        "Zehn Uhr fünfundvierzig. Die Kolonne fährt ab. " +
        "Doch die Fahrer der vorderen Wagen wissen nichts von der Änderung. Sie fahren " +
        "die Route, die sie gelernt haben — und biegen rechts in die Franz-Joseph-Straße " +
        "ein, genau in die Altstadt, die man vermeiden wollte. " +
        "Erst jetzt fällt der Irrtum auf. Man ruft dem Chauffeur zu, er sei falsch " +
        "abgebogen. Der Wagen hält an. Er muss zurücksetzen. " +
        "Und dabei kommt er zum Stehen.",
    },
    board: {
      heading: "10:45 — Die falsche Abzweigung",
      text:
        "Die Fahrer der ersten Wagen wurden nicht über die geänderte Route informiert " +
        "und biegen in die ursprünglich geplante Franz-Joseph-Straße ein. Als der " +
        "Irrtum bemerkt wird, müssen die Fahrzeuge anhalten und zurücksetzen.",
    },
    module: { name: "routeMap", seconds: 12 },
  },

  {
    id: 5,
    clock: "10:48",
    title: "Die tödlichen Schüsse",
    shots: [
      { file: "media/video/shot_10.mp4", duration: 18 },
      { file: "media/video/shot_11.mp4", duration: 28 },
    ],
    narration: {
      file: "media/audio/vo_05.mp3",
      score: "media/audio/score_05.mp3",
      seconds: 43.3,
      voice: "narrator",
      instructions:
        "Sehr leise, sehr langsam, lange Pausen. Nach den Schuessen fast fluesternd. " +
        "Keine Dramatisierung - die Zurueckhaltung traegt die Wirkung.",
      text:
        "Zehn Uhr achtundvierzig. Der Wagen steht. Vor dem Delikatessenladen von " +
        "Moritz Schiller. " +
        "Wenige Schritte entfernt steht Gavrilo Princip. Neunzehn Jahre alt. Er hatte " +
        "den Anschlag am Morgen für gescheitert gehalten und war stehen geblieben. " +
        "Jetzt steht der Wagen genau vor ihm. " +
        "Er tritt heran und gibt zwei Schüsse ab. " +
        "Franz Ferdinand wird am Hals getroffen, Sophie am Unterleib. " +
        "Etwa eine halbe Stunde später sterben beide im Konak, der Residenz des " +
        "Statthalters.",
      // Nach dem Erzaehltext wird board.quote mit der Zitatstimme gesprochen
      // (Phase P1). Der Text steht bewusst nur einmal, in board.quote.
      quoteFile: "media/audio/vo_05_zitat.mp3",
      quoteAfter: true,
    },
    board: {
      heading: "10:48 — Die Schüsse",
      text:
        "Der Wagen kommt vor dem Delikatessenladen von Moritz Schiller zum Stehen. " +
        "Gavrilo Princip, 19 Jahre alt, steht wenige Schritte entfernt, tritt an das " +
        "offene Auto heran und gibt zwei Schüsse ab. Franz Ferdinand wird am Hals " +
        "getroffen, Sophie schwer am Unterleib verletzt. Beide sterben etwa eine halbe " +
        "Stunde später im Konak, der Residenz des Statthalters.",
      quote: "Sopherl, Sopherl, stirb nicht! Bleibe am Leben für unsere Kinder!",
      source: "Überliefert von Graf Franz von Harrach, der auf dem Trittbrett stand",
    },
    module: null,
  },

  {
    id: 6,
    clock: null,
    title: "Epilog: Der Funke",
    shots: [{ file: "media/video/shot_12.mp4", duration: 20 }],
    narration: {
      file: "media/audio/vo_06.mp3",
      score: "media/audio/score_06.mp3",
      seconds: 43.7,
      voice: "narrator",
      instructions:
        "Aufziehend, weiter werdend. Die Datumsangaben klar und getaktet, wie " +
        "fallende Dominosteine.",
      text:
        "Zwei Schüsse in einer Seitenstraße. Und dann geht alles sehr schnell. " +
        "Am 23. Juli stellt Österreich-Ungarn ein Ultimatum an Serbien, das kaum " +
        "erfüllbar ist. Am 28. Juli erklärt es Serbien den Krieg. " +
        "Russland mobilisiert, weil es Serbien stützt. Deutschland erklärt Russland " +
        "am 1. August den Krieg, Frankreich am 3. August. Als deutsche Truppen in " +
        "das neutrale Belgien einmarschieren, tritt am 4. August Großbritannien in " +
        "den Krieg ein. " +
        "Siebenunddreißig Tage nach den Schüssen von Sarajevo steht Europa im Krieg. " +
        "Es wird vier Jahre dauern und Millionen Menschen das Leben kosten.",
    },
    board: {
      heading: "Die Julikrise — 37 Tage",
      text:
        "23. Juli: Ultimatum Österreich-Ungarns an Serbien. 28. Juli: Kriegserklärung " +
        "an Serbien. 30. Juli: russische Mobilmachung. 1. August: Deutschland erklärt " +
        "Russland den Krieg, 3. August Frankreich. 4. August: Großbritannien tritt in " +
        "den Krieg ein, nachdem deutsche Truppen in das neutrale Belgien einmarschiert " +
        "sind. Aus einem Attentat wird ein Weltkrieg.",
    },
    module: { name: "europeFuse", seconds: 27 },
  },

  {
    id: 7,
    clock: null,
    title: "Anlass oder Ursache?",
    shots: [{ file: "media/video/shot_13.mp4", duration: 14 }],
    narration: {
      file: "media/audio/vo_07.mp3",
      score: "media/audio/score_07.mp3",
      seconds: 47.2,
      voice: "narrator",
      instructions:
        "Offen, fragend, an die Klasse gerichtet. Am Ende nicht abschliessend " +
        "klingen - die Frage soll stehen bleiben.",
      text:
        "An diesem Vormittag ging sehr viel schief. Das Datum war ausgerechnet " +
        "Vidovdan. Die Route stand in der Zeitung. Es gab kaum Absperrungen. " +
        "Die Granate prallte ab. Die geänderte Route wurde nicht weitergegeben. " +
        "Und Princip stand genau an der Stelle, an der der Wagen zum Stehen kam. " +
        "Nimm einen dieser Zufälle weg, und der 28. Juni 1914 wäre ein Tag wie " +
        "jeder andere geblieben. " +
        "Aber: Die Bündnisse bestanden schon. Das Wettrüsten lief schon. Die " +
        "Interessengegensätze in Südosteuropa bestanden schon. " +
        "Das Attentat war der Anlass des Krieges. War es auch seine Ursache?",
    },
    board: {
      heading: "Anlass oder Ursache?",
      text:
        "Die Kette der Zufälle: Datum Vidovdan · Route vorab veröffentlicht · kaum " +
        "Absperrung · Granate prallt ab · Routenänderung nicht weitergegeben · Princip " +
        "steht genau dort. Daneben die strukturellen Ursachen, die unabhängig von " +
        "diesem Tag bestanden: Imperialismus, Bündnissysteme, Wettrüsten, " +
        "Nationalismus, Interessengegensätze in Südosteuropa. Das Attentat war der " +
        "Anlass. War es die Ursache?",
    },
    module: { name: "dominoes", seconds: 36 },
  },
];

/** Summe aller Shot-Dauern in Sekunden. */
export function totalShotSeconds() {
  return BEATS.reduce(
    (sum, beat) => sum + beat.shots.reduce((s, shot) => s + shot.duration, 0),
    0,
  );
}

/** Uhrzeit des naechsten Beats, der eine nennt - fuer die Uhr-Interpolation. */
export function nextClockAfter(index) {
  for (let i = index + 1; i < BEATS.length; i++) {
    if (BEATS[i].clock !== null) return BEATS[i].clock;
  }
  return null;
}
