import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency Management", layout="wide")

# --- STILE GRAFICO ---
st.markdown("""
    <style>
    .main { background-color: #f4f7f6; }
    .card { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-bottom: 20px; border-top: 5px solid #007bff; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATABASE (SESSION STATE) ---
if 'db_agenti' not in st.session_state:
    st.session_state.monete_agenzia = 1000000  # Capitale iniziale Master
    st.session_state.db_agenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Agente {i}' for i in range(1, 13)],
        'Username': [f'taurus_user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}' for i in range(1, 13)],
        'Monete_Attuali': [0 for _ in range(12)],
        'Guadagno_Coin': [0 for _ in range(12)]
    })
if 'vendite' not in st.session_state:
    st.session_state.vendite = pd.DataFrame(columns=['Data', 'ID_StarMaker', 'Agente', 'Euro', 'Coin', 'Profitto_M', 'Profitto_A'])
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- LOGIN ---
if not st.session_state.logged_in:
    st.title("🔒 Accesso Taurus Agency")
    with st.form("Login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Entra"):
            if u == "TaurusMaster" and p == "Taurus2026":
                st.session_state.logged_in = True
                st.session_state.role = "Master"
                st.rerun()
            else:
                # Controllo se è un agente
                user_match = st.session_state.db_agenti[st.session_state.db_agenti['Username'] == u]
                if not user_match.empty and user_match.iloc[0]['Password'] == p:
                    st.session_state.logged_in = True
                    st.session_state.role = "Agente"
                    st.session_state.username = u
                    st.rerun()
                else:
                    st.error("Credenziali errate")
    st.stop()

# --- HEADER FISSO ---
st.markdown(f"<div class='card'><h2>🐂 Dashboard Taurus Agency - {st.session_state.role}</h2></div>", unsafe_allow_html=True)

# CALCOLO GUADAGNI TOTALI (In diretta)
profitto_master_tot = st.session_state.vendite['Profitto_M'].sum()
euro_totali = st.session_state.vendite['Euro'].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Cassaforte Master (Coin)", f"{st.session_state.monete_agenzia:,}")
c2.metric("Euro Totali Incassati", f"{euro_totali} €")
c3.metric("Mio Guadagno (Coin)", f"{profitto_master_tot if st.session_state.role == 'Master' else 0}")
c4.metric("Status", "Operativo", "✅")

st.divider()

# --- NAVIGAZIONE ---
if st.session_state.role == "Master":
    menu = ["💼 Cassaforte & Agenti", "🛒 Vendita Coins", "📊 Statistiche & Gara"]
else:
    menu = ["🛒 Vendita Coins", "📊 Mie Vendite"]
scelta = st.sidebar.radio("Menu", menu)

# --- 1. SEZIONE CASSAFORTE & AGENTI (SOLO MASTER) ---
if scelta == "💼 Cassaforte & Agenti":
    st.subheader("🏦 Gestione Capitale e 12 Agenti")
    
    # A) Gestione Cassaforte Centrale
    with st.expander("💰 Gestisci Cassaforte Master (Aumenta/Diminuisci)"):
        col_a, col_b = st.columns(2)
        quantita = col_a.number_input("Quantità monete", min_value=0, step=1000)
        operazione = col_b.radio("Azione", ["Aggiungi (+)", "Rimuovi (-)"])
        if st.button("Aggiorna Cassaforte"):
            if operazione == "Aggiungi (+)":
                st.session_state.monete_agenzia += quantita
            else:
                st.session_state.monete_agenzia -= quantita
            st.success("Capitale aggiornato!")
            st.rerun()

    st.divider()
    
    # B) Gestione Agenti (Username, Password e Rabbocco)
    for i, row in st.session_state.db_agenti.iterrows():
        with st.container():
            st.markdown(f"<div style='border:1px solid #ddd; padding:15px; border-radius:10px; margin-bottom:10px;'><b>{row['Nome']}</b> (Saldo: {row['Monete_Attuali']:,} 🪙)</div>", unsafe_allow_html=True)
            c_user, c_pass, c_rab, c_btn = st.columns([2, 2, 2, 1])
            
            new_u = c_user.text_input("User", row['Username'], key=f"u{i}")
            new_p = c_pass.text_input("Pass", row['Password'], key=f"p{i}")
            amount_rab = c_rab.number_input("Rabbocco", min_value=0, key=f"r{i}")
            
            if c_btn.button("Salva/Invia", key=f"b{i}"):
                # Se c'è un rabbocco, togliamo dalla cassaforte e diamo all'agente
                if amount_rab > 0:
                    if st.session_state.monete_agenzia >= amount_rab:
                        st.session_state.monete_agenzia -= amount_rab
                        st.session_state.db_agenti.at[i, 'Monete_Attuali'] += amount_rab
                    else:
                        st.error("Monete insufficienti in cassaforte!")
                
                st.session_state.db_agenti.at[i, 'Username'] = new_u
                st.session_state.db_agenti.at[i, 'Password'] = new_p
                
                # Link WhatsApp
                msg = f"Ciao {row['Nome']}, credenziali aggiornate:\nUser: {new_u}\nPass: {new_p}\nCarico ricevuto: {amount_rab}"
                st.markdown(f"[📲 Invia a WhatsApp](https://wa.me/?text={urllib.parse.quote(msg)})")
                st.rerun()

# --- 2. SEZIONE VENDITA (LOGICA 101/91) ---
elif scelta == "🛒 Vendita Coins":
    st.subheader("Registra Vendita (Formula 1€ = 91 Coin)")
    with st.form("vendita"):
        id_sm = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Euro ricevuti", min_value=1)
        if st.form_submit_button("Esegui Vendita"):
            coin_da_dare = euro * 91
            prof_m = euro * 5
            prof_a = euro * 5
            
            # Qui andrebbe il controllo se l'agente ha abbastanza monete (omesso per brevità)
            nuova_v = {
                'Data': pd.Timestamp.now().strftime("%H:%M:%S"),
                'ID_StarMaker': id_sm,
                'Agente': st.session_state.get('username', 'Master'),
                'Euro': euro,
                'Coin': coin_da_dare,
                'Profitto_M': prof_m,
                'Profitto_A': prof_a
            }
            st.session_state.vendite = pd.concat([st.session_state.vendite, pd.DataFrame([nuova_v])], ignore_index=True)
            st.balloons()
            st.success(f"Vendita completata! Consegnare {coin_da_dare} coins.")

# --- 3. STATISTICHE ---
elif scelta == "📊 Statistiche & Gara":
    st.subheader("Classifica e Guadagni")
    st.dataframe(st.session_state.vendite)
    fig = px.bar(st.session_state.db_agenti, x='Nome', y='Monete_Attuali', title="Monete possedute dagli agenti")
    st.plotly_chart(fig)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()
