"""ui/views/add_word.py

Ansicht zum Hinzufügen einzelner neuer Vokabeln in das Profil.
"""

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

        # 1. EINGABEFELDER (Input)
        # autofocus=True sorgt dafür, dass der Cursor direkt im Feld blinkt
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

        # 2. FEEDBACK-TEXT (Output)
        # Am Anfang leer, wird rot bei Fehlern oder grün bei Erfolg
        self.message_text = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

        # 3. BUTTONS
        self.save_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.SAVE), ft.Text("Vokabel speichern")],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,  # tight=True sorgt dafür, dass die Reihe nur so breit wie ihr Inhalt ist
            ),
            on_click=self.handle_save,  # Ruft die Speicher-Funktion auf
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
            on_click=lambda e: (
                self.on_back()
            ),  # Kehrt über die main.py zum Dashboard zurück
        )

        # 4. LAYOUT
        # Column ordnet alle Elemente untereinander an
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
        # .strip() entfernt versehentlich getippte Leerzeichen am Anfang und Ende
        front = self.front_input.value.strip()
        back = self.back_input.value.strip()

        # Validierung 1: Leere Felder abfangen
        if not front or not back:
            self.message_text.value = "Bitte fülle beide Felder aus!"
            self.message_text.color = ft.Colors.RED_600
            self.update()  # Zeichnet diese Ansicht neu, damit der Text sichtbar wird
            return  # Bricht die Funktion hier ab

        # Validierung 2: Duplikatsprüfung (greift auf unsere ausgelagerte Logik zu)
        if word_exists(self.profile.words, back):
            self.message_text.value = f"'{back}' existiert bereits in deiner Liste!"
            self.message_text.color = ft.Colors.ORANGE_800
            self.update()
            return

        # 3. Neue ID berechnen:
        # Sucht die höchste ID aller Wörter. Ist die Liste leer, nimmt max() den default=0.
        new_id = max([w.id for w in self.profile.words], default=0) + 1

        # 4. Wort in den Speicherbaum einfügen
        new_word = Word(id=new_id, front=front, back=back)
        self.profile.words.append(new_word)

        # 5. Festplatte aktualisieren
        save_app_data(self.all_profiles, active_profile_name=self.profile.name)

        # 6. Erfolgsmeldung zeigen und Eingabefelder für das nächste Wort leeren
        self.message_text.value = f"'{front}' -> '{back}' erfolgreich hinzugefügt!"
        self.message_text.color = ft.Colors.GREEN_600
        self.front_input.value = ""
        self.back_input.value = ""

        # Cursor springt automatisch wieder in das erste Feld

        self.front_input.focus()
        self.update()
