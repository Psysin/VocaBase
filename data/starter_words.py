"""data/starter_words.py

Dieses Modul lädt die Vokabel-Startpakete nicht mehr aus hardcodiertem Text,
sondern liest sie dynamisch aus CSV-Tabellen ein.
"""

import csv
import os
import pathlib

# __file__ ist der absolute Pfad zu dieser starter_words.py Datei.
# .parent geht einen Schritt zurück und gibt uns genau den Ordner "data".
DATA_DIR = pathlib.Path(__file__).parent

# Da wir nun wissen, wo der "data"-Ordner auf dem iPhone liegt,
# reichen hier die reinen Dateinamen ohne das "data/" davor.
PAKET_DATEIEN = {
    "Spanisch Basis A1": "spanisch_a1.csv",
    "Englisch Basis A1": "englisch_a1.csv",
    "Französisch Basis A1": "franzoesisch_a1.csv",
    "Italienisch Basis A1": "italienisch_a1.csv",
}

STARTER_PACKS: dict[str, list[tuple[str, str]]] = {}


# 2. DIE LADE-ROUTINE
def lade_alle_pakete():
    """Liest alle definierten CSV-Dateien ein und füllt STARTER_PACKS."""

    for paket_name, dateiname in PAKET_DATEIEN.items():
        paket_liste = []

        # Hier setzen wir den absoluten Pfad für iOS zusammen:
        # z.B. /var/mobile/Containers/.../App/data/spanisch_a1.csv
        dateipfad = DATA_DIR / dateiname

        # .exists() prüft, ob die Datei dort wirklich liegt
        if dateipfad.exists():
            with open(dateipfad, mode="r", encoding="utf-8") as datei:
                leser = csv.reader(datei, delimiter=",")
                next(leser, None)

                for zeile in leser:
                    if len(zeile) >= 2:
                        fremdwort = zeile[0].strip()
                        deutsch = zeile[1].strip()
                        paket_liste.append((deutsch, fremdwort))
        else:
            print(
                f"Hinweis: Datei {dateipfad} für das Paket '{paket_name}' wurde nicht gefunden."
            )

        # Wenn die Datei fertig gelesen ist, speichern wir die volle Liste im Dictionary ab
        STARTER_PACKS[paket_name] = paket_liste


# 3. AUSFÜHRUNG BEIM START
# Wenn 'starter_words.py' in der main.py geladen wird,
# soll die Lade-Funktion sofort einmal automatisch ausgeführt werden.
lade_alle_pakete()
