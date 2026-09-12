"""ui/views/practice.py

Setzt die Leitner-Logik visuell in einer Schreibübung um.
"""

import flet as ft
from flet_audio import Audio

from core.audio import get_or_cache_audio_path, has_audio
from core.i18n import t
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
        self.lang = getattr(profile, "ui_language", "Deutsch")

        # 1. SPIELLOGIK (State / Zustand)
        quest_limit = getattr(self.profile, "daily_quest_size", 30)

        # Fällige Karten zuerst, bei Bedarf mit weiteren Vokabeln aufgefüllt,
        # damit immer eine volle, gemischte Session zustande kommt.
        self.due_words: list[Word] = build_practice_session(
            self.profile.words, quest_limit
        )
        self.current_index: int = 0
        self.attempts_left: int = 3  # Wird in load_next_card überschrieben
        self.correct_count: int = 0  # Zählt richtig gewusste Vokabeln für den Abschluss-Screen
        self._aktueller_player: Audio | None = None  # siehe play_pronunciation()

        # 2. UI-ELEMENTE
        self.status_text = ft.Text(
            value="", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_600
        )

        self.btn_abort = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CLOSE, size=16, color=ft.Colors.RED_400),
                    ft.Text(t("abbrechen", self.lang), color=ft.Colors.RED_400, size=13),
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
            value="",
            size=26,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
            width=260,
        )

        # Lautsprecher-Button: spielt die Aussprache der Zielsprachen-Antwort ab.
        # Nur sichtbar, wenn dafür eine vorbereitete Audiodatei existiert
        # (aktuell nur Englisch Basis A1) - siehe load_next_card().
        self.speaker_btn = ft.IconButton(
            icon=ft.Icons.VOLUME_UP_OUTLINED,
            tooltip=t("aussprache_abspielen_tooltip", self.lang),
            visible=False,
            on_click=self.play_pronunciation,
        )

        # Feedback-Text (Richtig / Falsch / Lösung) - Unsichtbar zu Beginn!
        self.feedback_display = ft.Text(
            value="", size=15, text_align=ft.TextAlign.CENTER, visible=False
        )

        # Motivationsspruch: nur auf dem Abschluss-Screen sichtbar, passend zur
        # Erfolgsquote der Runde (siehe _motivation_key()).
        self.motivation_display = ft.Text(
            value="", size=13, text_align=ft.TextAlign.CENTER, visible=False
        )

        # Referenz auf den inneren Container, damit load_next_card() die Höhe
        # für den (dreizeiligen) Abschluss-Screen vergrößern kann, ohne die
        # kompakte Höhe während der normalen Abfrage zu beeinflussen.
        self.card_inner = ft.Container(
            content=ft.Stack(
                controls=[
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            self.word_display,
                            self.feedback_display,
                            self.motivation_display,
                        ],
                    ),
                    ft.Container(
                        content=self.speaker_btn,
                        alignment=ft.Alignment.TOP_RIGHT,
                    ),
                ],
            ),
            width=320,
            height=150,
            padding=15,
        )
        self.card_container = ft.Card(content=self.card_inner)

        # Eingabefeld
        # on_submit triggert, wenn der Nutzer auf dem Handy oder PC "Enter"/"Return" drückt
        self.input_field = ft.TextField(
            label=t("uebersetzung_sprache", self.lang, sprache=self.profile.language),
            hint_text=t("antwort_eintippen", self.lang),
            dense=True,
            width=320,
            autofocus=True,
            on_submit=self.check_typed_answer,
        )

        self.btn_check = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.CHECK), ft.Text(t("pruefen", self.lang))],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=320,
            height=46,
            on_click=self.check_typed_answer,
        )

        # Icon/Text als Referenzen gehalten, da sich die Beschriftung bei der
        # letzten Vokabel der Runde ändert (siehe _update_next_button_label()) -
        # "Nächste Vokabel" wäre dort irreführend, es kommt ja keine mehr.
        self.btn_next_icon = ft.Icon(ft.Icons.ARROW_FORWARD)
        self.btn_next_label = ft.Text(t("naechste_vokabel", self.lang))
        self.btn_next = ft.ElevatedButton(
            content=ft.Row(
                controls=[self.btn_next_icon, self.btn_next_label],
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
                controls=[
                    ft.Icon(ft.Icons.HOME),
                    ft.Text(t("zurueck_hauptmenue", self.lang)),
                ],
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

    def _motivation_key(self, quote: float) -> str:
        """Wählt den passenden Motivationsspruch-Key zur Erfolgsquote (0.0-1.0)."""
        if quote >= 1.0:
            return "motivation_perfekt"
        elif quote >= 0.8:
            return "motivation_sehr_gut"
        elif quote >= 0.6:
            return "motivation_gut"
        elif quote >= 0.4:
            return "motivation_dabeibleiben"
        else:
            return "motivation_weiter_ueben"

    def _update_next_button_label(self):
        """Passt Icon/Text von btn_next an: Bei der letzten Vokabel der Runde
        wäre "Nächste Vokabel" irreführend, da direkt der Abschluss-Screen
        folgt - dort steht stattdessen "Ergebnis anzeigen"."""
        if self.current_index + 1 >= len(self.due_words):
            self.btn_next_icon.icon = ft.Icons.EMOJI_EVENTS
            self.btn_next_label.value = t("ergebnis_anzeigen", self.lang)
        else:
            self.btn_next_icon.icon = ft.Icons.ARROW_FORWARD
            self.btn_next_label.value = t("naechste_vokabel", self.lang)

    def load_next_card(self):
        """Lädt die nächste fällige Karte oder beendet die Übung."""
        if self.current_index < len(self.due_words):
            # Es gibt noch Karten zum Abfragen
            current_word = self.due_words[self.current_index]
            self.card_inner.height = 150
            self.word_display.width = 260
            self.word_display.value = current_word.front
            self.speaker_btn.visible = has_audio(self.profile.language, current_word.back)

            # Alles für den neuen Versuch auf Standard zurücksetzen
            self.feedback_display.visible = False
            self.motivation_display.visible = False
            self.attempts_left = getattr(self.profile, "max_attempts", 3)
            self.input_field.visible = True
            self.input_field.value = ""
            self.input_field.read_only = False
            self.btn_check.visible = True
            self.btn_next.visible = False
            self.btn_finish.visible = False
            self.btn_abort.visible = True
            self.status_text.visible = True
            self.status_text.value = f"{self.current_index + 1}/{len(self.due_words)}"
            self.input_field.focus()  # Holt den Cursor zurück
        else:
            # Übung abgeschlossen
            if len(self.due_words) > 0:
                self.profile.weekly_sessions += 1
                save_app_data(self.all_profiles, active_profile_name=self.profile.name)

            # Sieges-Bildschirm bauen (Eingabefeld verschwindet)
            # Karte etwas größer + Wortanzeige breiter, damit Ergebnis- und
            # Motivationszeile nicht gequetscht wirken (Lautsprecher-Icon ist
            # hier ohnehin ausgeblendet, der Platz kann also genutzt werden).
            self.card_inner.height = 220
            self.word_display.width = 290
            self.word_display.value = t("uebung_gemeistert", self.lang)

            if len(self.due_words) > 0:
                self.feedback_display.value = t(
                    "vokabeln_ergebnis",
                    self.lang,
                    richtig=self.correct_count,
                    gesamt=len(self.due_words),
                )
                self.feedback_display.color = ft.Colors.GREEN_400
                self.feedback_display.visible = True

                quote = self.correct_count / len(self.due_words)
                self.motivation_display.value = t(self._motivation_key(quote), self.lang)
                self.motivation_display.visible = True

            self.speaker_btn.visible = False
            self.input_field.visible = False
            self.btn_check.visible = False
            self.btn_next.visible = False
            self.btn_abort.visible = False
            self.btn_finish.visible = True
            # Kein "Fertig"-Label mehr oben - die Karte sagt bereits alles.
            self.status_text.visible = False

    def check_typed_answer(self, e):
        """Prüft die eingegebene Übersetzung gegen das hinterlegte Lösungswort."""
        # Schutz gegen doppelte Auswertung derselben Karte (z.B. Doppel-Tap auf
        # "Prüfen" oder Enter kurz nach dem Klick) - würde sonst correct_count
        # mehrfach für dieselbe Vokabel hochzählen.
        if self.input_field.read_only:
            return

        current_word = self.due_words[self.current_index]
        user_input = self.input_field.value.strip()

        # Korrekte Eingabe
        if user_input.lower() == current_word.back.strip().lower():
            self.feedback_display.value = t("richtig", self.lang)
            self.feedback_display.color = ft.Colors.GREEN_400
            self.feedback_display.visible = True
            self.input_field.read_only = True
            self.btn_check.visible = False
            self._update_next_button_label()
            self.btn_next.visible = True

            # Vokabel steigt einen Kasten auf
            review_word(current_word, "gewusst")
            save_app_data(self.all_profiles, active_profile_name=self.profile.name)
            self.correct_count += 1
        else:
            # Falsche Eingabe - Versuch abziehen
            self.attempts_left -= 1

            if self.attempts_left > 0:
                if self.attempts_left == 1:
                    self.feedback_display.value = t("falsch_1_versuch", self.lang)
                else:
                    self.feedback_display.value = t(
                        "falsch_n_versuche", self.lang, n=self.attempts_left
                    )
                self.feedback_display.color = ft.Colors.ORANGE_400
                self.feedback_display.visible = True
                self.input_field.value = ""
                self.input_field.focus()
            else:
                # Alle Fehlversuche aufgebraucht
                self.feedback_display.value = t(
                    "falsch_endgueltig", self.lang, loesung=current_word.back
                )
                self.feedback_display.color = ft.Colors.RED_400
                self.feedback_display.visible = True
                self.input_field.read_only = True
                self.btn_check.visible = False
                self._update_next_button_label()
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

    def play_pronunciation(self, e):
        """Spielt die Aussprache der aktuellen Zielsprachen-Antwort ab.

        Frische Audio(src=Dateipfad, autoplay=True)-Instanz pro Wiedergabe
        (siehe main.py-Testaufbau) - rohe Bytes bleiben auf iOS lautlos, ein
        echter Dateipfad aus get_or_cache_audio_path() funktioniert zuverlässig."""
        current_word = self.due_words[self.current_index]
        audio_pfad = get_or_cache_audio_path(self.profile.language, current_word.back)
        if audio_pfad is None:
            return

        # Vorherige Wiedergabe-Instanz entfernen, damit page.services über eine
        # lange Übungssitzung nicht unbegrenzt anwächst.
        if self._aktueller_player is not None and self._aktueller_player in self.page.services:
            self.page.services.remove(self._aktueller_player)

        self._aktueller_player = Audio(src=audio_pfad, autoplay=True)
        self.page.services.append(self._aktueller_player)
        self.page.update()
