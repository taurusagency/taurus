import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", layout="wide", initial_sidebar_state="collapsed")

# --- DATABASE INIZIALE (Gli account che hai già creato) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
    }
    # Creazione dei 12 subagenti pronti per l'accesso
    for i in range(1, 13):
        st.session_state.users_db[f"agente{i}"] = {
            "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", 
            "budget": 0, "guadagno_accumulato_coin": 0, "foto": None
        }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000

# --- COSTANTI ---
COIN_PER_EURO = 91
MARGINE_COIN = 10 
MIO_WHATSAPP = "+393331234567" # Sostituisci col tuo numero reale
APP_URL = "https://taurus-agency.streamlit.app"

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
<style>
    .taurus-header {
        text-align: center; padding: 20px;
        background: linear-gradient(90deg, #1e1e1e 0%, #434343 100%);
        color: #FFD700; border-radius: 15px; margin-bottom: 25px;
    }
    .profit-container {
        position: fixed; top: 70px; right: 20px; z-index: 1000;
        background: #1e1e1e; color: #FFD700; padding: 15px;
        border-radius: 12px; border: 2px solid #FFD700; text-align: center;
    }
    .agent-card {
        background: white; padding: 20px; border-radius: 15px;
        border-top: 5px solid #FFD700; margin-bottom: 20px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- INTESTAZIONE GRAFICA ---
st.markdown('<div class="taurus-header"><h1 style="margin:0;">🐂 TAURUS AGENCY</h1></div>', unsafe_allow_html=True)

# --- 1. SCHERMATA DI LOGIN CORRETTA (SOLO USER E PASS) ---
if not st.session_state.authenticated:
    st.markdown("### 🛡️ Area di Accesso")
    # Usiamo st.text_input invece di widget complessi per evitare etichette "Email"
    with st.container():
        user_in = st.text_input("Nome Utente (Username)", placeholder="Inserisci il tuo username")
        pass_in = st.text_input("Chiave di Accesso (Password)", type="password", placeholder="Inserisci la tua password")
        
        if st.button("ACCEDI ALLA DASHBOARD"):
            if user_in in st.session_state.users_db and st.session_state.users_db[user_in]["pass"] == pass_in:
                st.session_state.authenticated = True
                st.session_state.user_logged = user_in
                st.session_state.user_role = st.session_state.users_db[user_in]["role"]
                st.rerun()
            else:
                st.error("Credenziali errate. Controlla maiuscole e minuscole.")
    st.stop()

# --- LOGICA OPERATIVA ---
user = st.session_state.user_logged
role = st.session_state.user_role

# --- WIDGET GUADAGNO ---
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin:,.0f} COIN</b><br>{tot_coin/101:.2f} €</div>', unsafe_allow_html=True)
else:
    guadagno_agente = st.session_state.users_db[user]["guadagno_accumulato_coin"]
    testo_wa = urllib.parse.quote(f"Ciao TaurusMaster, richiedo il compenso di {guadagno_agente:,.0f} monete.")
    st.markdown(f'<a href="https://wa.me/{MIO_WHATSAPP}?text={testo_wa}" target="_blank" style="text-decoration:none;"><div class="profit-container">RICHIEDI COMPENSO<br><b>{guadagno_agente:,.0f} COIN</b><br>{guadagno_agente/101:.2f} €</div></a>', unsafe_allow_html=True)

# --- 2. VISTA TAURUSMASTER (AMMINISTRATORE) ---
if role == "Agenzia":
    st.title("Pannello Proprietario")
    
    c1, c2 = st.columns(2)
    c1.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
    with c2:
        with st.expander("Modifica Stock"):
            nuovo_val = st.number_input("Imposta Stock", value=st.session_state.stock_centrale)
            if st.button("Salva Stock"):
                st.session_state.stock_centrale = nuovo_val
                st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 Team", "💰 Rabbocchi", "🏆 Gara"])
    
    with tab1:
        cols = st.columns(3)
        for i, (u_key, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 3]:
                    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                    if data['foto']: st.image(data['foto'], width=80)
                    st.write(f"**{data['name']}**")
                    with st.expander("Gestione"):
                        if st.button("Azzera Compensi", key=f"z_{u_key}"):
                            st.session_state.users_db[u_key]["guadagno_accumulato_coin"] = 0
                            st.rerun()
                        # Qui puoi cambiare username e password
                        n_u = st.text_input("Username", value=u_key, key=f"un_{u_key}")
                        n_p = st.text_input("Password", value=data['pass'], key=f"pw_{u_key}")
                        if st.button("Salva", key=f"sv_{u_key}"):
                            if n_u != u_key:
                                st.session_state.users_db[n_u] = st.session_state.users_db.pop(u_key)
                            st.session_state.users_db[n_u]["pass"] = n_p
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        sel = st.selectbox("Seleziona Agente", [k for k,v in st.session_state.users_db.items() if v['role']=="Subagente"])
        amt = st.number_input("Coin da inviare", step=10000)
        if st.button("Invia Rabbocco"):
            if st.session_state.stock_centrale >= amt:
                st.session_state.users_db[sel]["budget"] += amt
                st.session_state.stock_centrale -= amt
                st.success("Trasferito!")
                st.rerun()

# --- 3. VISTA SUBAGENTE (OPERATIVO) ---
else:
    st.title(f"🚀 Area Agente: {st.session_state.users_db[user]['name']}")
    st.metric("Tuo Budget (Coin)", f"{st.session_state.users_db[user]['budget']:,.0f}")
    
    with st.form("vendita"):
        id_cli = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Euro Ricevuti", min_value=1)
        # Supporto pre-compilazione
        coin_out = euro * COIN_PER_EURO
        st.info(f"💡 Erogazione: {coin_out:,.0f} monete")
        
        if st.form_submit_button("REGISTRA"):
            if st.session_state.users_db[user]["budget"] >= coin_out:
                m = euro * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "Nome Agente": st.session_state.users_db[user]['name'],
                    "ID Cliente": id_cli, "Euro": euro, "Coin": coin_out,
                    "m_sub": m/2, "m_agenzia": m/2
                })
                st.session_state.users_db[user]["budget"] -= coin_out
                st.session_state.users_db[user]["guadagno_accumulato_coin"] += (m/2)
                st.rerun()
            else:
                st.error("Budget insufficiente!")

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
