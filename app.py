import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. MEMORIA CONDIVISA ---
@st.cache_resource
def get_shared_db():
    utenti = ["MassimoMaster", "Terry", "Fabio", "Elena", "USA_Agent", "Queen", "Libidus"]
    return pd.DataFrame({
        'Agente': utenti,
        'Coins_Disponibili': [1000000.0 if u == "MassimoMaster" else 0.0 for u in utenti],
        'Guadagno_Coins': [0.0] * len(utenti),
        'Vendite_Totali_Coins': [0.0] * len(utenti),
        'Euro_Da_Inviare': [0.0] * len(utenti) 
    })

shared_db = get_shared_db()

# --- 2. GESTIONE ACCESSI ---
UTENTI_PWD = {
    "MassimoMaster": "Taurus2026",
    "Terry": "Taurus01", "Fabio": "Taurus02", "Elena": "Taurus03", 
    "USA_Agent": "Taurus04", "Queen": "Taurus05", "Libidus": "Taurus06"
}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🐂 Taurus Agency - Login")
    user_in = st.text_input("Username").strip()
    pwd_in = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if user_in in UTENTI_PWD and UTENTI_PWD[user_in] == pwd_in:
            st.session_state.auth, st.session_state.user = True, user_in
            st.session_state.is_master = (user_in == "MassimoMaster")
            st.rerun()
        else: st.error("Credenziali Errate.")
    st.stop()

# --- 3. FUNZIONE GENERATRICE BARRA ENERGIA (HTML) ---
def build_energy_bar(label, current_coins, max_ref=50000):
    if label == "MassimoMaster": max_ref = 1000000
    perc = min(100, int((current_coins / max_ref) * 100))
    color = "#00FF00" if perc > 20 else "#FF4B4B"
    return f"""
    <div style="margin-bottom: 10px;">
        <p style="color: #AAA; font-size: 12px; margin: 0;">{label.upper()}: {int(current_coins)} COINS</p>
        <div style="background-color: #444; border-radius: 5px; height: 8px; width: 100%; overflow: hidden;">
            <div style="background-color: {color}; height: 8px; width: {perc}%; transition: width 0.5s;"></div>
        </div>
    </div>
    """

# --- 4. TABELLONE RISULTATI PRINCIPALE ---
idx_u = shared_db['Agente'] == st.session_state.user
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])
guadagno_e = guadagno_c / 5 
coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

titolo = "🏆 MIA PROVVIGIONE AGENZIA" if st.session_state.is_master else "🏆 MIO GUADAGNO PERSONALE"

html_main = f"""
<div style="background: linear-gradient(90deg, #1e1e1e 0%, #3a3a3a 100%); padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; margin-bottom: 20px; color: white;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo}</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">GUADAGNATI</span></h2>
    <div style="margin-top: 15px;">
        {build_energy_bar("Energia Disponibile", coins_disp)}
    </div>
"""
if not st.session_state.is_master:
    html_main += f'<h3 style="color: #FF4B4B; margin-top: 15px;">💰 EURO DA INVIARE: € {euro_debito:.2f}</h3>'
html_main += "</div>"

st.markdown(html_main, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.button("🔄 Refresh"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 5. PANNELLO MASTER (Monitoraggio Subagenti) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    # NUOVA SEZIONE: Monitoraggio Energia di tutti i subagenti
    with st.container():
        st.subheader("🔋 Monitoraggio Energia Subagenti")
        cols = st.columns(3)
        sub_list = shared_db[shared_db['Agente'] != "MassimoMaster"]
        for i, row in enumerate(sub_list.itertuples()):
            with cols[i % 3]:
                st.markdown(build_energy_bar(row.Agente, row.Coins_Disponibili), unsafe_allow_html=True)

    with st.expander("💸 Gestione Depositi e Rabbocchi (COINS)"):
        target = st.selectbox("Seleziona Conto", shared_db['Agente'])
        quant = st.number_input("Quantità COINS (+/- ricarica)", step=100.0)
        if st.button("Esegui"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += quant
            st.rerun()

    st.write("### 📊 Riepilogo Debiti")
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)

# --- 6. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Agente: {st.session_state.user}")
    with st.expander("💳 Registra Invio Denaro a Massimo"):
        invio = st.number_input("Importo versato (€)", min_value=0.0)
        if st.button("✅ Conferma"):
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] -= invio
            st.rerun()
    
    st.divider()
    id_sm = st.text_input("ID STARMAKER")
    euro_v = st.number_input("EURO INCASSATI (€)", min_value=0.0)
    if st.button("🚀 CARICA MONETE"):
        c_scalare = int(euro_v * 91)
        if coins_disp >= c_scalare:
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= c_scalare
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += c_scalare
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_v
            st.balloons()
            st.rerun()
        else: st.error("Energia insufficiente!")

# --- 7. GARA ---
st.divider()
st.subheader("🏁 Classifica Gara Taurus")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
