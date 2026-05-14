import streamlit as st
import pandas as pd
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

# --- 3. LOGICA DATI ---
idx_u = shared_db['Agente'] == st.session_state.user
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])
guadagno_e = guadagno_c / 5 
coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

# --- 4. TABELLONE NERO (Grafica Pulita) ---
titolo = "🏆 MIA PROVVIGIONE AGENZIA" if st.session_state.is_master else "🏆 MIO GUADAGNO PERSONALE"

st.markdown(f"""
<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; color: white;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo}</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">GUADAGNATI</span></h2>
</div>
""", unsafe_allow_html=True)

# Barra energia nel tabellone (Usiamo componente nativo per image_18.png)
st.write(f"**🔋 ENERGIA BUDGET DISPONIBILE: {coins_disp} COINS**")
max_v = 1000000 if st.session_state.is_master else 50000
st.progress(min(1.0, coins_disp / max_v))

if not st.session_state.is_master:
    st.markdown(f'<h3 style="color: #FF4B4B; text-align: right;">💰 EURO DA INVIARE: € {euro_debito:.2f}</h3>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.button("🔄 Refresh"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 5. PANNELLO MASTER ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    st.subheader("🔋 Monitoraggio Energia Subagenti")
    cols = st.columns(3)
    subs = shared_db[shared_db['Agente'] != "MassimoMaster"]
    for i, row in enumerate(subs.itertuples()):
        with cols[i % 3]:
            st.write(f"⚡ {row.Agente}: {int(row.Coins_Disponibili)} COINS")
            st.progress(min(1.0, row.Coins_Disponibili / 50000))

    with st.expander("💸 Gestione Depositi (COINS)"):
        target = st.selectbox("Seleziona Conto", shared_db['Agente'])
        quant = st.number_input("Quantità (+/-)", step=100.0)
        if st.button("Conferma"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += quant
            st.rerun()
    
    st.write("### 📊 Riepilogo Debiti")
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)

# --- 6. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Agente: {st.session_state.user}")
    with st.expander("💳 Registra Invio Denaro"):
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
