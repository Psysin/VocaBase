"""data/storage.py

Dieses Modul ist das 'Gedächtnis' der App.
Es regelt das Speichern und Laden aller Python-Objekte
(Profile und Vokabeln) als dauerhafte Text-Datei (JSON).
"""

import json
import os
import pathlib
from core.models import UserProfile

# Dynamischen Dokumenten-Ordner für Mac und die iOS-Sandbox ermitteln
DOCUMENTS_DIR = pathlib.Path.home() / "Documents"

# Erstellt den Ordner sicherheitshalber, falls er auf einem neuen Gerät noch nicht existiert
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

# Der neue absolute Pfad zur Speicherdatei
DATA_FILE = str(DOCUMENTS_DIR / "app_data.json")


def save_app_data(
    profiles: list[UserProfile],
    active_profile_name: str | None = None,
    filepath: str = DATA_FILE,
) -> None:
    """Speichert alle Profile und den aktuell ausgewählten Nutzer in einer JSON-Datei.

    :param profiles: Die Liste aller UserProfile-Objekte im Arbeitsspeicher
    :param active_profile_name: Der Name des Nutzers, der zuletzt eingeloggt war
    :param filepath: Der Pfad zur Speicherdatei (Standard: dynamischer Dokumenten-Ordner)
    """

    # Wir bauen ein großes Dictionary auf, das alle Daten enthält.
    # [p.to_dict() for p in profiles] ruft für jedes Profil die Funktion auf,
    # die das Profil und seine Vokabeln in ein simples Dictionary umwandelt.
    data = {
        "active_profile": active_profile_name,
        "profiles": [p.to_dict() for p in profiles],
    }

    # Datei sicher im Schreib-Modus ("w" = write) öffnen
    with open(filepath, "w", encoding="utf-8") as file:
        # json.dump() übersetzt das Python-Dictionary in einen echten JSON-Text.
        # indent=4 sorgt für schöne Zeilenumbrüche, ensure_ascii=False erhält Umlaute.
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_app_data(
    filepath: str = DATA_FILE,
) -> tuple[list[UserProfile], str | None]:
    """Lädt alle Profile und gibt (Liste_der_Profile, aktiver_Nutzername) zurück.

    Gibt ([], None) zurück, wenn noch keine Speicherdatei existiert.
    """
    # Wenn die App zum ersten Mal startet, gibt es noch keine app_data.json
    if not os.path.exists(filepath):
        return [], None

    # try-except fängt Abstürze ab (z. B. wenn die JSON-Datei manuell kaputtgemacht wurde)
    try:
        # Datei sicher im Lese-Modus ("r" = read) öffnen
        with open(filepath, "r", encoding="utf-8") as file:
            # json.load() liest den JSON-Text und macht ein Python-Dictionary daraus
            data = json.load(file)

            # Aus den nackten Dictionary-Daten (p) bauen wir über die Fabrik-Methode
            # from_dict() wieder echte, funktionierende UserProfile-Objekte zusammen.
            profiles = [UserProfile.from_dict(p) for p in data.get("profiles", [])]
            active_profile = data.get("active_profile")

            # Wir geben die fertige Liste und den zuletzt aktiven Nutzer zurück
            return profiles, active_profile

    except (json.JSONDecodeError, KeyError):
        # Falls beim Lesen ein Fehler auftritt, verhalten wir uns wie beim allerersten Start
        return [], None
