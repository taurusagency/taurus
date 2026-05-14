import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Dashboard", page_icon="🐂", layout="wide")

# --- DATABASE CREDENZIALI (Gestione Dinamica) ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
        "Queen": {"pass": "Taurus69", "role": "Subagente", "name": "Queen"},
    }
    for i in range(1, 13):
        u_k = f"agente{i}"
        if u_k not in st.session_state.users_db:
            st.session_state.users_db[u_k] = {"pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}"}

# --- STATO E DATI ---
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'db_vendite' not in st.session_state: st.session_state.db_vendite = []
if 'stock_centrale' not in st.session_state: st.session_state.stock_centrale = 1000000
if 'budgets' not in st.session_state:
    st.session_state.budgets = {k: 0 for k in st.session_state.users_db if st.session_state.users_db[k].get('role') == 'Subagente'}
if 'guadagni' not in st.session_state:
    st.session_state.guadagni = {k: 0 for k in st.session_state.users_db if st.session_state.users_db[k].get('role') == 'Subagente'}
if 'fotos' not in st.session_state:
    st.session_state.fotos = {} # Inizializzato vuoto per sicurezza

# --- COSTANTI ---
APP_URL = "https://taurus-agency.streamlit.app"
COIN_PER_EURO = 91
MARGINE_COIN = 10 
MIO_WHATSAPP = "+393331234567" 

