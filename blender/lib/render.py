"""Render-Voreinstellungen und Ausgabe. Blender 5.1, Eevee.

Zentral, damit alle vierzehn Shots garantiert denselben Look haben - eine
Stelle fuer Belichtung, Bloom, Korn und Vignette statt vierzehn.

Die hier gesetzten Werte sind teuer erkauft: Bloom-Defaults fluten das
Bild, der Glare-Node ist in 5.1 socket-basiert statt property-basiert, und
der Compositor haengt nicht mehr an use_nodes. Wer hier etwas aendert,
prueft es an einem Test-Still nach.
"""

from __future__ import annotations

import bpy

WIDTH, HEIGHT, FPS = 1920, 1080, 30

# Qualitaetsstufen. still = schnelle Sichtpruefung, final = Auslieferung.
PRESETS = {
    "still": {"samples": 16, "scale": 50, "volumetric": 32},
    "preview": {"samples": 24, "scale": 75, "volumetric": 48},
    "final": {"samples": 64, "scale": 100, "volumetric": 96},
}


def engine_name() -> str:
    """Eevee heisst in 5.1 wieder BLENDER_EEVEE - aber nicht ueberall gleich.

    Statt zu raten wird die Aufzaehlung gefragt. Ein falscher Name ist ein
    stiller Fehler: Blender rendert dann mit dem Standard weiter.
    """
    items = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
    for kandidat in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        if kandidat in items:
            return kandidat
    return items[0].identifier


def setup_scene(scene: bpy.types.Scene, quality: str = "still") -> None:
    preset = PRESETS[quality]

    scene.render.engine = engine_name()
    scene.render.resolution_x = WIDTH
    scene.render.resolution_y = HEIGHT
    scene.render.resolution_percentage = preset["scale"]
    scene.render.fps = FPS
    scene.render.film_transparent = False

    eevee = scene.eevee
    eevee.taa_render_samples = preset["samples"]
    eevee.use_shadows = True
    # Gegen "Shadow buffer full" - tritt bei vielen Lichtern sofort auf.
    if hasattr(eevee, "shadow_pool_size"):
        eevee.shadow_pool_size = "1024"
    if hasattr(eevee, "use_volumetric_shadows"):
        eevee.use_volumetric_shadows = True
    if hasattr(eevee, "volumetric_samples"):
        eevee.volumetric_samples = preset["volumetric"]
    if hasattr(eevee, "use_raytracing"):
        eevee.use_raytracing = True

    # Motion Blur nur im Endrender - im Still kostet es nur Zeit.
    scene.render.use_motion_blur = quality == "final"
    if quality == "final":
        scene.render.motion_blur_shutter = 0.5

    # Filmisch, nicht klinisch. Standard sorgt fuer ausgebrannte Himmel.
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    # Eine halbe Blende zurueck. AgX rollt Spitzlichter weich ab, aber wenn
    # das Eingangssignal zu hell ist, landet ALLES in der Schulter und das
    # Bild wird weiss - so sah der erste Testrender aus. Die Belichtung
    # steht hier zentral, damit alle vierzehn Shots gleich hell sind.
    # Nicht die absolute Helligkeit ist entscheidend, sondern das VERHAELTNIS
    # von Sonne zu Himmel. Bei Sonne 2,6 gegen Himmel 0,22 sah der
    # Junivormittag aus wie bedeckter Himmel: kaum Richtungslicht, flache
    # Fassaden. Die Sonne steht jetzt deutlich hoeher, und die Belichtung
    # nimmt den Gesamtpegel entsprechend zurueck.
    scene.view_settings.exposure = -2.1


def _menu_or_value(sock, wert):
    """Setzt einen Socket. Menue-Sockets werden schreibweise-unempfindlich
    gegen die gueltige Aufzaehlung abgeglichen.

    Grund: die Glare-Typen heissen in 5.1 'Bloom', 'Fog Glow', 'Simple Star' -
    in Klarschrift mit Leerzeichen, nicht als BLOOM-Konstanten. Wer aus
    Gewohnheit Grossbuchstaben schreibt, bekommt einen Enum-Fehler oder,
    schlimmer, einen stillen Rueckfall auf 'Streaks'.
    """
    if isinstance(wert, str):
        prop = sock.bl_rna.properties.get("default_value")
        erlaubt = [e.identifier for e in getattr(prop, "enum_items", [])]
        if erlaubt:
            for kandidat in erlaubt:
                if kandidat.lower() == wert.lower():
                    sock.default_value = kandidat
                    return kandidat
            return f"nicht gefunden, erlaubt: {erlaubt}"
    try:
        sock.default_value = wert
        return sock.default_value
    except (TypeError, ValueError) as err:
        return f"FEHLER: {err}"


