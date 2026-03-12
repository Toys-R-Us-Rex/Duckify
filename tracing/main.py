from pathlib import Path

from tracing.color import Color
from tracing.config import TracerConfig
from tracing.tracer import Tracer

PROJECT_DIR = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUT_DIR = PROJECT_DIR / "output"


def main():
    texture_path: Path = ASSETS_DIR / "textures" / "duck_army.jpg"
    model_path: Path = ASSETS_DIR / "models" / "duck_uv.obj"
    texture_name: str = texture_path.stem
    model_name: str = model_path.stem
    output_path: Path = OUTPUT_DIR / f"{model_name}-{texture_name}-trace.json"
    palette: tuple[Color, ...] = ((0, 255, 0), (255, 255, 0),(255,255,255),)
    outlier: Color = (0,0,0)

    config: TracerConfig = TracerConfig(
        debug=True,
        fill_slicing_toggle=False
    )

    tracer: Tracer = Tracer(config, texture_path, model_path, palette, outlier)
    tracer.compute_traces()
    tracer.export_traces(output_path)


if __name__ == "__main__":
    main()
