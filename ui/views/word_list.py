"""ui/views/word_list.py

Die Verwaltungsoberfläche: Alle Vokabeln ansehen, durchsuchen,
bearbeiten und löschen.
"""

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

        # 1. SUCHFELD (Live-Filter)
        # on_change triggert bei jedem einzelnen Tastenanschlag sofort filter_words
        self.search_input = ft.TextField(
            hint_text="Vokabel suchen (Deutsch oder Fremdsprache)...",
            prefix_icon=ft.Icons.SEARCH,
            dense=True,
            width=340,
            on_change=self.filter_words,
        )

        # 2. SCROLLBARE LISTE FÜR ERGEBNISSE
        self.words_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,  # Macht die Liste scrollbar, wenn sie länger als der Bildschirm wird
            expand=True,
            spacing=8,
        )

        self.header_text = ft.Text(
            value="", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER
        )

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

        # 3. GESAMTLAYOUT
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            expand=True,
            controls=[
                self.header_text,
                self.search_input,
                # Container fungiert hier als sichtbare "Box" um die Scroll-Liste
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

        # Zum Start alle Vokabeln ungefiltert anzeigen
        self.display_words(self.profile.words)

    def display_words(self, words_to_show: list[Word]):
        """Baut die visuelle Liste (UI) basierend auf einer Vokabelliste neu auf."""
        # Löscht alle alten Kacheln vom Bildschirm
        self.words_column.controls.clear()
        self.header_text.value = f"Alle Vokabeln ({len(self.profile.words)})"

        if not words_to_show:
            # Fallback, wenn Liste leer oder Suche erfolglos
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
            # ListTile ist ein vorgefertigtes Flet-Element, das perfekt für Listen mit
            # Icon links (leading), Text in der Mitte und Buttons rechts (trailing) ist.
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
                                    # Der w=word Trick ist extrem wichtig, damit jeder Button
                                    # sich exakt sein eigenes Wort merkt und nicht das letzte der Schleife!
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
        """Wird bei jedem Tastendruck im Suchfeld aufgerufen."""
        query = self.search_input.value.strip().lower()

        if not query:
            self.display_words(self.profile.words)
        else:
            # List Comprehension: Sammelt alle Wörter, in denen die Suche steckt (in Deutsch oder Fremdsprache)
            filtered = [
                w
                for w in self.profile.words
                if query in w.front.lower() or query in w.back.lower()
            ]
            self.display_words(filtered)

        self.update()

    def open_edit_dialog(self, word: Word):
        """Erstellt und öffnet das Popup zum Bearbeiten einer Vokabel."""

        # Eingabefelder werden mit den aktuellen Werten des Wortes vorbefüllt
        edit_front = ft.TextField(label="Deutsches Wort", value=word.front, dense=True)
        edit_back = ft.TextField(
            label=f"Übersetzung ({self.profile.language})", value=word.back, dense=True
        )
        edit_box = ft.Dropdown(
            label="Kasten (Stufe)",
            value=str(word.box),
            dense=True,
            options=[ft.dropdown.Option(str(i)) for i in range(1, 6)],
        )

        def save_changes(e):
            new_front = edit_front.value.strip()
            new_back = edit_back.value.strip()
            new_box = int(edit_box.value or word.box)

            if new_front and new_back:
                # 1. Überschreibt das originale Word-Objekt im Arbeitsspeicher
                word.front = new_front
                word.back = new_back
                word.box = new_box

                # 2. Sichert die Änderungen auf die Festplatte
                save_app_data(self.all_profiles, active_profile_name=self.profile.name)

                # 3. Schließt den Dialog
                edit_dialog.open = False
                if self.page:
                    self.page.update()

                # 4. Lädt die Liste (inklusive Suchfilter) im Hintergrund neu
                self.filter_words(None)

        def close_dialog(e):
            edit_dialog.open = False
            if self.page:
                self.page.update()

        # Das Popup Fenster
        edit_dialog = ft.AlertDialog(
            title=ft.Text("Vokabel bearbeiten"),
            content=ft.Column(controls=[edit_front, edit_back, edit_box], tight=True),
            actions=[
                ft.TextButton(content=ft.Text("Abbrechen"), on_click=close_dialog),
                ft.ElevatedButton(content=ft.Text("Speichern"), on_click=save_changes),
            ],
        )

        # Ein Popup muss in Flet auf das "Overlay" der Seite gelegt werden,
        # damit es über allen anderen Elementen schwebt.
        if self.page:
            self.page.overlay.append(edit_dialog)
            edit_dialog.open = True
            self.page.update()

    def delete_word(self, word_to_delete: Word):
        """Entfernt eine Vokabel und aktualisiert sofort die Ansicht."""
        self.profile.words.remove(word_to_delete)
        save_app_data(self.all_profiles, active_profile_name=self.profile.name)
        self.filter_words(None)
