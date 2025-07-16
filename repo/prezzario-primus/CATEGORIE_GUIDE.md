# 📋 Sistema di Categorie Gerarchiche - Guida Completa

## 🎯 Panoramica

Il sistema di categorie gerarchiche è un'estensione avanzata del Prezzario Primus che permette di organizzare le tariffe in una struttura ad albero personalizzabile con massimo 3 livelli di profondità.

### ✨ Caratteristiche Principali

- **Sintassi Intuitiva**: Usa virgole e parentesi per definire la struttura
- **Validazione Completa**: Controllo automatico degli errori di sintassi
- **Numerazione Automatica**: Sistema di numerazione gerarchica (1, 1.1, 1.1.1)
- **Export/Import**: Salvataggio e caricamento in formato JSON
- **Integrazione Seamless**: Perfettamente integrato nell'interfaccia esistente

## 🚀 Come Usare

### 1. Accesso al Sistema

1. Avvia l'applicazione: `streamlit run app_streamlit.py`
2. Carica un file Excel con le tariffe nel tab **⚙️ Impostazioni**
3. Vai al tab **📋 Categorie** per gestire le categorie gerarchiche

### 2. Sintassi delle Categorie

#### Regole di Base
- **Virgole** `,` → separano categorie allo stesso livello
- **Parentesi** `()` → creano sotto-livelli
- **Massimo 3 livelli**: 0 (principale), 1 (sottocategoria), 2 (sotto-sottocategoria)

#### Esempi Pratici

```
# Categorie semplici (livello 0)
Edilizia, Impianti, Finiture

# Con un livello di sotto-categorie
Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici)

# Con due livelli di annidamento
Costruzioni (Fondazioni (Scavi, Pali), Strutture (Pilastri, Travi))

# Esempio complesso realistico
Impianti (Elettrici (Illuminazione, Cablaggio), Idraulici (Tubazioni, Raccordi)), Finiture (Pavimenti, Rivestimenti)
```

### 3. Risultato Visivo

Il sistema genera automaticamente una struttura numerata:

```
1. 📁 Edilizia
   1.1. 📂 Murature
        1.1.1. 📄 Mattoni
        1.1.2. 📄 Malte
   1.2. 📂 Intonaci
2. 📁 Impianti
   2.1. 📂 Elettrici
   2.2. 📂 Idraulici
```

## 🔧 Funzionalità Avanzate

### Validazione Automatica

Il sistema controlla automaticamente:
- ✅ Parentesi bilanciate
- ✅ Virgole non consecutive
- ✅ Parentesi non vuote
- ✅ Livelli di annidamento corretti
- ✅ Nomi categorie validi

### Export/Import

- **Export JSON**: Salva le categorie in formato strutturato
- **Import JSON**: Carica categorie da file precedentemente esportati
- **Backup Automatico**: Le categorie sono salvate nel browser

### Integrazione con Dati Esistenti

Il sistema si integra con:
- **Categorie Tradizionali**: Mostra le categorie estratte dalle tariffe
- **Filtri Avanzati**: Applica filtri basati sulla nuova struttura
- **Export Personalizzato**: Organizza l'export secondo la gerarchia

## 🏗️ Struttura Tecnica

### File del Sistema

```
src/utils/
├── __init__.py              # Pacchetto utils
├── category_parser.py       # Logica di parsing e validazione
└── category_ui.py          # Componenti Streamlit

tests/
├── test_category_system.py  # Test funzionalità base
└── test_integration.py     # Test integrazione
```

### Funzioni Principali

#### `category_parser.py`
- `parse_categories_from_text()` - Parsing della sintassi
- `validate_category_syntax()` - Validazione input
- `generate_hierarchical_numbering()` - Numerazione automatica
- `export_categories_to_dict()` - Export JSON
- `import_categories_from_dict()` - Import JSON

#### `category_ui.py`
- `render_category_management_page()` - Interfaccia completa
- `render_category_input()` - Input categorie
- `display_current_categories()` - Visualizzazione
- `get_categories_for_dataframe_mapping()` - Integrazione dati

## 🧪 Test e Qualità

### Eseguire i Test

```bash
# Test funzionalità base
python tests/test_category_system.py

# Test integrazione
python tests/test_integration.py

# Verifica sintassi app principale
python -m py_compile app_streamlit.py
```

### Copertura Test

Il sistema include test per:
- ✅ Validazione sintassi (10 casi)
- ✅ Parsing base (3 scenari)
- ✅ Parsing annidato (4 scenari complessi)
- ✅ Numerazione gerarchica
- ✅ Export/Import JSON
- ✅ Casi limite (6 edge cases)
- ✅ Integrazione Streamlit

## 📊 Esempi d'Uso Reali

### Caso 1: Edilizia Residenziale
```
Strutture (Fondazioni (Scavi, Pilastri), Murature (Portanti, Tamponature)), 
Impianti (Elettrici (Illuminazione, Prese), Idraulici (Acqua, Scarichi)), 
Finiture (Pavimenti (Ceramica, Parquet), Rivestimenti (Bagni, Cucine))
```

### Caso 2: Infrastrutture
```
Movimento Terra (Scavi (Generali, Fondazioni), Riporti), 
Pavimentazioni (Stradali (Asfalto, Calcestruzzo), Pedonali), 
Opere d'Arte (Ponti, Gallerie)
```

### Caso 3: Restauro
```
Consolidamento (Strutturale (Murature, Volte), Superfici), 
Pulitura (Chimica, Meccanica), 
Protezione (Impermeabilizzazioni, Trattamenti)
```

## 🎛️ Configurazione e Personalizzazione

### Limiti Personalizzabili
- **Max livelli**: Modificabile in `category_parser.py` (default: 3)
- **Max lunghezza**: Controllo automatico per performance
- **Caratteri speciali**: Personalizzabile tramite regex

### Stili Visuali
- **Icone**: 📁 (livello 0), 📂 (livello 1), 📄 (livello 2)
- **Indentazione**: Spazi wide Unicode per allineamento
- **Numerazione**: Formato x.y.z automatico

## 🔍 Risoluzione Problemi

### Errori Comuni

**❌ "Parentesi non bilanciate"**
```
Sbagliato: Edilizia (Murature
Corretto:  Edilizia (Murature)
```

**❌ "Virgole consecutive"**
```
Sbagliato: Edilizia,, Impianti
Corretto:  Edilizia, Impianti
```

**❌ "Troppi livelli"**
```
Sbagliato: A (B (C (D)))
Corretto:  A (B (C))
```

### Log e Debug

Il sistema fornisce:
- ✅ Messaggi di errore dettagliati
- ✅ Warnings per best practices
- ✅ Contatori statistiche
- ✅ Preview struttura prima del salvataggio

## 🚀 Prossimi Sviluppi

### Funzionalità Future
- [ ] Import da Excel con struttura gerarchica
- [ ] Template predefiniti per settori specifici
- [ ] Drag & drop per riorganizzare categorie
- [ ] Ricerca full-text nelle categorie
- [ ] Analisi statistiche avanzate per categoria

### Integrazioni Pianificate
- [ ] Export in formato PDF strutturato
- [ ] API REST per integrazione esterna
- [ ] Sincronizzazione cloud
- [ ] Versioning delle categorie

---

## 📞 Supporto

Per problemi o domande:
1. Controlla i log di errore nell'interfaccia
2. Esegui i test di sistema: `python tests/test_category_system.py`
3. Verifica la sintassi con gli esempi sopra
4. Consulta i messaggi di validazione in tempo reale

**Sistema sviluppato per Prezzario Primus - Luglio 2025**
