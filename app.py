import streamlit as st

st.set_page_config(
    page_title="Donbas-Dashboard",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

for target in ("pages/Dashboard.py", "pages/1_Dashboard.py"):
    try:
        st.switch_page(target)
        st.stop()
    except Exception:
        continue

st.title("Donbas-Konflikt – Chronologisches Dashboard")
st.markdown("""
**Weiter zum Inhalt**

1. Oben links das **☰-Menü** öffnen (Sidebar), falls nichts Sichtbares links ist.  
2. Dort **Dashboard** anklicken.

Oder diese Adresse öffnen (an deine App-URL anhängen):

`/Dashboard`
""")
st.page_link("pages/Dashboard.py", label="→ Zum Dashboard", icon="📜")
