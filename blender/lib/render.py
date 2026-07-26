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


def setup_compositor(scene: bpy.types.Scene) -> None:
    """Bloom, Korn und Vignette.

    In 5.1 haengt der Compositor an scene.compositing_node_group; use_nodes
    ist deprecated. Der Glare-Node ist vollstaendig socket-basiert - der
    Typ wird ueber inputs["Type"] gesetzt, nicht ueber ein Property.
    """
    tree = bpy.data.node_groups.new("Post", "CompositorNodeTree")
    scene.compositing_node_group = tree

    nodes, links = tree.nodes, tree.links
    nodes.clear()

    render = nodes.new("NodeGroupInput")
    render.location = (-600, 0)
    if not tree.interface.items_tree:
        tree.interface.new_socket("Image", in_out="INPUT", socket_type="NodeSocketColor")
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    glare = nodes.new("CompositorNodeGlare")
    glare.location = (-350, 0)
    # Defaults sind 'Streaks' mit niedriger Schwelle: das ergibt
    # Sternkreuze und flutet das ganze Bild. Bloom mit hoher Schwelle.
    for name, value in (
        ("Type", "BLOOM"),
        ("Threshold", 10.0),
        ("Strength", 0.12),
        ("Size", 0.15),
    ):
        if name in glare.inputs:
            try:
                glare.inputs[name].default_value = value
            except (TypeError, ValueError):
                pass

    grain = nodes.new("CompositorNodeBrightContrast")
    grain.location = (-120, 0)
    grain.inputs["Contrast"].default_value = 0.04

    out = nodes.new("NodeGroupOutput")
    out.location = (150, 0)

    links.new(render.outputs[0], glare.inputs[0])
    links.new(glare.outputs[0], grain.inputs[0])
    links.new(grain.outputs[0], out.inputs[0])


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
    scene.render.filepath = path
    bpy.ops.render.render(animation=True)
