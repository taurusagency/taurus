import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import urllib.parse

# --- CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="Taurus Agency - Top 1 StarMaker", layout="wide")

# --- 1. GESTIONE ACCESSI SEMPLIFICATA ---
# Ho sostituito Giuseppe con Terry come richiesto
UTENTI = {
    "MassimoMaster": "Taurus2026",
    "Terry": "Taurus01", # Terry ora prende il posto di Giuseppe
    "Fabio": "Taurus02",
    "Elena": "Taurus03",
    "USA_Agent": "Taurus04",
    "Queen": "Taurus05"
}

if "auth" not in st.session_state:
    st.session_state.auth = False

# Schermata di Login
if not st.session_state.auth:
    st.title("🐂 Taurus Agency - Accesso Collaboratori")
    st.write("Benvenuto nell'Agenzia Top 1 nella vendita di monete StarMaker.")
    
    user_in = st.text_input("Username")
    pwd_in = st.text_input("Password", type="password")
    
    if st.button("Accedi"):
        if user_in in UTENTI and UTENTI[user_in] == pwd_in:
            st.session_state.auth = True
            st.session_state.user = user_in
            st.session_state.is_master = (user_in == "MassimoMaster")
            st.rerun()
        else:
            st.error("Username o Password errati. Riprova.")
    st.stop()

# --- 2. DATABASE IN TEMPO REALE ---
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame({
        'Agente': list(UTENTI.keys()),
        'Coins_Disponibili': [1000000.0 if u == "MassimoMaster" else 0.0 for u in UTENTI.keys()],
        'Guadagno_Coins': [0.0] * len(UTENTI),
        'Vendite_Totali_Coins': [0.0] * len(UTENTI)
    })
    st.session_state.id_privati = [] 
    st.session_state.foto_profili = {}

# --- 3. BARRA LATERALE (Sidebar) ---
with st.sidebar:
    st.header(f"👤 {st.session_state.user}")
    if st.session_state.user in st.session_state.foto_profili:
        st.image(st.session_state.foto_profili[st.session_state.user], width=100)
    
    up_foto = st.file_uploader("Carica/Cambia la tua foto", type=['jpg', 'png'])
    if up_foto:
        st.session_state.foto_profili[st.session_state.user] = Image.open(up_foto)
    
    st.divider()
    if st.button("🔄 Refresh Dati"):
        st.rerun()
    if st.button("🚪 Esci"):
        st.session_state.auth = False
        st.rerun()

# --- 4. AREA RISULTATO LAVORO (In alto a destra) ---
idx_u = st.session_state.db['Agente'] == st.session_state.user
guadagno_c = st.session_state.db.loc[idx_u, 'Guadagno_Coins'].values[0]
guadagno_e = (guadagno_c / 5) * 0.5 # Margine di 0.50€ ogni 5 coins guadagnate

st.markdown(f"""
    <div style="text-align: right; background-color: #f0f2f6; padding: 10px; border-radius: 10px; border-left: 5px solid #ff4b4b;">
        <h3 style="margin: 0;">💰 Mio Guadagno: {guadagno_c} Coins</h3>
        <p style="margin: 0; color: green; font-weight: bold; font-size: 18px;">€ {guadagno_e:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

# Tasto Riscatto WhatsApp
if not st.session_state.is_master:
    msg_wa = f"Ciao Massimo, richiedo riscatto provvigione Taurus per {st.session_state.user}: {guadagno_c} Coins (€ {guadagno_e:.2f})"
    url_wa = f"https://wa.me/393663749350?text={urllib.parse.quote(msg_wa)}"
    st.link_button("📩 Richiedi Pagamento (WhatsApp)", url_wa)

# --- 5. PANNELLO MASTER (MASSIMO) ---
if st.session_state.is_master:
    st.title("🚀 Taurus Control Center - Massimo Master")
    
    # Gestione Budget
    with st.expander("💸 Gestione Vasi Comunicanti (Sposta Monete)"):
        col_m1, col_m2 = st.columns(2)
        target = col_m1.selectbox("Seleziona Agente", st.session_state.db['Agente'])
        quantita = col_m2.number_input("Somma Monete (+ aggiungi, - togli)", step=100.0)
        if st.button("Aggiorna Budget Agente"):
            st.session_state.db.loc[st.session_state.db['Agente'] == target, 'Coins_Disponibili'] += quantita
            st.success(f"Budget di {target} aggiornato correttamente.")

    # Reset Guadagni
    with st.expander("♻️ Reset Provvigioni"):
        target_r = st.selectbox("Seleziona Agente da pagare", st.session_state.db['Agente'][1:])
        if st.button("Resetta Guadagno a Zero"):
            st.session_state.db.loc[st.session_state.db['Agente'] == target_r, 'Guadagno_Coins'] = 0.0
            st.warning(f"Il contatore di {target_r} è stato azzerato.")

    # Registro Privato ID
    st.subheader("🕵️ Registro ID StarMaker (Privato)")
    st.dataframe(pd.DataFrame(st.session_state.id_privati), use_container_width=True)

# --- 6. PANNELLO SUBAGENTE ---
else:
    st.title("🛒 Caricamento Monete")
    
    st.metric("Il tuo Budget Disponibile", f"{st.session_state.db.loc[idx_u, 'Coins_Disponibili'].values[0]} Coins")
    
    st.divider()
    id_sm = st.text_input("Inserisci ID StarMaker del cliente")
    euro_v = st.number_input("Euro incassati (€)", min_value=0.0, step=10.0)
    
    if st.button("🚀 Conferma e Carica"):
        c_erogate = int(euro_v * 91)
        m_agente = int(euro_v * 5)
        m_master = int(euro_v * 5)
        
        budget_attuale = st.session_state.db.loc[idx_u, 'Coins_Disponibili'].values[0]
        
        if budget_attuale >= c_erogate:
            st.session_state.db.loc[idx_u, 'Coins_Disponibili'] -= c_erogate
            st.session_state.db.loc[idx_u, 'Guadagno_Coins'] += m_agente
            st.session_state.db.loc[idx_u, 'Vendite_Totali_Coins'] += c_erogate
            st.session_state.db.loc[st.session_state.db['Agente'] == "MassimoMaster", 'Guadagno_Coins'] += m_master
            
            st.session_state.id_privati.append({
                "Data": pd.Timestamp.now().strftime("%d/%m %H:%M"),
                "Agente": st.session_state.user,
                "ID_StarMaker": id_sm,
                "Coins": c_erogate
            })
            st.balloons()
            st.rerun()
        else:
            st.error("Budget insufficiente! Contatta Massimo.")

# --- 7. GARA PUBBLICA ---
st.divider()
st.subheader("🏁 Gara Subagenti Taurus - Classifica Vendite")
classifica = st.session_state.db[st.session_state.db['Agente'] != "MassimoMaster"][['Agente', 'Vendite_Totali_Coins']]
st.table(classifica.sort_values(by='Vendite_Totali_Coins', ascending=False))
