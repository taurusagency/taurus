import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - StarMaker", layout="wide", initial_sidebar_state="collapsed")

# --- DATABASE INIZIALE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'totale_stock_agenzia' not in st.session_state:
    st.session_state.totale_stock_agenzia = 1000000 
if 'users_db' not in st.session_state:
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

# --- STILE CSS PERSONALIZZATO ---
st.markdown("""
<style>
    .profit-container {
        position: fixed; top: 70px; right: 20px; z-index: 1000;
        background: #1e1e1e; color: #FFD700; padding: 15px;
        border-radius: 12px; border: 2px solid #FFD700; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .agent-card {
        background: white; padding: 15px; border-radius: 12px;
        border-top: 5px solid #FFD700; margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- SCHERMATA LOGIN ---
if not st.session_state.authenticated:
    st.title("🛡️ Taurus Agency - Accesso")
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
                st.error("Credenziali non valide.")
    st.stop()

# --- LOGICA PROFITTI ---
user = st.session_state.user_logged
role = st.session_state.user_role
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
else:
    mie = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    tot_coin = sum([v['m_sub'] for v in mie])
tot_euro = tot_coin / 101

st.markdown(f'<div class="profit-container">GUADAGNO<br><b>{tot_coin:,.0f} COIN</b><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- DASHBOARD ADMIN (TAURUSMASTER) ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    col_a, col_b = st.columns(2)
    col_a.metric("Magazzino Centrale", f"{st.session_state.totale_stock_agenzia:,.0f} Coin")
    with col_b:
        rabbocco = st.number_input("Carica Stock Agenzia (Coin)", step=50000)
        if st.button("Conferma Carico"):
            st.session_state.totale_stock_agenzia += rabbocco
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 Gestione Rete", "💰 Rabbocchi Subagenti", "📜 Registro Vendite"])
    
    with tab1:
        cols = st.columns(2)
        # Usiamo una lista per iterare così da poter rinominare le chiavi
        for i, (old_user, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 2]:
                    with st.container(border=True):
                        st.write(f"### {data['name']}")
                        # NUOVO: Campo per modificare l'Username reale di accesso
                        new_user = st.text_input(f"Modifica Username di Accesso", value=old_user, key=f"u_{old_user}")
                        new_name = st.text_input(f"Nome Reale", value=data['name'], key=f"n_{old_user}")
                        new_pass = st.text_input(f"Password", value=data['pass'], key=f"p_{old_user}")
                        
                        if st.button(f"Salva Modifiche {old_user}", key=f"save_{old_user}"):
                            # Se l'username è cambiato, aggiorniamo la chiave nel dizionario
                            if new_user != old_user:
                                st.session_state.users_db[new_user] = st.session_state.users_db.pop(old_user)
                            st.session_state.users_db[new_user].update({"name": new_name, "pass": new_pass})
                            st.success("Dati aggiornati!")
                            st.rerun()
                        
                        st.code(f"Link: {APP_URL}\nUser: {new_user}\nPass: {new_pass}")

    with tab2:
        st.subheader("Invia o Togli Monete ai Subagenti")
        sub_list = [u for u, d in st.session_state.users_db.items() if d['role'] == "Subagente"]
        sel = st.selectbox("Seleziona Agente", sub_list)
        val = st.number_input("Quantità", step=5000)
        if st.button("Esegui Movimento"):
            if st.session_state.totale_stock_agenzia >= val:
                st.session_state.users_db[sel]["budget"] += val
                st.session_state.totale_stock_agenzia -= val
                st.success("Trasferimento completato!")
                st.rerun()
            else:
                st.error("Stock centrale insufficiente!")

    with tab3:
        if st.session_state.db_vendite:
            st.table(pd.DataFrame(st.session_state.db_vendite))
        else:
            st.info("Nessuna vendita registrata.")

# --- AREA SUBAGENTE ---
else:
    st.title(f"🚀 Operativo: {st.session_state.users_db[user]['name']}")
    st.metric("Tuo Budget Disponibile", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("vendita"):
        idc = st.text_input("ID StarMaker Cliente")
        eur = st.number_input("Euro ricevuti", min_value=1)
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
                st.error("Budget insufficiente!")
    
    st.subheader("Le tue ricariche")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    if mie_v:
        st.table(pd.DataFrame(mie_v))

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
