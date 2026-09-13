"""ui/views/translator.py

Einfacher Übersetzer: deutsches Wort eingeben, "Go" antippen, Haupttreffer
plus weitere zutreffende Übersetzungen ansehen (MyMemory Translation API,
siehe core/translate_client.py). Ein gefundener Treffer kann über
"Als Vokabel speichern" auf einer eigenen Seite (translator_save.py)
übernommen werden.
"""

import asyncio

import flet as ft
from core.i18n import t
from core.models import UserProfile
from core.translate_client import TranslateFehler, translate_word, zielsprachcode


class TranslatorView(ft.Container):
    """Eingabemaske mit Übersetzungs-Ergebnis (Haupttreffer + Alternativen)."""

    def __init__(self, profile: UserProfile, on_back, on_save_word):
        super().__init__()
        self.profile = profile
        self.on_back = on_back
        self.on_save_word = on_save_word
        self.lang = getattr(profile, "ui_language", "Deutsch")
        self.target_code = zielsprachcode(profile.language)
        # Letztes erfolgreiches Ergebnis, bereits auf Deutsch/Zielsprache
        # normalisiert (siehe handle_translate) - für die Navigation zur
        # Speicherseite, die die Suchrichtung nicht kennen muss.
        self.last_front_primary: str | None = None
        self.last_front_alternatives: list[str] = []
        self.last_back_primary: str | None = None
        self.last_back_alternatives: list[str] = []
        # Übersetzungsrichtung: False = Deutsch -> Zielsprache (Standard),
        # True = Zielsprache -> Deutsch. Wirkt sich NUR auf den Übersetzer
        # aus - beim Speichern landet unabhängig davon immer Deutsch oben
        # und die Zielsprache unten (siehe handle_translate).
        self.reverse: bool = False

        # 0. RICHTUNGS-UMSCHALTER
        self.direction_label = ft.Text(
            value=t("translator_richtung_vorwaerts", self.lang, sprache=self.profile.language),
            size=13,
            color=ft.Colors.GREY_500,
        )
        self.direction_switch = ft.Switch(value=False, on_change=self.handle_toggle_direction)

        # 1. EINGABEFELD
        self.input_field = ft.TextField(
            label=t("translator_eingabe_hint", self.lang),
            hint_text="z. B. Haus",
            width=320,
            autofocus=True,
            on_submit=self.handle_translate,
        )

        # 2. GO-BUTTON + LADEANZEIGE
        self.loading_ring = ft.ProgressRing(width=16, height=16, visible=False)
        self.go_btn = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    self.loading_ring,
                    ft.Text(t("translator_go_button", self.lang)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=self.handle_translate,
        )

        # 3. ERGEBNIS-BEREICH
        self.result_label = ft.Text(
            value=t("translator_ergebnis_label", self.lang),
            size=13,
            color=ft.Colors.GREY_500,
            visible=False,
        )
        self.result_text = ft.Text(value="", size=26, weight=ft.FontWeight.BOLD)
        self.alternatives_label = ft.Text(
            value=t("translator_weitere_label", self.lang),
            size=13,
            color=ft.Colors.GREY_500,
            visible=False,
        )
        self.alternatives_column = ft.Column(spacing=2)
        self.message_text = ft.Text(value="", size=14, weight=ft.FontWeight.W_500)

        # 3b. ALS VOKABEL SPEICHERN (nur sichtbar nach erfolgreicher Übersetzung)
        self.btn_save_word = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.BOOKMARK_ADD),
                    ft.Text(t("translator_als_vokabel_speichern", self.lang)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            visible=False,
            on_click=lambda e: self.on_save_word(
                self.last_front_primary,
                self.last_front_alternatives,
                self.last_back_primary,
                self.last_back_alternatives,
            ),
        )

        # 4. ZURÜCK-BUTTON
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
                ft.Text(t("translator_titel", self.lang), size=22, weight=ft.FontWeight.BOLD),
                ft.Row(
                    controls=[self.direction_label, self.direction_switch],
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                self.input_field,
                self.go_btn,
                self.message_text,
                self.result_label,
                self.result_text,
                self.alternatives_label,
                self.alternatives_column,
                self.btn_save_word,
                self.back_btn,
            ],
        )

    def handle_toggle_direction(self, e):
        """Wechselt die Übersetzungsrichtung (wirkt sich nur auf den
        Übersetzer aus, nicht auf die Feldbelegung beim Speichern)."""
        self.reverse = self.direction_switch.value
        if self.reverse:
            self.direction_label.value = t(
                "translator_richtung_rueckwaerts", self.lang, sprache=self.profile.language
            )
            self.input_field.label = t("translator_eingabe_hint_rueckwaerts", self.lang)
        else:
            self.direction_label.value = t(
                "translator_richtung_vorwaerts", self.lang, sprache=self.profile.language
            )
            self.input_field.label = t("translator_eingabe_hint", self.lang)

        self.message_text.value = ""
        self.result_label.visible = False
        self.alternatives_label.visible = False
        self.alternatives_column.controls = []
        self.btn_save_word.visible = False
        self.update()

    async def handle_translate(self, e):
        """Übersetzt die Eingabe asynchron (urllib blockiert sonst die Oberfläche)."""
        text = self.input_field.value.strip()
        if not text:
            self.message_text.value = t("translator_leere_eingabe", self.lang)
            self.message_text.color = ft.Colors.ORANGE_800
            self.update()
            return

        self.message_text.value = ""
        self.result_label.visible = False
        self.alternatives_label.visible = False
        self.alternatives_column.controls = []
        self.btn_save_word.visible = False
        self.last_front_primary = None
        self.last_front_alternatives = []
        self.last_back_primary = None
        self.last_back_alternatives = []
        self.loading_ring.visible = True
        self.go_btn.disabled = True
        self.update()

        source_code = self.target_code if self.reverse else "de"
        target_code = "de" if self.reverse else self.target_code

        try:
            ergebnis = await asyncio.to_thread(translate_word, text, source_code, target_code)
        except TranslateFehler as fehler:
            self.result_text.value = ""
            self.message_text.value = t("translator_fehler", self.lang, grund=str(fehler))
            self.message_text.color = ft.Colors.RED_600
        else:
            self.result_text.value = ergebnis.primary
            self.result_label.visible = True
            if ergebnis.alternatives:
                self.alternatives_label.visible = True
                self.alternatives_column.controls = [
                    ft.Text(alt, size=15) for alt in ergebnis.alternatives
                ]

            # Normalisierung auf Deutsch (front) / Zielsprache (back) - die
            # Speicherseite bekommt so immer dieselbe Feldbelegung, egal in
            # welche Richtung gerade gesucht wurde.
            if self.reverse:
                self.last_front_primary = ergebnis.primary
                self.last_front_alternatives = ergebnis.alternatives
                self.last_back_primary = text
                self.last_back_alternatives = []
            else:
                self.last_front_primary = text
                self.last_front_alternatives = []
                self.last_back_primary = ergebnis.primary
                self.last_back_alternatives = ergebnis.alternatives
            self.btn_save_word.visible = True
        finally:
            self.loading_ring.visible = False
            self.go_btn.disabled = False
            self.update()
