"""core/models.py

Dieses Modul definiert das logische Datenmodell der Anwendung.
Es bildet Karteikarten (Word) und Benutzerkonten (UserProfile)
als eigenständige Python-Objekte ab.
"""

from datetime import date


class Word:
    """Repräsentiert eine einzelne Vokabelkarteikarte nach dem Leitner-System."""

    def __init__(
        self,
        id: int,
        front: str,
        back: str,
        box: int = 1,
        due_date: str | None = None,
    ):
        """Initialisiert eine neue Karteikarte."""
        self.id = id
        self.front = front
        self.back = back
        self.box = box

        # Fallback: Wenn kein Datum übergeben wird, ist die Karte ab heute fällig.
        # Wichtig: Wir speichern das Datum bewusst als Text (String) im Format 'JJJJ-MM-TT',
        # da sich Strings später extrem einfach in JSON-Dateien abspeichern lassen.
        self.due_date = str(date.today()) if due_date is None else due_date

    def to_dict(self) -> dict:
        """Wandelt das Python-Objekt in ein Dictionary um (für die JSON-Speicherung)."""
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "box": self.box,
            "due_date": self.due_date,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Baut ein neues Word-Objekt aus einem Dictionary auf (beim Laden aus JSON).

        Der Einsatz von data.get("key", standardwert) verhindert Programmabstürze,
        falls in einer alten Speicherdatei mal ein Schlüssel fehlen sollte.
        """
        return cls(
            id=data["id"],
            front=data["front"],
            back=data["back"],
            box=data.get("box", 1),
            due_date=data.get("due_date", str(date.today())),
        )

    def __str__(self) -> str:
        """Definiert, wie das Wort in der Konsole angezeigt wird, wenn man print(wort) nutzt."""
        return (
            f"{self.front} -> {self.back} (Kasten {self.box}, Fällig: {self.due_date})"
        )


class UserProfile:
    """Verwaltet das Lernprofil eines Nutzers (Einstellungen, Statistiken, Vokabeln)."""

    def __init__(
        self,
        name: str,
        language: str,
        weekly_sessions: int = 0,
        daily_quest_size: int = 30,
        dark_mode: bool = True,
        words: list[Word] | None = None,
        max_attempts: int = 3,
    ):
        self.name = name
        self.language = language
        self.weekly_sessions = weekly_sessions
        self.daily_quest_size = daily_quest_size
        self.dark_mode = dark_mode
        self.max_attempts = max_attempts

        # Wenn keine Wörter übergeben werden, starte mit einer leeren Liste.
        # Dies verhindert den berüchtigten "Mutable Default Argument"-Fehler in Python,
        # bei dem sich sonst alle Profile dieselbe Liste teilen würden.
        self.words: list[Word] = [] if words is None else words

    def to_dict(self) -> dict:
        """Verpackt das Profil und rekursiv alle enthaltenen Wörter in ein Dictionary."""
        return {
            "name": self.name,
            "language": self.language,
            "weekly_sessions": self.weekly_sessions,
            "daily_quest_size": self.daily_quest_size,
            "dark_mode": self.dark_mode,
            "max_attempts": self.max_attempts,
            # Hier greift eine 'List Comprehension': Sie ruft to_dict() für jedes einzelne Wort auf
            "words": [word.to_dict() for word in self.words],
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Baut das Profil aus den JSON-Daten wieder auf."""
        # Baut zuerst die Liste der Word-Objekte wieder zusammen
        words_list = [Word.from_dict(w) for w in data.get("words", [])]

        return cls(
            name=data["name"],
            language=data["language"],
            weekly_sessions=data.get("weekly_sessions", 0),
            daily_quest_size=data.get("daily_quest_size", 30),
            dark_mode=data.get("dark_mode", True),
            max_attempts=data.get("max_attempts", 3),
            words=words_list,
        )

    def __str__(self) -> str:
        return (
            f"Profil '{self.name}' | Sprache: {self.language} | "
            f"Vokabeln: {len(self.words)} | Quest: {self.daily_quest_size} Wörter | "
            f"Versuche: {self.max_attempts} | Dark Mode: {self.dark_mode}"
        )
