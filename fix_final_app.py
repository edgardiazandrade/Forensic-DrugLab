import csv
import re

# 1. Update CSV
filepath = 'pH_vs_Ionizacion_Comparada_Datos.csv'
rows = []
with open(filepath, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        if row['Sustancia '] == 'Alprazolam':
            row['Prueba presuntiva'] = "No se especifica en Clarke's [1]"
            row['Color característico'] = "No se especifica en Clarke's [1]"
        rows.append(row)

with open(filepath, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# 2. Update app.py
with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add note to Tab 1
if '⚠️ Nota: Todo resultado positivo presuntivo tiene que confirmarse por pruebas confirmatorias' not in text:
    tab1_marker = "def tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph):\n    st.markdown(\"<h2 style='text-align:center;'>⚖️ Ficha Comparativa (Sustancia vs Adulterante)</h2>\", unsafe_allow_html=True)"
    note_html = """
    st.markdown('''
    <div class="nota-card" style="border-left-color: #E74C3C;">
        <p style="color: #000000; text-align:center;"><b>⚠️ Nota:</b> Todo resultado positivo presuntivo tiene que confirmarse por pruebas confirmatorias instrumentales (GC-MS, FTIR).</p>
    </div>
    ''', unsafe_allow_html=True)"""
    if tab1_marker in text:
        text = text.replace(tab1_marker, tab1_marker + note_html)

# Add note to Tab 2
if '⚠️ Nota: Todo resultado positivo presuntivo tiene que confirmarse' not in text:
    tab2_marker = 'def tab2_arbol_decision():\n    st.markdown("<h2 style=\'text-align:center;\'>🌳 Flujo de Descarte Analítico (ODV / Sirchie)</h2>", unsafe_allow_html=True)'
    if tab2_marker in text:
        text = text.replace(tab2_marker, tab2_marker + note_html)

# 3. Fix IR and MS images to fixed height
def get_base64_func(func_name, title, dict_prefix):
    return f'''def {func_name}(sustancia, info):
    import base64
    img_path = find_image(sustancia, '{dict_prefix}')
    if img_path:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            ext = img_path.split('.')[-1]
            html_img = f'<div style="height: 250px; display: flex; align-items: center; justify-content: center;"><img src="data:image/{{ext}};base64,{{encoded_string}}" style="max-height: 100%; max-width: 100%; object-fit: contain;"></div>'
            st.markdown(html_img, unsafe_allow_html=True)
    else:
        st.markdown('<div style="height: 250px; display: flex; align-items: center; justify-content: center; border: 1px dashed #CCC; color: #999;">⚠️ {title} no disponible</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>{title} de {{sustancia}}</div>", unsafe_allow_html=True)'''

# Replace render_ir
old_ir = re.search(r'def render_ir\(sustancia, info\):.*?st\.markdown\(f"<div style=\'font-size:0\.8rem; color:#003366; text-align:center;\'>Espectro Infrarrojo de \\n\{sustancia\}</div>", unsafe_allow_html=True\)', text, re.DOTALL)
if not old_ir:
    old_ir = re.search(r'def render_ir\(sustancia, info\):.*?st\.markdown\(f"<div style=\'font-size:0\.8rem; color:#003366; text-align:center;\'>Espectro Infrarrojo de \{sustancia\}</div>", unsafe_allow_html=True\)', text, re.DOTALL)
if old_ir:
    text = text.replace(old_ir.group(0), get_base64_func('render_ir', 'Espectro Infrarrojo', 'Espectro_IR'))

# Replace render_ms
old_ms = re.search(r'def render_ms\(sustancia, info\):.*?st\.markdown\(f"<div style=\'font-size:0\.8rem; color:#003366; text-align:center;\'>Espectro de Masas de \\n\{sustancia\}</div>", unsafe_allow_html=True\)', text, re.DOTALL)
if not old_ms:
    old_ms = re.search(r'def render_ms\(sustancia, info\):.*?st\.markdown\(f"<div style=\'font-size:0\.8rem; color:#003366; text-align:center;\'>Espectro de Masas de \{sustancia\}</div>", unsafe_allow_html=True\)', text, re.DOTALL)
if old_ms:
    text = text.replace(old_ms.group(0), get_base64_func('render_ms', 'Espectro de Masas', 'GS-MS'))

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated CSV and app.py successfully.')
