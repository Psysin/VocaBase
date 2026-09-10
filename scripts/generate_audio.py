"""scripts/generate_audio.py

Entwickler-Tool (läuft NIE auf dem Handy): erzeugt am Mac per macOS "say"
für jedes Wort eines Sprachpakets eine kleine .m4a-Datei und schreibt
anschließend das Manifest, das core/audio.py zur Laufzeit liest.
Idempotent - vorhandene Dateien werden übersprungen, das Skript kann
also nach Änderungen an der CSV einfach erneut laufen.

Sprachen und ihre Audio-Ordner/Manifeste kommen aus core.audio.
SPRACH_AUDIO_KONFIG, die CSV-Dateinamen aus data.starter_words.
PAKET_DATEIEN - eine neue Sprache muss also nur dort einmal ergänzt
werden, nicht in diesem Skript.

Aufruf:
    python3 scripts/generate_audio.py "Englisch Basis A1"
    python3 scripts/generate_audio.py "Spanisch Basis A1" --only "hola,adiós"
"""

import argparse
import csv
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "data"

sys.path.insert(0, str(REPO_ROOT))
from core.audio import SPRACH_AUDIO_KONFIG, slugify_word  # noqa: E402
from data.starter_words import PAKET_DATEIEN  # noqa: E402

# macOS-Stimme je Sprachpaket (per `say -v '?'` geprüfte, "normale"
# Standardstimmen - keine Effekt-/Novelty-Stimmen wie Grandma/Rocko).
STIMMEN: dict[str, str] = {
    "Englisch Basis A1": "Samantha",
    "Spanisch Basis A1": "Mónica",
}


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


def generiere_audio(wort: str, stimme: str, audio_ordner: pathlib.Path) -> None:
    """Erzeugt (falls nicht vorhanden) die .m4a-Datei für ein Wort."""
    ziel = audio_ordner / f"{slugify_word(wort)}.m4a"
    if ziel.exists():
        return

    audio_ordner.mkdir(parents=True, exist_ok=True)
    # Bewusst OHNE --data-format=aac: bei den hier typischen sehr kurzen
    # Einzelwort-Clips ist unkomprimiertes PCM tatsächlich kleiner als AAC
    # (der AAC-Container-Overhead überwiegt bei so kurzer Dauer den
    # Kompressionsgewinn - gemessen: ~76 MB AAC vs. ~66 MB PCM fürs
    # komplette Set). PCM-in-.m4a spielt in der App einwandfrei (bereits
    # auf echtem iPhone getestet), lässt sich am Mac nur nicht per
    # Doppelklick öffnen - das betrifft nur die Entwicklung, nicht die App.
    subprocess.run(["say", "-v", stimme, "-o", str(ziel), wort], check=True)


def main():
    parser = argparse.ArgumentParser(description="Erzeugt Aussprache-Audio für ein Sprachpaket.")
    parser.add_argument(
        "sprache", choices=sorted(SPRACH_AUDIO_KONFIG.keys()), help="z. B. 'Spanisch Basis A1'"
    )
    parser.add_argument(
        "--only",
        help="Kommagetrennte Liste von Wörtern für einen kleinen Testlauf "
        "(statt aller Wörter aus der CSV).",
    )
    args = parser.parse_args()

    konfig = SPRACH_AUDIO_KONFIG[args.sprache]
    stimme = STIMMEN[args.sprache]
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

    neu = 0
    uebersprungen = 0
    for wort in woerter:
        war_da = (audio_ordner / f"{slugify_word(wort)}.m4a").exists()
        generiere_audio(wort, stimme, audio_ordner)
        if war_da:
            uebersprungen += 1
        else:
            neu += 1

    # Manifest immer aus ALLEN aktuell tatsächlich vorhandenen Audiodateien
    # aufbauen (nicht nur aus diesem Lauf), damit --only-Testläufe das
    # Manifest nicht verkleinern.
    vorhandene_woerter = sorted(
        wort for wort in alle_woerter if (audio_ordner / f"{slugify_word(wort)}.m4a").exists()
    )
    with open(manifest_datei, "w", encoding="utf-8") as datei:
        json.dump(vorhandene_woerter, datei, ensure_ascii=False, indent=2)

    print(
        f"Fertig ({args.sprache}): {neu} neu erzeugt, {uebersprungen} bereits vorhanden, "
        f"{len(vorhandene_woerter)} insgesamt im Manifest "
        f"(von {len(alle_woerter)} eindeutigen Wörtern in der CSV)."
    )


if __name__ == "__main__":
    main()
