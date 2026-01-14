import json
import os
import platform
from pathlib import Path
from typing import List, Dict, Any, Tuple

class PresetsManager:
    """
    Manages loading and saving of timer presets in the user's Documents folder.
    File path: ~/Documents/TimeFlow/presets.json
    """

    def __init__(self):
        self._ensure_storage_dir()

    def _get_documents_path(self) -> Path:
        """Returns the path to the user's Documents directory."""
        return Path.home() / "Documents"

    def _get_storage_path(self) -> Path:
        """Returns the full path to presets.json."""
        return self._get_documents_path() / "TimeFlow" / "presets.json"

    def _ensure_storage_dir(self):
        """Creates the TimeFlow directory in Documents if it doesn't exist."""
        path = self._get_storage_path().parent
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating storage directory: {e}")

    def load_presets(self) -> List[Dict[str, Any]]:
        """Loads all presets. Returns a list of dicts: [{'name': '...', 'segments': [...]}]"""
        path = self._get_storage_path()
        if not path.exists():
            return []
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("presets", [])
        except Exception as e:
            print(f"Error loading presets: {e}")
            return []

    def save_preset(self, name: str, segments: List[Tuple[str, float]]) -> bool:
        """Saves a new preset or overwrites an existing one with the same name."""
        presets = self.load_presets()
        
        # Convert segments to JSON-serializable format if needed (list of lists/tuples is fine)
        new_entry = {
            "name": name,
            "segments": segments
        }
        
        # Check if exists, update index
        found = False
        for i, p in enumerate(presets):
            if p["name"] == name:
                presets[i] = new_entry
                found = True
                break
        
        if not found:
            presets.append(new_entry)
            
        return self._write_presets(presets)

    def delete_preset(self, name: str) -> bool:
        """Deletes a preset by name."""
        presets = self.load_presets()
        initial_len = len(presets)
        presets = [p for p in presets if p["name"] != name]
        
        if len(presets) < initial_len:
            return self._write_presets(presets)
        return False

    def rename_preset(self, old_name: str, new_name: str) -> bool:
        """Renames a preset."""
        presets = self.load_presets()
        for p in presets:
            if p["name"] == old_name:
                p["name"] = new_name
                return self._write_presets(presets)
        return False

    def _write_presets(self, presets: List[Dict[str, Any]]) -> bool:
        """Writes the list of presets to disk."""
        path = self._get_storage_path()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"presets": presets}, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error writing presets: {e}")
            return False
