import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", page_icon="🐂", layout="wide", initial_sidebar_state="collapsed")

# --- DATABASE INIZIALE ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
        "Queen": {"pass": "Taurus69", "role": "Subagente", "name": "Queen", "budget": 0, "guadagno_accumulato_coin": 0, "foto": None, "wa": ""},
    }
    for i in range(1, 13):
        u_key = f"agente{i}"
        if u_key not in st.session_state.users_db:
            st.session_state.users_db[u_key] = {
                "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", 
                "budget": 0, "guadagno_accumulato_coin": 0, "foto": None, "wa": ""
            }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000

# --- COSTANTI ---
APP_URL = "https://taurus-agency.streamlit.app" # URL PUBBLICO
COIN_PER_EURO = 91
MARGINE_COIN = 10 

# --- STILE ---
st.markdown("""
<style>
    .taurus-header { text-align: center; padding: 20px; background: #1a1a1a; color: #FFD700; border-radius: 15px; margin-bottom: 25px; border: 1px solid #FFD700; }
    .profit-container { position: fixed; top: 70px; right: 20px; z-index: 1000; background: #1e1e1e; color: #FFD700; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; text-align: center; }
    .wa-button { background-color: #25D366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown('<div class="taurus-header"><h1>🐂 TAURUS AGENCY LOGIN</h1></div>', unsafe_allow_html=True)
    u_in = st.text_input("Username")
    p_in = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u_in in st.session_state.users_db and st.session_state.users_db[u_in]["pass"] == p_in:
            st.session_state.authenticated = True
            st.session_state.user_logged = u_in
            st.session_state.user_role = st.session_state.users_db[u_in]["role"]
            st.rerun()
        else: st.error("Dati errati")
    st.stop()

user = st.session_state.user_logged
role = st.session_state.user_role

# --- DASHBOARD ADMIN ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    tab1, tab2 = st.tabs(["👥 Gestione & WhatsApp", "💰 Stock"])
    
    with tab1:
        cols = st.columns(3)
        for i, (u_k, d) in enumerate(list(st.session_state.users_db.items())):
            if d['role'] == "Subagente":
                with cols[i % 3]:
                    with st.container(border=True):
                        st.write(f"**{d['name']}**")
                        num_wa = st.text_input("WhatsApp (es: 39333...)", value=d['wa'], key=f"wa_input_{u_k}")
                        st.session_state.users_db[u_k]['wa'] = num_wa
                        
                        # --- GENERATORE LINK WHATSAPP ---
                        testo = f"🛡️ *TAURUS AGENCY*\\n\\n🔗 Clicca qui per entrare: {APP_URL}\\n👤 User: {u_k}\\n🔑 Pass: {d['pass']}"
                        testo_encoded = urllib.parse.quote(testo.replace("\\n", "\n"))
                        link_wa_diretto = f"https://wa.me/{num_wa}?text={testo_encoded}"
                        
                        st.markdown(f'<a href="{link_wa_diretto}" target="_blank" class="wa-button">📲 Invia su WhatsApp</a>', unsafe_allow_html=True)
                        
                        with st.expander("Modifica Credenziali"):
                            st.session_state.users_db[u_k]["pass"] = st.text_input("Nuova Pass", d['pass'], key=f"pw_{u_k}")

    with tab2:
        st.metric("Stock Centrale", f"{st.session_state.stock_centrale:,.0f}")
        rabbocco = st.number_input("Aggiungi Coin allo Stock", step=100000)
        if st.button("Aggiorna"): 
            st.session_state.stock_centrale += rabbocco
            st.rerun()

# --- AREA SUBAGENTE ---
else:
    st.title(f"🚀 Area Agente: {st.session_state.users_db[user]['name']}")
    st.metric("Tuo Budget", f"{st.session_state.users_db[user]['budget']:,.0f}")
    with st.form("vendita"):
        id_c = st.text_input("ID StarMaker Cliente")
        eur = st.number_input("Euro", min_value=1)
        if st.form_submit_button("REGISTRA"):
            coin_v = eur * COIN_PER_EURO
            if st.session_state.users_db[user]["budget"] >= coin_v:
                m = eur * MARGINE_COIN
                st.session_state.db_vendite.append({"Data": datetime.now().strftime("%d/%m %H:%M"), "Agente": user, "ID Cliente": id_c, "Euro": eur, "Coin": coin_v, "m_sub": m/2, "m_agenzia": m/2})
                st.session_state.users_db[user]["budget"] -= coin_v
                st.session_state.users_db[user]["guadagno_accumulato_coin"] += (m/2)
                st.rerun()
            else: st.error("Budget esaurito!")

if st.sidebar.button("Logout"): st.session_state.authenticated = False; st.rerun()
