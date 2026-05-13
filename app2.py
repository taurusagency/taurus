import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# Configurazione Pagina
st.set_page_config(page_title="Taurus Agency Pro", layout="wide", initial_sidebar_state="collapsed")

# CSS per creare lo stile a "Quadrati/Card"
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 150px;
        border-radius: 15px;
        font-size: 20px;
        font-weight: bold;
        background-color: #f0f2f6;
        border: 2px solid #e0e0e0;
    }
    .stButton>button:hover {
        background-color: #007bff;
        color: white;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- STATO DELL'AGENZIA (Simulazione dati) ---
if 'capitale_totale' not in st.session_state:
    st.session_state.capitale_totale = 1000000  # Totale monete agenzia
    st.session_state.subagenti = pd.DataFrame({
        'Nome': [f'Subagente {i+1}' for i in range(12)],
        'Username': [f'user_{i+1}' for i in range(12)],
        'Password': [f'pass_{i+1}' for i in range(12)],
        'Monete': [50000 for _ in range(12)],
        'Trend': [2.5 for _ in range(12)] # Più o meno sul rabocco
    })

# --- HEADER ---
st.title("🐂 Taurus Agency - Global Dashboard")
st.write("Benvenuto, Amministratore. Gestisci il tuo capitale e i tuoi 12 subagenti.")

# --- SEZIONE 1: KPI GENERALI ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Capitale Totale Agenzia", f"{st.session_state.capitale_totale:,}", "+5%")
with col2:
    st.metric("Subagenti Attivi", "12/12")
with col3:
    st.metric("Media Vendite", "85k")
with col4:
    st.metric("Status Server", "Online", delta_color="normal")

st.divider()

# --- SEZIONE 2: MENU A QUADRATI (Interfaccia Grafica) ---
st.subheader("Seleziona un'operazione")
q1, q2, q3, q4 = st.columns(4)

menu = "Home"
if q1.button("📊\nDashboard Grafica"):
    st.session_state.view = "grafica"
if q2.button("👥\nGestione Subagenti"):
    st.session_state.view = "subagenti"
if q3.button("🏆\nGara Subagenti"):
    st.session_state.view = "gara"
if q4.button("📥\nRabocco Agenzia"):
    st.session_state.view = "rabocco"

# Logica di visualizzazione basata sul click
view = st.session_state.get('view', 'grafica')

# --- VISTA: DASHBOARD GRAFICA ---
if view == "grafica":
    c1, c2 = st.columns([2, 1])
    with c1:
        st.write("### Andamento Vendite Globali")
        df_grafico = pd.DataFrame({'Giorno': range(1,11), 'Monete': [i*10000 for i in range(1,11)]})
        fig = px.area(df_grafico, x='Giorno', y='Monete', title="Crescita Capitale")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("### Distribuzione Monete")
        fig2 = px.pie(st.session_state.subagenti, values='Monete', names='Nome')
        st.plotly_chart(fig2, use_container_width=True)

# --- VISTA: GESTIONE SUBAGENTI & WHATSAPP ---
elif view == "subagenti":
    st.subheader("Anagrafica e Invio Credenziali")
    for index, row in st.session_state.subagenti.iterrows():
        with st.expander(f"⚙️ Modifica {row['Nome']}"):
            new_user = st.text_input(f"Username per {row['Nome']}", row['Username'])
            new_pass = st.text_input(f"Password per {row['Nome']}", row['Password'], type="password")
            
            # Creazione link WhatsApp
            msg = f"Ciao {row['Nome']}, ecco le tue credenziali Taurus Agency:\nUsername: {new_user}\nPassword: {new_pass}\nAccedi qui: https://taurus-app-finale.streamlit.app"
            msg_encoded = urllib.parse.quote(msg)
            whatsapp_url = f"https://wa.me/?text={msg_encoded}"
            
            st.markdown(f"[📲 Invia Credenziali su WhatsApp]({whatsapp_url})")

# --- VISTA: GARA SUBAGENTI (Ranking) ---
elif view == "gara":
    st.subheader("🏆 Classifica Gara Subagenti")
    df_sorted = st.session_state.subagenti.sort_values(by='Monete', ascending=False)
    st.table(df_sorted[['Nome', 'Monete', 'Trend']])
    st.bar_chart(df_sorted.set_index('Nome')['Monete'])

# --- VISTA: RABOCCO ---
elif view == "rabocco":
    st.subheader("Gestione Flussi di Cassa")
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("### Rabocco Agenzia (Proprietario)")
        nuovo_carico = st.number_input("Aggiungi Monete al Totale", min_value=0)
        if st.button("Conferma Carico"):
            st.session_state.capitale_totale += nuovo_carico
            st.success("Capitale Aggiornato!")
    with col_b:
        st.write("### Sposta Capitale a Subagente")
        target = st.selectbox("Seleziona Subagente", st.session_state.subagenti['Nome'])
        quantita = st.number_input("Monete da assegnare", min_value=0)
        if st.button("Esegui Trasferimento"):
            st.warning(f"Trasferimento di {quantita} a {target} completato.")
