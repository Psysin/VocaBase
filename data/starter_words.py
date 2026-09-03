"""data/starter_words.py

Dieses Modul lädt die Vokabel-Startpakete nicht mehr aus hardcodiertem Text,
sondern liest sie dynamisch aus CSV-Tabellen ein.
"""

import csv
import os

# 1. DAS INHALTSVERZEICHNIS
# Hier definieren wir, wie die Pakete in der App heißen sollen (z. B. im Dropdown)
# und wo die dazugehörige CSV-Datei liegt. 
# Wenn du später "Englisch B1" hinzufügst, trägst du es einfach hier als neue Zeile ein!
PAKET_DATEIEN = {
    "Spanisch Basis A1": "data/spanisch_a1.csv",
    "Englisch Basis A1": "data/englisch_a1.csv",
    "Französisch Basis A1": "data/franzoesisch_a1.csv",
    "Italienisch Basis A1": "data/italienisch_a1.csv",
}

# Dieses Dictionary füllen wir gleich mit Leben. Die App greift später darauf zu.
STARTER_PACKS: dict[str, list[tuple[str, str]]] = {}


# 2. DIE LADE-ROUTINE
def lade_alle_pakete():
    """Liest alle definierten CSV-Dateien ein und füllt STARTER_PACKS."""
    
    # Wir gehen jedes Paket aus unserem Inhaltsverzeichnis oben durch
    for paket_name, dateipfad in PAKET_DATEIEN.items():
        paket_liste = []
        
        # Sicherheits-Check: Gibt es die CSV-Datei überhaupt in diesem Ordner?
        if os.path.exists(dateipfad):
            
            # with open(...) öffnet die Datei sicher und schließt sie danach wieder.
            # 'r' steht für read (lesen). encoding='utf-8' sorgt dafür, 
            # dass Umlaute wie 'ä' oder 'ñ' richtig dargestellt werden.
            with open(dateipfad, mode='r', encoding='utf-8') as datei:
                
                # Der csv.reader hilft uns, die Datei zeilenweise als Liste zu lesen.
                # Wir geben an, dass das Komma das Trennzeichen ist.
                leser = csv.reader(datei, delimiter=',')
                
                # Jede Tabelle hat eine Kopfzeile ("Spanisch", "Deutsch", "Kategorie").
                # Diese wollen wir nicht als Vokabel laden. Mit next() springen
                # wir einfach über die erste Zeile hinweg.
                next(leser, None)
                
                # Nun gehen wir die restlichen echten Vokabel-Zeilen durch
                for zeile in leser:
                    
                    # Eine Zeile sieht nun z.B. so aus: ["hello", "hallo", "Begrüßung"]
                    # Wir prüfen, ob die Zeile mindestens 2 Spalten hat (Sicherheits-Check)
                    if len(zeile) >= 2:
                        # strip() entfernt unsichtbare Leerzeichen am Anfang und Ende
                        fremdwort = zeile[0].strip()
                        deutsch = zeile[1].strip()
                        
                        # Wir fügen das Wortpaar als Tupel (Deutsch, Fremdwort) in unsere 
                        # Liste ein, genau so, wie VocaBase es bisher erwartet.
                        paket_liste.append((deutsch, fremdwort))
        else:
            # Falls du vergessen hast, eine Datei in den Ordner zu legen, 
            # meldet sich Python hier, anstatt abzustürzen.
            print(f"Hinweis: Datei {dateipfad} für das Paket '{paket_name}' wurde nicht gefunden.")
        
        # Wenn die Datei fertig gelesen ist, speichern wir die volle Liste im Dictionary ab
        STARTER_PACKS[paket_name] = paket_liste


# 3. AUSFÜHRUNG BEIM START
# Wenn 'starter_words.py' in der main.py geladen wird, 
# soll die Lade-Funktion sofort einmal automatisch ausgeführt werden.
lade_alle_pakete()