import csv
import io
from typing import List, Dict
def export_categories_to_csv(categories: List[Dict]) -> str:
    """
    Esporta le categorie in una stringa CSV.
    Colonne: name,level,id,hierarchical_number,display_name
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "level", "id", "hierarchical_number", "display_name"])
    for cat in categories:
        writer.writerow([
            cat['name'],
            cat['level'],
            cat['id'],
            cat.get('hierarchical_number', ''),
            cat.get('display_name', cat['name'])
        ])
    return output.getvalue()

def import_categories_from_csv(csv_content: str) -> List[Dict]:
    """
    Importa le categorie da una stringa CSV.
    """
    input_io = io.StringIO(csv_content)
    reader = csv.DictReader(input_io)
    categories = []
    for row in reader:
        category = {
            'name': row['name'],
            'level': int(row['level']),
            'id': row.get('id', generate_category_id()),
            'hierarchical_number': row.get('hierarchical_number', ''),
            'display_name': row.get('display_name', row['name'])
        }
        categories.append(category)
    return categories
"""
Sistema di parsing per categorie gerarchiche con sintassi a parentesi annidate.

Supporta sintassi come:
- Edilizia, Impianti, Finiture (categorie base)
- Edilizia (Murature, Intonaci), Impianti (categorie con sotto-livelli)
- Costruzioni (Fondazioni (Scavi), Strutture (Pilastri)) (3 livelli massimo)

