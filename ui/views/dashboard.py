"""ui/views/dashboard.py

Dies ist das Herzstück nach dem App-Start. Es zeigt Statistiken an
und bietet Navigation zu allen anderen Bereichen.
"""

import flet as ft
from core.i18n import t
from core.models import UserProfile
from core.spaced_rep import get_due_words


class DashboardView(ft.Container):
    """Haupt-Dashboard mit klar getrennten Bereichen."""

    def __init__(
        self,
        profile: UserProfile,
        on_start_practice,
        on_add_word,
        on_open_list,
        on_open_settings,
    ):
        super().__init__()
        self.expand = True  # Container nimmt den gesamten verfügbaren Platz ein
        self.profile = profile
        self.on_start_practice = on_start_practice
        self.on_add_word = on_add_word
        self.on_open_list = on_open_list
        self.on_open_settings = on_open_settings

        lang = getattr(profile, "ui_language", "Deutsch")

        # 1. LIVE-DATEN BERECHNEN
        total_words = len(self.profile.words)
        due_words_count = len(get_due_words(self.profile.words))

        # Zählt, wie viele Wörter schon gut verinnerlicht sind (Kasten 4 oder 5)
        learned_count = sum(1 for w in self.profile.words if w.box in (4, 5))

        quest_size = getattr(self.profile, "daily_quest_size", 30)

        # Fällige Karten werden bei Bedarf mit weiteren Vokabeln aus dem Pool
        # aufgefüllt (siehe build_practice_session), daher entspricht die
        # tatsächliche Session-Größe stets dem Minimum aus Durchgangsgröße
        # und der Gesamtzahl vorhandener Vokabeln.
        actual_quest_words = min(quest_size, total_words)

        # -------------------------------------------------------------
        # UI-AUFBAU IN BÖCKEN
        # -------------------------------------------------------------

        # ABSCHNITT 2: Begrüßungs-Bereich (zentriert untereinander)
        greeting_block = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(
                    t("begruessung", lang, name=self.profile.name),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    t("zielsprache_zeile", lang, sprache=self.profile.language),
                    size=14,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            width=340,
        )

        # ABSCHNITT 3: Dashboard-Statistiken (3 Kacheln nebeneinander)
        # Nutzt eine Hilfsfunktion (unten definiert), um Code-Wiederholungen zu vermeiden
        stat_sessions = self._build_stat_card(
            t("stat_einheiten_titel", lang),
            str(self.profile.weekly_sessions),
            t("stat_einheiten_sub", lang),
        )
        stat_learned = self._build_stat_card(
            t("stat_gelernt_titel", lang),
            f"{learned_count}/{total_words}",
            t("stat_gelernt_sub", lang),
        )
        stat_due = self._build_stat_card(
            t("stat_faellig_titel", lang),
            str(due_words_count),
            t("stat_faellig_sub", lang),
        )

        stats_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=[stat_sessions, stat_learned, stat_due],
            width=340,
        )

        # ABSCHNITT 4: Aktions-Buttons
        btn_quest = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=ft.Colors.WHITE),
                    ft.Text(
                        t("btn_uebung", lang, anzahl=actual_quest_words),
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=340,
            height=48,
            # Nur gesperrt, wenn das Profil überhaupt keine Vokabeln hat.
            # Sind alle fälligen Karten erledigt, wird aus dem Gesamtpool
            # aufgefüllt, damit beliebig oft geübt werden kann.
            disabled=total_words == 0,
            on_click=lambda e: self.on_start_practice(),
        )

        btn_add = ft.ElevatedButton(
            content=ft.Row(
                controls=[ft.Icon(ft.Icons.ADD), ft.Text(t("btn_neue_vokabel", lang))],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=340,
            height=44,
            on_click=lambda e: self.on_add_word(),
        )

        btn_list = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LIST_ALT),
                    ft.Text(t("btn_vokabeln_verwalten", lang, anzahl=total_words)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=340,
            height=44,
            on_click=lambda e: self.on_open_list(),
        )

        btn_settings = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SETTINGS),
                    ft.Text(t("btn_einstellungen", lang)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=340,
            height=44,
            on_click=lambda e: self.on_open_settings(),
        )

        buttons_block = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[btn_quest, btn_add, btn_list, btn_settings],
            width=340,
        )

        # ZUSAMMENBAU DES GESAMTLAYOUTS
        # SafeArea statt fester top-Padding: berechnet den nötigen Abstand zur
        # Notch/Dynamic Island automatisch pro Gerät, anstatt eine feste Zahl zu
        # raten (die auf einem iPhone zu knapp und auf einem anderen zu großzügig war).
        self.content = ft.SafeArea(
            content=ft.Container(
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16,
                    controls=[greeting_block, stats_row, buttons_block],
                ),
                padding=ft.Padding(left=20, top=36, right=20, bottom=20),
                expand=True,
            ),
            expand=True,
        )

    def _build_stat_card(self, title: str, main_val: str, subtitle: str) -> ft.Card:
        """Hilfsfunktion: Erzeugt eine gleichmäßig formatierte Statistik-Kachel."""
        return ft.Card(
            # margin=0, da Card sonst per Default ringsum 4px Außenabstand
            # addiert - bei 3 Karten mit fixer Breite in der stats_row führte
            # das auf echten Geräten zu einem RenderFlex-Overflow von 12px.
            margin=0,
            content=ft.Container(
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                    controls=[
                        ft.Text(title, size=11, weight=ft.FontWeight.W_500),
                        ft.Text(
                            main_val,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_400,
                        ),
                        ft.Text(subtitle, size=10, color=ft.Colors.GREY_600),
                    ],
                ),
                width=104,
                height=84,
                padding=6,
            )
        )
