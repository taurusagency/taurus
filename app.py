import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", layout="wide")

# --- DATABASE INIZIALE E CREDENZIALI ---
if 'users_db' not in st.session_state:
    # IMPOSTATE LE TUE CREDENZIALI ESATTE DALL'IMMAGINE 10
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
    }
    # Generazione dei 12 subagenti
    for i in range(1, 13):
        st.session_state.users_db[f"agente{i}"] = {
            "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", "budget": 0
        }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000

# --- COSTANTI DI BUSINESS ---
COIN_PER_EURO = 91
MARGINE_COIN = 10 
APP_URL = "https://taurus-agency.streamlit.app"

# --- STILE GRAFICO ---
st.markdown("""
<style>
    .profit-container {
        position: fixed; top: 70px; right: 20px; z-index: 1000;
        background: #1e1e1e; color: #FFD700; padding: 15px;
        border-radius: 12px; border: 2px solid #FFD700; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. SISTEMA DI LOGIN ---
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
                st.error("Credenziali errate! Verifica maiuscole e minuscole.")
    st.stop()

# --- 2. LOGICA PROFITTI ---
user = st.session_state.user_logged
role = st.session_state.user_role
df_vendite = pd.DataFrame(st.session_state.db_vendite)

if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
else:
    mie = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    tot_coin = sum([v['m_sub'] for v in mie])
tot_euro = tot_coin / 101

st.markdown(f'<div class="profit-container">GUADAGNO<br><b>{tot_coin:,.0f} COIN</b><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- 3. DASHBOARD TAURUSMASTER (AMMINISTRATORE) ---
if role == "Agenzia":
    st.title("🛡️ Pannello Amministratore")
    
    col1, col2 = st.columns(2)
    col1.metric("Stock Centrale Agenzia", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col2:
        rabbocco = st.number_input("Ricarica Stock (Coin)", step=50000)
        if st.button("Conferma Ricarica"):
            st.session_state.stock_centrale += rabbocco
            st.rerun()

    t1, t2, t3, t4 = st.tabs(["👥 Gestione Rete", "💰 Rabbocchi Agenti", "🏆 Gara Taurus", "📜 Registro Segreto ID"])
    
    with t1:
        cols = st.columns(2)
        for i, (u_key, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 2]:
                    with st.container(border=True):
                        st.write(f"### {data['name']}")
                        new_u = st.text_input("Modifica Username", value=u_key, key=f"u_{u_key}")
                        new_n = st.text_input("Modifica Nome Reale", value=data['name'], key=f"n_{u_key}")
                        new_p = st.text_input("Modifica Password", value=data['pass'], key=f"p_{u_key}")
                        if st.button("Salva", key=f"s_{u_key}"):
                            if new_u != u_key:
                                st.session_state.users_db[new_u] = st.session_state.users_db.pop(u_key)
                            st.session_state.users_db[new_u].update({"name": new_n, "pass": new_p})
                            st.rerun()
                        st.code(f"User: {new_u} | Pass: {new_p}")

    with t3:
        st.subheader("Gara Mensile: Chi vende di più?")
        if not df_vendite.empty:
            classifica = df_vendite.groupby('Nome Agente')['Euro'].sum().reset_index().sort_values(by='Euro', ascending=False)
            fig = px.bar(classifica, x='Nome Agente', y='Euro', color='Euro', title="Totale Vendite (€)")
            st.plotly_chart(fig, use_container_width=True)

    with t4:
        st.subheader("Registro Completo (Solo Amministratore)")
        st.dataframe(df_vendite, use_container_width=True)

# --- 4. AREA OPERATIVA SUBAGENTE ---
else:
    st.title(f"🚀 Dashboard Agente: {st.session_state.users_db[user]['name']}")
    st.metric("Budget Disponibile", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("form_vendita"):
        st.subheader("Compilazione Ricarica")
        id_cli = st.text_input("ID StarMaker Cliente")
        euro_v = st.number_input("Euro Ricevuti (€)", min_value=1)
        if st.form_submit_button("CONFERMA E REGISTRA"):
            coin_v = euro_v * COIN_PER_EURO
            if st.session_state.users_db[user]["budget"] >= coin_v:
                margine = euro_v * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "Nome Agente": st.session_state.users_db[user]['name'],
                    "ID Cliente": id_cli, "Euro": euro_v, "Coin": coin_v,
                    "m_sub": margine/2, "m_agenzia": margine/2
                })
                st.session_state.users_db[user]["budget"] -= coin_v
                st.rerun()
            else:
                st.error("Budget insufficiente! Contatta TaurusMaster.")

    st.subheader("🏆 La Gara del Team")
    if not df_vendite.empty:
        st.bar_chart(df_vendite.groupby('Nome Agente')['Euro'].sum())
    
    st.subheader("📜 Storico Personale")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    if mie_v:
        st.table(pd.DataFrame(mie_v)[['Data', 'ID Cliente', 'Euro', 'Coin']])

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
