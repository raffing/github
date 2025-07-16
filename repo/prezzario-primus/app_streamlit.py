import json
import base64
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import os
import re
from src.esamina_excel import esamina_excel, raggruppa_per_lettera_tariffa, crea_struttura_gerarchica

# COSTANTI GLOBALI
CATEGORIE_MAP = {
    '01': '01 - Edilizia',
    '02': '02 - Restauro e opere di recupero',
    '03': '03 - Infrastrutture',
    '04': '04 - Impianti elettrici',
    '05': '05 - Impianti di adduzione idrica e di scarico',
    '06': '06 - Impianti antincendio',
    '07': '07 - Impianti termici',
    '08': '08 - Fognature ed acquedotti',
    '09': '09 - Sicurezza in azienda e in cantiere',
    '10': '10 - Opere marittime',
    '11': '11 - Impianti sportivi',
    '12': '12 - Igiene ambientale',
    '13': '13 - Opere idrauliche e di bonifica e consolidamento',
    '14': '14 - Opere forestali',
    '15': '15 - Sondaggi e prove',
    '16': '16 - Opere a verde e irrigazione',
    '17': '17 - Arredo urbano e parco giochi'
}

# FUNZIONI UTILITY
def estrai_categoria(tariffa):
    """Estrae il numero di categoria da una tariffa"""
    if pd.isna(tariffa):
        return None
    
    # Prova diversi pattern per estrarre la categoria
    patterns = [
        r'/(\d{2})\.',  # /01. /02. etc.
        r'\.(\d{2})\.',  # .01. .02. etc.
        r'(\d{2})\.',   # 01. 02. etc. (all'inizio)
        r'/(\d{1,2})\.',  # /1. /01. etc. (più flessibile)
    ]
    
    for pattern in patterns:
        match = re.search(pattern, str(tariffa))
        if match:
            numero_cat = match.group(1).zfill(2)  # Assicura 2 cifre (01, 02, etc.)
            categoria = CATEGORIE_MAP.get(numero_cat, f"Categoria {numero_cat}")
            return categoria
    
    return None

def get_categoria_from_tariffa(tariffa):
    """Estrae solo il numero di categoria da una tariffa"""
    if pd.isna(tariffa):
        return None
    
    patterns = [
        r'/(\d{2})\.',
        r'\.(\d{2})\.',
        r'(\d{2})\.',
        r'/(\d{1,2})\.',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, str(tariffa))
        if match:
            return match.group(1).zfill(2)
    
    return None

def aggiungi_categoria_estesa(df):
    """Aggiunge la colonna CATEGORIA_ESTESA se non esiste"""
    if 'CATEGORIA_ESTESA' not in df.columns:
        # Prima di applicare la funzione, mostra alcuni esempi di tariffe per debug
        print("Debug: Prime 10 tariffe nel dataset:")
        print(df['TARIFFA'].head(10).tolist())
        
        df['CATEGORIA_ESTESA'] = df['TARIFFA'].apply(estrai_categoria)
        
        # Verifica quante categorie sono state estratte
        categorie_trovate = df['CATEGORIA_ESTESA'].value_counts()
        print("Debug: Categorie estratte:")
        print(categorie_trovate)
        
    return df

def group_results_by_category(df_batch):
    """Raggruppa i risultati per categoria"""
    groups = {}
    for _, row in df_batch.iterrows():
        categoria_num = get_categoria_from_tariffa(row['TARIFFA'])
        if categoria_num:
            categoria_nome = CATEGORIE_MAP.get(categoria_num, f"Categoria {categoria_num}")
        else:
            categoria_nome = "Senza Categoria"
        if categoria_nome not in groups:
            groups[categoria_nome] = []
        groups[categoria_nome].append(row)
    return groups

# JavaScript per gestire il local storage
LOCAL_STORAGE_JS = """
<script>
// Funzioni per gestire il local storage
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (e) {
        console.error('Errore nel salvataggio:', e);
        return false;
    }
}

function loadFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Errore nel caricamento:', e);
        return null;
    }
}

function deleteFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('Errore nella cancellazione:', e);
        return false;
    }
}

// Funzione per scaricare dati come file JSON
function downloadJSON(data, filename) {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Esponi le funzioni a Streamlit
window.localStorageHelpers = {
    save: saveToLocalStorage,
    load: loadFromLocalStorage,
    delete: deleteFromLocalStorage,
    download: downloadJSON
};
</script>
"""

# Funzione di autosalvataggio in localStorage
def auto_save_work_state():
    work_state = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'custom_categories': st.session_state.get('custom_categories', []),
        'selected_rows': st.session_state.get('selected_rows', []),
        'version': '1.1'  # Incrementata la versione per il nuovo formato
    }
    
    # Salva in session state per poter essere utilizzato da JavaScript
    st.session_state['auto_save_data'] = work_state
    
    # Inietta JavaScript per salvare nel localStorage
    components.html(f"""
    {LOCAL_STORAGE_JS}
    <script>
    if (window.localStorageHelpers) {{
        const success = window.localStorageHelpers.save('prezzario_autosave', {json.dumps(work_state)});
        if (success) {{
            console.log('Autosalvataggio completato');
        }}
    }}
    </script>
    """, height=0)

