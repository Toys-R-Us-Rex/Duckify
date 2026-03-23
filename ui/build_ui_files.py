import subprocess
from pathlib import Path


def build_ui():
    print("Building UI files...")
    ui_dir: Path = Path(__file__).parent / "ui"
    for ui_file in ui_dir.glob("*.ui"):
        py_file = ui_file.parent / f"{ui_file.stem}_ui.py"
        print(f"{ui_file} -> {py_file}")
        subprocess.run(["pyuic6", str(ui_file), "-o", str(py_file)], check=True)


if __name__ == "__main__":
    build_ui()
