import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", page_icon="🐂", layout="wide")

# --- DATABASE UTENTI ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        # L'UNICO ADMIN (TU)
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
        # SUBAGENTI PERSONALIZZATI
        "Queen": {"pass": "Taurus69", "role": "Subagente", "name": "Queen", "budget": 0, "guadagno_accumulato_coin": 0, "wa": ""},
    }
    # Generazione automatica degli altri 11 subagenti
    for i in range(1, 12):
        u_key = f"agente{i}"
        if u_key not in st.session_state.users_db:
            st.session_state.users_db[u_key] = {
                "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", 
                "budget": 0, "guadagno_accumulato_coin": 0, "wa": ""
            }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000

# --- COSTANTI ---
APP_URL = "https://taurus-agency.streamlit.app"
COIN_PER_EURO = 91
MARGINE_COIN = 10 

# --- STILE CSS ---
st.markdown("""
<style>
    .taurus-header { text-align: center; padding: 20px; background: #1a1a1a; color: #FFD700; border-radius: 15px; margin-bottom: 25px; border: 1px solid #FFD700; }
    .profit-container { position: fixed; top: 70px; right: 20px; z-index: 1000; background: #1e1e1e; color: #FFD700; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; text-align: center; }
    .wa-button { background-color: #25D366; color: white; padding: 8px 15px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    st.markdown('<div class="taurus-header"><h1>🐂 TAURUS AGENCY LOGIN</h1></div>', unsafe_allow_html=True)
    u_in = st.text_input("Username")
    p_in = st.text_input("Password", type="password")
    if st.button("ACCEDI ALLA DASHBOARD"):
        if u_in in st.session_state.users_db and st.session_state.users_db[u_in]["pass"] == p_in:
            st.session_state.authenticated = True
            st.session_state.user_logged = u_in
            st.session_state.user_role = st.session_state.users_db[u_in]["role"]
            st.rerun()
        else:
            st.error("Credenziali non valide.")
    st.stop()

user = st.session_state.user_logged
role = st.session_state.user_role

# --- DASHBOARD ADMIN (TAURUSMASTER) ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    
    # Widget Profitto Agenzia
    tot_coin_agenzia = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin_agenzia:,.0f} COIN</b><br>{tot_coin_agenzia/101:.2f} €</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["👥 Gestione Rete & WhatsApp", "💰 Stock e Rabbocchi"])
    
    with tab1:
        cols = st.columns(3)
        for i, (u_k, d) in enumerate(list(st.session_state.users_db.items())):
            if d['role'] == "Subagente":
                with cols[i % 3]:
                    with st.container(border=True):
                        st.write(f"### {d['name']}")
                        # Input numero WhatsApp per invio link
                        num_wa = st.text_input("Numero WhatsApp", value=d.get('wa', ""), key=f"wa_{u_k}", placeholder="39333...")
                        st.session_state.users_db[u_k]['wa'] = num_wa
                        
                        # Generazione Messaggio e Link WhatsApp
                        testo_msg = f"🛡️ *TAURUS AGENCY - ACCESSO*\\n\\n🔗 Link: {APP_URL}\\n👤 User: {u_k}\\n🔑 Pass: {d['pass']}"
                        testo_encoded = urllib.parse.quote(testo_msg.replace("\\n", "\n"))
                        link_wa = f"https://wa.me/{num_wa}?text={testo_encoded}"
                        
                        st.markdown(f'<a href="{link_wa}" target="_blank" class="wa-button">📲 Invia Credenziali</a>', unsafe_allow_html=True)
                        
                        with st.expander("Modifica Dati"):
                            st.session_state.users_db[u_k]["pass"] = st.text_input("Cambia Pass", d['pass'], key=f"pw_{u_k}")
                            if st.button("Azzera Compensi", key=f"az_{u_k}"):
                                st.session_state.users_db[u_k]["guadagno_accumulato_coin"] = 0; st.rerun()

    with tab2:
        st.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
        sel_agente = st.selectbox("Seleziona Agente per Rabbocco", [k for k,v in st.session_state.users_db.items() if v['role']=="Subagente"])
        quantita = st.number_input("Quantità Coin da inviare", step=10000)
        if st.button("Esegui Trasferimento"):
            if st.session_state.stock_centrale >= quantita:
                st.session_state.users_db[sel_agente]["budget"] += quantita
                st.session_state.stock_centrale -= quantita
                st.success("Trasferimento completate!"); st.rerun()

# --- AREA SUBAGENTE ---
else:
    st.title(f"🚀 Dashboard Agente: {st.session_state.users_db[user]['name']}")
    
    # Widget Profitto Subagente
    g_acc = st.session_state.users_db[user]["guadagno_accumulato_coin"]
    st.markdown(f'<div class="profit-container">IL TUO GUADAGNO<br><b>{g_acc:,.0f} COIN</b><br>{g_acc/101:.2f} €</div>', unsafe_allow_html=True)

    st.metric("Tuo Budget (Coin da vendere)", f"{st.session_state.users_db[user]['budget']:,.0f}")
    
    with st.form("vendita"):
        id_cli = st.text_input("ID StarMaker Cliente")
        euro_v = st.number_input("Prezzo in Euro (€)", min_value=1)
        st.info(f"💡 Darai {euro_v * COIN_PER_EURO:,.0f} monete al cliente.")
        
        if st.form_submit_button("CONFERMA VENDITA"):
            coin_necessari = euro_v * COIN_PER_EURO
            if st.session_state.users_db[user]["budget"] >= coin_necessari:
                margine = euro_v * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "ID Cliente": id_cli, "Euro": euro_v, "Coin": coin_necessari,
                    "m_sub": margine/2, "m_agenzia": margine/2
                })
                st.session_state.users_db[user]["budget"] -= coin_necessari
                st.session_state.users_db[user]["guadagno_accumulato_coin"] += (margine/2)
                st.rerun()
            else:
                st.error("Budget insufficiente!")

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False; st.rerun()
