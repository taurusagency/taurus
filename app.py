import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import io

# Configurazione Estetica
st.set_page_config(page_title="Taurus Agency Gold", layout="wide")

# --- 1. SISTEMA DI ACCESSO DINAMICO ---
# Sostituisci qui con le mail reali dei tuoi 12 agenti
AUTHORIZED_EMAILS = ["admin@taurus.com", "agente1@taurus.com", "agente2@taurus.com"] 
MASTER_EMAIL = "admin@taurus.com"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🏆 Taurus Agency Login")
    with st.container():
        email = st.text_input("Inserisci la tua Email Aziendale")
        pwd = st.text_input("Password di Accesso", type="password")
        if st.button("Entra nel Sistema"):
            if email in AUTHORIZED_EMAILS and pwd == "Taurus2026":
                st.session_state.auth = True
                st.session_state.user = email
                st.session_state.is_master = (email == MASTER_EMAIL)
                st.rerun()
            else:
                st.error("Accesso negato. Controlla email e password.")
    st.stop()

# --- 2. DATABASE IN MEMORIA ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'Agente': AUTHORIZED_EMAILS,
        'Volume_Euro': [0.0] * len(AUTHORIZED_EMAILS),
        'Monete_Budget': [1000000.0 if e == MASTER_EMAIL else 0.0 for e in AUTHORIZED_EMAILS],
        'Guadagno_Monete': [0] * len(AUTHORIZED_EMAILS)
    })
    st.session_state.avatars = {} # Memoria per le foto profilo

# --- 3. PROFILO E AVATAR ---
with st.sidebar:
    st.header("👤 Il tuo Profilo")
    if st.session_state.user not in st.session_state.avatars:
        st.session_state.avatars[st.session_state.user] = "https://www.w3schools.com/howto/img_avatar.png"
    
    st.image(st.session_state.avatars[st.session_state.user], width=100)
    
    up_avatar = st.file_uploader("Cambia Foto Profilo", type=['png', 'jpg'])
    if up_avatar:
        st.session_state.avatars[st.session_state.user] = Image.open(up_avatar)
        st.rerun()
    
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

# --- 4. LOGICA MASTER ---
if st.session_state.is_master:
    st.title("🚀 Taurus Control Center - Master")
    
    # Classifica Grafica Accattivante
    st.subheader("🏁 Gara Subagenti (Top Sellers)")
    chart_data = st.session_state.data[st.session_state.data['Agente'] != MASTER_EMAIL]
    
    fig = px.bar(chart_data, x='Agente', y='Volume_Euro', 
                 color='Volume_Euro', color_continuous_scale='Viridis',
                 title="Performance in Tempo Reale")
    st.plotly_chart(fig, use_container_width=True)

    # Gestione Vasi Comunicanti
    with st.expander("💸 Iniezione Budget Monete"):
        target = st.selectbox("Seleziona Agente da Ricaricare", chart_data['Agente'])
        amount = st.number_input("Somma Monete", min_value=0)
        if st.button("Conferma Invio"):
            st.session_state.data.loc[st.session_state.data['Agente'] == MASTER_EMAIL, 'Monete_Budget'] -= amount
            st.session_state.data.loc[st.session_state.data['Agente'] == target, 'Monete_Budget'] += amount
            st.success("Budget aggiornato!")

# --- 5. LOGICA SUBAGENTE ---
else:
    st.title(f"📱 Dashboard Operativa: {st.session_state.user}")
    
    user_row = st.session_state.data[st.session_state.data['Agente'] == st.session_state.user]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Budget Monete", f"{user_row['Monete_Budget'].values[0]}")
    col2.metric("Euro Totali", f"{user_row['Volume_Euro'].values[0]}€")
    col3.metric("Monete Guadagnate", f"{user_row['Guadagno_Monete'].values[0]}")

    st.divider()
    st.subheader("📥 Registra Nuova Vendita")
    euro_in = st.number_input("Importo in Euro (€)", min_value=0.0)
    
    if euro_in > 0:
        monete_out = int(euro_in * 91)
        margine = int(euro_in * 5)
        st.info(f"👉 Erogazione: {monete_out} monete | Margine: +{margine} monete")
        
        if st.button("Conferma Operazione"):
            if user_row['Monete_Budget'].values[0] >= monete_out:
                idx = st.session_state.data['Agente'] == st.session_state.user
                st.session_state.data.loc[idx, 'Monete_Budget'] -= monete_out
                st.session_state.data.loc[idx, 'Volume_Euro'] += euro_in
                st.session_state.data.loc[idx, 'Guadagno_Monete'] += margine
                st.balloons() # Effetto grafico accattivante
                st.success("Vendita registrata! La tua posizione in classifica è migliorata.")
                st.rerun()
            else:
                st.error("Budget monete esaurito. Chiedi ricarica al Master.")

    st.divider()
    st.subheader("🏆 Classifica Globale (Gara)")
    gara_data = st.session_state.data[st.session_state.data['Agente'] != MASTER_EMAIL][['Agente', 'Volume_Euro']]
    st.table(gara_data.sort_values(by='Volume_Euro', ascending=False))
