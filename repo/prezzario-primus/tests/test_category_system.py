"""
Test completo del sistema di categorie gerarchiche

Questo file testa tutte le funzionalità del sistema:
- Parsing delle categorie
- Validazione della sintassi
- Numerazione gerarchica
- Export/Import
- Casi edge

Esegui con: python tests/test_category_system.py

Autore: Sistema Prezzario Primus
Data: 16 luglio 2025
"""

import sys
import os
import json
from datetime import datetime

# Aggiungi il path per importare i moduli del progetto
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.category_parser import (
    parse_categories_from_text, 
    validate_category_syntax,
    generate_hierarchical_numbering,
    get_category_display_name,
    export_categories_to_dict,
    import_categories_from_dict
)


def test_basic_validation():
    """Test della validazione base"""
    print("\n🧪 Test 1: Validazione Base")
    print("-" * 50)
    
    test_cases = [
        ("", True, "Stringa vuota"),
        ("Edilizia", True, "Categoria singola"),
        ("Edilizia, Impianti", True, "Due categorie"),
        ("Edilizia,, Impianti", False, "Virgole consecutive"),
        (",Edilizia", False, "Inizia con virgola"),
        ("Edilizia,", False, "Finisce con virgola"),
        ("Edilizia ()", False, "Parentesi vuote"),
        ("(Edilizia)", False, "Inizia con parentesi"),
        ("Edilizia (Murature", False, "Parentesi non bilanciate"),
        ("Edilizia Murature)", False, "Parentesi di chiusura extra"),
    ]
    
    passed = 0
    for text, expected_valid, description in test_cases:
        is_valid, errors, warnings = validate_category_syntax(text)
        status = "✅" if is_valid == expected_valid else "❌"
        print(f"{status} {description}: '{text}' -> {'VALIDA' if is_valid else 'NON VALIDA'}")
        if is_valid == expected_valid:
            passed += 1
        if errors:
            print(f"   Errori: {errors}")
    
    print(f"\nRisultato: {passed}/{len(test_cases)} test passati")
    return passed == len(test_cases)


