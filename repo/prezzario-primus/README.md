# 🏛️ Portale Tariffe Regione Puglia

Un'applicazione web Streamlit per ricercare, filtrare e organizzare le tariffe della Regione Puglia contenute in file Excel.

## Caratteristiche

- **🔍 Ricerca avanzata**: Filtra per categoria e cerca testo su tutte le colonne o colonne specifiche
- **🌳 Vista gerarchica**: Le voci sono organizzate in nodi espandibili (codice base → varianti)
- **📚 Elenco personalizzato**: Seleziona e salva le voci di interesse
- **🗂️ Gestione categorie**: Organizza le voci selezionate in categorie personalizzate
- **📥 Download**: Scarica i risultati in formato CSV
- **⚡ Ottimizzazioni**: Ricerca veloce con debounce e paginazione

## Struttura del progetto

```
├── app_streamlit.py        # Applicazione web Streamlit principale
├── src/
│   └── esamina_excel.py   # Funzioni per leggere e processare file Excel
├── data/                  # Directory per i file Excel
├── requirements.txt       # Dipendenze Python
└── README.md             # Documentazione
```

## Installazione

1. Clona il repository:
```bash
git clone <repository-url>
cd python-excel-search-app
```

2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

## Utilizzo

1. Avvia l'applicazione Streamlit:
```bash
streamlit run app_streamlit.py
```

2. Apri il browser all'indirizzo mostrato (solitamente http://localhost:8501)

3. Carica un file Excel della Regione Puglia

4. Utilizza le funzionalità:
   - **Ricerca voci**: Filtra per categoria, cerca testo, seleziona voci
   - **Il mio elenco**: Organizza le voci selezionate in categorie

## Formato file Excel supportato

Il file Excel deve contenere:
- Foglio denominato "Elenco Prezzi"
- Colonne: TARIFFA, DESCRIZIONE dell'ARTICOLO, Unità di misura, Prezzo
- Codici tariffa nel formato PUG2025/01.E01.001.XXX

## Dipendenze

- **streamlit**: Framework web per l'interfaccia utente
- **pandas**: Manipolazione e analisi dati
- **openpyxl**: Lettura file Excel
- **numpy**: Calcoli numerici ottimizzati
