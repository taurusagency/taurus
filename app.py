import streamlit as st
import pandas as pd
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Energy Dashboard", layout="wide")

# --- STILE CSS ---
st.markdown("""
    <style>
    .energy-bar-container { width: 100%; background-color: #e0e0e0; border-radius: 10px; margin: 10px 0; }
    .energy-bar-fill { height: 18px; border-radius: 10px; transition: width 0.5s; }
    .status-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; }
    .wa-button { background-color: #25D366; color: white !important; padding: 10px 20px; border-radius: 10px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE INIZIALE (Reset a Zero) ---
if 'monete_master_attuali' not in st.session_state:
    st.session_state.monete_master_attuali = 4450001
if 'db_agenti' not in st.session_state:
    st.session_state.db_agenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Agente {i}' for i in range(1, 13)],
        'Username': [f'user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}' for i in range(1, 13)],
        'Telefono': ['' for _ in range(12)],
        'Coin_Attuali': [0 for _ in range(12)], # TUTTI A ZERO
        'Coin_Max': [100000 for _ in range(12)]
    })

# --- FUNZIONE BARRA ENERGIA ---
def energy_bar(current, total):
    percent = min(100, max(0, int((current / total) * 100))) if total > 0 else 0
    color = "#28a745" if percent > 40 else "#ffc107" if percent > 15 else "#dc3545"
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 12px;">
            <span>Energia: {percent}%</span>
            <span>{current:,} / {total:,}</span>
        </div>
        <div class="energy-bar-container"><div class="energy-bar-fill" style="width: {percent}%; background-color: {color};"></div></div>
        """, unsafe_allow_html=True)

# --- SISTEMA DI LOGIN ---
if 'auth' not in st.session_state:
    st.title("🛡️ Taurus Agency Login")
    u, p = st.columns(2)
    user_in = u.text_input("Username")
    pass_in = p.text_input("Password", type="password")
    if st.button("Accedi"):
        if user_in == "TaurusMaster" and pass_in == "Taurus2026":
            st.session_state.auth = {"role": "Master"}
            st.rerun()
        # Logica subagente qui...
    st.stop()

# --- DASHBOARD MASTER ---
st.subheader("🔋 Stato Magazzino Centrale Taurus")
energy_bar(st.session_state.monete_master_attuali, 5000000) # Max 5 Milioni

st.divider()

tab1, tab2, tab3 = st.tabs(["👥 Monitoraggio Agenti", "📈 Report Vendite", "📦 Gestione Magazzino"])

with tab1:
    st.write("### Situazione Energia dei 12 Subagenti")
    cols = st.columns(3)
    for i, row in st.session_state.db_agenti.iterrows():
        with cols[i % 3]:
            st.markdown("<div class='status-card'>", unsafe_allow_html=True)
            st.write(f"**{row['Nome']}**")
            energy_bar(row['Coin_Attuali'], row['Coin_Max'])
            
            with st.expander("Modifica / Rabbocco"):
                new_u = st.text_input("User", row['Username'], key=f"u{i}")
                new_p = st.text_input("Pass", row['Password'], key=f"p{i}")
                new_t = st.text_input("Tel WhatsApp (es. 39333...)", row['Telefono'], key=f"t{i}")
                
                col_r1, col_r2 = st.columns(2)
                quantita = col_r1.number_input("Monete", min_value=0, key=f"n{i}")
                azione = col_r2.radio("Azione", ["Aggiungi", "Togli"], key=f"a{i}")
                
                if st.button(f"Conferma Operazione {i+1}", key=f"b{i}"):
                    if azione == "Aggiungi":
                        if st.session_state.monete_master_attuali >= quantita:
                            st.session_state.monete_master_attuali -= quantita
                            st.session_state.db_agenti.at[i, 'Coin_Attuali'] += quantita
                        else: st.error("Monete Master insufficienti!")
                    else:
                        st.session_state.db_agenti.at[i, 'Coin_Attuali'] -= quantita
                        st.session_state.monete_master_attuali += quantita
                    
                    st.session_state.db_agenti.at[i, 'Username'] = new_u
                    st.session_state.db_agenti.at[i, 'Password'] = new_p
                    st.session_state.db_agenti.at[i, 'Telefono'] = new_t
                    st.rerun()

                # --- SEZIONE INVIO WHATSAPP ---
                if new_t:
                    testo = f"Credenziali Taurus:\nUser: {new_u}\nPass: {new_p}\nCarico: {row['Coin_Attuali']}"
                    link_wa = f"https://wa.me/{new_t}?text={urllib.parse.quote(testo)}"
                    st.markdown(f'<a href="{link_wa}" target="_blank" class="wa-button">📲 Invia su WhatsApp</a>', unsafe_allow_html=True)
                    st.code(link_wa, language="text") # Copia di emergenza
            st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.subheader("Gestione Carico Magazzino")
    add_m = st.number_input("Carica monete nel Magazzino Centrale", min_value=0)
    if st.button("Esegui Carico Master"):
        st.session_state.monete_master_attuali += add_m
        st.rerun()

st.sidebar.button("Logout", on_click=lambda: st.session_state.pop('auth'))
