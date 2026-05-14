import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Gestione Coin", layout="wide")

# --- DATABASE INIZIALE ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
    }
    for i in range(1, 13):
        st.session_state.users_db[f"agente{i}"] = {
            "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", 
            "budget": 0, "guadagno_accumulato_coin": 0
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
MIO_WHATSAPP = "+393331234567" # <--- INSERISCI IL TUO NUMERO VERO QUI

# --- STILE CSS ---
st.markdown("""
<style>
    .profit-container {
        position: fixed; top: 70px; right: 20px; z-index: 1000;
        background: #1e1e1e; color: #FFD700; padding: 15px;
        border-radius: 12px; border: 2px solid #FFD700; text-align: center;
        cursor: pointer; transition: 0.3s;
    }
    .profit-container:hover { background: #333; transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    st.title("🛡️ Taurus Agency - Login")
    with st.form("login_form"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("ACCEDI"):
            if u in st.session_state.users_db and st.session_state.users_db[u]["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_logged = u
                st.session_state.user_role = st.session_state.users_db[u]["role"]
                st.rerun()
            else:
                st.error("Credenziali errate!")
    st.stop()

user = st.session_state.user_logged
role = st.session_state.user_role

# --- QUADRATINO GUADAGNO CLICCABILE ---
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin:,.0f} COIN</b><br>{tot_coin/101:.2f} €</div>', unsafe_allow_html=True)
else:
    guadagno_agente = st.session_state.users_db[user]["guadagno_accumulato_coin"]
    testo_wa = urllib.parse.quote(f"Ciao TaurusMaster, richiedo il compenso maturato di {guadagno_agente:,.0f} monete.")
    link_wa = f"https://wa.me/{MIO_WHATSAPP}?text={testo_wa}"
    
    st.markdown(f"""
        <a href="{link_wa}" target="_blank" style="text-decoration: none;">
            <div class="profit-container">
                RICHIEDI COMPENSO<br><b>{guadagno_agente:,.0f} COIN</b><br>{guadagno_agente/101:.2f} €
                <br><span style="font-size: 0.7rem;">(Clicca per WhatsApp)</span>
            </div>
        </a>
    """, unsafe_allow_html=True)

# --- DASHBOARD ADMIN ---
if role == "Agenzia":
    st.title("🛡️ Pannello Amministratore")
    
    col1, col2 = st.columns(2)
    col1.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col2:
        rabbocco = st.number_input("Carica Stock Centrale (Coin)", step=50000)
        if st.button("Conferma Ricarica"):
            st.session_state.stock_centrale += rabbocco
            st.rerun()

    t1, t2, t3 = st.tabs(["👥 Gestione & Pagamenti", "💰 Rabbocchi Agenti", "🏆 Gara Taurus"])
    
    with t1:
        cols = st.columns(2)
        for i, (u_key, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 2]:
                    with st.container(border=True):
                        st.write(f"### {data['name']}")
                        st.write(f"Guadagno da pagare: **{data['guadagno_accumulato_coin']:,.0f} Coin**")
                        if st.button(f"Segna come Pagato (Azzera)", key=f"pay_{u_key}"):
                            st.session_state.users_db[u_key]["guadagno_accumulato_coin"] = 0
                            st.success("Compensi azzerati!")
                            st.rerun()
                        # Modifica credenziali
                        new_u = st.text_input("Username", value=u_key, key=f"u_{u_key}")
                        new_p = st.text_input("Password", value=data['pass'], key=f"p_{u_key}")
                        if st.button("Salva Credenziali", key=f"s_{u_key}"):
                            if new_u != u_key:
                                st.session_state.users_db[new_u] = st.session_state.users_db.pop(u_key)
                            st.session_state.users_db[new_u]["pass"] = new_p
                            st.rerun()

    with t2:
        st.subheader("Invia monete ai subagenti (Sottrae dallo Stock Reale)")
        sel_agente = st.selectbox("Seleziona Agente", [k for k,v in st.session_state.users_db.items() if v['role']=="Subagente"])
        quantita = st.number_input("Quantità Coin", step=10000)
        if st.button("Esegui Trasferimento"):
            if st.session_state.stock_centrale >= quantita:
                st.session_state.users_db[sel_agente]["budget"] += quantita
                st.session_state.stock_centrale -= quantita
                st.success("Trasferito!")
                st.rerun()
            else:
                st.error("Stock centrale insufficiente!")

# --- AREA OPERATIVA SUBAGENTE ---
else:
    st.title(f"🚀 Dashboard: {st.session_state.users_db[user]['name']}")
    st.metric("Budget Monete Disponibili", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("form_vendita"):
        st.subheader("Compilazione Ricarica")
        id_cli = st.text_input("ID StarMaker Cliente")
        euro_v = st.number_input("Importo (€)", min_value=1)
        
        # PRE-COMPILAZIONE SUPPORTO
        coin_cliente = euro_v * COIN_PER_EURO
        st.info(f"💡 Supporto: Per {euro_v}€ darai **{coin_cliente:,.0f} monete** al cliente.")
        
        if st.form_submit_button("CONFERMA VENDITA"):
            if st.session_state.users_db[user]["budget"] >= coin_cliente:
                margine = euro_v * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "Nome Agente": st.session_state.users_db[user]['name'],
                    "ID Cliente": id_cli, "Euro": euro_v, "Coin": coin_cliente,
                    "m_sub": margine/2, "m_agenzia": margine/2
                })
                # Aggiornamento budget e guadagno maturato
                st.session_state.users_db[user]["budget"] -= coin_cliente
                st.session_state.users_db[user]["guadagno_accumulato_coin"] += (margine/2)
                st.success("Registrato!")
                st.rerun()
            else:
                st.error("Budget insufficiente!")

    st.subheader("📜 Storico Tue Vendite")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    if mie_v:
        st.table(pd.DataFrame(mie_v)[['Data', 'ID Cliente', 'Euro', 'Coin']])

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
