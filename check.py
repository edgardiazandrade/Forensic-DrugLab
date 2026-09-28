import csv

filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    with open('output.txt', 'w', encoding='utf-8') as out:
        for row in list(reader)[:3]:
            out.write(row['Sustancia '] + '\n')
            for i in range(1,7):
                out.write(f' P{i}: {row[f"P{i}"]}, S{i}: {row[f"S{i}"]}\n')
            for i in range(1,9):
                out.write(f' I{i}: {row[f"I{i}"]}, D{i}: {row[f"D{i}"]}\n')
