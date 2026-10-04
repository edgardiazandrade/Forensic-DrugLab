with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix matching logic
old_match = '''            if prueba_db == selected or (selected.split(" ")[-1] in prueba_db and len(selected.split(" ")[-1]) > 3):'''
new_match = '''            # Extraer el nombre base de la prueba del CSV de datos (ej. "Prueba de Marquis")
            if prueba_db and (prueba_db in selected or selected in prueba_db or prueba_db.replace("Prueba de ", "") in selected):'''
text = text.replace(old_match, new_match)

# Fix hardcoded colors in main
text = text.replace('background-color: #22262F', 'background-color: #E6F2FF')
text = text.replace('border: 1px solid #3A4252', 'border: 1px solid #003366; color: #000000')
text = text.replace('color:#A0AABF', 'color:#003366')

# Fix text colors inside the flow cards
text = text.replace('<div style="font-size:2.5rem; color:#00E5FF;', '<div style="font-size:2.5rem; color:#003366;')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.py updated with better matching and colors')
