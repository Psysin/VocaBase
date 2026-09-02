import flet as ft
from core.models import UserProfile, Word
from core.spaced_rep import word_exists
from data.storage import save_app_data


class AddWordView(ft.Container):
    """Eingabemaske zum Hinzufügen neuer Vokabeln mit Duplikatsprüfung."""

    def __init__(self, profile: UserProfile, all_profiles: list[UserProfile], on_back):
        super().__init__()
        self.profile = profile
        self.all_profiles = all_profiles
        self.on_back = on_back

        # 1. Eingabefelder
        self.front_input = ft.TextField(
            label="Deutsches Wort / Frage",
            hint_text="z. B. Buch",
            width=320,
            autofocus=True,
        )

        self.back_input = ft.TextField(
            label=f"Übersetzung ({self.profile.language})",
            hint_text="z. B. book",
            width=320,
        )

        # 2. Rückmeldetext für Fehler oder Erfolg
        self.message_text = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

        # 3. Buttons
        self.save_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SAVE),
                    ft.Text("Vokabel speichern"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=self.handle_save,
        )

        self.back_btn = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ARROW_BACK),
                    ft.Text("Zurück zum Hauptmenü"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=lambda e: self.on_back(),
        )

        # 4. Layout-Zusammenstellung
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Text(
                    f"Neue Vokabel ({self.profile.language})",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                self.front_input,
                self.back_input,
                self.message_text,
                self.save_btn,
                self.back_btn,
            ],
        )

    def handle_save(self, e):
        """Validiert die Eingaben, prüft auf Duplikate und speichert die Vokabel."""
        front = self.front_input.value.strip()
        back = self.back_input.value.strip()

        # Validierung 1: Leere Felder abfangen
        if not front or not back:
            self.message_text.value = "Bitte fülle beide Felder aus!"
            self.message_text.color = ft.Colors.RED_600
            self.update()
            return

        # Validierung 2: Duplikatsprüfung
        if word_exists(self.profile.words, back):
            self.message_text.value = f"'{back}' existiert bereits in deiner Liste!"
            self.message_text.color = ft.Colors.ORANGE_800
            self.update()
            return

        # Neue fortlaufende ID berechnen
        new_id = max([w.id for w in self.profile.words], default=0) + 1

        # Neues Wort erstellen und der Profilliste anhängen
        new_word = Word(id=new_id, front=front, back=back)
        self.profile.words.append(new_word)

        # Daten dauerhaft speichern
        save_app_data(self.all_profiles, active_profile_name=self.profile.name)

        # Erfolgsmeldung & Eingabefelder zurücksetzen
        self.message_text.value = f"'{front}' -> '{back}' erfolgreich hinzugefügt!"
        self.message_text.color = ft.Colors.GREEN_600
        self.front_input.value = ""
        self.back_input.value = ""
        self.update()
