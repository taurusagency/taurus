import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Configurazione Iniziale
st.set_page_config(page_title="Taurus Agency Gold", layout="wide")

# --- 1. ACCESSI AGGIORNATI ---
# Ho inserito te come unico Master e rimosso Queen da qui
MASTER_EMAIL = "marchiano.massimo@gmail.com"
MASTER_PASSWORD = "Taurus2026"

# Elenco Subagenti Autorizzati
SUBAGENTI = [
    "Giuseppe.papangelo@outlook.it",
    "starmakertaurususa2026@gmail.com",
    "fabio60322@gmail.com",
    "elenamirenda1@gmail.com",
    "queen" # Queen ora è solo un subagente come gli altri
]

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- SCHERMATA LOGIN ---
if not st.session_state.auth:
    st.title("🏆 Taurus Agency - Accesso Master & Agenti")
    email_in = st.text_input("Email")
    pass_in = st.text_input("Password", type="password")
    
    if st.button("Entra nel Sistema"):
        # Accesso per MASSIMO (Master)
        if email_in == MASTER_EMAIL and pass_in == MASTER_PASSWORD:
            st.session_state.auth = True
            st.session_state.user = MASTER_EMAIL
            st.session_state.is_master = True
            st.rerun()
        # Accesso per SUBAGENTI
        elif email_in in SUBAGENTI and pass_in == "TaurusSub2026":
            st.session_state.auth = True
            st.session_state.user = email_in
            st.session_state.is_master = False
            st.rerun()
        else:
            st.error("Accesso negato. Controlla email e password.")
    st.stop()

# --- 2. DATABASE VASI COMUNICANTI ---
if 'data' not in st.session_state:
    tutti = [MASTER_EMAIL] + SUBAGENTI
    st.session_state.data = pd.DataFrame({
        'Agente': tutti,
        'Volume_Euro': [0.0] * len(tutti),
        'Monete_Budget': [1000000.0 if a == MASTER_EMAIL else 0.0 for a in tutti],
        'Guadagno_Monete': [0] * len(tutti)
    })
    st.session_state.avatars = {}

# --- 3. PROFILO E FOTO (Sidebar) ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.session_state.user not in st.session_state.avatars:
        st.session_state.avatars[st.session_state.user] = "https://www.w3schools.com/howto/img_avatar.png"
    st.image(st.session_state.avatars[st.session_state.user], width=100)
    
    foto = st.file_uploader("Aggiorna foto", type=['png', 'jpg'])
    if foto:
        st.session_state.avatars[st.session_state.user] = Image.open(foto)
        st.rerun()
    
    if st.button("Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 4. PANNELLO MASTER (Massimo) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Control Center - Massimo")
    
    # Gara tra subagenti
    st.subheader("🏁 Classifica Gara Agenti")
    df_sub = st.session_state.data[st.session_state.data['Agente'] != MASTER_EMAIL]
    if df_sub['Volume_Euro'].sum() > 0:
        fig = px.bar(df_sub, x='Agente', y='Volume_Euro', color='Volume_Euro', text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Riepilogo Agenzia")
    st.dataframe(st.session_state.data, use_container_width=True)

    with st.expander("💸 Invia Monete ai Subagenti"):
        dest = st.selectbox("Seleziona Agente", SUBAGENTI)
        qty = st.number_input("Quantità Monete", min_value=0)
        if st.button("Conferma Ricarica"):
            st.session_state.data.loc[st.session_state.data['Agente'] == MASTER_EMAIL, 'Monete_Budget'] -= qty
            st.session_state.data.loc[st.session_state.data['Agente'] == dest, 'Monete_Budget'] += qty
            st.success("Operazione completata!")

# --- 5. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Area Operativa: {st.session_state.user}")
    idx = st.session_state.data['Agente'] == st.session_state.user
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Mio Budget", f"{st.session_state.data.loc[idx, 'Monete_Budget'].values[0]}")
    c2.metric("Totale Euro (€)", f"{st.session_state.data.loc[idx, 'Volume_Euro'].values[0]}")
    c3.metric("Guadagno", f"{st.session_state.data.loc[idx, 'Guadagno_Monete'].values[0]}")

    st.divider()
    euro = st.number_input("Importo Vendita (€)", min_value=0.0)
    if euro > 0:
        monete = int(euro * 91)
        margine = int(euro * 5)
        st.info(f"Erogherai {monete} monete. Margine: {margine}")
        if st.button("Conferma"):
            if st.session_state.data.loc[idx, 'Monete_Budget'].values[0] >= monete:
                st.session_state.data.loc[idx, 'Monete_Budget'] -= monete
                st.session_state.data.loc[idx, 'Volume_Euro'] += euro
                st.session_state.data.loc[idx, 'Guadagno_Monete'] += margine
                st.balloons()
                st.rerun()
