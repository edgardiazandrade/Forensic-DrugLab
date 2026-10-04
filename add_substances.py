import csv
import os

filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
new_data = [
    {'Sustancia ': 'GHB', 'pKa': '4.7', 'Carácter': 'Ácido', "Solubilidad (Clarke's)": 'Soluble en agua y alcohol.'},
    {'Sustancia ': 'Anfetamina', 'pKa': '9.9', 'Carácter': 'Base', "Solubilidad (Clarke's)": 'Soluble 1 en 50 de agua; soluble en etanol y éter.'},
    {'Sustancia ': 'Codeína', 'pKa': '8.2', 'Carácter': 'Base', "Solubilidad (Clarke's)": 'Soluble 1 en 120 de agua, 1 en 2 de etanol, 1 en 0.5 de cloroformo.'},
    {'Sustancia ': 'Diazepam', 'pKa': '3.4', 'Carácter': 'Base', "Solubilidad (Clarke's)": 'Ligeramente soluble en agua; soluble 1 en 25 de etanol, 1 en 2 de cloroformo.'},
    {'Sustancia ': 'Alprazolam', 'pKa': '2.4', 'Carácter': 'Base', "Solubilidad (Clarke's)": 'Prácticamente insoluble en agua; poco soluble en etanol; soluble en cloroformo.'},
    {'Sustancia ': 'Fenobarbital', 'pKa': '7.4', 'Carácter': 'Ácido', "Solubilidad (Clarke's)": 'Soluble 1 en 1000 de agua, 1 en 8 de etanol, 1 en 40 de cloroformo.'}
]

# Read existing fieldnames
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    existing = [row['Sustancia '] for row in reader]

with open(filepath, 'a', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
    for d in new_data:
        if d['Sustancia '] not in existing:
            writer.writerow(d)

print('Nuevas sustancias agregadas.')
