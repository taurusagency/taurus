import streamlit as st
import pandas as pd

# 1. Configurazione - Accesso facilitato
st.set_page_config(page_title="Taurus Agency Top 1", layout="wide")

# Password fissa per tutti i subagenti per non sbagliare: TaurusSub2026
AGENTI = {"Terry": "Taurus01", "Fabio": "Taurus02", "Elena": "Taurus03", "USA_Agent": "Taurus04", "Queen": "Taurus05"}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🐂 Taurus Agency - Login")
    u = st.text_input("Username").strip()
    p = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if u == "MassimoMaster" and p == "Taurus2026":
            st.session_state.auth, st.session_state.user, st.session_state.master = True, u, True
            st.rerun()
        elif u in AGENTI and p == AGENTI[u]:
            st.session_state.auth, st.session_state.user, st.session_state.master = True, u, False
            st.rerun()
        else:
            st.error("Credenziali Errate")
    st.stop()

# 2. Database e Risultato Lavoro
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({'Agente': ["MassimoMaster"] + list(AGENTI.keys()), 'Coins': [1000000.0] + [0.0]*5, 'Guadagno': [0.0]*6})

# Visualizzazione in alto a destra
guadagno = st.session_state.db.loc[st.session_state.db['Agente'] == st.session_state.user, 'Guadagno'].values[0]
st.sidebar.metric("💰 Mio Guadagno", f"{guadagno} Coins", f"€ {guadagno/10:.2f}")

if st.session_state.master:
    st.title("🚀 Dashboard Master - Massimo")
    target = st.selectbox("Invia a:", list(AGENTI.keys()))
    quant = st.number_input("Quantità Monete", step=100.0)
    if st.button("Invia"):
        st.session_state.db.loc[st.session_state.db['Agente'] == target, 'Coins'] += quant
        st.success("Fatto!")
    st.write(st.session_state.db)
else:
    st.title(f"📱 Area Agente: {st.session_state.user}")
    budget = st.session_state.db.loc[st.session_state.db['Agente'] == st.session_state.user, 'Coins'].values[0]
    st.metric("Budget Disponibile", f"{budget} Coins")
    euro = st.number_input("Euro Incassati", min_value=0.0)
    if st.button("Registra Vendita") and budget >= (euro * 91):
        st.session_state.db.loc[st.session_state.db['Agente'] == st.session_state.user, 'Coins'] -= (euro * 91)
        st.session_state.db.loc[st.session_state.db['Agente'] == st.session_state.user, 'Guadagno'] += (euro * 5)
        st.balloons()
        st.rerun()
