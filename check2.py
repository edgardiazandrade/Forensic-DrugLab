import csv

filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with open('test_check.txt', 'w', encoding='utf-8') as out:
        for row in reader:
            out.write(f"{row['Sustancia ']}: {row['Prueba presuntiva']} -> {row['Color característico']}\n")
