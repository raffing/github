"""
Componenti Streamlit per la gestione delle categorie gerarchiche

Questo modulo contiene tutti i componenti UI necessari per:
- Input e validazione delle categorie
- Visualizzazione delle categorie attuali
- Export/Import delle categorie
- Integrazione con il sistema principale

Autore: Sistema Prezzario Primus
Data: 16 luglio 2025
"""

import streamlit as st
import json
from datetime import datetime
from typing import List, Dict, Optional

from .category_parser import (
    parse_categories_from_text, 
    validate_category_syntax,
    generate_hierarchical_numbering,
    get_category_display_name,
    export_categories_to_dict,
    import_categories_from_dict
)


def render_category_input() -> str:
    """
    Renderizza l'interfaccia per l'input delle categorie con sintassi gerarchica
    Restituisce il testo di input inserito dall'utente
    """
    
    st.subheader("📋 Gestione Categorie Gerarchiche")
    
    # Sezione di aiuto
    with st.expander("ℹ️ Sintassi delle Categorie", expanded=False):
        st.markdown("""
        **Regole per la sintassi:**
        - Usa le **virgole** `,` per separare categorie allo stesso livello
        - Usa le **parentesi** `()` per creare sotto-livelli (massimo 3 livelli: 0, 1, 2)
        - Le virgole **dentro** le parentesi creano nodi fratelli nello stesso sotto-livello
        
        **Esempi:**
        ```
        Edilizia, Impianti, Finiture
        → 3 categorie di livello 0
        
        Edilizia (Murature, Intonaci), Impianti
        → Edilizia con 2 sotto-categorie + Impianti
        
        Costruzioni (Fondazioni (Scavi), Strutture (Pilastri))
        → Struttura a 3 livelli con ramificazioni
        
        Impianti (Elettrici (Illuminazione), Idraulici (Tubazioni)), Finiture
        → Esempio complesso con più rami
        ```
        """)
    
    # Area di input
    st.markdown("**Inserisci le categorie:**")
    category_input = st.text_area(
        "Categorie",
        height=100,
        placeholder="Esempio: Edilizia (Murature (Mattoni), Intonaci), Impianti (Elettrici, Idraulici), Finiture",
        help="Usa virgole per separare, parentesi per i sotto-livelli",
        label_visibility="collapsed",
        key="category_input_area"
    )
    
    # Validazione in tempo reale
    validation_container = st.container()
    
    if category_input.strip():
        is_valid, errors, warnings = validate_category_syntax(category_input)
        
        with validation_container:
            if not is_valid:
                st.error("❌ **Sintassi non valida:**")
                for error in errors:
                    st.error(f"   • {error}")
            else:
                st.success("✅ **Sintassi valida**")
                
                if warnings:
                    st.warning("⚠️ **Avvertimenti:**")
                    for warning in warnings:
                        st.warning(f"   • {warning}")
    
    # Pulsante per processare
    col1, col2 = st.columns([1, 3])
    
    with col1:
        process_button = st.button(
            "🔄 Elabora Categorie", 
            disabled=not category_input.strip(),
            type="primary",
            key="process_categories_btn"
        )
    
    # Processa le categorie
    if process_button and category_input.strip():
        is_valid, errors, warnings = validate_category_syntax(category_input)
        
        if is_valid:
            # Parsa le categorie
            hierarchical_cats = parse_categories_from_text(category_input)
            
            if hierarchical_cats:
                # Genera numerazione gerarchica
                numbered_cats = generate_hierarchical_numbering(hierarchical_cats)
                
                # Salva in session state
                st.session_state.categories = numbered_cats
                st.session_state.categories_input = category_input
                
                st.success(f"✅ **{len(numbered_cats)} categorie elaborate con successo!**")
                
                # Mostra anteprima struttura
                st.markdown("**📊 Struttura generata:**")
                preview_container = st.container()
                
                with preview_container:
                    for cat in numbered_cats:
                        st.markdown(f"`{cat['hierarchical_number']:>6}` {cat['display_name']}")
                
                # Pulsante per confermare
                if st.button("💾 Salva Categorie", key="save_cats"):
                    st.session_state.categories_confirmed = True
                    st.success("Categorie salvate!")
                    st.rerun()
            else:
                st.error("Nessuna categoria valida trovata.")
        else:
            st.error("Impossibile elaborare: correggi gli errori di sintassi.")
    
    return category_input


