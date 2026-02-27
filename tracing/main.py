from pathlib import Path

from tracing.color import Color
from tracing.tracer import Tracer

PROJECT_DIR = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUT_DIR = PROJECT_DIR / "output"


def main():
    texture_path: Path = ASSETS_DIR / "textures" / "trapezoid_colors.png"
    model_path: Path = ASSETS_DIR / "models" / "trapezoid_letters.obj"
    texture_name: str = texture_path.stem
    model_name: str = model_path.stem
    output_path: Path = OUTPUT_DIR / f"{model_name}-{texture_name}-trace.json"
    palette: tuple[Color, ...] = ((255, 255, 255), (255, 0, 0), (0, 255, 0))

    tracer: Tracer = Tracer(texture_path, model_path, palette, debug=True)
    tracer.compute_traces()
    tracer.export_traces(output_path)


if __name__ == "__main__":
    main()
