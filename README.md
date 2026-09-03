# 📚 Vokabeltrainer (Spaced Repetition App)

Ein moderner, plattformübergreifender Karteikarten- und Vokabeltrainer, entwickelt mit **Python 3** und dem UI-Framework **Flet**. Die Anwendung basiert auf dem bewährten **Leitner-Karteikastensystem** (Spaced Repetition) und bietet eine Mehrbenutzer-Verwaltung für unterschiedliche Lernende und Zielsprachen.

---

## 🚀 Kernfunktionen

* **Mehrbenutzer- & Mehrsprachen-Verwaltung:**
  * Dynamisches Anlegen und Löschen von Profilen direkt in der Benutzeroberfläche.
  * Individuelle Zielsprachen pro Profil (Englisch, Spanisch, Französisch, Italienisch).
  * Vordefinierte A1-Starter-Wortschätze (100+ Grundvokabeln bzw. 1500+ kuratierte Buchvokabeln) mit optionaler Startauswahl via Checkbox.
  * Vokabellisten wurde per CSV im /data Ordner abgelegt, der Zugriff auf die Vokabeln erfolgt über
  starter_words.py
  * Vokabeln liegen zusätzlich als Tabelle in Google Drive ab
  * Vollständig getrennte Vokabeldaten, Einstellungen und Lernstatistiken pro Nutzer.
* **Intelligenter Spaced-Repetition-Algorithmus (Leitner-System):**
  * Automatisches 5-Kästen-Intervallsystem (1, 3, 7, 14 und 30 Tage) zur nachhaltigen Langzeitverankerung.
  * Automatische Berechnung der nächsten Fälligkeit (`due_date`) im ISO-Format (`JJJJ-MM-TT`).
* **Interaktiver Übungs- & Daily-Quest-Modus:**
  * **Gewichteter Modus-Mix:**  100 % Schreib-Modus (Aktives Eintippen mit automatischer Prüfung).
  * **Fehlertoleranz beim Schreiben:** Bis zu 5 (variabel einstellbar) Versuche pro Vokabel. Erst nach dem letzten  Fehlversuch wird aufgelöst und die Karte auf Kasten 1 zurückgestuft.
  * **Daily Quest Portionierung:** Frei konfigurierbare Session-Größe (10, 20, 30, 50 oder 100 Vokabeln pro Durchgang), um große Vokabelmengen portionsweise zu bewältigen.
  * **Jederzeit abbrechbar:** Bereits geübte Wörter werden sofort persistent gespeichert.
  * Zähler für wöchentlich gemeisterte Lerneinheiten.
* **Vokabelverwaltung & Live-Suche:**
  * Durchsuchbare Listenansicht mit Schnellfilter beim Tippen.
  * Bearbeiten-Dialog für bestehende Einträge (Wortkorrekturen und manuelle Kastenanpassung).
  * Ein-Klick-Löschfunktion für einzelne Einträge.
  * Schnelle Erfassungsmaske mit automatischem Duplikatschutz.
* **Einstellungen & Design:**
  * Einstellungs-Dialog (Zahnrad-Menü) zur Anpassung der Daily-Quest-Größe.
  * Nahtlose Umschaltung zwischen Dark Mode und Light Mode pro Profil.
  * Anpassung der Fehlversuche zwischen 1 und 5
  * Mobil-optimiertes Layout mit Safe-Area-Padding für iOS.
  * Versions- und Entwicklerinformationen.

---

## 📐 Projekt- & Ordnerstruktur

Die Software folgt einer modularen Architektur mit klarer Trennung zwischen Datenmodell, Geschäftslogik, Persistenz und Benutzeroberfläche (*Separation of Concerns*):

