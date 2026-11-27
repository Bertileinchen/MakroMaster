"""Makroschliff-Aufbereitung (MakroMaster) – Desktop-Start.

Öffnet die Oberfläche (app/index.html) in einem eigenen Fenster
(Windows: Edge WebView2) und stellt native „Speichern unter“-Dialoge für
PNG-Export und Projektdateien bereit. Alle Bilddaten bleiben lokal.
"""
import base64
import ctypes
import os
import sys

import webview

APP_TITLE = "MakroMaster – Makroschliff-Aufbereitung"

# (Beschreibung, Muster) je Dateiart
FILE_TYPES = {
    "png": [("PNG-Bild", "*.png")],
    "makro": [("MakroMaster-Projekt", "*.makro"), ("JSON", "*.json")],
}
DEFAULT_EXT = {"png": ".png", "makro": ".makro"}


if sys.platform == "win32":
    from ctypes import wintypes

    class OPENFILENAMEW(ctypes.Structure):
        _fields_ = [
            ("lStructSize", wintypes.DWORD),
            ("hwndOwner", wintypes.HWND),
            ("hInstance", wintypes.HINSTANCE),
            ("lpstrFilter", ctypes.c_wchar_p),
            ("lpstrCustomFilter", ctypes.c_wchar_p),
            ("nMaxCustFilter", wintypes.DWORD),
            ("nFilterIndex", wintypes.DWORD),
            ("lpstrFile", ctypes.c_wchar_p),
            ("nMaxFile", wintypes.DWORD),
            ("lpstrFileTitle", ctypes.c_wchar_p),
            ("nMaxFileTitle", wintypes.DWORD),
            ("lpstrInitialDir", ctypes.c_wchar_p),
            ("lpstrTitle", ctypes.c_wchar_p),
            ("Flags", wintypes.DWORD),
            ("nFileOffset", wintypes.WORD),
            ("nFileExtension", wintypes.WORD),
            ("lpstrDefExt", ctypes.c_wchar_p),
            ("lCustData", wintypes.LPARAM),
            ("lpfnHook", ctypes.c_void_p),
            ("lpTemplateName", ctypes.c_wchar_p),
            ("pvReserved", ctypes.c_void_p),
            ("dwReserved", wintypes.DWORD),
            ("FlagsEx", wintypes.DWORD),
        ]


def _win_save_dialog(filename: str, directory: str, kind: str):
    """Windows-Standarddialog „Speichern unter“ (comdlg32) direkt aufrufen."""
    # Dialog braucht COM im aufrufenden Thread (js_api läuft in eigenem Thread)
    try:
        ctypes.windll.ole32.CoInitializeEx(None, 0x2)  # COINIT_APARTMENTTHREADED
    except Exception:
        pass

    types = FILE_TYPES.get(kind, [("Alle Dateien", "*.*")])
    filt = "".join(f"{d} ({p})\0{p}\0" for d, p in types) + "\0"
    filter_buf = ctypes.create_unicode_buffer(filt, len(filt) + 1)
    file_buf = ctypes.create_unicode_buffer(filename, 1024)
    defext = DEFAULT_EXT.get(kind, "").lstrip(".")

    ofn = OPENFILENAMEW()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAMEW)
    ofn.hwndOwner = ctypes.windll.user32.GetForegroundWindow()
    ofn.lpstrFilter = ctypes.cast(filter_buf, ctypes.c_wchar_p)
    ofn.nFilterIndex = 1
    ofn.lpstrFile = ctypes.cast(file_buf, ctypes.c_wchar_p)
    ofn.nMaxFile = 1024
    ofn.lpstrInitialDir = directory
    ofn.lpstrDefExt = defext or None
    # OVERWRITEPROMPT | NOCHANGEDIR | PATHMUSTEXIST | EXPLORER
    ofn.Flags = 0x2 | 0x8 | 0x800 | 0x80000

    if not ctypes.windll.comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
        err = ctypes.windll.comdlg32.CommDlgExtendedError()
        if err:
            raise OSError(f"Speichern-Dialog meldet Fehler 0x{err:X}")
        return None  # abgebrochen
    return file_buf.value


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
        filename = "".join(c for c in filename if c not in '<>:"/\\|?*').strip() or "Makro"
        if sys.platform == "win32":
            path = _win_save_dialog(filename, self._last_dir, kind)
        else:
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG, directory=self._last_dir, save_filename=filename
            )
            path = (result[0] if isinstance(result, (list, tuple)) else result) if result else None
        if not path:
            return None
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
