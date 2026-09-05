"""core/i18n.py

Übersetzungen für die Bedienoberfläche (Buttons, Labels, Meldungen).
Betrifft ausschließlich die App-Oberfläche - die Vokabelkarten fragen
unabhängig von der App-Sprache immer Deutsch -> Zielsprache ab, da die
Starter-CSVs nur eine deutsche Spalte enthalten.
"""

SPRACHEN = ["Deutsch", "Englisch", "Spanisch"]

_TEXTE: dict[str, dict[str, str]] = {
    # --- Allgemein / mehrfach verwendet ---
    "abbrechen": {"Deutsch": "Abbrechen", "Englisch": "Cancel", "Spanisch": "Cancelar"},
    "speichern": {"Deutsch": "Speichern", "Englisch": "Save", "Spanisch": "Guardar"},
    "zurueck_hauptmenue": {
        "Deutsch": "Zurück zum Hauptmenü",
        "Englisch": "Back to main menu",
        "Spanisch": "Volver al menú principal",
    },
    "deutsches_wort": {
        "Deutsch": "Deutsches Wort",
        "Englisch": "German word",
        "Spanisch": "Palabra en alemán",
    },
    "deutsches_wort_frage": {
        "Deutsch": "Deutsches Wort / Frage",
        "Englisch": "German word / prompt",
        "Spanisch": "Palabra en alemán / pregunta",
    },
    "uebersetzung_sprache": {
        "Deutsch": "Übersetzung ({sprache})",
        "Englisch": "Translation ({sprache})",
        "Spanisch": "Traducción ({sprache})",
    },
    "vokabel_bearbeiten_tooltip": {
        "Deutsch": "Vokabel bearbeiten",
        "Englisch": "Edit word",
        "Spanisch": "Editar vocabulario",
    },
    "vokabel_loeschen_tooltip": {
        "Deutsch": "Vokabel löschen",
        "Englisch": "Delete word",
        "Spanisch": "Eliminar vocabulario",
    },
    "kasten_stufe": {
        "Deutsch": "Kasten (Stufe)",
        "Englisch": "Box (level)",
        "Spanisch": "Casilla (nivel)",
    },
    "vokabel_bearbeiten_titel": {
        "Deutsch": "Vokabel bearbeiten",
        "Englisch": "Edit word",
        "Spanisch": "Editar vocabulario",
    },

    # --- Dashboard ---
    "einstellungen_tooltip": {
        "Deutsch": "Einstellungen",
        "Englisch": "Settings",
        "Spanisch": "Ajustes",
    },
    "begruessung": {
        "Deutsch": "Hallo, {name}! 👋",
        "Englisch": "Hello, {name}! 👋",
        "Spanisch": "¡Hola, {name}! 👋",
    },
    "zielsprache_zeile": {
        "Deutsch": "Zielsprache: {sprache}",
        "Englisch": "Target language: {sprache}",
        "Spanisch": "Idioma objetivo: {sprache}",
    },
    "stat_einheiten_titel": {
        "Deutsch": "🔥 Einheiten",
        "Englisch": "🔥 Sessions",
        "Spanisch": "🔥 Sesiones",
    },
    "stat_einheiten_sub": {
        "Deutsch": "diese Woche",
        "Englisch": "this week",
        "Spanisch": "esta semana",
    },
    "stat_gelernt_titel": {
        "Deutsch": "🧠 Gelernt",
        "Englisch": "🧠 Learned",
        "Spanisch": "🧠 Aprendido",
    },
    "stat_gelernt_sub": {
        "Deutsch": "Kasten 4 & 5",
        "Englisch": "Box 4 & 5",
        "Spanisch": "Casilla 4 y 5",
    },
    "stat_faellig_titel": {
        "Deutsch": "📅 Fällig",
        "Englisch": "📅 Due",
        "Spanisch": "📅 Vencidas",
    },
    "stat_faellig_sub": {
        "Deutsch": "gesamt offen",
        "Englisch": "total open",
        "Spanisch": "total pendiente",
    },
    "btn_uebung": {
        "Deutsch": "Übung ({anzahl} Vokabeln)",
        "Englisch": "Practice ({anzahl} words)",
        "Spanisch": "Ejercicio ({anzahl} palabras)",
    },
    "btn_neue_vokabel": {
        "Deutsch": "Neue Vokabel erfassen",
        "Englisch": "Add new word",
        "Spanisch": "Añadir nueva palabra",
    },
    "btn_vokabeln_verwalten": {
        "Deutsch": "Vokabeln verwalten ({anzahl})",
        "Englisch": "Manage words ({anzahl})",
        "Spanisch": "Gestionar palabras ({anzahl})",
    },
    "btn_profil_wechseln": {
        "Deutsch": "Profil / Sprache wechseln",
        "Englisch": "Switch profile / language",
        "Spanisch": "Cambiar perfil / idioma",
    },

    # --- Übungsansicht (practice.py) ---
    "antwort_eintippen": {
        "Deutsch": "Antwort eintippen...",
        "Englisch": "Type your answer...",
        "Spanisch": "Escribe tu respuesta...",
    },
    "pruefen": {"Deutsch": "Prüfen", "Englisch": "Check", "Spanisch": "Comprobar"},
    "naechste_vokabel": {
        "Deutsch": "Nächste Vokabel",
        "Englisch": "Next word",
        "Spanisch": "Siguiente palabra",
    },
    "richtig": {"Deutsch": "✅ Richtig!", "Englisch": "✅ Correct!", "Spanisch": "✅ ¡Correcto!"},
    "falsch_1_versuch": {
        "Deutsch": "❌ Falsch! Noch 1 Versuch.",
        "Englisch": "❌ Wrong! 1 attempt left.",
        "Spanisch": "❌ ¡Incorrecto! Queda 1 intento.",
    },
    "falsch_n_versuche": {
        "Deutsch": "❌ Falsch! Noch {n} Versuche.",
        "Englisch": "❌ Wrong! {n} attempts left.",
        "Spanisch": "❌ ¡Incorrecto! Quedan {n} intentos.",
    },
    "falsch_endgueltig": {
        "Deutsch": "❌ Leider falsch! Richtige Lösung: {loesung}",
        "Englisch": "❌ Wrong! Correct answer: {loesung}",
        "Spanisch": "❌ ¡Incorrecto! Respuesta correcta: {loesung}",
    },
    "uebung_gemeistert": {
        "Deutsch": "🏆 Übung gemeistert!",
        "Englisch": "🏆 Practice complete!",
        "Spanisch": "🏆 ¡Ejercicio superado!",
    },
    "vokabeln_abgeschlossen": {
        "Deutsch": "{anzahl} Vokabeln erfolgreich abgeschlossen.",
        "Englisch": "{anzahl} words completed successfully.",
        "Spanisch": "{anzahl} palabras completadas con éxito.",
    },
    "zurueck_zum_hauptmenue_btn": {
        "Deutsch": "Zurück zum Hauptmenü",
        "Englisch": "Back to main menu",
        "Spanisch": "Volver al menú principal",
    },
    "fertig": {"Deutsch": "Fertig", "Englisch": "Done", "Spanisch": "Listo"},

    # --- Vokabel hinzufügen (add_word.py) ---
    "neue_vokabel_titel": {
        "Deutsch": "Neue Vokabel ({sprache})",
        "Englisch": "New word ({sprache})",
        "Spanisch": "Nueva palabra ({sprache})",
    },
    "vokabel_speichern": {
        "Deutsch": "Vokabel speichern",
        "Englisch": "Save word",
        "Spanisch": "Guardar palabra",
    },
    "fehler_felder_leer": {
        "Deutsch": "Bitte fülle beide Felder aus!",
        "Englisch": "Please fill in both fields!",
        "Spanisch": "¡Por favor, rellena ambos campos!",
    },
    "fehler_duplikat": {
        "Deutsch": "'{wort}' existiert bereits in deiner Liste!",
        "Englisch": "'{wort}' already exists in your list!",
        "Spanisch": "¡'{wort}' ya existe en tu lista!",
    },
    "erfolg_hinzugefuegt": {
        "Deutsch": "'{front}' -> '{back}' erfolgreich hinzugefügt!",
        "Englisch": "'{front}' -> '{back}' added successfully!",
        "Spanisch": "¡'{front}' -> '{back}' añadido con éxito!",
    },

    # --- Vokabelliste (word_list.py) ---
    "suche_hint": {
        "Deutsch": "Vokabel suchen (Deutsch oder Fremdsprache)...",
        "Englisch": "Search word (German or foreign language)...",
        "Spanisch": "Buscar palabra (alemán o idioma extranjero)...",
    },
    "alle_vokabeln_titel": {
        "Deutsch": "Alle Vokabeln ({anzahl})",
        "Englisch": "All words ({anzahl})",
        "Spanisch": "Todas las palabras ({anzahl})",
    },
    "keine_treffer": {
        "Deutsch": "Keine passenden Vokabeln gefunden.",
        "Englisch": "No matching words found.",
        "Spanisch": "No se encontraron palabras coincidentes.",
    },
    "faellig_am": {
        "Deutsch": "Fällig: {datum}",
        "Englisch": "Due: {datum}",
        "Spanisch": "Vence: {datum}",
    },

    # --- Einstellungsdialog (main.py) ---
    "einstellungen_titel": {
        "Deutsch": "⚙️ Einstellungen",
        "Englisch": "⚙️ Settings",
        "Spanisch": "⚙️ Ajustes",
    },
    "vokabeln_pro_durchgang": {
        "Deutsch": "Vokabeln pro Durchgang",
        "Englisch": "Words per round",
        "Spanisch": "Palabras por ronda",
    },
    "fehlversuche_label": {
        "Deutsch": "Fehlversuche beim Schreiben",
        "Englisch": "Allowed mistakes while typing",
        "Spanisch": "Intentos fallidos permitidos",
    },
    "dark_mode": {"Deutsch": "Dark Mode", "Englisch": "Dark mode", "Spanisch": "Modo oscuro"},
    "app_sprache_label": {
        "Deutsch": "App-Sprache",
        "Englisch": "App language",
        "Spanisch": "Idioma de la app",
    },
    "app_informationen": {
        "Deutsch": "App-Informationen:",
        "Englisch": "App information:",
        "Spanisch": "Información de la app:",
    },
    "version_zeile": {
        "Deutsch": "Version: {version}",
        "Englisch": "Version: {version}",
        "Spanisch": "Versión: {version}",
    },
    "entwickler_zeile": {
        "Deutsch": "Entwickler: {name}",
        "Englisch": "Developer: {name}",
        "Spanisch": "Desarrollador: {name}",
    },
    "copyright_zeile": {
        "Deutsch": "© {jahr} Alle Rechte vorbehalten",
        "Englisch": "© {jahr} All rights reserved",
        "Spanisch": "© {jahr} Todos los derechos reservados",
    },

    # --- Profildialog (main.py) ---
    "profile_sprachen_titel": {
        "Deutsch": "Profile & Sprachen",
        "Englisch": "Profiles & Languages",
        "Spanisch": "Perfiles e idiomas",
    },
    "vorhandene_profile": {
        "Deutsch": "Vorhandene Profile:",
        "Englisch": "Existing profiles:",
        "Spanisch": "Perfiles existentes:",
    },
    "profil_subtitle": {
        "Deutsch": "Zielsprache: {sprache} ({anzahl} Vokabeln)",
        "Englisch": "Target language: {sprache} ({anzahl} words)",
        "Spanisch": "Idioma objetivo: {sprache} ({anzahl} palabras)",
    },
    "profil_loeschen_tooltip": {
        "Deutsch": "Profil löschen",
        "Englisch": "Delete profile",
        "Spanisch": "Eliminar perfil",
    },
    "neuer_profilname_label": {
        "Deutsch": "Neuer Profilname",
        "Englisch": "New profile name",
        "Spanisch": "Nombre del nuevo perfil",
    },
    "neuer_profilname_hint": {
        "Deutsch": "z. B. Nadine",
        "Englisch": "e.g. Nadine",
        "Spanisch": "p. ej. Nadine",
    },
    "zielsprache_startpaket_label": {
        "Deutsch": "Zielsprache / Startpaket",
        "Englisch": "Target language / starter pack",
        "Spanisch": "Idioma objetivo / paquete inicial",
    },
    "mit_starter_vokabeln": {
        "Deutsch": "Mit Starter-Vokabeln beginnen",
        "Englisch": "Start with starter words",
        "Spanisch": "Empezar con vocabulario inicial",
    },
    "neues_profil_anlegen": {
        "Deutsch": "Neues Profil anlegen:",
        "Englisch": "Create new profile:",
        "Spanisch": "Crear nuevo perfil:",
    },
    "profil_anlegen_btn": {
        "Deutsch": "Profil anlegen",
        "Englisch": "Create profile",
        "Spanisch": "Crear perfil",
    },
}


def t(schluessel: str, ui_sprache: str = "Deutsch", **werte) -> str:
    """Gibt den übersetzten Text für `schluessel` in `ui_sprache` zurück.

    Fällt auf Deutsch zurück, wenn die Sprache oder der Schlüssel fehlt
    (z. B. bei einem Tippfehler oder einer noch nicht übersetzten
    Zeichenkette), damit die App nie mit einer KeyError abstürzt.
    Übergebene **werte werden per str.format() eingesetzt, z. B.
    t("begruessung", ui_sprache, name="Nadine"). Der Parametername
    'ui_sprache' (statt z. B. 'sprache') vermeidet bewusst eine Kollision
    mit Platzhaltern wie {sprache}, die selbst als **werte übergeben werden
    (z. B. bei "zielsprache_zeile", das {sprache}=Zielsprache erwartet).
    """
    eintrag = _TEXTE.get(schluessel, {})
    text = eintrag.get(ui_sprache) or eintrag.get("Deutsch") or schluessel
    return text.format(**werte) if werte else text
