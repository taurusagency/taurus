
import streamlit as st
import pandas as pd
from datetime import datetime
import base64

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Taurus Agency - StarMaker Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- COSTANTI DI BUSINESS ---
# Acquisto: 1€ = 101 Coin
# Vendita: 1€ = 91 Coin
# Margine Totale: 10 Coin/€ -> 5 Coin Agenzia / 5 Coin Subagente
COIN_PER_EURO_VENDITA = 91
MARGINE_COIN_TOTALE = 10
RIPARTIZIONE_PERCENTUALE = 0.5
APP_URL = "https://taurus-agency.streamlit.app" # Sostituisci con il tuo URL reale

# --- STILE CSS ---
st.markdown("""
<style>
    /* Sfondo e font */
    .main { background-color: #f8f9fa; }
    
    /* Box Guadagno in alto a destra */
    .profit-container {
        position: fixed;
        top: 60px;
        right: 20px;
        z-index: 999;
        background: linear-gradient(135deg, #1e1e1e 0%, #333333 100%);
        color: #FFD700;
        padding: 15px 25px;
        border-radius: 15px;
        border: 2px solid #FFD700;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        min-width: 180px;
    }
    
    /* Card Subagenti */
    .agent-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #FFD700;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Header e Titoli */
    h1, h2, h3 { color: #1a1a1a; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Bottoni */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONI DI CALCOLO ---
def calcola_operazione(euro):
    coin_erogati = euro * COIN_PER_EURO_VENDITA
    margine_totale = euro * MARGINE_COIN_TOTALE
    guadagno_singolo_coin = margine_totale * RIPARTIZIONE_PERCENTUALE
    # Conversione in Euro basata sul costo reale di acquisto (101 coin = 1€)
    guadagno_singolo_euro = guadagno_singolo_coin / 101
    return coin_erogati, guadagno_singolo_coin, guadagno_singolo_euro

# --- GESTIONE STATO (DATABASE TEMPORANEO) ---
if 'user_role' not in st.session_state:
    st.session_state.user_role = 'Agenzia' # Alternare tra 'Agenzia' e 'Subagente' per test
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []

# --- CALCOLO TOTALI PER IL QUADRATINO IN ALTO ---
if st.session_state.user_role == 'Agenzia':
    # L'agenzia vede il totale di tutti i suoi margini dai subagenti
    tot_coin = sum([v['margine_agency_coin'] for v in st.session_state.db_vendite])
    tot_euro = sum([v['margine_agency_euro'] for v in st.session_state.db_vendite])
else:
    # Il subagente vede solo il suo guadagno
    tot_coin = sum([v['margine_sub_coin'] for v in st.session_state.db_vendite])
    tot_euro = sum([v['margine_sub_euro'] for v in st.session_state.db_vendite])

# --- WIDGET GUADAGNO FISSO ---
st.markdown(f"""
    <div class="profit-container">
        <div style="font-size: 0.8rem; letter-spacing: 1px;">GUADAGNO TOTALE</div>
        <div style="font-size: 1.6rem; font-weight: 800;">{tot_coin:,.0f} COIN</div>
        <div style="font-size: 1.2rem; color: #ffffff;">{tot_euro:,.2f} €</div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR LOGOUT/SWITCH (PER DEMO) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1055/1055644.png", width=100)
    st.title("Taurus Admin")
    role = st.radio("Seleziona Interfaccia (Test):", ["Agenzia", "Subagente"])
    st.session_state.user_role = role
    st.divider()
    st.info(f"Connesso come: **{st.session_state.user_role}**")

# --- CONTENUTO PRINCIPALE ---
st.title("🛡️ Taurus Agency Management")
st.write("Sistema integrato ricariche StarMaker & Rete Subagenti")

if st.session_state.user_role == 'Agenzia':
    # ==========================
    # AREA TAURUS AGENCY (ADMIN)
    # ==========================
    t1, t2 = st.tabs(["📊 Dashboard Rete", "👥 Gestione Subagenti"])
    
    with t1:
        st.subheader("Riepilogo Performance Subagenti")
        col_main1, col_main2, col_main3 = st.columns(3)
        col_main1.metric("Totale Coin Agenzia", f"{tot_coin:,.0f}")
        col_main2.metric("Valore in Euro", f"€ {tot_euro:,.2f}")
        col_main3.metric("Operazioni Totali", len(st.session_state.db_vendite))
        
        st.divider()
        
        # Griglia Subagenti
        cols = st.columns(2)
        for i in range(1, 13):
            with cols[i%2]:
                st.markdown(f"""
                <div class="agent-card">
                    <h3>Subagente {i:02d}</h3>
                    <p>ID Account: <b>ST-AGENT-{i:03d}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(f"Dettagli e Credenziali Agente {i}"):
                    u = f"taurus_sub_{i}"
                    p = f"pass_{i}2026"
                    wa = st.text_input("Numero WhatsApp", key=f"wa_{i}")
                    
                    msg = f"🛡️ *TAURUS AGENCY - CREDENZIALI*\n\n🔗 Accedi qui: {APP_URL}\n👤 Username: {u}\n🔑 Password: {p}\n\n*Nota: Ogni ricarica genera 5 coin di guadagno per te ogni 1€ venduto.*"
                    
                    if st.button(f"Invia Credenziali Agente {i}", key=f"btn_{i}"):
                        st.success("Testo pronto per l'invio!")
                        st.code(msg)
                st.write("") # Spacer

    with t2:
        st.subheader("Registro Tutte le Vendite")
        if st.session_state.db_vendite:
            df = pd.DataFrame(st.session_state.db_vendite)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Nessuna vendita registrata al momento.")

else:
    # ==========================
    # AREA SUBAGENTE (OPERATIVO)
    # ==========================
    st.subheader("📲 Nuova Ricarica Cliente")
    
    with st.container():
        st.markdown('<div class="agent-card" style="border-left-color: #007bff;">', unsafe_allow_html=True)
        with st.form("form_ricarica"):
            c1, c2 = st.columns(2)
            id_starmaker = c1.text_input("ID StarMaker Cliente", placeholder="Es: 1234567")
            importo_euro = c2.number_input("Importo Ricarica (€)", min_value=1, value=10)
            
            coin_cli, g_coin, g_euro = calcola_operazione(importo_euro)
            
            st.divider()
            st.write("### Anteprima Operazione")
            cc1, cc2 = st.columns(2)
            cc1.info(f"**Al Cliente:** {coin_cli:,.0f} Coin")
            cc2.success(f"**Tuo Guadagno:** {g_coin:,.0f} Coin ({g_euro:.2f} €)")
            
            submit = st.form_submit_button("CONFERMA E REGISTRA RICARICA")
            
            if submit:
                if id_starmaker:
                    v = {
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "ID Cliente": id_starmaker,
                        "Euro Venduti": importo_euro,
                        "Coin Cliente": coin_cli,
                        "margine_sub_coin": g_coin,
                        "margine_sub_euro": g_euro,
                        "margine_agency_coin": g_coin, # 50% all'agenzia
                        "margine_agency_euro": g_euro
                    }
                    st.session_state.db_vendite.append(v)
                    st.balloons()
                    st.success("Operazione registrata con successo!")
                else:
                    st.error("Inserire un ID StarMaker valido.")
        st.markdown('</div>', unsafe_allow_html=True)
