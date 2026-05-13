import streamlit as st
import pandas as pd

# Configurazione della pagina
st.set_page_config(page_title="Taurus Agency Management", layout="wide")

# Titolo principale
st.title("🐂 Taurus Agency - Dashboard Ufficiale")

# Sidebar per la navigazione
menu = ["Home", "Gestione Monete", "Analisi Guadagni", "Supporto"]
choice = st.sidebar.selectbox("Menu Navigazione", menu)

if choice == "Home":
    st.subheader("Benvenuto nella gestione Taurus Agency")
    st.write("Usa il menu a sinistra per gestire le tue attività su StarMaker.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Stato Agenzia", "Attiva")
    col2.metric("Lingue Supportate", "FR, IT, EN, DE")
    col3.metric("Piattaforma", "StarMaker")

elif choice == "Gestione Monete":
    st.subheader("Modulo Vendita Monete")
    st.info("Inserisci i dati della transazione qui sotto.")
    
    user_id = st.text_input("ID Utente StarMaker")
    amount = st.number_input("Quantità Monete", min_value=0)
    price = st.number_input("Prezzo Concordato (€)", min_value=0.0, format="%.2f")
    
    if st.button("Registra Transazione"):
        st.success(f"Transazione di {amount} monete per l'utente {user_id} registrata con successo!")

elif choice == "Analisi Guadagni":
    st.subheader("Monitoraggio Profitto")
    # Esempio di tabella dati
    data = {
        'Data': ['2026-05-10', '2026-05-12', '2026-05-14'],
        'Vendite (€)': [150.00, 230.50, 180.00]
    }
    df = pd.DataFrame(data)
    st.line_chart(df.set_index('Data'))
    st.table(df)

elif choice == "Supporto":
    st.subheader("Centro Assistenza Multilingua")
    st.write("Seleziona la lingua per i template di risposta:")
    lang = st.radio("Lingua", ("Italiano", "Français", "English", "Deutsch"))
    
    if lang == "Italiano":
        st.code("Salve! Come posso aiutarla con l'acquisto di monete Taurus?")
    elif lang == "Français":
        st.code("Bonjour! Comment puis-je vius aider con l'achat de pièces Taurus?")
