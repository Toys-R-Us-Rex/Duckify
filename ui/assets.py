from pathlib import Path


class AssetRegistry:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = root_dir
        self.assets_dir: Path = self.root_dir / "assets"
        self.models_dir: Path = self.assets_dir / "models"
        self.textures_dir: Path = self.assets_dir / "textures"
        self.masks_dir: Path = self.textures_dir / "masks"
        self.output_dir: Path = self.root_dir / "output"
        self.transformation_reference: Path = (
            self.assets_dir / "transformation_reference.json"
        )
        self.default_tcp_calibration_path: Path = self.root_dir / "robot" / "duckify_simulation" / "defaults" / "calibration_default.pkl"
        self.test_transformation_path: Path = self.root_dir / "robot" / "duckify_simulation" / "defaults" / "transformation_test.pkl"

    def list_models(self, extension: str) -> list[Path]:
        return sorted(self.models_dir.glob(f"*.{extension}"))

    def list_textures(self) -> list[Path]:
        return sorted(self.textures_dir.iterdir())

    def list_masks(self) -> list[Path]:
        return sorted(self.masks_dir.iterdir())

    def list_traces(self) -> list[Path]:
        return sorted(self.output_dir.glob("*-trace.json"))
