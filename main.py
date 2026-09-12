"""main.py

Dies ist die Hauptdatei (Einstiegspunkt) der VocaBase-App.
Sie steuert das Flet-Fenster, lädt die gespeicherten Profile und
verwaltet die Navigation zwischen den einzelnen Bildschirmen (Views).
"""

import asyncio
import json
import pathlib
from datetime import date, datetime
import flet as ft

# Import der eigenen Logik- und Daten-Module
from core.audio import has_audio, save_downloaded_audio
from core.i18n import SPRACHEN, t
from core.models import UserProfile, Word
from core.tts_client import TTSFehler, load_tts_config, save_tts_config, synthesize
from data.starter_words import STARTER_PACKS
from data.storage import DATA_FILE, DOCUMENTS_DIR, load_app_data, save_app_data

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
        lang = getattr(active_profile, "ui_language", "Deutsch")

        quest_dropdown = ft.Dropdown(
            label=t("vokabeln_pro_durchgang", lang),
            value=str(getattr(active_profile, "daily_quest_size", 30)),
            options=[ft.dropdown.Option(str(i)) for i in range(10, 101, 10)],
            dense=True,
        )
        attempts_dropdown = ft.Dropdown(
            label=t("fehlversuche_label", lang),
            value=str(getattr(active_profile, "max_attempts", 3)),
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
            width=280,
        )

        sprache_dropdown = ft.Dropdown(
            label=t("app_sprache_label", lang),
            value=lang,
            options=[ft.dropdown.Option(s) for s in SPRACHEN],
            dense=True,
        )

        theme_switch = ft.Switch(
            label=t("dark_mode", lang),
            value=getattr(active_profile, "dark_mode", True),
        )

        def export_backup(e):
            """Speichert eine datierte Kopie von app_data.json direkt im
            Dokumente-Ordner der App - dank UIFileSharingEnabled (siehe
            pyproject.toml) bereits in der iOS Dateien-App sichtbar.

            Nutzt bewusst kein ft.Share: dessen native Umsetzung reagiert auf
            iOS aktuell nicht (dauerhafter 10-Sekunden-Timeout bei
            share_files, auch mit gesetztem share_position_origin - ein
            offenbar noch offener Flet-Bug). Von hier aus kann der Nutzer die
            Datei über den nativen Teilen-Button der Dateien-App selbst
            weiterleiten (Mail, AirDrop, ...) oder sie direkt wieder über
            'Sicherung importieren' einspielen."""
            dateiname = f"vocabase_sicherung_{date.today()}.json"
            save_app_data(
                profiles,
                active_profile_name=active_profile.name,
                filepath=str(pathlib.Path(DOCUMENTS_DIR) / dateiname),
            )

            snackbar = ft.SnackBar(
                content=ft.Text(t("backup_erfolgreich", lang, dateiname=dateiname)),
                open=True,
            )
            page.overlay.append(snackbar)
            page.update()

        def show_import_confirmation(daten: dict, rohe_profile: list):
            """Zeigt die Sicherheitsabfrage vor dem eigentlichen Import und
            ersetzt bei Bestätigung alle aktuellen Profile, Vokabeln und den
            Fortschritt auf diesem Gerät durch die importierten Daten."""
            namen = ", ".join(p.get("name", "?") for p in rohe_profile)
            anzahl_vokabeln = sum(len(p.get("words", [])) for p in rohe_profile)

            def apply_import(e):
                nonlocal active_profile
                imported_profiles = [UserProfile.from_dict(p) for p in rohe_profile]

                # In-Place-Mutation statt Neuzuweisung: Andere Closures (show_view,
                # der Profile-Tab im Einstellungsdialog, ...) halten dieselbe
                # Listen-Referenz und sehen die neuen Daten dadurch automatisch.
                profiles.clear()
                profiles.extend(imported_profiles)

                gewuenschter_name = daten.get("active_profile")
                active_profile = next(
                    (p for p in profiles if p.name == gewuenschter_name), profiles[0]
                )
                page.theme_mode = (
                    ft.ThemeMode.DARK
                    if getattr(active_profile, "dark_mode", True)
                    else ft.ThemeMode.LIGHT
                )
                save_app_data(profiles, active_profile_name=active_profile.name)

                confirm_dialog.open = False
                settings_dialog.open = False
                show_view("dashboard")

                snackbar = ft.SnackBar(
                    content=ft.Text(t("import_erfolgreich", lang)), open=True
                )
                page.overlay.append(snackbar)
                page.update()

            def cancel_import(e):
                confirm_dialog.open = False
                page.update()

            confirm_dialog = ft.AlertDialog(
                title=ft.Text(t("import_bestaetigung_titel", lang)),
                content=ft.Text(
                    t(
                        "import_bestaetigung_text",
                        lang,
                        anzahl_profile=len(rohe_profile),
                        namen=namen,
                        anzahl_vokabeln=anzahl_vokabeln,
                    )
                ),
                actions=[
                    ft.TextButton(
                        content=ft.Text(t("abbrechen", lang)), on_click=cancel_import
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(t("backup_import_button", lang)),
                        on_click=apply_import,
                    ),
                ],
            )
            page.overlay.append(confirm_dialog)
            confirm_dialog.open = True
            page.update()

        def import_backup(e):
            """Zeigt alle .json-Sicherungsdateien, die der Nutzer zuvor manuell
            über die iOS Dateien-App ('Auf meinem iPhone' -> 'VocaBase') in den
            Dokumente-Ordner der App gelegt hat, zur Auswahl an.

            Nutzt bewusst kein ft.FilePicker: dessen natives Plugin wird in
            aktuellen Flet-Versionen auf iOS nicht registriert ('Unknown
            control: FilePicker'), während der Dokumente-Ordner dank
            UIFileSharingEnabled (siehe pyproject.toml) ohnehin schon direkt
            durchsuchbar ist."""
            eigener_dateiname = pathlib.Path(DATA_FILE).name
            gefundene_dateien = sorted(
                (
                    p
                    for p in pathlib.Path(DOCUMENTS_DIR).glob("*.json")
                    if p.name != eigener_dateiname
                ),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            if not gefundene_dateien:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("import_keine_dateien_gefunden", lang)),
                    open=True,
                )
                page.overlay.append(snackbar)
                page.update()
                return

            def close_file_dialog(e):
                file_dialog.open = False
                page.update()

            def select_file(pfad: pathlib.Path):
                try:
                    daten = json.loads(pfad.read_text(encoding="utf-8"))
                    rohe_profile = daten["profiles"]
                    if not isinstance(rohe_profile, list):
                        raise ValueError
                except (
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                    KeyError,
                    ValueError,
                ):
                    file_dialog.open = False
                    snackbar = ft.SnackBar(
                        content=ft.Text(t("import_fehler_ungueltig", lang)), open=True
                    )
                    page.overlay.append(snackbar)
                    page.update()
                    return

                file_dialog.open = False
                page.update()
                show_import_confirmation(daten, rohe_profile)

            file_dialog = ft.AlertDialog(
                title=ft.Text(t("import_dialog_titel", lang)),
                content=ft.Column(
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.DESCRIPTION_OUTLINED),
                            title=ft.Text(p.name),
                            subtitle=ft.Text(
                                datetime.fromtimestamp(p.stat().st_mtime).strftime(
                                    "%Y-%m-%d %H:%M"
                                )
                            ),
                            on_click=lambda e, pfad=p: select_file(pfad),
                        )
                        for p in gefundene_dateien
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                actions=[
                    ft.TextButton(
                        content=ft.Text(t("abbrechen", lang)),
                        on_click=close_file_dialog,
                    ),
                ],
            )
            page.overlay.append(file_dialog)
            file_dialog.open = True
            page.update()

        def berechne_sprachdaten_status() -> str:
            """Zählt, für wie viele Vokabeln des aktiven Profils bereits eine
            Aussprache-Audiodatei vorbereitet ist - deckt sowohl die
            ausgelieferten Basispakete (Englisch/Spanisch) als auch per
            ElevenLabs nachgeladene eigene Vokabeln ab (siehe has_audio())."""
            vorhandene = sum(
                1
                for w in active_profile.words
                if has_audio(active_profile.language, w.back)
            )
            return t(
                "sprachdaten_status",
                lang,
                vorhanden=vorhandene,
                gesamt=len(active_profile.words),
            )

        sprachdaten_status_text = ft.Text(
            berechne_sprachdaten_status(), size=12, color=ft.Colors.GREY_500
        )

        # ElevenLabs-Zugangsdaten: API-Key + je eine Voice-ID pro Sprache,
        # vorbefüllt aus tts_config.json (siehe core/tts_client.py). Wird
        # zusammen mit den übrigen Einstellungen über den "Speichern"-Button
        # des Dialogs persistiert (siehe save_settings unten).
        # autocorrect=False + capitalization=NONE: API-Keys/Voice-IDs sind
        # exakte, groß-/kleinschreibungsempfindliche Zeichenfolgen - ohne das
        # kann iOS' Autokorrektur/Großschreibung unbemerkt ein Zeichen
        # verändern (bei einem passwortmaskierten Feld sieht man das nicht).
        tts_config = load_tts_config()
        tts_key_field = ft.TextField(
            label=t("tts_api_key_label", lang),
            value=tts_config["api_key"],
            password=True,
            can_reveal_password=False,
            autocorrect=False,
            capitalization=ft.TextCapitalization.NONE,
            dense=True,
        )
        tts_voice_en_field = ft.TextField(
            label=t("tts_voice_id_englisch_label", lang),
            value=tts_config["voice_ids"]["Englisch Basis A1"],
            autocorrect=False,
            capitalization=ft.TextCapitalization.NONE,
            dense=True,
        )
        tts_voice_es_field = ft.TextField(
            label=t("tts_voice_id_spanisch_label", lang),
            value=tts_config["voice_ids"]["Spanisch Basis A1"],
            autocorrect=False,
            capitalization=ft.TextCapitalization.NONE,
            dense=True,
        )

        async def sprachdaten_laden(e):
            """Lädt Aussprache für alle Vokabeln des aktiven Profils nach, die
            noch keine haben - in der Praxis betrifft das nur selbst
            hinzugefügte Vokabeln, das Basispaket ist bereits vollständig
            abgedeckt (has_audio() liefert dafür schon True). Aktualisiert
            die Übersicht nach JEDEM Wort live, nicht erst am Ende."""
            fehlende = [
                w
                for w in active_profile.words
                if not has_audio(active_profile.language, w.back)
            ]

            if not fehlende:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("sprachdaten_nichts_fehlt", lang)), open=True
                )
                page.overlay.append(snackbar)
                page.update()
                return

            api_key = tts_key_field.value.strip()
            voice_id = {
                "Englisch Basis A1": tts_voice_en_field.value.strip(),
                "Spanisch Basis A1": tts_voice_es_field.value.strip(),
            }.get(active_profile.language, "")

            if not api_key or not voice_id:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("sprachdaten_kein_key", lang)), open=True
                )
                page.overlay.append(snackbar)
                page.update()
                return

            erfolgreich = 0
            fehlgeschlagen = 0
            for word in fehlende:
                try:
                    audio_bytes = await asyncio.to_thread(
                        synthesize,
                        word.back,
                        active_profile.language,
                        api_key,
                        voice_id,
                    )
                    save_downloaded_audio(
                        active_profile.language, word.back, audio_bytes
                    )
                    erfolgreich += 1
                except TTSFehler:
                    fehlgeschlagen += 1

                # Live-Aktualisierung nach jedem Wort statt nur am Ende.
                sprachdaten_status_text.value = berechne_sprachdaten_status()
                page.update()

            if fehlgeschlagen:
                meldung = t(
                    "sprachdaten_teilweise",
                    lang,
                    erfolgreich=erfolgreich,
                    fehlgeschlagen=fehlgeschlagen,
                )
            else:
                meldung = t("sprachdaten_erfolgreich", lang, anzahl=erfolgreich)
            snackbar = ft.SnackBar(content=ft.Text(meldung), open=True)
            page.overlay.append(snackbar)
            page.update()

        def save_settings(e):
            """Speichert die neuen Einstellungen direkt im aktiven Profil-Objekt."""
            active_profile.daily_quest_size = int(quest_dropdown.value or 30)
            active_profile.max_attempts = int(attempts_dropdown.value or 3)
            active_profile.dark_mode = theme_switch.value
            active_profile.ui_language = sprache_dropdown.value or "Deutsch"

            page.theme_mode = (
                ft.ThemeMode.DARK if active_profile.dark_mode else ft.ThemeMode.LIGHT
            )

            # Daten sofort auf der Festplatte sichern
            save_app_data(profiles, active_profile_name=active_profile.name)
            save_tts_config(
                tts_key_field.value.strip(),
                {
                    "Englisch Basis A1": tts_voice_en_field.value.strip(),
                    "Spanisch Basis A1": tts_voice_es_field.value.strip(),
                },
            )
            settings_dialog.open = False
            page.update()
            show_view("dashboard")

        def close_settings(e):
            settings_dialog.open = False
            page.update()

        # Reiter "Profile": Profil wechseln/löschen/anlegen (früher ein eigener
        # Dialog, siehe open_profile_dialog in einer älteren Version dieser Datei).
        def select_profile(selected_profile: UserProfile):
            nonlocal active_profile
            active_profile = selected_profile
            page.theme_mode = (
                ft.ThemeMode.DARK
                if getattr(active_profile, "dark_mode", True)
                else ft.ThemeMode.LIGHT
            )
            save_app_data(profiles, active_profile_name=active_profile.name)
            settings_dialog.open = False
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
            settings_dialog.open = False
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
                settings_dialog.open = False
                page.update()
                show_view("dashboard")

        # Baut die Liste der anklickbaren Profile im Dialog
        profile_controls: list[ft.Control] = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text(p.name, weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(
                    t(
                        "profil_subtitle",
                        lang,
                        sprache=p.language,
                        anzahl=len(p.words),
                    )
                ),
                on_click=lambda e, prof=p: select_profile(prof),
                trailing=ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color=ft.Colors.RED_400,
                    tooltip=t("profil_loeschen_tooltip", lang),
                    on_click=lambda e, prof=p: delete_profile(prof),
                    visible=len(profiles) > 1,
                ),
            )
            for p in profiles
        ]

        new_name_input = ft.TextField(
            label=t("neuer_profilname_label", lang),
            hint_text=t("neuer_profilname_hint", lang),
            dense=True,
        )

        # HIER SIND DIE NEUEN SPRACH-PAKETE HINTERLEGT
        lang_dropdown = ft.Dropdown(
            label=t("zielsprache_startpaket_label", lang),
            value="Spanisch Basis A1",
            options=[
                ft.dropdown.Option("Spanisch Basis A1"),
                ft.dropdown.Option("Englisch Basis A1"),
            ],
            dense=True,
        )
        default_vocab_checkbox = ft.Checkbox(
            label=t("mit_starter_vokabeln", lang),
            value=True,
        )

        btn_create = ft.ElevatedButton(
            content=ft.Text(t("profil_anlegen_btn", lang)),
            on_click=create_new_profile,
        )

        profile_tab_content = ft.Container(
            padding=ft.Padding(left=0, top=16, right=0, bottom=0),
            content=ft.Column(
                controls=[
                    ft.Text(
                        t("vorhandene_profile", lang),
                        weight=ft.FontWeight.BOLD,
                        size=14,
                    ),
                    *profile_controls,
                    ft.Divider(),
                    ft.Text(
                        t("neues_profil_anlegen", lang),
                        weight=ft.FontWeight.BOLD,
                        size=14,
                    ),
                    new_name_input,
                    lang_dropdown,
                    default_vocab_checkbox,
                    btn_create,
                ],
                spacing=10,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        # Reiter "Allgemein": die bisherigen, direkt speicherbaren Einstellungen
        allgemein_tab_content = ft.Container(
            padding=ft.Padding(left=0, top=16, right=0, bottom=0),
            content=ft.Column(
                controls=[
                    quest_dropdown,
                    attempts_dropdown,
                    sprache_dropdown,
                    theme_switch,
                ],
                spacing=14,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        # Reiter "Erweitert": Datenverwaltung (Export/Import) + App-Infos
        erweitert_tab_content = ft.Container(
            padding=ft.Padding(left=0, top=16, right=0, bottom=0),
            content=ft.Column(
                controls=[
                    ft.OutlinedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.SAVE_ALT),
                                ft.Text(
                                    t("backup_button", lang),
                                    text_align=ft.TextAlign.CENTER,
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        # width=280 + expand=True auf dem Text: der lange Label-Text
                        # ("Vokabeln & Fortschritt sichern") passte bei "tight"-Row
                        # sonst auf echten Geräten nicht in die 320px-Dialogbreite
                        # (RenderFlex-Overflow) - jetzt bricht er stattdessen um.
                        width=280,
                        on_click=export_backup,
                    ),
                    ft.OutlinedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.FILE_OPEN_OUTLINED),
                                ft.Text(
                                    t("backup_import_button", lang),
                                    text_align=ft.TextAlign.CENTER,
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        width=280,
                        on_click=import_backup,
                    ),
                    ft.OutlinedButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.VOLUME_UP_OUTLINED),
                                ft.Text(
                                    t("sprachdaten_laden_button", lang),
                                    text_align=ft.TextAlign.CENTER,
                                    expand=True,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        width=280,
                        on_click=sprachdaten_laden,
                    ),
                    sprachdaten_status_text,
                    ft.Divider(),
                    ft.ExpansionTile(
                        title=ft.Text(
                            t("tts_config_titel", lang),
                            weight=ft.FontWeight.BOLD,
                            size=13,
                        ),
                        controls=[
                            tts_key_field,
                            tts_voice_en_field,
                            tts_voice_es_field,
                        ],
                        expanded=False,
                    ),
                    ft.Divider(),
                    ft.Text(
                        t("app_informationen", lang), weight=ft.FontWeight.BOLD, size=13
                    ),
                    ft.Text(
                        t("version_zeile", lang, version="1.2.2"),
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        t("entwickler_zeile", lang, name="Philipp Edelbrock"),
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Text(
                        t("copyright_zeile", lang, jahr="2026"),
                        size=11,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=10,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
        )

        # Tabs brauchen eine begrenzte Höhe im Elternbaum (siehe unten der
        # umschließende Container mit fester Höhe), da TabBarView mit
        # expand=True sonst einen "unbounded height"-Layout-Fehler auslöst.
        settings_tabs = ft.Tabs(
            length=3,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label=t("tab_allgemein", lang)),
                            ft.Tab(label=t("tab_erweitert", lang)),
                            ft.Tab(label=t("tab_profile", lang)),
                        ],
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            allgemein_tab_content,
                            erweitert_tab_content,
                            profile_tab_content,
                        ],
                    ),
                ],
            ),
        )

        # Aufbau des Popups
        settings_dialog = ft.AlertDialog(
            title=ft.Text(t("einstellungen_titel", lang)),
            content=ft.Container(width=320, height=430, content=settings_tabs),
            actions=[
                ft.TextButton(
                    content=ft.Text(t("abbrechen", lang)), on_click=close_settings
                ),
                ft.ElevatedButton(
                    content=ft.Text(t("speichern", lang)), on_click=save_settings
                ),
            ],
        )

        page.overlay.append(settings_dialog)
        settings_dialog.open = True
        page.update()

    # Nach App-Start direkt das Dashboard anzeigen
    show_view("dashboard")


# Startet die Flet-Anwendung
ft.run(main)
