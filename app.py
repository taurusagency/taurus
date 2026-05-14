import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", page_icon="🐂", layout="wide")

# --- DATABASE CREDENZIALI FISSE (BLINDATE) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
        "Queen": {"pass": "Taurus69", "role": "Subagente", "name": "Queen"},
    }
    # Generazione automatica altri agenti
    for i in range(1, 13):
        u_k = f"agente{i}"
        if u_k not in st.session_state.users_db:
            st.session_state.users_db[u_k] = {"pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}"}

# --- INIZIALIZZAZIONE DATI PERSISTENTI ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state:
    st.session_state.stock_centrale = 1000000
if 'budgets' not in st.session_state:
    st.session_state.budgets = {k: 0 for k in st.session_state.users_db if st.session_state.users_db[k]['role'] == 'Subagente'}
if 'guadagni' not in st.session_state:
    st.session_state.guadagni = {k: 0 for k in st.session_state.users_db if st.session_state.users_db[k]['role'] == 'Subagente'}
if 'fotos' not in st.session_state:
    st.session_state.fotos = {k: None for k in st.session_state.users_db}

# --- COSTANTI ---
APP_URL = "https://taurus-agency.streamlit.app"
COIN_PER_EURO = 91
MARGINE_COIN = 10 
MIO_WHATSAPP = "+393331234567" # Sostituisci col tuo numero reale

