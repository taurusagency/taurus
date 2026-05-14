import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Gestione", page_icon="🐂", layout="wide")

# --- COSTANTI ---
APP_URL = "https://taurus-agency.streamlit.app" # URL PUBBLICO DELL'APP
COIN_PER_EURO = 91
MARGINE_COIN = 10 
MIO_WHATSAPP = "+393331234567" 

# --- DATABASE INIZIALE ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
        "Queen": {"pass": "Taurus69", "role": "Subagente", "name": "Queen", "budget": 0, "guadagno_accumulato_coin": 0, "foto": None},
    }
    for i in range(1, 13):
        u_key = f"agente{i}"
        if u_key not in st.session_state.users_db:
            st.session_state.users_db[u_key] = {
                "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", 
                "budget": 0, "guadagno_accumulato_coin": 0, "foto": None
            }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000

# --- STILE CSS ---
st.markdown("""
<style>
    .taurus-header { text-align: center; padding: 20px; background: #1e1e1e; color: #FFD700; border-radius: 15px; margin-bottom: 25px; }
    .profit-container { position: fixed; top: 70px; right: 20px; z-index: 1000; background: #1e1e1e; color: #FFD700; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; text-align: center; }
    .agent-card { background: white; padding: 15px; border-radius: 12px; border-top: 5px solid #FFD700; margin-bottom: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="taurus-header"><h1>🐂 TAURUS AGENCY</h1></div>', unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    st.subheader("🛡️ Accesso Riservato")
    u_in = st.text_input("Username")
    p_in = st.text_input("Password", type="password")
    if st.button("ACCEDI ALLA DASHBOARD"):
        if u_in in st.session_state.users_db and st.session_state.users_db[u_in]["pass"] == p_in:
            st.session_state.authenticated = True
            st.session_state.user_logged = u_in
            st.session_state.user_role = st.session_state.users_db[u_in]["role"]
            st.rerun()
        else:
            st.error("Credenziali errate.")
    st.stop()

user = st.session_state.user_logged
role = st.session_state.user_role

# --- WIDGET PROFITTI ---
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin:,.0f} COIN</b><br>{tot_coin/101:.2f} €</div>', unsafe_allow_html=True)
else:
    g_acc = st.session_state.users_db[user]["guadagno_accumulato_coin"]
    msg_wa = urllib.parse.quote(f"Richiedo compenso di {g_acc:,.0f} monete.")
    st.markdown(f'<a href="https://wa.me/{MIO_WHATSAPP}?text={msg_wa}" target="_blank" style="text-decoration:none;"><div class="profit-container">RICHIEDI COMPENSO<br><b>{g_acc:,.0f} COIN</b><br>{g_acc/101:.2f} €</div></a>', unsafe_allow_html=True)

# --- DASHBOARD ADMIN ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    col1, col2 = st.columns(2)
    col1.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col2:
        with st.expander("Modifica Stock"):
            nuovo_v = st.number_input("Nuovo Totale", value=st.session_state.stock_centrale)
            if st.button("Salva Stock"): st.session_state.stock_centrale = nuovo_v; st.rerun()

    tab1, tab2 = st.tabs(["👥 Gestione & Messaggi", "💰 Rabbocchi"])
    
    with tab1:
        cols = st.columns(3)
        for i, (u_k, d) in enumerate(list(st.session_state.users_db.items())):
            if d['role'] == "Subagente":
                with cols[i % 3]:
                    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                    if d['foto']: st.image(d['foto'], width=70)
                    st.write(f"**{d['name']}**")
                    with st.expander("Azioni & Credenziali"):
                        if st.button("Saldato", key=f"z_{u_k}"):
                            st.session_state.users_db[u_k]["guadagno_accumulato_coin"] = 0; st.rerun()
                        n_u = st.text_input("User", u_k, key=f"un_{u_k}")
                        n_p = st.text_input("Pass", d['pass'], key=f"pw_{u_k}")
                        if st.button("Salva", key=f"sv_{u_k}"):
                            if n_u != u_k: st.session_state.users_db[n_u] = st.session_state.users_db.pop(u_k)
                            st.session_state.users_db[n_u]["pass"] = n_p; st.rerun()
                        
                        # --- NUOVO: MESSAGGIO WHATSAPP CON LINK ---
                        msg_whatsapp = f"🛡️ *TAURUS AGENCY - ACCESSO*\\n\\n🔗 Accedi qui: {APP_URL}\\n👤 Username: {n_u}\\n🔑 Password: {n_p}\\n\\n*Salva questo link per ricaricare i tuoi clienti!*"
                        st.code(msg_whatsapp)
                        st.info("Copia il testo sopra e invialo su WhatsApp.")
                    st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        sel = st.selectbox("Agente", [k for k,v in st.session_state.users_db.items() if v['role']=="Subagente"])
        amt = st.number_input("Invia monete", step=10000)
        if st.button("Conferma Rabbocco"):
            if st.session_state.stock_centrale >= amt:
                st.session_state.users_db[sel]["budget"] += amt
                st.session_state.stock_centrale -= amt; st.rerun()

# --- AREA SUBAGENTE ---
else:
    st.title(f"🚀 Area Agente: {st.session_state.users_db[user]['name']}")
    st.metric("Budget (Coin)", f"{st.session_state.users_db[user]['budget']:,.0f}")
    with st.form("vendita"):
        id_c = st.text_input("ID StarMaker Cliente")
        eur = st.number_input("Euro", min_value=1)
        st.info(f"💡 Erogazione: {eur * COIN_PER_EURO:,.0f} monete")
        if st.form_submit_button("REGISTRA"):
            coin_out = eur * COIN_PER_EURO
            if st.session_state.users_db[user]["budget"] >= coin_out:
                m = eur * MARGINE_COIN
                st.session_state.db_vendite.append({"Data": datetime.now().strftime("%d/%m %H:%M"), "Agente": user, "Nome Agente": st.session_state.users_db[user]['name'], "ID Cliente": id_c, "Euro": eur, "Coin": coin_out, "m_sub": m/2, "m_agenzia": m/2})
                st.session_state.users_db[user]["budget"] -= coin_out
                st.session_state.users_db[user]["guadagno_accumulato_coin"] += (m/2)
                st.rerun()
            else: st.error("Budget insufficiente!")

if st.sidebar.button("Logout"): st.session_state.authenticated = False; st.rerun()
