from PySide6.QtCore import QSettings
import json

class NoisePresetsManager:
    """
    Verwaltet die Speicherung und das Laden von Lärmampel-Voreinstellungen.
    Die Voreinstellungen werden in QSettings gespeichert.
    """
    def __init__(self):
        self.settings = QSettings("TimeFlow", "NoisePresets")

    def save_preset(self, name: str, sensitivity: int, limit: int):
        """Speichert eine neue Voreinstellung."""
        presets = self.load_presets()
        # Vorhandenes mit gleichem Namen überschreiben oder neu hinzufügen
        new_presets = [p for p in presets if p["name"] != name]
        new_presets.append({
            "name": name,
            "sensitivity": sensitivity,
            "limit": limit
        })
        self.settings.setValue("all_presets", json.dumps(new_presets))

    def load_presets(self):
        """Lädt alle gespeicherten Voreinstellungen."""
        raw = self.settings.value("all_presets", "[]")
        try:
            return json.loads(raw)
        except:
            return []

    def delete_preset(self, name: str):
        """Löscht eine Voreinstellung."""
        presets = self.load_presets()
        new_presets = [p for p in presets if p["name"] != name]
        self.settings.setValue("all_presets", json.dumps(new_presets))

    def rename_preset(self, old_name: str, new_name: str):
        """Benennt eine Voreinstellung um."""
        presets = self.load_presets()
        for p in presets:
            if p["name"] == old_name:
                p["name"] = new_name
                break
        self.settings.setValue("all_presets", json.dumps(presets))

    def save_last_settings(self, sensitivity: int, limit: int):
        """Speichert die zuletzt verwendeten Einstellungen."""
        last_settings = QSettings("TimeFlow", "TimeFlow")
        last_settings.setValue("noise_last_sensitivity", sensitivity)
        last_settings.setValue("noise_last_limit", limit)

    def load_last_settings(self):
        """Lädt die zuletzt verwendeten Einstellungen."""
        last_settings = QSettings("TimeFlow", "TimeFlow")
        sens = last_settings.value("noise_last_sensitivity", 40)
        limit = last_settings.value("noise_last_limit", 70)
        return int(sens), int(limit)
