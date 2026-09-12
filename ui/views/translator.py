"""ui/views/translator.py

Einfacher Übersetzer: deutsches Wort eingeben, "Go" antippen, Haupttreffer
plus weitere zutreffende Übersetzungen ansehen (MyMemory Translation API,
siehe core/translate_client.py). Das Speichern als Vokabel ist bewusst noch
nicht Teil dieser Ansicht - das kommt erst in einer späteren Phase.
"""

import asyncio

import flet as ft
from core.i18n import t
from core.models import UserProfile
from core.translate_client import TranslateFehler, translate_word, zielsprachcode


class TranslatorView(ft.Container):
    """Eingabemaske mit Übersetzungs-Ergebnis (Haupttreffer + Alternativen)."""

    def __init__(self, profile: UserProfile, on_back):
        super().__init__()
        self.profile = profile
        self.on_back = on_back
        self.lang = getattr(profile, "ui_language", "Deutsch")
        self.target_code = zielsprachcode(profile.language)

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
                self.input_field,
                self.go_btn,
                self.message_text,
                self.result_label,
                self.result_text,
                self.alternatives_label,
                self.alternatives_column,
                self.back_btn,
            ],
        )

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
        self.loading_ring.visible = True
        self.go_btn.disabled = True
        self.update()

        try:
            ergebnis = await asyncio.to_thread(translate_word, text, self.target_code)
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
        finally:
            self.loading_ring.visible = False
            self.go_btn.disabled = False
            self.update()