# --- STILE CSS ---
st.markdown("""
<style>
    .taurus-header { text-align: center; padding: 20px; background: #1a1a1a; color: #FFD700; border-radius: 15px; border: 2px solid #FFD700; margin-bottom: 25px; }
    .profit-container { position: fixed; top: 70px; right: 20px; z-index: 1000; background: #1e1e1e; color: #FFD700; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .wa-button { background-color: #25D366; color: white !important; padding: 10px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 10px; }
    .agent-card { background: white; padding: 15px; border-radius: 15px; border-top: 5px solid #FFD700; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="taurus-header"><h1>🐂 TAURUS AGENCY</h1><p>Sistema Professionale Gestione StarMaker</p></div>', unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    with st.container():
        st.subheader("🛡️ Login Riservato")
        u_in = st.text_input("Username")
        p_in = st.text_input("Password", type="password")
        if st.button("ACCEDI ALLA DASHBOARD"):
            if u_in in st.session_state.users_db and st.session_state.users_db[u_in]["pass"] == p_in:
                st.session_state.authenticated = True
                st.session_state.user_logged = u_in
                st.session_state.user_role = st.session_state.users_db[u_in]["role"]
                st.rerun()
            else: st.error("Credenziali non valide.")
    st.stop()

user = st.session_state.user_logged
role = st.session_state.user_role
df_vendite = pd.DataFrame(st.session_state.db_vendite)

# --- QUADRATINO GUADAGNO ---
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin:,.0f} COIN</b><br>{tot_coin/101:.2f} €</div>', unsafe_allow_html=True)
else:
    g_acc = st.session_state.guadagni[user]
    msg_wa = urllib.parse.quote(f"Ciao TaurusMaster, richiedo il compenso di {g_acc:,.0f} monete.")
    st.markdown(f'<a href="https://wa.me/{MIO_WHATSAPP}?text={msg_wa}" target="_blank" style="text-decoration:none;"><div class="profit-container">RICHIEDI COMPENSO<br><b>{g_acc:,.0f} COIN</b><br>{g_acc/101:.2f} €</div></a>', unsafe_allow_html=True)

# --- DASHBOARD ADMIN (TAURUSMASTER) ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    col1, col2 = st.columns(2)
    col1.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col2:
        with st.expander("Modifica o Carica Stock"):
            n_s = st.number_input("Imposta Stock", value=st.session_state.stock_centrale)
            if st.button("Salva Stock Centrale"): st.session_state.stock_centrale = n_s; st.rerun()

    t1, t2, t3, t4 = st.tabs(["👥 Gestione & WhatsApp", "💰 Rabbocchi", "🏆 Gara Taurus", "📜 Registro ID"])
    
    with t1:
        cols = st.columns(3)
        for i, (u_k, d) in enumerate(list(st.session_state.users_db.items())):
            if d['role'] == "Subagente":
                with cols[i % 3]:
                    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                    if st.session_state.fotos[u_k]: st.image(st.session_state.fotos[u_k], width=80)
                    st.write(f"### {d['name']}")
                    st.write(f"Maturato: **{st.session_state.guadagni[u_k]:,.0f} Coin**")
                    if st.button(f"Saldato (Azzera)", key=f"z_{u_k}"):
                        st.session_state.guadagni[u_k] = 0; st.rerun()
                    # WhatsApp Link
                    testo = f"🛡️ *TAURUS AGENCY*\\n\\n🔗 Link: {APP_URL}\\n👤 User: {u_k}\\n🔑 Pass: {d['pass']}"
                    t_enc = urllib.parse.quote(testo.replace("\\n", "\n"))
                    st.markdown(f'<a href="https://wa.me/?text={t_enc}" target="_blank" class="wa-button">📲 Invia su WhatsApp</a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        sel = st.selectbox("Seleziona Agente", [k for k,v in st.session_state.users_db.items() if v['role']=="Subagente"])
        amt = st.number_input("Quantità Coin", step=10000)
        if st.button("Invia Rabbocco"):
            if st.session_state.stock_centrale >= amt:
                st.session_state.budgets[sel] += amt
                st.session_state.stock_centrale -= amt; st.success("Trasferito!"); st.rerun()

    with t3:
        st.subheader("🏆 Classifica Gara Mensile")
        if not df_vendite.empty:
            classifica = df_vendite.groupby('Nome Agente')['Euro'].sum().reset_index().sort_values(by='Euro', ascending=False)
            st.plotly_chart(px.bar(classifica, x='Nome Agente', y='Euro', color='Euro'), use_container_width=True)

    with t4:
        st.subheader("📜 Registro Completo ID Clienti")
        st.dataframe(df_vendite, use_container_width=True)

# --- AREA OPERATIVA SUBAGENTE ---
else:
    st.title(f"🚀 Dashboard: {st.session_state.users_db[user]['name']}")
    with st.sidebar:
        st.subheader("Tuo Profilo")
        foto = st.file_uploader("Carica foto", type=['png', 'jpg', 'jpeg'])
        if foto: st.session_state.fotos[user] = Image.open(foto); st.success("Foto caricata!")

    st.metric("Tuo Budget Disponibile", f"{st.session_state.budgets[user]:,.0f} Coin")
    with st.form("vendita"):
        id_c = st.text_input("ID StarMaker Cliente")
        eur = st.number_input("Euro Ricevuti", min_value=1)
        st.info(f"💡 Erogazione prevista: {eur * COIN_PER_EURO:,.0f} monete")
        if st.form_submit_button("CONFERMA E REGISTRA"):
            c_out = eur * COIN_PER_EURO
            if st.session_state.budgets[user] >= c_out:
                m = eur * MARGINE_COIN
                st.session_state.db_vendite.append({"Data": datetime.now().strftime("%d/%m %H:%M"), "Agente": user, "Nome Agente": st.session_state.users_db[user]['name'], "ID Cliente": id_c, "Euro": eur, "Coin": c_out, "m_sub": m/2, "m_agenzia": m/2})
                st.session_state.budgets[user] -= c_out
                st.session_state.guadagni[user] += (m/2)
                st.rerun()
            else: st.error("Budget monete esaurito!")

    st.subheader("🏆 La Gara del Team")
    if not df_vendite.empty: st.bar_chart(df_vendite.groupby('Nome Agente')['Euro'].sum())
    
    st.subheader("📜 Le Tue Ultime Vendite")
    mie_v = [v for v in st.session_state.db_vendite if v['Agente'] == user]
    if mie_v: st.table(pd.DataFrame(mie_v)[['Data', 'ID Cliente', 'Euro', 'Coin']])

if st.sidebar.button("Logout"): st.session_state.authenticated = False; st.rerun()
