import flet as ft
from core.models import UserProfile, Word
from data.storage import save_app_data


class WordListView(ft.Container):
    """Zeigt alle Vokabeln mit Live-Suche, Bearbeitungs-Dialog und Löschfunktion an."""

    def __init__(self, profile: UserProfile, all_profiles: list[UserProfile], on_back):
        super().__init__()
        self.profile = profile
        self.all_profiles = all_profiles
        self.on_back = on_back

        # 1. Such-Eingabefeld
        self.search_input = ft.TextField(
            hint_text="Vokabel suchen (Deutsch oder Fremdsprache)...",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            width=340,
            on_change=self.filter_words,
        )

        # 2. Scrollbare Spalte für Vokabelkacheln
        self.words_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=8,
        )

        # 3. Header mit dynamischem Zähler
        self.header_text = ft.Text(
            value="",
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # 4. Zurück-Button
        self.back_btn = ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ARROW_BACK),
                    ft.Text("Zurück zum Hauptmenü"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            on_click=lambda e: self.on_back(),
        )

        # 5. Gesamtes Layout
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            expand=True,
            controls=[
                self.header_text,
                self.search_input,
                ft.Container(
                    content=self.words_column,
                    width=340,
                    height=400,
                    border=ft.Border.all(1, ft.Colors.GREY_800),
                    border_radius=10,
                    padding=8,
                ),
                self.back_btn,
            ],
        )

        self.display_words(self.profile.words)

    def display_words(self, words_to_show: list[Word]):
        """Baut die Liste der Kacheln mit Bearbeiten- und Löschen-Buttons auf."""
        self.words_column.controls.clear()
        self.header_text.value = f"Alle Vokabeln ({len(self.profile.words)})"

        if not words_to_show:
            self.words_column.controls.append(
                ft.Container(
                    content=ft.Text(
                        "Keine passenden Vokabeln gefunden.",
                        italic=True,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=20,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            for word in words_to_show:
                self.words_column.controls.append(
                    ft.ListTile(
                        leading=ft.Container(
                            content=ft.Text(
                                f"K{word.box}",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_400,
                            ),
                            bgcolor=ft.Colors.GREY_900,
                            padding=6,
                            border_radius=6,
                        ),
                        title=ft.Text(
                            f"{word.front} ➔ {word.back}", weight=ft.FontWeight.W_500
                        ),
                        subtitle=ft.Text(
                            f"Fällig: {word.due_date}",
                            size=12,
                            color=ft.Colors.GREY_600,
                        ),
                        trailing=ft.Row(
                            tight=True,
                            spacing=0,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_color=ft.Colors.BLUE_300,
                                    tooltip="Vokabel bearbeiten",
                                    on_click=lambda e, w=word: self.open_edit_dialog(w),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Vokabel löschen",
                                    on_click=lambda e, w=word: self.delete_word(w),
                                ),
                            ],
                        ),
                    )
                )

    def filter_words(self, e):
        """Filtert die angezeigten Vokabeln live beim Tippen."""
        query = self.search_input.value.strip().lower()

        if not query:
            self.display_words(self.profile.words)
        else:
            filtered = [
                w
                for w in self.profile.words
                if query in w.front.lower() or query in w.back.lower()
            ]
            self.display_words(filtered)

        self.update()

    def open_edit_dialog(self, word: Word):
        """Öffnet ein Dialogfenster zum Bearbeiten des ausgewählten Wortes."""
        edit_front = ft.TextField(
            label="Deutsches Wort",
            value=word.front,
            dense=True,
        )
        edit_back = ft.TextField(
            label=f"Übersetzung ({self.profile.language})",
            value=word.back,
            dense=True,
        )
        edit_box = ft.Dropdown(
            label="Kasten (Stufe)",
            value=str(word.box),
            options=[
                ft.dropdown.Option("1"),
                ft.dropdown.Option("2"),
                ft.dropdown.Option("3"),
                ft.dropdown.Option("4"),
                ft.dropdown.Option("5"),
            ],
            dense=True,
        )

        def save_changes(e):
            new_front = edit_front.value.strip()
            new_back = edit_back.value.strip()
            new_box = int(edit_box.value or word.box)

            if new_front and new_back:
                word.front = new_front
                word.back = new_back
                word.box = new_box

                save_app_data(self.all_profiles, active_profile_name=self.profile.name)
                edit_dialog.open = False
                if self.page:
                    self.page.update()
                self.filter_words(None)

        def close_dialog(e):
            edit_dialog.open = False
            if self.page:
                self.page.update()

        edit_dialog = ft.AlertDialog(
            title=ft.Text("Vokabel bearbeiten"),
            content=ft.Column(
                controls=[edit_front, edit_back, edit_box],
                tight=True,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Abbrechen"), on_click=close_dialog),
                ft.ElevatedButton(content=ft.Text("Speichern"), on_click=save_changes),
            ],
        )

        if self.page:
            self.page.overlay.append(edit_dialog)
            edit_dialog.open = True
            self.page.update()

    def delete_word(self, word_to_delete: Word):
        """Entfernt eine Vokabel, speichert und aktualisiert die Ansicht."""
        self.profile.words.remove(word_to_delete)
        save_app_data(self.all_profiles, active_profile_name=self.profile.name)
        self.filter_words(None)
