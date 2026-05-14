import streamlit as st
import pandas as pd
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Magazzino Real-Time", layout="wide")

# --- STILE CSS ---
st.markdown("""
    <style>
    .energy-bar-container { width: 100%; background-color: #e0e0e0; border-radius: 10px; margin: 10px 0; }
    .energy-bar-fill { height: 18px; border-radius: 10px; transition: width 0.5s; }
    .status-card { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 20px; }
    .wa-button { background-color: #25D366; color: white !important; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 14px; }
    .master-card { background: #1E1E1E; color: white; padding: 20px; border-radius: 15px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE INIZIALE ---
if 'magazzino_master' not in st.session_state:
    st.session_state.magazzino_master = 0  # PARTE A ZERO COME RICHIESTO
if 'db_agenti' not in st.session_state:
    st.session_state.db_agenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Agente {i}' for i in range(1, 13)],
        'Username': [f'user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}' for i in range(1, 13)],
        'Telefono': ['' for _ in range(12)],
        'Coin_Attuali': [0 for _ in range(12)]
    })

# --- FUNZIONE BARRA ENERGIA ---
def energy_bar(current, max_val, label="Energia"):
    percent = min(100, max(0, int((current / max_val) * 100))) if max_val > 0 else 0
    color = "#28a745" if percent > 40 else "#ffc107" if percent > 15 else "#dc3545"
    st.markdown(f"""
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top:10px;">
            <span>{label}: {percent}%</span>
            <span>{current:,} Coin</span>
        </div>
        <div class="energy-bar-container"><div class="energy-bar-fill" style="width: {percent}%; background-color: {color};"></div></div>
        """, unsafe_allow_html=True)

# --- LOGIN ---
if 'auth' not in st.session_state:
    st.title("🛡️ Taurus Agency Login")
    u, p = st.columns(2)
    user_in = u.text_input("Username")
    pass_in = p.text_input("Password", type="password")
    if st.button("Accedi"):
        if user_in == "TaurusMaster" and pass_in == "Taurus2026":
            st.session_state.auth = {"role": "Master"}
            st.rerun()
    st.stop()

# --- DASHBOARD MASTER ---
st.markdown(f"""
    <div class="master-card">
        <h1 style='margin:0; color: #FFD700;'>🐂 TAURUS MASTER CONTROL</h1>
        <p style='margin:0; opacity: 0.8;'>Gestione Magazzino Centrale e Subagenti</p>
    </div>
    """, unsafe_allow_html=True)

# Sezione Magazzino Centrale (Modificabile)
col_m1, col_m2 = st.columns([2, 1])
with col_m1:
    st.markdown("### 🏦 Stato Magazzino Centrale")
    # Usiamo 10 Milioni come scala massima puramente estetica per la barra
    energy_bar(st.session_state.magazzino_master, 10000000, label="Giacenza Centrale")

with col_m2:
    st.markdown("### ⚙️ Regola Magazzino")
    val_m = st.number_input("Quantità Coin", min_value=0, step=10000, key="master_val")
    cm1, cm2 = st.columns(2)
    if cm1.button("➕ Carica", use_container_width=True):
        st.session_state.magazzino_master += val_m
        st.rerun()
    if cm2.button("➖ Scarica", use_container_width=True):
        st.session_state.magazzino_master -= val_m
        st.rerun()

st.divider()

# --- MONITORAGGIO AGENTI ---
st.markdown("### 👥 Gestione Subagenti (Vasi Comunicanti)")
cols = st.columns(3)

for i, row in st.session_state.db_agenti.iterrows():
    with cols[i % 3]:
        st.markdown("<div class='status-card'>", unsafe_allow_html=True)
        st.write(f"**{row['Nome']}**")
        energy_bar(row['Coin_Attuali'], 500000, label="Budget Agente")
        
        with st.expander("Gestisci Credenziali e Monete"):
            # Credenziali
            new_u = st.text_input("Username", row['Username'], key=f"u{i}")
            new_p = st.text_input("Password", row['Password'], key=f"p{i}")
            new_t = st.text_input("WhatsApp (es. 39333...)", row['Telefono'], key=f"t{i}")
            
            st.divider()
            
            # Movimento Monete (Tutto collegato al magazzino master)
            quantita = st.number_input("Quantità da spostare", min_value=0, key=f"n{i}")
            b1, b2 = st.columns(2)
            
            if b1.button(f"⬆️ Dai Monete", key=f"give{i}"):
                if st.session_state.magazzino_master >= quantita:
                    st.session_state.magazzino_master -= quantita
                    st.session_state.db_agenti.at[i, 'Coin_Attuali'] += quantita
                    st.session_state.db_agenti.at[i, 'Username'] = new_u
                    st.session_state.db_agenti.at[i, 'Password'] = new_p
                    st.session_state.db_agenti.at[i, 'Telefono'] = new_t
                    st.success(f"Trasferiti {quantita} coin!")
                    st.rerun()
                else:
                    st.error("Magazzino Master insufficiente!")

            if b2.button(f"⬇️ Togli Monete", key=f"take{i}"):
                if st.session_state.db_agenti.at[i, 'Coin_Attuali'] >= quantita:
                    st.session_state.db_agenti.at[i, 'Coin_Attuali'] -= quantita
                    st.session_state.magazzino_master += quantita
                    st.success(f"Recuperati {quantita} coin!")
                    st.rerun()
                else:
                    st.error("L'agente non ha abbastanza monete!")
            
            # Invio WhatsApp
            if new_t:
                testo = f"Ciao {row['Nome']}, ecco i tuoi dati Taurus:\n👤 User: {new_u}\n🔑 Pass: {new_p}\n🔋 Saldo: {st.session_state.db_agenti.at[i, 'Coin_Attuali']}"
                link_wa = f"https://wa.me/{new_t}?text={urllib.parse.quote(testo)}"
                st.markdown(f'<a href="{link_wa}" target="_blank" class="wa-button">📲 Invia Credenziali</a>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

st.sidebar.button("Logout", on_click=lambda: st.session_state.pop('auth'))
