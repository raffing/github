import re
def raggruppa_per_lettera_tariffa(df):
    """
    Raggruppa i record del DataFrame per lettera/le lettere contenute nel campo 'TARIFFA'.
    Restituisce un dizionario: {lettera: DataFrame}
    """
    if 'TARIFFA' not in df.columns:
        print("Colonna 'TARIFFA' non trovata!")
        return {}
    # Estrai la/le lettere dopo la prima '/' e prima del prossimo punto
    def estrai_lettere(tariffa):
        if pd.isna(tariffa):
            return None
        match = re.search(r'/\d+\.([A-Z]+)', str(tariffa))
        if match:
            return match.group(1)
        return None
    df['LIVELLO_LETTERA'] = df['TARIFFA'].apply(estrai_lettere)
    gruppi = {}
    for lettera, gruppo in df.groupby('LIVELLO_LETTERA'):
        gruppi[lettera] = gruppo
    return gruppi
import pandas as pd
import os

def esamina_excel(percorso_file):
    if not os.path.exists(percorso_file):
        print(f"File non trovato: {percorso_file}")
        return None
    try:
        import openpyxl
        wb = openpyxl.load_workbook(percorso_file, read_only=True, data_only=True)
        if 'Elenco Prezzi' not in wb.sheetnames:
            print("Foglio 'Elenco Prezzi' non trovato!")
            return None
        ws = wb['Elenco Prezzi']
        # Trova la riga header
        header_row = None
        for idx, row in enumerate(ws.iter_rows(min_row=1, max_row=20, values_only=True)):
            if row and any('TARIFFA' in str(cell).upper() for cell in row if cell):
                header_row = idx
                break
        if header_row is None:
            print("Header 'TARIFFA' non trovato!")
            return None
        # Carica tutte le righe dopo l'header
        data_rows = list(ws.iter_rows(min_row=header_row+2, values_only=True))
        # Salta la prima riga se contiene 'Voce riservata'
        if data_rows and data_rows[0] and any('VOCE RISERVATA' in str(cell).upper() for cell in data_rows[0] if cell):
            data_rows = data_rows[1:]
        records = []
        i = 0
        while i < len(data_rows):
            row = data_rows[i]
            codice = str(row[1]).strip() if row and len(row) > 1 and row[1] else ''
            if codice.startswith('PUG'):
                descrizione = str(row[2]).strip() if len(row) > 2 and row[2] else ''
                # Cerca la riga successiva per unità/prezzo
                unita = ''
                prezzo = ''
                if i+1 < len(data_rows):
                    next_row = data_rows[i+1]
                    unita = str(next_row[3]).strip() if len(next_row) > 3 and next_row[3] else ''
                    prezzo = str(next_row[4]).strip() if len(next_row) > 4 and next_row[4] else ''
                records.append({
                    'TARIFFA': codice,
                    "DESCRIZIONE dell'ARTICOLO": descrizione,
                    'Unità di misura': unita,
                    'Prezzo': prezzo
                })
                i += 2
            else:
                i += 1
        df = pd.DataFrame(records)
        print(f"Colonne rilevate: {df.columns.tolist()}")
        print(df.head(10))
        return df
    except Exception as e:
        print(f"Errore durante la lettura del file: {e}")
        return None

if __name__ == "__main__":
    percorso = os.path.join("data", "regione puglia 2025.xlsx")
    df = esamina_excel(percorso)
    if df is not None:
        gruppi = raggruppa_per_lettera_tariffa(df)
        print(f"Raggruppamento per lettere LIVELLO_LETTERA trovate: {list(gruppi.keys())}")
        # Mostra un esempio per una lettera
        for lettera, gruppo in gruppi.items():
            print(f"\n--- Record per lettera {lettera} ---")
            print(gruppo.head(3))
            break
