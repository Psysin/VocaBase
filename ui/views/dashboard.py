"""ui/views/dashboard.py

Dies ist das Herzstück nach dem App-Start. Es zeigt Statistiken an
und bietet Navigation zu allen anderen Bereichen.
"""

import flet as ft
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
        on_switch_profile,
        on_open_settings,
    ):
        super().__init__()
        self.expand = True  # Container nimmt den gesamten verfügbaren Platz ein
        self.profile = profile
        self.on_start_practice = on_start_practice
        self.on_add_word = on_add_word
        self.on_open_list = on_open_list
        self.on_switch_profile = on_switch_profile
        self.on_open_settings = on_open_settings

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

        # ABSCHNITT 1: Zahnrad-Zeile ganz oben (rechtsbündig)
        settings_row = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    tooltip="Einstellungen",
                    icon_size=22,
                    on_click=lambda e: self.on_open_settings(),
                ),
            ],
            width=340,
        )

        # ABSCHNITT 2: Begrüßungs-Bereich (zentriert untereinander)
        greeting_block = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
            controls=[
                ft.Text(
                    f"Hallo, {self.profile.name}! 👋",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    f"Zielsprache: {self.profile.language}",
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
            "🔥 Einheiten", str(self.profile.weekly_sessions), "diese Woche"
        )
        stat_learned = self._build_stat_card(
            "🧠 Gelernt", f"{learned_count}/{total_words}", "Kasten 4 & 5"
        )
        stat_due = self._build_stat_card(
            "📅 Fällig", str(due_words_count), "gesamt offen"
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
                        f"Übung ({actual_quest_words} Vokabeln)",
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
                controls=[ft.Icon(ft.Icons.ADD), ft.Text("Neue Vokabel erfassen")],
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
                    ft.Text(f"Vokabeln verwalten ({total_words})"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            width=340,
            height=44,
            on_click=lambda e: self.on_open_list(),
        )

        btn_profile = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SWITCH_ACCOUNT_OUTLINED, size=18),
                    ft.Text("Profil / Sprache wechseln"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=lambda e: self.on_switch_profile(),
        )

        buttons_block = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[btn_quest, btn_add, btn_list, btn_profile],
            width=340,
        )

        # ZUSAMMENBAU DES GESAMTLAYOUTS
        self.content = ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[settings_row, greeting_block, stats_row, buttons_block],
            ),
            # top=48 sorgt dafür, dass die App auf dem iPhone nicht unter der Notch/Kamera klebt!
            padding=ft.Padding(left=20, top=48, right=20, bottom=20),
            expand=True,
        )

    def _build_stat_card(self, title: str, main_val: str, subtitle: str) -> ft.Card:
        """Hilfsfunktion: Erzeugt eine gleichmäßig formatierte Statistik-Kachel."""
        return ft.Card(
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
