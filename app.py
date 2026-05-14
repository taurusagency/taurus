import streamlit as st
import pandas as pd
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. DATABASE CONDIVISO ---
@st.cache_resource
def get_shared_db():
    utenti = ["MassimoMaster", "Terry", "Fabio", "Elena", "USA_Agent", "Queen", "Libidus"]
    return pd.DataFrame({
        'Agente': utenti,
        'Coins_Disponibili': [0.0] * len(utenti),
        'Guadagno_Coins': [0.0] * len(utenti),
        'Vendite_Totali_Coins': [0.0] * len(utenti),
        'Euro_Da_Inviare': [0.0] * len(utenti) 
    })

shared_db = get_shared_db()

# --- 2. ACCESSI ---
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

# --- 3. LOGICA DATI E CALCOLO REALE (Corretto: 500 coins = 5,49€) ---
idx_u = shared_db['Agente'] == st.session_state.user
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])

# IL CALCOLO CORRETTO: 
# Se 91 monete vendute = 1 Euro, e l'agente ne prende 5 di margine:
# Il valore in euro del suo guadagno è (Coins / 91)
guadagno_e = guadagno_c / 91

coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

# --- 4. TABELLONE SUPERIORE ---
html_tabellone = f"""
<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; color: white; font-family: sans-serif;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">🏆 IL TUO GUADAGNO MATURATO</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">RISCATTABILI</span></h2>
</div>
"""
st.markdown(html_tabellone, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    foto = st.file_uploader("Carica Foto Profilo", type=['png', 'jpg'])
    if st.button("🔄 Refresh"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 6. PANNELLO MASTER ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    with st.expander("📦 CARICO REALE AGENZIA"):
        carico = st.number_input("Coins acquistati", min_value=0.0, step=10000.0)
        if st.button("Carica Magazzino Master"):
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += carico
            st.rerun()
    
    st.write("### 📊 Riepilogo Agenzia")
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)

# --- 7. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Agente: {st.session_state.user}")
    st.error(f"⚠️ DA INVIARE A MASSIMO: € {euro_debito:.2f}")
    
    id_cli = st.text_input("ID StarMaker Cliente")
    euro_v = st.number_input("Prezzo vendita (€)", min_value=0.0, step=1.0)
    
    if st.button("🚀 ESEGUI VENDITA"):
        costo_c = int(euro_v * 91)
        if coins_disp >= costo_c and id_cli != "":
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= costo_c
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += costo_c
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_v
            st.rerun()
        else: st.error("Dati mancanti o budget insufficiente!")

    # MESSAGGIO WHATSAPP CORRETTO
    msg = f"Ciao Massimo, riscatto guadagno Taurus: {guadagno_c} Coins (Valore: € {guadagno_e:.2f})"
    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text={urllib.parse.quote(msg)}")

# --- 8. GARA ---
st.divider()
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))


