from datetime import date, timedelta
from core.models import Word

# Zeitabstände pro Kasten in Tagen
BOX_INTERVALS = {
    1: 1,
    2: 3,
    3: 7,
    4: 14,
    5: 30,
}


def word_exists(words: list[Word], foreign_word: str) -> bool:
    """Prüft, ob ein Fremdwort bereits in der Vokabelliste des Nutzers existiert.

    Ignoriert Groß-/Kleinschreibung und überflüssige Leerzeichen.
    """
    clean_search_word = foreign_word.strip().lower()

    for word in words:
        if word.back.strip().lower() == clean_search_word:
            return True  # Duplikat gefunden

    return False


def get_due_words(words: list[Word]) -> list[Word]:
    """Gibt alle Vokabeln zurück, die heute oder früher zur Wiederholung fällig sind."""
    heute = str(date.today())

    return [word for word in words if word.due_date <= heute]


def review_word(word: Word, rating: str) -> None:
    """Aktualisiert Kasten und Fälligkeit einer Vokabel basierend auf der Bewertung.

    Erlaubte Werte für rating: 'gewusst', 'wiederholen', 'nicht_gewusst'
    """
    heute = date.today()

    if rating == "gewusst":
        # Steigt einen Kasten auf (maximal Kasten 5)
        word.box = min(word.box + 1, 5)
        tage_pause = BOX_INTERVALS[word.box]
        word.due_date = str(heute + timedelta(days=tage_pause))

    elif rating == "wiederholen":
        # Bleibt im Kasten, bleibt heute fällig für die aktuelle Session
        word.due_date = str(heute)

    elif rating == "nicht_gewusst":
        # Fällt zurück in Kasten 1, bleibt heute fällig
        word.box = 1
        word.due_date = str(heute)
