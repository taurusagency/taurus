import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", layout="wide")

# --- DATABASE INIZIALE E CREDENZIALI ---
if 'users_db' not in st.session_state:
    # IMPOSTATE LE TUE CREDENZIALI MEMORIZZATE ESATTAMENTE COME RICHIESTO
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus26", "role": "Agenzia", "name": "Taurus Owner"},
    }
    # Generazione dei 12 subagenti iniziali
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
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border-left: 5px solid #FFD700; }
</style>
""", unsafe_allow_html=True)

# --- 1. LOGICA DI ACCESSO ---
if not st.session_state.authenticated:
    st.title("🛡️ Taurus Agency - Login")
    with st.form("login_form"):
        u = st.text_input("Username (Nome Utente)")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("ACCEDI"):
            # Controllo case-sensitive per TaurusMaster e Taurus26
            if u in st.session_state.users_db and st.session_state.users_db[u]["pass"] == p:
                st.session_state.authenticated = True
                st.session_state.user_logged = u
                st.session_state.user_role = st.session_state.users_db[u]["role"]
                st.rerun()
            else:
                st.error("Credenziali errate! Assicurati di usare TaurusMaster e Taurus26 con le maiuscole corrette.")
    st.stop()

# --- 2. GESTIONE DATI E PROFITTI ---
user = st.session_state.user_logged
role = st.session_state.user_role
df_vendite = pd.DataFrame(st.session_state.db_vendite)

# Calcolo guadagni per il quadratino in alto
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
else:
    mie = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    tot_coin = sum([v['m_sub'] for v in mie])
tot_euro = tot_coin / 101

st.markdown(f'<div class="profit-container">GUADAGNO<br><b>{tot_coin:,.0f} COIN</b><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- 3. INTERFACCIA AMMINISTRATORE (TAURUSMASTER) ---
if role == "Agenzia":
    st.title("🛡️ Pannello Amministratore")
    
    col1, col2 = st.columns(2)
    col1.metric("Stock Centrale Agenzia", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col2:
        rabbocco = st.number_input("Ricarica Stock Centrale (Coin)", step=50000)
        if st.button("Conferma Ricarica"):
            st.session_state.stock_centrale += rabbocco
            st.rerun()

    t1, t2, t3, t4 = st.tabs(["👥 Gestione Rete", "💰 Rabbocchi Agenti", "🏆 Gara e Statistiche", "📜 Registro ID"])
    
    with t1:
        st.subheader("Configurazione Subagenti")
        cols = st.columns(3)
        for i, (u_key, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 3]:
                    with st.container(border=True):
                        st.write(f"### {data['name']}")
                        new_u = st.text_input("Modifica User", value=u_key, key=f"u_{u_key}")
                        new_n = st.text_input("Modifica Nome", value=data['name'], key=f"n_{u_key}")
                        new_p = st.text_input("Modifica Pass", value=data['pass'], key=f"p_{u_key}")
                        if st.button("Salva Modifiche", key=f"s_{u_key}"):
                            if new_u != u_key:
                                st.session_state.users_db[new_u] = st.session_state.users_db.pop(u_key)
                            st.session_state.users_db[new_u].update({"name": new_n, "pass": new_p})
                            st.rerun()
                        st.code(f"User: {new_u}\nPass: {new_p}")

    with t2:
        st.subheader("Invia monete ai subagenti")
        sel_agente = st.selectbox("Seleziona Agente", [k for k,v in st.session_state.users_db.items() if v['role']=="Subagente"])
        quantita = st.number_input("Quantità Coin", step=10000)
        if st.button("Esegui Trasferimento"):
            if st.session_state.stock_centrale >= quantita:
                st.session_state.users_db[sel_agente]["budget"] += quantita
                st.session_state.stock_centrale -= quantita
                st.success("Trasferimento completato!")
                st.rerun()

    with t3:
        st.subheader("📊 Performance Vendite (Gara Mensile)")
        if not df_vendite.empty:
            classifica = df_vendite.groupby('Nome Agente')['Euro'].sum().reset_index().sort_values(by='Euro', ascending=False)
            fig = px.bar(classifica, x='Nome Agente', y='Euro', color='Euro', title="Classifica Vendite in Euro")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Inizia a registrare vendite per vedere il grafico della gara!")

    with t4:
        st.subheader("Registro Completo (Solo Amministratore)")
        st.dataframe(df_vendite, use_container_width=True)

# --- 4. INTERFACCIA SUBAGENTE (OPERATIVO) ---
else:
    st.title(f"🚀 Dashboard Agente: {st.session_state.users_db[user]['name']}")
    
    c1, c2 = st.columns(2)
    c1.metric("Il Tuo Budget Disponibile", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("form_vendita"):
        st.subheader("Compilazione Ricarica Cliente")
        id_cli = st.text_input("ID StarMaker Cliente")
        euro_v = st.number_input("Importo Venduto (€)", min_value=1)
        
        if st.form_submit_button("CONFERMA E REGISTRA"):
            coin_v = euro_v * COIN_PER_EURO
            if st.session_state.users_db[user]["budget"] >= coin_v:
                margine = euro_v * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user,
                    "Nome Agente": st.session_state.users_db[user]['name'],
                    "ID Cliente": id_cli,
                    "Euro": euro_v,
                    "Coin": coin_v,
                    "m_sub": margine/2, "m_agenzia": margine/2
                })
                st.session_state.users_db[user]["budget"] -= coin_v
                st.success("Vendita registrata correttamente!")
                st.rerun()
            else:
                st.error("Budget monete insufficiente! Contatta TaurusMaster.")

    st.divider()
    st.subheader("🏆 La Gara del Team (Classifica)")
    if not df_vendite.empty:
        # Mostra la classifica generale a tutti per stimolare la competizione
        grafico_gara = df_vendite.groupby('Nome Agente')['Euro'].sum().sort_values(ascending=False)
        st.bar_chart(grafico_gara)
    
    st.subheader("📜 Il Tuo Storico Giornaliero")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    if mie_v:
        # L'agente vede solo i SUOI ID cliente, non quelli degli altri per privacy
        st.table(pd.DataFrame(mie_v)[['Data', 'ID Cliente', 'Euro', 'Coin']])

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
