import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Login", page_icon="🛡️", layout="wide")

# --- DATABASE SIMULATO (In un'app reale useresti un database vero) ---
# Qui salviamo le credenziali che tu modifichi nel pannello Admin
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"pass": "taurus2026", "role": "Agenzia"},
    }
    # Pre-popoliamo i 12 agenti con nomi di default modificabili
    for i in range(1, 13):
        st.session_state.users_db[f"agente{i}"] = {"pass": f"pass{i}", "role": "Subagente", "name": f"Subagente {i}"}

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []

# --- COSTANTI ---
COIN_PER_EURO_VENDITA = 91
MARGINE_COIN_TOTALE = 10
APP_URL = "https://taurus-agency.streamlit.app" 

# --- STILE CSS ---
st.markdown("""
<style>
    .profit-container {
        position: fixed; top: 60px; right: 20px; z-index: 999;
        background: linear-gradient(135deg, #1e1e1e 0%, #333333 100%);
        color: #FFD700; padding: 15px; border-radius: 15px; border: 2px solid #FFD700;
        text-align: center; min-width: 180px;
    }
    .agent-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 6px solid #FFD700; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. SCHERMATA DI LOGIN ---
if not st.session_state.authenticated:
    st.title("🛡️ Accesso Taurus Agency")
    with st.form("login_form"):
        user_input = st.text_input("Username")
        pass_input = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Accedi")
        
        if login_btn:
            if user_input in st.session_state.users_db and st.session_state.users_db[user_input]["pass"] == pass_input:
                st.session_state.authenticated = True
                st.session_state.user_logged = user_input
                st.session_state.user_role = st.session_state.users_db[user_input]["role"]
                st.rerun()
            else:
                st.error("Credenziali errate. Riprova.")
    st.stop() # Blocca il resto del codice se non autenticato

# --- 2. LOGICA POST-LOGIN ---
current_user = st.session_state.user_logged
user_role = st.session_state.user_role

# Calcolo Guadagni
if user_role == 'Agenzia':
    tot_coin = sum([v['margine_agency_coin'] for v in st.session_state.db_vendite])
    tot_euro = sum([v['margine_agency_euro'] for v in st.session_state.db_vendite])
else:
    # Filtra solo le vendite fatte dall'utente loggato
    mie_vendite = [v for v in st.session_state.db_vendite if v['Agente'] == current_user]
    tot_coin = sum([v['margine_sub_coin'] for v in mie_vendite])
    tot_euro = sum([v['margine_sub_euro'] for v in mie_vendite])

# Widget Guadagno Fisso
st.markdown(f'<div class="profit-container">GUADAGNO TOTALE<br><span style="font-size:1.5rem; font-weight:bold;">{tot_coin:,.0f} COIN</span><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- 3. INTERFACCIA AGENZIA ---
if user_role == 'Agenzia':
    st.title("Pannello Admin - Taurus Agency")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    tab1, tab2 = st.tabs(["📊 Dashboard Subagenti", "📝 Registro Vendite"])
    
    with tab1:
        cols = st.columns(2)
        for i in range(1, 13):
            agent_key = f"agente{i}"
            with cols[i%2]:
                st.markdown(f'<div class="agent-card"><h3>{st.session_state.users_db[agent_key]["name"]}</h3>', unsafe_allow_html=True)
                with st.expander("Modifica Credenziali e Invia"):
                    # Qui puoi modificare nome e password
                    new_name = st.text_input("Rinomina Agente (es: Marco)", value=st.session_state.users_db[agent_key]["name"], key=f"n_{i}")
                    new_pass = st.text_input("Nuova Password", value=st.session_state.users_db[agent_key]["pass"], key=f"p_{i}")
                    
                    # Aggiorna il database "finto"
                    st.session_state.users_db[agent_key]["name"] = new_name
                    st.session_state.users_db[agent_key]["pass"] = new_pass
                    
                    msg = f"🛡️ *TAURUS AGENCY*\\n\\n🔗 Link: {APP_URL}\\n👤 User: {agent_key}\\n🔑 Pass: {new_pass}"
                    st.code(msg)
                    st.button(f"Salva e Conferma {i}", key=f"save_{i}")
                st.markdown('</div>', unsafe_allow_html=True)

# --- 4. INTERFACCIA SUBAGENTE ---
else:
    st.title(f"Benvenuto, {st.session_state.users_db[current_user]['name']}")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

    with st.form("ricarica"):
        st.subheader("📲 Nuova Operazione")
        id_sm = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Euro Ricevuti", min_value=1)
        
        # Calcoli
        coin_cli = euro * COIN_PER_EURO_VENDITA
        g_coin = (euro * MARGINE_COIN_TOTALE) / 2
        g_euro = g_coin / 101
        
        st.write(f"Al cliente: **{coin_cli} Coin** | Tuo Guadagno: **{g_coin} Coin**")
        
        if st.form_submit_button("Registra Vendita"):
            st.session_state.db_vendite.append({
                "Data": datetime.now().strftime("%d/%m %H:%M"),
                "Agente": current_user,
                "ID Cliente": id_sm,
                "Euro": euro,
                "margine_sub_coin": g_coin, "margine_sub_euro": g_euro,
                "margine_agency_coin": g_coin, "margine_agency_euro": g_euro
            })
            st.success("Ricarica Registrata!")
            st.rerun()
