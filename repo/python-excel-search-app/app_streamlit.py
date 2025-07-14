import streamlit as st
import pandas as pd
from src.esamina_excel import esamina_excel, raggruppa_per_lettera_tariffa
import os

st.set_page_config(page_title="Excel Search App", layout="wide")
st.title("Ricerca e filtro Excel - Regione Puglia")

# Caricamento file
uploaded_file = st.file_uploader("Carica file Excel Regione Puglia", type=["xlsx"])

if uploaded_file:
    # Salva temporaneamente il file caricato
    temp_path = os.path.join("data", "temp_uploaded.xlsx")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())
    df = esamina_excel(temp_path)
    if df is not None and not df.empty:
        st.success(f"{len(df)} record caricati.")
        # Filtro per lettera tariffa
        gruppi = raggruppa_per_lettera_tariffa(df)
        lettere = sorted([l for l in gruppi.keys() if l])
        lettera_sel = st.sidebar.selectbox("Filtra per lettera tariffa", ["Tutte"] + lettere)
        if lettera_sel != "Tutte":
            df = gruppi[lettera_sel]
        # Ricerca testo
        search = st.text_input("Cerca testo (su tutte le colonne)")
        if search:
            mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False, na=False).any(), axis=1)
            df = df[mask]
        st.write(f"Totale risultati: {len(df)}")
        st.dataframe(df, use_container_width=True)
        # Download risultati
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Scarica risultati filtrati (CSV)", csv, "risultati_filtrati.csv", "text/csv")
    else:
        st.warning("Nessun dato trovato nel file caricato.")
else:
    st.info("Carica un file Excel per iniziare.")