# Funzione per preparare il download del lavoro
def prepare_work_download():
    """Prepara i dati per il download come file JSON"""
    work_state = {
        'timestamp': datetime.now().isoformat(),
        'custom_categories': st.session_state.get('custom_categories', []),
        'selected_rows': st.session_state.get('selected_rows', []),
        'version': '1.1'
    }
    
    # Crea il nome del file
    filename = f"lavoro_tariffe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # Converte in JSON per il download
    json_str = json.dumps(work_state, ensure_ascii=False, indent=2)
    
    return json_str, filename

# Funzione di caricamento backup (ora non più utilizzata)
def try_load_autosave():
    # Questa funzione ora utilizza JavaScript per caricare dal localStorage
    # Restituisce sempre False per disabilitare il caricamento automatico
    return False, None

# Funzione di test per debug categorie
def test_estrazione_categorie(df):
    """Funzione di test per verificare l'estrazione delle categorie"""
    if df is not None and not df.empty:
        st.write("### 🔍 Debug Estrazione Categorie")
        
        # Mostra alcuni esempi di tariffe
        esempi_tariffe = df['TARIFFA'].head(10).tolist()
        st.write("**Esempi di tariffe nel dataset:**")
        for i, tariffa in enumerate(esempi_tariffe, 1):
            categoria = estrai_categoria(tariffa)
            st.write(f"{i}. `{tariffa}` → `{categoria}`")
        
        # Mostra il conteggio delle categorie
        if 'CATEGORIA_ESTESA' in df.columns:
            conteggio = df['CATEGORIA_ESTESA'].value_counts()
            st.write("**Conteggio categorie estratte:**")
            st.write(conteggio)
        
        # Mostra le righe senza categoria
        senza_categoria = df[df['CATEGORIA_ESTESA'].isna()]
        if not senza_categoria.empty:
            st.write(f"**Righe senza categoria ({len(senza_categoria)}):**")
            st.write(senza_categoria[['TARIFFA', 'DESCRIZIONE']].head())


st.set_page_config(page_title="Portale Tariffe Regione Puglia", layout="wide")

# Inizializzazione session state
if 'selected_rows' not in st.session_state:
    st.session_state['selected_rows'] = []
if 'file_loaded' not in st.session_state:
    st.session_state['file_loaded'] = False
if 'custom_categories' not in st.session_state:
    st.session_state['custom_categories'] = []
if 'selected_custom_category' not in st.session_state:
    st.session_state['selected_custom_category'] = None

def save_work_state():
    """Prepara i dati per il download come file JSON"""
    work_state = {
        'timestamp': datetime.now().isoformat(),
        'custom_categories': st.session_state['custom_categories'],
        'selected_rows': st.session_state['selected_rows'],
        'version': '1.1'
    }
    
    filename = f"lavoro_tariffe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_str = json.dumps(work_state, ensure_ascii=False, indent=2)
    
    return json_str, filename

def load_work_state(uploaded_work_file):
    """Carica lo stato del lavoro da un file JSON"""
    import json
    
    try:
        work_data = json.loads(uploaded_work_file.read().decode('utf-8'))
        
        # Valida la struttura
        if 'custom_categories' in work_data and 'selected_rows' in work_data:
            st.session_state['custom_categories'] = work_data['custom_categories']
            st.session_state['selected_rows'] = work_data['selected_rows']
            return True, f"Caricato lavoro del {work_data.get('timestamp', 'data sconosciuta')}"
        else:
            return False, "File di lavoro non valido"
    except Exception as e:
        return False, f"Errore nel caricamento: {str(e)}"

# Header condizionale
import glob
if not st.session_state['file_loaded']:
    st.title("🏛️ Portale Tariffe Regione Puglia")
    st.markdown("### Carica il file Excel per iniziare")
    
    # Aggiungi JavaScript helper per verificare localStorage
    if 'main_js_loaded' not in st.session_state:
        components.html(LOCAL_STORAGE_JS, height=0)
        st.session_state['main_js_loaded'] = True
    
    # Informazione sul salvataggio automatico
    st.info("💡 I tuoi dati vengono salvati automaticamente nel browser. Vai al tab **Impostazioni** per gestire i backup.")

    # Cerca file Excel già presenti in data/ (se ce ne sono)
    excel_files = sorted(glob.glob(os.path.join("data", "*.xlsx")))
    if excel_files:
        st.info(f"📁 File Excel disponibili nella cartella data: {len(excel_files)}")
        default_file = excel_files[0]
        
        # Se non è stato caricato nessun file, carica il primo file Excel trovato
        if 'uploaded_file_data' not in st.session_state:
            st.session_state['uploaded_file_data'] = default_file
            st.session_state['file_loaded'] = True
            st.rerun()

    # Caricamento di un nuovo file Excel
    uploaded_file = st.file_uploader("📂 Carica il tuo file Excel", type=["xlsx"], help="Il file verrà processato temporaneamente e non salvato sul server")
    if uploaded_file:
        # Salva temporaneamente in memoria
        st.session_state['uploaded_file_content'] = uploaded_file.read()
        st.session_state['uploaded_file_name'] = uploaded_file.name
        st.session_state['file_loaded'] = True
        st.rerun()
