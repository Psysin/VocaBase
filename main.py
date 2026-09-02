from datetime import date
import flet as ft
from core.models import UserProfile, Word
from data.starter_words import STARTER_PACKS
from data.storage import load_app_data, save_app_data
from ui.views.add_word import AddWordView
from ui.views.dashboard import DashboardView
from ui.views.practice import PracticeView
from ui.views.word_list import WordListView


def generate_starter_words(language: str) -> list[Word]:
    raw_pairs = STARTER_PACKS.get(language, [])
    today_str = str(date.today())
    return [
        Word(id=idx + 1, front=de, back=foreign, box=1, due_date=today_str)
        for idx, (de, foreign) in enumerate(raw_pairs)
    ]


def main(page: ft.Page):
    page.title = "Vokabeltrainer"
    page.window.width = 390
    page.window.height = 720
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    profiles, active_name = load_app_data()

    if not profiles:
        philipp_words = generate_starter_words("Englisch")
        profil_philipp = UserProfile(
            name="Philipp", language="Englisch", words=philipp_words
        )
        profiles = [profil_philipp]
        active_name = "Philipp"
        save_app_data(profiles, active_profile_name=active_name)

    active_profile = next((p for p in profiles if p.name == active_name), profiles[0])

    # Theme basierend auf dem aktiven Profil setzen
    page.theme_mode = (
        ft.ThemeMode.DARK
        if getattr(active_profile, "dark_mode", True)
        else ft.ThemeMode.LIGHT
    )

    def show_view(view_name: str):
        page.clean()

        if view_name == "dashboard":
            page.add(
                DashboardView(
                    profile=active_profile,
                    on_start_practice=lambda: show_view("practice"),
                    on_add_word=lambda: show_view("add_word"),
                    on_open_list=lambda: show_view("word_list"),
                    on_switch_profile=open_profile_dialog,
                    on_open_settings=open_settings_dialog,
                )
            )
        elif view_name == "practice":
            page.add(
                PracticeView(
                    profile=active_profile,
                    all_profiles=profiles,
                    on_finish=lambda: show_view("dashboard"),
                )
            )
        elif view_name == "add_word":
            page.add(
                AddWordView(
                    profile=active_profile,
                    all_profiles=profiles,
                    on_back=lambda: show_view("dashboard"),
                )
            )
        elif view_name == "word_list":
            page.add(
                WordListView(
                    profile=active_profile,
                    all_profiles=profiles,
                    on_back=lambda: show_view("dashboard"),
                )
            )

        page.update()

    def open_settings_dialog():
        """Einstellungsdialog für Quest-Größe, Dark Mode, Version und Copyright."""
        quest_dropdown = ft.Dropdown(
            label="Daily Quest Umfang (Wörter)",
            value=str(getattr(active_profile, "daily_quest_size", 30)),
            options=[
                ft.dropdown.Option("10"),
                ft.dropdown.Option("20"),
                ft.dropdown.Option("30"),
                ft.dropdown.Option("50"),
                ft.dropdown.Option("100"),
            ],
            dense=True,
        )

        theme_switch = ft.Switch(
            label="Dark Mode",
            value=getattr(active_profile, "dark_mode", True),
        )

        def save_settings(e):
            active_profile.daily_quest_size = int(quest_dropdown.value or 30)
            active_profile.dark_mode = theme_switch.value
            page.theme_mode = (
                ft.ThemeMode.DARK if active_profile.dark_mode else ft.ThemeMode.LIGHT
            )

            save_app_data(profiles, active_profile_name=active_profile.name)
            settings_dialog.open = False
            page.update()
            show_view("dashboard")

        def close_settings(e):
            settings_dialog.open = False
            page.update()

        settings_dialog = ft.AlertDialog(
            title=ft.Text("⚙️ Einstellungen"),
            content=ft.Column(
                controls=[
                    quest_dropdown,
                    theme_switch,
                    ft.Divider(),
                    ft.Text("App-Informationen:", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text("Version: 1.0.0", size=12, color=ft.Colors.GREY_500),
                    ft.Text(
                        "Entwickler: Philipp Edelbrock",
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        "© 2026 Alle Rechte vorbehalten",
                        size=11,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                tight=True,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Abbrechen"), on_click=close_settings),
                ft.ElevatedButton(content=ft.Text("Speichern"), on_click=save_settings),
            ],
        )

        page.overlay.append(settings_dialog)
        settings_dialog.open = True
        page.update()

    def open_profile_dialog():
        nonlocal active_profile

        def select_profile(selected_profile: UserProfile):
            nonlocal active_profile
            active_profile = selected_profile
            page.theme_mode = (
                ft.ThemeMode.DARK
                if getattr(active_profile, "dark_mode", True)
                else ft.ThemeMode.LIGHT
            )
            save_app_data(profiles, active_profile_name=active_profile.name)
            dialog.open = False
            page.update()
            show_view("dashboard")

        def delete_profile(profile_to_delete: UserProfile):
            nonlocal active_profile
            if len(profiles) <= 1:
                return

            profiles.remove(profile_to_delete)
            if active_profile.name == profile_to_delete.name:
                active_profile = profiles[0]

            save_app_data(profiles, active_profile_name=active_profile.name)
            dialog.open = False
            page.update()
            show_view("dashboard")

        def create_new_profile(e):
            nonlocal active_profile
            name_val = new_name_input.value.strip()
            lang_val = lang_dropdown.value or "Englisch"
            use_defaults = default_vocab_checkbox.value

            if name_val:
                existing = next(
                    (p for p in profiles if p.name.lower() == name_val.lower()), None
                )
                if existing:
                    active_profile = existing
                else:
                    initial_words = (
                        generate_starter_words(lang_val) if use_defaults else []
                    )
                    new_p = UserProfile(
                        name=name_val, language=lang_val, words=initial_words
                    )
                    profiles.append(new_p)
                    active_profile = new_p

                page.theme_mode = (
                    ft.ThemeMode.DARK
                    if getattr(active_profile, "dark_mode", True)
                    else ft.ThemeMode.LIGHT
                )
                save_app_data(profiles, active_profile_name=active_profile.name)
                dialog.open = False
                page.update()
                show_view("dashboard")

        profile_controls: list[ft.Control] = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text(p.name, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(
                    f"Zielsprache: {p.language} ({len(p.words)} Vokabeln)"
                ),
                on_click=lambda e, prof=p: select_profile(prof),
                trailing=ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Profil löschen",
                    on_click=lambda e, prof=p: delete_profile(prof),
                    visible=len(profiles) > 1,
                ),
            )
            for p in profiles
        ]

        new_name_input = ft.TextField(
            label="Neuer Profilname", hint_text="z. B. Nadine", dense=True
        )
        lang_dropdown = ft.Dropdown(
            label="Zielsprache",
            value="Spanisch",
            options=[
                ft.dropdown.Option("Spanisch"),
                ft.dropdown.Option("Englisch"),
                ft.dropdown.Option("Französisch"),
                ft.dropdown.Option("Italienisch"),
            ],
            dense=True,
        )
        default_vocab_checkbox = ft.Checkbox(
            label="Mit Standard-Vokabeln starten",
            value=True,
        )

        btn_create = ft.ElevatedButton(
            content=ft.Text("Profil anlegen"),
            on_click=create_new_profile,
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Profile & Sprachen"),
            content=ft.Column(
                controls=[
                    ft.Text("Vorhandene Profile:", weight=ft.FontWeight.BOLD, size=14),
                    *profile_controls,
                    ft.Divider(),
                    ft.Text(
                        "Neues Profil anlegen:", weight=ft.FontWeight.BOLD, size=14
                    ),
                    new_name_input,
                    lang_dropdown,
                    default_vocab_checkbox,
                    btn_create,
                ],
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    show_view("dashboard")


ft.run(main)
