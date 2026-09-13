"""ui/views/translator_save.py

Eigene Seite, um einen Übersetzer-Treffer als Vokabel zu speichern (siehe
ui/views/translator.py). Haupttreffer-Maske ist vorausgefüllt und editierbar;
weitere zutreffende Übersetzungen können optional per Checkbox als
zusätzliche Vokabeln mitgespeichert werden (Standard: nur der Haupttreffer).
"""

import flet as ft
from core.i18n import t
from core.models import UserProfile, Word
from core.spaced_rep import word_exists
from core.translate_client import TranslationResult
from data.storage import save_app_data


class TranslatorSaveView(ft.Container):
    """Vorausgefüllte Speichermaske für einen Übersetzer-Treffer plus Alternativen."""

    def __init__(
        self,
        profile: UserProfile,
        all_profiles: list[UserProfile],
        front_text: str,
        result: TranslationResult,
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
            value=front_text,
            width=320,
        )
        self.back_input = ft.TextField(
            label=t("uebersetzung_sprache", self.lang, sprache=self.profile.language),
            value=result.primary,
            width=320,
        )

        # 2. WEITERE ÜBERSETZUNGEN (optional, standardmäßig abgewählt)
        # Jede Checkbox merkt sich ihren Alternativ-Text über (Checkbox, Text)
        # -Paare, damit handle_save() beim Auswerten nicht erneut auf die
        # Reihenfolge der Controls angewiesen ist.
        self.alt_checkboxes: list[tuple[ft.Checkbox, str]] = []
        alternatives_controls: list[ft.Control] = []
        if result.alternatives:
            alternatives_controls.append(
                ft.Text(
                    t("translator_weitere_speichern_hinweis", self.lang),
                    size=13,
                    color=ft.Colors.GREY_500,
                )
            )
            for alt in result.alternatives:
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
        """Prüft die Haupttreffer-Felder, sammelt angehakte Alternativen und
        speichert alle nicht bereits vorhandenen Paare als neue Vokabeln."""
        front = self.front_input.value.strip()
        back = self.back_input.value.strip()

        if not front or not back:
            self.message_text.value = t("fehler_felder_leer", self.lang)
            self.message_text.color = ft.Colors.RED_600
            self.update()
            return

        # Haupttreffer immer dabei, plus jede angehakte Alternative - alle
        # mit demselben (ggf. vom Nutzer angepassten) deutschen Wort.
        zu_speichern = [back] + [
            alt for checkbox, alt in self.alt_checkboxes if checkbox.value
        ]

        hinzugefuegt: list[str] = []
        duplikate: list[str] = []
        for kandidat in zu_speichern:
            # Sequenziell prüfen: bereits in dieser Aktion gespeicherte
            # Wörter zählen für die Duplikatsprüfung der nächsten mit, da
            # word_exists() direkt gegen self.profile.words prüft.
            if word_exists(self.profile.words, kandidat):
                duplikate.append(kandidat)
                continue
            new_id = max([w.id for w in self.profile.words], default=0) + 1
            self.profile.words.append(Word(id=new_id, front=front, back=kandidat))
            hinzugefuegt.append(kandidat)

        if hinzugefuegt:
            save_app_data(self.all_profiles, active_profile_name=self.profile.name)

        nachricht = ""
        if hinzugefuegt:
            nachricht = t(
                "translator_speichern_erfolg", self.lang, anzahl=len(hinzugefuegt)
            )
        if duplikate:
            duplikat_zeile = t(
                "translator_speichern_duplikate", self.lang, woerter=", ".join(duplikate)
            )
            nachricht = f"{nachricht}\n{duplikat_zeile}" if nachricht else duplikat_zeile

        self.message_text.value = nachricht
        self.message_text.color = ft.Colors.GREEN_600 if hinzugefuegt else ft.Colors.ORANGE_800
        self.update()
