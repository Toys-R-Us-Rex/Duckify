from pathlib import Path

from tracing.color import Color
from tracing.config import TracerConfig
from tracing.tracer import Tracer

PROJECT_DIR = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUT_DIR = PROJECT_DIR / "output"


def main():
    texture_path: Path = ASSETS_DIR / "textures" / "clown_triste.png"
    model_path: Path = ASSETS_DIR / "models" / "duck_uv_v2.obj"
    mask_path: Path = ASSETS_DIR / "textures/masks" / "drawable_mask_v2.png"
    texture_name: str = texture_path.stem
    model_name: str = model_path.stem
    output_path: Path = OUTPUT_DIR / f"{model_name}-{texture_name}-trace.json"
    palette: tuple[Color, ...] = ((217, 213, 102), (10, 122, 40), (0,0,255),(255,255,255),(10,10,10),(255,0,0),)
    color_not_to_draw: tuple[Color, ...] = ((217, 213, 102),)


    config: TracerConfig = TracerConfig(
        debug=True,
        enable_fill_slicing=False,
        enable_reduction_visualisation=False,
        enable_inputs_visualisation=False,
        enable_texture_transformation_visualisation=True,
        enable_island_selection_visualisation=False,
    )

    tracer: Tracer = Tracer(config, texture_path, model_path, mask_path, palette, color_not_to_draw)
    tracer.compute_traces()
    tracer.export_traces(output_path)


if __name__ == "__main__":
    main()
