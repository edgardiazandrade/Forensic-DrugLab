import csv

filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
rows = []

updates = {
    'GHB': {
        'Prueba presuntiva': 'Prueba de Nitrato de Cobalto',
        'Color característico': 'Rosa a violeta',
        'ms': ['147', '73', '75', '233', '117', '148', '77', '59']
    },
    'Anfetamina': {
        'Prueba presuntiva': 'Prueba de Marquis',
        'Color característico': 'Naranja a marrón',
        'ms': ['44', '91', '40', '42', '65', '45', '39', '43']
    },
    'Codeína': {
        'Prueba presuntiva': 'Prueba de Marquis',
        'Color característico': 'Violeta',
        'ms': ['299', '42', '162', '124', '229', '59', '300', '69']
    },
    'Diazepam': {
        'Prueba presuntiva': 'Prueba de Formaldehído-ácido sulfúrico',
        'Color característico': 'Naranja',
        'ms': ['256', '283', '284', '285', '257', '255', '258', '286']
    },
    'Alprazolam': {
        'Prueba presuntiva': 'N/A',
        'Color característico': 'N/A',
        'ms': ['308', '279', '204', '273', '77', '307', '310', '309']
    },
    'Fenobarbital': {
        'Prueba presuntiva': 'Prueba de Koppanyi-Zwikker',
        'Color característico': 'Violeta',
        'ms': ['204', '117', '146', '161', '77', '103', '115', '118']
    },
    '2CB': {
        'Prueba presuntiva': 'Prueba de Marquis',
        'Color característico': 'Amarillo a verde',
        'ir': ['1250', '1500', '825', '740', '750', ''],
        'ms': ['230', '232', '215', '217', '77', '259', '261', '91']
    }
}

with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        sus = row['Sustancia ']
        if sus in ['pH', 'Ph'] or sus.isdigit() or not sus.strip():
            continue # skip junk
        if sus in updates:
            u = updates[sus]
            if 'Prueba presuntiva' in u:
                row['Prueba presuntiva'] = u['Prueba presuntiva']
                row['Color característico'] = u['Color característico']
            if 'ms' in u:
                for i, v in enumerate(u['ms']):
                    row[f'I{i+1}'] = v
            if 'ir' in u:
                for i, v in enumerate(u['ir']):
                    row[f'P{i+1}'] = v
        rows.append(row)

with open(filepath, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print('Base de datos completada y purgada de filas basura.')
