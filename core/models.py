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
        self.id = id
        self.front = front  # Deutsches Wort (z. B. "Tisch")
        self.back = back  # Fremdwort (z. B. "table" oder "mesa")
        self.box = box  # Aktueller Kasten (1 bis 5)
        # Wenn kein Datum übergeben wird, ist das Wort ab heute fällig
        self.due_date = str(date.today()) if due_date is None else due_date

    def to_dict(self) -> dict:
        """Wandelt das Word-Objekt in ein Dictionary um (für die JSON-Speicherung)."""
        return {
            "id": self.id,
            "front": self.front,
            "back": self.back,
            "box": self.box,
            "due_date": self.due_date,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Erzeugt ein Word-Objekt aus einem Dictionary (beim Laden aus der JSON-Datei)."""
        return cls(
            id=data["id"],
            front=data["front"],
            back=data["back"],
            box=data.get("box", 1),
            due_date=data.get("due_date", str(date.today())),
        )

    def __str__(self) -> str:
        return (
            f"{self.front} -> {self.back} (Kasten {self.box}, Fällig: {self.due_date})"
        )


class UserProfile:
    """Verwaltet das Lernprofil eines Nutzers inklusive Statistiken und Einstellungen."""

    def __init__(
        self,
        name: str,
        language: str,
        weekly_sessions: int = 0,
        daily_quest_size: int = 30,  # Anzahl der Wörter pro Daily Quest
        dark_mode: bool = True,  # Design-Einstellung: Dunkel (True) / Hell (False)
        words: list[Word] | None = None,
        max_attempts: int = 3,
    ):
        self.name = name
        self.language = language
        self.weekly_sessions = weekly_sessions
        self.daily_quest_size = daily_quest_size
        self.dark_mode = dark_mode
        # Startet mit einer leeren Liste, falls keine Vokabelliste übergeben wurde
        self.words: list[Word] = [] if words is None else words
        self.max_attempts = max_attempts

    def to_dict(self) -> dict:
        """Wandelt das gesamte Profil inklusive Einstellungen und Vokabeln in ein Dictionary um."""
        return {
            "name": self.name,
            "language": self.language,
            "weekly_sessions": self.weekly_sessions,
            "daily_quest_size": self.daily_quest_size,
            "dark_mode": self.dark_mode,
            # Wandelt jedes enthaltene Word-Objekt rekursiv in ein Dictionary um
            "words": [word.to_dict() for word in self.words],
            "max_attempts": self.max_attempts,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Baut das UserProfile samt aller Einstellungen und Word-Objekte aus einem Dictionary auf."""
        # 1. Alle Roh-Wörter aus der JSON-Liste in echte Word-Objekte umwandeln
        words_list = [Word.from_dict(w) for w in data.get("words", [])]

        # 2. Profil instanziieren – data.get(key, fallback) stellt sicher,
        # dass ältere JSON-Dateien ohne diese Schlüssel automatisch Standardwerte nutzen
        return cls(
            name=data["name"],
            language=data["language"],
            weekly_sessions=data.get("weekly_sessions", 0),
            daily_quest_size=data.get("daily_quest_size", 30),
            dark_mode=data.get("dark_mode", True),
            words=words_list,
            max_attempts=data.get("max_attempts", 3),
        )

    def __str__(self) -> str:
        return (
            f"Profil '{self.name}' | Sprache: {self.language} | "
            f"Vokabeln: {len(self.words)} | Quest: {self.daily_quest_size} Wörter | "
            f"Dark Mode: {self.dark_mode}"
        )