def test_parsing_basic():
    """Test del parsing base"""
    print("\n🧪 Test 2: Parsing Base")
    print("-" * 50)
    
    test_cases = [
        {
            "name": "Categorie semplici",
            "input": "Demolizioni, Costruzioni, Finiture, Impianti",
            "expected_count": 4,
            "expected_names": ["Demolizioni", "Costruzioni", "Finiture", "Impianti"],
            "expected_levels": [0, 0, 0, 0]
        },
        {
            "name": "Categoria singola",
            "input": "Edilizia",
            "expected_count": 1,
            "expected_names": ["Edilizia"],
            "expected_levels": [0]
        },
        {
            "name": "Con spazi extra",
            "input": " Edilizia ,  Impianti  , Finiture ",
            "expected_count": 3,
            "expected_names": ["Edilizia", "Impianti", "Finiture"],
            "expected_levels": [0, 0, 0]
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        
        categories = parse_categories_from_text(test_case['input'])
        
        # Verifica conteggio
        count_ok = len(categories) == test_case['expected_count']
        print(f"Conteggio: {'✅' if count_ok else '❌'} {len(categories)}/{test_case['expected_count']}")
        
        # Verifica nomi
        actual_names = [cat['name'] for cat in categories]
        names_ok = actual_names == test_case['expected_names']
        print(f"Nomi: {'✅' if names_ok else '❌'} {actual_names}")
        
        # Verifica livelli
        actual_levels = [cat['level'] for cat in categories]
        levels_ok = actual_levels == test_case['expected_levels']
        print(f"Livelli: {'✅' if levels_ok else '❌'} {actual_levels}")
        
        if count_ok and names_ok and levels_ok:
            passed += 1
    
    print(f"\nRisultato: {passed}/{len(test_cases)} test passati")
    return passed == len(test_cases)


def test_parsing_nested():
    """Test del parsing con parentesi annidate"""
    print("\n🧪 Test 3: Parsing Annidato")
    print("-" * 50)
    
    test_cases = [
        {
            "name": "Un livello di annidamento",
            "input": "Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici)",
            "expected_count": 6,
            "expected_names": ["Edilizia", "Murature", "Intonaci", "Impianti", "Elettrici", "Idraulici"],
            "expected_levels": [0, 1, 1, 0, 1, 1]
        },
        {
            "name": "Due livelli di annidamento",
            "input": "Costruzioni (Fondazioni (Scavi), Strutture (Pilastri))",
            "expected_count": 5,
            "expected_names": ["Costruzioni", "Fondazioni", "Scavi", "Strutture", "Pilastri"],
            "expected_levels": [0, 1, 2, 1, 2]
        },
        {
            "name": "Caso complesso",
            "input": "Impianti (Elettrici (Illuminazione), Idraulici (Tubazioni)), Finiture",
            "expected_count": 6,
            "expected_names": ["Impianti", "Elettrici", "Illuminazione", "Idraulici", "Tubazioni", "Finiture"],
            "expected_levels": [0, 1, 2, 1, 2, 0]
        },
        {
            "name": "Solo sotto-categorie",
            "input": "Edilizia (Murature, Intonaci, Pavimenti)",
            "expected_count": 4,
            "expected_names": ["Edilizia", "Murature", "Intonaci", "Pavimenti"],
            "expected_levels": [0, 1, 1, 1]
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        
        categories = parse_categories_from_text(test_case['input'])
        
        # Verifica conteggio
        count_ok = len(categories) == test_case['expected_count']
        print(f"Conteggio: {'✅' if count_ok else '❌'} {len(categories)}/{test_case['expected_count']}")
        
        # Verifica nomi
        actual_names = [cat['name'] for cat in categories]
        names_ok = actual_names == test_case['expected_names']
        print(f"Nomi: {'✅' if names_ok else '❌'} {actual_names}")
        if not names_ok:
            print(f"   Attesi: {test_case['expected_names']}")
            print(f"   Trovati: {actual_names}")
        
        # Verifica livelli
        actual_levels = [cat['level'] for cat in categories]
        levels_ok = actual_levels == test_case['expected_levels']
        print(f"Livelli: {'✅' if levels_ok else '❌'} {actual_levels}")
        if not levels_ok:
            print(f"   Attesi: {test_case['expected_levels']}")
            print(f"   Trovati: {actual_levels}")
        
        if count_ok and names_ok and levels_ok:
            passed += 1
    
    print(f"\nRisultato: {passed}/{len(test_cases)} test passati")
    return passed == len(test_cases)


def test_hierarchical_numbering():
    """Test della numerazione gerarchica"""
    print("\n🧪 Test 4: Numerazione Gerarchica")
    print("-" * 50)
    
    input_text = "Edilizia (Murature (Mattoni), Intonaci), Impianti (Elettrici, Idraulici), Finiture"
    print(f"Input: {input_text}")
    
    categories = parse_categories_from_text(input_text)
    numbered_cats = generate_hierarchical_numbering(categories)
    
    expected_numbers = ["1", "1.1", "1.1.1", "1.2", "2", "2.1", "2.2", "3"]
    actual_numbers = [cat['hierarchical_number'] for cat in numbered_cats]
    
    print("\nStruttura generata:")
    for cat in numbered_cats:
        print(f"   {cat['hierarchical_number']:>6}. {cat['display_name']}")
    
    numbers_ok = actual_numbers == expected_numbers
    print(f"\nNumerazione: {'✅' if numbers_ok else '❌'}")
    if not numbers_ok:
        print(f"   Attesi: {expected_numbers}")
        print(f"   Trovati: {actual_numbers}")
    
    return numbers_ok


def test_export_import():
    """Test dell'export/import JSON"""
    print("\n🧪 Test 5: Export/Import JSON")
    print("-" * 50)
    
    # Crea categorie di test
    input_text = "Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici)"
    categories = parse_categories_from_text(input_text)
    numbered_cats = generate_hierarchical_numbering(categories)
    
    print(f"Categorie originali: {len(numbered_cats)}")
    
    # Test export
    export_data = export_categories_to_dict(numbered_cats)
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    
    print(f"Export JSON: {'✅' if 'categories' in export_data else '❌'}")
    print(f"Dimensione JSON: {len(json_str)} caratteri")
    
    # Test import
    imported_cats = import_categories_from_dict(export_data)
    
    print(f"Categorie importate: {len(imported_cats)}")
    
    # Verifica coerenza
    original_names = [cat['name'] for cat in numbered_cats]
    imported_names = [cat['name'] for cat in imported_cats]
    
    names_match = original_names == imported_names
    print(f"Coerenza nomi: {'✅' if names_match else '❌'}")
    
    original_levels = [cat['level'] for cat in numbered_cats]
    imported_levels = [cat['level'] for cat in imported_cats]
    
    levels_match = original_levels == imported_levels
    print(f"Coerenza livelli: {'✅' if levels_match else '❌'}")
    
    return names_match and levels_match


def test_edge_cases():
    """Test di casi limite"""
    print("\n🧪 Test 6: Casi Limite")
    print("-" * 50)
    
    edge_cases = [
        ("", [], "Stringa vuota"),
        ("   ", [], "Solo spazi"),
        ("A", [("A", 0)], "Categoria minima"),
        ("A,B,C,D,E,F,G,H,I,J", [(f"{chr(65+i)}", 0) for i in range(10)], "Molte categorie"),
        ("A(B(C))", [("A", 0), ("B", 1), ("C", 2)], "Massima profondità"),
        ("A (B, C, D, E, F)", [("A", 0), ("B", 1), ("C", 1), ("D", 1), ("E", 1), ("F", 1)], "Molte sotto-categorie"),
    ]
    
    passed = 0
    for input_text, expected_structure, description in edge_cases:
        print(f"\n📝 {description}")
        print(f"Input: '{input_text}'")
        
        categories = parse_categories_from_text(input_text)
        
        if not expected_structure:
            # Caso di input vuoto
            empty_ok = len(categories) == 0
            print(f"Risultato vuoto: {'✅' if empty_ok else '❌'}")
            if empty_ok:
                passed += 1
        else:
            # Verifica struttura
            actual_structure = [(cat['name'], cat['level']) for cat in categories]
            structure_ok = actual_structure == expected_structure
            print(f"Struttura: {'✅' if structure_ok else '❌'}")
            print(f"   Atteso: {expected_structure}")
            print(f"   Trovato: {actual_structure}")
            if structure_ok:
                passed += 1
    
    print(f"\nRisultato: {passed}/{len(edge_cases)} test passati")
    return passed == len(edge_cases)


def run_all_tests():
    """Esegue tutti i test e mostra il riepilogo finale"""
    print("🚀 AVVIO TEST SISTEMA CATEGORIE GERARCHICHE")
    print("=" * 80)
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Esegui tutti i test
    test_results.append(("Validazione Base", test_basic_validation()))
    test_results.append(("Parsing Base", test_parsing_basic()))
    test_results.append(("Parsing Annidato", test_parsing_nested()))
    test_results.append(("Numerazione Gerarchica", test_hierarchical_numbering()))
    test_results.append(("Export/Import JSON", test_export_import()))
    test_results.append(("Casi Limite", test_edge_cases()))
    
    # Riepilogo finale
    print("\n" + "=" * 80)
    print("📊 RIEPILOGO FINALE")
    print("=" * 80)
    
    passed_count = 0
    for test_name, passed in test_results:
        status = "✅ PASSATO" if passed else "❌ FALLITO"
        print(f"{status:>12} | {test_name}")
        if passed:
            passed_count += 1
    
    total_tests = len(test_results)
    success_rate = (passed_count / total_tests) * 100
    
    print("-" * 80)
    print(f"TOTALE: {passed_count}/{total_tests} test passati ({success_rate:.1f}%)")
    
    if passed_count == total_tests:
        print("🎉 TUTTI I TEST SONO PASSATI! Il sistema è pronto per l'uso.")
    else:
        print("⚠️  Alcuni test sono falliti. Controllare l'implementazione.")
    
    return passed_count == total_tests


def demo_usage():
    """Dimostra l'uso pratico del sistema"""
    print("\n" + "=" * 80)
    print("🎯 DEMO UTILIZZO PRATICO")
    print("=" * 80)
    
    demo_inputs = [
        "Edilizia, Impianti, Finiture",
        "Edilizia (Murature, Intonaci), Impianti (Elettrici, Idraulici)",
        "Costruzioni (Fondazioni (Scavi, Pali), Strutture (Pilastri, Travi)), Finiture (Pavimenti, Rivestimenti)"
    ]
    
    for i, demo_input in enumerate(demo_inputs, 1):
        print(f"\n📝 Esempio {i}:")
        print(f"Input: {demo_input}")
        print()
        
        # Parsing
        categories = parse_categories_from_text(demo_input)
        numbered_cats = generate_hierarchical_numbering(categories)
        
        # Mostra risultato
        print("Struttura generata:")
        for cat in numbered_cats:
            print(f"   {cat['hierarchical_number']:>6}. {cat['display_name']}")
        
        print(f"Totale categorie: {len(numbered_cats)}")
        
        # Statistiche per livello
        level_counts = {0: 0, 1: 0, 2: 0}
        for cat in numbered_cats:
            level_counts[cat['level']] += 1
        
        print(f"Livello 0: {level_counts[0]}, Livello 1: {level_counts[1]}, Livello 2: {level_counts[2]}")


if __name__ == "__main__":
    # Esegui tutti i test
    success = run_all_tests()
    
    # Se tutti i test passano, mostra la demo
    if success:
        demo_usage()
    
    # Exit code per integrazione CI/CD
    sys.exit(0 if success else 1)
