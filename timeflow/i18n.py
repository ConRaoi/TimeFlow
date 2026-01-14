from dataclasses import dataclass
from typing import List, Tuple

SUPPORTED_LANGS = [
    ("en", "English"),
    ("de", "Deutsch"),
    ("es", "Español"),
    ("fr", "Français"),
]

@dataclass(frozen=True)
class Strings:
    app_title: str
    language_label: str
    mode_label: str
    mode_countdown: str
    mode_countup: str
    segments_label: str
    add_segment: str
    remove_segment: str
    focus_timer: str
    show_segments: str
    start: str
    pause: str
    reset: str
    time_remaining: str
    time_elapsed: str
    prev_segment: str
    next_segment: str
    
    current_segment: str # Z.B. "Aktuell:"
    next_segment: str    # Z.B. "Nächstes:"

    col_name: str
    col_minutes: str
    default_segments: List[Tuple[str, float]]

    # Presets
    presets_label: str
    save_preset: str
    manage_presets: str
    preset_name: str
    preset_saved: str
    preset_loaded: str
    preset_deleted: str
    confirm_delete: str
    new_segment_default: str # Default name for new segments

_STRINGS = {
    "en": Strings(
        app_title="TimeFlow",
        language_label="Language",
        mode_label="Mode",
        mode_countdown="Count down",
        mode_countup="Count up",
        segments_label="Segments",
        add_segment="Add",
        remove_segment="Remove",
        focus_timer="Focus timer",
        show_segments="Show segments",
        start="Start",
        pause="Pause",
        reset="Reset",
        time_remaining="Remaining",
        time_elapsed="Elapsed",
        
        current_segment="Current:",
        next_segment="Next:",
        prev_segment="Previous segment",

        col_name="Name",
        col_minutes="Minutes",
        default_segments=[("Intro", 3), ("Work", 20), ("Wrap-up", 5)],
        
        presets_label="Presets",
        save_preset="Save",
        manage_presets="Templates",
        preset_name="Template Name",
        preset_saved="Template saved!",
        preset_loaded="Template loaded!",
        preset_deleted="Template deleted!",
        confirm_delete="Are you sure you want to delete this template?",
        new_segment_default="New segment",
    ),
    "de": Strings(
        app_title="TimeFlow",
        language_label="Sprache",
        mode_label="Modus",
        mode_countdown="Runterzählen",
        mode_countup="Hochzählen",
        segments_label="Segmente",
        add_segment="Hinzufügen",
        remove_segment="Entfernen",
        focus_timer="Nur Timer",
        show_segments="Segmente anzeigen",
        start="Start",
        pause="Pause",
        reset="Zurücksetzen",
        time_remaining="Restzeit",
        time_elapsed="Vergangen",
        
        current_segment="Aktuell:",
        next_segment="Nächstes:",
        prev_segment="Vorheriger Abschnitt",

        col_name="Name",
        col_minutes="Minuten",
        default_segments=[("Einstieg", 3), ("Arbeitsphase", 20), ("Abschluss", 5)],
        
        presets_label="Vorlagen",
        save_preset="Speichern",
        manage_presets="Vorlagen",
        preset_name="Vorlagen-Name",
        preset_saved="Vorlage gespeichert!",
        preset_loaded="Vorlage geladen!",
        preset_deleted="Vorlage gelöscht!",
        confirm_delete="Möchten Sie diese Vorlage wirklich löschen?",
        new_segment_default="Neuer Abschnitt",
    ),
    "es": Strings(
        app_title="TimeFlow",
        language_label="Idioma",
        mode_label="Modo",
        mode_countdown="Cuenta atrás",
        mode_countup="Cuenta adelante",
        segments_label="Segmentos",
        add_segment="Añadir",
        remove_segment="Quitar",
        focus_timer="Solo tiempo",
        show_segments="Ver segmentos",
        start="Inicio",
        pause="Pausa",
        reset="Reset",
        time_remaining="Restante",
        time_elapsed="Transcurrido",
        
        current_segment="Actual:",
        next_segment="Siguiente:",
        prev_segment="Segmento anterior",

        col_name="Nombre",
        col_minutes="Minutos",
        default_segments=[("Intro", 3), ("Trabajo", 20), ("Cierre", 5)],
        
        presets_label="Plantillas",
        save_preset="Guardar",
        manage_presets="Plantillas",
        preset_name="Nombre de la plantilla",
        preset_saved="¡Plantilla guardada!",
        preset_loaded="¡Plantilla cargada!",
        preset_deleted="¡Plantilla eliminada!",
        confirm_delete="¿Seguro que quieres eliminar esta plantilla?",
        new_segment_default="Nuevo segmento",
    ),
    "fr": Strings(
        app_title="TimeFlow",
        language_label="Langue",
        mode_label="Mode",
        mode_countdown="Compte à rebours",
        mode_countup="Chronomètre",
        segments_label="Segments",
        add_segment="Ajouter",
        remove_segment="Supprimer",
        focus_timer="Minuteur seul",
        show_segments="Voir segments",
        start="Démarrer",
        pause="Pause",
        reset="RàZ",
        time_remaining="Restant",
        time_elapsed="Écoulé",
        
        current_segment="Actuel :",
        next_segment="Suivant :",
        prev_segment="Segment précédent",

        col_name="Nom",
        col_minutes="Minutes",
        default_segments=[("Intro", 3), ("Travail", 20), ("Clôture", 5)],
        
        presets_label="Modèles",
        save_preset="Enregistrer",
        manage_presets="Modèles",
        preset_name="Nom du modèle",
        preset_saved="Modèle enregistré !",
        preset_loaded="Modèle chargé !",
        preset_deleted="Modèle supprimé !",
        confirm_delete="Voulez-vous vraiment supprimer ce modèle ?",
        new_segment_default="Nouveau segment",
    ),
}

def get_strings(lang_code: str) -> Strings:
    return _STRINGS.get(lang_code, _STRINGS["en"])