# --- STILE CSS ---
st.markdown("""
<style>
    .taurus-header { text-align: center; padding: 20px; background: #1a1a1a; color: #FFD700; border-radius: 15px; border: 2px solid #FFD700; margin-bottom: 25px; }
    .profit-container { position: fixed; top: 70px; right: 20px; z-index: 1000; background: #1e1e1e; color: #FFD700; padding: 15px; border-radius: 12px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .wa-button { background-color: #25D366; color: white !important; padding: 10px 20px; text-decoration: none; border-radius: 10px; font-weight: bold; display: inline-block; margin-top: 10px; }
    .agent-card { background: white; padding: 15px; border-radius: 15px; border-top: 5px solid #FFD700; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="taurus-header"><h1>🐂 TAURUS AGENCY</h1></div>', unsafe_allow_html=True)

# --- LOGIN ---
if not st.session_state.authenticated:
    u_in = st.text_input("Username")
    p_in = st.text_input("Password", type="password")
    if st.button("ACCEDI"):
        if u_in in st.session_state.users_db and st.session_state.users_db[u_in]["pass"] == p_in:
            st.session_state.authenticated, st.session_state.user_logged, st.session_state.user_role = True, u_in, st.session_state.users_db[u_in]["role"]
            st.rerun()
        else: st.error("Errore credenziali.")
    st.stop()

user, role = st.session_state.user_logged, st.session_state.user_role
df_v = pd.DataFrame(st.session_state.db_vendite)

# --- PROFITTO ---
if role == "Agenzia":
    tot = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot:,.0f} COIN</b><br>{tot/101:.2f} €</div>', unsafe_allow_html=True)
else:
    g = st.session_state.guadagni.get(user, 0)
    msg = urllib.parse.quote(f"Richiedo compenso di {g:,.0f} monete.")
    st.markdown(f'<a href="https://wa.me/{MIO_WHATSAPP}?text={msg}" target="_blank" style="text-decoration:none;"><div class="profit-container">RICHIEDI COMPENSO<br><b>{g:,.0f} COIN</b><br>{g/101:.2f} €</div></a>', unsafe_allow_html=True)

# --- PANNELLO ADMIN ---
if role == "Agenzia":
    col1, col2 = st.columns(2)
    col1.metric("Stock Centrale", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col2:
        with st.expander("Modifica Stock"):
            n_s = st.number_input("Imposta Stock", value=st.session_state.stock_centrale)
            if st.button("Salva Stock"): st.session_state.stock_centrale = n_s; st.rerun()

    t1, t2, t3, t4 = st.tabs(["👥 Gestione & WhatsApp", "💰 Rabbocchi", "🏆 Gara", "📜 Registro ID"])
    
    with t1:
        cols = st.columns(3)
        subagenti = {k: v for k, v in st.session_state.users_db.items() if v.get('role') == 'Subagente'}
        for i, (u_k, d) in enumerate(subagenti.items()):
            with cols[i % 3]:
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                # FIX ERRORE IMAGE_16.PNG: Controllo se la chiave esiste prima di caricarla
                if u_k in st.session_state.fotos and st.session_state.fotos[u_k]:
                    st.image(st.session_state.fotos[u_k], width=60)
                else:
                    st.write("👤 Nessuna foto")
                
                st.write(f"### {d.get('name', u_k)}")
                curr_g = st.session_state.guadagni.get(u_k, 0)
                st.write(f"Maturato: **{curr_g:,.0f}**")
                
                if st.button(f"Saldato", key=f"z_{u_k}"): 
                    st.session_state.guadagni[u_k] = 0
                    st.rerun()
                
                # Modifica Credenziali
                new_u = st.text_input("Username", u_k, key=f"un_{u_k}")
                new_p = st.text_input("Password", d.get('pass', ''), key=f"pw_{u_k}")
                
                if st.button("Salva Dati", key=f"sv_{u_k}"):
                    if new_u != u_k:
                        st.session_state.users_db[new_u] = st.session_state.users_db.pop(u_k)
                        # Allineamento altri dizionari
                        if u_k in st.session_state.budgets: st.session_state.budgets[new_u] = st.session_state.budgets.pop(u_k)
                        if u_k in st.session_state.guadagni: st.session_state.guadagni[new_u] = st.session_state.guadagni.pop(u_k)
                        if u_k in st.session_state.fotos: st.session_state.fotos[new_u] = st.session_state.fotos.pop(u_k)
                    st.session_state.users_db[new_u]["pass"] = new_p
                    st.rerun()
                
                testo = f"🛡️ *TAURUS AGENCY*\\n\\n🔗 Link: {APP_URL}\\n👤 User: {new_u}\\n🔑 Pass: {new_p}"
                t_enc = urllib.parse.quote(testo.replace("\\n", "\n"))
                st.markdown(f'<a href="https://wa.me/?text={t_enc}" target="_blank" class="wa-button">📲 Invia su WhatsApp</a>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        sel = st.selectbox("Agente", list(subagenti.keys()))
        amt = st.number_input("Coin", step=10000)
        if st.button("Invia"):
            if st.session_state.stock_centrale >= amt:
                st.session_state.budgets[sel] = st.session_state.budgets.get(sel, 0) + amt
                st.session_state.stock_centrale -= amt
                st.rerun()

    with t3:
        if not df_v.empty:
            st.plotly_chart(px.bar(df_v.groupby('Nome Agente')['Euro'].sum().reset_index(), x='Nome Agente', y='Euro', color='Euro'))

# --- AREA SUBAGENTE ---
else:
    st.title(f"🚀 Dashboard: {st.session_state.users_db[user].get('name', user)}")
    with st.sidebar:
        foto = st.file_uploader("Carica foto", type=['png', 'jpg', 'jpeg'])
        if foto: 
            st.session_state.fotos[user] = Image.open(foto)
            st.success("Foto OK")

    curr_b = st.session_state.budgets.get(user, 0)
    st.metric("Budget", f"{curr_b:,.0f} Coin")
    with st.form("vendita"):
        id_c, eur = st.text_input("ID Cliente"), st.number_input("Euro", min_value=1)
        st.info(f"💡 Erogazione: {eur * COIN_PER_EURO:,.0f} monete")
        if st.form_submit_button("CONFERMA"):
            c_out = eur * COIN_PER_EURO
            if st.session_state.budgets.get(user, 0) >= c_out:
                m = eur * MARGINE_COIN
                st.session_state.db_vendite.append({"Data": datetime.now().strftime("%d/%m %H:%M"), "Agente": user, "Nome Agente": st.session_state.users_db[user].get('name'), "ID Cliente": id_c, "Euro": eur, "Coin": c_out, "m_sub": m/2, "m_agenzia": m/2})
                st.session_state.budgets[user] -= c_out
                st.session_state.guadagni[user] = st.session_state.guadagni.get(user, 0) + (m/2)
                st.rerun()
            else: st.error("Budget finito")

if st.sidebar.button("Logout"): 
    st.session_state.authenticated = False
    st.rerun()
