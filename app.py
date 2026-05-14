import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# Configurazione Avanzata
st.set_page_config(page_title="Taurus Agency - Pro Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Stile CSS per un'interfaccia a card moderna
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .agent-card { border: 2px solid #007bff; padding: 15px; border-radius: 10px; background-color: white; margin-bottom: 5px; color: #1f1f1f; }
    div.stButton > button:first-child { height: 3em; width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Dati Subagenti (12)
if 'db_subagenti' not in st.session_state:
    st.session_state.capitale_agenzia = 5000000
    st.session_state.db_subagenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Subagente {i}' for i in range(1, 13)],
        'Username': [f'taurus_user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}026' for i in range(1, 13)],
        'Monete_Attuali': [100000 for _ in range(12)],
        'Performance': [0.0 for _ in range(12)]
    })

# --- HEADER ---
st.title("🐂 Taurus Agency - Dashboard Ultra")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Capitale Agenzia", f"{st.session_state.capitale_agenzia:,}", "+15k oggi")
c2.metric("Saldo Subagenti", f"{st.session_state.db_subagenti['Monete_Attuali'].sum():,}", "-5k (distribuite)")
c3.metric("Gara Leaderboard", "Attiva", "🔥")
c4.metric("Subagenti", "12/12", "Online")

st.divider()

# --- MENU A QUADRATI ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
if col_m1.button("📊 Grafici & Analisi"): st.session_state.page = "grafica"
if col_m2.button("👥 Gestione Accessi"): st.session_state.page = "subagenti"
if col_m3.button("🏆 Gara Profitti"): st.session_state.page = "gara"
if col_m4.button("💰 Carico/Scarico"): st.session_state.page = "rabocco"

if 'page' not in st.session_state: st.session_state.page = "subagenti"

# --- PAGINA: GESTIONE SUBAGENTI (MODIFICA USERNAME E PASSWORD) ---
if st.session_state.page == "subagenti":
    st.subheader("Modifica Credenziali e Accessi Subagenti")
    st.info("Qui puoi cambiare Username e Password. Usa il tasto verde per inviare i nuovi dati su WhatsApp.")
    
    for i, row in st.session_state.db_subagenti.iterrows():
        with st.container():
            st.markdown(f"<div class='agent-card'><b>GESTIONE: {row['Nome']}</b></div>", unsafe_allow_html=True)
            col_user, col_pass, col_btn, col_wa = st.columns([3, 3, 2, 2])
            
            # Campi di modifica
            nuovo_user = col_user.text_input(f"Username {row['Nome']}", row['Username'], key=f"user_{i}")
            nuova_pass = col_pass.text_input(f"Password {row['Nome']}", row['Password'], key=f"pass_{i}")
            
            # Tasto per salvare nel database locale della sessione
            if col_btn.button(f"Salva {i+1}", key=f"save_{i}"):
                st.session_state.db_subagenti.at[i, 'Username'] = nuovo_user
                st.session_state.db_subagenti.at[i, 'Password'] = nuova_pass
                st.toast(f"Dati di {row['Nome']} aggiornati!")

            # Generazione link WhatsApp con i NUOVI dati
            messaggio = f"Ciao {row['Nome']}, ecco le tue nuove credenziali Taurus:\n\n👤 User: {nuovo_user}\n🔑 Pass: {nuova_pass}\n\nAccedi qui: https://taurus-app-finale.streamlit.app"
            url_whatsapp = f"https://wa.me/?text={urllib.parse.quote(messaggio)}"
            col_wa.markdown(f"<a href='{url_whatsapp}' target='_blank'><button style='background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%; cursor:pointer;'>📲 WhatsApp</button></a>", unsafe_allow_html=True)
        st.write("")

# --- PAGINA: GRAFICA ---
elif st.session_state.page == "grafica":
    st.subheader("Performance Visiva")
    fig = px.bar(st.session_state.db_subagenti, x='Nome', y='Monete_Attuali', color='Nome', title="Monete possedute per Subagente")
    st.plotly_chart(fig, use_container_width=True)

# --- PAGINA: GARA ---
elif st.session_state.page == "gara":
    st.subheader("🏆 Gara tra Subagenti")
    df_gara = st.session_state.db_subagenti.sort_values(by='Monete_Attuali', ascending=False)
    st.table(df_gara[['Nome', 'Username', 'Monete_Attuali']])

# --- PAGINA: RABOCCO ---
elif st.session_state.page == "rabocco":
    st.subheader("Gestione Capitale")
    # Logica per spostare monete (come nel precedente)
    st.write("Usa questa sezione per aumentare il capitale dell'agenzia o distribuirlo.")
