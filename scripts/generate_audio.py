"""scripts/generate_audio.py

Entwickler-Tool (läuft NIE auf dem Handy): erzeugt am Mac für jedes Wort
eines Sprachpakets eine kleine Audiodatei und schreibt anschließend das
Manifest, das core/audio.py zur Laufzeit liest. Idempotent - vorhandene
Dateien werden übersprungen, das Skript kann also nach Änderungen an der
CSV einfach erneut laufen.

Zwei Backends:
- elevenlabs (Standard): ruft core.tts_client.synthesize() auf, erzeugt
  .mp3-Dateien mit einer festen, gewählten Stimme (Voice-ID) - so wird
  der komplette App-weite Aussprache-Bestand erzeugt. Braucht den API-Key
  in der Umgebungsvariable ELEVENLABS_API_KEY (bewusst NICHT als
  Kommandozeilenargument, damit er nicht in der Shell-History landet)
  sowie --voice-id.
- say: macOS-Systemstimme (Samantha/Mónica), erzeugt .m4a-Dateien, kein
  API-Key/Internet nötig - Altlast aus der ersten Version dieser Datei,
  bevor auf ElevenLabs für eine einheitliche Stimme pro Sprache
  umgestellt wurde. `say` kann kein MP3 erzeugen, daher eine andere
  Dateiendung als der elevenlabs-Pfad.

Sprachen und ihre Audio-Ordner/Manifeste kommen aus core.audio.
SPRACH_AUDIO_KONFIG, die CSV-Dateinamen aus data.starter_words.
PAKET_DATEIEN - eine neue Sprache muss also nur dort einmal ergänzt
werden, nicht in diesem Skript.

Aufruf:
    export ELEVENLABS_API_KEY="sk_..."
    python3 scripts/generate_audio.py "Englisch Basis A1" --voice-id kdmDKE6EkgrWrrykO9Qt
    python3 scripts/generate_audio.py "Spanisch Basis A1" --voice-id 1CeqBeXMOqCleeQjfYfO --only "hola,adiós"
    python3 scripts/generate_audio.py "Englisch Basis A1" --backend say
"""

import argparse
import csv
import json
import os
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"

sys.path.insert(0, str(REPO_ROOT))
from core.audio import SPRACH_AUDIO_KONFIG, slugify_word  # noqa: E402
from core.tts_client import TTSFehler, synthesize  # noqa: E402
from data.starter_words import PAKET_DATEIEN  # noqa: E402

# macOS-Stimme je Sprachpaket, nur für --backend say relevant (per
# `say -v '?'` geprüfte, "normale" Standardstimmen).
SAY_STIMMEN: dict[str, str] = {
    "Englisch Basis A1": "Samantha",
    "Spanisch Basis A1": "Mónica",
}

DATEIENDUNG: dict[str, str] = {"elevenlabs": "mp3", "say": "m4a"}


def lade_eindeutige_woerter(csv_datei: pathlib.Path) -> list[str]:
    """Liest die erste Spalte (Zielsprache) der CSV und gibt eindeutige
    Wörter zurück (Reihenfolge wie im ersten Auftreten)."""
    gesehen: set[str] = set()
    woerter: list[str] = []

    with open(csv_datei, "r", encoding="utf-8") as datei:
        leser = csv.reader(datei, delimiter=",")
        next(leser, None)  # Kopfzeile überspringen

        for zeile in leser:
            if len(zeile) >= 1:
                wort = zeile[0].strip()
                if wort and wort.lower() not in gesehen:
                    gesehen.add(wort.lower())
                    woerter.append(wort)

    return woerter


def pruefe_slug_kollisionen(woerter: list[str]) -> None:
    """Bricht laut ab, falls zwei unterschiedliche Wörter innerhalb der
    Sprache denselben Dateinamen ergeben würden."""
    slug_zu_wort: dict[str, str] = {}

    for wort in woerter:
        slug = slugify_word(wort)
        if slug in slug_zu_wort and slug_zu_wort[slug].lower() != wort.lower():
            print(
                f"FEHLER: Slug-Kollision '{slug}' zwischen "
                f"'{slug_zu_wort[slug]}' und '{wort}'. Abbruch.",
                file=sys.stderr,
            )
            sys.exit(1)
        slug_zu_wort[slug] = wort


def generiere_mit_say(wort: str, sprache: str, ziel: pathlib.Path) -> None:
    subprocess.run(["say", "-v", SAY_STIMMEN[sprache], "-o", str(ziel), wort], check=True)


