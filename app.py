import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - StarMaker", layout="wide")

# --- INIZIALIZZAZIONE DATABASE E CREDENZIALI ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'totale_stock_agenzia' not in st.session_state:
    st.session_state.totale_stock_agenzia = 1000000 
if 'users_db' not in st.session_state:
    # IMPOSTATE LE TUE CREDENZIALI MEMORIZZATE
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus26", "role": "Agenzia", "name": "Taurus Owner"},
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
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .agent-card {
        background: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #FFD700; margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. SCHERMATA DI LOGIN ---
if not st.session_state.authenticated:
    st.title("🛡️ Taurus Agency - Accesso Sistema")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("ACCEDI"):
            # Controllo preciso delle credenziali
            if u in st.session_state.users_db and st.session_state.users_db[u]["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_logged = u
                st.session_state.user_role = st.session_state.users_db[u]["role"]
                st.rerun()
            else:
                st.error("Credenziali non valide. Controlla maiuscole e minuscole.")
    st.stop()

# --- 2. LOGICA DATI E PROFITTI ---
user = st.session_state.user_logged
role = st.session_state.user_role

if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
else:
    mie = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    tot_coin = sum([v['m_sub'] for v in mie])
tot_euro = tot_coin / 101

st.markdown(f'<div class="profit-container">GUADAGNO<br><b>{tot_coin:,.0f} COIN</b><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- 3. DASHBOARD AGENZIA (TAURUSMASTER) ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Magazzino Centrale", f"{st.session_state.totale_stock_agenzia:,.0f} Coin")
    with col_b:
        rabbocco = st.number_input("Carica Stock Agenzia (Coin)", step=50000)
        if st.button("Conferma Carico"):
            st.session_state.totale_stock_agenzia += rabbocco
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 Gestione Rete", "💰 Rabbocchi Subagenti", "📜 Registro Vendite"])
    
    with tab1:
        cols = st.columns(2)
        for i in range(1, 13):
            ak = f"agente{i}"
            with cols[i%2]:
                with st.container(border=True):
                    st.write(f"### {st.session_state.users_db[ak]['name']}")
                    st.session_state.users_db[ak]["name"] = st.text_input(f"Nome Reale {i}", value=st.session_state.users_db[ak]["name"], key=f"n{i}")
                    st.session_state.users_db[ak]["pass"] = st.text_input(f"Password {i}", value=st.session_state.users_db[ak]["pass"], key=f"p{i}")
                    st.code(f"Link: {APP_URL}\nUser: {ak}\nPass: {st.session_state.users_db[ak]['pass']}")

    with tab2:
        st.subheader("Invia o Togli Monete ai Subagenti")
        sel = st.selectbox("Seleziona Agente", [f"agente{i}" for i in range(1, 13)])
        val = st.number_input("Quantità (usa il '-' per togliere)", step=5000)
        if st.button("Esegui Movimento"):
            if st.session_state.totale_stock_agenzia >= val:
                st.session_state.users_db[sel]["budget"] += val
                st.session_state.totale_stock_agenzia -= val
                st.success("Operazione completata!")
                st.rerun()
            else:
                st.error("Stock insufficiente nel magazzino centrale!")

    with tab3:
        st.table(pd.DataFrame(st.session_state.db_vendite))

# --- 4. AREA OPERATIVA SUBAGENTE ---
else:
    st.title(f"🚀 Operativo: {st.session_state.users_db[user]['name']}")
    st.metric("Tuo Budget Disponibile", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("vendita"):
        st.subheader("Registra Ricarica Cliente")
        idc = st.text_input("ID StarMaker")
        eur = st.number_input("Euro pagati dal cliente", min_value=1)
        # Calcolo 91 coin per ogni euro
        coin_v = eur * COIN_PER_EURO
        
        if st.form_submit_button("CONFERMA VENDITA"):
            if st.session_state.users_db[user]["budget"] >= coin_v:
                margine = eur * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "ID Cliente": idc, "Euro": eur, "Coin": coin_v,
                    "m_sub": margine/2, "m_agenzia": margine/2
                })
                st.session_state.users_db[user]["budget"] -= coin_v
                st.rerun()
            else:
                st.error("Budget monete esaurito! Contatta l'agenzia.")
    
    st.subheader("Le tue ricariche")
    st.table(pd.DataFrame([v for v in st.session_state.db_vendite if v['Agente'] == user]))

if st.sidebar.button("Log out"):
    st.session_state.authenticated = False
    st.rerun()