def setup_compositor(scene: bpy.types.Scene, laut: bool = False) -> None:
    """Bloom und eine Spur Kontrast.

    AUFBAU, gemessen statt geraten. In Blender 5.1 haengt der Compositor an
    `scene.compositing_node_group`, und die Quelle des Bildes ist ein
    `CompositorNodeRLayers`-Knoten INNERHALB der Gruppe. Der Gruppeneingang
    wird NICHT vom Render gefuettert.

    Belegt an einer Minimalszene, mittlere Bildhelligkeit:
        ohne Compositor              0,3600
        RLayers -> GroupOutput       0,3600
        RLayers -> Glare -> Output   0,3600
        GroupInput -> Glare -> Out   0,0003   <- schwarz

    Der letzte Aufbau war der erste Versuch. Er wirft keinen Fehler, er
    rendert nur schwarz - deshalb hat es so lange gedauert, ihn zu finden.

    `CompositorNodeComposite` existiert in 5.1 nicht mehr; die Senke ist
    `NodeGroupOutput`.

    Vignette und Filmkorn bewusst NICHT hier: die macht die Web-Schicht im
    EffectComposer. Dort kostet eine Aenderung Sekunden, hier kostet sie
    einen kompletten Neurender.
    """
    tree = bpy.data.node_groups.new("Post", "CompositorNodeTree")
    tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    nodes, links = tree.nodes, tree.links
    nodes.clear()

    quelle = nodes.new("CompositorNodeRLayers")
    quelle.location = (-600, 0)

    glare = nodes.new("CompositorNodeGlare")
    glare.location = (-320, 0)

    # Der Standardtyp ist "Streaks" mit Threshold 1,0: das ergibt
    # Sternkreuze an jedem Spitzlicht und flutet das ganze Bild. Bloom mit
    # hoher Schwelle und schwacher Staerke - nur die echten Lichter glimmen.
    gesetzt = {}
    for name, wert in (
        ("Type", "Bloom"),
        ("Threshold", 10.0),
        ("Strength", 0.12),
        ("Size", 0.15),
        ("Quality", "High"),
    ):
        if name not in glare.inputs:
            continue
        gesetzt[name] = _menu_or_value(glare.inputs[name], wert)

    # Ein stiller Rueckfall auf Streaks waere schlimmer als ein Abbruch:
    # das Bild saehe falsch aus und niemand wuesste warum.
    if str(gesetzt.get("Type", "")).lower() != "bloom":
        print(f"  WARNUNG: Glare-Type ist '{gesetzt.get('Type')}', nicht Bloom - "
              f"das Bild bekommt Sternkreuze statt Bloom.")
    if laut:
        print(f"  Compositor: Glare {gesetzt}")

    kontrast = nodes.new("CompositorNodeBrightContrast")
    kontrast.location = (-80, 0)
    kontrast.inputs["Contrast"].default_value = 0.04

    ausgang = nodes.new("NodeGroupOutput")
    ausgang.location = (160, 0)

    links.new(quelle.outputs["Image"], glare.inputs[0])
    links.new(glare.outputs[0], kontrast.inputs[0])
    links.new(kontrast.outputs[0], ausgang.inputs[0])

    scene.compositing_node_group = tree


def write_still(scene: bpy.types.Scene, path: str) -> None:
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def write_video(scene: bpy.types.Scene, path: str) -> None:
    """Reihenfolge ist zwingend: erst media_type, dann file_format.

    Umgekehrt wirft Blender 5.1 einen Enum-Fehler, weil FFMPEG bei
    media_type=IMAGE nicht in der Aufzaehlung steht.
    """
    settings = scene.render.image_settings
    if hasattr(settings, "media_type"):
        settings.media_type = "VIDEO"
    settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.audio_codec = "NONE"

    # Der Pfad MUSS die Endung tragen. Ohne sie haengt Blender den
    # Bildbereich an und schreibt "shot_030001-0510.mp4" - die Praesentation
    # sucht aber "shot_03.mp4" und faellt still auf den Platzhalter zurueck.
    if not path.lower().endswith(".mp4"):
        path = f"{path}.mp4"
    scene.render.filepath = path
    bpy.ops.render.render(animation=True)
    return path
