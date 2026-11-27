"""Makroschliff-Aufbereitung (MakroMaster) – Desktop-Start.

Öffnet die Oberfläche (app/index.html) in einem eigenen Fenster
(Windows: Edge WebView2) und stellt native „Speichern unter“-Dialoge für
PNG-Export und Projektdateien bereit. Alle Bilddaten bleiben lokal.
"""
import base64
import os
import sys

import webview

APP_TITLE = "MakroMaster – Makroschliff-Aufbereitung"

FILE_TYPES = {
    "png": ("PNG-Bild (*.png)",),
    "makro": ("MakroMaster-Projekt (*.makro)", "JSON (*.json)"),
}
DEFAULT_EXT = {"png": ".png", "makro": ".makro"}


def resource_path(*parts: str) -> str:
    """Pfad zu mitgelieferten Dateien – auch in der PyInstaller-EXE."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


class Api:
    """Von der Oberfläche über window.pywebview.api aufrufbar.

    Wichtig: Interne Attribute beginnen mit "_", sonst versucht pywebview,
    sie (inkl. des Fensterobjekts) an JavaScript zu übergeben – dann steht
    die Schnittstelle nicht zur Verfügung.
    """

    def __init__(self) -> None:
        self._window = None
        pics = os.path.join(os.path.expanduser("~"), "Pictures")
        self._last_dir = pics if os.path.isdir(pics) else os.path.expanduser("~")

    def _bind(self, window) -> None:
        self._window = window

    def save_file(self, data_url: str, filename: str, kind: str = "png"):
        """Datei (als data:-URL) über einen Speichern-Dialog ablegen.

        Gibt den gespeicherten Pfad zurück, oder None bei Abbruch.
        """
        if "," not in data_url or not data_url.startswith("data:"):
            raise ValueError("Unerwartetes Datenformat")
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            directory=self._last_dir,
            save_filename=filename,
            file_types=FILE_TYPES.get(kind, ("Alle Dateien (*.*)",)),
        )
        if not result:
            return None
        path = result[0] if isinstance(result, (list, tuple)) else result
        ext = DEFAULT_EXT.get(kind)
        if ext and not os.path.splitext(path)[1]:
            path += ext
        header, payload = data_url.split(",", 1)
        raw = base64.b64decode(payload) if ";base64" in header else payload.encode("utf-8")
        with open(path, "wb") as fh:
            fh.write(raw)
        self._last_dir = os.path.dirname(path)
        return path

    # Kompatibilität mit älterer Oberfläche
    def save_png(self, data_url: str, filename: str):
        return self.save_file(data_url, filename, "png")


def main() -> None:
    try:  # Fallback, falls die Oberfläche doch einen Browser-Download auslöst
        webview.settings["ALLOW_DOWNLOADS"] = True
    except Exception:
        pass

    api = Api()
    # Oberfläche direkt als HTML übergeben (kein lokaler Webserver auf
    # 127.0.0.1 – der wird in Firmennetzen oft von Proxy/Firewall blockiert).
    with open(resource_path("app", "index.html"), encoding="utf-8") as fh:
        html = fh.read()
    window = webview.create_window(
        APP_TITLE,
        html=html,
        js_api=api,
        width=1400,
        height=900,
        min_size=(1000, 650),
        background_color="#16181b",
    )
    api._bind(window)
    webview.start(debug="--debug" in sys.argv)


if __name__ == "__main__":
    main()
