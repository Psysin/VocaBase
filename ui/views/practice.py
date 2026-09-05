"""ui/views/practice.py

Setzt die Leitner-Logik visuell in einer Schreibübung um.
"""

import flet as ft
from core.models import UserProfile, Word
from core.spaced_rep import build_practice_session, review_word
from data.storage import save_app_data


class PracticeView(ft.Container):
    """Übungsansicht: Reines Schreib-Training mit Eingabeprüfung."""

    def __init__(
        self, profile: UserProfile, all_profiles: list[UserProfile], on_finish
    ):
        super().__init__()
        self.expand = True
        self.profile = profile
        self.all_profiles = all_profiles
        self.on_finish = on_finish

        # 1. SPIELLOGIK (State / Zustand)
        quest_limit = getattr(self.profile, "daily_quest_size", 30)

        # Fällige Karten zuerst, bei Bedarf mit weiteren Vokabeln aufgefüllt,
        # damit immer eine volle, gemischte Session zustande kommt.
        self.due_words: list[Word] = build_practice_session(
            self.profile.words, quest_limit
        )
        self.current_index: int = 0
        self.attempts_left: int = 3  # Wird in load_next_card überschrieben

        # 2. UI-ELEMENTE
        self.status_text = ft.Text(
            value="", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_600
        )

        self.btn_abort = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CLOSE, size=16, color=ft.Colors.RED_400),
                    ft.Text("Abbrechen", color=ft.Colors.RED_400, size=13),
                ],
                tight=True,
            ),
            on_click=lambda e: self.on_finish(),
        )

        header_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[self.btn_abort, self.status_text],
            width=320,
        )

        # Wortanzeige (Deutsches Wort)
        self.word_display = ft.Text(
            value="", size=26, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
        )

        # Feedback-Text (Richtig / Falsch / Lösung) - Unsichtbar zu Beginn!
        self.feedback_display = ft.Text(
            value="", size=15, text_align=ft.TextAlign.CENTER, visible=False
        )

        self.card_container = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    controls=[self.word_display, self.feedback_display],
                ),
                width=320,
                height=150,
                padding=15,
            )
        )

        # Eingabefeld
        # on_submit triggert, wenn der Nutzer auf dem Handy oder PC "Enter"/"Return" drückt
        self.input_field = ft.TextField(
            label=f"Übersetzung ({self.profile.language})",
            hint_text="Antwort eintippen...",
            dense=True,
            width=320,
            autofocus=True,
            on_submit=self.check_typed_answer,
        )

        self.btn_check = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.CHECK), ft.Text("Prüfen")],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=320,
            height=46,
            on_click=self.check_typed_answer,
        )

        self.btn_next = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.ARROW_FORWARD), ft.Text("Nächste Vokabel")],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=320,
            height=46,
            on_click=lambda e: self.advance_to_next(),
            visible=False,  # Erst sichtbar, wenn geprüft wurde
        )

        self.btn_finish = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.HOME), ft.Text("Zurück zum Dashboard")],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=320,
            height=46,
            on_click=lambda e: self.on_finish(),
            visible=False,
        )

        self.content = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    header_row,
                    self.card_container,
                    self.input_field,
                    self.btn_check,
                    self.btn_next,
                    self.btn_finish,
                ],
            ),
            padding=ft.Padding(left=20, top=48, right=20, bottom=20),
            expand=True,
        )

        # Startet die Logik und füllt die UI-Elemente mit dem ersten Wort
        self.load_next_card()

    def load_next_card(self):
        """Lädt die nächste fällige Karte oder beendet die Quest."""
        if self.current_index < len(self.due_words):
            # Es gibt noch Karten zum Abfragen
            current_word = self.due_words[self.current_index]
            self.word_display.value = current_word.front

            # Alles für den neuen Versuch auf Standard zurücksetzen
            self.feedback_display.visible = False
            self.attempts_left = getattr(self.profile, "max_attempts", 3)
            self.input_field.visible = True
            self.input_field.value = ""
            self.input_field.read_only = False
            self.btn_check.visible = True
            self.btn_next.visible = False
            self.btn_finish.visible = False
            self.btn_abort.visible = True
            self.status_text.value = f"{self.current_index + 1}/{len(self.due_words)}"
            self.input_field.focus()  # Holt den Cursor zurück
        else:
            # Übung abgeschlossen
            if len(self.due_words) > 0:
                self.profile.weekly_sessions += 1
                save_app_data(self.all_profiles, active_profile_name=self.profile.name)

            # Sieges-Bildschirm bauen (Eingabefeld verschwindet)
            self.word_display.value = "🏆 Quest gemeistert!"
            self.feedback_display.value = (
                f"{len(self.due_words)} Vokabeln erfolgreich abgeschlossen."
            )
            self.feedback_display.color = ft.Colors.GREEN_400
            self.feedback_display.visible = True

            self.input_field.visible = False
            self.btn_check.visible = False
            self.btn_next.visible = False
            self.btn_abort.visible = False
            self.btn_finish.visible = True
            self.status_text.value = "Fertig"

    def check_typed_answer(self, e):
        """Prüft die eingegebene Übersetzung gegen das hinterlegte Lösungswort."""
        current_word = self.due_words[self.current_index]
        user_input = self.input_field.value.strip()

        # Korrekte Eingabe
        if user_input.lower() == current_word.back.strip().lower():
            self.feedback_display.value = "✅ Richtig!"
            self.feedback_display.color = ft.Colors.GREEN_400
            self.feedback_display.visible = True
            self.input_field.read_only = True
            self.btn_check.visible = False
            self.btn_next.visible = True

            # Vokabel steigt einen Kasten auf
            review_word(current_word, "gewusst")
            save_app_data(self.all_profiles, active_profile_name=self.profile.name)
        else:
            # Falsche Eingabe - Versuch abziehen
            self.attempts_left -= 1

            if self.attempts_left > 0:
                self.feedback_display.value = f"❌ Falsch! Noch {self.attempts_left} Versuch{'e' if self.attempts_left > 1 else ''}."
                self.feedback_display.color = ft.Colors.ORANGE_400
                self.feedback_display.visible = True
                self.input_field.value = ""
                self.input_field.focus()
            else:
                # Alle Fehlversuche aufgebraucht
                self.feedback_display.value = (
                    f"❌ Leider falsch! Richtige Lösung: {current_word.back}"
                )
                self.feedback_display.color = ft.Colors.RED_400
                self.feedback_display.visible = True
                self.input_field.read_only = True
                self.btn_check.visible = False
                self.btn_next.visible = True

                # Kasten-Strafaktion
                review_word(current_word, "nicht_gewusst")
                save_app_data(self.all_profiles, active_profile_name=self.profile.name)

        # WICHTIG: Das UI muss manuell angewiesen werden, sich neu zu zeichnen,
        # da wir visibility, texte und buttons im Hintergrund verändert haben.
        self.update()

    def advance_to_next(self):
        """Weiterschalten zur nächsten Vokabelkarte."""
        self.current_index += 1
        self.load_next_card()
        self.update()
