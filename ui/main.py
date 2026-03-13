from pathlib import Path
import sys

from PyQt6 import QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon

from main_ui import Ui_MainWindow

ROOT_DIR: Path = Path(__file__).parent.parent


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    MODELS_DIR: Path = ROOT_DIR / "assets" / "models"
    TEXTURES_DIR: Path = ROOT_DIR / "assets" / "textures"

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Duckify")
        
        self.gen_ai_result_model: QStandardItemModel = QStandardItemModel(self.genAIResults)
        self.gen_ai_result_model.itemChanged.connect(self.select_gen_ai_result)

        self.setup_gen_ai()
        self.setup_tracing()
        self.setup_robot()

    def setup_gen_ai(self):
        self.genAIModel.addItems(self.list_models())
        self.genAIGenerate.clicked.connect(self.generate_texture)
        self.genAIResults.clicked.connect(self.select_gen_ai_result)

    def setup_tracing(self):
        self.tracingModel.addItems(self.list_models())
        self.tracingTexture.addItems(self.list_textures())
        self.tracingTrace.clicked.connect(self.start_tracing)

    def setup_robot(self):
        pass

    def list_models(self) -> list[str]:
        paths: list[Path] = list(self.MODELS_DIR.iterdir())
        return list(map(lambda p: str(p.relative_to(self.MODELS_DIR)), paths))

    def list_textures(self) -> list[str]:
        paths: list[Path] = list(self.TEXTURES_DIR.iterdir())
        return list(map(lambda p: str(p.relative_to(self.TEXTURES_DIR)), paths))

    def generate_texture(self):
        self.set_texture_results(list(self.TEXTURES_DIR.iterdir()))
        print("Generating texture")

    def start_tracing(self):
        print("Starting tracing")
    
    def set_texture_results(self, results: list[Path]):
        model: QStandardItemModel = self.gen_ai_result_model
        for result in results:
            item = QStandardItem(QIcon(str(result)), str(result.relative_to(self.TEXTURES_DIR)))
            item.setData(result)
            item.setEditable(False)
            model.appendRow(item)
        
        self.genAIResults.setModel(model)
    
    def select_gen_ai_result(self, item: QStandardItem):
        path: Path = item.data()
        print(f"Selected {path}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
