import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Configurazione Iniziale
st.set_page_config(page_title="Taurus Agency Gold", layout="wide")

# --- 1. ACCESSI TOTALMENTE RESETTATI ---
# Tu sei l'unico proprietario e amministratore
MASTER_EMAIL = "marchiano.massimo@gmail.com"
MASTER_PASSWORD = "Taurus2026"

# Elenco Subagenti (Queen è solo un'agente ora)
SUBAGENTI = [
    "Giuseppe.papangelo@outlook.it",
    "starmakertaurususa2026@gmail.com",
    "fabio60322@gmail.com",
    "elenamirenda1@gmail.com",
    "queen@taurus.com" # Inserita come subagente semplice
]

if "auth" not in st.session_state:
    st.session_state.auth = False

# --- SCHERMATA LOGIN ---
if not st.session_state.auth:
    st.title("🏆 Taurus Agency - Accesso Massimo")
    email_in = st.text_input("Email Aziendale")
    pass_in = st.text_input("Password", type="password")
    
    if st.button("Entra nel Sistema"):
        # Accesso MASSIMO (Il Capo)
        if email_in == MASTER_EMAIL and pass_in == MASTER_PASSWORD:
            st.session_state.auth = True
            st.session_state.user = MASTER_EMAIL
            st.session_state.is_master = True
            st.rerun()
        # Accesso SUBAGENTI (Password standard per loro)
        elif email_in in SUBAGENTI and pass_in == "TaurusSub2026":
            st.session_state.auth = True
            st.session_state.user = email_in
            st.session_state.is_master = False
            st.rerun()
        else:
            st.error("Accesso negato. Solo personale autorizzato.")
    st.stop()

# --- 2. DATABASE VASI COMUNICANTI ---
if 'data' not in st.session_state:
    # Inizializziamo il database con Massimo che ha il milione di monete
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
    # Foto di default se non caricata
    if st.session_state.user not in st.session_state.avatars:
        st.session_state.avatars[st.session_state.user] = "https://www.w3schools.com/howto/img_avatar.png"
    st.image(st.session_state.avatars[st.session_state.user], width=100)
    
    foto = st.file_uploader("Aggiorna la tua foto profilo", type=['png', 'jpg'])
    if foto:
        st.session_state.avatars[st.session_state.user] = Image.open(foto)
        st.rerun()
    
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 4. PANNELLO MASTER (Massimo) ---
if st.session_state.is_master:
    st.title(f"🚀 Taurus Control Center - Benvenuto Massimo")
    
    # Classifica Gara tra i 5 Subagenti
    st.subheader("🏁 Gara Agenti (Top Performance)")
    df_sub = st.session_state.data[st.session_state.data['Agente'] != MASTER_EMAIL]
    
    if df_sub['Volume_Euro'].sum() > 0:
        fig = px.bar(df_sub, x='Agente', y='Volume_Euro', color='Volume_Euro', 
                     text_auto=True, color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Riepilogo Totale Agenzia")
    st.dataframe(st.session_state.data, use_container_width=True)

    with st.expander("💸 Invia Monete ai Subagenti"):
        dest = st.selectbox("Seleziona Agente", SUBAGENTI)
        qty = st.number_input("Quantità Monete da trasferire", min_value=0)
        if st.button("Esegui Ricarica"):
            # Sottrae al Master e aggiunge al subagente
            st.session_state.data.loc[st.session_state.data['Agente'] == MASTER_EMAIL, 'Monete_Budget'] -= qty
            st.session_state.data.loc[st.session_state.data['Agente'] == dest, 'Monete_Budget'] += qty
            st.success(f"Ricarica di {qty} monete completata con successo!")

# --- 5. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Area Operativa Agente")
    idx = st.session_state.data['Agente'] == st.session_state.user
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Budget Monete", f"{st.session_state.data.loc[idx, 'Monete_Budget'].values[0]}")
    col2.metric("Vendite (€)", f"{st.session_state.data.loc[idx, 'Volume_Euro'].values[0]}")
    col3.metric("Mio Margine", f"{st.session_state.data.loc[idx, 'Guadagno_Monete'].values[0]}")

    st.divider()
    euro = st.number_input("Soldi ricevuti dal cliente (€)", min_value=0.0)
    if euro > 0:
        monete = int(euro * 91) # Cambio 1 euro = 91 monete
        margine = int(euro * 5) # Margine 5 monete
        st.info(f"👉 Operazione: Erogherai {monete} monete. Il tuo guadagno sarà di {margine} monete.")
        
        if st.button("Conferma Operazione"):
            if st.session_state.data.loc[idx, 'Monete_Budget'].values[0] >= monete:
                st.session_state.data.loc[idx, 'Monete_Budget'] -= monete
                st.session_state.data.loc[idx, 'Volume_Euro'] += euro
                st.session_state.data.loc[idx, 'Guadagno_Monete'] += margine
                st.balloons() # Celebrazione vendita
                st.rerun()
            else:
                st.error("Budget monete insufficiente! Chiedi ricarica a Massimo.")
