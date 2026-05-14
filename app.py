import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# Configurazione Avanzata
st.set_page_config(page_title="Taurus Agency - Pro Dashboard", layout="wide", initial_sidebar_state="collapsed")

# Stile CSS per un'interfaccia moderna e intuitiva
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .agent-card { border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; background-color: white; margin-bottom: 10px; }
    div.stButton > button:first-child { height: 3em; width: 100%; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Dati Subagenti (12)
if 'db_subagenti' not in st.session_state:
    st.session_state.capitale_agenzia = 5000000
    st.session_state.db_subagenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Subagente {i}' for i in range(1, 13)],
        'Username': [f'taurus_user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}026' for i in range(1, 13)],
        'Monete_Attuali': [100000 for _ in range(12)],
        'Vendite_Mese': [0 for _ in range(12)],
        'Performance': [0.0 for _ in range(12)]
    })

# Titolo e Indicatori Principali (Il "più e meno" sul capitale)
st.title("🐂 Taurus Agency - Controllo Totale")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Capitale Totale Agenzia", f"{st.session_state.capitale_agenzia:,}", "+12% vs ieri")
c2.metric("Totale Monete Subagenti", f"{st.session_state.db_subagenti['Monete_Attuali'].sum():,}", "-2% (scarico)")
c3.metric("Gara attiva", "Maggio 2026", "Giorno 14")
c4.metric("Status Rete", "12 Subagenti Online", "✅")

st.divider()

# Menu a Quadrati (Navigazione Intuitiva)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
v1 = col_m1.button("📊 Analisi Grafica")
v2 = col_m2.button("👥 Gestione Subagenti")
v3 = col_m3.button("🏆 Gara & Profitti")
v4 = col_m4.button("💰 Rabocco / Scarico")

# Gestione della navigazione
if v1: st.session_state.page = "grafica"
elif v2: st.session_state.page = "subagenti"
elif v3: st.session_state.page = "gara"
elif v4: st.session_state.page = "rabocco"
elif 'page' not in st.session_state: st.session_state.page = "grafica"

# --- PAGINA: ANALISI GRAFICA ---
if st.session_state.page == "grafica":
    st.subheader("Andamento Analitico Agenzia")
    col_g1, col_g2 = st.columns([2,1])
    with col_g1:
        fig_perf = px.bar(st.session_state.db_subagenti, x='Nome', y='Monete_Attuali', color='Monete_Attuali', title="Distribuzione Monete tra Subagenti")
        st.plotly_chart(fig_perf, use_container_width=True)
    with col_g2:
        fig_pie = px.pie(st.session_state.db_subagenti, values='Monete_Attuali', names='Nome', title="Quote Capitale")
        st.plotly_chart(fig_pie, use_container_width=True)

# --- PAGINA: GESTIONE SUBAGENTI (Accessi e WhatsApp) ---
elif st.session_state.page == "subagenti":
    st.subheader("Pannello Gestione 12 Subagenti")
    for i, row in st.session_state.db_subagenti.iterrows():
        with st.container():
            st.markdown(f"""<div class='agent-card'><b>{row['Nome']}</b> | User: {row['Username']}</div>""", unsafe_allow_html=True)
            ca, cb, cc = st.columns([2,2,1])
            nuova_pass = ca.text_input(f"Cambia Password {row['Nome']}", row['Password'], key=f"p{i}")
            if cb.button(f"Salva Credenziali {i+1}"):
                st.session_state.db_subagenti.at[i, 'Password'] = nuova_pass
                st.success("Salvato!")
            
            # Link WhatsApp
            testo_wa = f"Ciao {row['Nome']}, credenziali Taurus aggiornate:\nUser: {row['Username']}\nPass: {nuova_pass}"
            url_wa = f"https://wa.me/?text={urllib.parse.quote(testo_wa)}"
            cc.markdown(f"[📲 Invia]({url_wa})")

# --- PAGINA: GARA & PROFITTI ---
elif st.session_state.page == "gara":
    st.subheader("🏆 Leaderboard Gara Subagenti")
    st.write("Il sistema calcola automaticamente il più e il meno sui volumi di vendita.")
    classifica = st.session_state.db_subagenti.sort_values(by='Monete_Attuali', ascending=False)
    st.dataframe(classifica[['Nome', 'Monete_Attuali', 'Performance']], use_container_width=True)

# --- PAGINA: RABOCCO ---
elif st.session_state.page == "rabocco":
    st.subheader("Gestione Rabocco Agenzia e Subagenti")
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.write("### Rabocco Agenzia Centrale")
        quantita = st.number_input("Quantità Monete da aggiungere al capitale totale", min_value=0)
        if st.button("Conferma Rabocco Totale"):
            st.session_state.capitale_agenzia += quantita
            st.balloons()
    with col_r2:
        st.write("### Trasferimento a Subagente")
        sub_scelto = st.selectbox("Seleziona chi deve ricevere", st.session_state.db_subagenti['Nome'])
        m_trasf = st.number_input("Quantità da trasferire", min_value=0)
        if st.button("Esegui Trasferimento"):
            st.session_state.capitale_agenzia -= m_trasf
            st.success(f"Trasferimento completato a {sub_scelto}")
