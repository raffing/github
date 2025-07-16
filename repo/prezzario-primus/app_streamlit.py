import json
import base64
from datetime import datetime

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


import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import os
import re
from src.esamina_excel import esamina_excel, raggruppa_per_lettera_tariffa, crea_struttura_gerarchica

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
                # Aggiungi la colonna CATEGORIA_ESTESA se non esiste
                if 'CATEGORIA_ESTESA' not in df.columns:
                    # Mappatura categorie
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
                    
                    def estrai_categoria(tariffa):
                        if pd.isna(tariffa):
                            return None
                        match = re.search(r'/(\d+)\.', str(tariffa))
                        if match:
                            numero_cat = match.group(1)
                            return categorie_map.get(numero_cat, numero_cat)
                        return None
                    
                    df['CATEGORIA_ESTESA'] = df['TARIFFA'].apply(estrai_categoria)
                
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
                    if 'CATEGORIA_ESTESA' not in df_temp.columns:
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
                        def estrai_categoria(tariffa):
                            if pd.isna(tariffa):
                                return None
                            match = re.search(r'/(\d+)\.', str(tariffa))
                            if match:
                                numero_cat = match.group(1)
                                return categorie_map.get(numero_cat, numero_cat)
                            return None
                        df_temp['CATEGORIA_ESTESA'] = df_temp['TARIFFA'].apply(estrai_categoria)
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
            categoria_col = "CATEGORIA_ESTESA" if "CATEGORIA_ESTESA" in df.columns else None
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
                all_categories = sorted(list(df[categoria_col].dropna().unique()))
                categoria_sel = st.selectbox("Categoria", ["Tutte le categorie"] + all_categories, key="categoria_filter_ricerca")
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
            if categoria_sel == "Tutte le categorie" or not categoria_col:
                df_categoria = df
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
            def get_categoria_from_tariffa(tariffa):
                if pd.isna(tariffa):
                    return None
                match = re.search(r'/([0-9]+)\\.', str(tariffa))
                return match.group(1) if match else None

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
                        categoria_nome = categorie_map.get(categoria_num, f"Categoria {categoria_num}")
                    else:
                        categoria_nome = "Senza Categoria"
                    if categoria_nome not in groups:
                        groups[categoria_nome] = []
                    groups[categoria_nome].append(row)
                return groups

            category_groups = group_results_by_category(df_batch)

            # Visualizzazione risultati
            if total_found > 0:
                st.markdown("### 🌳 Risultati della ricerca organizzati per categoria")
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
        # Tutta la logica di gestione e visualizzazione delle voci selezionate
        # ...existing code...
        # FILTRI CON COMPONENTI NATIVI STREAMLIT
        col_categoria, col_filtri = st.columns([1, 3])

        # Definisci la colonna categoria
        categoria_col = "CATEGORIA_ESTESA" if "CATEGORIA_ESTESA" in df.columns else None
        
        with col_categoria:
            st.markdown("#### 🏷️ Filtro Categoria")
            if categoria_col:
                # Ottieni tutte le categorie disponibili
                all_categories = sorted(list(df[categoria_col].unique()))
                categoria_sel = st.selectbox(
                    "Seleziona categoria", 
                    ["Tutte le categorie"] + all_categories, 
                    key="categoria_filter",
                    help="Filtra per categoria specifica"
                )
                
                # Bottone reset categoria solo se diverso da "Tutte le categorie"
                if categoria_sel != "Tutte le categorie":
                    if st.button("🔄 Reset categoria", help="Torna a tutte le categorie", use_container_width=True):
                        # Cancella la chiave per far resettare il widget
                        if 'categoria_filter' in st.session_state:
                            del st.session_state['categoria_filter']
                        st.session_state['batch_start'] = 0
                        st.rerun()
            else:
                categoria_sel = "Tutte le categorie"
                st.info("Nessuna categoria disponibile")
        
        with col_filtri:
            st.markdown("#### 🔍 Filtri di Ricerca")
            
            # Campi di ricerca con clear integrato
            col1, col2, col3, col4 = st.columns(4)
            if 'search_tariffa_input' not in st.session_state:
                st.session_state['search_tariffa_input'] = ""
            if 'search_desc_input' not in st.session_state:
                st.session_state['search_desc_input'] = ""
            if 'search_unita_input' not in st.session_state:
                st.session_state['search_unita_input'] = ""
            if 'search_prezzo_input' not in st.session_state:
                st.session_state['search_prezzo_input'] = ""

            with col1:
                search_tariffa = st.text_input(
                    "🏷️ Tariffa",
                    value=st.session_state['search_tariffa_input'],
                    help="Filtra per codice tariffa",
                    key="search_tariffa_input",
                    placeholder="Inserisci codice tariffa...",
                    on_change=lambda: st.session_state.update({'search_tariffa': st.session_state['search_tariffa_input'], 'batch_start': 0})
                )
            with col2:
                search_desc = st.text_input(
                    "📝 Descrizione",
                    value=st.session_state['search_desc_input'],
                    help="Filtra per descrizione",
                    key="search_desc_input",
                    placeholder="Inserisci descrizione...",
                    on_change=lambda: st.session_state.update({'search_desc': st.session_state['search_desc_input'], 'batch_start': 0})
                )
            with col3:
                search_unita = st.text_input(
                    "📏 Unità",
                    value=st.session_state['search_unita_input'],
                    help="Filtra per unità di misura",
                    key="search_unita_input",
                    placeholder="Inserisci unità...",
                    on_change=lambda: st.session_state.update({'search_unita': st.session_state['search_unita_input'], 'batch_start': 0})
                )
            with col4:
                search_prezzo = st.text_input(
                    "💰 Prezzo",
                    value=st.session_state['search_prezzo_input'],
                    help="Filtra per prezzo",
                    key="search_prezzo_input",
                    placeholder="Inserisci prezzo...",
                    on_change=lambda: st.session_state.update({'search_prezzo': st.session_state['search_prezzo_input'], 'batch_start': 0})
                )
            
            # Bottone cancella tutti i filtri se ce ne sono di attivi
            active_search_filters = any([search_tariffa, search_desc, search_unita, search_prezzo])
            if active_search_filters:
                col_clear = st.columns([3, 1])
                with col_clear[1]:
                    if st.button("🗑️ Cancella filtri", help="Cancella tutti i campi di ricerca", use_container_width=True):
                        # Reset di tutti i campi di ricerca usando cancellazione delle chiavi
                        for key in ['search_tariffa', 'search_desc', 'search_unita', 'search_prezzo']:
                            if key in st.session_state:
                                del st.session_state[key]
                        for key in ['search_tariffa_input', 'search_desc_input', 'search_unita_input', 'search_prezzo_input']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.session_state['batch_start'] = 0
                        st.rerun()

        # Ricerca batch ottimizzata - restituisce risultati raggruppati per categoria
        def batch_search(df, search_tariffa, search_desc, search_unita, search_prezzo, batch_size=50, batch_start=0):
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
            
            # Applica paginazione
            total = len(df_filtered)
            start = batch_start
            end = min(start + batch_size, total)
            df_batch = df_filtered.iloc[start:end]
            
            return df_batch, total

        def get_categoria_from_tariffa(tariffa):
            """Estrae il numero categoria dal codice tariffa"""
            if pd.isna(tariffa):
                return None
            match = re.search(r'/(\d+)\.', str(tariffa))
            return match.group(1) if match else None

        def group_results_by_category(df_batch):
            """Raggruppa i risultati per categoria"""
            # Mappatura categorie
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
            
            groups = {}
            
            for _, row in df_batch.iterrows():
                categoria_num = get_categoria_from_tariffa(row['TARIFFA'])
                if categoria_num:
                    categoria_nome = categorie_map.get(categoria_num, f"Categoria {categoria_num}")
                else:
                    categoria_nome = "Senza Categoria"
                
                if categoria_nome not in groups:
                    groups[categoria_nome] = []
                groups[categoria_nome].append(row)
            
            return groups

        def get_category_full_stats(df_filtered, category_groups):
            """Calcola le statistiche complete per ogni categoria (non solo il batch corrente)"""
            # Mappatura categorie
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
            
            # Raggruppa TUTTO il dataset filtrato per categoria (non solo il batch)
            full_category_stats = {}
            
            for _, row in df_filtered.iterrows():
                categoria_num = get_categoria_from_tariffa(row['TARIFFA'])
                if categoria_num:
                    categoria_nome = categorie_map.get(categoria_num, f"Categoria {categoria_num}")
                else:
                    categoria_nome = "Senza Categoria"
                
                if categoria_nome not in full_category_stats:
                    full_category_stats[categoria_nome] = []
                full_category_stats[categoria_nome].append(row)
            
            return full_category_stats

        # Gestione batch
        if 'batch_start' not in st.session_state:
            st.session_state['batch_start'] = 0
        batch_size = 50
        if categoria_sel == "Tutte le categorie" or not categoria_col:
            df_categoria = df
        else:
            df_categoria = df[df[categoria_col] == categoria_sel]
        df_batch, total_found = batch_search(df_categoria, search_tariffa, search_desc, search_unita, search_prezzo, batch_size, st.session_state['batch_start'])

        # STATISTICHE FILTRI
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Voci in categoria", f"{len(df_categoria):,}")
        with col_stats2:
            st.metric("Voci filtrate", f"{total_found:,}")
        with col_stats3:
            current_page = (st.session_state['batch_start'] // batch_size) + 1
            total_pages = max(1, (total_found - 1) // batch_size + 1)
            st.metric("Pagina", f"{current_page}/{total_pages}")

        def show_category_details(categoria_nome, rows, batch_start):
            """Mostra i dettagli di una categoria con tabella interattiva"""
            # Configura colonne per le tabelle
            column_config = {
                "Aggiungi": st.column_config.CheckboxColumn(
                    "➕ Aggiungi",
                    help="Seleziona per aggiungere al tuo elenco",
                    default=False,
                ),
                "TARIFFA": st.column_config.TextColumn("🏷️ Tariffa", width="medium"),
                "DESCRIZIONE dell'ARTICOLO": st.column_config.TextColumn("📝 Descrizione", width="large"),
                "Unità di misura": st.column_config.TextColumn("📏 Unità", width="small"),
                "Prezzo": st.column_config.NumberColumn("💰 Prezzo", format="%.2f €", width="small"),
            }
            
            with st.container():
                st.markdown(f"##### 📋 {categoria_nome}")
                
                # Converti in DataFrame
                df_cat = pd.DataFrame(rows)
                df_cat.insert(0, "Aggiungi", False)
                
                # Rimuovi colonne interne se presenti
                columns_to_show = [col for col in df_cat.columns if not col.startswith('_')]
                df_cat_clean = df_cat[columns_to_show].copy()
                
                # Tabella interattiva per questa categoria
                edited_df = st.data_editor(
                    df_cat_clean,
                    column_config=column_config,
                    disabled=["TARIFFA", "DESCRIZIONE dell'ARTICOLO", "Unità di misura", "Prezzo"] + ([categoria_col] if categoria_col else []),
                    hide_index=True,
                    use_container_width=True,
                    height=min(300, 50 * len(df_cat_clean) + 50),
                    key=f"compact_detail_{categoria_nome}_{batch_start}"
                )
                
                # Gestione selezioni per questa categoria
                selected_indices = edited_df[edited_df["Aggiungi"] == True].index
                if len(selected_indices) > 0:
                    col_add, col_info = st.columns([2, 1])
                    with col_add:
                        if st.button(
                            f"➕ Aggiungi {len(selected_indices)} voci selezionate", 
                            key=f"add_compact_{categoria_nome}_{batch_start}", 
                            type="primary",
                            use_container_width=True
                        ):
                            if 'selected_rows' not in st.session_state:
                                st.session_state['selected_rows'] = []
                            
                            added_count = 0
                            skipped_count = 0
                            existing_items = set()
                            
                            # Costruisci set di voci già presenti
                            for existing_row in st.session_state['selected_rows']:
                                if 'TARIFFA' in existing_row:
                                    existing_items.add(existing_row['TARIFFA'])
                            
                            # Aggiungi le voci selezionate
                            for display_idx in selected_indices:
                                if display_idx < len(df_cat):
                                    row_data = df_cat.iloc[display_idx].to_dict()
                                    row_data.pop('Aggiungi', None)
                                    
                                    tariffa_id = row_data.get('TARIFFA', '')
                                    if tariffa_id not in existing_items:
                                        # Assegna categoria personalizzata se selezionata
                                        if st.session_state.get('selected_custom_category'):
                                            row_data['_CUSTOM_CATEGORY'] = st.session_state['selected_custom_category']
                                        else:
                                            row_data['_CUSTOM_CATEGORY'] = None
                                        
                                        st.session_state['selected_rows'].append(row_data)
                                        existing_items.add(tariffa_id)
                                        added_count += 1
                                    else:
                                        skipped_count += 1
                            
                            # Autosalva e mostra risultato
                            if added_count > 0:
                                auto_save_work_state()
                                st.success(f"✅ Aggiunte {added_count} nuove voci al tuo elenco!")
                            
                            if skipped_count > 0:
                                st.info(f"⏭️ Saltate {skipped_count} voci già presenti nel tuo elenco.")
                            
                            if added_count == 0 and skipped_count > 0:
                                st.warning("⚠️ Tutte le voci selezionate erano già nel tuo elenco.")
                            
                            st.rerun()
                    
                    with col_info:
                        st.info(f"🎯 {len(selected_indices)} voci selezionate")
                
                st.markdown("---")

        # VISUALIZZAZIONE RISULTATI COME TREE CON NODI APRIBILI/CHIUDIBILI
        if total_found > 0:
            st.markdown("### 🌳 Risultati della ricerca organizzati per categoria")
            
            # Prima calcola le statistiche complete sul dataset filtrato
            mask = np.ones(len(df_categoria), dtype=bool)
            if search_tariffa:
                mask &= df_categoria['TARIFFA'].astype(str).str.contains(search_tariffa, case=False, na=False).values
            if search_desc:
                mask &= df_categoria["DESCRIZIONE dell'ARTICOLO"].astype(str).str.contains(search_desc, case=False, na=False).values
            if search_unita:
                mask &= df_categoria['Unità di misura'].astype(str).str.contains(search_unita, case=False, na=False).values
            if search_prezzo:
                mask &= df_categoria['Prezzo'].astype(str).str.contains(search_prezzo, case=False, na=False).values
            
            df_filtered_complete = df_categoria[mask]
            
            # Ottieni le statistiche complete per tutte le categorie
            full_category_stats = get_category_full_stats(df_filtered_complete, {})
            
            # Raggruppa risultati per categoria (solo per il batch corrente)
            category_groups = group_results_by_category(df_batch)
            
            # Salva i dati per la sidebar
            st.session_state['search_results_available'] = True
            st.session_state['full_category_stats'] = full_category_stats
            
            # Determina la modalità vista dalla sidebar
            view_mode = st.session_state.get('tree_view_mode', '📊 Compatta')

            # VISTA COMPATTA - Mostra tutti i nodi chiusi
            if view_mode == '📊 Compatta':
                st.markdown("### 📋 Categorie Disponibili")
                
                # Tabella riassuntiva delle categorie
                category_summary = []
                # Usa le statistiche complete per mostrare TUTTE le categorie presenti nel dataset filtrato
                for categoria_nome, full_rows in full_category_stats.items():
                    # Icona per la categoria
                    icon = "📂"
                    if "Edilizia" in categoria_nome:
                        icon = "🏗️"
                    elif "Impianti" in categoria_nome:
                        icon = "⚡"
                    elif "Infrastrutture" in categoria_nome:
                        icon = "🛣️"
                    elif "Restauro" in categoria_nome:
                        icon = "🏛️"
                    elif "Sicurezza" in categoria_nome:
                        icon = "🦺"
                    elif "Opere" in categoria_nome:
                        icon = "🌊"
                    elif "Verde" in categoria_nome:
                        icon = "🌿"
                    
                    # Usa le statistiche complete per questa categoria (TUTTE le voci della categoria)
                    total_voci_categoria = len(full_rows)
                    
                    # Calcola statistiche per categoria usando TUTTE le voci della categoria
                    prezzi = []
                    for row in full_rows:
                        if pd.notna(row['Prezzo']):
                            try:
                                prezzo = pd.to_numeric(row['Prezzo'], errors='coerce')
                                if not pd.isna(prezzo):
                                    prezzi.append(float(prezzo))
                            except:
                                pass
                    
                    valore_totale = sum(prezzi) if prezzi else 0
                    prezzo_medio = valore_totale / len(prezzi) if prezzi else 0
                    
                    category_summary.append({
                        "Categoria": f"{icon} {categoria_nome}",
                        "Voci": total_voci_categoria,  # Totale reale di tutte le voci
                        "Valore Totale": f"€ {valore_totale:,.2f}",
                        "Prezzo Medio": f"€ {prezzo_medio:,.2f}",
                        "Apri": False
                    })
                
                # Mostra tabella riassuntiva
                if category_summary:
                    summary_df = pd.DataFrame(category_summary)
                    
                    edited_summary = st.data_editor(
                        summary_df,
                        column_config={
                            "Categoria": st.column_config.TextColumn("🏷️ Categoria", width="large"),
                            "Voci": st.column_config.NumberColumn("📊 N° Voci", width="small"),
                            "Valore Totale": st.column_config.TextColumn("💰 Valore Tot.", width="medium"),
                            "Prezzo Medio": st.column_config.TextColumn("📈 Prezzo Medio", width="medium"),
                            "Apri": st.column_config.CheckboxColumn("👁️ Apri", help="Seleziona per aprire i dettagli", width="small")
                        },
                        disabled=["Categoria", "Voci", "Valore Totale", "Prezzo Medio"],
                        hide_index=True,
                        use_container_width=True,
                        height=min(400, 50 * len(category_summary) + 50),
                        key="compact_view_table"
                    )
                    
                    # Mostra dettagli delle categorie selezionate
                    selected_categories = edited_summary[edited_summary["Apri"] == True]["Categoria"].tolist()
                    
                    if selected_categories:
                        st.markdown("#### 🔍 Dettagli categorie selezionate")
                        
                        # Per ogni categoria selezionata, crea un expander individuale
                        for cat_display in selected_categories:
                            # Trova il nome categoria originale (rimuovi icona dal nome)
                            cat_name = None
                            for nome in full_category_stats.keys():
                                if nome in cat_display:
                                    cat_name = nome
                                    break
                            
                            if cat_name and cat_name in full_category_stats:
                                # Prendi le voci per questa categoria dal batch corrente (se presenti)
                                rows = category_groups.get(cat_name, [])
                                
                                # Usa le statistiche complete per mostrare il totale reale
                                full_rows = full_category_stats.get(cat_name, [])
                                total_voci_reali = len(full_rows)
                                
                                # Icona per la categoria
                                icon = "📂"
                                if "Edilizia" in cat_name:
                                    icon = "🏗️"
                                elif "Impianti" in cat_name:
                                    icon = "⚡"
                                elif "Infrastrutture" in cat_name:
                                    icon = "🛣️"
                                elif "Restauro" in cat_name:
                                    icon = "🏛️"
                                elif "Sicurezza" in cat_name:
                                    icon = "🦺"
                                elif "Opere" in cat_name:
                                    icon = "🌊"
                                elif "Verde" in cat_name:
                                    icon = "🌿"
                                
                                # Expander per questa categoria con informazioni complete
                                with st.expander(
                                    f"{icon} **{cat_name}** ({total_voci_reali} voci totali - {len(rows)} in questa pagina)", 
                                    expanded=len(selected_categories) == 1  # Espandi solo se è l'unica selezionata
                                ):
                                    if len(rows) > 0:
                                        show_category_details(cat_name, rows, st.session_state['batch_start'])
                                    else:
                                        st.info(f"Nessuna voce di '{cat_name}' in questa pagina. Naviga tra le pagine per trovare le voci di questa categoria.")
                                        
                                        # Mostra informazioni sulle voci totali della categoria
                                        if total_voci_reali > 0:
                                            st.info(f"📊 Questa categoria contiene {total_voci_reali} voci totali che soddisfano i filtri di ricerca.")
            
            # VISTA ESPANSA - Expander tradizionali (come prima)
            else:
                # Configura colonne per le tabelle
                column_config = {
                    "Aggiungi": st.column_config.CheckboxColumn(
                        "➕ Aggiungi",
                        help="Seleziona per aggiungere al tuo elenco",
                        default=False,
                    ),
                    "TARIFFA": st.column_config.TextColumn(
                        "🏷️ Tariffa",
                        width="medium",
                    ),
                    "DESCRIZIONE dell'ARTICOLO": st.column_config.TextColumn(
                        "📝 Descrizione",
                        width="large",
                    ),
                    "Unità di misura": st.column_config.TextColumn(
                        "📏 Unità",
                        width="small",
                    ),
                    "Prezzo": st.column_config.NumberColumn(
                        "💰 Prezzo",
                        format="%.2f €",
                        width="small",
                    ),
                }

                # Crea un expander per ogni categoria (nodo del tree)
                for categoria_nome, rows in category_groups.items():
                    # Determina se aprire di default (prima categoria aperta, altre chiuse)
                    is_first_category = list(category_groups.keys())[0] == categoria_nome
                    
                    # Icona per la categoria
                    icon = "📂"
                    if "Edilizia" in categoria_nome:
                        icon = "🏗️"
                    elif "Impianti" in categoria_nome:
                        icon = "⚡"
                    elif "Infrastrutture" in categoria_nome:
                        icon = "🛣️"
                    elif "Restauro" in categoria_nome:
                        icon = "🏛️"
                    elif "Sicurezza" in categoria_nome:
                        icon = "🦺"
                    elif "Opere" in categoria_nome:
                        icon = "🌊"
                    elif "Verde" in categoria_nome:
                        icon = "🌿"
                    
                    # Nodo del tree (expander)
                    with st.expander(f"{icon} **{categoria_nome}** ({len(rows)} voci)", expanded=is_first_category):
                        if not rows:
                            st.info("Nessuna voce in questa categoria per i filtri attuali.")
                            continue
                        
                        # Converti in DataFrame
                        df_cat = pd.DataFrame(rows)
                        df_cat.insert(0, "Aggiungi", False)
                        
                        # Rimuovi colonne interne se presenti
                        columns_to_show = [col for col in df_cat.columns if not col.startswith('_')]
                        df_cat_clean = df_cat[columns_to_show].copy()
                        
                        # Tabella interattiva per questa categoria
                        edited_df = st.data_editor(
                            df_cat_clean,
                            column_config=column_config,
                            disabled=["TARIFFA", "DESCRIZIONE dell'ARTICOLO", "Unità di misura", "Prezzo"] + ([categoria_col] if categoria_col else []),
                            hide_index=True,
                            use_container_width=True,
                            height=min(400, 50 * len(df_cat_clean) + 50),
                            key=f"tree_editor_{categoria_nome}_{st.session_state['batch_start']}"
                        )
                        
                        # Gestione selezioni per questa categoria
                        selected_indices = edited_df[edited_df["Aggiungi"] == True].index
                        if len(selected_indices) > 0:
                            col_add, col_info = st.columns([2, 1])
                            with col_add:
                                if st.button(
                                    f"➕ Aggiungi {len(selected_indices)} voci selezionate", 
                                    key=f"add_tree_{categoria_nome}_{st.session_state['batch_start']}", 
                                    type="primary",
                                    use_container_width=True
                                ):
                                    if 'selected_rows' not in st.session_state:
                                        st.session_state['selected_rows'] = []
                                    
                                    added_count = 0
                                    skipped_count = 0
                                    existing_items = set()
                                    
                                    # Costruisci set di voci già presenti
                                    for existing_row in st.session_state['selected_rows']:
                                        if 'TARIFFA' in existing_row:
                                            existing_items.add(existing_row['TARIFFA'])
                                    
                                    # Aggiungi le voci selezionate
                                    for display_idx in selected_indices:
                                        if display_idx < len(df_cat):
                                            row_data = df_cat.iloc[display_idx].to_dict()
                                            row_data.pop('Aggiungi', None)
                                            
                                            tariffa_id = row_data.get('TARIFFA', '')
                                            if tariffa_id not in existing_items:
                                                # Assegna categoria personalizzata se selezionata
                                                if st.session_state.get('selected_custom_category'):
                                                    row_data['_CUSTOM_CATEGORY'] = st.session_state['selected_custom_category']
                                                else:
                                                    row_data['_CUSTOM_CATEGORY'] = None
                                                
                                                st.session_state['selected_rows'].append(row_data)
                                                existing_items.add(tariffa_id)
                                                added_count += 1
                                            else:
                                                skipped_count += 1
                                    
                                    # Autosalva e mostra risultato
                                    if added_count > 0:
                                        auto_save_work_state()
                                        st.success(f"✅ Aggiunte {added_count} nuove voci al tuo elenco!")
                                    
                                    if skipped_count > 0:
                                        st.info(f"⏭️ Saltate {skipped_count} voci già presenti nel tuo elenco.")
                                    
                                    if added_count == 0 and skipped_count > 0:
                                        st.warning("⚠️ Tutte le voci selezionate erano già nel tuo elenco.")
                                    
                                    st.rerun()
                            
                            with col_info:
                                st.info(f"🎯 {len(selected_indices)} voci selezionate")
                        
                        st.markdown("---")

            # Navigazione batch migliorata
            col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
            with col_nav1:
                if st.session_state['batch_start'] > 0:
                    if st.button("⬅️ Precedenti", help="Vai alla pagina precedente", use_container_width=True):
                        st.session_state['batch_start'] = max(0, st.session_state['batch_start'] - batch_size)
                        st.rerun()
            with col_nav2:
                if total_pages > 1:
                    page_number = st.number_input(
                        f"Vai alla pagina (1-{total_pages})", 
                        min_value=1, 
                        max_value=total_pages, 
                        value=current_page,
                        key="page_input"
                    )
                    if page_number != current_page:
                        st.session_state['batch_start'] = (page_number - 1) * batch_size
                        st.rerun()
            with col_nav3:
                if st.session_state['batch_start'] + batch_size < total_found:
                    if st.button("➡️ Successivi", help="Vai alla pagina successiva", use_container_width=True):
                        st.session_state['batch_start'] += batch_size
                        st.rerun()
        else:
            st.warning("⚠️ Nessun risultato trovato per i criteri di ricerca specificati.")
    
    # ...existing code for tab_elenco...
        

