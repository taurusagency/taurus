import streamlit as st
import pandas as pd
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. DATABASE CONDIVISO (Vasi Comunicanti) ---
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

if 'foto_agenti' not in st.session_state:
    st.session_state.foto_agenti = {}

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

# --- 3. LOGICA DATI E COLORI ---
idx_u = shared_db['Agente'] == st.session_state.user
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])
# Calcolo esatto: 500 coins = 5,49€ (basato su 91 coins/euro)
guadagno_e = guadagno_c / 91 
coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

def get_energy_style(current, is_master=False):
    ref = 1000000 if is_master else 50000
    perc = (current / ref)
    if perc > 0.5: return "#00FF00", min(100, int(perc * 100)) # Verde
    if perc > 0.2: return "#FFFF00", min(100, int(perc * 100)) # Giallo
    return "#FF4B4B", min(100, int(perc * 100)) # Rosso

# --- 4. TABELLONE SUPERIORE GRAFICO ---
titolo_tab = "🏆 PROVVIGIONE AGENZIA" if st.session_state.is_master else "🏆 IL TUO GUADAGNO MATURATO"
color_bar, perc_bar = get_energy_style(coins_disp, st.session_state.is_master)

st.markdown(f"""
<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; color: white; font-family: sans-serif;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo_tab}</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">RISCATTABILI</span></h2>
    <div style="margin-top: 15px; text-align: left;">
        <p style="color: #AAA; font-size: 14px; margin: 0;">ENERGIA BUDGET DISPONIBILE: {coins_disp} COINS</p>
        <div style="background-color: #444; border-radius: 10px; width: 100%; height: 15px; margin-top: 5px;">
            <div style="background-color: {color_bar}; width: {perc_bar}%; height: 15px; border-radius: 10px; transition: width 0.5s;"></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    foto = st.file_uploader("Carica Foto Profilo", type=['png', 'jpg'])
    if foto: st.session_state.foto_agenti[st.session_state.user] = foto
    if st.session_state.user in st.session_state.foto_agenti:
        st.image(st.session_state.foto_agenti[st.session_state.user], width=100)
    if st.button("🔄 Refresh"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth, st.session_state.user = False, None
        st.rerun()

# --- 6. PANNELLO MASTER ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    with st.expander("📦 CARICO REALE AGENZIA (Acquisto Monete)"):
        carico = st.number_input("Coins acquistati da StarMaker", min_value=0.0, step=10000.0)
        if st.button("Aggiorna Magazzino Master"):
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += carico
            st.rerun()

    st.subheader("🔋 Stato Energie Subagenti")
    cols_en = st.columns(3)
    subs_df = shared_db[shared_db['Agente'] != "MassimoMaster"]
    for i, row in enumerate(subs_df.itertuples()):
        with cols_en[i % 3]:
            c_s, p_s = get_energy_style(row.Coins_Disponibili)
            st.write(f"⚡ {row.Agente}: {int(row.Coins_Disponibili)} COINS")
            st.markdown(f'<div style="background-color:#444;width:100%;height:10px;border-radius:5px;overflow:hidden;"><div style="background-color:{c_s};width:{p_s}%;height:10px;"></div></div>', unsafe_allow_html=True)

    with st.expander("💸 Spostamento Budget (Vasi Comunicanti)"):
        target = st.selectbox("Seleziona Agente", [u for u in UTENTI_PWD.keys() if u != "MassimoMaster"])
        monto = st.number_input("Quantità Coins", min_value=0.0, step=1000.0)
        c1, c2 = st.columns(2)
        if c1.button("⬆️ Invia ad Agente"):
            if shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'].values[0] >= monto:
                shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += monto
                shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] -= monto
                st.rerun()
            else: st.error("Saldo Master insufficiente!")
        if c2.button("⬇️ Recupera da Agente"):
            if shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'].values[0] >= monto:
                shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] -= monto
                shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += monto
                st.rerun()

    st.write("### 📊 Riepilogo Agenzia")
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)

# --- 7. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Agente: {st.session_state.user}")
    st.error(f"⚠️ DA INVIARE A MASSIMO: € {euro_debito:.2f}")
    
    with st.expander("💳 Registra Versamento ad Agenzia"):
        vers = st.number_input("Euro inviati (€)", min_value=0.0)
        if st.button("Conferma"):
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] -= vers
            st.rerun()

    st.divider()
    id_cli = st.text_input("ID StarMaker Cliente")
    euro_v = st.number_input("Euro incassati (€)", min_value=0.0, step=1.0)
    
    if st.button("🚀 ESEGUI VENDITA"):
        costo_c = int(euro_v * 91)
        if coins_disp >= costo_c and id_cli != "":
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= costo_c
            # Provvigione 5 coins all'agente e 5 all'agenzia per ogni euro
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += costo_c
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_v
            st.balloons()
            st.rerun()
        else: st.error("Budget insufficiente o ID mancante!")

    msg = f"Ciao Massimo, riscatto guadagno Taurus: {guadagno_c} Coins (Valore: € {guadagno_e:.2f})"
    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text={urllib.parse.quote(msg)}")

# --- 8. GARA ---
st.divider()
st.subheader("🏁 Classifica Gara Taurus Agency")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
