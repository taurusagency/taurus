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
        'Euro_Da_Inviare': [0.0] * len(utenti) # Cassa contante in mano ai subagenti
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
guadagno_e = guadagno_c / 5 # Provvigione calcolata (5 coins ogni 1€)

titolo_tab = "🏆 MIA PROVVIGIONE AGENZIA" if st.session_state.is_master else "🏆 MIO GUADAGNO PERSONALE"

st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e1e1e 0%, #3a3a3a 100%); padding: 25px; border-radius: 15px; border-right: 15px solid #FF4B4B; text-align: right; margin-bottom: 20px;">
        <p style="color: #FF4B4B; font-size: 18px; font-weight: bold; margin: 0;">{titolo_tab}</p>
        <h1 style="color: white; font-size: 60px; margin: 0;">{int(guadagno_c)} <span style="font-size: 25px;">COINS</span></h1>
        <h2 style="color: #00FF00; font-size: 45px; margin: 0;">€ {guadagno_e:.2f} <span style="font-size: 20px;">MATURATI</span></h2>
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
        target = st.selectbox("Seleziona Conto (incluso MassimoMaster)", shared_db['Agente'])
        quant = st.number_input("Quantità COINS (+ per caricare, - per scaricare)", step=100.0)
        if st.button("Esegui Movimentazione"):
            shared_db.loc[shared_db['Agente'] == target, 'Coins_Disponibili'] += quant
            st.success("Saldo aggiornato!")
            st.rerun()
    
    st.write("### 📊 Tabella Incassi dai Subagenti (Euro da ricevere)")
    # Tabella che mostra quanto ogni agente deve versarti
    st.dataframe(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Euro_Da_Inviare', 'Guadagno_Coins', 'Vendite_Totali_Coins']], use_container_width=True)
    
    if st.button("🗑️ Reset Globale Provvigioni"):
        shared_db['Guadagno_Coins'] = 0.0
        st.rerun()

# --- 5. PANNELLO SUBAGENTE ---
else:
    st.title(f"📱 Console Operativa: {st.session_state.user}")
    
    # BOX DEBITO VERSO AGENZIA
    euro_debito = shared_db.loc[idx_u, 'Euro_Da_Inviare'].values[0]
    st.error(f"⚠️ EURO TOTALI DA INVIARE ALL'AGENZIA (INCASSI CLIENTI): € {euro_debito:.2f}")
    
    with st.expander("💳 Registra Invio Denaro ad Agenzia (Defalca)"):
        invio = st.number_input("Importo versato a Massimo (€)", min_value=0.0, step=1.0)
        if st.button("✅ Conferma Versamento Effettuato"):
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] -= invio
            st.success(f"Hai defalcato € {invio}. Il tuo debito residuo è aggiornato.")
            st.rerun()

    st.divider()
    budget_c = shared_db.loc[idx_u, 'Coins_Disponibili'].values[0]
    st.metric("TUO BUDGET COINS PER VENDITE", f"{int(budget_c)}")
    
    id_sm = st.text_input("ID UTENTE STARMAKER CLIENTE")
    euro_v = st.number_input("EURO INCASSATI DA QUESTA VENDITA (€)", min_value=0.0, step=1.0)
    
    if st.button("🚀 ESEGUI CARICAMENTO MONETE"):
        coins_da_scalare = int(euro_v * 91)
        provvigione_fissa = int(euro_v * 5)
        
        if budget_c >= coins_da_scalare:
            # Scarico monete dal budget agente
            shared_db.loc[idx_u, 'Coins_Disponibili'] -= coins_da_scalare
            # Assegnazione 5 coins all'agente e 5 coins a Massimo
            shared_db.loc[idx_u, 'Guadagno_Coins'] += provvigione_fissa
            shared_db.loc[shared_db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += provvigione_fissa
            # Aggiornamento Gara e Debito Cash
            shared_db.loc[idx_u, 'Vendite_Totali_Coins'] += coins_da_scalare
            shared_db.loc[idx_u, 'Euro_Da_Inviare'] += euro_v
            st.balloons()
            st.rerun()
        else:
            st.error(f"Errore: Budget insufficiente! Servono {coins_da_scalare} monete.")

    msg_wa = f"Ciao Massimo, riscatto la mia provvigione Taurus: {int(guadagno_c)} Coins (€ {guadagno_e:.2f})"
    st.link_button("📩 RISCATTA GUADAGNO (WHATSAPP)", f"https://wa.me/393663749350?text={urllib.parse.quote(msg_wa)}")

# --- 6. GARA ---
st.divider()
st.subheader("🏁 Classifica Gara Taurus Agency")
st.table(shared_db[shared_db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']].sort_values(by='Vendite_Totali_Coins', ascending=False))
