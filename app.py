import streamlit as st
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Taurus Agency - StarMaker Portal", layout="centered")

# --- DATABASE CREDENZIALI (Semplificato) ---
# Puoi aggiungere qui tutte le mail dei tuoi subagenti
USERS = {
    "TaurusMaster": "Taurus2026",
    "giuseppe.papangelo@outlook.it": "TaurusSub2026",
    "subagente2@gmail.com": "TaurusSub2026"
}

def login_screen():
    st.title("🛡️ Taurus Agency - Login")
    st.info("Inserisci la tua mail e la password fornita dal Master per accedere.")
    
    with st.form("login_form"):
        email = st.text_input("Email o Username")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Accedi al Portale")
        
        if submit:
            if email in USERS and USERS[email] == pwd:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.is_master = (email == "TaurusMaster")
                st.rerun()
            else:
                st.error("Credenziali errate o account non autorizzato.")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_screen()
else:
    # --- LOGICA APP DOPO IL LOGIN ---
    st.sidebar.success(f"Loggato come: {st.session_state.user_email}")
    if st.sidebar.button("Esci"):
        st.session_state.authenticated = False
        st.rerun()

    if st.session_state.is_master:
        st.title("📊 Pannello Master - Taurus Agency")
        st.write("Qui controlli tutti i subagenti e i margini.")
        # Spazio per la tabella globale delle vendite
    else:
        st.title("📱 Area Vendite Sub-Agente")
        st.write(f"Benvenuto nel tuo portale operativo.")
        
        # Calcolo automatico monete
        euro = st.number_input("Inserisci Euro incassati (€)", min_value=0.0)
        if euro > 0:
            monete_erogate = int(euro * 91)
            margine_tuo = int(euro * 5)
            st.metric("Monete da ricaricare", f"{monete_erogate}")
            st.metric("Tuo margine (guadagno)", f"{margine_tuo} monete")
            
            if st.button("Conferma Operazione"):
                # Qui andrebbe il codice per salvare i dati su un file o database
                st.success("Operazione registrata con successo!")