else:
    # Nascondi header quando file è caricato - tutto va nella sidebar
    uploaded_file = st.session_state.get('uploaded_file_data', None)

df = None

# Gestione caricamento file
if st.session_state.get('file_loaded', False):
    # Carica dati se non già caricati
    if 'df_data' not in st.session_state:
        # Verifica se abbiamo un file da un percorso esistente o contenuto in memoria
        if 'uploaded_file_content' in st.session_state:
            # File caricato dall'utente - usa contenuto in memoria
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(st.session_state['uploaded_file_content'])
                temp_path = tmp_file.name
        elif st.session_state.get('uploaded_file_data'):
            # File esistente nella cartella data
            temp_path = st.session_state['uploaded_file_data']
        else:
            temp_path = None
        
        if temp_path:
            df = esamina_excel(temp_path)
            
            # Pulisci il file temporaneo se era stato creato
            if 'uploaded_file_content' in st.session_state and temp_path != st.session_state.get('uploaded_file_data'):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            if df is not None and not df.empty:
                # Usa la funzione utility per aggiungere CATEGORIA_ESTESA
                df = aggiungi_categoria_estesa(df)
                st.session_state['df_data'] = df
            else:
                st.error("⚠️ Errore nel caricamento del file")
                st.session_state['file_loaded'] = False
                st.rerun()
    
    df = st.session_state.get('df_data', None)
    
