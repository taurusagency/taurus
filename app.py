import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. MEMORIA CONDIVISA (SINCRONIZZAZIONE REAL-TIME) ---
@st.cache_resource
def get_shared_db():
    utenti = ["MassimoMaster", "Terry", "Fabio", "Elena", "USA_Agent", "Queen"]
    return pd.DataFrame({
        'Agente': utenti,
        'Coins_Disponibili': [1000000.0 if u == "MassimoMaster" else 0.0 for u in utenti],
        'Guadagno_Coins': [0.0] * len(utenti),
        'Vendite_Totali_Coins': [0.0] * len(utenti)
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

# --- 3. GRAFICA "RISULTATO LAVORO" (Tabellone in alto a destra) ---
idx_u = shared_db['Agente'] == st.session_state.user
guadagno_c = shared_db.loc[idx_u, 'Guadagno_Coins'].values[0]
# Formula: 5 monete = 0.50€ (metà del margine di 1 euro)
guadagno_e = (guadagno_c / 5) * 0.5 

# Creazione di un'area evidenziata con CSS personalizzato
st.markdown(f"""
    <div style="
        background: linear-gradient(90deg, #1e1e1e 0%, #3a3a3a 100%);
        padding: 25px;
        border-radius: 15px;
        border-right: 15px solid #FF4B4B;
        text-align: right;
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    ">
        <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0; text-transform: uppercase;">🏆 Risultato del tuo Lavoro</p>
        <h1 style="color: white; font-size: 55px; margin: 0; line-height: 1.1;">{int(guadagno_c)} <span style="font-size: 25px;">COINS</span></h1>
        <h2 style="color: #00FF00; font-size: 40px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 20px;">MATURATI</span></h2>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.button("🔄 Aggiorna Dati"): st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 4. PANNELLO MASTER (MASSIMO) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Master Control")
    with st.expander("💸 Gestione Vasi Comunicanti (COINS)"):
        target = st.selectbox("Seleziona Agente", shared_db['Agente'])
        quant = st.number_input("Quantità COINS (+ aggiungi, - togli)", step=100.0)
        if st.button("Conferma Spostamento"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += quant
            st.success(f"Budget COINS di {target} aggiornato!")
            st.rerun()
    
    st.write("### Riepilogo Agenzia")
    st.dataframe(shared_db, use_container_width=True)
    if st.button("🗑️ Reset Provvigioni"):
        shared_db['Guadagno_Coins'] = 0.0
        st.rerun()

# --- 5. PANNELLO SUBAGENTE ---
else:
    st.title("🛒 Caricamento Monete StarMaker")
    budget_c = shared_db.loc[idx_u, 'Coins_Disponibili'].values[0]
    st.metric("BUDGET DISPONIBILE PER VENDITE", f"{int(budget_c)} COINS")
    
    st.divider()
    id_sm = st.text_input("ID UTENTE STARMAKER")
    euro_v = st.number_input("EURO INCASSATI DAL CLIENTE (€)", min_value=0.0, step=1.0)
    
    if st.button("🚀 CONFERMA E CARICA MONETE"):
        c_erogate = int(euro_v * 91)
        if budget_c >= c_erogate:
            # Sottrazione budget
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= c_erogate
            # 5 coins subagente e 5 coins Massimo
            shared_db.loc[idx_u, 'Guadagno_Coins'] += (euro_v * 5)
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += (euro_v * 5)
            # Gara
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += c_erogate
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ Budget insufficiente! Mancano {int(c_erogate - budget_c)} COINS.")

    # WhatsApp
    msg_wa = f"Ciao Massimo, riscatto il mio guadagno Taurus: {int(guadagno_c)} Coins (€ {guadagno_e:.2f})"
    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text={urllib.parse.quote(msg_wa)}")

# --- 6. GARA PUBBLICA ---
st.divider()
st.subheader("🏁 Classifica Subagenti (Gara in COINS)")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
