import csv

solubilities = {
    'ASPIRINA': 'Soluble 1 en 300 de agua, 1 en 5 de etanol, 1 en 17 de cloroformo, y 1 en 10 a 15 de éter.',
    'CAFEÍNA': 'Soluble 1 en 46 de agua, 1 en 66 de alcohol, 1 en 50 de acetona, 1 en 5.5 de cloroformo; 1 en 530 de éter.',
    'CLONAZEPAM': 'Solubilidad en mg/mL a 25°C: acetona 31, cloroformo 15, metanol 8.6, éter 0.7, agua <0.1.',
    'COCAÍNA': 'Soluble 1 en 600 de agua, 1 en 6.5 de etanol, 1 en 0.7 de cloroformo y 1 en 3.5 de éter.',
    'HEROÍNA': 'Soluble 1 en 1700 de agua, 1 en 31 de etanol, 1 en 1.5 de cloroformo y 1 en 100 de éter.',
    'DIAMORFINA': 'Soluble 1 en 1700 de agua, 1 en 31 de etanol, 1 en 1.5 de cloroformo y 1 en 100 de éter.',
    'DIPIRONA': 'Soluble 1 en 1.5 de agua y 1 en 30 de etanol; prácticamente insoluble en éter, acetona, benceno y cloroformo.',
    'METAMIZOL': 'Soluble 1 en 1.5 de agua y 1 en 30 de etanol; prácticamente insoluble en éter, acetona, benceno y cloroformo.',
    'EFEDRINA': 'Soluble 1 en 20 de agua y 1 en <1 de etanol; soluble en cloroformo con turbidez; soluble en éter.',
    'FENTANILO': 'Ligeramente soluble en agua. (Citrato: Soluble 1 en 40 de agua, 1 en 140 de etanol, 1 en 350 de cloroformo).',
    'IBUPROFENO': 'Prácticamente insoluble en agua; soluble 1 en 1.5 de etanol, 1 en 1 de cloroformo y 1 en 2 de éter.',
    'KETAMINA': 'Sal hidrocloruro: Soluble 1 en 4 de agua, 1 en 14 de etanol y 1 en 6 de metanol; poco soluble en cloroformo; prácticamente insoluble en éter.',
    'LEVAMISOL': 'Soluble en ácido acético diluido y en cloroformo.',
    'LSD': 'Soluble en agua.',
    'METANFETAMINA': 'Ligeramente soluble en agua; miscible con etanol, cloroformo y éter.',
    'NAPROXENO': 'Prácticamente insoluble en agua; soluble 1 en 25 de etanol, 1 en 15 de cloroformo, y 1 en 40 de éter.',
    'FENACETINA': 'Soluble 1 en 1300 de agua, 1 en 15 de etanol, 1 en 14 de cloroformo y 1 en 90 de éter.',
    'SERTRALINA': 'Agua 3.8 mg/mL (pH dependiente). Soluble en cloroformo:metanol (1:1), etanol.',
    'THC': 'Esencialmente insoluble en agua; soluble 1 en 1 en etanol y acetona; fácilmente soluble en cloroformo y éter de petróleo.',
    'MDA': 'Datos no especificados en la monografía.',
    'MDMA': 'Datos no especificados en la monografía.'
}

filepath_db = 'pH_vs_Ionizacion_Comparada_Datos.csv'
rows = []
with open(filepath_db, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    if "Solubilidad (Clarke's)" not in fieldnames:
        fieldnames.append("Solubilidad (Clarke's)")
        
    for row in reader:
        sub = row['Sustancia '].upper()
        # Find solubility
        sol = 'No especificada en el manual.'
        for key, val in solubilities.items():
            if key in sub:
                sol = val
                break
        row["Solubilidad (Clarke's)"] = sol
        rows.append(row)

with open(filepath_db, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

filepath_pruebas = 'Pruebas Presuntivas.csv'
pruebas_rows = []
with open(filepath_pruebas, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    p_fieldnames = reader.fieldnames
    for row in reader:
        name = row['Prueba']
        name = name.replace(" (Clarke's)", "")
        name = name.replace("Reactivo KN / Fast Blue B", "Reactivo KN")
        
        if "Prueba de Mandelin" in name and "(" not in name:
            name += " (Anfetaminas y Antidepresivos)"
        elif "Prueba de Cloruro Férrico" in name and "(" not in name:
            name += " (Fenoles y Salicilatos)"
        elif "Prueba de McNally" in name and "(" not in name:
            name += " (Salicilatos)"
        elif "Prueba de Ácido Amálico" in name and "(" not in name:
            name += " (Xantinas)"
            
        row['Prueba'] = name
        pruebas_rows.append(row)

with open(filepath_pruebas, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=p_fieldnames)
    writer.writeheader()
    writer.writerows(pruebas_rows)

print('CSV databases updated.')
