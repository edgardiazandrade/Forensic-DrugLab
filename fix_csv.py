import csv
import os

base_dir = r"C:\Users\DXD_C\.gemini\antigravity\scratch\ionizacion"
csv_path = os.path.join(base_dir, 'pH_vs_Ionizacion_Comparada_Datos.csv')

with open(csv_path, 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    rows = list(reader)

for row in rows:
    if len(row) > 1:
        sus = row[1].strip().upper()
        if sus == 'KETAMINA':
            row[11] = "Morris"
            row[12] = "Púrpura / Violeta"
            row[13] = "Reactivo A y B de Morris."
            row[14] = "Añadir A y B, agitar."
            row[15] = "Da color púrpura característico con Morris."
        elif sus == 'MDA':
            row[12] = "Negro / Púrpura oscuro"
            row[14] = "1 gota; reacción inmediata."
            row[15] = "Color muy similar al MDMA."
        elif sus == 'FENACETINA':
            row[12] = "Sin reacción"
            row[15] = "Generalmente no presenta reacción con Marquis."
        elif sus == 'CAFEÍNA':
            row[5] = "0.61"
        elif sus == 'SERTRALINA':
            row[15] = "Reacción no estandarizada; reportada empíricamente."

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
