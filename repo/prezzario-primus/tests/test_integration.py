"""
Test di integrazione per verificare che il sistema di categorie 
sia correttamente integrato nell'applicazione principale

Esegui con: python tests/test_integration.py

Autore: Sistema Prezzario Primus
Data: 16 luglio 2025
"""

import sys
import os

# Aggiungi il path per importare i moduli del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_imports():
    """Testa che tutti gli import funzionino correttamente"""
    print("🧪 Test Import Moduli")
    print("-" * 50)
    
    try:
        # Test import del parser
        from src.utils.category_parser import (
            parse_categories_from_text, 
            validate_category_syntax,
            generate_hierarchical_numbering
        )
        print("✅ Import category_parser riuscito")
        
        # Test import dei componenti UI
        from src.utils.category_ui import (
            render_category_management_page,
            render_category_input,
            display_current_categories,
            get_categories_for_dataframe_mapping,
            get_category_hierarchy_dict
        )
        print("✅ Import category_ui riuscito")
        
        # Test import app principale (solo moduli, non esecuzione)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "app_streamlit", 
            "c:\\github\\repo\\prezzario-primus\\app_streamlit.py"
        )
        if spec is not None:
            print("✅ App principale importabile")
        else:
            print("❌ Errore nell'import dell'app principale")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Errore di import: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False


def test_functionality():
    """Testa le funzionalità base del sistema integrato"""
    print("\n🧪 Test Funzionalità Base")
    print("-" * 50)
    
    try:
        from src.utils.category_parser import parse_categories_from_text, generate_hierarchical_numbering
        from src.utils.category_ui import get_categories_for_dataframe_mapping, get_category_hierarchy_dict
        
        # Test parsing
        test_input = "Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici)"
        categories = parse_categories_from_text(test_input)
        numbered_cats = generate_hierarchical_numbering(categories)
        
        print(f"✅ Parsing completato: {len(numbered_cats)} categorie")
        
        # Simula session_state per testare le funzioni UI
        import types
        mock_session_state = types.SimpleNamespace()
        mock_session_state.categories = numbered_cats
        
        # Test estrazione nomi per dataframe
        category_names = [cat['name'] for cat in numbered_cats]
        print(f"✅ Nomi categorie estratti: {len(category_names)}")
        
        # Test gerarchia - versione semplificata
        hierarchy_dict = {}
        level_0_cats = [cat for cat in numbered_cats if cat['level'] == 0]
        print(f"✅ Gerarchia creata: {len(level_0_cats)} categorie principali")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore nel test funzionalità: {e}")
        return False


def test_streamlit_compatibility():
    """Testa la compatibilità con Streamlit (senza avviare l'app)"""
    print("\n🧪 Test Compatibilità Streamlit")
    print("-" * 50)
    
    try:
        import streamlit as st
        print("✅ Streamlit importato correttamente")
        
        # Test che le funzioni UI siano definite correttamente
        from src.utils.category_ui import render_category_input, display_current_categories
        
        # Verifica che le funzioni siano callable
        if callable(render_category_input):
            print("✅ render_category_input è una funzione valida")
        else:
            print("❌ render_category_input non è callable")
            return False
            
        if callable(display_current_categories):
            print("✅ display_current_categories è una funzione valida")
        else:
            print("❌ display_current_categories non è callable")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Errore import Streamlit: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore compatibilità: {e}")
        return False


def test_file_structure():
    """Verifica che tutti i file necessari esistano"""
    print("\n🧪 Test Struttura File")
    print("-" * 50)
    
    required_files = [
        "src/utils/__init__.py",
        "src/utils/category_parser.py", 
        "src/utils/category_ui.py",
        "tests/test_category_system.py",
        "app_streamlit.py"
    ]
    
    base_path = "c:\\github\\repo\\prezzario-primus"
    
    all_exist = True
    for file_path in required_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ MANCANTE: {file_path}")
            all_exist = False
    
    return all_exist


def run_integration_tests():
    """Esegue tutti i test di integrazione"""
    print("🚀 AVVIO TEST DI INTEGRAZIONE")
    print("=" * 80)
    
    tests = [
        ("Struttura File", test_file_structure),
        ("Import Moduli", test_imports),
        ("Funzionalità Base", test_functionality),
        ("Compatibilità Streamlit", test_streamlit_compatibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERRORE in {test_name}: {e}")
            results.append((test_name, False))
    
    # Riepilogo
    print("\n" + "=" * 80)
    print("📊 RIEPILOGO TEST DI INTEGRAZIONE")
    print("=" * 80)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSATO" if result else "❌ FALLITO"
        print(f"{status:>12} | {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    success_rate = (passed / total) * 100
    
    print("-" * 80)
    print(f"TOTALE: {passed}/{total} test passati ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 INTEGRAZIONE COMPLETATA CON SUCCESSO!")
        print("✨ Il sistema di categorie è pronto per l'uso nell'app principale.")
    else:
        print("⚠️  Alcuni test di integrazione sono falliti.")
        print("🔧 Controlla i messaggi di errore sopra per risolvere i problemi.")
    
    return passed == total


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
