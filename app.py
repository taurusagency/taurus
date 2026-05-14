import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - Team Management", layout="wide")

# --- DATABASE INIZIALE ---
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "TaurusMaster": {"pass": "Taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
    }
    for i in range(1, 13):
        st.session_state.users_db[f"agente{i}"] = {
            "pass": f"pass{i}", "role": "Subagente", "name": f"Agente {i}", 
            "budget": 0, "guadagno_accumulato_coin": 0, "foto": None
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
MIO_WHATSAPP = "+393331234567" # Sostituisci col tuo numero reale

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
        border-top: 5px solid #FFD700; margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. SCHERMATA LOGIN ---
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

user = st.session_state.user_logged
role = st.session_state.user_role

# --- WIDGET GUADAGNO ---
if role == "Agenzia":
    tot_coin = sum([v['m_agenzia'] for v in st.session_state.db_vendite])
    st.markdown(f'<div class="profit-container">GUADAGNO AGENZIA<br><b>{tot_coin:,.0f} COIN</b><br>{tot_coin/101:.2f} €</div>', unsafe_allow_html=True)
else:
    guadagno_agente = st.session_state.users_db[user]["guadagno_accumulato_coin"]
    testo_wa = urllib.parse.quote(f"Ciao TaurusMaster, richiedo il compenso maturato di {guadagno_agente:,.0f} monete.")
    st.markdown(f'<a href="https://wa.me/{MIO_WHATSAPP}?text={testo_wa}" target="_blank" style="text-decoration:none;"><div class="profit-container">RICHIEDI COMPENSO<br><b>{guadagno_agente:,.0f} COIN</b><br>{guadagno_agente/101:.2f} €</div></a>', unsafe_allow_html=True)

# --- 2. DASHBOARD TAURUSMASTER (ADMIN) ---
if role == "Agenzia":
    st.title("🛡️ Pannello TaurusMaster")
    
    col_a, col_b = st.columns(2)
    col_a.metric("Stock Centrale Reale", f"{st.session_state.stock_centrale:,.0f} Coin")
    with col_b:
        with st.expander("Modifica o Carica Stock"):
            nuovo_s = st.number_input("Imposta nuovo totale", value=st.session_state.stock_centrale)
            if st.button("Aggiorna Stock Centrale"):
                st.session_state.stock_centrale = nuovo_s
                st.rerun()

    tab1, tab2, tab3 = st.tabs(["👥 Gestione Team", "💰 Rabbocchi", "📜 Registro"])
    
    with tab1:
        cols = st.columns(3)
        for i, (u_key, data) in enumerate(list(st.session_state.users_db.items())):
            if data['role'] == "Subagente":
                with cols[i % 3]:
                    st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                    # MOSTRA FOTO SE PRESENTE
                    if data['foto'] is not None:
                        st.image(data['foto'], width=100)
                    else:
                        st.write("👤 *Nessuna foto*")
                    
                    st.write(f"### {data['name']}")
                    st.write(f"Budget: **{data['budget']:,.0f}**")
                    
                    with st.expander("Azioni & Credenziali"):
                        if st.button(f"Saldato (Azzera Guadagno)", key=f"pay_{u_key}"):
                            st.session_state.users_db[u_key]["guadagno_accumulato_coin"] = 0
                            st.rerun()
                        new_u = st.text_input("User", value=u_key, key=f"u_{u_key}")
                        new_p = st.text_input("Pass", value=data['pass'], key=f"p_{u_key}")
                        if st.button("Salva", key=f"s_{u_key}"):
                            if new_u != u_key:
                                st.session_state.users_db[new_u] = st.session_state.users_db.pop(u_key)
                            st.session_state.users_db[new_u]["pass"] = new_p
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("Invia monete ai subagenti")
        sub_list = [u for u, d in st.session_state.users_db.items() if d['role'] == "Subagente"]
        sel = st.selectbox("Seleziona Agente", sub_list)
        val = st.number_input("Quantità Coin", step=10000)
        if st.button("Trasferisci"):
            if st.session_state.stock_centrale >= val:
                st.session_state.users_db[sel]["budget"] += val
                st.session_state.stock_centrale -= val
                st.success("Trasferimento completato!")
                st.rerun()

# --- 3. AREA SUBAGENTE (OPERATIVO) ---
else:
    st.title(f"🚀 Area Agente: {st.session_state.users_db[user]['name']}")
    
    with st.sidebar:
        # CARICAMENTO FOTO PROFILO
        st.subheader("Profilo")
        uploaded_file = st.file_uploader("Carica la tua foto", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.session_state.users_db[user]['foto'] = image
            st.image(image, width=150)
            st.success("Foto aggiornata!")

    st.metric("Tuo Budget Disponibile", f"{st.session_state.users_db[user]['budget']:,.0f} Coin")
    
    with st.form("vendita"):
        id_c = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Prezzo (€)", min_value=1)
        
        c_supporto = euro * COIN_PER_EURO
        st.info(f"Erogazione prevista: {c_supporto:,.0f} monete")
        
        if st.form_submit_button("CONFERMA E SCARICA BUDGET"):
            if st.session_state.users_db[user]["budget"] >= c_supporto:
                margine = euro * MARGINE_COIN
                st.session_state.db_vendite.append({
                    "Data": datetime.now().strftime("%d/%m %H:%M"),
                    "Agente": user, "ID Cliente": id_c, "Euro": euro, "Coin": c_supporto,
                    "m_sub": margine/2, "m_agenzia": margine/2
                })
                st.session_state.users_db[user]["budget"] -= c_supporto
                st.session_state.users_db[user]["guadagno_accumulato_coin"] += (margine/2)
                st.rerun()
            else:
                st.error("Budget insufficiente!")

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
