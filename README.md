# Donbas-Dashboard (Streamlit + SQLite)

Interaktives chronologisches Dashboard zum Donbas-Konflikt  
mit 4 Informationstufen, Quellen, Querverweisen und einfacher Redaktionsoberfläche.

Komplett kostenlos und lokal.

## Voraussetzungen
- Python 3.10 oder neuer

## Installation

```bash
cd donbas-dashboard

python -m venv venv

# Windows:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

## Datenbank initialisieren + Beispieldaten importieren

Einmalig ausführen:

```bash
python -m utils.import_json
```

Das erzeugt die Datei `data/db/donbas.db` und füllt sie mit den 11 Beispiel-Ereignissen.

## Starten

```bash
streamlit run app.py
```

Öffnet sich unter **http://localhost:8503**

### Seiten
- **Dashboard** → Chronologische Ansicht, Filter, 4 Stufen, Quellen, Querverweise
- **Admin** → Redaktion (Passwort: `redaktion`)

## Redaktionsrechte

Aktuell gibt es einen einfachen Passwortschutz für den Admin-Bereich.  
Standard-Passwort: **`redaktion`**

Das Passwort kannst du in `pages/2_Admin.py` in der Variable `ADMIN_PASSWORD` ändern.

Später erweiterbar auf mehrere Benutzer / Rollen, wenn gewünscht.

## Datenmodell (SQLite)

- `events` – die 4 Stufen + Status (entwurf / freigegeben)
- `sources` + `event_sources` – Quellen
- `cross_refs` – Querverweise
- `tags` + `event_tags` – Themen
- `clips` – für spätere Video/Audio-Einbindung

## Erweitern

Neue Ereignisse am einfachsten über die **Admin-Seite** anlegen.  
Quellen, Tags und Querverweise können später über zusätzliche Formulare oder direkt per SQL ergänzt werden.

Die alte JSON-Struktur bleibt als Backup / Import-Quelle erhalten.
