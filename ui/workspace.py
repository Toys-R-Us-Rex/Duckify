import tempfile
from pathlib import Path


class WorkspaceManager:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="duckify_")
        self.root: Path = Path(self.tmp.name)

    def cleanup(self):
        self.tmp.cleanup()

    @property
    def texture_path(self) -> Path:
        return self.root / "texture.png"

    @property
    def paletted_texture_path(self) -> Path:
        return self.root / "paletted.png"

    @property
    def traces_path(self) -> Path:
        return self.root / "traces.json"

    @property
    def calibration_path(self) -> Path:
        return self.root / "calibration.json"

    @property
    def transformation_path(self) -> Path:
        return self.root / "transformation.json"

    @property
    def pen_origin_path(self) -> Path:
        return self.root / "pen_origin.json"
