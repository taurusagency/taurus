import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. ACCESSI (Senza Email - Solo Username) ---
UTENTI = {
    "MassimoMaster": "Taurus2026",
    "Terry": "Taurus01", 
    "Fabio": "Taurus02",
    "Elena": "Taurus03",
    "USA_Agent": "Taurus04",
    "Queen": "Taurus05"
}

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🐂 Taurus Agency - Login")
    user_in = st.text_input("Username").strip()
    pwd_in = st.text_input("Password", type="password")
    
    if st.button("Accedi"):
        if user_in in UTENTI and UTENTI[user_in] == pwd_in:
            st.session_state.auth = True
            st.session_state.user = user_in
            st.session_state.is_master = (user_in == "MassimoMaster")
            st.rerun()
        else:
            st.error("Credenziali Errate. Verifica maiuscole e minuscole.")
    st.stop()

# --- 2. DATABASE VASI COMUNICANTI (In tempo reale) ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        'Agente': list(UTENTI.keys()),
        'Coins_Disponibili': [1000000.0 if u == "MassimoMaster" else 0.0 for u in UTENTI.keys()],
        'Guadagno_Coins': [0.0] * len(UTENTI),
        'Vendite_Totali_Coins': [0.0] * len(UTENTI)
    })
    st.session_state.id_privati = [] 
    st.session_state.foto_profili = {}

# --- 3. RISULTATO LAVORO (In alto a destra) ---
idx_u = st.session_state.db['Agente'] == st.session_state.user
guadagno_c = st.session_state.db.loc[idx_u, 'Guadagno_Coins'].values[0]
guadagno_e = (guadagno_c / 5) * 0.5 # Ogni 5 coins guadagnati = 0.50€

st.markdown(f"""
    <div style="text-align: right; background-color: #1E1E1E; color: white; padding: 15px; border-radius: 10px; border-right: 8px solid #FF4B4B;">
        <h2 style="margin: 0;">💰 Risultato: {guadagno_c} Coins</h2>
        <p style="margin: 0; color: #00FF00; font-size: 20px;">Valore: € {guadagno_e:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar e Refresh
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.session_state.user in st.session_state.foto_profili:
        st.image(st.session_state.foto_profili[st.session_state.user], width=120)
    st.file_uploader("Carica Foto Profilo", type=['jpg', 'png'], key="up_f")
    if st.button("🔄 Refresh"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 4. PANNELLO MASTER (MASSIMO) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    with st.expander("💸 Gestione Budget (Vasi Comunicanti)"):
        target = st.selectbox("Seleziona Agente", st.session_state.db['Agente'])
        quant = st.number_input("Quantità (+ aggiungi, - togli)", step=100.0)
        if st.button("Aggiorna"):
            st.session_state.db.loc[st.session_state.db['Agente'] == target, 'Coins_Disponibili'] += quant
            st.success("Budget aggiornato")

    st.subheader("🕵️ Registro Privato ID StarMaker")
    st.dataframe(pd.DataFrame(st.session_state.id_privati), use_container_width=True)
    
    if st.button("🗑️ Reset Provvigioni"):
        st.session_state.db['Guadagno_Coins'] = 0.0
        st.warning("Tutti i guadagni sono stati resettati.")

# --- 5. PANNELLO SUBAGENTE ---
else:
    st.title("🛒 Registrazione Vendita StarMaker")
    budget_a = st.session_state.db.loc[idx_u, 'Coins_Disponibili'].values[0]
    st.metric("Tuo Budget Disponibile", f"{budget_a} Coins")
    
    id_sm = st.text_input("ID Utente StarMaker")
    euro_v = st.number_input("Euro incassati (€)", min_value=0.0, step=10.0)
    
    if st.button("🚀 Conferma Vendita"):
        c_erogate = int(euro_v * 91) # 1€ = 91 monete per il cliente
        m_agente = int(euro_v * 5)   # 5 monete al subagente
        m_master = int(euro_v * 5)   # 5 monete a Massimo
        
        if budget_a >= c_erogate:
            st.session_state.db.loc[idx_u, 'Coins_Disponibili'] -= c_erogate
            st.session_state.db.loc[idx_u, 'Guadagno_Coins'] += m_agente
            st.session_state.db.loc[idx_u, 'Vendite_Totali_Coins'] += c_erogate
            st.session_state.db.loc[st.session_state.db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += m_master
            st.session_state.id_privati.append({"Agente": st.session_state.user, "ID": id_sm, "Coins": c_erogate})
            st.balloons()
            st.rerun()
        else:
            st.error("Budget insufficiente!")

    # Tasto WhatsApp
    msg_wa = f"Ciao Massimo, riscatto: {guadagno_c} Coins (€ {guadagno_e:.2f})"
    st.link_button("📩 Riscatta Guadagno (WhatsApp)", f"https://wa.me/393663749350?text={urllib.parse.quote(msg_wa)}")

# --- 6. GARA PUBBLICA ---
st.divider()
st.subheader("🏁 Gara Subagenti Taurus")
st.table(st.session_state.db[st.session_state.db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
