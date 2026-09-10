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
    "aussprache_abspielen_tooltip": {
        "Deutsch": "Aussprache abspielen",
        "Englisch": "Play pronunciation",
        "Spanisch": "Reproducir pronunciación",
    },
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
    "treffer_begrenzt": {
        "Deutsch": "Zeige {angezeigt} von {gesamt} Treffern – Suche weiter eingrenzen.",
        "Englisch": "Showing {angezeigt} of {gesamt} matches – refine your search.",
        "Spanisch": "Mostrando {angezeigt} de {gesamt} resultados – afina tu búsqueda.",
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
    "backup_button": {
        "Deutsch": "Vokabeln & Fortschritt sichern",
        "Englisch": "Back up words & progress",
        "Spanisch": "Copiar vocabulario y progreso",
    },
    "backup_erfolgreich": {
        "Deutsch": "Sicherung gespeichert: {dateiname}\nZu finden in der Dateien-App unter „Auf meinem iPhone“ → „VocaBase“.",
        "Englisch": "Backup saved: {dateiname}\nFind it in the Files app under “On My iPhone” → “VocaBase”.",
        "Spanisch": "Copia de seguridad guardada: {dateiname}\nDisponible en la app Archivos, en “En mi iPhone” → “VocaBase”.",
    },
    "tab_allgemein": {
        "Deutsch": "Allgemein",
        "Englisch": "General",
        "Spanisch": "General",
    },
    "tab_erweitert": {
        "Deutsch": "Erweitert",
        "Englisch": "Advanced",
        "Spanisch": "Avanzado",
    },
    "backup_import_button": {
        "Deutsch": "Sicherung importieren",
        "Englisch": "Import backup",
        "Spanisch": "Importar copia de seguridad",
    },
    "sprachdaten_laden_button": {
        "Deutsch": "Sprachdaten laden",
        "Englisch": "Load speech data",
        "Spanisch": "Cargar datos de voz",
    },
    "sprachdaten_status": {
        "Deutsch": "{vorhanden} von {gesamt} Vokabeln mit Aussprache",
        "Englisch": "{vorhanden} of {gesamt} words with pronunciation",
        "Spanisch": "{vorhanden} de {gesamt} palabras con pronunciación",
    },
    "import_dialog_titel": {
        "Deutsch": "VocaBase-Sicherung auswählen",
        "Englisch": "Select VocaBase backup",
        "Spanisch": "Seleccionar copia de seguridad de VocaBase",
    },
    "import_bestaetigung_titel": {
        "Deutsch": "Sicherung wirklich importieren?",
        "Englisch": "Really import this backup?",
        "Spanisch": "¿Importar esta copia de seguridad?",
    },
    "import_bestaetigung_text": {
        "Deutsch": "Die Datei enthält {anzahl_profile} Profil(e): {namen} mit insgesamt {anzahl_vokabeln} Vokabeln.\n\nAlle aktuellen Profile, Vokabeln und der Fortschritt auf diesem Gerät werden dabei unwiderruflich überschrieben.",
        "Englisch": "The file contains {anzahl_profile} profile(s): {namen} with {anzahl_vokabeln} words in total.\n\nAll current profiles, words, and progress on this device will be permanently overwritten.",
        "Spanisch": "El archivo contiene {anzahl_profile} perfil(es): {namen} con un total de {anzahl_vokabeln} palabras.\n\nSe sobrescribirán de forma permanente todos los perfiles, palabras y el progreso actuales de este dispositivo.",
    },
    "import_erfolgreich": {
        "Deutsch": "Sicherung erfolgreich importiert.",
        "Englisch": "Backup imported successfully.",
        "Spanisch": "Copia de seguridad importada con éxito.",
    },
    "import_fehler_ungueltig": {
        "Deutsch": "Diese Datei ist keine gültige VocaBase-Sicherung.",
        "Englisch": "This file is not a valid VocaBase backup.",
        "Spanisch": "Este archivo no es una copia de seguridad de VocaBase válida.",
    },
    "import_keine_dateien_gefunden": {
        "Deutsch": "Keine Sicherungsdatei gefunden. Lege deine .json-Sicherung zuerst über die Dateien-App ab: „Auf meinem iPhone“ → „VocaBase“.",
        "Englisch": "No backup file found. First place your .json backup via the Files app: “On My iPhone” → “VocaBase”.",
        "Spanisch": "No se encontró ninguna copia de seguridad. Primero coloca tu archivo .json mediante la app Archivos: “En mi iPhone” → “VocaBase”.",
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