Autore: Sistema Prezzario Primus
Data: 16 luglio 2025
"""

import uuid
import re
from typing import List, Dict, Tuple, Optional


def generate_category_id() -> str:
    """Genera un ID univoco per una categoria"""
    return str(uuid.uuid4())[:8]


def validate_category_syntax(text: str) -> Tuple[bool, List[str], List[str]]:
    """
    Valida la sintassi della stringa delle categorie
    Restituisce (is_valid: bool, errors: list, warnings: list)
    """
    if not text or not text.strip():
        return True, [], []
    
    errors = []
    warnings = []
    text = text.strip()
    
    # 1. Controllo parentesi bilanciate
    paren_count = 0
    
    for i, char in enumerate(text):
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
            if paren_count < 0:
                errors.append(f"Parentesi di chiusura ')' senza apertura alla posizione {i+1}")
                break
    
    if paren_count > 0:
        errors.append(f"Mancano {paren_count} parentesi di chiusura ')'")
    
    # 2. Controllo virgole problematiche
    if ',,' in text:
        errors.append("Virgole consecutive ',,' non sono permesse")
    
    if text.startswith(','):
        errors.append("La stringa non può iniziare con una virgola")
    
    if text.endswith(','):
        errors.append("La stringa non può finire con una virgola")
    
    # 3. Controllo parentesi vuote
    if re.search(r'\(\s*\)', text):
        errors.append("Trovate parentesi vuote '()' - ogni parentesi deve contenere almeno una categoria")
    
    # 4. Controllo livelli di annidamento (massimo 3 livelli: 0, 1, 2)
    max_depth = 0
    current_depth = 0
    for char in text:
        if char == '(':
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == ')':
            current_depth -= 1
    
    if max_depth > 3:
        errors.append(f"Troppi livelli di annidamento ({max_depth}). Massimo consentito: 3 livelli")
    
    # 5. Controllo che non inizi con parentesi
    if text.strip().startswith('('):
        errors.append("La stringa non può iniziare con parentesi - ogni categoria deve avere un nome")
    
    # 6. Controllo lunghezza nomi categorie
    category_names = re.findall(r'([^(),\s][^(),]*?)(?=\s*[(),]|$)', text)
    for name in category_names:
        name = name.strip()
        if not name or len(name) < 2:
            warnings.append(f"Nome categoria troppo corto: '{name}' (minimo 2 caratteri)")
    
    # 7. Controllo lunghezza totale
    if len(text) > 500:
        warnings.append(f"Stringa molto lunga ({len(text)} caratteri) - considerare di dividerla")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def parse_nested_parentheses(text: str) -> List[Dict]:
    """
    Parsa una stringa con parentesi annidate per creare una gerarchia
    Esempio: "Edilizia (Muratura (Mattoni))" -> 
    [
        {'name': 'Edilizia', 'level': 0},
        {'name': 'Muratura', 'level': 1}, 
        {'name': 'Mattoni', 'level': 2}
    ]
    """
    result = []
    text = text.strip()
    
    def extract_categories(s: str, current_level: int = 0) -> None:
        s = s.strip()
        if not s or current_level > 2:  # Limita ai livelli 0, 1, 2
            return
        
        # Trova la prima parentesi aperta
        paren_start = s.find('(')
        
        if paren_start == -1:
            # Nessuna parentesi, aggiungi categoria al livello corrente
            if s.strip():
                result.append({'name': s.strip(), 'level': current_level})
            return
        
        # Prendi la parte prima della parentesi come categoria del livello corrente
        main_category = s[:paren_start].strip()
        if main_category:
            result.append({'name': main_category, 'level': current_level})
        
        # Trova tutte le coppie di parentesi bilanciate nel contenuto
        content_parts = []
        paren_count = 0
        start_pos = paren_start + 1
        current_part = ""
        i = start_pos
        
        while i < len(s):
            char = s[i]
            if char == '(':
                paren_count += 1
                current_part += char
            elif char == ')':
                if paren_count == 0:
                    # Questa è la parentesi di chiusura principale
                    if current_part.strip():
                        content_parts.append(current_part.strip())
                    break
                else:
                    paren_count -= 1
                    current_part += char
            elif char == ',' and paren_count == 0:
                # Virgola al livello principale dentro le parentesi
                if current_part.strip():
                    content_parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
            i += 1
        
        # Se siamo arrivati alla fine senza trovare la parentesi di chiusura
        if i >= len(s) and current_part.strip():
            content_parts.append(current_part.strip())
        
        # Processa ogni parte del contenuto
        for part in content_parts:
            if part.strip():
                extract_categories(part.strip(), current_level + 1)
    
    extract_categories(text)
    return result


def parse_categories_from_text(text: str) -> List[Dict]:
    """Parsa le categorie da testo con virgole e parentesi annidate per creare struttura gerarchica"""
    if not text or not text.strip():
        return []
    
    # Prima valida la sintassi
    is_valid, errors, warnings = validate_category_syntax(text)
    if not is_valid:
        print(f"⚠️ Sintassi non valida: {errors}")
        return []  # Restituisce lista vuota per input non validi
    
    hierarchical_cats = []
    
    # Dividi per virgole ESTERNE (non dentro parentesi) per ottenere le categorie principali
    main_categories = []
    current_category = ""
    paren_count = 0
    
    for char in text:
        if char == '(':
            paren_count += 1
            current_category += char
        elif char == ')':
            paren_count -= 1
            current_category += char
        elif char == ',' and paren_count == 0:
            # Virgola esterna - separa le categorie principali
            if current_category.strip():
                main_categories.append(current_category.strip())
            current_category = ""
        else:
            current_category += char
    
    # Aggiungi l'ultima categoria se non vuota
    if current_category.strip():
        main_categories.append(current_category.strip())
    
    for main_cat in main_categories:
        # Per ogni categoria principale, analizza le parentesi annidate
        nested_structure = parse_nested_parentheses(main_cat)
        
        # Aggiungi tutte le categorie della struttura annidata
        for cat_data in nested_structure:
            # Limita i livelli a massimo 2 (0, 1, 2)
            level = min(cat_data['level'], 2)
            hierarchical_cats.append({
                'name': cat_data['name'],
                'level': level,
                'id': generate_category_id()
            })
    
    return hierarchical_cats


def get_category_display_name(category: Dict, hierarchical_number: str = "") -> str:
    """Restituisce il nome della categoria con indentazione visiva e numerazione gerarchica"""
    indent = "　　" * category['level']  # Usa spazi wide per indentazione
    level_prefix = ""
    if category['level'] == 0:
        level_prefix = "📁 "
    elif category['level'] == 1:
        level_prefix = "📂 "
    elif category['level'] == 2:
        level_prefix = "📄 "
    
    # Aggiungi numerazione gerarchica se fornita
    number_prefix = f"{hierarchical_number}. " if hierarchical_number else ""
    
    return f"{indent}{level_prefix}{number_prefix}{category['name']}"


def generate_hierarchical_numbering(hierarchical_categories: List[Dict]) -> List[Dict]:
    """Genera numerazione gerarchica per le categorie (1, 1.1, 1.2, 1.1.1, 2, 2.1, ecc.)"""
    numbered_categories = []
    level_counters = [0, 0, 0]  # Contatori per livelli 0, 1, 2
    
    for category in hierarchical_categories:
        level = category['level']
        
        # Incrementa il contatore per il livello corrente
        level_counters[level] += 1
        
        # Reset dei contatori dei livelli inferiori
        for i in range(level + 1, len(level_counters)):
            level_counters[i] = 0
        
        # Genera il numero gerarchico
        hierarchical_number = ""
        if level == 0:
            hierarchical_number = str(level_counters[0])
        elif level == 1:
            hierarchical_number = f"{level_counters[0]}.{level_counters[1]}"
        elif level == 2:
            hierarchical_number = f"{level_counters[0]}.{level_counters[1]}.{level_counters[2]}"
        
        # Crea una copia della categoria con il numero gerarchico
        numbered_category = category.copy()
        numbered_category['hierarchical_number'] = hierarchical_number
        numbered_category['display_name'] = get_category_display_name(category, hierarchical_number)
        
        numbered_categories.append(numbered_category)
    
    return numbered_categories
