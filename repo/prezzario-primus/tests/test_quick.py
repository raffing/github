"""
Test Manuale Rapido per il Sistema di Categorie

Esegui questo script per testare rapidamente che tutto funzioni.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_quick():
    print("🚀 TEST RAPIDO SISTEMA CATEGORIE")
    print("=" * 50)
    
    # Test 1: Import
    try:
        from src.utils.category_parser import parse_categories_from_text, generate_hierarchical_numbering
        from src.utils.category_ui import get_categories_for_dataframe_mapping
        print("✅ Import riusciti")
    except Exception as e:
        print(f"❌ Errore import: {e}")
        return False
    
    # Test 2: Parsing
    test_input = "Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici), Finiture"
    try:
        categories = parse_categories_from_text(test_input)
        numbered = generate_hierarchical_numbering(categories)
        
        print(f"✅ Parsing riuscito: {len(numbered)} categorie")
        
        # Mostra struttura
        print("\n📊 Struttura generata:")
        for cat in numbered:
            print(f"   {cat['hierarchical_number']:>4}. {cat['display_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore parsing: {e}")
        return False

if __name__ == "__main__":
    success = test_quick()
    print(f"\n{'🎉 SUCCESSO!' if success else '❌ FALLITO'}")
    sys.exit(0 if success else 1)