def display_current_categories() -> None:
    """Mostra le categorie attualmente caricate"""
    
    if 'categories' in st.session_state and st.session_state.categories:
        st.subheader("📚 Categorie Attuali")
        
        categories = st.session_state.categories
        
        # Statistiche
        col1, col2, col3, col4 = st.columns(4)
        
        level_counts = {0: 0, 1: 0, 2: 0}
        for cat in categories:
            level_counts[cat['level']] += 1
        
        with col1:
            st.metric("Totale", len(categories))
        with col2:
            st.metric("Livello 0", level_counts[0])
        with col3:
            st.metric("Livello 1", level_counts[1])
        with col4:
            st.metric("Livello 2", level_counts[2])
        
        # Lista delle categorie
        with st.expander("📋 Lista Completa", expanded=True):
            for cat in categories:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{cat['display_name']}")
                with col2:
                    st.code(f"L{cat['level']}")
        
        # Azioni
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ Cancella Tutte", key="clear_all_cats"):
                del st.session_state.categories
                if 'categories_confirmed' in st.session_state:
                    del st.session_state.categories_confirmed
                if 'categories_input' in st.session_state:
                    del st.session_state.categories_input
                st.rerun()
        
        with col2:
            if st.button("📝 Modifica", key="edit_cats"):
                if 'categories_input' in st.session_state:
                    st.session_state.edit_mode = True
                    st.rerun()
        
        with col3:
            # Export JSON
            export_data = export_categories_to_dict(categories)
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                "📥 Export JSON",
                data=json_str,
                file_name=f"categorie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="export_cats_btn"
            )


def render_category_import() -> None:
    """Renderizza l'interfaccia per importare categorie da file JSON"""
    
    st.subheader("📥 Importa Categorie")
    
    uploaded_file = st.file_uploader(
        "Seleziona file JSON delle categorie",
        type=['json'],
        help="Carica un file JSON esportato precedentemente",
        key="category_import_file"
    )
    
    if uploaded_file is not None:
        try:
            # Leggi il contenuto del file
            content = uploaded_file.read().decode('utf-8')
            data = json.loads(content)
            
            # Importa le categorie
            imported_categories = import_categories_from_dict(data)
            
            if imported_categories:
                st.success(f"✅ **{len(imported_categories)} categorie importate con successo!**")
                
                # Mostra anteprima
                with st.expander("📋 Anteprima Categorie Importate", expanded=True):
                    for cat in imported_categories:
                        st.markdown(f"{cat['display_name']}")
                
                # Pulsanti di azione
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Sostituisci Categorie Attuali", key="replace_cats"):
                        st.session_state.categories = imported_categories
                        st.session_state.categories_confirmed = True
                        st.success("Categorie sostituite!")
                        st.rerun()
                
                with col2:
                    if st.button("➕ Aggiungi alle Categorie Attuali", key="append_cats"):
                        if 'categories' in st.session_state and st.session_state.categories:
                            st.session_state.categories.extend(imported_categories)
                        else:
                            st.session_state.categories = imported_categories
                        st.session_state.categories_confirmed = True
                        st.success("Categorie aggiunte!")
                        st.rerun()
            else:
                st.error("❌ Nessuna categoria valida trovata nel file")
                
        except json.JSONDecodeError as e:
            st.error(f"❌ Errore nel parsing del JSON: {str(e)}")
        except Exception as e:
            st.error(f"❌ Errore durante l'importazione: {str(e)}")


