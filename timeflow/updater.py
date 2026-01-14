import sys
import os
import requests
from packaging import version
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot

# Wir holen die Version dynamisch aus deiner Datei
from .version import __version__ as CURRENT_VERSION

# --- KONFIGURATION ---
GITHUB_REPO = "ConRaoi/TimeFlow"
# ---------------------

class UpdateWorker(QObject):
    # Signale für die GUI
    updateAvailable = Signal(str, str, str) # version, url, notes
    noUpdate = Signal()
    error = Signal(str)
    
    downloadProgress = Signal(int)
    downloadFinished = Signal(str)

    def __init__(self):
        super().__init__()
        self._download_url = None # Zwischenspeicher

    @Slot()
    def check_updates(self):
        """Prüft auf GitHub, ob eine neue Version vorliegt."""
        try:
            print(f"[Updater] Prüfe Updates für {GITHUB_REPO} (Lokal: {CURRENT_VERSION})...")
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            
            # Timeout wichtig, damit die App nicht hängt, wenn kein Internet da ist
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                data = response.json()
                latest_tag = data.get("tag_name", "").lstrip("v")
                
                # Versionen sicher vergleichen
                try:
                    local_v = version.parse(CURRENT_VERSION)
                    remote_v = version.parse(latest_tag)
                    
                    if remote_v > local_v:
                        download_url = self._get_url_for_os(data.get("assets", []))
                        if download_url:
                            notes = data.get("body", "Keine Details verfügbar.")
                            self.updateAvailable.emit(latest_tag, download_url, notes)
                        else:
                            self.noUpdate.emit() 
                    else:
                        self.noUpdate.emit()
                except Exception as ve:
                    print(f"[Updater] Versionsfehler: {ve}")
                    self.noUpdate.emit()
            else:
                # Server-Fehler oder Rate Limit, wir ignorieren es stillschweigend
                self.noUpdate.emit()

        except Exception as e:
            print(f"[Updater] Fehler beim Check: {e}")
            self.error.emit(str(e))

    @Slot(str)
    def start_download(self, url):
        """Lädt die Datei herunter, wenn der User klickt."""
        try:
            filename = url.split("/")[-1]
            save_path = Path.home() / "Downloads" / filename
            
            print(f"[Updater] Starte Download nach: {save_path}")
            
            with requests.get(url, stream=True, timeout=20) as r:
                r.raise_for_status()
                total_length = r.headers.get('content-length')
                
                with open(save_path, 'wb') as f:
                    if total_length is None:
                        f.write(r.content)
                        self.downloadProgress.emit(100)
                    else:
                        dl = 0
                        total_length = int(total_length)
                        for data in r.iter_content(chunk_size=4096):
                            dl += len(data)
                            f.write(data)
                            percent = int(100 * dl / total_length)
                            self.downloadProgress.emit(percent)
                            
            self.downloadFinished.emit(str(save_path))
            
        except Exception as e:
            self.error.emit(f"Download fehlgeschlagen: {e}")

    def _get_url_for_os(self, assets):
        """Sucht in der Asset-Liste die passende Datei für das aktuelle OS."""
        target_ext = ""
        if sys.platform == "win32":
            target_ext = ".exe"
        elif sys.platform == "darwin":
            target_ext = ".dmg"
        
        if not target_ext:
            return None

        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(target_ext):
                return asset.get("browser_download_url", "")
        
        return None