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
    
    current_segment: str # Z.B. "Aktuell:"
    next_segment: str    # Z.B. "Nächstes:"

    col_name: str
    col_minutes: str
    default_segments: List[Tuple[str, float]]

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

        col_name="Name",
        col_minutes="Minutes",
        default_segments=[("Intro", 3), ("Work", 20), ("Wrap-up", 5)],
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

        col_name="Name",
        col_minutes="Minuten",
        default_segments=[("Einstieg", 3), ("Arbeitsphase", 20), ("Abschluss", 5)],
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

        col_name="Nombre",
        col_minutes="Minutos",
        default_segments=[("Intro", 3), ("Trabajo", 20), ("Cierre", 5)],
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

        col_name="Nom",
        col_minutes="Minutes",
        default_segments=[("Intro", 3), ("Travail", 20), ("Clôture", 5)],
    ),
}

def get_strings(lang_code: str) -> Strings:
    return _STRINGS.get(lang_code, _STRINGS["en"])