```text
Vokabel_App/
│
├── core/                        # Kernmodelle & Anwendungslogik (Pure Python)
│   ├── models.py                # Klassen 'Word' und 'UserProfile' (inkl. Settings)
│   └── spaced_rep.py            # Leitner-Algorithmus, Intervalle & Duplikatsprüfung
│
├── data/                        # Datenhaltung, Persistenz & Stammdaten
│   ├── starter_words.py         # Kuratierte Startvokabelpakete nach Sprachen
│   └── storage.py               # JSON-Speicher- und Laderoutinen (app_data.json)
│
├── ui/                          # Grafische Benutzeroberfläche (Flet)
│   └── views/
│       ├── dashboard.py         # Startseite mit Statistiken, Daily Quest & Header
│       ├── practice.py          # Interaktive Übungsansicht (Lesen/Schreiben-Mix)
│       ├── add_word.py          # Formular zum Erfassen neuer Vokabeln
│       └── word_list.py         # Durchsuchbare & editierbare Vokabelliste
│
├── main.py                      # App-Einstiegspunkt, View-Manager & Dialogsteuerung
├── app_data.json                # Lokale JSON-Datenbank (automatisch generiert)
└── README.md                    # Technische Projektdokumentation
```

---

## 🧠 Der Spaced-Repetition-Algorithmus im Detail

Jedes Wort (`Word`) besitzt eine Kasten-Zugehörigkeit (`box`: 1–5) und ein Fälligkeitsdatum (`due_date` im ISO-Format `JJJJ-MM-TT`).

### Intervall-Konfiguration (`core/spaced_rep.py`)

| Kasten | Zeitabstand bis zur nächsten Abfrage | Lernziel |
| :--- | :--- | :--- |
| **Kasten 1** | 1 Tag | Tägliche Festigung & Neuerfassung |
| **Kasten 2** | 3 Tage | Kurzzeit-Wiederholung |
| **Kasten 3** | 7 Tage | Wöchentliche Festigung |
| **Kasten 4** | 14 Tage | Übergang ins Langzeitgedächtnis |
| **Kasten 5** | 30 Tage | Langzeit-Erhalt (Gemeistert) |

### Bewertungs-Dynamik

* **Richtig beantwortet (Schreiben / „Gewusst“):** Die Karte steigt einen Kasten auf (`box = min(box + 1, 5)`). Das neue Fälligkeitsdatum wird mit `date.today() + timedelta(days=intervall)` in die Zukunft gesetzt.
* **Wiederholen (Lesen):** Die Karte verbleibt im aktuellen Kasten und bleibt für den aktuellen Tag fällig.
* **Falsch beantwortet (nach diversen Fehlversuchen / „Nicht gewusst“):** Die Karte fällt sofort auf Kasten 1 zurück (`box = 1`) und muss ab morgen erneut geübt werden.

---

## 🛠 Installation & Lokaler Start

### 1. Repository klonen & Verzeichnis öffnen

```bash
git clone [https://github.com/Psysin/VocaBase.git](https://github.com/Psysin/VocaBase.git)
cd VocaBase
```

### 2. Virtuelle Umgebung erstellen und aktivieren

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. Abhängigkeiten installieren

```bash
pip install flet
```

### 4. Anwendung starten

```bash
# Desktop-Modus
python main.py

# Mobil- / Web-Server-Modus (für iOS / Test via Flet-App)
flet run --web -p 8550
```

---

## 🗺 Geplante Erweiterungen (GitHub Issues / Roadmap)

Folgende Module sind für zukünftige Releases vorgesehen:

* [ ] **Issue #1: Satzbausteine & Wort-Puzzle**
  * Interaktive Satzbau-Übungen: Zerlegung spanischer/englischer Sätze in Klick-Chips (`ft.Row`), die in korrekter syntaktischer Reihenfolge angeordnet werden müssen.
* [ ] **Issue #2: Grammatik- & Konjugationstrainer**
  * Gezieltes Training von Verbtabellen und Zeitformen (z. B. spanische Konjugationen *yo / tú / él / nosotros* für Verben auf *-ar*, *-er*, *-ir*).
* [ ] **Issue #3: Lückentext-Modus**
  * Übungen für typische Grammatik-Stolpersteine und Präpositionen (z. B. Unterscheidung *por* vs. *para* oder *ser* vs. *estar*) über Inline-Eingabefelder.

---

## 👤 Entwickler & Copyright

* **Entwickler:** Philipp Edelbrock
* **Version:** 1.0.1
* **Lizenz:** © 2026 Alle Rechte vorbehalten