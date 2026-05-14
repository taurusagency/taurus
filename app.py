import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Energy Dashboard", layout="wide")

# --- STILE CSS PER LE BARRE DI ENERGIA ---
st.markdown("""
    <style>
    .energy-bar-container { width: 100%; background-color: #e0e0e0; border-radius: 10px; margin: 10px 0; }
    .energy-bar-fill { height: 20px; border-radius: 10px; transition: width 0.5s; }
    .status-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE PER DISEGNARE LA BARRA DI ENERGIA ---
def energy_bar(current, total):
    percent = min(100, max(0, int((current / total) * 100))) if total > 0 else 0
    color = "#28a745" if percent > 50 else "#ffc107" if percent > 20 else "#dc3545"
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span>Energia Coin: {percent}%</span>
            <span>{current:,} / {total:,}</span>
        </div>
        <div class="energy-bar-container">
            <div class="energy-bar-fill" style="width: {percent}%; background-color: {color};"></div>
        </div>
        """, unsafe_allow_html=True)

# --- DATABASE IN MEMORIA ---
if 'monete_master_max' not in st.session_state:
    st.session_state.monete_master_max = 5000000
    st.session_state.monete_master_attuali = 4500000
if 'db_agenti' not in st.session_state:
    st.session_state.db_agenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Agente {i}' for i in range(1, 13)],
        'Username': [f'user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}' for i in range(1, 13)],
        'Telefono': ['' for _ in range(12)],
        'Coin_Max': [100000 for _ in range(12)],
        'Coin_Attuali': [50000 for _ in range(12)],
        'Guadagno_E': [0 for _ in range(12)]
    })
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=['Data', 'Agente', 'Euro', 'Coin', 'G_M', 'G_A'])

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.title("🛡️ Taurus Agency Energy Access")
    u, p = st.columns(2)
    user_in = u.text_input("Username")
    pass_in = p.text_input("Password", type="password")
    if st.button("Accedi"):
        if user_in == "TaurusMaster" and pass_in == "Taurus2026":
            st.session_state.auth = {"role": "Master", "user": "Master"}
            st.rerun()
        else:
            match = st.session_state.db_agenti[(st.session_state.db_agenti['Username'] == user_in) & (st.session_state.db_agenti['Password'] == pass_in)]
            if not match.empty:
                st.session_state.auth = {"role": "Agente", "user": user_in, "idx": match.index[0]}
                st.rerun()
    st.stop()

# --- DASHBOARD ---
role = st.session_state.auth['role']

# Barra Superiore Master
if role == "Master":
    st.subheader("🔋 Stato Magazzino Centrale Taurus")
    energy_bar(st.session_state.monete_master_attuali, st.session_state.monete_master_max)
else:
    idx = st.session_state.auth['idx']
    st.subheader(f"🔋 La tua Energia Coin ({st.session_state.db_agenti.at[idx, 'Nome']})")
    energy_bar(st.session_state.db_agenti.at[idx, 'Coin_Attuali'], st.session_state.db_agenti.at[idx, 'Coin_Max'])

st.divider()

# --- MENU MASTER ---
if role == "Master":
    tab1, tab2, tab3 = st.tabs(["👥 Monitoraggio Agenti", "📊 Report Vendite", "📦 Gestione Magazzino"])
    
    with tab1:
        st.write("### Situazione Energia dei 12 Subagenti")
        cols = st.columns(3)
        for i, row in st.session_state.db_agenti.iterrows():
            with cols[i % 3]:
                st.markdown(f"<div class='status-card'>", unsafe_allow_html=True)
                st.write(f"**{row['Nome']}**")
                energy_bar(row['Coin_Attuali'], row['Coin_Max'])
                
                with st.expander("Modifica / Rabbocco"):
                    new_u = st.text_input("User", row['Username'], key=f"u{i}")
                    new_p = st.text_input("Pass", row['Password'], key=f"p{i}")
                    rabbocco = st.number_input("Rabbocco Monete", min_value=0, key=f"r{i}")
                    if st.button("Salva e Invia WhatsApp", key=f"b{i}"):
                        if rabbocco <= st.session_state.monete_master_attuali:
                            st.session_state.monete_master_attuali -= rabbocco
                            st.session_state.db_agenti.at[i, 'Coin_Attuali'] += rabbocco
                            # Aggiorna credenziali
                            st.session_state.db_agenti.at[i, 'Username'] = new_u
                            st.session_state.db_agenti.at[i, 'Password'] = new_p
                            st.success("Rabbocco completato!")
                            st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.write("### Gestione Magazzino Master")
        new_max = st.number_input("Imposta Capacità Massima Magazzino", value=st.session_state.monete_master_max)
        if st.button("Aggiorna Capacità"): st.session_state.monete_master_max = new_max
        
        agg = st.number_input("Aggiungi monete al magazzino attuale", min_value=0)
        if st.button("Carica Magazzino Master"):
            st.session_state.monete_master_attuali += agg
            st.rerun()

# --- AREA VENDITA AGENTE ---
else:
    idx = st.session_state.auth['idx']
    st.subheader("🛒 Punto Vendita Diretta")
    with st.form("vendita"):
        id_sm = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Euro Ricevuti", min_value=1)
        if st.form_submit_button("CONFERMA VENDITA"):
            costo_coin = euro * 91
            if st.session_state.db_agenti.at[idx, 'Coin_Attuali'] >= costo_coin:
                st.session_state.db_agenti.at[idx, 'Coin_Attuali'] -= costo_coin
                st.session_state.db_agenti.at[idx, 'Guadagno_E'] += (euro * 5)
                # Log
                new_v = {'Data': pd.Timestamp.now(), 'Agente': st.session_state.auth['user'], 'Euro': euro, 'Coin': costo_coin, 'G_M': euro*5, 'G_A': euro*5}
                st.session_state.logs = pd.concat([st.session_state.logs, pd.DataFrame([new_v])], ignore_index=True)
                st.balloons()
                st.success(f"Vendita terminata! Hai usato {costo_coin} di energia.")
                st.rerun()
            else:
                st.error("Energia insufficiente! Chiedi un rabbocco a Taurus Master.")

st.sidebar.button("Logout", on_click=lambda: st.session_state.pop('auth'))