def generiere_mit_elevenlabs(
    wort: str, sprache: str, ziel: pathlib.Path, api_key: str, voice_id: str
) -> None:
    audio_bytes = synthesize(wort, sprache, api_key, voice_id)
    with open(ziel, "wb") as datei:
        datei.write(audio_bytes)


def main():
    parser = argparse.ArgumentParser(description="Erzeugt Aussprache-Audio für ein Sprachpaket.")
    parser.add_argument(
        "sprache", choices=sorted(SPRACH_AUDIO_KONFIG.keys()), help="z. B. 'Spanisch Basis A1'"
    )
    parser.add_argument(
        "--backend", choices=["elevenlabs", "say"], default="elevenlabs"
    )
    parser.add_argument(
        "--voice-id", help="ElevenLabs Voice-ID (nur bei --backend elevenlabs nötig)"
    )
    parser.add_argument(
        "--only",
        help="Kommagetrennte Liste von Wörtern für einen kleinen Testlauf "
        "(statt aller Wörter aus der CSV).",
    )
    args = parser.parse_args()

    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    if args.backend == "elevenlabs":
        if not api_key:
            print("FEHLER: ELEVENLABS_API_KEY ist nicht gesetzt.", file=sys.stderr)
            sys.exit(1)
        if not args.voice_id:
            print("FEHLER: --voice-id ist bei --backend elevenlabs erforderlich.", file=sys.stderr)
            sys.exit(1)

    konfig = SPRACH_AUDIO_KONFIG[args.sprache]
    endung = DATEIENDUNG[args.backend]
    csv_datei = DATA_DIR / PAKET_DATEIEN[args.sprache]
    audio_ordner = DATA_DIR / konfig["ordner"]
    manifest_datei = DATA_DIR / konfig["manifest"]

    alle_woerter = lade_eindeutige_woerter(csv_datei)
    pruefe_slug_kollisionen(alle_woerter)

    if args.only:
        gewuenscht = {w.strip().lower() for w in args.only.split(",")}
        woerter = [w for w in alle_woerter if w.lower() in gewuenscht]
        fehlend = gewuenscht - {w.lower() for w in woerter}
        if fehlend:
            print(f"Hinweis: nicht in der CSV gefunden, übersprungen: {fehlend}")
    else:
        woerter = alle_woerter

    audio_ordner.mkdir(parents=True, exist_ok=True)

    neu = 0
    uebersprungen = 0
    fehlgeschlagen: list[str] = []
    for index, wort in enumerate(woerter, start=1):
        ziel = audio_ordner / f"{slugify_word(wort)}.{endung}"
        if ziel.exists():
            uebersprungen += 1
            continue

        try:
            if args.backend == "elevenlabs":
                generiere_mit_elevenlabs(wort, args.sprache, ziel, api_key, args.voice_id)
            else:
                generiere_mit_say(wort, args.sprache, ziel)
            neu += 1
        except (TTSFehler, subprocess.CalledProcessError) as fehler:
            print(f"  Fehlgeschlagen ({wort!r}): {fehler}", file=sys.stderr)
            fehlgeschlagen.append(wort)
            continue

        if neu % 50 == 0:
            print(f"  ... {index}/{len(woerter)} verarbeitet")

    # Manifest immer aus ALLEN aktuell tatsächlich vorhandenen Audiodateien
    # aufbauen (nicht nur aus diesem Lauf), damit --only-Testläufe das
    # Manifest nicht verkleinern.
    vorhandene_woerter = sorted(
        wort for wort in alle_woerter if (audio_ordner / f"{slugify_word(wort)}.{endung}").exists()
    )
    with open(manifest_datei, "w", encoding="utf-8") as datei:
        json.dump(vorhandene_woerter, datei, ensure_ascii=False, indent=2)

    print(
        f"Fertig ({args.sprache}, Backend {args.backend}): {neu} neu erzeugt, "
        f"{uebersprungen} bereits vorhanden, {len(fehlgeschlagen)} fehlgeschlagen, "
        f"{len(vorhandene_woerter)} insgesamt im Manifest "
        f"(von {len(alle_woerter)} eindeutigen Wörtern in der CSV)."
    )
    if fehlgeschlagen:
        print(f"Fehlgeschlagene Wörter (--only=\"{','.join(fehlgeschlagen)}\" zum Nachholen):")


if __name__ == "__main__":
    main()
