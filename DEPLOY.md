# Online stellen (nur Lesen + Suchen) – Streamlit Community Cloud

## Voraussetzungen
- Kostenloses Konto auf [github.com](https://github.com)
- Kostenloses Konto auf [share.streamlit.io](https://share.streamlit.io)

## Schritte

### 1. Projekt auf GitHub
Im Ordner `donbas-dashboard` (lokal):

```bash
git init
git add app.py pages requirements.txt utils data/events.json data/sources.json .streamlit DEPLOY.md README.md .gitignore
git add data/db/donbas.db
git commit -m "Donbas-Dashboard read-only"
```

Neues **öffentliches** Repository auf GitHub anlegen, dann:

```bash
git remote add origin https://github.com/DEIN_USER/donbas-dashboard.git
git branch -M main
git push -u origin main
```

`data/events.json` muss mit hochgeladen werden.  
`data/db/donbas.db` ist optional: Beim ersten Start füllt die App eine leere DB aus der JSON.

**Nicht** committen: `venv/`, Passwörter, `.streamlit/secrets.toml`.

### 2. Streamlit Cloud
1. [share.streamlit.io](https://share.streamlit.io) → **New app**
2. GitHub-Repo und Branch `main` wählen
3. Main file path: `app.py`
4. Deploy

Nach 1–3 Minuten erscheint eine URL wie  
`https://donbas-dashboard-xxxx.streamlit.app`

### 3. Was öffentlich ist
- Seite **Dashboard**: chronologisch lesen, Suche, Filter, Lesarten
- Seite **Admin** ist ausgeblendet (`_2_Admin.py`) – nur lokal wieder nutzbar

### 4. Daten aktualisieren
1. Lokal `data/events.json` pflegen
2. Optional: `python -m utils.import_json`
3. `git add` / `commit` / `push`
4. Streamlit Cloud baut die App neu (oder „Reboot“)

### 5. Falls die Liste leer ist
Einmal im Cloud-Log prüfen, ob `events.json` im Repo liegt.  
Die Funktion `ensure_data()` importiert automatisch, wenn die DB leer ist.

## Hinweis
Free-Tier: App kann nach Inaktivität schlafen und beim ersten Aufruf kurz brauchen.
