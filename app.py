# Donbas-Dashboard – öffentlich, nur Lesen/Suche
# Zeitstrahl wie in der Offline-Version
import json
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="Donbas-Dashboard",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    '<div lang="de" translate="no" class="notranslate" style="display:none">notranslate</div>',
    unsafe_allow_html=True,
)


def _find_events_json():
    base = Path(__file__).parent
    for c in (base / "events.json", base / "data" / "events.json"):
        if c.exists():
            return c
    return None


@st.cache_data
def load_events():
    path = _find_events_json()
    if path is None:
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for e in data:
        e.setdefault("status", "freigegeben")
        e.setdefault("actor", "KONTEXT")
        e.setdefault("tags", [])
        e.setdefault("cross_refs", [])
        e.setdefault("sources", [])
        e.setdefault("fact", e.get("fact") or e.get("background") or "")
        e.setdefault("view_ua_west", "")
        e.setdefault("view_ru", "")
        e.setdefault("streitpunkt", "")
        e.setdefault("short", "")
        e.setdefault("thema", "")
        if not e.get("year"):
            try:
                e["year"] = int(str(e.get("date", "1970"))[:4])
            except Exception:
                e["year"] = 1970
    return data


def event_by_id(events, eid):
    for e in events:
        if e.get("id") == eid:
            return e
    return None


ACTOR_LABELS = {
    "RU": "Russland",
    "UA": "Ukraine",
    "WEST": "NATO / USA / EU",
    "BEIDE": "Wechselseitig",
    "KONTEXT": "Kontext / Struktur",
}
ACTOR_STYLE = {
    "RU": "background:linear-gradient(90deg,#fff 0%,#fff 33%,#0039a6 33%,#0039a6 66%,#d52b1e 66%,#d52b1e 100%); color:#111;",
    "UA": "background:linear-gradient(180deg,#0057b7 0%,#0057b7 50%,#ffd700 50%,#ffd700 100%); color:#111;",
    "WEST": "background:#1e3a5f; color:#fff;",
    "BEIDE": "background:#6b21a8; color:#fff;",
    "KONTEXT": "background:#64748b; color:#fff;",
}


def actor_chip(actor: str) -> str:
    label = ACTOR_LABELS.get(actor, actor)
    style = ACTOR_STYLE.get(actor, ACTOR_STYLE["KONTEXT"])
    return (
        f'<span style="display:inline-block;padding:0.2rem 0.65rem;border-radius:999px;'
        f'font-size:0.75rem;font-weight:600;{style}">{label}</span>'
    )


all_events = [e for e in load_events() if e.get("status", "freigegeben") == "freigegeben"]
all_events = sorted(all_events, key=lambda x: x.get("date") or "")
if not all_events:
    st.error("Keine Ereignisse gefunden. Lege events.json ins Repo-Root oder nach data/events.json.")
    st.stop()

# ---------- Sidebar ----------
st.sidebar.header("Suche & Filter")
search = st.sidebar.text_input("Volltextsuche", placeholder="Titel, Fakt, Lesart ...")
years = sorted(set(int(e.get("year") or 0) for e in all_events))
year_range = st.sidebar.slider(
    "Zeitraum",
    min_value=min(years),
    max_value=max(years),
    value=(min(years), max(years)),
)
st.sidebar.markdown("**Handelnde Seite**")
actor_options = ["RU", "UA", "WEST", "BEIDE", "KONTEXT"]
selected_actors = st.sidebar.multiselect(
    "Seite filtern",
    actor_options,
    format_func=lambda a: ACTOR_LABELS.get(a, a),
    default=[],
)
all_tags = sorted({t for e in all_events for t in (e.get("tags") or [])})
selected_tags = st.sidebar.multiselect("Themen / Tags", all_tags)
st.sidebar.markdown("---")
st.sidebar.markdown("**Legende**")
for a in actor_options:
    st.sidebar.markdown(actor_chip(a), unsafe_allow_html=True)

# ---------- Filter ----------
events = []
q = (search or "").strip().lower()
for e in all_events:
    y = int(e.get("year") or 0)
    if y < year_range[0] or y > year_range[1]:
        continue
    if selected_actors and e.get("actor") not in selected_actors:
        continue
    if selected_tags and not set(selected_tags) & set(e.get("tags") or []):
        continue
    if q:
        blob = " ".join(
            [
                str(e.get("title") or ""),
                str(e.get("thema") or ""),
                str(e.get("short") or ""),
                str(e.get("fact") or ""),
                str(e.get("view_ua_west") or ""),
                str(e.get("view_ru") or ""),
                str(e.get("streitpunkt") or ""),
                " ".join(e.get("tags") or []),
            ]
        ).lower()
        if q not in blob:
            continue
    events.append(e)

if not events:
    st.warning("Keine Ereignisse für diese Filter.")
    st.stop()

# ---------- Fokus / Zeitstrahl ----------
if "focus_id" not in st.session_state:
    st.session_state.focus_id = events[-1]["id"]
ids = [e["id"] for e in events]
if st.session_state.focus_id not in ids:
    st.session_state.focus_id = events[-1]["id"]
focus_idx = ids.index(st.session_state.focus_id)
selected = events[focus_idx]
sel_actor = selected.get("actor") or "KONTEXT"

