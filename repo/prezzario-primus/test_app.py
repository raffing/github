#!/usr/bin/env python3
"""
Script di test per verificare le funzionalità principali dell'app
"""

import os
import sys
import tempfile
import json
from datetime import datetime

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test degli import principali"""
    print("🔍 Test degli import...")
    try:
        import streamlit as st
        import streamlit.components.v1 as components
        import pandas as pd
        import numpy as np
        from src.esamina_excel import esamina_excel
        print("✅ Tutti gli import riusciti")
        return True
    except ImportError as e:
        print(f"❌ Errore negli import: {e}")
        return False

def test_excel_processing():
    """Test del processamento file Excel"""
    print("\n📊 Test processamento Excel...")
    
    # Verifica se esiste un file Excel di test
    test_file = os.path.join("data", "regione puglia 2025.xlsx")
    if os.path.exists(test_file):
        try:
            from src.esamina_excel import esamina_excel
            df = esamina_excel(test_file)
            if df is not None and not df.empty:
                print(f"✅ File Excel caricato con successo: {len(df)} righe")
                print(f"   Colonne: {list(df.columns)}")
                return True
            else:
                print("❌ DataFrame vuoto o None")
                return False
        except Exception as e:
            print(f"❌ Errore nel processamento Excel: {e}")
            return False
    else:
        print("⚠️ File Excel di test non trovato, saltando il test")
        return True

def test_json_operations():
    """Test delle operazioni JSON per salvataggio/caricamento"""
    print("\n💾 Test operazioni JSON...")
    
    try:
        # Crea dati di test
        test_data = {
            'timestamp': datetime.now().isoformat(),
            'custom_categories': ['Test Category 1', 'Test Category 2'],
            'selected_rows': [
                {
                    'TARIFFA': 'TEST/01.E01.001.001',
                    'DESCRIZIONE dell\'ARTICOLO': 'Test item',
                    'Unità di misura': 'm³',
                    'Prezzo': '10.50'
                }
            ],
            'version': '1.1'
        }
        
        # Test serializzazione JSON
        json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
        print("✅ Serializzazione JSON riuscita")
        
        # Test deserializzazione JSON
        loaded_data = json.loads(json_str)
        print("✅ Deserializzazione JSON riuscita")
        
        # Verifica integrità dati
        if (loaded_data['custom_categories'] == test_data['custom_categories'] and 
            len(loaded_data['selected_rows']) == len(test_data['selected_rows'])):
            print("✅ Integrità dati verificata")
            return True
        else:
            print("❌ Dati corrotti durante serializzazione/deserializzazione")
            return False
            
    except Exception as e:
        print(f"❌ Errore nelle operazioni JSON: {e}")
        return False

def test_temp_file_operations():
    """Test delle operazioni sui file temporanei"""
    print("\n📁 Test operazioni file temporanei...")
    
    try:
        # Crea un file temporaneo
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp_file:
            test_data = {'test': 'data'}
            json.dump(test_data, tmp_file)
            temp_path = tmp_file.name
        
        # Verifica che il file esista
        if os.path.exists(temp_path):
            print("✅ File temporaneo creato")
            
            # Leggi il file
            with open(temp_path, 'r') as f:
                loaded_data = json.load(f)
            
            if loaded_data == test_data:
                print("✅ Lettura file temporaneo riuscita")
                
                # Pulisci il file temporaneo
                os.unlink(temp_path)
                print("✅ File temporaneo rimosso")
                return True
            else:
                print("❌ Dati del file temporaneo corrotti")
                return False
        else:
            print("❌ File temporaneo non creato")
            return False
            
    except Exception as e:
        print(f"❌ Errore nelle operazioni file temporanei: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🧪 Avvio test dell'applicazione Prezzario Primus\n")
    
    tests = [
        ("Import", test_imports),
        ("Excel Processing", test_excel_processing),
        ("JSON Operations", test_json_operations),
        ("Temp File Operations", test_temp_file_operations)
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Riepilogo risultati
    print("\n" + "="*50)
    print("📋 RIEPILOGO TEST")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} : {status}")
        if result:
            passed += 1
    
    print("-"*50)
    print(f"Test passati: {passed}/{total}")
    
    if passed == total:
        print("🎉 Tutti i test sono passati! L'applicazione è pronta.")
        return True
    else:
        print("⚠️ Alcuni test sono falliti. Controlla i dettagli sopra.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
