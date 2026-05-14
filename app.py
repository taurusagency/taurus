import streamlit as st
import pandas as pd
import urllib.parse
from PIL import Image

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. DATABASE CONDIVISO (Vasi Comunicanti e Memoria) ---
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

# Foto profilo persistenti
if 'foto_agenti' not in st.session_state:
    st.session_state.foto_agenti = {}

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

# --- 3. CALCOLI E LIVELLI (Novità: Gamification) ---
idx_u = shared_db['Agente'] == st.session_state.user
coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])
guadagno_e = guadagno_c / 5 
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

# Sistema Livelli per motivare i subagenti
def get_rank(total_sales):
    if total_sales > 100000: return "💎 ELITE MASTER"
    if total_sales > 50000: return "🥇 TOP AGENT GOLD"
    if total_sales > 10000: return "🥈 SILVER VETERAN"
    return "🥉 AGENTE JUNIOR"

rank = get_rank(shared_db.loc[idx_u, 'Vendite_Totali_Coins'].values[0])

# --- 4. TABELLONE SUPERIORE DESIGN ---
titolo_tab = "🏆 PROVVIGIONE AGENZIA" if st.session_state.is_master else f"🏆 {rank}"

html_tabellone = f"""
<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; color: white; font-family: sans-serif;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo_tab}</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">MATURATI</span></h2>
    <div style="margin-top: 15px; text-align: left;">
        <p style="color: #AAA; font-size: 14px; margin: 0;">ENERGIA BUDGET DISPONIBILE: {coins_disp} COINS</p>
        <div style="background-color: #444; border-radius: 10px; width: 100%; height: 15px; margin-top: 5px;">
            <div style="background-color: {'#00FF00' if coins_disp > 10000 else '#FF4B4B'}; width: {min(100, int((coins_disp/1000000 if st.session_state.is_master else coins_disp/50000)*100))}% ; height: 15px; border-radius: 10px;"></div>
        </div>
    </div>
</div>
"""
st.markdown(html_tabellone, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    foto = st.file_uploader("Foto Profilo", type=['png', 'jpg'])
    if foto: st.session_state.foto_agenti[st.session_state.user] = foto
    if st.session_state.user in st.session_state.foto_agenti:
        st.image(st.session_state.foto_agenti[st.session_state.user], width=100)
    if st.button("🔄 Refresh"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 6. PANNELLO MASTER (MASSIMO) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    with st.expander("📦 CARICO REALE AGENZIA"):
        carico = st.number_input("Acquisto monete", min_value=0.0, step=10000.0)
        if st.button("Carica Magazzino"):
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += carico
            st.rerun()
    
    # Monitoraggio Energie (image_23.png)
    st.subheader("🔋 Stato Energie Subagenti")
    c_en = st.columns(3)
    for i, row in enumerate(shared_db[shared_db['Agente'] != "MassimoMaster"].itertuples()):
        with c_en[i % 3]:
            st.write(f"⚡ {row.Agente}: {int(row.Coins_Disponibili)} COINS")
            st.progress(min(1.0, row.Coins_Disponibili / 50000))

    with st.expander("💸 Spostamento Vasi Comunicanti"):
        target = st.selectbox("Agente", [u for u in UTENTI_PWD.keys() if u != "MassimoMaster"])
        monto = st.number_input("Quantità", min_value=0.0, step=1000.0)
        b1, b2 = st.columns(2)
        if b1.button("⬆️ Carica Agente"):
            if shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'].values[0] >= monto:
                shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += monto
                shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] -= monto
                st.rerun()
        if b2.button("⬇️ Scarica Agente"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] -= monto
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += monto
            st.rerun()

# --- 7. PANNELLO SUBAGENTE (Novità: Tasti Rapidi) ---
else:
    st.title(f"📱 Console Agente: {st.session_state.user}")
    
    st.markdown(f"### ⚠️ Da inviare all'Agenzia: **€ {euro_debito:.2f}**")
    
    st.divider()
    id_cli = st.text_input("ID StarMaker Cliente")
    
    # Integrazione Tasti Rapidi per velocizzare
    st.write("⚡ Vendita Rapida:")
    c1, c2, c3 = st.columns(3)
    euro_val = 0.0
    if c1.button("€ 10"): euro_val = 10.0
    if c2.button("€ 20"): euro_val = 20.0
    if c3.button("€ 50"): euro_val = 50.0
    
    euro_input = st.number_input("Oppure inserisci Euro manuali", value=euro_val, step=1.0)
    
    if st.button("🚀 ESEGUI VENDITA"):
        costo_coins = int(euro_input * 91)
        if coins_disp >= costo_coins and id_cli != "":
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= costo_coins
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_input * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_input * 5)
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += costo_coins
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_input
            st.balloons()
            st.rerun()
        else: st.error("Errore: Budget insufficiente o ID mancante!")

    # Riscatto Doppia Valuta (Novità richiesta)
    msg = f"Ciao Massimo, riscatto guadagno Taurus: {guadagno_c} Coins (Valore: € {guadagno_e:.2f})"
    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text={urllib.parse.quote(msg)}")

# --- 8. GARA PUBBLICA (image_22.png) ---
st.divider()
st.subheader("🏁 Classifica Gara Taurus Agency")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