st.markdown(
    """
<style>
.progress-track { height:6px; background:#e2e8f0; border-radius:99px; margin:0.4rem 0 1rem 0; overflow:hidden; }
.progress-fill { height:100%; background:linear-gradient(90deg,#3b82f6,#1d4ed8); border-radius:99px; }
.focus-card {
  background:linear-gradient(145deg,#1e3a8a 0%,#1d4ed8 100%); color:#fff;
  border-radius:14px; padding:1.1rem 1.3rem; margin:0.6rem 0 1rem 0;
  box-shadow:0 8px 24px rgba(29,78,216,0.22);
}
.focus-card h2 { margin:0.2rem 0 0.35rem 0; font-size:1.35rem; line-height:1.3; color:#fff; }
.focus-card .meta { font-size:0.85rem; opacity:0.9; margin-bottom:0.45rem; }
div[data-testid="stHorizontalBlock"] button {
  white-space:pre-line; text-align:left; font-size:0.78rem; min-height:4.2rem; line-height:1.25;
}
div[data-testid="stTextArea"] textarea {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  background-color: #ffffff !important;
  opacity: 1 !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 10px !important;
  font-size: 1rem !important;
  line-height: 1.55 !important;
  caret-color: transparent !important;
}
div[data-testid="stTextArea"] textarea:disabled {
  color: #0f172a !important;
  -webkit-text-fill-color: #0f172a !important;
  background-color: #ffffff !important;
  opacity: 1 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("Donbas-Konflikt")
st.caption("Fakt · Ukrainisch/westliche Lesart · Russische Lesart · Streitpunkt")

pct = int((focus_idx / max(1, len(events) - 1)) * 100) if len(events) > 1 else 100
st.markdown(
    f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>',
    unsafe_allow_html=True,
)

n1, n2, n3, n4 = st.columns([1, 1, 4, 1])
with n1:
    if st.button("← Älter", use_container_width=True, disabled=focus_idx == 0):
        st.session_state.focus_id = events[focus_idx - 1]["id"]
        st.rerun()
with n2:
    if st.button("Neuer →", use_container_width=True, disabled=focus_idx >= len(events) - 1):
        st.session_state.focus_id = events[focus_idx + 1]["id"]
        st.rerun()
with n3:
    labels = [f"{e['date']}  ·  {e['title']}" for e in events]
    choice = st.selectbox(
        "Sprungmarke",
        range(len(events)),
        index=focus_idx,
        format_func=lambda i: labels[i],
        label_visibility="collapsed",
    )
    if choice != focus_idx:
        st.session_state.focus_id = events[choice]["id"]
        st.rerun()
with n4:
    st.markdown(
        f"<div style='text-align:right;padding-top:0.55rem;color:#64748b;font-size:0.9rem'>"
        f"{focus_idx+1} / {len(events)}</div>",
        unsafe_allow_html=True,
    )

# Nachbar-Kacheln (Zeitstrahl)
window = 3
start = max(0, focus_idx - window)
end = min(len(events), focus_idx + window + 1)
neighbors = events[start:end]
cols = st.columns(len(neighbors))
for i, ev in enumerate(neighbors):
    is_focus = ev["id"] == selected["id"]
    with cols[i]:
        d = ev.get("date") or ""
        try:
            short_date = d[8:10] + "." + d[5:7] + "." + d[2:4]
        except Exception:
            short_date = d
        label = f"{'● ' if is_focus else ''}{short_date}\n{(ev.get('title') or '')[:36]}"
        if st.button(
            label,
            key=f"nb_{ev['id']}",
            use_container_width=True,
            type="primary" if is_focus else "secondary",
        ):
            st.session_state.focus_id = ev["id"]
            st.rerun()

_title = (selected.get("title") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
_thema = (selected.get("thema") or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
st.markdown(
    f"""
<div class="focus-card">
  {actor_chip(sel_actor)}
  <div class="meta" style="margin-top:0.5rem">{selected.get('date','')} · {_thema}</div>
  <h2>{_title}</h2>
</div>
""",
    unsafe_allow_html=True,
)

if selected.get("short"):
    st.markdown(selected["short"])

st.subheader("Harter Fakt")
fact = selected.get("fact") or "—"
st.text_area(
    "Harter Fakt",
    value=fact,
    height=min(420, 140 + fact.count("\n") * 18),
    disabled=True,
    label_visibility="collapsed",
)

st.subheader("Lesarten im Vergleich")
col_a, col_b = st.columns(2)
with col_a:
    st.caption("UKRAINISCH / WESTLICH")
    st.info(selected.get("view_ua_west") or "—")
with col_b:
    st.caption("RUSSISCH")
    st.info(selected.get("view_ru") or "—")

if selected.get("streitpunkt"):
    st.subheader("Streitpunkt")
    st.warning(selected["streitpunkt"])

tags = selected.get("tags") or []
if tags:
    st.markdown("**Tags:** " + " · ".join(tags))

refs = selected.get("cross_refs") or []
if refs:
    st.subheader("Im Zusammenhang")
    for rid in refs:
        ref = event_by_id(all_events, rid)
        if not ref:
            continue
        d = ref.get("date") or ""
        try:
            dlab = f"{d[8:10]}.{d[5:7]}.{d[0:4]}"
        except Exception:
            dlab = d
        label = f"{dlab} · {(ref.get('title') or rid)[:70]}"
        if st.button(label, key=f"ref_{selected['id']}_{rid}"):
            if rid in ids:
                st.session_state.focus_id = rid
                st.rerun()
            else:
                st.info(f"Nicht in der aktuellen Filterauswahl: {label}")
