import streamlit as st
import pandas as pd
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. DATABASE CONDIVISO ---
@st.cache_resource
def get_shared_db():
    utenti = ["MassimoMaster", "Terry", "Fabio", "Elena", "USA_Agent", "Queen", "Libidus"]
    return pd.DataFrame({
        'Agente': utenti,
        'Coins_Disponibili': [0.0] * len(utenti), # Parte da zero per il carico reale
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

# --- 3. LOGICA COLORI ENERGIA ---
idx_u = shared_db['Agente'] == st.session_state.user
coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])
guadagno_e = guadagno_c / 5 
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

def get_color(current, is_master=False):
    ref = 1000000 if is_master else 50000
    perc = (current / ref)
    if perc > 0.5: return "#00FF00" # VERDE
    if perc > 0.2: return "#FFFF00" # GIALLO
    return "#FF4B4B" # ROSSO

# --- 4. TABELLONE SUPERIORE ---
titolo = "🏆 PROVVIGIONE AGENZIA" if st.session_state.is_master else "🏆 GUADAGNO MATURATO"

st.markdown(f"""
<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; color: white;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo}</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">EFFETTIVI</span></h2>
</div>
""", unsafe_allow_html=True)

# BARRA ENERGIA DINAMICA
c_main = get_color(coins_disp, st.session_state.is_master)
p_main = min(100, int((coins_disp / (1000000 if st.session_state.is_master else 50000)) * 100))

st.write(f"**🔋 ENERGIA DISPONIBILE: {coins_disp} COINS**")
st.markdown(f"""
    <div style="background-color: #444; border-radius: 10px; width: 100%; height: 15px;">
        <div style="background-color: {c_main}; width: {p_main}%; height: 15px; border-radius: 10px;"></div>
    </div>
""", unsafe_allow_html=True)

if not st.session_state.is_master:
    st.markdown(f'<h3 style="color: #FF4B4B; text-align: right;">💰 EURO DA INVIARE: € {euro_debito:.2f}</h3>', unsafe_allow_html=True)

# --- 5. PANNELLO MASTER ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    with st.expander("📦 CARICO REALE MONETE (Acquisto Agenzia)"):
        nuovo_carico = st.number_input("Inserisci Coins acquistati", min_value=0.0, step=10000.0)
        if st.button("Aggiorna Magazzino Principale"):
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += nuovo_carico
            st.rerun()

    st.subheader("🔋 Stato Energie Subagenti")
    cols = st.columns(3)
    subs = shared_db[shared_db['Agente'] != "MassimoMaster"]
    for i, row in enumerate(subs.itertuples()):
        with cols[i % 3]:
            col_s = get_color(row.Coins_Disponibili)
            per_s = min(100, int((row.Coins_Disponibili / 50000) * 100))
            st.write(f"⚡ {row.Agente}: {int(row.Coins_Disponibili)} COINS")
            st.markdown(f'<div style="background-color:#444;width:100%;height:8px;"><div style="background-color:{col_s};width:{per_s}%;height:8px;"></div></div>', unsafe_allow_html=True)

    with st.expander("💸 Spostamento Vasi Comunicanti"):
        target = st.selectbox("Agente", [u for u in UTENTI_PWD.keys() if u != "MassimoMaster"])
        monto = st.number_input("Quantità", min_value=0.0, step=1000.0)
        c1, c2 = st.columns(2)
        if c1.button("⬆️ Carica Agente"):
            if shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'].values[0] >= monto:
                shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += monto
                shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] -= monto
                st.rerun()
        if c2.button("⬇️ Scarica Agente"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] -= monto
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += monto
            st.rerun()

# --- 6. PANNELLO AGENTE ---
else:
    st.title(f"📱 Console: {st.session_state.user}")
    id_sm = st.text_input("ID StarMaker")
    euro_v = st.number_input("Euro Incassati", min_value=0.0)
    if st.button("🚀 Carica"):
        costo = int(euro_v * 91)
        if coins_disp >= costo:
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= costo
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_v
            st.rerun()

st.sidebar.button("🔄 Refresh", on_click=lambda: st.rerun())