def render_category_selection(categories: List[Dict], key_prefix: str = "cat_sel") -> Optional[Dict]:
    """
    Renderizza un selettore per scegliere una categoria dalla lista
    Restituisce la categoria selezionata o None
    """
    
    if not categories:
        st.warning("⚠️ Nessuna categoria disponibile")
        return None
    
    # Crea le opzioni per il selectbox
    options = ["Nessuna selezione"] + [cat['display_name'] for cat in categories]
    
    selected_option = st.selectbox(
        "Seleziona una categoria:",
        options=options,
        key=f"{key_prefix}_selectbox"
    )
    
    if selected_option == "Nessuna selezione":
        return None
    
    # Trova la categoria corrispondente
    for cat in categories:
        if cat['display_name'] == selected_option:
            return cat
    
    return None


def render_category_management_page() -> None:
    """
    Renderizza una pagina completa per la gestione delle categorie
    Utilizzabile come pagina standalone o come sezione del main app
    """
    
    st.title("📋 Sistema di Categorie Gerarchiche")
    
    # Tab per organizzare le funzionalità
    tab1, tab2, tab3 = st.tabs(["📝 Crea Categorie", "📚 Gestisci Categorie", "📥 Import/Export"])
    
    with tab1:
        st.markdown("### Creazione Nuove Categorie")
        category_input = render_category_input()
    
    with tab2:
        st.markdown("### Categorie Attuali")
        display_current_categories()
        
        # Modalità modifica
        if st.session_state.get('edit_mode', False):
            st.markdown("### 📝 Modalità Modifica")
            
            if 'categories_input' in st.session_state:
                edited_input = st.text_area(
                    "Modifica categorie:",
                    value=st.session_state.categories_input,
                    height=100,
                    key="edit_categories_area"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("💾 Salva Modifiche", key="save_edit"):
                        # Rielabora le categorie modificate
                        is_valid, errors, warnings = validate_category_syntax(edited_input or "")
                        if is_valid:
                            hierarchical_cats = parse_categories_from_text(edited_input or "")
                            numbered_cats = generate_hierarchical_numbering(hierarchical_cats)
                            st.session_state.categories = numbered_cats
                            st.session_state.categories_input = edited_input
                            st.session_state.edit_mode = False
                            st.success("Modifiche salvate!")
                            st.rerun()
                        else:
                            st.error("Impossibile salvare: correggi gli errori di sintassi")
                
                with col2:
                    if st.button("❌ Annulla", key="cancel_edit"):
                        st.session_state.edit_mode = False
                        st.rerun()
    
    with tab3:
        st.markdown("### Import/Export Categorie")
        render_category_import()


def get_categories_for_dataframe_mapping() -> List[str]:
    """
    Restituisce una lista di nomi di categorie per il mapping con dataframe
    Utilizzabile per assegnare categorie alle tariffe
    """
    
    if 'categories' not in st.session_state or not st.session_state.categories:
        return []
    
    # Restituisce solo i nomi delle categorie senza formattazione
    return [cat['name'] for cat in st.session_state.categories]


def get_category_hierarchy_dict() -> Dict:
    """
    Restituisce un dizionario con la gerarchia delle categorie
    Formato: {'categoria_padre': ['sottocategoria1', 'sottocategoria2']}
    """
    
    if 'categories' not in st.session_state or not st.session_state.categories:
        return {}
    
    hierarchy = {}
    categories = st.session_state.categories
    
    # Raggruppa per livello
    level_0_cats = [cat for cat in categories if cat['level'] == 0]
    level_1_cats = [cat for cat in categories if cat['level'] == 1]
    level_2_cats = [cat for cat in categories if cat['level'] == 2]
    
    # Crea la mappatura gerarchica
    for i, cat_0 in enumerate(level_0_cats):
        hierarchy[cat_0['name']] = []
        
        # Trova le sottocategorie di livello 1
        start_idx = categories.index(cat_0) + 1
        
        for j in range(start_idx, len(categories)):
            if categories[j]['level'] == 0:
                break
            elif categories[j]['level'] == 1:
                hierarchy[cat_0['name']].append(categories[j]['name'])
    
    return hierarchy
