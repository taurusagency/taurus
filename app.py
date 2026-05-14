import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. MEMORIA CONDIVISA (Database Centralizzato) ---
@st.cache_resource
def get_shared_db():
    utenti = ["MassimoMaster", "Terry", "Fabio", "Elena", "USA_Agent", "Queen"]
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
    "Terry": "Taurus01", "Fabio": "Taurus02", "Elena": "Taurus03", "USA_Agent": "Taurus04", "Queen": "Taurus05"
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

# --- 3. TABELLONE RISULTATI (Grafica differenziata) ---
idx_u = shared_db['Agente'] == st.session_state.user
guadagno_c = shared_db.loc[idx_u, 'Guadagno_Coins'].values[0]
guadagno_e = guadagno_c / 5 

# Recupero Coins Disponibili per visualizzazione in alto
coins_disp = shared_db.loc[idx_u, 'Coins_Disponibili'].values[0]

if st.session_state.is_master:
    titolo_tab = "🏆 MIA PROVVIGIONE AGENZIA"
    colore_testo = "#00FF00"
else:
    titolo_tab = "🏆 MIO GUADAGNO PERSONALE"
    colore_testo = "#00FF00"

st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e1e1e 0%, #3a3a3a 100%); padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; margin-bottom: 20px;">
        <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo_tab}</p>
        <h1 style="color: white; font-size: 50px; margin: 0;">{int(guadagno_c)} <span style="font-size: 20px;">COINS</span></h1>
        <h2 style="color: {colore_testo}; font-size: 40px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 20px;">MATURATI</span></h2>
        <hr style="border: 0.5px solid #444;">
        <p style="color: #AAA; font-size: 16px; margin: 0;">SALDO DISPONIBILE ATTUALE:</p>
        <h3 style="color: #FF4B4B; font-size: 30px; margin: 0;">{int(coins_disp)} COINS</h3>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.button("🔄 Aggiorna Dati (Refresh)"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 4. PANNELLO MASTER (MASSIMO) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    with st.expander("💸 Gestione Depositi e Rabbocchi (COINS)"):
        target = st.selectbox("Seleziona Conto", shared_db['Agente'])
        quant = st.number_input("Quantità COINS (+ per caricare, - per scaricare)", step=100.0)
        if st.button("Esegui Movimentazione"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += quant
            st.success("Operazione eseguita!")
            st.rerun()
    
    st.write("### 📊 Riepilogo Agenzia (Situazione Debiti)")
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)
    
    if st.button("🗑️ Reset Globale Provvigioni"):
        shared_db['Guadagno_Coins'] = 0.0
        st.rerun()

# --- 5. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Operativa: {st.session_state.user}")
    
    euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]
    st.error(f"⚠️ EURO DA INVIARE ALL'AGENZIA (INCASSI): € {euro_debito:.2f}")
    
    with st.expander("💳 Registra Invio Denaro"):
        invio = st.number_input("Importo versato (€)", min_value=0.0, step=1.0)
        if st.button("✅ Conferma"):
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] -= invio
            st.rerun()

    st.divider()
    id_sm = st.text_input("ID UTENTE STARMAKER")
    euro_v = st.number_input("EURO INCASSATI (€)", min_value=0.0, step=1.0)
    
    if st.button("🚀 CARICA MONETE"):
        coins_da_scalare = int(euro_v * 91)
        provvigione = int(euro_v * 5)
        
        if coins_disp >= coins_da_scalare:
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= coins_da_scalare
            shared_db.loc[idx_u, 'Guadagno_Coins'] += provvigione
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += provvigione
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += coins_da_scalare
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_v
            st.balloons()
            st.rerun()
        else:
            st.error("Budget insufficiente!")

    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text=Richiedo riscatto provvigione: {int(guadagno_c)} Coins")

# --- 6. GARA ---
st.divider()
st.subheader("🏁 Classifica Gara Taurus Agency")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
