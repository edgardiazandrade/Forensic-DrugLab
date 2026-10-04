import csv
with open('pH_vs_Ionizacion_Comparada_Datos.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        missing = []
        if not row.get("Solubilidad (Clarke's)"): missing.append('Solubilidad')
        if not row.get('Prueba presuntiva'): missing.append('Prueba')
        if not row.get('P1'): missing.append('IR')
        if not row.get('I1'): missing.append('MS')
        if missing:
            print(f"{row['Sustancia ']}: Faltan {missing}")
