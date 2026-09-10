"""core/audio.py

Ordnet Vokabeltexten vorab erzeugte Aussprache-Audiodateien zu.

Die eigentlichen .m4a-Dateien werden nicht zur Laufzeit erzeugt (das
bräuchte Internet oder ein natives TTS-Plugin), sondern einmalig am Mac
über scripts/generate_audio.py per macOS "say" generiert und als
Projektdateien mit ausgeliefert - genau wie die CSV-Vokabelpakete in
data/starter_words.py.
"""

import json
import pathlib
import re
import shutil

from data.storage import DOCUMENTS_DIR

# __file__ liegt in core/, .parent.parent ist daher das Projekt-Root,
# analog zu DATA_DIR in data/starter_words.py.
DATA_DIR = pathlib.Path(__file__).parent.parent / "data"

# Schreibbarer Zwischenspeicher für Audiodateien, die dem nativen Audio-
# Control als echter Dateipfad (statt roher Bytes) übergeben werden -
# siehe core/audio.py Docstring-Hinweis zu get_or_cache_audio_path().
AUDIO_CACHE_DIR = DOCUMENTS_DIR / "audio_cache"

# Pro Sprachpaket: Unterordner mit den .m4a-Dateien und die zugehörige
# Manifest-Datei (Liste der Original-Wörter, für die Audio existiert).
# Weitere Sprachen werden hier künftig einfach ergänzt.
SPRACH_AUDIO_KONFIG: dict[str, dict[str, str]] = {
    "Englisch Basis A1": {
        "ordner": "audio/en",
        "manifest": "audio_manifest_en.json",
    },
    "Spanisch Basis A1": {
        "ordner": "audio/es",
        "manifest": "audio_manifest_es.json",
    },
}

_manifest_cache: dict[str, set[str]] = {}


def slugify_word(text: str) -> str:
    """Wandelt ein Vokabel-Wort in einen dateisystem-sicheren Namen um.

    Deterministisch und ohne externe Abhängigkeiten, damit Generierungs-
    Skript und Laufzeit-Code immer denselben Dateinamen berechnen. Nur
    Leerzeichen/Interpunktion werden durch "_" ersetzt - Buchstaben mit
    Akzenten (á, ñ, ü, ...) bleiben erhalten (macOS/iOS unterstützen
    Unicode-Dateinamen problemlos), sonst würden z. B. die spanischen
    Wörter "allí" und "allá" beide zu "all" kollabieren.
    """
    return re.sub(r"[^\w]+", "_", text.strip().lower(), flags=re.UNICODE).strip("_")


def _lade_manifest(language: str) -> set[str]:
    """Lädt (und cached) die Menge der Wörter mit vorhandener Audiodatei."""
    if language in _manifest_cache:
        return _manifest_cache[language]

    konfig = SPRACH_AUDIO_KONFIG.get(language)
    woerter: set[str] = set()

    if konfig:
        manifest_pfad = DATA_DIR / konfig["manifest"]
        if manifest_pfad.exists():
            try:
                with open(manifest_pfad, "r", encoding="utf-8") as datei:
                    woerter = set(json.load(datei))
            except (json.JSONDecodeError, OSError):
                woerter = set()

    _manifest_cache[language] = woerter
    return woerter


def has_audio(language: str, word: str) -> bool:
    """Prüft, ob für dieses Wort in dieser Sprache eine Aussprache existiert."""
    return word.strip().lower() in {w.strip().lower() for w in _lade_manifest(language)}


def get_audio_bytes(language: str, word: str) -> bytes | None:
    """Lädt die Audiodaten für ein Wort, oder None falls nicht vorhanden."""
    konfig = SPRACH_AUDIO_KONFIG.get(language)
    if not konfig or not has_audio(language, word):
        return None

    dateipfad = DATA_DIR / konfig["ordner"] / f"{slugify_word(word)}.m4a"
    if not dateipfad.exists():
        return None

    with open(dateipfad, "rb") as datei:
        return datei.read()


def get_or_cache_audio_path(language: str, word: str) -> str | None:
    """Liefert einen echten, abspielbaren Dateipfad für ein Wort.

    flet_audio.Audio.src akzeptiert zwar auch rohe Bytes, doch auf iOS
    fehlt dafür ein mimeType-Hinweis im aktuellen flet-audio (siehe
    Plan-Notizen) - die Wiedergabe bleibt dadurch stumm. Ein echter
    Dateipfad umgeht das Problem (Formaterkennung über die Dateiendung).

    Da data/audio/<ordner>/ schreibgeschützt mit der App ausgeliefert
    wird, wird die Datei bei Bedarf einmalig in den beschreibbaren
    Dokumente-Ordner kopiert (siehe AUDIO_CACHE_DIR) und von dort
    abgespielt - idempotent, spätere Aufrufe finden die Kopie bereits vor.
    """
    konfig = SPRACH_AUDIO_KONFIG.get(language)
    if not konfig or not has_audio(language, word):
        return None

    quelle = DATA_DIR / konfig["ordner"] / f"{slugify_word(word)}.m4a"
    if not quelle.exists():
        return None

    # Nach Sprachordner getrennt (z. B. audio_cache/audio/en/...), da sich
    # Slugs zwischen Sprachen überschneiden können (z. B. "no", "total" -
    # existieren sowohl im Englisch- als auch im Spanisch-Paket).
    ziel = AUDIO_CACHE_DIR / konfig["ordner"] / f"{slugify_word(word)}.m4a"
    if not ziel.exists():
        ziel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(quelle, ziel)

    return str(ziel)
