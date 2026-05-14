import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="Taurus Agency PRO", layout="wide")

st.markdown("""
    <style>
    .reportview-container { background: #f0f2f6; }
    .main-stats { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #007bff; }
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE TEMPORANEO (Inizializzazione) ---
if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = pd.DataFrame(columns=['Data', 'ID_StarMaker', 'Subagente', 'Euro_Spesi', 'Coin_Venduti', 'Guadagno_Taurus', 'Guadagno_Sub'])
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None # 'Master' o 'Subagente'

# --- SISTEMA DI LOGIN ---
if not st.session_state.logged_in:
    st.title("🔐 Accesso Taurus Agency")
    user = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Accedi"):
        if user == "TaurusMaster" and password == "Taurus2026": # Credenziali Master
            st.session_state.logged_in = True
            st.session_state.user_role = "Master"
            st.rerun()
        elif user.startswith("sub") and password == "pass": # Esempio per subagenti
            st.session_state.logged_in = True
            st.session_state.user_role = "Subagente"
            st.session_state.username = user
            st.rerun()
        else:
            st.error("Credenziali errate")
    st.stop()

# --- LOGICA CALCOLO GUADAGNI ---
# Calcoliamo i totali per visualizzarli "in diretta" su ogni pagina
tot_euro = st.session_state.db_vendite['Euro_Spesi'].sum()
tot_guadagno_taurus = st.session_state.db_vendite['Guadagno_Taurus'].sum()
tot_guadagno_sub = st.session_state.db_vendite['Guadagno_Sub'].sum()

# --- HEADER FISSO (Visibile in tutte le pagine) ---
st.markdown(f"""
    <div class="main-stats">
        <h2 style='margin-top:0;'>🐂 Taurus Dashboard - {st.session_state.user_role}</h2>
        <p>Benvenuto, <b>{st.session_state.get('username', 'Taurus Master')}</b></p>
    </div>
    """, unsafe_allow_html=True)

# METRICHE SEMPRE VISIBILI
c1, c2, c3 = st.columns(3)
c1.metric("Volume Totale (€)", f"{tot_euro} €")
if st.session_state.user_role == "Master":
    c2.metric("Guadagno Agenzia (Coin)", f"{tot_guadagno_taurus} 🪙")
    c3.metric("Guadagno Tot. Subagenti (Coin)", f"{tot_guadagno_sub} 🪙")
else:
    # Il subagente vede solo il suo guadagno
    mio_guadagno = st.session_state.db_vendite[st.session_state.db_vendite['Subagente'] == st.session_state.username]['Guadagno_Sub'].sum()
    c2.metric("Il Tuo Guadagno (Coin)", f"{mio_guadagno} 🪙")
    c3.metric("Stato Obiettivo", "In crescita")

st.divider()

# --- NAVIGAZIONE ---
menu = ["🛒 Vendita Coins", "📊 Statistiche", "👥 Gestione Accessi"] if st.session_state.user_role == "Master" else ["🛒 Vendita Coins", "📊 Le Mie Statistiche"]
scelta = st.sidebar.radio("Navigazione", menu)

# --- SEZIONE VENDITA (UGUALE PER TUTTI) ---
if scelta == "🛒 Vendita Coins":
    st.subheader("Registra Nuova Vendita StarMaker")
    with st.form("form_vendita"):
        id_sm = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Euro Ricevuti dal Cliente", min_value=1)
        submit = st.form_submit_button("Conferma Vendita")
        
        if submit:
            # Calcoli basati sulla tua formula
            coin_consegnati = euro * 91
            guadagno_t = euro * 5
            guadagno_s = euro * 5
            
            nuova_vendita = {
                'Data': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
                'ID_StarMaker': id_sm,
                'Subagente': st.session_state.get('username', 'Master'),
                'Euro_Spesi': euro,
                'Coin_Venduti': coin_consegnati,
                'Guadagno_Taurus': guadagno_t,
                'Guadagno_Sub': guadagno_s
            }
            st.session_state.db_vendite = pd.concat([st.session_state.db_vendite, pd.DataFrame([nuova_vendita])], ignore_index=True)
            st.success(f"Vendita Registrata! Consegnare {coin_consegnati} coins all'ID {id_sm}")

# --- SEZIONE STATISTICHE ---
elif scelta == "📊 Statistiche" or scelta == "📊 Le Mie Statistiche":
    st.subheader("Analisi Vendite e Profitti")
    df = st.session_state.db_vendite
    if st.session_state.user_role == "Subagente":
        df = df[df['Subagente'] == st.session_state.username]
    
    st.dataframe(df, use_container_width=True)
    
    if not df.empty:
        fig = px.line(df, x='Data', y='Euro_Spesi', title="Andamento Vendite nel Tempo")
        st.plotly_chart(fig, use_container_width=True)

# --- SEZIONE GESTIONE (SOLO MASTER) ---
elif scelta == "👥 Gestione Accessi" and st.session_state.user_role == "Master":
    st.subheader("Controllo Subagenti")
    st.write("Qui puoi gestire i 12 subagenti, cambiare password e monitorare chi sta vendendo di più.")
    # Logica precedente di modifica username/password...
    st.info("Pannello di controllo Master attivo.")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
