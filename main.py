"""main.py

Dies ist die Hauptdatei (Einstiegspunkt) der VocaBase-App.
Sie steuert das Flet-Fenster, lädt die gespeicherten Profile und
verwaltet die Navigation zwischen den einzelnen Bildschirmen (Views).
"""

from datetime import date
import flet as ft

# Import der eigenen Logik- und Daten-Module
from core.models import UserProfile, Word
from data.starter_words import STARTER_PACKS
from data.storage import load_app_data, save_app_data

# Import der einzelnen Benutzeroberflächen (Bildschirme)
from ui.views.add_word import AddWordView
from ui.views.dashboard import DashboardView
from ui.views.practice import PracticeView
from ui.views.word_list import WordListView


def generate_starter_words(language: str) -> list[Word]:
    """Holt die rohen Vokabel-Tupel aus der starter_words.py und baut Word-Objekte daraus.

    :param language: Der exakte Name des Pakets (z.B. "Spanisch Basis A1")
    :return: Eine Liste von fertigen Word-Objekten für Kasten 1.
    """
    # .get(language, []) sucht das Paket. Falls es nicht existiert, wird eine leere Liste zurückgegeben.
    raw_pairs = STARTER_PACKS.get(language, [])
    today_str = str(date.today())

    # List Comprehension: Baut in einer kurzen Schleife für jedes Tupel ein neues Word-Objekt
    return [
        Word(id=idx + 1, front=de, back=foreign, box=1, due_date=today_str)
        for idx, (de, foreign) in enumerate(raw_pairs)
    ]


def main(page: ft.Page):
    """Hauptfunktion, die von Flet beim App-Start aufgerufen wird."""

    # 1. GRUNDEINSTELLUNGEN DES FENSTERS
    page.title = "VocaBase"
    page.window.width = 390
    page.window.height = 720
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 2. DATEN LADEN
    # Wir rufen das "Gedächtnis" der App auf und holen alle Profile
    profiles, active_name = load_app_data()

    # FALLBACK: Wenn die App zum allerersten Mal startet (keine Profile da)
    if not profiles:
        # Hier nutzen wir den NEUEN Schlüssel, der zur CSV-Datei passt!
        philipp_words = generate_starter_words("Englisch Basis A1")
        profil_philipp = UserProfile(
            name="Philipp", language="Englisch Basis A1", words=philipp_words
        )
        profiles = [profil_philipp]
        active_name = "Philipp"
        save_app_data(profiles, active_profile_name=active_name)

    # Das aktive Profil aus der Liste heraussuchen (oder das erste nehmen)
    active_profile = next((p for p in profiles if p.name == active_name), profiles[0])

    # 3. DESIGN FESTLEGEN (Hell oder Dunkel)
    page.theme_mode = (
        ft.ThemeMode.DARK
        if getattr(active_profile, "dark_mode", True)
        else ft.ThemeMode.LIGHT
    )

    # 4. NAVIGATION (ROUTING)
    def show_view(view_name: str):
        """Wechselt den Bildschirm, indem das alte UI gelöscht und das neue geladen wird."""
        page.clean()  # Löscht alles vom Bildschirm

        # Je nach übergebenem String wird die passende UI-Klasse geladen
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

        page.update()  # Zeichnet den Bildschirm neu

    # 5. DIALOGE (Popups)
    def open_settings_dialog():
        """Baut und öffnet den Einstellungsdialog (Fehlversuche, Dark Mode, etc.)."""
        quest_dropdown = ft.Dropdown(
            label="Vokabeln pro Durchgang",
            value=str(getattr(active_profile, "daily_quest_size", 30)),
            options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)],
            dense=True,
        )
        attempts_dropdown = ft.Dropdown(
            label="Fehlversuche beim Schreiben",
            value=str(getattr(active_profile, "max_attempts", 3)),
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            width=280,
        )

        theme_switch = ft.Switch(
            label="Dark Mode",
            value=getattr(active_profile, "dark_mode", True),
        )

        def save_settings(e):
            """Speichert die neuen Einstellungen direkt im aktiven Profil-Objekt."""
            active_profile.daily_quest_size = int(quest_dropdown.value or 30)
            active_profile.max_attempts = int(attempts_dropdown.value or 3)
            active_profile.dark_mode = theme_switch.value

            page.theme_mode = (
                ft.ThemeMode.DARK if active_profile.dark_mode else ft.ThemeMode.LIGHT
            )

            # Daten sofort auf der Festplatte sichern
            save_app_data(profiles, active_profile_name=active_profile.name)
            settings_dialog.open = False
            page.update()
            show_view("dashboard")

        def close_settings(e):
            settings_dialog.open = False
            page.update()

        # Aufbau des Popups
        settings_dialog = ft.AlertDialog(
            title=ft.Text("⚙️ Einstellungen"),
            content=ft.Column(
                controls=[
                    quest_dropdown,
                    attempts_dropdown,
                    theme_switch,
                    ft.Divider(),
                    ft.Text("App-Informationen:", weight=ft.FontWeight.BOLD, size=13),
                    ft.Text("Version: 1.0.1", size=12, color=ft.Colors.GREY_500),
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
        """Baut und öffnet den Dialog zum Wechseln und Anlegen von Profilen."""
        # nonlocal erlaubt es uns, die Variable 'active_profile' aus der main-Funktion zu verändern
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
            # Das letzte Profil darf nicht gelöscht werden
            if len(profiles) <= 1:
                return

            profiles.remove(profile_to_delete)
            # Wenn das aktive Profil gelöscht wird, springen wir auf das erste in der Liste
            if active_profile.name == profile_to_delete.name:
                active_profile = profiles[0]

            save_app_data(profiles, active_profile_name=active_profile.name)
            dialog.open = False
            page.update()
            show_view("dashboard")

        def create_new_profile(e):
            nonlocal active_profile
            name_val = new_name_input.value.strip()
            lang_val = lang_dropdown.value or "Englisch Basis A1"
            use_defaults = default_vocab_checkbox.value

            if name_val:
                # Prüfen, ob der Name schon vergeben ist (Groß-/Kleinschreibung ignorieren)
                existing = next(
                    (p for p in profiles if p.name.lower() == name_val.lower()), None
                )
                if existing:
                    active_profile = existing
                else:
                    # Hier wird beim Anlegen auf unsere csv-Pakete zugegriffen
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

        # Baut die Liste der anklickbaren Profile im Dialog
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

        # HIER SIND DIE NEUEN SPRACH-PAKETE HINTERLEGT
        lang_dropdown = ft.Dropdown(
            label="Zielsprache / Startpaket",
            value="Spanisch Basis A1",
            options=[
                ft.dropdown.Option("Spanisch Basis A1"),
                ft.dropdown.Option("Englisch Basis A1"),
            ],
            dense=True,
        )
        default_vocab_checkbox = ft.Checkbox(
            label="Mit ausgewählten Vokabeln starten",
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

    # Nach App-Start direkt das Dashboard anzeigen
    show_view("dashboard")


# Startet die Flet-Anwendung
ft.run(main)
