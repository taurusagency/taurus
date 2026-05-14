import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Login", page_icon="🐂", layout="wide")

# --- DATABASE CREDENZIALI FISSE (HARDCODED) ---
# Qui le password sono bloccate nel codice: non si cancellano mai.
USER_CREDENTIALS = {
    "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
    "Queen": {"pass": "Taurus69", "role": "Subagente", "name": "Queen"},
    "agente1": {"pass": "pass1", "role": "Subagente", "name": "Agente 1"},
    "agente2": {"pass": "pass2", "role": "Subagente", "name": "Agente 2"},
    "agente3": {"pass": "pass3", "role": "Subagente", "name": "Agente 3"},
    "agente4": {"pass": "pass4", "role": "Subagente", "name": "Agente 4"},
    "agente5": {"pass": "pass5", "role": "Subagente", "name": "Agente 5"},
}

# --- INIZIALIZZAZIONE DATI ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000
if 'budgets' not in st.session_state:
    st.session_state.budgets = {k: 0 for k in USER_CREDENTIALS if USER_CREDENTIALS[k]['role'] == 'Subagente'}
if 'guadagni' not in st.session_state:
    st.session_state.guadagni = {k: 0 for k in USER_CREDENTIALS if USER_CREDENTIALS[k]['role'] == 'Subagente'}

# --- COSTANTI ---
APP_URL = "https://taurus-agency.streamlit.app"
COIN_PER_EURO = 91
MARGINE_COIN = 10 
MIO_WHATSAPP = "+393331234567" # Metti il tuo numero qui

# --- STILE CSS ---
st.markdown("""
<style>
    .taurus-header { text-align: center; padding: 20px; background: #1a1a1a; color: #FFD700; border-radius: 15px; margin-bottom: 25px; border: 1px solid #FFD700; }
    .profit-container { position: fixed; top: 70px; right: 20px; z-index: 1000; background: #1e1e1e; color: #FFD700; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .wa-button { background-color: #25D366; color: white; padding: 8px 15px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown('<div class="taurus-header"><h1>🐂 TAURUS AGENCY LOGIN</h1></div>', unsafe_allow_html=True)
    u_in = st.text_input("Username")
    p_in = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u_in in USER_CREDENTIALS and USER_CREDENTIALS[u_in]["pass"] == p_in:
            st.session_state.authenticated = True
            st.session_state.user_logged = u_in
            st.session_state.user_role = USER_CREDENTIALS[u_in]["role"]
            st.rerun()
        else:
            st.error("Credenziali non valide. Verifica maiuscole e minuscole.")
    st.stop()

user = st.session_state.user_logged
role = st.session_state.user_role

# --- DASHBOARD ADMIN (TAURUSMASTER) ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    
    # Guadagno totale dell'agenzia
    tot_coin_agenzia = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin_agenzia:,.0f} COIN</b><br>{tot_coin_agenzia/101:.2f} €</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👥 Gestione & WhatsApp", "💰 Rabbocchi"])
    
    with tab1:
        cols = st.columns(3)
        for i, (u_k, d) in enumerate(USER_CREDENTIALS.items()):
            if d['role'] == "Subagente":
                with cols[i % 3]:
                    with st.container(border=True):
                        st.write(f"### {d['name']}")
                        st.write(f"Maturato: **{st.session_state.guadagni[u_k]:,.0f} Coin**")
                        
                        if st.button(f"Saldato", key=f"pay_{u_k}"):
                            st.session_state.guadagni[u_k] = 0; st.rerun()
                        
                        # Generatore Link WhatsApp
                        testo = f"🛡️ *TAURUS AGENCY*\\n\\n🔗 Link: {APP_URL}\\n👤 User: {u_k}\\n🔑 Pass: {d['pass']}"
                        testo_enc = urllib.parse.quote(testo.replace("\\n", "\n"))
                        st.markdown(f'<a href="https://wa.me/?text={testo_enc}" target="_blank" class="wa-button">📲 Invia su WhatsApp</a>', unsafe_allow_html=True)

    with tab2:
        st.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
        sel = st.selectbox("Agente", [k for k,v in USER_CREDENTIALS.items() if v['role']=="Subagente"])
        qta = st.number_input("Quantità Coin", step=10000)
        if st.button("Invia Rabbocco"):
            if st.session_state.stock_centrale >= qta:
                st.session_state.budgets[sel] += qta
                st.session_state.stock_centrale -= qta; st.success("Fatto!"); st.rerun()

# --- AREA OPERATIVA SUBAGENTE ---
else:
    st.title(f"🚀 Area Agente: {USER_CREDENTIALS[user]['name']}")
    
    g_agente = st.session_state.guadagni[user]
    st.markdown(f'<div class="profit-container">IL TUO GUADAGNO<br><b>{g_agente:,.0f} COIN</b><br>{g_agente/101:.2f} €</div>', unsafe_allow_html=True)

    st.metric("Budget Monete", f"{st.session_state.budgets[user]:,.0f}")
    
    with st.form("vendita"):
        idc = st.text_input("ID StarMaker Cliente")
        eur = st.number_input("Euro", min_value=1)
        st.info(f"💡 Erogazione prevista: {eur * COIN_PER_EURO:,.0f} monete")
        
        if st.form_submit_button("CONFERMA VENDITA"):
            coin_out = eur * COIN_PER_EURO
            if st.session_state.budgets[user] >= coin_out:
                m = eur * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "ID Cliente": idc, "Euro": eur, "Coin": coin_out,
                    "m_sub": m/2, "m_agenzia": m/2
                })
                st.session_state.budgets[user] -= coin_out
                st.session_state.guadagni[user] += (m/2)
                st.rerun()
            else: st.error("Budget insufficiente!")

if st.sidebar.button("Logout"): st.session_state.authenticated = False; st.rerun()
