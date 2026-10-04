import csv
with open('pH_vs_Ionizacion_Comparada_Datos.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        print(f"{row['Sustancia ']}: {row['pKa']} - {row['Carácter']}")
