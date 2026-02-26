from pathlib import Path

from tracing.color import Color
from tracing.trace import Trace3D
from tracing.tracer import Tracer

PROJECT_DIR = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"


def main():
    texture_path: Path = ASSETS_DIR / "textures" / "dice.jpg"
    model_path: Path = ASSETS_DIR / "models" / "dice.obj"
    palette: tuple[Color, ...] = ((255, 0, 0), (0, 255, 0), (0, 0, 255))

    traces: list[Trace3D] = tracer.compute_traces()


if __name__ == "__main__":
    main()
