import csv

filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['Sustancia ']}: pKa={row['pKa']}, Char={row['Carácter']}, Solv_acid={row['Disolvente        <']}, Solv_base={row['>       Disolvente']}")