if df is not None and not df.empty:
    # TABS PRINCIPALI: Impostazioni, Ricerca Dati, Il Mio Elenco
    tab_impostazioni, tab_ricerca, tab_elenco = st.tabs(["⚙️ Impostazioni", "🔍 Ricerca Dati", "📚 Il Mio Elenco"])

    with tab_impostazioni:
        st.markdown("### ⚙️ Impostazioni e Gestione Categorie")
        # Caricamento/cambio file Excel
        st.markdown("#### 📂 Caricamento o Cambio File Excel")
        uploaded_file = st.file_uploader("Scegli un file Excel", type=["xlsx"], key="settings_file_uploader", help="Il file verrà processato temporaneamente senza essere salvato sul server")
        if uploaded_file:
            # Salva in memoria senza scrivere su disco
            st.session_state['uploaded_file_content'] = uploaded_file.read()
            st.session_state['uploaded_file_name'] = uploaded_file.name
            st.session_state['file_loaded'] = True
            
            # Carica subito i dati usando file temporaneo
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                tmp_file.write(st.session_state['uploaded_file_content'])
                temp_path = tmp_file.name
            
            try:
                df_temp = esamina_excel(temp_path)
                if df_temp is not None and not df_temp.empty:
                    # Usa la funzione utility
                    df_temp = aggiungi_categoria_estesa(df_temp)
                    st.session_state['df_data'] = df_temp
                    st.success(f"File caricato e dati pronti: {uploaded_file.name}")
                else:
                    st.error("⚠️ Errore nel caricamento del file")
            except Exception as e:
                st.error(f"⚠️ Errore durante il processamento del file: {str(e)}")
            finally:
                # Pulisci il file temporaneo
                try:
                    os.unlink(temp_path)
                except:
                    pass
            st.rerun()
        
        # Mostra info sul file corrente
        current_file = st.session_state.get('uploaded_file_name', 'Nessun file caricato')
        st.info(f"📄 File attualmente utilizzato: {current_file}")

        # Gestione categorie personalizzate
        st.markdown("#### 🏗️ Gestione Categorie Personalizzate")
        if 'new_category_input' not in st.session_state:
            st.session_state['new_category_input'] = ""
        if st.session_state.get('reset_new_category_input', False):
            st.session_state['new_category_input'] = ""
            st.session_state['reset_new_category_input'] = False
            st.rerun()
        with st.form("new_category_form_settings"):
            new_category = st.text_input(
                "📝 Nome nuova categoria",
                value=st.session_state['new_category_input'],
                placeholder="es. Muratura, Impianti, ecc...",
                key="new_category_input_settings"
            )
            submitted = st.form_submit_button("➕ Crea Categoria", use_container_width=True)
            if submitted:
                if new_category:
                    if new_category not in st.session_state['custom_categories']:
                        st.session_state['custom_categories'].append(new_category)
                        auto_save_work_state()
                    st.session_state['reset_new_category_input'] = True
                    st.rerun()
                else:
                    st.session_state['reset_new_category_input'] = True
                    st.rerun()
        if st.session_state['custom_categories']:
            st.markdown("**Categorie disponibili:**")
            for i, cat in enumerate(st.session_state['custom_categories']):
                st.write(f"{i+1}. {cat}")
        else:
            st.info("Nessuna categoria personalizzata creata.")

        # Salvataggio/caricamento lavoro
        st.markdown("#### 💾 Salvataggio e Caricamento Lavoro Locale")
        
        # Aggiungi JavaScript helper se non già presente
        if 'js_loaded' not in st.session_state:
            components.html(LOCAL_STORAGE_JS, height=0)
            st.session_state['js_loaded'] = True
        
        # Informazioni sul salvataggio locale
        st.info("ℹ️ Il lavoro viene salvato automaticamente sul tuo dispositivo. Puoi anche scaricare un backup o caricare un lavoro precedente.")
        
        col_save, col_load, col_restore = st.columns(3)
        
        with col_save:
            if st.button("� Scarica Backup", use_container_width=True, help="Scarica il tuo lavoro come file JSON"):
                if st.session_state['selected_rows'] or st.session_state['custom_categories']:
                    try:
                        json_str, filename = save_work_state()
                        
                        # Crea il download usando streamlit
                        st.download_button(
                            label="⬇️ Download File JSON",
                            data=json_str,
                            file_name=filename,
                            mime="application/json",
                            use_container_width=True,
                            key="download_backup"
                        )
                        st.success(f"✅ Backup pronto per il download!")
                    except Exception as e:
                        st.error(f"❌ Errore nella preparazione del backup: {str(e)}")
                else:
                    st.warning("⚠️ Nessun lavoro da salvare")
        
        with col_load:
            uploaded_work = st.file_uploader(
                "📤 Carica Backup",
                type=["json"],
                key="work_file_uploader_settings",
                help="Carica un file JSON precedentemente scaricato"
            )
            if uploaded_work:
                success, message = load_work_state(uploaded_work)
                if success:
                    # Salva anche nel localStorage dopo il caricamento
                    auto_save_work_state()
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
        
        with col_restore:
            # Bottone per ripristinare dal localStorage
            if st.button("🔄 Ripristina Automatico", use_container_width=True, help="Ripristina l'ultimo lavoro salvato automaticamente"):
                # Inietta JavaScript per caricare dal localStorage
                components.html(f"""
                {LOCAL_STORAGE_JS}
                <script>
                if (window.localStorageHelpers) {{
                    const data = window.localStorageHelpers.load('prezzario_autosave');
                    if (data) {{
                        // Invia i dati a Streamlit tramite un evento personalizzato
                        const event = new CustomEvent('localStorageData', {{ detail: data }});
                        document.dispatchEvent(event);
                        console.log('Dati caricati dal localStorage:', data);
                    }} else {{
                        console.log('Nessun dato trovato nel localStorage');
                    }}
                }}
                </script>
                """, height=100)
                
                # Per ora mostra un messaggio che richiede refresh
                st.info("🔄 Se hai dati salvati automaticamente, ricarica la pagina per ripristinarli.")
        
        # Sezione per cancellare i dati locali
        st.markdown("#### 🗑️ Gestione Dati Locali")
        col_clear1, col_clear2 = st.columns(2)
        
        with col_clear1:
            if st.button("🗑️ Cancella Tutto", use_container_width=True, help="Cancella tutto il lavoro corrente"):
                st.session_state['selected_rows'] = []
                st.session_state['custom_categories'] = []
                auto_save_work_state()  # Salva lo stato vuoto
                st.success("✅ Tutto il lavoro è stato cancellato!")
                st.rerun()
        
        with col_clear2:
            if st.button("🧹 Pulisci Cache Browser", use_container_width=True, help="Rimuove i dati salvati automaticamente dal browser"):
                components.html(f"""
                {LOCAL_STORAGE_JS}
                <script>
                if (window.localStorageHelpers) {{
                    window.localStorageHelpers.delete('prezzario_autosave');
                    console.log('Cache del browser pulita');
                }}
                </script>
                """, height=0)
                st.success("✅ Cache del browser pulita!")

    with tab_ricerca:
        st.markdown("### 🔍 Ricerca e Filtri Dati")
        if 'df_data' not in st.session_state or st.session_state['df_data'] is None or st.session_state['df_data'].empty:
            st.warning("⚠️ Nessun dato caricato. Carica un file Excel dal tab Impostazioni.")
        else:
            df = st.session_state['df_data']
            
            # SEZIONE DEBUG (rimuovi dopo aver risolto)
            with st.expander("🐛 Debug Categorie", expanded=False):
                test_estrazione_categorie(df)
            
            categoria_col = "CATEGORIA_ESTESA" if "CATEGORIA_ESTESA" in df.columns else None
            
            # Sezione categorie disponibili (richiudibile)
            with st.expander("📋 Categorie Disponibili", expanded=False):
                st.markdown("#### 🏷️ Panoramica delle Categorie")
                if categoria_col:
                    all_categories = sorted(list(df[categoria_col].dropna().unique()))
                    
                    # Inizializza la selezione delle categorie se non esiste
                    if 'selected_categories_filter' not in st.session_state:
                        st.session_state['selected_categories_filter'] = all_categories.copy()
                    
                    # Sezione di controllo per la selezione
                    col_sel1, col_sel2, col_sel3 = st.columns([2, 1, 1])
                    with col_sel1:
                        st.markdown("**Seleziona le categorie che ti interessano:**")
                    with col_sel2:
                        if st.button("✅ Seleziona Tutte", key="select_all_categories", use_container_width=True):
                            st.session_state['selected_categories_filter'] = all_categories.copy()
                            st.rerun()
                    with col_sel3:
                        if st.button("❌ Deseleziona Tutte", key="deselect_all_categories", use_container_width=True):
                            st.session_state['selected_categories_filter'] = []
                            st.rerun()
                    
                    # Lista di checkbox per ogni categoria
                    selected_categories = []
                    
                    # Organizza in colonne per una migliore visualizzazione
                    num_cols = 2
                    cols = st.columns(num_cols)
                    
                    for i, cat in enumerate(all_categories):
                        with cols[i % num_cols]:
                            df_cat = df[df[categoria_col] == cat]
                            count = len(df_cat)
                            
                            # Checkbox per ogni categoria
                            is_selected = cat in st.session_state['selected_categories_filter']
                            checkbox_key = f"category_checkbox_{i}_{cat}"
                            
                            if st.checkbox(
                                f"{cat} ({count} voci)",
                                value=is_selected,
                                key=checkbox_key
                            ):
                                if cat not in selected_categories:
                                    selected_categories.append(cat)
                            else:
                                if cat in st.session_state['selected_categories_filter']:
                                    st.session_state['selected_categories_filter'].remove(cat)
                    
                    # Aggiorna le categorie selezionate
                    for cat in selected_categories:
                        if cat not in st.session_state['selected_categories_filter']:
                            st.session_state['selected_categories_filter'].append(cat)
                    
                    # Mostra riepilogo delle categorie selezionate
                    st.markdown(f"**Categorie selezionate:** {len(st.session_state['selected_categories_filter'])}/{len(all_categories)}")
                    
                    # Crea una tabella riassuntiva solo delle categorie selezionate
                    if st.session_state['selected_categories_filter']:
                        category_overview = []
                        for cat in st.session_state['selected_categories_filter']:
                            df_cat = df[df[categoria_col] == cat]
                            count = len(df_cat)
                            # Calcola prezzo medio se possibile
                            try:
                                prezzi_validi = pd.to_numeric(df_cat['Prezzo'], errors='coerce').dropna()
                                prezzo_medio = prezzi_validi.mean() if len(prezzi_validi) > 0 else 0
                                valore_totale = prezzi_validi.sum() if len(prezzi_validi) > 0 else 0
                            except:
                                prezzo_medio = 0
                                valore_totale = 0
                            
                            category_overview.append({
                                "Categoria": cat,
                                "N° Voci": count,
                                "Prezzo Medio": f"€ {prezzo_medio:.2f}",
                                "Valore Totale": f"€ {valore_totale:,.2f}"
                            })
                        
                        if category_overview:
                            overview_df = pd.DataFrame(category_overview)
                            st.dataframe(
                                overview_df,
                                use_container_width=True,
                                hide_index=True
                            )
                    else:
                        st.warning("⚠️ Nessuna categoria selezionata. I filtri mostreranno tutti i risultati.")
                else:
                    st.info("Nessuna categoria rilevata nel dataset.")
            
            # Filtri di ricerca
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                search_tariffa = st.text_input("🏷️ Tariffa", value=st.session_state.get('search_tariffa_input_ricerca', ''), key="search_tariffa_input_ricerca", placeholder="Codice tariffa...")
            with col2:
                search_desc = st.text_input("📝 Descrizione", value=st.session_state.get('search_desc_input_ricerca', ''), key="search_desc_input_ricerca", placeholder="Descrizione...")
            with col3:
                search_unita = st.text_input("📏 Unità", value=st.session_state.get('search_unita_input_ricerca', ''), key="search_unita_input_ricerca", placeholder="Unità...")
            with col4:
                search_prezzo = st.text_input("💰 Prezzo", value=st.session_state.get('search_prezzo_input_ricerca', ''), key="search_prezzo_input_ricerca", placeholder="Prezzo...")

            # Bottone reset filtri
            active_search_filters = any([search_tariffa, search_desc, search_unita, search_prezzo])
            if active_search_filters:
                if st.button("🗑️ Cancella filtri", help="Cancella tutti i filtri di ricerca", use_container_width=True):
                    for key in ['search_tariffa_input_ricerca', 'search_desc_input_ricerca', 'search_unita_input_ricerca', 'search_prezzo_input_ricerca']:
                        if key in st.session_state:
                            st.session_state[key] = ''
                    st.session_state['batch_start'] = 0
                    st.rerun()

            # Filtro categoria
            if categoria_col:
                # Usa solo le categorie selezionate nel filtro
                if 'selected_categories_filter' in st.session_state and st.session_state['selected_categories_filter']:
                    filtered_categories = sorted(st.session_state['selected_categories_filter'])
                    categoria_options = ["Tutte le categorie selezionate"] + filtered_categories
                    help_text = f"Mostra solo le {len(filtered_categories)} categorie selezionate nell'expander sopra"
                else:
                    # Fallback a tutte le categorie se nessuna è selezionata
                    all_categories = sorted(list(df[categoria_col].dropna().unique()))
                    categoria_options = ["Tutte le categorie"] + all_categories
                    help_text = "Seleziona delle categorie nell'expander sopra per filtrare questo elenco"
                
                categoria_sel = st.selectbox(
                    "Categoria", 
                    categoria_options, 
                    key="categoria_filter_ricerca",
                    help=help_text
                )
            else:
                categoria_sel = "Tutte le categorie"

            # Ricerca batch
            def batch_search_ricerca(df, search_tariffa, search_desc, search_unita, search_prezzo, batch_size=50, batch_start=0):
                mask = np.ones(len(df), dtype=bool)
                if search_tariffa:
                    mask &= df['TARIFFA'].astype(str).str.contains(search_tariffa, case=False, na=False).values
                if search_desc:
                    mask &= df["DESCRIZIONE dell'ARTICOLO"].astype(str).str.contains(search_desc, case=False, na=False).values
                if search_unita:
                    mask &= df['Unità di misura'].astype(str).str.contains(search_unita, case=False, na=False).values
                if search_prezzo:
                    mask &= df['Prezzo'].astype(str).str.contains(search_prezzo, case=False, na=False).values
                df_filtered = df[mask]
                total = len(df_filtered)
                start = batch_start
                end = min(start + batch_size, total)
                df_batch = df_filtered.iloc[start:end]
                return df_batch, total, df_filtered

            if 'batch_start' not in st.session_state:
                st.session_state['batch_start'] = 0
            batch_size = 50
            
            # Gestione filtro categoria con selezione multipla
            if categoria_sel in ["Tutte le categorie", "Tutte le categorie selezionate"] or not categoria_col:
                if categoria_sel == "Tutte le categorie selezionate" and 'selected_categories_filter' in st.session_state:
                    # Filtra solo per le categorie selezionate
                    if st.session_state['selected_categories_filter']:
                        df_categoria = df[df[categoria_col].isin(st.session_state['selected_categories_filter'])]
                    else:
                        df_categoria = df  # Se nessuna categoria selezionata, mostra tutto
                else:
                    df_categoria = df  # Tutte le categorie
            else:
                df_categoria = df[df[categoria_col] == categoria_sel]
            
            df_batch, total_found, df_filtered = batch_search_ricerca(df_categoria, search_tariffa, search_desc, search_unita, search_prezzo, batch_size, st.session_state['batch_start'])

            # Statistiche
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Voci in categoria", f"{len(df_categoria):,}")
            with col_stats2:
                st.metric("Voci filtrate", f"{total_found:,}")
            with col_stats3:
                current_page = (st.session_state['batch_start'] // batch_size) + 1
                total_pages = max(1, (total_found - 1) // batch_size + 1)
                st.metric("Pagina", f"{current_page}/{total_pages}")

            # Raggruppamento per categoria
            categorie_map = {
                '01': '01 - Edilizia',
                '02': '02 - Restauro e opere di recupero',
                '03': '03 - Infrastrutture',
                '04': '04 - Impianti elettrici',
                '05': '05 - Impianti di adduzione idrica e di scarico',
                '06': '06 - Impianti antincendio',
                '07': '07 - Impianti termici',
                '08': '08 - Fognature ed acquedotti',
                '09': '09 - Sicurezza in azienda e in cantiere',
                '10': '10 - Opere marittime',
                '11': '11 - Impianti sportivi',
                '12': '12 - Igiene ambientale',
                '13': '13 - Opere idrauliche e di bonifica e consolidamento',
                '14': '14 - Opere forestali',
                '15': '15 - Sondaggi e prove',
                '16': '16 - Opere a verde e irrigazione',
                '17': '17 - Arredo urbano e parco giochi'
            }

            def group_results_by_category(df_batch):
                groups = {}
                for _, row in df_batch.iterrows():
                    categoria_num = get_categoria_from_tariffa(row['TARIFFA'])
                    if categoria_num:
                        categoria_nome = CATEGORIE_MAP.get(categoria_num, f"Categoria {categoria_num}")
                    else:
                        categoria_nome = "Senza Categoria"
                    if categoria_nome not in groups:
                        groups[categoria_nome] = []
                    groups[categoria_nome].append(row)
                return groups

            category_groups = group_results_by_category(df_batch)

            # Visualizzazione risultati
            if total_found > 0:
                # Titolo dinamico basato sulla categoria selezionata
                if categoria_sel in ["Tutte le categorie", "Tutte le categorie selezionate"]:
                    if categoria_sel == "Tutte le categorie selezionate":
                        num_selected = len(st.session_state.get('selected_categories_filter', []))
                        st.markdown(f"### 🌳 Risultati per le {num_selected} categorie selezionate")
                    else:
                        st.markdown("### 🌳 Risultati della ricerca organizzati per categoria")
                else:
                    st.markdown(f"### 🌳 Risultati per: **{categoria_sel}**")
                    
                for categoria_nome, rows in category_groups.items():
                    with st.expander(f"{categoria_nome} ({len(rows)})", expanded=True):
                        df_cat = pd.DataFrame(rows)
                        df_cat.insert(0, "Aggiungi", False)
                        columns_to_show = [col for col in df_cat.columns if not col.startswith('_')]
                        df_cat_clean = df_cat[columns_to_show].copy()
                        edited_df = st.data_editor(
                            df_cat_clean,
                            column_config={
                                "Aggiungi": st.column_config.CheckboxColumn("➕ Aggiungi", help="Seleziona per aggiungere al tuo elenco", default=False),
                                "TARIFFA": st.column_config.TextColumn("🏷️ Tariffa", width="medium"),
                                "DESCRIZIONE dell'ARTICOLO": st.column_config.TextColumn("📝 Descrizione", width="large"),
                                "Unità di misura": st.column_config.TextColumn("📏 Unità", width="small"),
                                "Prezzo": st.column_config.NumberColumn("💰 Prezzo", format="%.2f €", width="small"),
                            },
                            disabled=["TARIFFA", "DESCRIZIONE dell'ARTICOLO", "Unità di misura", "Prezzo"] + ([categoria_col] if categoria_col else []),
                            hide_index=True,
                            use_container_width=True,
                            height=min(300, 50 * len(df_cat_clean) + 50),
                            key=f"ricerca_editor_{categoria_nome}_{st.session_state['batch_start']}"
                        )
                        selected_indices = edited_df[edited_df["Aggiungi"] == True].index
                        if len(selected_indices) > 0:
                            if st.button(f"➕ Aggiungi {len(selected_indices)} voci selezionate a Il Mio Elenco", key=f"add_ricerca_{categoria_nome}_{st.session_state['batch_start']}", use_container_width=True):
                                if 'selected_rows' not in st.session_state:
                                    st.session_state['selected_rows'] = []
                                added_count = 0
                                skipped_count = 0
                                existing_items = set(row['TARIFFA'] for row in st.session_state['selected_rows'] if 'TARIFFA' in row)
                                for display_idx in selected_indices:
                                    if display_idx < len(df_cat):
                                        row_data = df_cat.iloc[display_idx].to_dict()
                                        row_data.pop('Aggiungi', None)
                                        tariffa_id = row_data.get('TARIFFA', '')
                                        if tariffa_id not in existing_items:
                                            row_data['_CUSTOM_CATEGORY'] = None
                                            st.session_state['selected_rows'].append(row_data)
                                            existing_items.add(tariffa_id)
                                            added_count += 1
                                        else:
                                            skipped_count += 1
                                if added_count > 0:
                                    auto_save_work_state()
                                    st.success(f"✅ Aggiunte {added_count} nuove voci al tuo elenco!")
                                if skipped_count > 0:
                                    st.info(f"⏭️ Saltate {skipped_count} voci già presenti nel tuo elenco.")
                                st.rerun()
            else:
                st.warning("⚠️ Nessun risultato trovato per i criteri di ricerca specificati.")

            # Navigazione batch
            col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
            with col_nav1:
                if st.session_state['batch_start'] > 0:
                    if st.button("⬅️ Precedenti", help="Vai alla pagina precedente", use_container_width=True, key=f"prev_page_ricerca_{st.session_state['batch_start']}"):
                        st.session_state['batch_start'] = max(0, st.session_state['batch_start'] - batch_size)
                        st.rerun()
            with col_nav2:
                if total_pages > 1:
                    page_number = st.number_input(
                        f"Vai alla pagina (1-{total_pages})",
                        min_value=1,
                        max_value=total_pages,
                        value=current_page,
                        key="page_input_ricerca"
                    )
                    if page_number != current_page:
                        st.session_state['batch_start'] = (page_number - 1) * batch_size
                        st.rerun()
            with col_nav3:
                if st.session_state['batch_start'] + batch_size < total_found:
                    if st.button("➡️ Successivi", help="Vai alla pagina successiva", use_container_width=True, key=f"next_page_ricerca_{st.session_state['batch_start']}"):
                        st.session_state['batch_start'] += batch_size
                        st.rerun()

    with tab_elenco:
        st.markdown("### 📚 Il Mio Elenco Personalizzato")
        
        # Mostra statistiche del mio elenco
        selected_count = len(st.session_state.get('selected_rows', []))
        
        if selected_count == 0:
            st.info("📝 Il tuo elenco è vuoto. Usa il tab **Ricerca Dati** per aggiungere voci.")
        else:
            # Statistiche dell'elenco
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("📊 Voci nel mio elenco", selected_count)
            
            # Calcola valore totale se possibile
            total_value = 0
            valid_prices = 0
            for row in st.session_state['selected_rows']:
                try:
                    prezzo = pd.to_numeric(row.get('Prezzo', 0), errors='coerce')
                    if not pd.isna(prezzo):
                        total_value += float(prezzo)
                        valid_prices += 1
                except:
                    pass
            
            with col_stats2:
                st.metric("💰 Valore Totale", f"€ {total_value:,.2f}")
            
            with col_stats3:
                avg_price = total_value / valid_prices if valid_prices > 0 else 0
                st.metric("📈 Prezzo Medio", f"€ {avg_price:.2f}")
            
            # Mostra voci filtrate 
            st.markdown(f"#### � Le Mie Voci ({selected_count})")
            
            # Raggruppa per categoria personalizzata
            groups = {}
            for row in st.session_state['selected_rows']:
                cat = row.get('_CUSTOM_CATEGORY', 'Senza categoria')
                if cat not in groups:
                    groups[cat] = []
                groups[cat].append(row)
            
            # Mostra ogni gruppo
            for categoria, rows in groups.items():
                icon = "📂" if categoria != "Senza categoria" else "📄"
                
                with st.expander(f"{icon} **{categoria}** ({len(rows)} voci)", expanded=True):
                    # Crea DataFrame per questo gruppo
                    df_group = pd.DataFrame(rows)
                    
                    # Aggiungi colonna per rimozione
                    df_group.insert(0, "Rimuovi", False)
                    
                    # Rimuovi colonne interne
                    columns_to_show = [col for col in df_group.columns if not col.startswith('_')]
                    df_group_clean = df_group[columns_to_show].copy()
                    
                    # Editor per questo gruppo
                    edited_group = st.data_editor(
                        df_group_clean,
                        column_config={
                            "Rimuovi": st.column_config.CheckboxColumn(
                                "🗑️ Rimuovi",
                                help="Seleziona per rimuovere dal tuo elenco",
                                default=False
                            ),
                            "TARIFFA": st.column_config.TextColumn("🏷️ Tariffa", width="medium"),
                            "DESCRIZIONE dell'ARTICOLO": st.column_config.TextColumn("📝 Descrizione", width="large"),
                            "Unità di misura": st.column_config.TextColumn("📏 Unità", width="small"),
                            "Prezzo": st.column_config.NumberColumn("💰 Prezzo", format="%.2f €", width="small"),
                        },
                        disabled=["TARIFFA", "DESCRIZIONE dell'ARTICOLO", "Unità di misura", "Prezzo", "CATEGORIA_ESTESA"],
                        hide_index=True,
                        use_container_width=True,
                        height=min(400, 50 * len(df_group_clean) + 50),
                        key=f"my_list_editor_{categoria}"
                    )
                    
                    # Gestisci rimozioni
                    to_remove_indices = edited_group[edited_group["Rimuovi"] == True].index
                    if len(to_remove_indices) > 0:
                        col_remove, col_info = st.columns([2, 1])
                        with col_remove:
                            if st.button(
                                f"🗑️ Rimuovi {len(to_remove_indices)} voci selezionate",
                                key=f"remove_{categoria}",
                                type="secondary",
                                use_container_width=True
                            ):
                                # Rimuovi le voci selezionate
                                tariffe_to_remove = set()
                                for idx in to_remove_indices:
                                    if idx < len(df_group):
                                        tariffa = df_group.iloc[idx]['TARIFFA']
                                        tariffe_to_remove.add(tariffa)
                                
                                # Aggiorna la lista principale
                                st.session_state['selected_rows'] = [
                                    row for row in st.session_state['selected_rows']
                                    if row.get('TARIFFA') not in tariffe_to_remove
                                ]
                                
                                auto_save_work_state()
                                st.success(f"✅ Rimosse {len(to_remove_indices)} voci!")
                                st.rerun()
                        
                        with col_info:
                            st.info(f"🎯 {len(to_remove_indices)} voci selezionate")
            
            # Opzioni di esportazione
            st.markdown("#### 📤 Esportazione")
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                if st.button("🗑️ Svuota Elenco", help="Rimuovi tutte le voci dal tuo elenco"):
                    st.session_state['selected_rows'] = []
                    auto_save_work_state()
                    st.success("✅ Elenco svuotato!")
                    st.rerun()
            
            with col_exp2:
                if st.session_state['selected_rows']:
                    # Prepara CSV
                    df_export = pd.DataFrame(st.session_state['selected_rows'])
                    csv_data = df_export.to_csv(index=False)
                    
                    st.download_button(
                        label="📊 Scarica CSV",
                        data=csv_data,
                        file_name=f"mio_elenco_tariffe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    st.download_button(
                        label="📊 Scarica CSV",
                        data=csv_data,
                        file_name=f"mio_elenco_tariffe_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        

