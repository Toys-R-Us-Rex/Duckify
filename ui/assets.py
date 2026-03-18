from pathlib import Path


class AssetRegistry:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = root_dir
        self.models_dir: Path = self.root_dir / "assets" / "models"
        self.textures_dir: Path = self.root_dir / "assets" / "textures"
        self.output_dir: Path = self.root_dir / "output"
        self.transformation_reference: Path = (
            self.root_dir / "assets" / "transformation_reference.json"
        )

    def list_models(self, extension: str) -> list[Path]:
        return sorted(self.models_dir.glob(f"*.{extension}"))

    def list_textures(self) -> list[Path]:
        return sorted(self.textures_dir.iterdir())

    def list_traces(self) -> list[Path]:
        return sorted(self.output_dir.glob("*-trace.json"))
