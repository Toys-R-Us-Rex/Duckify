from pathlib import Path

from tracing.color import Color
from tracing.trace import Trace
from tracing.tracer import Tracer

PROJECT_DIR = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"


def main():
    texture_path: Path = ASSETS_DIR / "textures" / "dice.jpg"
    model_path: Path = ASSETS_DIR / "models" / "dice.obj"
    palette: tuple[Color, ...] = ((255, 0, 0), (0, 255, 0), (0, 0, 255))

    tracer: Tracer = Tracer(texture_path, model_path, palette)
    traces: list[Trace] = tracer.compute_traces()


if __name__ == "__main__":
    main()
