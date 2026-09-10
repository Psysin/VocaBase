"""core/tts_client.py

Bindet ElevenLabs' Text-to-Speech-API an, um Aussprache für Vokabeln zu
erzeugen, die noch nicht im mit der App ausgelieferten Audio-Bestand
enthalten sind (typischerweise selbst hinzugefügte Vokabeln).

Wird von zwei Stellen genutzt:
- main.py (sprachdaten_laden): live vom Handy aus, für einzelne fehlende
  Vokabeln des aktiven Profils.
- scripts/generate_audio.py (--backend elevenlabs): am Mac, um den
  kompletten Basisbestand einmalig neu zu erzeugen (pro Sprache eine
  eigene Stimme, siehe TTS_SPRACHCODES/voice_ids in tts_config.json).

synthesize() ist bewusst synchron (urllib ist ohnehin blockierend) -
der App-seitige Aufrufer kapselt das nötigenfalls selbst in
asyncio.to_thread(), damit die Oberfläche nicht einfriert.
"""

import json
import pathlib
import urllib.error
import urllib.request

from data.storage import DOCUMENTS_DIR

TTS_CONFIG_DATEI = DOCUMENTS_DIR / "tts_config.json"

# ISO-639-1-Sprachcode je Sprachpaket, für ElevenLabs' language_code-Parameter.
TTS_SPRACHCODES: dict[str, str] = {
    "Englisch Basis A1": "en",
    "Spanisch Basis A1": "es",
}

# Fest gewählte Stimmen (keine Geheimnisse, im Gegensatz zum API-Key) -
# dienen als Vorbelegung, solange auf einem Gerät noch nichts gespeichert
# wurde, damit z. B. Nadine nicht selbst danach suchen muss.
_VOICE_ID_STANDARDWERTE: dict[str, str] = {
    "Englisch Basis A1": "kdmDKE6EkgrWrrykO9Qt",
    "Spanisch Basis A1": "1CeqBeXMOqCleeQjfYfO",
}

_API_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
_MODELL = "eleven_multilingual_v2"


class TTSFehler(Exception):
    """Klartext-Fehler bei der Sprachsynthese (kein Key, Netzwerk, API-Fehler)."""


def load_tts_config() -> dict:
    """Lädt die ElevenLabs-Zugangsdaten (API-Key + eine Voice-ID pro Sprache),
    falls vorhanden.

    Liegt App-weit in DOCUMENTS_DIR, nicht pro Profil - es handelt sich um
    ein Konto-Geheimnis, nicht um Lerndaten wie app_data.json. Pro Sprache
    eine eigene Stimme (statt einer gemeinsamen), da eine auf eine Sprache
    trainierte Stimme in der jeweils anderen leicht akzentbehaftet klingen
    kann - siehe Absprache mit dem Nutzer.
    """
    standard = {"api_key": "", "voice_ids": dict(_VOICE_ID_STANDARDWERTE)}
    if not TTS_CONFIG_DATEI.exists():
        return standard

    try:
        with open(TTS_CONFIG_DATEI, "r", encoding="utf-8") as datei:
            daten = json.load(datei)
            gespeicherte_ids = daten.get("voice_ids", {})
            return {
                "api_key": daten.get("api_key", ""),
                "voice_ids": {
                    # or-Fallback statt nur .get(): auch ein leer gespeichertes
                    # Feld (z. B. versehentlich geleert) bekommt wieder die
                    # feste Standard-Stimme, nicht dauerhaft "".
                    sprache: gespeicherte_ids.get(sprache) or _VOICE_ID_STANDARDWERTE[sprache]
                    for sprache in TTS_SPRACHCODES
                },
            }
    except (json.JSONDecodeError, OSError):
        return standard


def save_tts_config(api_key: str, voice_ids: dict[str, str]) -> None:
    """Speichert die ElevenLabs-Zugangsdaten (API-Key + Voice-ID je Sprache)."""
    with open(TTS_CONFIG_DATEI, "w", encoding="utf-8") as datei:
        json.dump({"api_key": api_key, "voice_ids": voice_ids}, datei)


def synthesize(text: str, language: str, api_key: str, voice_id: str) -> bytes:
    """Erzeugt Aussprache-Audio (MP3-Bytes) über die ElevenLabs-API.

    Wirft TTSFehler mit einer für die Oberfläche geeigneten Klartext-
    Meldung, statt die App abstürzen zu lassen - Aufrufer fangen das ab.
    """
    if not api_key or not voice_id:
        raise TTSFehler("Kein ElevenLabs API-Key/Voice-ID hinterlegt.")

    sprachcode = TTS_SPRACHCODES.get(language)
    body = json.dumps(
        {
            "text": text,
            "model_id": _MODELL,
            **({"language_code": sprachcode} if sprachcode else {}),
        }
    ).encode("utf-8")

    anfrage = urllib.request.Request(
        _API_URL.format(voice_id=voice_id),
        data=body,
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(anfrage, timeout=30) as antwort:
            return antwort.read()
    except urllib.error.HTTPError as e:
        fehlertext = e.read().decode("utf-8", errors="replace")
        raise TTSFehler(f"ElevenLabs-Fehler ({e.code}): {fehlertext[:200]}") from e
    except urllib.error.URLError as e:
        raise TTSFehler(f"Netzwerkfehler: {e.reason}") from e
