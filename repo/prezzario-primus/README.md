# 🏛️ Portale Tariffe Regione Puglia

Un'applicazione web Streamlit per ricercare, filtrare e organizzare le tariffe della Regione Puglia contenute in file Excel. **I dati vengono salvati localmente sul dispositivo dell'utente**, garantendo privacy e portabilità.

## Caratteristiche

- **🔍 Ricerca avanzata**: Filtra per categoria e cerca testo su tutte le colonne o colonne specifiche
- **🌳 Vista gerarchica**: Le voci sono organizzate in nodi espandibili (codice base → varianti)
- **📚 Elenco personalizzato**: Seleziona e salva le voci di interesse
- **🗂️ Gestione categorie**: Organizza le voci selezionate in categorie personalizzate
- **� Salvataggio locale**: I dati vengono salvati automaticamente nel browser (LocalStorage)
- **�📥 Download backup**: Scarica i risultati in formato JSON per backup
- **📤 Caricamento backup**: Ripristina lavori precedenti da file JSON
- **⚡ Ottimizzazioni**: Ricerca veloce con debounce e paginazione

## Gestione Dati Locale

### Salvataggio Automatico
- I dati vengono salvati automaticamente nel browser ogni volta che aggiungi voci o crei categorie
- Non è necessario alcun server di backend per salvare i tuoi dati
- I dati persistono tra le sessioni del browser

### Backup e Ripristino
- **Download Backup**: Scarica il tuo lavoro come file JSON sul tuo dispositivo
- **Caricamento Backup**: Carica un file JSON precedentemente scaricato per ripristinare il lavoro
- **Ripristino Automatico**: Ripristina automaticamente l'ultimo stato dal browser
- **Gestione Cache**: Pulisci i dati salvati nel browser quando necessario

### Privacy e Sicurezza
- **Nessun salvataggio su server**: Tutti i dati rimangono sul tuo dispositivo
- **Controllo totale**: Puoi cancellare o esportare i tuoi dati in qualsiasi momento
- **Portabilità**: Porta i tuoi dati su altri dispositivi tramite file di backup

## Struttura del progetto

```
├── app_streamlit.py        # Applicazione web Streamlit principale
├── src/
│   └── esamina_excel.py   # Funzioni per leggere e processare file Excel
├── data/                  # Directory per file Excel di esempio (opzionale)
├── requirements.txt       # Dipendenze Python
└── README.md             # Documentazione
```

## Installazione

1. Clona il repository:
```bash
git clone <repository-url>
cd prezzario-primus
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
   - **Impostazioni**: Gestisci backup e categorie personalizzate

## Formato file Excel supportato

Il file Excel deve contenere:
- Foglio denominato "Elenco Prezzi"
- Colonne: TARIFFA, DESCRIZIONE dell'ARTICOLO, Unità di misura, Prezzo
- Codici tariffa nel formato PUG2025/01.E01.001.XXX

## Funzionalità Web

### Gestione File
- **Caricamento temporaneo**: I file Excel vengono processati temporaneamente senza essere salvati sul server
- **Sicurezza**: Nessun file rimane permanentemente sul server
- **Efficienza**: Processamento rapido e immediato dei dati

### Persistenza Dati
- **LocalStorage**: Utilizza il localStorage del browser per salvare automaticamente il lavoro
- **JSON Export/Import**: Formato standard per backup e condivisione
- **Cross-device**: Sincronizza il lavoro tra dispositivi tramite file di backup

## Dipendenze

- **streamlit**: Framework web per l'interfaccia utente
- **pandas**: Manipolazione e analisi dati
- **openpyxl**: Lettura file Excel
- **numpy**: Calcoli numerici ottimizzati

## Note per la Distribuzione Web

Questa applicazione è ottimizzata per il deployment su servizi cloud come:
- Streamlit Cloud
- Heroku
- Railway
- Google Cloud Run
- AWS ECS

Tutti i dati utente vengono gestiti lato client, eliminando la necessità di database o storage persistente sul server.
