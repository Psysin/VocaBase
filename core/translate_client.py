"""core/translate_client.py

Bindet die kostenlose MyMemory Translation API an, um im "Übersetzer"
(ui/views/translator.py) ein deutsches Wort in die Zielsprache des aktiven
Profils zu übersetzen. Kein API-Key nötig - im Gegensatz zu ElevenLabs
(core/tts_client.py) gibt es hier also keine Zugangsdaten zu speichern.

translate_word() ist bewusst synchron (urllib ist ohnehin blockierend) -
der App-seitige Aufrufer kapselt das nötigenfalls selbst in
asyncio.to_thread(), damit die Oberfläche nicht einfriert.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

# Wiederverwendung der bereits gepflegten Sprachcode-Zuordnung aus
# tts_client.py, statt sie hier ein zweites Mal zu pflegen.
from core.tts_client import TTS_SPRACHCODES

_API_URL = "https://api.mymemory.translated.net/get"

# Weitere Treffer aus dem "matches"-Array der API werden auf diese Anzahl
# begrenzt, damit die Ergebnisliste in der Oberfläche nicht ausufert.
_MAX_ALTERNATIVEN = 5


class TranslateFehler(Exception):
    """Klartext-Fehler bei der Übersetzung (leere Eingabe, Netzwerk, API-Fehler)."""


@dataclass
class TranslationResult:
    """Ergebnis einer Übersetzung: Haupttreffer plus weitere zutreffende Übersetzungen."""

    primary: str
    alternatives: list[str] = field(default_factory=list)


def zielsprachcode(profile_language: str) -> str:
    """Ordnet die Profil-Zielsprache (z. B. 'Englisch Basis A1') einem
    ISO-639-1-Sprachcode für den MyMemory-langpair-Parameter zu."""
    return TTS_SPRACHCODES.get(profile_language, "en")


def translate_word(text: str, target_code: str) -> TranslationResult:
    """Übersetzt `text` von Deutsch in die Sprache `target_code` (z. B. 'en').

    Wirft TranslateFehler mit einer für die Oberfläche geeigneten Klartext-
    Meldung, statt die App abstürzen zu lassen - Aufrufer fangen das ab.
    """
    text = text.strip()
    if not text:
        raise TranslateFehler("Kein Wort eingegeben.")

    query = urllib.parse.urlencode({"q": text, "langpair": f"de|{target_code}"})
    anfrage = urllib.request.Request(f"{_API_URL}?{query}", method="GET")

    try:
        with urllib.request.urlopen(anfrage, timeout=10) as antwort:
            daten = json.loads(antwort.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise TranslateFehler(f"Übersetzungsdienst-Fehler ({e.code}).") from e
    except urllib.error.URLError as e:
        raise TranslateFehler(f"Netzwerkfehler: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise TranslateFehler("Übersetzungsdienst lieferte eine unlesbare Antwort.") from e

    primary = daten.get("responseData", {}).get("translatedText", "").strip()
    if not primary:
        raise TranslateFehler("Keine Übersetzung gefunden.")

    # Weitere Treffer aus dem Translation-Memory-Array einsammeln, dabei
    # Duplikate (case-insensitive, inkl. Duplikat zum Haupttreffer) entfernen
    # und nach Match-Qualität sortiert auf _MAX_ALTERNATIVEN begrenzen.
    gesehen = {primary.lower()}
    matches = sorted(
        daten.get("matches", []), key=lambda m: m.get("match", 0), reverse=True
    )
    alternativen: list[str] = []
    for match in matches:
        kandidat = match.get("translation", "").strip()
        if not kandidat or kandidat.lower() in gesehen:
            continue
        gesehen.add(kandidat.lower())
        alternativen.append(kandidat)
        if len(alternativen) >= _MAX_ALTERNATIVEN:
            break

    return TranslationResult(primary=primary, alternatives=alternativen)
