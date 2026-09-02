# Donbas-Dashboard – öffentliche Version (nur Lesen/Suche)
# Einstiegspunkt für Streamlit Cloud
import streamlit as st
from utils.db import (
    ensure_data, get_all_events, get_sources_for_event,
    get_cross_refs, get_tags_for_event, get_all_tags
)

st.set_page_config(page_title="Donbas-Dashboard", page_icon="📜", layout="wide")

# Gegen Browser-Übersetzung: kein <script> (verursacht Streamlit-DOM-Fehler removeChild)
st.markdown(
    '<div lang="de" translate="no" class="notranslate" style="display:none">notranslate</div>',
    unsafe_allow_html=True,
)

ensure_data()

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

all_events = [e for e in get_all_events() if e.get("status") == "freigegeben"]
all_events = sorted(all_events, key=lambda x: x["date"])
if not all_events:
    st.warning("Keine freigegebenen Ereignisse.")
    st.stop()

# ---------- Sidebar ----------
st.sidebar.header("Suche & Filter")
search = st.sidebar.text_input("Volltextsuche", placeholder="Titel, Fakt, Lesart …")
show_sources = st.sidebar.checkbox("Quellen anzeigen", value=True)
years = sorted(set(e["year"] for e in all_events))
year_range = st.sidebar.slider("Zeitraum", min_value=min(years), max_value=max(years), value=(min(years), max(years)))
st.sidebar.markdown("**Handelnde Seite**")
actor_options = ["RU", "UA", "WEST", "BEIDE", "KONTEXT"]
selected_actors = st.sidebar.multiselect(
    "Seite filtern", actor_options,
    format_func=lambda a: ACTOR_LABELS.get(a, a), default=[],
    help="Vorwiegende Initiative / Handelnde Seite"
)
all_tags = get_all_tags()
selected_tags = st.sidebar.multiselect("Themen / Tags", all_tags)
st.sidebar.markdown("---")
st.sidebar.markdown("**Legende**")
for a in actor_options:
    st.sidebar.markdown(actor_chip(a), unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.caption(f"{len(all_events)} Ereignisse gesamt")

# Filter
events = []
for e in all_events:
    if not (year_range[0] <= e["year"] <= year_range[1]):
        continue
    actor = e.get("actor") or "KONTEXT"
    if selected_actors and actor not in selected_actors:
        continue
    if selected_tags:
        etags = get_tags_for_event(e["id"])
        if not any(t in etags for t in selected_tags):
            continue
    if search:
        tag_str = " ".join(get_tags_for_event(e["id"]))
        blob = " ".join([
            e.get("title") or "", e.get("short") or "", e.get("thema") or "",
            e.get("fact") or "", e.get("view_ua_west") or "", e.get("view_ru") or "",
            e.get("streitpunkt") or "", e.get("background") or "", tag_str, actor,
        ]).lower()
        if search.lower() not in blob:
            continue
    events.append(e)

if not events:
    st.warning("Keine Ereignisse entsprechen den aktuellen Filtern.")
    st.stop()

if "focus_id" not in st.session_state:
    st.session_state.focus_id = events[-1]["id"]
ids = [e["id"] for e in events]
if st.session_state.focus_id not in ids:
    st.session_state.focus_id = events[-1]["id"]
focus_idx = ids.index(st.session_state.focus_id)
selected = events[focus_idx]
sel_actor = selected.get("actor") or "KONTEXT"

st.markdown("""
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
/* Textareas lesbar machen (disabled ist sonst grau) */
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
""", unsafe_allow_html=True)

st.title("Donbas-Konflikt")
st.caption("Fakt · Ukrainisch/westliche Lesart · Russische Lesart · Streitpunkt")

pct = int((focus_idx / max(1, len(events) - 1)) * 100) if len(events) > 1 else 100
st.markdown(f'<div class="progress-track"><div class="progress-fill" style="width:{pct}%"></div></div>', unsafe_allow_html=True)

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
    choice = st.selectbox("Sprungmarke", range(len(events)), index=focus_idx,
                          format_func=lambda i: labels[i], label_visibility="collapsed")
    if choice != focus_idx:
        st.session_state.focus_id = events[choice]["id"]
        st.rerun()
with n4:
    st.markdown(f"<div style='text-align:right;padding-top:0.55rem;color:#64748b;font-size:0.9rem'>{focus_idx+1} / {len(events)}</div>", unsafe_allow_html=True)

window = 3
start = max(0, focus_idx - window)
end = min(len(events), focus_idx + window + 1)
neighbors = events[start:end]
cols = st.columns(len(neighbors))
for i, ev in enumerate(neighbors):
    is_focus = ev["id"] == selected["id"]
    with cols[i]:
        short_date = ev["date"][8:10] + "." + ev["date"][5:7] + "." + ev["date"][2:4]
        label = f"{'● ' if is_focus else ''}{short_date}\n{ev['title'][:36]}"
        if st.button(label, key=f"nb_{ev['id']}", use_container_width=True,
                     type="primary" if is_focus else "secondary"):
            st.session_state.focus_id = ev["id"]
            st.rerun()

_title = (selected.get("title") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
_thema = (selected.get("thema") or "—").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
st.markdown(f"""
<div class="focus-card">
  {actor_chip(sel_actor)}
  <div class="meta" style="margin-top:0.5rem">{selected['date']} · {_thema}</div>
  <h2>{_title}</h2>
</div>
""", unsafe_allow_html=True)

# ===== VIERERSTRUKTUR =====
def _safe(text: str) -> str:
    """HTML-Sonderzeichen escapen, Zeilenumbrüche für Markdown erhalten."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

# ID → lesbare Kurzform für Texte und Buttons
def _event_label(ev: dict) -> str:
    d = ev.get("date") or ""
    try:
        # YYYY-MM-DD → TT.MM.JJJJ
        d = f"{d[8:10]}.{d[5:7]}.{d[0:4]}"
    except Exception:
        pass
    title = (ev.get("title") or ev.get("id") or "")[:48]
    return f"{d} · {title}"

_id_to_label = {e["id"]: _event_label(e) for e in events}
_id_to_event = {e["id"]: e for e in events}

def humanize_ids(text: str) -> str:
    """Ersetzt e012 / (siehe e012) durch Datum · Titel – bedienfreundlicher."""
    if not text:
        return "—"
    import re
    text = text.replace("**", "")
    # (siehe e067) / (siehe e067, e018)
    def repl_siehe(m):
        ids = re.findall(r"e\d+", m.group(0))
        labels = [_id_to_label.get(i, i) for i in ids]
        return "(" + " · ".join(labels) + ")"
    text = re.sub(r"\(siehe\s+e\d+(?:\s*,\s*e\d+)*\)", repl_siehe, text, flags=re.I)
    # einzelne e012, die noch übrig sind (Wortgrenze)
    def repl_id(m):
        eid = m.group(0)
        return _id_to_label.get(eid, eid)
    text = re.sub(r"\be\d{2,4}\b", repl_id, text)
    return text

def render_text_block(text: str, key: str):
    """Stabil: read-only Textarea – IDs als Datum·Titel, kein DOM-Fehler."""
    text = humanize_ids(text)
    lines = max(4, min(22, text.count("\n") + 3))
    st.text_area(
        label=key,
        value=text,
        height=lines * 24,
        disabled=True,
        label_visibility="collapsed",
        key=f"tb_{key}_{selected.get('id', '')}",
    )

# Manöver-Serie: Zähler + Navigation
_tags_l = [t.lower() for t in (selected.get("tags") or [])]
_is_maneuver = (
    selected.get("id") == "e074"
    or "manöver" in _tags_l
    or "manöver-serie" in _tags_l
    or any(k in (selected.get("title") or "").lower()
           for k in ("rapid trident", "sea breeze", "partnership for peace", "übersicht: manöver", "cossack", "maple arch", "blonde avalanche", "avalanche", "fearless", "jmtg"))
)
if _is_maneuver:
    _man_ids = [
        "e041", "e080", "e077", "e061", "e024", "e081",
        "e062", "e078", "e063", "e064", "e079", "e026",
    ]
    _man_present = sorted(
        [i for i in _man_ids if i in _id_to_event],
        key=lambda i: _id_to_event[i].get("date") or "",
    )
    if selected.get("id") in _man_present:
        _idx = _man_present.index(selected["id"]) + 1
        st.info(
            f"**Manöver-Serie:** Station **{_idx} von {len(_man_present)}** "
            f"(PfP → Rapid Trident / Sea Breeze → Intensivierung bis 2021)."
        )
    c_prev, c_ov, c_next = st.columns(3)
    with c_ov:
        if "e074" in _id_to_event and selected.get("id") != "e074":
            if st.button("Gesamtübersicht Manöver", use_container_width=True, key="man_ov"):
                st.session_state.focus_id = "e074"
                st.rerun()
        elif selected.get("id") == "e074":
            st.caption("Übersichtsstation")
    if selected.get("id") in _man_present:
        _ix = _man_present.index(selected["id"])
        with c_prev:
            if _ix > 0 and st.button("← Vorherige Übung", use_container_width=True, key="man_prev"):
                st.session_state.focus_id = _man_present[_ix - 1]
                st.rerun()
        with c_next:
            if _ix < len(_man_present) - 1 and st.button("Nächste Übung →", use_container_width=True, key="man_next"):
                st.session_state.focus_id = _man_present[_ix + 1]
                st.rerun()


# Auf der Manöver-Übersicht: alle Stationen als Sprungziele
if selected.get("id") == "e074":
    st.markdown("##### Zu den einzelnen Manövern springen")
    _man_ids_ov = [
        "e041", "e080", "e077", "e061", "e024", "e081",
        "e062", "e078", "e063", "e064", "e079", "e026",
    ]
    _man_ov = sorted(
        [_id_to_event[i] for i in _man_ids_ov if i in _id_to_event],
        key=lambda x: x.get("date") or "",
    )
    for _i in range(0, len(_man_ov), 3):
        _row = _man_ov[_i : _i + 3]
        _cols = st.columns(len(_row))
        for _j, _ev in enumerate(_row):
            with _cols[_j]:
                _d = _ev.get("date") or ""
                try:
                    _d = f"{_d[8:10]}.{_d[5:7]}.{_d[0:4]}"
                except Exception:
                    pass
                _t = (_ev.get("title") or "")[:36]
                if st.button(
                    f"{_d}\n{_t}",
                    key=f"man_jump_{_ev['id']}",
                    use_container_width=True,
                ):
                    st.session_state.focus_id = _ev["id"]
                    st.rerun()

st.subheader("Harter Fakt")

fact_text = selected.get("fact") or selected.get("short") or "noch nicht hinterlegt"
render_text_block(fact_text, "fact")

# Klickbarer Zusammenhang: cross_refs + im Rohtext erwähnte IDs
import re as _re
_mentioned = set(selected.get("cross_refs") or [])
_mentioned |= set(_re.findall(r"\be\d{2,4}\b", fact_text))
_ctx = sorted(
    (_id_to_event[i] for i in _mentioned if i in _id_to_event and i != selected.get("id")),
    key=lambda x: x.get("date") or "",
)
if _ctx:
    st.markdown("##### Im Zusammenhang – anklicken zum Springen")
    for _i in range(0, len(_ctx), 3):
        _row = _ctx[_i : _i + 3]
        _cols = st.columns(len(_row))
        for _j, _ev in enumerate(_row):
            with _cols[_j]:
                _d = _ev.get("date") or ""
                try:
                    _d = f"{_d[8:10]}.{_d[5:7]}.{_d[0:4]}"
                except Exception:
                    pass
                _t = (_ev.get("title") or "")[:42]
                if st.button(
                    f"{_d}\n{_t}",
                    key=f"ctx_{selected['id']}_{_ev['id']}",
                    use_container_width=True,
                ):
                    st.session_state.focus_id = _ev["id"]
                    st.rerun()

has_views = bool(selected.get("view_ua_west") or selected.get("view_ru"))
if has_views:
    st.subheader("Lesarten im Vergleich")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.caption("UKRAINISCH / WESTLICH")
        render_text_block(selected.get("view_ua_west") or "noch nicht hinterlegt", "ua")
    with c2:
        st.caption("RUSSISCH")
        render_text_block(selected.get("view_ru") or "noch nicht hinterlegt", "ru")
    if selected.get("streitpunkt"):
        st.caption("STREITPUNKT")
        render_text_block(selected.get("streitpunkt"), "streit")
else:
    with st.expander("Hintergrund (noch nicht in Lesarten überführt)", expanded=False):
        render_text_block(selected.get("background") or "kein Text", "bg")

# Quellen / Querverweise
st.markdown("---")
col_a, col_b = st.columns(2, gap="large")
with col_a:
    if show_sources:
        st.markdown("#### Quellen")
        srcs = get_sources_for_event(selected["id"])
        if srcs:
            for s in srcs:
                title = s.get("title") or s.get("id", "")
                url = s.get("url") or ""
                note = s.get("note") or ""
                if url:
                    st.markdown(f"- [{title}]({url})")
                else:
                    st.markdown(f"- {title}")
                if note:
                    st.caption(note)
        else:
            st.caption("Keine Quellen hinterlegt.")
with col_b:
    refs = get_cross_refs(selected["id"])
    # Falls DB keine refs liefert: aus JSON-Feld cross_refs der aktuellen Auswahl
    if not refs:
        raw = selected.get("cross_refs") or []
        refs = [_id_to_event[i] for i in raw if i in _id_to_event]
    if refs:
        st.markdown("#### Verknüpfte Ereignisse")
        st.caption("Anklicken = dorthin springen")
        for r in refs:
            label = _event_label(r)
            if st.button(f"→  {label}",
                         key=f"xr_{selected['id']}_{r['id']}", use_container_width=True):
                st.session_state.focus_id = r["id"]
                st.rerun()
    tags = get_tags_for_event(selected["id"])
    if tags:
        st.markdown("#### Tags")
        st.caption(" · ".join(tags))

st.markdown("---")
with st.expander(f"{len(events)} Ereignisse in der aktuellen Auswahl"):
    for ev in events:
        actor = ev.get("actor") or "KONTEXT"
        mark = "▶ " if ev["id"] == selected["id"] else ""
        chip = ACTOR_LABELS.get(actor, actor)
        if st.button(f"{mark}[{chip}] {ev['date']} — {ev['title']}",
                     key=f"full_{ev['id']}", use_container_width=True):
            st.session_state.focus_id = ev["id"]
            st.rerun()
