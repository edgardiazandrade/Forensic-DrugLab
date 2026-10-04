import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1 & 2: CSS Updates
# Change #E6F2FF (light blue) to a slightly strong gray like #CCCCCC or #D3D3D3
text = text.replace('background-color: #E6F2FF', 'background-color: #D3D3D3')
text = text.replace('background-color: #F0F0F0 !important;', 'background-color: #E0E0E0 !important;')

# Add hover animation to metric-box
if '.metric-box { text-align: center;' in text:
    text = text.replace('.metric-box { text-align: center;', '.metric-box { transition: all 0.3s ease-in-out; text-align: center;')
if '.metric-box:hover' not in text:
    text = text.replace('</style>', '    .metric-box:hover { transform: scale(1.05); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }\n    </style>')

# 3: Move "Resultados Esperados" after "Procedimiento"
# This requires manipulating the tab4_reactivos code blocks.
# Let's use regex or split on chunks.
# The structure is:
# st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Resultados Esperados (Colores)</h3>"... to ... st.info(...)
# st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Reactivos Necesarios</h3>"... to ... st.table(...)
# st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Procedimiento Analítico</h3>"... to ... st.markdown(flow_html...)

block_resultados = re.search(r'(st\.markdown\(\"<hr style=\'border-color:#3A4252;\'><h3 style=\'text-align:center;\'>Resultados Esperados \(Colores\)</h3>\".*?)(st\.markdown\(\"<hr style=\'border-color:#3A4252;\'><h3 style=\'text-align:center;\'>Reactivos Necesarios</h3>\")', text, re.DOTALL)
if block_resultados:
    resultados_str = block_resultados.group(1)
    # Remove from original
    text = text.replace(resultados_str, '')
    
    # Insert after Procedimiento
    block_proc = re.search(r'(st\.markdown\(\"<hr style=\'border-color:#3A4252;\'><h3 style=\'text-align:center;\'>Procedimiento Analítico</h3>\".*?st\.markdown\(flow_html, unsafe_allow_html=True\)\n)', text, re.DOTALL)
    if block_proc:
        proc_str = block_proc.group(1)
        text = text.replace(proc_str, proc_str + '\n        ' + resultados_str)

# 4: Fix IR logic
# We need to extract the first continuous number block.
old_ir_logic = '''def interpretar_ir(pico_str):
    try:
        p = float(pico_str)
    except:
        return "-"'''
new_ir_logic = '''def interpretar_ir(pico_str):
    import re
    match = re.search(r'\d+', pico_str)
    if not match: return "-"
    p = float(match.group(0))'''
text = text.replace(old_old_ir_logic if 'old_old_ir_logic' in locals() else old_ir_logic, new_ir_logic)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

# 5: Fix Alprazolam in CSV
import csv
filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
rows = []
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        if row['Sustancia '] == 'Alprazolam':
            row['Prueba presuntiva'] = 'Prueba de Zimmerman'
            row['Color característico'] = 'Violeta / Rosa'
        rows.append(row)
with open(filepath, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# 6: And add Zimmerman to Pruebas Presuntivas.csv if not there
pruebas = []
has_zim = False
with open('Pruebas Presuntivas.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    p_fields = reader.fieldnames
    for r in reader:
        if 'Zimmerman' in r['Prueba']:
            has_zim = True
        pruebas.append(r)

if not has_zim:
    pruebas.append({
        'Prueba': 'Prueba de Zimmerman (Benzodiazepinas)',
        'Reactivos': 'Solución 1: 1% dinitrobenceno en metanol\\nSolución 2: 15% KOH en agua',
        'Procedimiento': 'Disolver muestra en metanol\\nAgregar 2 gotas Solución 1\\nAgregar 2 gotas Solución 2',
        'Falsos Positivos': 'Cetonas',
        'Falsos Negativos': 'Benzodiazepinas muy diluidas'
    })
    with open('Pruebas Presuntivas.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=p_fields)
        writer.writeheader()
        writer.writerows(pruebas)

print('Everything updated.')
