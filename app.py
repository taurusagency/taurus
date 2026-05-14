import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE DELLA PAGINA ---
st.set_page_config(
    page_title="Taurus Agency - StarMaker Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- LOGICA DI SICUREZZA E DATABASE UTENTI ---
# Qui definiamo le tue credenziali (Admin) e quelle iniziali dei subagenti
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        "admin": {"pass": "taurus2026", "role": "Agenzia", "name": "Taurus Owner"},
    }
    # Creazione automatica dei 12 profili subagenti modificabili
    for i in range(1, 13):
        user_key = f"agente{i}"
        st.session_state.users_db[user_key] = {
            "pass": f"pass{i}", 
            "role": "Subagente", 
            "name": f"Agente {i}"
        }

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'db_vendite' not in st.session_state:
    st.session_state.db_vendite = []

# --- COSTANTI DI BUSINESS ---
COIN_PER_EURO_VENDITA = 91
MARGINE_COIN_TOTALE = 10
APP_URL = "https://taurus-agency.streamlit.app" # <--- CAMBIA QUESTO CON IL TUO URL REALE

# --- STILE GRAFICO CSS ---
st.markdown("""
<style>
    .main { background-color: #f4f7f6; }
    .profit-container {
        position: fixed; top: 60px; right: 20px; z-index: 999;
        background: linear-gradient(135deg, #1e1e1e 0%, #434343 100%);
        color: #FFD700; padding: 18px; border-radius: 15px; border: 2px solid #FFD700;
        text-align: center; min-width: 200px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .agent-card {
        background-color: white; padding: 20px; border-radius: 15px;
        border-left: 8px solid #FFD700; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button { width: 100%; border-radius: 10px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 1. SCHERMATA DI LOGIN (ACCESSO) ---
if not st.session_state.authenticated:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.title("🛡️ Taurus Agency Login")
        with st.form("login_form"):
            user_input = st.text_input("Username (Nome Utente)")
            pass_input = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("ACCEDI AL SISTEMA")
            
            if login_btn:
                if user_input in st.session_state.users_db and st.session_state.users_db[user_input]["pass"] == pass_input:
                    st.session_state.authenticated = True
                    st.session_state.user_logged = user_input
                    st.session_state.user_role = st.session_state.users_db[user_input]["role"]
                    st.rerun()
                else:
                    st.error("Credenziali errate. Controlla Username e Password.")
    st.stop() 

# --- 2. CALCOLO GUADAGNI REAL-TIME ---
current_user = st.session_state.user_logged
user_role = st.session_state.user_role

if user_role == 'Agenzia':
    # L'admin vede il margine totale (5 coin per ogni euro venduto da chiunque)
    tot_coin = sum([v['margine_agency_coin'] for v in st.session_state.db_vendite])
    tot_euro = sum([v['margine_agency_euro'] for v in st.session_state.db_vendite])
else:
    # Il subagente vede solo i suoi 5 coin per ogni euro che ha venduto lui
    mie_vendite = [v for v in st.session_state.db_vendite if v['Agente'] == current_user]
    tot_coin = sum([v['margine_sub_coin'] for v in mie_vendite])
    tot_euro = sum([v['margine_sub_euro'] for v in mie_vendite])

# Widget Fisso in Alto a Destra
st.markdown(f"""
    <div class="profit-container">
        <div style="font-size: 0.8rem; opacity: 0.8;">GUADAGNO ATTUALE</div>
        <div style="font-size: 1.6rem; font-weight: bold;">{tot_coin:,.0f} COIN</div>
        <div style="font-size: 1.2rem; color: #fff;">{tot_euro:,.2f} €</div>
    </div>
""", unsafe_allow_html=True)

# --- 3. INTERFACCIA AGENZIA (AMMINISTRATORE) ---
if user_role == 'Agenzia':
    st.sidebar.title("Menu Admin")
    if st.sidebar.button("LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

    st.title("Pannello Taurus Agency - Gestione Rete")
    
    t1, t2 = st.tabs(["👥 Gestione Subagenti", "📊 Registro Vendite Totali"])
    
    with t1:
        st.subheader("Configurazione Credenziali e Invio")
        cols = st.columns(2)
        for i in range(1, 13):
            u_key = f"agente{i}"
            with cols[i%2]:
                st.markdown(f'<div class="agent-card">', unsafe_allow_html=True)
                st.markdown(f"### {st.session_state.users_db[u_key]['name']}")
                
                with st.expander("Modifica Nome/Pass e Genera Messaggio"):
                    # Campi per modificare dati
                    nuovo_nome = st.text_input(f"Nome Agente {i}", value=st.session_state.users_db[u_key]["name"], key=f"n_{i}")
                    nuova_pass = st.text_input(f"Password Agente {i}", value=st.session_state.users_db[u_key]["pass"], key=f"p_{i}")
                    
                    # Salvataggio nel database della sessione
                    st.session_state.users_db[u_key]["name"] = nuovo_nome
                    st.session_state.users_db[u_key]["pass"] = nuova_pass
                    
                    # Messaggio da copiare
                    msg = f"🛡️ *TAURUS AGENCY - ACCESSO*\\n\\n🔗 Link: {APP_URL}\\n👤 User: {u_key}\\n🔑 Pass: {nuova_pass}\\n\\nBenvenuto nel team!"
                    st.code(msg)
                    if st.button(f"Conferma Modifiche Agente {i}", key=f"btn_{i}"):
                        st.success("Dati aggiornati!")
                st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.subheader("Storico Operazioni di tutta la rete")
        if st.session_state.db_vendite:
            df = pd.DataFrame(st.session_state.db_vendite)
            st.table(df)
        else:
            st.info("Nessuna ricarica registrata finora.")

# --- 4. INTERFACCIA SUBAGENTE (OPERATIVO) ---
else:
    st.sidebar.title("Menu Agente")
    if st.sidebar.button("LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

    st.title(f"Operativo: {st.session_state.users_db[current_user]['name']}")
    
    with st.container():
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        with st.form("ricarica_form"):
            st.subheader("📲 Inserisci Nuova Ricarica")
            id_sm = st.text_input("ID StarMaker Cliente (ID Utente)")
            euro = st.number_input("Prezzo Pagato dal Cliente (€)", min_value=1, step=1)
            
            # Calcoli automatici
            coin_al_cliente = euro * COIN_PER_EURO_VENDITA
            guadagno_agente_coin = (euro * MARGINE_COIN_TOTALE) / 2
            guadagno_agente_euro = guadagno_agente_coin / 101
            
            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("Monete al Cliente", f"{coin_al_cliente:,.0f} Coin")
            c2.metric("Tuo Guadagno", f"€ {guadagno_agente_euro:.2f}", f"{guadagno_agente_coin:.0f} Coin")
            
            submit = st.form_submit_button("REGISTRA E INVIA RICARICA")
            
            if submit:
                if id_sm:
                    # Registra l'operazione
                    st.session_state.db_vendite.append({
                        "Data": datetime.now().strftime("%d/%m %H:%M"),
                        "Agente": current_user,
                        "ID StarMaker": id_sm,
                        "Euro": euro,
                        "Coin Cliente": coin_al_cliente,
                        "margine_sub_coin": guadagno_agente_coin,
                        "margine_sub_euro": guadagno_agente_euro,
                        "margine_agency_coin": guadagno_agente_coin, # 50% all'admin
                        "margine_agency_euro": guadagno_agente_euro
                    })
                    st.balloons()
                    st.success("Ricarica registrata con successo!")
                else:
                    st.error("Inserisci l'ID del cliente per procedere.")
        st.markdown('</div>', unsafe_allow_html=True)
