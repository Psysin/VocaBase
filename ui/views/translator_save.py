"""ui/views/translator_save.py

Eigene Seite, um einen Übersetzer-Treffer als Vokabel zu speichern (siehe
ui/views/translator.py). Haupttreffer-Maske ist vorausgefüllt und editierbar;
weitere zutreffende Übersetzungen können optional per Checkbox mit angehakt
werden - sie werden dann kommagetrennt in dasselbe Feld eingetragen (nur EINE
Vokabel pro Speicherung, keine separaten Einträge). front/back sind hier
immer bereits auf Deutsch (oben) / Zielsprache (unten) normalisiert - unab-
hängig davon, in welche Richtung im Übersetzer gesucht wurde (siehe
translator.py: handle_translate).
"""

import flet as ft
from core.i18n import t
from core.models import UserProfile, Word
from core.spaced_rep import word_exists
from data.storage import save_app_data


class TranslatorSaveView(ft.Container):
    """Vorausgefüllte Speichermaske für einen Übersetzer-Treffer plus Alternativen."""

    def __init__(
        self,
        profile: UserProfile,
        all_profiles: list[UserProfile],
        front_primary: str,
        front_alternatives: list[str],
        back_primary: str,
        back_alternatives: list[str],
        on_back,
    ):
        super().__init__()
        self.profile = profile
        self.all_profiles = all_profiles
        self.on_back = on_back
        self.lang = getattr(profile, "ui_language", "Deutsch")

        # 1. HAUPTTREFFER-MASKE (vorausgefüllt, editierbar)
        self.front_input = ft.TextField(
            label=t("deutsches_wort_frage", self.lang),
            value=front_primary,
            width=320,
        )
        self.back_input = ft.TextField(
            label=t("uebersetzung_sprache", self.lang, sprache=self.profile.language),
            value=back_primary,
            width=320,
        )

        # 2. WEITERE ÜBERSETZUNGEN (optional, standardmäßig abgewählt)
        # Nur eine der beiden Listen ist nicht leer, je nachdem in welche
        # Richtung übersetzt wurde: Alternativen gehören immer zur Seite, die
        # gerade das Übersetzungsergebnis war (Zielsprache vorwärts, Deutsch
        # rückwärts). Jede Checkbox merkt sich ihren Alternativ-Text über
        # (Checkbox, Text)-Paare, damit handle_save() beim Auswerten nicht
        # erneut auf die Reihenfolge der Controls angewiesen ist.
        self.combine_front = bool(front_alternatives)
        alternativen = front_alternatives or back_alternatives
        self.alt_checkboxes: list[tuple[ft.Checkbox, str]] = []
        alternatives_controls: list[ft.Control] = []
        if alternativen:
            alternatives_controls.append(
                ft.Text(
                    t("translator_weitere_speichern_hinweis", self.lang),
                    size=13,
                    color=ft.Colors.GREY_500,
                )
            )
            for alt in alternativen:
                checkbox = ft.Checkbox(label=alt, value=False)
                self.alt_checkboxes.append((checkbox, alt))
                # In einem Container mit derselben Breite wie die TextFields
                # oben ausrichten - eine Checkbox ohne das würde sonst am
                # linken Rand statt zentriert erscheinen (width direkt auf
                # Checkbox setzen würde stattdessen das Kästchen selbst
                # aufblähen).
                alternatives_controls.append(ft.Container(content=checkbox, width=320))

        # 3. FEEDBACK-TEXT
        self.message_text = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

        # 4. BUTTONS
        self.save_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.SAVE), ft.Text(t("speichern", self.lang))],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=self.handle_save,
        )
        self.back_btn = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ARROW_BACK),
                    ft.Text(t("zurueck_hauptmenue", self.lang)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=lambda e: self.on_back(),
        )

        # 5. LAYOUT
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            controls=[
                ft.Text(
                    t("translator_speichern_titel", self.lang), size=22, weight=ft.FontWeight.BOLD
                ),
                self.front_input,
                self.back_input,
                *alternatives_controls,
                self.message_text,
                self.save_btn,
                self.back_btn,
            ],
        )

    def handle_save(self, e):
        """Prüft die Felder, kombiniert angehakte Alternativen kommagetrennt
        in das jeweilige Feld und speichert EINE Vokabel (Muster wie
        add_word.py, nur mit vorausgefüllten/kombinierbaren Feldern)."""
        front = self.front_input.value.strip()
        back = self.back_input.value.strip()

        if not front or not back:
            self.message_text.value = t("fehler_felder_leer", self.lang)
            self.message_text.color = ft.Colors.RED_600
            self.update()
            return

        angehakt = [alt for checkbox, alt in self.alt_checkboxes if checkbox.value]
        if angehakt:
            if self.combine_front:
                front = ", ".join([front] + angehakt)
            else:
                back = ", ".join([back] + angehakt)

        if word_exists(self.profile.words, back):
            self.message_text.value = t("fehler_duplikat", self.lang, wort=back)
            self.message_text.color = ft.Colors.ORANGE_800
            self.update()
            return

        new_id = max([w.id for w in self.profile.words], default=0) + 1
        self.profile.words.append(Word(id=new_id, front=front, back=back))
        save_app_data(self.all_profiles, active_profile_name=self.profile.name)

        self.message_text.value = t("erfolg_hinzugefuegt", self.lang, front=front, back=back)
        self.message_text.color = ft.Colors.GREEN_600
        self.update()
