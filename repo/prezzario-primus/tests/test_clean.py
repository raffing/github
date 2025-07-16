"""
Test senza warning di Streamlit

Questo file esegue i test principali sopprimendo i warning di ScriptRunContext
che sono normali quando si importano moduli Streamlit fuori dall'app.
"""

import sys
import os
import warnings

# Sopprimi i warning di Streamlit
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")

# Sopprimi anche i log di Streamlit
import logging
logging.getLogger("streamlit").setLevel(logging.ERROR)

# Aggiungi il path per importare i moduli del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_clean():
    print("🧪 TEST PULITO SENZA WARNING")
    print("=" * 50)
    
    # Test 1: Import
    try:
        from src.utils.category_parser import parse_categories_from_text, generate_hierarchical_numbering
        print("✅ Import category_parser riusciti")
    except Exception as e:
        print(f"❌ Errore import parser: {e}")
        return False
    
    # Test 2: Parsing
    test_input = "Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici), Finiture"
    try:
        categories = parse_categories_from_text(test_input)
        numbered = generate_hierarchical_numbering(categories)
        
        print(f"✅ Parsing riuscito: {len(numbered)} categorie")
        
        # Mostra struttura compatta
        print("\n📊 Struttura:")
        for cat in numbered[:3]:  # Mostra solo le prime 3
            print(f"   {cat['hierarchical_number']}. {cat['name']} (L{cat['level']})")
        if len(numbered) > 3:
            print(f"   ... e altre {len(numbered) - 3} categorie")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore parsing: {e}")
        return False

def test_app_syntax():
    """Testa che l'app principale non abbia errori di sintassi"""
    print("\n🧪 TEST SINTASSI APP PRINCIPALE")
    print("=" * 50)
    
    try:
        import py_compile
        py_compile.compile("app_streamlit.py", doraise=True)
        print("✅ Sintassi app_streamlit.py corretta")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Errore sintassi: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TEST RAPIDO E PULITO")
    print("=" * 60)
    
    success1 = test_clean()
    success2 = test_app_syntax()
    
    overall_success = success1 and success2
    
    print("\n" + "=" * 60)
    if overall_success:
        print("🎉 TUTTI I TEST PASSATI - SISTEMA PRONTO!")
    else:
        print("⚠️  Alcuni test falliti - controllare errori sopra")
    
    print("=" * 60)
    sys.exit(0 if overall_success else 1)
