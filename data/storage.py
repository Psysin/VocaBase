import json
import os
from core.models import UserProfile

DATA_FILE = "app_data.json"


def save_app_data(
    profiles: list[UserProfile],
    active_profile_name: str | None = None,
    filepath: str = DATA_FILE,
) -> None:
    """Speichert alle Profile und den aktuell ausgewählten Nutzer in einer JSON-Datei."""
    data = {
        "active_profile": active_profile_name,
        "profiles": [p.to_dict() for p in profiles],
    }

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_app_data(
    filepath: str = DATA_FILE,
) -> tuple[list[UserProfile], str | None]:
    """Lädt alle Profile und gibt (Liste_der_Profile, aktiver_Nutzername) zurück."""
    if not os.path.exists(filepath):
        return [], None

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
            profiles = [UserProfile.from_dict(p) for p in data.get("profiles", [])]
            active_profile = data.get("active_profile")
            return profiles, active_profile
    except (json.JSONDecodeError, KeyError):
        return [], None
