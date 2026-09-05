"""core/logic.py

Dieses Modul bündelt die eigenständige Anwendungslogik.
Es steuert das Leitner-Lernsystem und kümmert sich um die Suche in Vokabellisten.
"""

import random
from datetime import date, timedelta
from core.models import Word

# Ein Dictionary für die Intervalle ist viel eleganter als eine lange if-elif-Kette.
# Die Zahlen repräsentieren die Tage, die ein Wort pausiert, wenn es gewusst wurde.
BOX_INTERVALS = {
    1: 1,  # Kasten 1: Morgen wiederholen
    2: 3,  # Kasten 2: In 3 Tagen
    3: 7,  # Kasten 3: In einer Woche
    4: 14,  # Kasten 4: In zwei Wochen
    5: 30,  # Kasten 5: In einem Monat
}


def word_exists(words: list[Word], foreign_word: str) -> bool:
    """Prüft, ob ein Fremdwort bereits in der Vokabelliste des Nutzers existiert.

    Nutzt .strip() (entfernt Leerzeichen) und .lower() (alles klein),
    damit "Haus " und "haus" als Duplikat erkannt werden.
    """
    clean_search_word = foreign_word.strip().lower()

    for word in words:
        if word.back.strip().lower() == clean_search_word:
            return True  # Duplikat gefunden, Suche sofort abbrechen

    return False


def get_due_words(words: list[Word]) -> list[Word]:
    """Sammelt alle Vokabeln ein, die heute oder früher zur Wiederholung fällig sind."""
    heute = str(date.today())

    # Nutzt eine List Comprehension, um die Liste in einer Zeile zu filtern.
    # Da das Datum als ISO-String (JJJJ-MM-TT) formatiert ist, funktioniert
    # der einfache lexikografische String-Vergleich (<=) perfekt!
    return [word for word in words if word.due_date <= heute]


def build_practice_session(words: list[Word], size: int) -> list[Word]:
    """Stellt eine Übungs-Session zusammen, damit immer beliebig oft geübt werden kann.

    Zuerst werden alle fälligen Karten genommen. Reichen die nicht für die
    gewünschte Durchgangsgröße, wird mit zufälligen weiteren (noch nicht
    fälligen) Vokabeln aus dem Gesamtpool aufgefüllt. Am Ende wird gemischt,
    damit die Abfragereihenfolge nicht vorhersehbar ist.
    """
    session = get_due_words(words)

    if len(session) < size:
        due_ids = {word.id for word in session}
        extra_pool = [word for word in words if word.id not in due_ids]
        random.shuffle(extra_pool)
        session = session + extra_pool[: size - len(session)]

    random.shuffle(session)
    return session[:size]


def review_word(word: Word, rating: str) -> None:
    """Aktualisiert Kasten und Fälligkeit einer Vokabel basierend auf der Bewertung.

    :param word: Das zu aktualisierende Word-Objekt
    :param rating: 'gewusst', 'wiederholen' oder 'nicht_gewusst'
    """
    heute = date.today()

    if rating == "gewusst":
        # min() ist hier extrem elegant: Es stellt sicher, dass der Kasten
        # niemals über 5 hinausgeht, egal wie oft die Karte gewusst wird.
        word.box = min(word.box + 1, 5)

        # Holt die nötigen Pausen-Tage aus unserem Dictionary oben
        tage_pause = BOX_INTERVALS[word.box]

        # Berechnet das Zieldatum mit timedelta und wandelt es zurück in einen String
        word.due_date = str(heute + timedelta(days=tage_pause))

    elif rating == "wiederholen":
        # 'Wiederholen' (z. B. Tippfehler) ändert den Kasten nicht,
        # aber die Karte wird auf heute gesetzt, damit sie in der laufenden Session bleibt.
        word.due_date = str(heute)

    elif rating == "nicht_gewusst":
        # Strafe: Komplett zurück auf Anfang, sofort wieder fällig
        word.box = 1
        word.due_date = str(heute)
