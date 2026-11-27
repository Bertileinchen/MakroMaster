"""Makroschliff-Aufbereitung – Desktop-Start.

Öffnet die Web-Oberfläche (app/index.html) in einem eigenen Fenster
(Windows: Edge WebView2) und stellt einen nativen „Speichern unter“-Dialog
für den PNG-Export bereit. Alle Bilddaten bleiben lokal.
"""
import base64
import os
import sys

import webview

APP_TITLE = "Makroschliff-Aufbereitung"


def resource_path(*parts: str) -> str:
    """Pfad zu mitgelieferten Dateien – auch in der PyInstaller-EXE."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


class Api:
    """Funktionen, die die Oberfläche über window.pywebview.api aufrufen kann."""

    def __init__(self) -> None:
        self.window = None
        self.last_dir = os.path.join(os.path.expanduser("~"), "Pictures")
        if not os.path.isdir(self.last_dir):
            self.last_dir = os.path.expanduser("~")

    def save_png(self, data_url: str, filename: str):
        """PNG (als data:-URL) über einen Speichern-Dialog ablegen.

        Gibt den gespeicherten Pfad zurück, oder None bei Abbruch.
        """
        if not data_url.startswith("data:image/png;base64,"):
            raise ValueError("Unerwartetes Datenformat")
        result = self.window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=self.last_dir,
            save_filename=filename,
            file_types=("PNG-Bild (*.png)",),
        )
        if not result:
            return None
        path = result[0] if isinstance(result, (list, tuple)) else result
        if not path.lower().endswith(".png"):
            path += ".png"
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(data_url.split(",", 1)[1]))
        self.last_dir = os.path.dirname(path)
        return path


def main() -> None:
    api = Api()
    window = webview.create_window(
        APP_TITLE,
        url=resource_path("app", "index.html"),
        js_api=api,
        width=1400,
        height=900,
        min_size=(1000, 650),
        background_color="#16181b",
    )
    api.window = window
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
