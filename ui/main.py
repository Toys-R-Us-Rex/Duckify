from pathlib import Path
import sys
import tempfile

from PyQt6 import QtWidgets
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon

from main_ui import Ui_MainWindow
from tracing.color import Color
from tracing.config import TracerConfig
from tracing.tracer import Tracer

ROOT_DIR: Path = Path(__file__).parent.parent


class App(QtWidgets.QMainWindow, Ui_MainWindow):
    MODELS_DIR: Path = ROOT_DIR / "assets" / "models"
    TEXTURES_DIR: Path = ROOT_DIR / "assets" / "textures"

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)
        
        self.gen_ai_result_model: QStandardItemModel = QStandardItemModel(self.genAIResults)
        self.gen_ai_result_model.itemChanged.connect(self.select_gen_ai_result)
        working_dir = tempfile.TemporaryDirectory(prefix="duckify_")
        self.working_dir: Path = Path(working_dir.name)

        self.setup_gen_ai()
        self.setup_tracing()
        self.setup_robot()
    
    @property
    def texture_path(self) -> Path:
        return self.working_dir / "texture.png"
    
    @property
    def traces_path(self) -> Path:
        return self.working_dir / "traces.json"

    def setup_gen_ai(self):
        for model_path in self.list_models():
            name: str = str(model_path.relative_to(self.MODELS_DIR))
            self.genAIModel.addItem(name, model_path)

        self.genAIGenerate.clicked.connect(self.generate_texture)
        self.genAIResults.clicked.connect(self.select_gen_ai_result)

    def setup_tracing(self):
        for model_path in self.list_models():
            name: str = str(model_path.relative_to(self.MODELS_DIR))
            self.tracingModel.addItem(name, model_path)
        
        for texture_path in self.list_textures():
            name: str = str(texture_path.relative_to(self.TEXTURES_DIR))
            self.tracingTexture.addItem(name, texture_path)

        self.tracingTrace.clicked.connect(self.start_tracing)

    def setup_robot(self):
        pass

    def list_models(self) -> list[Path]:
        return list(self.MODELS_DIR.iterdir())

    def list_textures(self) -> list[Path]:
        return list(self.TEXTURES_DIR.iterdir())

    def generate_texture(self):
        self.set_texture_results(list(self.TEXTURES_DIR.iterdir()))
        print("Generating texture")

    def start_tracing(self):
        print("Starting tracing")
        palette: tuple[Color, ...] = ((0, 255, 0), (255, 255, 0),(255,255,255),)
        ignored_color: Color = (0,0,0)
        
        model_path: Path = self.tracingModel.currentData()
        texture_path: Path = self.tracingTexture.currentData()

        config: TracerConfig = TracerConfig(
            enable_fill_slicing=self.tracingEnableFill.isChecked()
        )

        tracer: Tracer = Tracer(config, texture_path, model_path, palette, ignored_color)
        tracer.compute_traces()
        tracer.export_traces(self.traces_path)
    
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
