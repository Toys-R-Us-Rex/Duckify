from pathlib import Path
import socket

from PyQt6.QtWidgets import QComboBox


def ping(host: str, port: int, timeout: int = 3) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))
        sock.close()
        return True

    # Timeout => host not up
    except socket.timeout:
        return False

    # Other error => host up but port not open
    except Exception:
        return False


def populate_combobox(box: QComboBox, paths: list[Path], base: Path):
    for path in paths:
        box.addItem(str(path.relative_to(base)), path)