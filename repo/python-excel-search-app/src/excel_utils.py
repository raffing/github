def read_excel_file(filepath):
    import pandas as pd
    try:
        data = pd.read_excel(filepath)
        return data
    except Exception as e:
        print(f"Error reading the Excel file: {e}")
        return None

def get_headers(data):
    if data is not None:
        return list(data.columns)
    return []

def extract_data(data):
    if data is not None:
        return data.to_dict(orient='records')
    return []

def filter_data(data, search_term):
    if data is not None:
        filtered_data = [row for row in data if any(search_term.lower() in str(value).lower() for value in row.values())]
        return filtered_data
    return []

def group_by_tariff(data):
    if data is not None:
        grouped_data = {}
        for row in data:
            tariff = row.get('Tariffa')
            if tariff not in grouped_data:
                grouped_data[tariff] = []
            grouped_data[tariff].append(row)
        return grouped_data
    return {}