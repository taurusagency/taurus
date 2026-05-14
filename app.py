import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - StarMaker Dashboard", layout="wide")

# --- DATABASE INIZIALE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
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

# --- STILE CSS ---
st.markdown("""
<style>
    .profit-container {
        position: fixed; top: 70px; right: 20px; z-index: 1000;
        background: #1e1e1e; color: #FFD700; padding: 15px;
        border-radius: 12px; border: 2px solid #FFD700; text-align: center;
    }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    st.title("🛡️ Taurus Agency - Login")
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

# --- DATI ---
user = st.session_state.user_logged
role = st.session_state.user_role
df_all = pd.DataFrame(st.session_state.db_vendite)

# --- CALCOLO PROFITTI ---
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
else:
    mie = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    tot_coin = sum([v['m_sub'] for v in mie])
tot_euro = tot_coin / 101
st.markdown(f'<div class="profit-container">GUADAGNO<br><b>{tot_coin:,.0f} COIN</b><br>{tot_euro:,.2f} €</div>', unsafe_allow_html=True)

# --- INTERFACCIA ---
if role == "Agenzia":
    st.title(f"🛡️ Pannello TaurusMaster")
    
    t1, t2, t3, t4 = st.tabs(["👥 Rete", "💰 Rabbocchi", "🏆 Classifica Gara", "📜 Registro ID"])
    
    with t1:
        cols = st.columns(3)
        for i, (u_key, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 3]:
                    with st.container(border=True):
                        st.write(f"### {data['name']}")
                        new_u = st.text_input("Modifica User", value=u_key, key=f"u_{u_key}")
                        new_n = st.text_input("Modifica Nome", value=data['name'], key=f"n_{u_key}")
                        new_p = st.text_input("Modifica Pass", value=data['pass'], key=f"p_{u_key}")
                        if st.button("Salva", key=f"s_{u_key}"):
                            if new_u != u_key:
                                st.session_state.users_db[new_u] = st.session_state.users_db.pop(u_key)
                            st.session_state.users_db[new_u].update({"name": new_n, "pass": new_p})
                            st.rerun()

    with t3:
        st.subheader("Gara Taurus: Chi vende di più?")
        if not df_all.empty:
            # Raggruppa vendite per nome reale dell'agente
            classifica = df_all.groupby('Nome Agente')['Euro'].sum().reset_index()
            fig = px.bar(classifica, x='Nome Agente', y='Euro', color='Euro', title="Vendite Totali (€)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nessun dato per la classifica.")

    with t4:
        st.subheader("Registro Segreto (Solo per Te)")
        st.dataframe(df_all, use_container_width=True)

else:
    # --- AREA SUBAGENTE ---
    st.title(f"🚀 Operativo: {st.session_state.users_db[user]['name']}")
    
    c1, c2 = st.columns(2)
    c1.metric("Il Tuo Budget", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("vendita"):
        st.subheader("Registra Ricarica")
        id_c = st.text_input("ID StarMaker Cliente")
        eur = st.number_input("Euro Ricevuti", min_value=1)
        if st.form_submit_button("CONFERMA E SCARICA"):
            coin_v = eur * COIN_PER_EURO
            if st.session_state.users_db[user]["budget"] >= coin_v:
                m = eur * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user,
                    "Nome Agente": st.session_state.users_db[user]['name'],
                    "ID Cliente": id_c,
                    "Euro": eur,
                    "Coin": coin_v,
                    "m_sub": m/2, "m_agenzia": m/2
                })
                st.session_state.users_db[user]["budget"] -= coin_v
                st.rerun()
            else:
                st.error("Budget insufficiente!")

    st.divider()
    st.subheader("🏆 La Gara degli Agenti")
    if not df_all.empty:
        # Classifica visibile a tutti ma SENZA gli ID clienti
        classifica_pub = df_all.groupby('Nome Agente')['Euro'].sum().sort_values(ascending=False)
        st.bar_chart(classifica_pub)
    
    st.subheader("📜 Il Tuo Storico Personale")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    if mie_v:
        # Mostra solo i dati propri, ID incluso perché sono i suoi clienti
        st.table(pd.DataFrame(mie_v)[['Data', 'ID Cliente', 'Euro', 'Coin']])

if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
