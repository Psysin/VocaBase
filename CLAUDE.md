# VocaBase – Projektregeln für Claude Code

Spaced-Repetition-Vokabeltrainer (Python 3, Flet 0.86.5), gebaut für iOS
(eigenes Gerät + das der Frau, Nadine). Läuft komplett offline für den
Kern-Lernbetrieb, mit optionalem Online-Nachladen von Aussprache.

## Workflow für größere Features

- Größere/riskante Erweiterungen **nicht direkt auf `main`** entwickeln,
  sondern in einem eigenen `git worktree` + eigenem `feature/<name>`-Branch:
  `git worktree add ../Vokabel_App-<name> -b feature/<name>`.
  Eigene `.venv` im neuen Worktree anlegen, `.claude/launch.json` aus einem
  bestehenden Worktree kopieren (ist gitignored).
- Erst auf `main` mergen, nachdem das Feature auf einem **echten iPhone**
  getestet wurde (siehe unten) und der Nutzer das Merge ausdrücklich will.
  iOS Simulator ist gut für schnelle Iteration, ersetzt aber keinen
  finalen Real-Device-Test bei Audio/Netzwerk-Features.
- Nach erfolgreichem Merge: alte Worktree-Ordner und Branches (lokal +
  auf GitHub) aufräumen, damit nur noch `main` übrig bleibt – aber nur
  nach expliziter Bestätigung durch den Nutzer.
- Commits granular nach Thema trennen (nicht alles in einen Commit),
  Commit-Nachrichten auf Deutsch, Typ-Präfix (`feat:`, `fix:`, `docs:`,
  `chore:`), siehe `git log` für Stil-Vorbild.
- Nur committen/pushen/mergen, wenn der Nutzer das explizit sagt.

## Versionierung

- `pyproject.toml` (`version`), `main.py` (`version_zeile`-Text) und
  `README.md` ("Version:") müssen synchron sein.
- Bei jedem größeren Update (neues Feature, nicht bei Kleinstfixes) die
  Version anheben (z. B. 1.1.0 → 1.2.0).

## Sicherheit: Geheimnisse

- API-Keys (z. B. ElevenLabs) **nie** im Code oder Repo speichern – das
  Repo ist öffentlich auf GitHub. Geheimnisse liegen ausschließlich lokal
  pro Gerät in `~/Documents/tts_config.json` (außerhalb des Projektordners,
  nie eingecheckt).
- Passwortmaskierte Felder für Keys: `can_reveal_password=False` setzen,
  damit niemand den Wert über die UI wieder einsehen kann.
- Nicht-geheime, aber exakte IDs (Voice-IDs u. Ä.) dürfen als Default
  fest im Code hinterlegt werden – erspart erneutes Nachschlagen.

## Bekannte iOS/Flet-Fallstricke

- `Audio`-Control (`flet_audio`) ist ein `Service` → gehört in
  `page.services`, nicht `page.overlay`.
- Rohe `bytes` als `Audio.src` bleiben auf iOS stumm (fehlender
  mime-type in `flet-audio`). Immer Bytes in eine echte Datei schreiben
  und den Dateipfad übergeben.
- `TextField` hat standardmäßig `autocorrect=True` ohne Großschreibungs-
  Kontrolle – bei exakten, case-sensitiven Eingaben (API-Keys, IDs)
  immer `autocorrect=False, capitalization=ft.TextCapitalization.NONE`
  setzen, sonst korrigiert iOS unbemerkt Zeichen (besonders gefährlich
  bei passwortmaskierten Feldern, da man es nicht sieht).
- Neue native Abhängigkeiten (z. B. neue Flutter/CocoaPod-Pakete) brauchen
  `--clear-cache` beim Build; reine Python-Änderungen (stdlib, eigene
  Module) nicht.
- Für Netzwerk-Aufrufe bevorzugt `urllib` (Standardbibliothek) statt
  `requests`, um zusätzliche Abhängigkeiten mit eigener Dependency-Kette
  zu vermeiden (hat beim mobilen Packaging schon anderswo Probleme
  gemacht).

## Persistenz

- Nutzerdaten (`app_data.json`) und Geheimnisse (`tts_config.json`) liegen
  in `~/Documents`, **nicht** im Projektordner – das funktioniert auch
  innerhalb der iOS-Sandbox und übersteht App-Updates (nur ein komplettes
  Deinstallieren löscht es).
- Bestehende Nutzerprofile werden beim App-Start/-Update **nie** neu aus
  den Start-CSVs befüllt oder überschrieben – das passiert nur einmalig
  beim allerersten Start ohne vorhandene `app_data.json`.
