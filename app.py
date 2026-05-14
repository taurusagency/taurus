import streamlit as st
import pandas as pd
import plotly.express as px
import urllib.parse

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Taurus Agency - Gestione Integrata", layout="wide")

# --- DATABASE IN MEMORIA ---
if 'monete_master' not in st.session_state:
    st.session_state.monete_master = 1000000
if 'db_agenti' not in st.session_state:
    st.session_state.db_agenti = pd.DataFrame({
        'ID': range(1, 13),
        'Nome': [f'Agente {i}' for i in range(1, 13)],
        'Username': [f'user{i}' for i in range(1, 13)],
        'Password': [f'pass{i}' for i in range(1, 13)],
        'Telefono': ['' for _ in range(12)],
        'Budget_Monete': [0 for _ in range(12)],
        'Guadagno_Accumulato': [0 for _ in range(12)]
    })
if 'log_vendite' not in st.session_state:
    st.session_state.log_vendite = pd.DataFrame(columns=['Data', 'Agente', 'ID_StarMaker', 'Euro', 'Coins', 'G_Master', 'G_Agente'])

# --- SISTEMA DI LOGIN ---
if 'auth' not in st.session_state:
    st.title("🛡️ Accesso Riservato Taurus Agency")
    col_l, col_r = st.columns(2)
    user_in = col_l.text_input("Username")
    pass_in = col_r.text_input("Password", type="password")
    
    if st.button("Entra nell'Area Operativa"):
        if user_in == "TaurusMaster" and pass_in == "Taurus2026":
            st.session_state.auth = {"role": "Master", "user": "Master"}
            st.rerun()
        else:
            agente_match = st.session_state.db_agenti[
                (st.session_state.db_agenti['Username'] == user_in) & 
                (st.session_state.db_agenti['Password'] == pass_in)
            ]
            if not agente_match.empty:
                st.session_state.auth = {"role": "Agente", "user": user_in, "idx": agente_match.index[0]}
                st.rerun()
            else:
                st.error("Credenziali non valide.")
    st.stop()

# --- INTERFACCIA POST-LOGIN ---
role = st.session_state.auth['role']

# Statistiche in tempo reale in alto
st.markdown(f"### 🐂 Dashboard {role}: {st.session_state.auth['user']}")
c1, c2, c3, c4 = st.columns(4)

if role == "Master":
    c1.metric("Cassaforte Master", f"{st.session_state.monete_master:,} 🪙")
    c2.metric("Guadagno Agenzia", f"{st.session_state.log_vendite['G_Master'].sum():,} 🪙")
    c3.metric("Euro Totali", f"{st.session_state.log_vendite['Euro'].sum()} €")
    c4.button("Esci", on_click=lambda: st.session_state.pop('auth'))
else:
    idx = st.session_state.auth['idx']
    c1.metric("Il Tuo Budget", f"{st.session_state.db_agenti.at[idx, 'Budget_Monete']:,} 🪙")
    c2.metric("Il Tuo Guadagno", f"{st.session_state.db_agenti.at[idx, 'Guadagno_Accumulato']:,} 🪙")
    c4.button("Esci", on_click=lambda: st.session_state.pop('auth'))

st.divider()

# --- NAVIGAZIONE ---
if role == "Master":
    tab1, tab2, tab3 = st.tabs(["👥 Gestione Subagenti", "📈 Report Vendite", "💰 Cassaforte Master"])
    
    with tab1:
        st.subheader("Controllo e Invio Credenziali WhatsApp")
        for i, row in st.session_state.db_agenti.iterrows():
            with st.expander(f"⚙️ Configura {row['Nome']}"):
                col_u, col_p, col_t, col_r = st.columns(4)
                new_u = col_u.text_input("Username", row['Username'], key=f"u{i}")
                new_p = col_p.text_input("Password", row['Password'], key=f"p{i}")
                new_t = col_t.text_input("WhatsApp (es. 39333...)", row['Telefono'], key=f"t{i}")
                rabbocco = col_r.number_input("Rabbocco Monete", min_value=0, key=f"r{i}")
                
                if st.button(f"Salva e Invia a {row['Nome']}", key=f"b{i}"):
                    if rabbocco <= st.session_state.monete_master:
                        st.session_state.monete_master -= rabbocco
                        st.session_state.db_agenti.at[i, 'Budget_Monete'] += rabbocco
                        st.session_state.db_agenti.at[i, 'Username'] = new_u
                        st.session_state.db_agenti.at[i, 'Password'] = new_p
                        st.session_state.db_agenti.at[i, 'Telefono'] = new_t
                        
                        # Link WhatsApp
                        testo = f"Ciao {row['Nome']}, credenziali Taurus:\nUser: {new_u}\nPass: {new_p}\nCarico: {rabbocco}\nAccedi: https://taurus-app-finale.streamlit.app"
                        url_wa = f"https://wa.me/{new_t}?text={urllib.parse.quote(testo)}"
                        st.markdown(f"**[CLICCA QUI PER INVIARE SU WHATSAPP]({url_wa})**")
                        st.success("Dati aggiornati!")
                    else:
                        st.error("Monete Master insufficienti!")

    with tab3:
        st.subheader("Gestione Monete Master")
        val = st.number_input("Quantità da caricare/scaricare", min_value=0)
        col_m1, col_m2 = st.columns(2)
        if col_m1.button("➕ Aggiungi al Totale"):
            st.session_state.monete_master += val
            st.rerun()
        if col_m2.button("➖ Sottrai dal Totale"):
            st.session_state.monete_master -= val
            st.rerun()

else: # --- AREA AGENTE ---
    st.subheader("🚀 Punto Vendita Diretta")
    with st.form("vendita_diretta"):
        idx = st.session_state.auth['idx']
        st.write(f"Budget disponibile: **{st.session_state.db_agenti.at[idx, 'Budget_Monete']:,} 🪙**")
        id_sm = st.text_input("ID StarMaker Cliente")
        euro = st.number_input("Euro Ricevuti", min_value=1)
        
        if st.form_submit_button("CONFERMA VENDITA"):
            coins_da_scalare = euro * 91
            if st.session_state.db_agenti.at[idx, 'Budget_Monete'] >= coins_da_scalare:
                # Esecuzione Vendita
                st.session_state.db_agenti.at[idx, 'Budget_Monete'] -= coins_da_scalare
                st.session_state.db_agenti.at[idx, 'Guadagno_Accumulato'] += (euro * 5)
                
                # Log per il Master
                nuova_v = {
                    'Data': pd.Timestamp.now().strftime("%d/%m %H:%M"),
                    'Agente': st.session_state.auth['user'],
                    'ID_StarMaker': id_sm,
                    'Euro': euro,
                    'Coins': coins_da_scalare,
                    'G_Master': euro * 5,
                    'G_Agente': euro * 5
                }
                st.session_state.log_vendite = pd.concat([st.session_state.log_vendite, pd.DataFrame([nuova_v])], ignore_index=True)
                st.balloons()
                st.success(f"Vendita completata! Consegnati {coins_da_scalare} coins a {id_sm}")
            else:
                st.error("Non hai abbastanza monete nel tuo budget per questa vendita!")

    st.subheader("📜 Le mie ultime vendite")
    mie_v = st.session_state.log_vendite[st.session_state.log_vendite['Agente'] == st.session_state.auth['user']]
    st.table(mie_v)

