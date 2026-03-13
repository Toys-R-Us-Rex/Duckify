from pathlib import Path
import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt

from main_ui import Ui_MainWindow

ROOT_DIR: Path = Path(__file__).parent.parent


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    MODELS_DIR: Path = ROOT_DIR / "assets" / "models"
    TEXTURES_DIR: Path = ROOT_DIR / "assets" / "textures"

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Duckify")
        
        self.setup_gen_ai()
        self.setup_tracing()
        self.setup_robot()
    
    def setup_gen_ai(self):
        self.genAIModel.addItems(self.list_models())
    
    def setup_tracing(self):
        self.tracingModel.addItems(self.list_models())
        self.tracingTexture.addItems(self.list_textures())
    
    def setup_robot(self):
        pass

    def list_models(self) -> list[str]:
        paths: list[Path] = list(self.MODELS_DIR.iterdir())
        return list(map(lambda p: str(p.relative_to(self.MODELS_DIR)), paths))

    def list_textures(self) -> list[str]:
        paths: list[Path] = list(self.TEXTURES_DIR.iterdir())
        return list(map(lambda p: str(p.relative_to(self.TEXTURES_DIR)), paths))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
