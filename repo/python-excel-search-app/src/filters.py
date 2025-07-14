def filter_data(data, search_term, column=None):
    filtered_data = []
    for row in data:
        if column is not None:
            if search_term.lower() in str(row[column]).lower():
                filtered_data.append(row)
        else:
            if any(search_term.lower() in str(cell).lower() for cell in row):
                filtered_data.append(row)
    return filtered_data

def group_by_tariff(data):
    grouped_data = {}
    for row in data:
        tariff = row.get('Tariffa')
        if tariff not in grouped_data:
            grouped_data[tariff] = []
        grouped_data[tariff].append(row)
    return grouped_data

def apply_filters(data, search_term, column=None):
    filtered_data = filter_data(data, search_term, column)
    grouped_data = group_by_tariff(filtered_data)
    return grouped_data