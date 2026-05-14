import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - StarMaker", layout="wide")

# --- INIZIALIZZAZIONE DATABASE (SESSION STATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'totale_stock_agenzia' not in st.session_state:
    st.session_state.totale_stock_agenzia = 1000000  # Tuo magazzino iniziale
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"pass": "taurus2026", "role": "Agenzia", "name": "Taurus Admin"},
    }
    for i in range(1, 13):
        st.session_state.users_db[f"agente{i}"] = {
            "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", "budget": 0
        }

# --- COSTANTI ---
COIN_PER_EURO = 91
MARGINE_COIN = 10 
APP_URL = "https://taurus-agency.streamlit.app"

# --- STILE CSS ---
st.markdown("""
<style>
    .profit-container {
        position: fixed; top: 70px; right: 20px; z-index: 1000;
        background: #1e1e1e; color: #FFD700; padding: 15px;
        border-radius: 12px; border: 2px solid #FFD700; text-align: center;
    }
    .main-card {
        background: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. FUNZIONE LOGIN ---
def login():
    st.title("🛡️ Taurus Agency - Accesso Sistema")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("ACCEDI"):
            if u in st.session_state.users_db and st.session_state.users_db[u]["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_logged = u
                st.session_state.user_role = st.session_state.users_db[u]["role"]
                st.rerun()
            else:
                st.error("Credenziali non valide")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- 2. LOGICA DATI ---
user = st.session_state.user_logged
role = st.session_state.user_role

# Calcolo guadagni per widget
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
else:
    mie = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    tot_coin = sum([v['m_sub'] for v in mie])
tot_euro = tot_coin / 101

# Widget Guadagno
st.markdown(f'<div class="profit-container">GUADAGNO<br><b>{tot_coin:,.0f} COIN</b><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- 3. INTERFACCIA AGENZIA (ADMIN) ---
if role == "Agenzia":
    st.title("🛡️ Dashboard Proprietario")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Stock Totale Agenzia", f"{st.session_state.totale_stock_agenzia:,.0f} Coin")
    with col_s2:
        nuovo_stock = st.number_input("Rifornisci Stock Agenzia (Coin)", step=10000)
        if st.button("Aggiorna Magazzino Centrale"):
            st.session_state.totale_stock_agenzia += nuovo_stock
            st.success("Stock aggiornato")

    tab1, tab2, tab3 = st.tabs(["👥 Gestione Rete", "💰 Rabbocchi Monete", "📜 Registro Totale"])
    
    with tab1:
        cols = st.columns(2)
        for i in range(1, 13):
            ak = f"agente{i}"
            with cols[i%2]:
                with st.container(border=True):
                    st.write(f"### {st.session_state.users_db[ak]['name']}")
                    n = st.text_input("Rinomina", value=st.session_state.users_db[ak]["name"], key=f"n{i}")
                    p = st.text_input("Pass", value=st.session_state.users_db[ak]["pass"], key=f"p{i}")
                    st.session_state.users_db[ak]["name"], st.session_state.users_db[ak]["pass"] = n, p
                    st.code(f"Link: {APP_URL}\nUser: {ak}\nPass: {p}")

    with tab2:
        st.subheader("Sposta Monete ai Subagenti")
        sel_agente = st.selectbox("Seleziona Agente", [f"agente{i}" for i in range(1, 13)])
        quantita = st.number_input("Quantità Coin (usa meno '-' per togliere)", step=1000)
        if st.button("Esegui Trasferimento"):
            if st.session_state.totale_stock_agenzia >= quantita:
                st.session_state.users_db[sel_agente]["budget"] += quantita
                st.session_state.totale_stock_agenzia -= quantita
                st.success(f"Trasferiti {quantita} monete a {sel_agente}")
            else:
                st.error("Stock insufficiente!")

    with tab3:
        st.dataframe(pd.DataFrame(st.session_state.db_vendite), use_container_width=True)

# --- 4. INTERFACCIA SUBAGENTE ---
else:
    st.title(f"🚀 Area Operativa: {st.session_state.users_db[user]['name']}")
    st.metric("Il Tuo Budget Disponibile", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("form_vendita"):
        st.subheader("Registra Nuova Ricarica")
        c_id = st.text_input("ID StarMaker Cliente")
        c_euro = st.number_input("Euro ricevuti dal cliente", min_value=1)
        # Calcolo: se vende 1 euro, deve dare 91 coin.
        c_coin = c_euro * COIN_PER_EURO
        
        if st.form_submit_button("CONFERMA E SCARICA COIN"):
            if st.session_state.users_db[user]["budget"] >= c_coin:
                m_tot = c_euro * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Agente": user, "ID Cliente": c_id, "Euro": c_euro, "Coin": c_coin,
                    "m_sub": m_tot/2, "m_agenzia": m_tot/2
                })
                st.session_state.users_db[user]["budget"] -= c_coin
                st.success("Vendita registrata!")
                st.rerun()
            else:
                st.error("Budget insufficiente! Chiedi un rabbocco all'agenzia.")
    
    st.subheader("Il Tuo Storico Vendite")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    st.table(pd.DataFrame(mie_v))

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
