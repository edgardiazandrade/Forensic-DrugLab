import re, base64

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove "Doc:" and replace N/A
text = text.replace('f"Doc: {color}"', 'color')
text = text.replace('"N/A"', '"No se especifica en Clarke\'s [1]"')
text = text.replace('info.get(\'Color característico\', \'N/A\')', 'info.get(\'Color característico\', \'No se especifica en Clarke\\\'s [1]\')')

# 2. Add Vancouver reference for IR
ref_vancouver = 'Francisco RC. Tablas de Espectroscopía Infrarroja [3].<br/>'
if 'Francisco RC.' not in text:
    text = text.replace('<span style="font-weight: bold;', ref_vancouver + '<span style="font-weight: bold;')

# 3. Fix colors
text = text.replace('color: #00E5FF;', 'color: #003366;')
text = text.replace('color:#00E5FF;', 'color:#003366;')
text = text.replace('color: #00FF9D;', 'color: #27AE60;')

# 4. Remove Nota de Interpretación Analítica in tab3
start_nota = text.find('st.markdown("""<div class="nota-card"')
if start_nota != -1:
    end_nota = text.find('unsafe_allow_html=True)', start_nota) + len('unsafe_allow_html=True)')
    if text[end_nota:end_nota+1] == '\\n': end_nota += 1
    # Check if the block actually contains "Nota de Interpretación Analítica"
    if 'Nota de Interpretación Analítica' in text[start_nota:end_nota]:
        text = text[:start_nota] + text[end_nota:]

# Let's use regex for the precise replacement of the nota-card in tab3
# Actually, the string in tab3 might be different. Let's just remove the text directly
text = re.sub(r'st\.markdown\(\'\'\'\s*<div class="nota-card".*?El número de valores de pKa.*?</div>\s*\'\'\', unsafe_allow_html=True\)', '', text, flags=re.DOTALL)
text = re.sub(r'st\.markdown\("""<div class="nota-card".*?El número de valores de pKa.*?</div>""", unsafe_allow_html=True\)', '', text, flags=re.DOTALL)
text = re.sub(r'st\.markdown\(\'<div class="nota-card".*?El número de valores de pKa.*?</div>\', unsafe_allow_html=True\)', '', text, flags=re.DOTALL)
# Try simply searching for the string "Nota de Interpretación Analítica:" and removing the st.markdown around it.
match_nota = re.search(r'st\.markdown\([^\)]*?Nota de Interpretación Analítica:[^\)]*?\)', text, re.DOTALL)
if match_nota:
    text = text.replace(match_nota.group(0), '')

# 5. Fix structure image heights
# Find render_structure
old_render_struct = '''def render_structure(sustancia, info, selected_ph):
    pka, char = info.get('pKa', '7'), info.get('Carácter', 'Base')
    sp = calculate_ionization(pka, char, selected_ph)
    obj_is_ion = 100.0 - sp.get('Neutro', 0.0)
    suffix = 'ion' if obj_is_ion >= 50.0 else 'base'
    img_path = find_image(sustancia, suffix)
    if img_path: st.image(img_path, use_container_width=True)
    else: st.info("🧪 Estructura molecular no disponible.")
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>Estructura de {sustancia}</div>", unsafe_allow_html=True)'''

new_render_struct = '''def render_structure(sustancia, info, selected_ph):
    import base64
    pka, char = info.get('pKa', '7'), info.get('Carácter', 'Base')
    sp = calculate_ionization(pka, char, selected_ph)
    obj_is_ion = 100.0 - sp.get('Neutro', 0.0)
    suffix = 'ion' if obj_is_ion >= 50.0 else 'base'
    img_path = find_image(sustancia, suffix)
    if img_path:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            ext = img_path.split('.')[-1]
            html_img = f'<div style="height: 250px; display: flex; align-items: center; justify-content: center;"><img src="data:image/{ext};base64,{encoded_string}" style="max-height: 100%; max-width: 100%; object-fit: contain;"></div>'
            st.markdown(html_img, unsafe_allow_html=True)
    else:
        st.markdown('<div style="height: 250px; display: flex; align-items: center; justify-content: center; border: 1px dashed #CCC; color: #999;">🧪 Estructura no disponible</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>Estructura de {sustancia}</div>", unsafe_allow_html=True)'''

# Replace depending on exactly how it is spelled
text = re.sub(r'def render_structure.*?Estructura de {sustancia}</div>", unsafe_allow_html=True\)', new_render_struct, text, flags=re.DOTALL)

# 6. Simulador manual: Agregar lo de la ventana de extracción
match_tab_sim = re.search(r'(def tab_simulador\(\):.*?st\.altair_chart\(\(base_chart \+ rule \+ point_chart\)\.interactive\(\), use_container_width=True\))', text, re.DOTALL)
if match_tab_sim:
    old_tab_sim = match_tab_sim.group(1)
    new_tab_sim = old_tab_sim + '''
    
    st.markdown("<hr style='border-color:#CCCCCC;'><h3 style='text-align:center;'>Viabilidad de Separación y Extracción (Simulada)</h3>", unsafe_allow_html=True)
    if name_b and name_b != "Sustancia B" and pka_b:
        info_a = {'pKa': pka_a, 'Carácter': char_a}
        info_b = {'pKa': pka_b, 'Carácter': char_b}
        ph_min, ph_max = find_optimal_separation_window(info_a, info_b)
        
        if ph_min is not None and ph_max is not None:
            opt_ph = (ph_min + ph_max) / 2
            st.success(f"✅ **Separación posible.** Ventana óptima de pH: **{ph_min:.1f} a {ph_max:.1f}** (pH ideal sugerido: **{opt_ph:.1f}**).")
            st.markdown(f"A este pH, **{name_a}** tiene una diferencia de ionización ≥90% respecto a **{name_b}**, lo que teóricamente permite separarlos por partición en disolventes inmiscibles.")
            st.markdown(f"**Protocolo Propuesto:** Ajustar el medio a pH {opt_ph:.1f}, añadir disolvente orgánico inmiscible, agitar y decantar.")
            st.markdown("<p style='font-size:0.85rem; color:#666;'>⚠️ <i>La capacidad real de separación también depende del logP/logD y la matriz de la muestra.</i></p>", unsafe_allow_html=True)
        else:
            st.error("⚠️ **No es posible proponer un protocolo basado exclusivamente en el pH (L-L simple).**")
            st.markdown("Las curvas de especiación dictan que los pKa de ambas sustancias son muy cercanos o que su comportamiento de ionización se traslapa, lo que impide alcanzar matemáticamente una diferencia de ionización ≥ 90% simultánea. Se recomienda utilizar cromatografía.")
    else:
        st.info("Ingresa los datos de una segunda sustancia (Sustancia B) para evaluar la viabilidad de separación Líquido-Líquido.")
'''
    text = text.replace(old_tab_sim, new_tab_sim)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('app.py modifications for Part 2 done')
