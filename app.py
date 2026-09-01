import streamlit as st

st.set_page_config(
    page_title="Donbas-Dashboard",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    '<div lang="de" translate="no" class="notranslate" style="display:none">notranslate</div>',
    unsafe_allow_html=True,
)

st.title("Donbas-Konflikt – Chronologisches Dashboard")
st.markdown("""
Willkommen.

Dieses Dashboard bietet eine **chronologische** Darstellung der Vorgeschichte und des Donbas-Konflikts
mit **harten Fakten**, **Lesarten im Vergleich** (ukrainisch/westlich · russisch) und **Streitpunkten**.

### Nutzung
- Links in der Sidebar: **Dashboard**
- **Suche** und **Filter** (Zeitraum, Seite, Tags)
- Ereignisse chronologisch lesen, Querverweise nutzen

**Hinweis:** Öffentliche Version ist **nur Lesen und Suchen**. Redaktion erfolgt lokal.
""")

st.info("Öffne links die Seite **Dashboard**.")
