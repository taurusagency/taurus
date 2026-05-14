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

# Inizializzazione per le foto profilo
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

# --- 3. LOGICA COLORI ENERGIA ---
idx_u = shared_db['Agente'] == st.session_state.user
coins_disp = int(shared_db.loc[idx_u, 'Coins_Disponibili'].values[0])
guadagno_c = int(shared_db.loc[idx_u, 'Guadagno_Coins'].values[0])
guadagno_e = guadagno_c / 5 
euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]

def get_color_style(current, is_master=False):
    ref = 1000000 if is_master else 50000
    perc = (current / ref)
    if perc > 0.5: return "#00FF00" # VERDE
    if perc > 0.2: return "#FFFF00" # GIALLO
    return "#FF4B4B" # ROSSO

# --- 4. TABELLONE SUPERIORE (image_21.png) ---
titolo_tab = "🏆 PROVVIGIONE AGENZIA" if st.session_state.is_master else "🏆 GUADAGNO PERSONALE"

html_tabellone = f"""
<div style="background-color: #1e1e1e; padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; color: white; font-family: sans-serif;">
    <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo_tab}</p>
    <h1 style="font-size: 50px; margin: 0;">{guadagno_c} <span style="font-size: 20px;">COINS</span></h1>
    <h2 style="color: #00FF00; font-size: 35px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 18px;">MATURATI</span></h2>
    <div style="margin-top: 15px; text-align: left;">
        <p style="color: #AAA; font-size: 14px; margin: 0;">ENERGIA BUDGET DISPONIBILE: {coins_disp} COINS</p>
        <div style="background-color: #444; border-radius: 10px; width: 100%; height: 15px; margin-top: 5px;">
            <div style="background-color: {get_color_style(coins_disp, st.session_state.is_master)}; width: {min(100, int((coins_disp/(1000000 if st.session_state.is_master else 50000))*100))}% ; height: 15px; border-radius: 10px;"></div>
        </div>
    </div>
"""
if not st.session_state.is_master:
    html_tabellone += f'<h3 style="color: #FF4B4B; margin-top: 15px;">💰 EURO DA INVIARE: € {euro_debito:.2f}</h3>'
html_tabellone += "</div>"

st.markdown(html_tabellone, unsafe_allow_html=True)

# --- 5. SIDEBAR (Foto e Refresh) ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    
    # Caricamento Foto Profilo
    foto = st.file_uploader("Carica la tua Foto Profilo", type=['png', 'jpg', 'jpeg'])
    if foto:
        st.session_state.foto_agenti[st.session_state.user] = foto
    
    if st.session_state.user in st.session_state.foto_agenti:
        st.image(st.session_state.foto_agenti[st.session_state.user], width=150)
        
    if st.button("🔄 Aggiorna Dati (Refresh)"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 6. PANNELLO MASTER ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    
    with st.expander("📦 CARICO REALE MONETE (Acquisto Agenzia)"):
        carico_in = st.number_input("Inserisci Coins acquistati", min_value=0.0, step=10000.0)
        if st.button("Aggiorna Magazzino Principale"):
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += carico_in
            st.rerun()

    st.subheader("🔋 Stato Energie Subagenti")
    cols_en = st.columns(3)
    subs_list = shared_db[shared_db['Agente'] != "MassimoMaster"]
    for i, row in enumerate(subs_list.itertuples()):
        with cols_en[i % 3]:
            c_s = get_color_style(row.Coins_Disponibili)
            p_s = min(100, int((row.Coins_Disponibili / 50000) * 100))
            st.write(f"⚡ {row.Agente}: {int(row.Coins_Disponibili)} COINS")
            st.markdown(f'<div style="background-color:#444;width:100%;height:10px;border-radius:5px;"><div style="background-color:{c_s};width:{p_s}%;height:10px;border-radius:5px;"></div></div>', unsafe_allow_html=True)

    with st.expander("💸 Spostamento Vasi Comunicanti"):
        target_a = st.selectbox("Seleziona Agente", [u for u in UTENTI_PWD.keys() if u != "MassimoMaster"])
        monto_a = st.number_input("Quantità da spostare", min_value=0.0, step=1000.0)
        c_v1, c_v2 = st.columns(2)
        if c_v1.button("⬆️ Carica Agente (Togli a Master)"):
            if shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'].values[0] >= monto_a:
                shared_db.loc[shared_db['Agente'] == target_a, 'Coins_Disponibili'] += monto_a
                shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] -= monto_a
                st.rerun()
            else: st.error("Saldo Master insufficiente!")
        if c_v2.button("⬇️ Scarica Agente (Rendi a Master)"):
            shared_db.loc[shared_db['Agente'] == target_a, 'Coins_Disponibili'] -= monto_a
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Coins_Disponibili'] += monto_a
            st.rerun()

    st.write("### 📊 Riepilogo Agenzia (Debiti e Provvigioni)")
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)

# --- 7. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Agente: {st.session_state.user}")
    
    with st.expander("💳 Registra Invio Denaro ad Agenzia"):
        versato = st.number_input("Importo versato a Massimo (€)", min_value=0.0)
        if st.button("✅ Conferma Invio"):
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] -= versato
            st.rerun()

    st.divider()
    id_sm_cli = st.text_input("ID StarMaker Cliente")
    euro_inc = st.number_input("Euro incassati dal cliente (€)", min_value=0.0, step=1.0)
    
    if st.button("🚀 ESEGUI CARICAMENTO MONETE"):
        costo_c = int(euro_inc * 91)
        if coins_disp >= costo_c:
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= costo_c
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_inc * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_inc * 5)
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += costo_c
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_inc
            st.balloons()
            st.rerun()
        else: st.error("Energia insufficiente!")

    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text=Richiedo riscatto Taurus: {int(guadagno_c)} Coins")

# --- 8. GARA PUBBLICA ---
st.divider()
st.subheader("🏁 Classifica Gara Taurus Agency")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
