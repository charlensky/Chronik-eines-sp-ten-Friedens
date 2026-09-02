# Donbas-Dashboard – öffentlich, nur Lesen/Suche (ohne utils-Paket)
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

DATA_PATH = Path(__file__).parent / "data" / "events.json"


@st.cache_data
def load_events():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
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
    st.error("Keine Ereignisse gefunden. Liegt data/events.json im Repository?")
    st.stop()

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

filtered = []
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
    filtered.append(e)

if not filtered:
    st.warning("Keine Ereignisse für diese Filter.")
    st.stop()

if "idx" not in st.session_state:
    st.session_state.idx = 0
if st.session_state.idx >= len(filtered):
    st.session_state.idx = 0

jump = st.sidebar.selectbox(
    "Ereignis wählen",
    options=list(range(len(filtered))),
    format_func=lambda i: f"{filtered[i].get('date', '')} - {filtered[i].get('title', '')[:60]}",
    index=min(st.session_state.idx, len(filtered) - 1),
)
st.session_state.idx = jump
e = filtered[st.session_state.idx]

c1, c2, c3 = st.columns([1, 1, 4])
with c1:
    if st.button("Aelter") and st.session_state.idx > 0:
        st.session_state.idx -= 1
        st.rerun()
with c2:
    if st.button("Neuer") and st.session_state.idx < len(filtered) - 1:
        st.session_state.idx += 1
        st.rerun()
with c3:
    st.caption(f"{st.session_state.idx + 1} / {len(filtered)} in der Auswahl")

actor = e.get("actor") or "KONTEXT"
title = e.get("title") or ""
date = e.get("date") or ""
thema = e.get("thema") or ""
st.markdown(
    f'<div style="background:linear-gradient(120deg,#0b1f3a,#1d4ed8);color:#fff;'
    f'padding:1.2rem 1.5rem;border-radius:16px;margin-bottom:1rem;">'
    f"{actor_chip(actor)}"
    f'<div style="opacity:0.85;font-size:0.9rem;margin-top:0.35rem;">{date} | {thema}</div>'
    f'<h2 style="margin:0.4rem 0 0 0;color:#fff;">{title}</h2></div>',
    unsafe_allow_html=True,
)

if e.get("short"):
    st.markdown(e["short"])

st.subheader("Harter Fakt")
fact = e.get("fact") or "-"
st.text_area(
    "Harter Fakt",
    value=fact,
    height=min(420, 140 + fact.count(chr(10)) * 18),
    disabled=True,
    label_visibility="collapsed",
)

st.subheader("Lesarten im Vergleich")
col_a, col_b = st.columns(2)
with col_a:
    st.caption("UKRAINISCH / WESTLICH")
    st.info(e.get("view_ua_west") or "-")
with col_b:
    st.caption("RUSSISCH")
    st.info(e.get("view_ru") or "-")

if e.get("streitpunkt"):
    st.subheader("Streitpunkt")
    st.warning(e["streitpunkt"])

tags = e.get("tags") or []
if tags:
    st.markdown("**Tags:** " + " | ".join(tags))

refs = e.get("cross_refs") or []
if refs:
    st.subheader("Im Zusammenhang")
    for rid in refs:
        ref = event_by_id(all_events, rid)
        if not ref:
            continue
        label = f"{ref.get('date', '')} - {ref.get('title', rid)[:70]}"
        if st.button(label, key=f"ref_{e['id']}_{rid}"):
            for i, fe in enumerate(filtered):
                if fe["id"] == rid:
                    st.session_state.idx = i
                    st.rerun()
            st.info(f"Nicht in der aktuellen Filterauswahl: {label}")
