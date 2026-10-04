import streamlit as st
import csv
import os
import re
import math
import unicodedata
import altair as alt

st.set_page_config(page_title="Análisis Químico de Sustancias", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    st.markdown("""
    <style>
    /* Pearl white background */
    .stApp, .main { background-color: #FBFBF9 !important; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #E0E0E0 !important; text-align: center; color: #000000 !important;}
    h1, h2, h3, h4, h5, h6 { color: #003366 !important; text-shadow: none; text-align: center !important; width: 100%; display: block; }
    p, span, div, label, li { text-align: center; color: #000000; }
    ul { list-style-position: inside; text-align: center; padding: 0; }
    table { width: 100%; margin: 0 auto; text-align: center; transition: all 0.3s ease-in-out; color: #000000 !important; }
    th, td { text-align: center !important; color: #000000 !important; }
    img { transition: all 0.3s ease-in-out; border-radius: 8px; margin: 0 auto; display: block; }
    .forensic-card { background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease-in-out; }
    .forensic-card:hover { transform: scale(1.02); box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2); border-color: #003366; }
    .nota-card { background-color: #D3D3D3; border-left: 5px solid #003366; padding: 15px; margin-top: 30px; border-radius: 4px; transition: all 0.3s ease-in-out; }
    .nota-card:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0, 51, 102, 0.4); border: 1px solid #003366; border-left: 5px solid #003366; }
    .numeric-val { font-family: 'Courier New', Courier, monospace; color: #003366; font-weight: bold; }
    .color-box { height: 50px; width: 100%; border-radius: 6px; margin-bottom: 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border: 1px solid #CCCCCC; }
        .metric-box:hover { transform: scale(1.05); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)
def normalize_name(name):
    name = name.lower().strip()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = re.sub(r'\s+', '', name)
    return name

def load_data(filepath):
    data = {}
    if not os.path.exists(filepath):
        return data
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try: headers = next(reader)
        except StopIteration: return data
        headers = [h.strip() for h in headers]
        for row in reader:
            if not row or len(row) < 2: continue
            sustancia = row[1].strip()
            if not sustancia or sustancia.lower() == 'ph' or sustancia.isdigit() or sustancia == '0': continue
            row += [''] * (len(headers) - len(row))
            data[sustancia] = dict(zip(headers, row))
    return data

def load_pruebas_csv():
    filepath = os.path.join(os.path.dirname(__file__), 'Pruebas Presuntivas.csv')
    tests = {}
    if os.path.exists(filepath):
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tests[row['Prueba']] = row
    return tests

import re

def calculate_ionization(pka_str, character, ph):
    # Extract all numerical values from pKa string
    parts = re.findall(r"[-+]?\d*\.\d+|\d+", str(pka_str))
    if not parts:
        return {"Neutro": 100.0, "Ionizado": 0.0}
    
    character = character.strip().lower()
    
    is_amphoteric = 'anfóter' in character or 'anfoter' in character
    is_diprotic = 'diprótic' in character or 'diprotic' in character
    
    # If not explicitly marked as amphoteric or diprotic, treat as MONOPROTIC.
    if len(parts) >= 2 and (is_amphoteric or is_diprotic):
        pk1, pk2 = sorted([float(parts[0]), float(parts[1])])
        if is_amphoteric:
            try:
                h2z = 10.0**(pk1 - ph)
                z = 10.0**(ph - pk2)
                denom = 1.0 + h2z + z
                return {"Neutro": 100.0 / denom, "Catión (+1)": 100.0 * h2z / denom, "Anión (-1)": 100.0 * z / denom}
            except OverflowError:
                if ph < pk1: return {"Neutro": 0.0, "Catión (+1)": 100.0, "Anión (-1)": 0.0}
                elif ph > pk2: return {"Neutro": 0.0, "Catión (+1)": 0.0, "Anión (-1)": 100.0}
                else: return {"Neutro": 100.0, "Catión (+1)": 0.0, "Anión (-1)": 0.0}
        
        elif 'ácido' in character or 'acido' in character:
            try:
                ha = 10.0**(ph - pk1)
                a2 = 10.0**(2*ph - pk1 - pk2)
                denom = 1.0 + ha + a2
                return {"Neutro": 100.0 / denom, "Anión 1 (-1)": 100.0 * ha / denom, "Anión 2 (-2)": 100.0 * a2 / denom}
            except OverflowError:
                if ph < pk1: return {"Neutro": 100.0, "Anión 1 (-1)": 0.0, "Anión 2 (-2)": 0.0}
                elif ph < pk2: return {"Neutro": 0.0, "Anión 1 (-1)": 100.0, "Anión 2 (-2)": 0.0}
                else: return {"Neutro": 0.0, "Anión 1 (-1)": 0.0, "Anión 2 (-2)": 100.0}
                
        else:
            try:
                bh = 10.0**(pk2 - ph)
                bh2 = 10.0**(pk1 + pk2 - 2*ph)
                denom = 1.0 + bh + bh2
                return {"Neutro": 100.0 / denom, "Catión 1 (+1)": 100.0 * bh / denom, "Catión 2 (+2)": 100.0 * bh2 / denom}
            except OverflowError:
                if ph > pk2: return {"Neutro": 100.0, "Catión 1 (+1)": 0.0, "Catión 2 (+2)": 0.0}
                elif ph > pk1: return {"Neutro": 0.0, "Catión 1 (+1)": 100.0, "Catión 2 (+2)": 0.0}
                else: return {"Neutro": 0.0, "Catión 1 (+1)": 0.0, "Catión 2 (+2)": 100.0}
    
    # Monoprotic fallback (uses the first pKa or averages if it's a range like "4.4-5.2")
    else:
        # If it has 2 parts but is not amphoteric/diprotic, we assume it's literature variation and average it
        if len(parts) >= 2:
            pka_val = (float(parts[0]) + float(parts[1])) / 2.0
        else:
            pka_val = float(parts[0])
            
        if 'ácido' in character or 'acido' in character:
            try:
                power = pka_val - ph
                if power > 100: ion = 0.0
                elif power < -100: ion = 100.0
                else: ion = 100.0 / (1.0 + 10.0**power)
            except OverflowError: ion = 0.0 if (pka_val - ph) > 0 else 100.0
        else:
            try:
                power = ph - pka_val
                if power > 100: ion = 0.0
                elif power < -100: ion = 100.0
                else: ion = 100.0 / (1.0 + 10.0**power)
            except OverflowError: ion = 0.0 if (ph - pka_val) > 0 else 100.0
        return {"Neutro": 100.0 - ion, "Ionizado": ion}

def find_optimal_separation_window(info_obj, info_cut):
    if "No extraíble" in info_obj.get('Disolvente        <', '') or "No extraíble" in info_obj.get('>       Disolvente', '') or "No extraíble" in info_cut.get('Disolvente        <', '') or "No extraíble" in info_cut.get('>       Disolvente', ''):
        return None, None
    window = []
    pka_obj, char_obj = info_obj.get('pKa', '7'), info_obj.get('Carácter', 'Base')
    pka_cut, char_cut = info_cut.get('pKa', '7'), info_cut.get('Carácter', 'Base')
    for ph_val in [x/10.0 for x in range(0, 141)]:
        sp_obj = calculate_ionization(pka_obj, char_obj, ph_val)
        sp_cut = calculate_ionization(pka_cut, char_cut, ph_val)
        n_obj = sp_obj.get('Neutro', 0.0)
        n_cut = sp_cut.get('Neutro', 0.0)
        if abs(n_obj - n_cut) >= 90.0: window.append(ph_val)
    if window: return window[0], window[-1]
    return None, None

def find_image(sub_name, suffix):
    img_dir = os.path.join(os.path.dirname(__file__), 'Imagenes estructura')
    norm_name = normalize_name(sub_name)
    for ext in ['.png', '.jpg', '.jpeg']:
        path = os.path.join(img_dir, f"{norm_name}_{suffix}{ext}")
        if os.path.exists(path): return path
        path = os.path.join(img_dir, f"{norm_name}_{suffix}{ext.upper()}")
        if os.path.exists(path): return path
        path = os.path.join(img_dir, f"{sub_name}_{suffix}{ext}")
        if os.path.exists(path): return path
    return None

def get_solvent(info, pka, current_ph):
    try: pka_val = float(pka.split(',')[0].strip())
    except Exception: pka_val = 7.0
    if current_ph < pka_val:
        for k, v in info.items():
            if '<' in k and 'Disolvente' in k: return v if v else "No especificado"
    else:
        for k, v in info.items():
            if '>' in k and 'Disolvente' in k: return v if v else "No especificado"
    return "No especificado"

def visual_button(label, bg_style, key, is_biphasic=False, top_bg="", bot_bg="", top_txt="", bot_txt="", custom_html=""):
    if custom_html:
        visual = custom_html
    elif is_biphasic:
        visual = f'<div style="height:50px; width:100%; border-radius:6px; display:flex; flex-direction:column; overflow:hidden; border:1px solid #111; margin-bottom:10px;"><div style="height:50%; background:{top_bg}; color:#fff; font-size:0.6rem; text-align:center; line-height:25px;">{top_txt}</div><div style="height:50%; background:{bot_bg}; color:#fff; font-size:0.6rem; text-align:center; line-height:25px;">{bot_txt}</div></div>'
    else:
        visual = f'<div style="height:50px; width:100%; border-radius:6px; background:{bg_style}; border:1px solid #111; margin-bottom:10px;"></div>'
    st.markdown(visual, unsafe_allow_html=True)
    return st.button(label, key=key, use_container_width=True)

def render_presumptive_card(test_name, color_desc, interpretation, bg_style, is_biphasic=False, top_bg="", bot_bg="", top_txt="", bot_txt="", custom_html=""):
    if custom_html:
        visual = custom_html
    elif is_biphasic:
        visual = f'<div class="biphasic-tube"><div class="biphasic-top" style="background: {top_bg};">{top_txt}</div><div class="biphasic-bottom" style="background: {bot_bg};">{bot_txt}</div></div>'
    else:
        visual = f'<div class="color-box" style="background: {bg_style};"></div>'
    st.markdown(f'''<div class="forensic-card">{visual}<div style="font-size: 1.1rem; font-weight: 600; color: #E1E4EA; margin-bottom: 5px; text-align:center;">{test_name}</div><div style="font-size: 0.9rem; color: #A0AABF; margin-bottom: 10px; text-align:center;"><b>Tono Visual:</b> {color_desc}</div><div style="font-size: 0.95rem; color: #27AE60; font-weight: bold; text-align:center;">{interpretation}</div></div>''', unsafe_allow_html=True)

def render_structure(sustancia, info, selected_ph):
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
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>Estructura de {sustancia}</div>", unsafe_allow_html=True)

def render_presumptive_info(sustancia, info):
    prueba = info.get('Prueba presuntiva', 'N/A')
    color = info.get('Color característico', 'No se especifica en Clarke\'s [1]')
    c_lower = color.lower()
    fallback_color = "#555555"
    if "naranja" in c_lower: fallback_color = "#E67E22"
    elif "rojo" in c_lower or "roja" in c_lower: fallback_color = "#E74C3C"
    elif "azul" in c_lower: fallback_color = "#3498DB"
    elif "violeta" in c_lower or "púrpura" in c_lower or "morado" in c_lower: fallback_color = "#8E44AD"
    elif "verde" in c_lower: fallback_color = "#27AE60"
    elif "amarillo" in c_lower: fallback_color = "#F1C40F"
    elif "rosa" in c_lower: fallback_color = "#F1948A"
    elif "marrón" in c_lower or "cafe" in c_lower: fallback_color = "#8B4513"
    elif "negro" in c_lower: fallback_color = "#1A1A1A"
    
    nombre = sustancia.lower()
    if "cocaína" in nombre or "cocaina" in nombre: render_presumptive_card("Scott (#904)", color, "Cocaína", "", True, "#F5B7B1", "#0077C8", "Acuosa", "Orgánica")
    elif "metanfetamina" in nombre or "anfetamina" in nombre: render_presumptive_card("Marquis (#902)", color, "Anfetaminas", "linear-gradient(to right, #D9531E, #E74C3C, #5C2C16)")
    elif "mdma" in nombre or "mda" in nombre: render_presumptive_card("Marquis (#902)", color, "Entactógenos", "#1A1A1A")
    elif "lsd" in nombre: render_presumptive_card("Ehrlich (#907)", color, "Indoles", "#8E44AD")
    elif "thc" in nombre: render_presumptive_card("Duquenois-Levine", color, "Cannabinoides", "", True, "#7F8C8D", "#5B2C6F", "Sup.", "Inf.")
    elif "heroína" in nombre or "heroina" in nombre: render_presumptive_card("Marquis (#902)", color, "Opiáceos", "#5B2C6F")
    else: render_presumptive_card(prueba, color, "Prueba base", fallback_color)
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>Prueba Presuntiva de {sustancia}</div>", unsafe_allow_html=True)


def interpretar_ir(pico_str):
    import re
    match = re.search(r'\d+', pico_str)
    if not match: return "-"
    p = float(match.group(0))
    if 3200 <= p <= 3650: return "O-H / N-H (Alcohol, Fenol, Amina)"
    if 3000 <= p < 3200: return "C-H sp2 (Aromático/Alqueno)"
    if 2800 <= p < 3000: return "C-H sp3 (Alcano)"
    if 2100 <= p < 2300: return "C≡C / C≡N (Alquino/Nitrilo)"
    if 1650 <= p < 1850: return "C=O (Carbonilo)"
    if 1550 <= p < 1650: return "C=C / N-H (Aromático/Amina)"
    if 1300 <= p < 1550: return "Flexiones C-H (Alcano/Aromático)"
    if 1000 <= p < 1300: return "C-O / C-N (Éter, Éster, Amina)"
    if p < 1000: return "C-H fuera de plano (Aromático)"
    return "Otra vibración"
def render_ir(sustancia, info):
    import base64
    img_path = find_image(sustancia, 'Espectro_IR')
    if img_path:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            ext = img_path.split('.')[-1]
            html_img = f'<div style="height: 250px; display: flex; align-items: center; justify-content: center;"><img src="data:image/{ext};base64,{encoded_string}" style="max-height: 100%; max-width: 100%; object-fit: contain;"></div>'
            st.markdown(html_img, unsafe_allow_html=True)
    else:
        st.markdown('<div style="height: 250px; display: flex; align-items: center; justify-content: center; border: 1px dashed #CCC; color: #999;">⚠️ Espectro Infrarrojo no disponible</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>Espectro Infrarrojo de {sustancia}</div>", unsafe_allow_html=True)
    picos_ir = []
    for i in range(1, 7):
        num = info.get(f"P{i}", "").strip()
        if num: picos_ir.append({"Vibración (cm⁻¹)": num, "Interpretación (Tablas IR)": interpretar_ir(num)})
    if picos_ir: st.table(picos_ir)

def render_ms(sustancia, info):
    import base64
    img_path = find_image(sustancia, 'GS-MS')
    if img_path:
        with open(img_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            ext = img_path.split('.')[-1]
            html_img = f'<div style="height: 250px; display: flex; align-items: center; justify-content: center;"><img src="data:image/{ext};base64,{encoded_string}" style="max-height: 100%; max-width: 100%; object-fit: contain;"></div>'
            st.markdown(html_img, unsafe_allow_html=True)
    else:
        st.markdown('<div style="height: 250px; display: flex; align-items: center; justify-content: center; border: 1px dashed #CCC; color: #999;">⚠️ Espectro de Masas no disponible</div>', unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.8rem; color:#003366; text-align:center;'>Espectro de Masas de {sustancia}</div>", unsafe_allow_html=True)
    iones = []
    for i in range(1, 9):
        ion_val = info.get(f"I{i}", "").strip()
        if ion_val: iones.append({"Relación m/z": ion_val})
    if iones: st.table(iones)

def tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph):
    st.markdown("<h2 style='text-align:center;'>📋 Ficha Comparativa (Sustancia vs Adulterante)</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<h3 style='color:#003366; text-align:center;'>🎯 Analito Objetivo:<br>{selected_sustancia}</h3>", unsafe_allow_html=True)
    with c2: st.markdown(f"<h3 style='color:#E74C3C; text-align:center;'>✂️ Adulterante:<br>{selected_adulterante}</h3>", unsafe_allow_html=True)
    
    st.markdown(f"<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Solubilidad Documentada (Clarke's)</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.info(data[selected_sustancia].get("Solubilidad (Clarke's)", "No especificada."))
    with c2: st.info(data[selected_adulterante].get("Solubilidad (Clarke's)", "No especificada."))
    
    st.markdown(f"<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Estructura Molecular (pH {selected_ph:.1f})</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_structure(selected_sustancia, data[selected_sustancia], selected_ph)
    with c2: render_structure(selected_adulterante, data[selected_adulterante], selected_ph)
    
    st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Prueba Presuntiva Documentada</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_presumptive_info(selected_sustancia, data[selected_sustancia])
    with c2: render_presumptive_info(selected_adulterante, data[selected_adulterante])
    
    st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Espectro Infrarrojo (FTIR-ATR)</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_ir(selected_sustancia, data[selected_sustancia])
    with c2: render_ir(selected_adulterante, data[selected_adulterante])
    
    st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Espectro de Masas (GC-MS)</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_ms(selected_sustancia, data[selected_sustancia])
    with c2: render_ms(selected_adulterante, data[selected_adulterante])

def tab2_arbol_decision():
    st.markdown("<h2 style='text-align:center;'>🌳 Flujo de Descarte Analítico (ODV / Sirchie)</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔄 Reiniciar Árbol de Decisión", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("odv_"): del st.session_state[key]
                
    for key in ["odv_origen", "odv_veg", "odv_duq", "odv_kn", "odv_mayer", "odv_marquis", "odv_scott", "odv_dille", "odv_ehrlich"]:
        if key not in st.session_state: st.session_state[key] = None
        
    st.markdown("<hr style='border-color:#3A4252;'><div style='text-align:center;'><h4>Paso 0: ¿Qué tipo de indicio físico es?</h4></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
    with c2:
        if visual_button("🌿 Material Vegetal / Aceites", "#2D4A22", "btn_orig_v"): st.session_state.odv_origen = "veg"
    with c3:
        if visual_button("💊 Polvo / Cristal / Líquido", "#3B4D61", "btn_orig_p"): st.session_state.odv_origen = "polvo"
        
    if st.session_state.odv_origen:
        st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
        
        if st.session_state.odv_origen == "veg":
            st.markdown("<div style='text-align:center;'><h4>Paso 1: Pruebas Botánicas</h4></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c2:
                if visual_button("#908 Duquenois-Levine", "", "btn_veg_duq", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#6A2C70", top_txt="Gris", bot_txt="Púrpura"): st.session_state.odv_veg = "duq"
            with c3:
                if visual_button("#909 Reactivo KN", "#8B2500", "btn_veg_kn"): st.session_state.odv_veg = "kn"
            
            if st.session_state.odv_veg == "duq":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultado #908</h4></div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2: render_presumptive_card("Duquenois-Levine (#908)", "Púrpura en capa de cloroformo", "[SOSPECHA: Marihuana / Hachís / THC]", "", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#6A2C70", top_txt="Gris Pizarra", bot_txt="Púrpura Violáceo")
            elif st.session_state.odv_veg == "kn":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultado #909</h4></div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if visual_button("Positivo Marihuana", "#8B2500", "btn_kn_m"): st.session_state.odv_kn = "m"
                with c2:
                    if visual_button("Positivo Hachís", "#4A1500", "btn_kn_h"): st.session_state.odv_kn = "h"
                with c3:
                    if visual_button("Negativo", "#22262F", "btn_kn_neg"): st.session_state.odv_kn = "neg"
                if st.session_state.odv_kn == "m": render_presumptive_card("Reactivo KN (#909)", "Marrón Rojizo", "[SOSPECHA: Marihuana]", "#8B2500")
                elif st.session_state.odv_kn == "h": render_presumptive_card("Reactivo KN (#909)", "Marrón Rojizo Oscuro", "[SOSPECHA: Hachís / Aceite THC]", "#4A1500")
                elif st.session_state.odv_kn == "neg": st.info("Negativo para cannabinoides.")
                
        elif st.session_state.odv_origen == "polvo":
            st.markdown("<div style='text-align:center;'><h4>PASO 1: #901 Reactivo de Mayer (Identificación de Alcaloides)</h4></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c2:
                if visual_button("Positivo (Blanco/Crema)", "#FDFEFE", "btn_may_pos"): st.session_state.odv_mayer = "pos"
            with c3:
                if visual_button("Negativo (Sin Reacción)", "#22262F", "btn_may_neg"): st.session_state.odv_mayer = "neg"
                
            if st.session_state.odv_mayer == "pos":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 2.A: #902 Reactivo de Marquis</h4></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    if visual_button("Violeta / Púrpura", "#6B1D5D", "btn_marq_v"): st.session_state.odv_marquis = "v"
                with c2:
                    if visual_button("Naranja → Rojo", "linear-gradient(to right, #FF8C00, #FF0000, #663300)", "btn_marq_o"): st.session_state.odv_marquis = "o"
                with c3:
                    if visual_button("Negro", "#1A1A1A", "btn_marq_b"): st.session_state.odv_marquis = "b"
                with c4:
                    if visual_button("Negativo", "#22262F", "btn_marq_neg"): st.session_state.odv_marquis = "neg"
                    
                if st.session_state.odv_marquis == "v":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultados y Confirmación Opiáceos</h4></div>", unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1: render_presumptive_card("Reactivo de Marquis (#902)", "Violeta Oscuro", "[SOSPECHA: OPIÁCEOS]", "#6B1D5D")
                    with cc2: render_presumptive_card("Confirmar: Mecke (#924)", "Verde Inmediato", "[CONFIRMACIÓN SUGERIDA: OPIÁCEOS]", "#1E7E34")
                elif st.session_state.odv_marquis == "o":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultados y Confirmación Anfetaminas</h4></div>", unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1: render_presumptive_card("Reactivo de Marquis (#902)", "Secuencia Naranja → Rojo", "[SOSPECHA: ANFETAMINAS / METANFETAMINA]", "linear-gradient(to right, #FF8C00, #FF0000, #663300)")
                    with cc2: render_presumptive_card("Confirmar: Simon (#923)", "Azul Inmediato", "[CONFIRMACIÓN SUGERIDA: METANFETAMINA]", "#0047AB")
                elif st.session_state.odv_marquis == "b":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 2, 1])
                    with cc2: render_presumptive_card("Reactivo de Marquis (#902)", "Negro Inmediato", "[SOSPECHA: MDMA / MDA]", "#1A1A1A")
                elif st.session_state.odv_marquis == "neg":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 3: #904 Reactivo de Scott (Cocaína)</h4></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                    scott_html = "<div style=\"display:flex; justify-content:space-between; margin-bottom:5px;\"><div style=\"width:32%; height:50px; background:#00A8FF; border:1px solid #111; border-radius:4px; text-align:center; color:#fff; font-size:0.6rem; line-height:50px;\">1. Azul</div><div style=\"width:32%; height:50px; background:#E8A5B8; border:1px solid #111; border-radius:4px; text-align:center; color:#fff; font-size:0.6rem; line-height:50px;\">2. Rosa</div><div style=\"width:32%; height:50px; background:linear-gradient(to bottom, #E8A5B8 50%, #0047AB 50%); border:1px solid #111; border-radius:4px; text-align:center; color:#fff; font-size:0.55rem; line-height:25px;\">3. Rosa<br>Azul</div></div>"
                    with c2:
                        if visual_button("Positivo", "", "btn_scott_pos", custom_html=scott_html): st.session_state.odv_scott = "pos"
                    with c3:
                        if visual_button("Negativo", "#22262F", "btn_scott_neg"): st.session_state.odv_scott = "neg"
                        
                    if st.session_state.odv_scott == "pos":
                        st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                        cc1, cc2, cc3 = st.columns([1, 2, 1])
                        with cc2: render_presumptive_card("Reactivo de Scott (#904)", "Secuencia de 3 Ampolletas", "[SOSPECHA: COCAÍNA (HCl / Base Libre)]", "", custom_html=scott_html)
                    elif st.session_state.odv_scott == "neg":
                        st.warning("Tamizaje presuntivo negativo en ruta de alcaloides. Remitir al laboratorio.")
                        
            elif st.session_state.odv_mayer == "neg":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 2.B: #905 Reactivo de Dille-Koppanyi</h4></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                with c2:
                    if visual_button("Positivo (Púrpura)", "#C8A2C8", "btn_dil_pos"): st.session_state.odv_dille = "pos"
                with c3:
                    if visual_button("Negativo (Sin reacción)", "#22262F", "btn_dil_neg"): st.session_state.odv_dille = "neg"
                    
                if st.session_state.odv_dille == "pos":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 2, 1])
                    with cc2: render_presumptive_card("Reactivo de Dille-Koppanyi (#905)", "Púrpura Claro", "[SOSPECHA: BARBITÚRICOS]", "#C8A2C8")
                elif st.session_state.odv_dille == "neg":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 3.B: #907 Reactivo de Ehrlich</h4></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                    with c2:
                        if visual_button("Positivo (Púrpura)", "#9B30FF", "btn_ehr_pos"): st.session_state.odv_ehrlich = "pos"
                    with c3:
                        if visual_button("Negativo (Sin reacción)", "#22262F", "btn_ehr_neg"): st.session_state.odv_ehrlich = "neg"
                        
                    if st.session_state.odv_ehrlich == "pos":
                        st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                        cc1, cc2, cc3 = st.columns([1, 2, 1])
                        with cc2: render_presumptive_card("Reactivo de Ehrlich (#907)", "Púrpura Violáceo", "[SOSPECHA: LSD / INDOLES]", "#9B30FF")
                    elif st.session_state.odv_ehrlich == "neg":
                        st.warning("Tamizaje botánico y químico negativo. Muestra remitida a laboratorio para análisis instrumental.")
                        
    



def tab3_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph):
    import altair as alt
    st.markdown("<h2 style='text-align:center;'>🧪 Fisicoquímica y Extracción L-L</h2>", unsafe_allow_html=True)
    
    info_obj = data[selected_sustancia]
    info_cut = data[selected_adulterante]
    pka_obj = info_obj.get('pKa', '7')
    char_obj = info_obj.get('Carácter', 'Base')
    pka_cut = info_cut.get('pKa', '7')
    char_cut = info_cut.get('Carácter', 'Base')
    solv_obj = info_obj.get("Solubilidad (Clarke's)", "")
    solv_cut = info_cut.get("Solubilidad (Clarke's)", "")
    
    chart_data = []
    for ph_val in [x/10.0 for x in range(0, 141, 2)]:
        sp_a = calculate_ionization(pka_obj, char_obj, ph_val)
        sp_b = calculate_ionization(pka_cut, char_cut, ph_val)
        for k, v in sp_a.items():
            chart_data.append({"pH": ph_val, "% Especie": v, "Sustancia": f"{selected_sustancia} ({k})", "Categoría": selected_sustancia})
        for k, v in sp_b.items():
            chart_data.append({"pH": ph_val, "% Especie": v, "Sustancia": f"{selected_adulterante} ({k})", "Categoría": selected_adulterante})
            
    point_data = []
    sp_a_curr = calculate_ionization(pka_obj, char_obj, selected_ph)
    sp_b_curr = calculate_ionization(pka_cut, char_cut, selected_ph)
    for k, v in sp_a_curr.items():
        point_data.append({"pH": selected_ph, "% Especie": v, "Sustancia": f"{selected_sustancia} ({k})", "Categoría": selected_sustancia})
    for k, v in sp_b_curr.items():
        point_data.append({"pH": selected_ph, "% Especie": v, "Sustancia": f"{selected_adulterante} ({k})", "Categoría": selected_adulterante})

    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio"),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo"),
        color=alt.Color('Sustancia:N', scale=alt.Scale(scheme='set1'), legend=alt.Legend(orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == selected_adulterante, alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#000", strokeWidth=2).encode(x='pH:Q', y='% Especie:Q', color='Sustancia:N', tooltip=['pH:Q', '% Especie:Q', 'Sustancia:N'])
    rule = alt.Chart(alt.Data(values=[{"pH": selected_ph}])).mark_rule(strokeDash=[3, 3], color='black', strokeWidth=1).encode(x='pH:Q')
    
    ph_min, ph_max = find_optimal_separation_window(info_obj, info_cut)
    if ph_min is not None:
        shade = alt.Chart(alt.Data(values=[{"start": ph_min, "end": ph_max}])).mark_rect(opacity=0.1, color='#00FF9D').encode(
            x='start:Q',
            x2='end:Q'
        )
        layered_chart = (shade + base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
    else:
        layered_chart = (base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
        
    st.altair_chart(layered_chart, use_container_width=True)
    
    st.markdown("<h3 style='text-align:center;'>Protocolo Automatizado de Extracción Diferencial</h3>", unsafe_allow_html=True)
    if selected_sustancia == selected_adulterante: 
        st.info("Seleccione una sustancia objetivo y un adulterante distinto para generar el protocolo.")
    elif "No extraíble" in solv_obj or "No extraíble" in solv_cut:
        st.error("⚠️ **No es posible la extracción L-L convencional.**")
    elif ph_min is None: 
        st.error("⚠️ **No es posible proponer un protocolo basado exclusivamente en el pH (L-L simple).**")
        st.markdown("Se recomienda recurrir a Extracción en Fase Sólida (SPE) o separación cromatográfica (LC/GC).")
    else:
        opt_ph = (ph_min + ph_max) / 2
        sp_opt_obj = calculate_ionization(pka_obj, char_obj, opt_ph)
        obj_in_water = sp_opt_obj.get('Neutro', 0.0) < 50.0
        
        if obj_in_water:
            if 'anf' in char_obj.lower() or 'dip' in char_obj.lower():
                try:
                    pkas = [float(x.strip()) for x in str(pka_obj).split(',')]
                    pi = sum(pkas)/len(pkas)
                except:
                    pi = 7.0
                action = f"Ajustar cuidadosamente el pH a su punto de máxima neutralidad (aprox. pH {pi:.1f}) para precipitar o extraer al {selected_sustancia}."
            elif 'cido' in char_obj.lower():
                try: pka_val = float(str(pka_obj).split(',')[0])
                except: pka_val = opt_ph - 3
                new_ph = pka_val - 2 if pka_val - 2 >= 0 else 0
                action = f"Acidificar fuertemente (pH < {new_ph:.1f}) para protonar y volver neutro al {selected_sustancia}."
            else:
                try: pka_val = float(str(pka_obj).split(',')[0])
                except: pka_val = opt_ph + 3
                new_ph = pka_val + 2 if pka_val + 2 <= 14 else 14
                action = f"Alcalinizar (pH > {new_ph:.1f}) para desprotonar y liberar al {selected_sustancia} como base libre."
                
            protocol_html = f'''
            <div class="forensic-card">
            <h4 style="color: #003366 !important;">PASO 1: Partición Inicial</h4>
            <p>Ajustar el pH de la matriz acuosa a <b style="color:#27AE60;">{opt_ph:.1f}</b> (dentro de la ventana verde).</p>
            <p>A este pH, <b>{selected_sustancia}</b> estará ionizado (retención en agua) y <b>{selected_adulterante}</b> estará neutro (transferencia a orgánico).</p>
            <ul>
            <li>Añadir volumen igual de disolvente orgánico inmiscible, agitar y decantar.</li>
            <li><span style="color:#E74C3C;"><b>Acción:</b></span> El adulterante pasará a la fase orgánica. Lavar repetidamente y <b>desechar la fase orgánica</b>. Conservar únicamente la <b>fase acuosa</b>.</li>
            </ul>
            <h4 style="color: #003366 !important; margin-top:20px;">PASO 2: Aislamiento del Objetivo</h4>
            <ul>
            <li>{action}</li>
            <li>Añadir solvente orgánico fresco, agitar y decantar.</li>
            <li><b>Conservar la nueva fase orgánica</b> que ahora contiene el analito purificado y desechar el agua.</li>
            </ul>
            </div>
            '''
        else:
            protocol_html = f'''
            <div class="forensic-card">
            <h4 style="color: #003366 !important;">PASO 1: Partición Inicial</h4>
            <p>Ajustar el pH de la matriz acuosa a <b style="color:#27AE60;">{opt_ph:.1f}</b> (dentro de la ventana verde).</p>
            <p>A este pH, <b>{selected_sustancia}</b> estará neutro (transferencia a orgánico) y <b>{selected_adulterante}</b> estará ionizado (retención en agua).</p>
            <ul>
            <li>Añadir volumen igual de disolvente orgánico inmiscible, agitar y decantar.</li>
            <li><span style="color:#E74C3C;"><b>Acción:</b></span> Extraer con el solvente orgánico. El adulterante quedará atrapado en el agua. <b>Conservar la fase orgánica</b> que contiene al objetivo puro y descartar la fase acuosa.</li>
            </ul>
            <h4 style="color: #003366 !important; margin-top:20px;">PASO 2: Aislamiento</h4>
            <ul>
            <li>El analito objetivo ({selected_sustancia}) ya se encuentra aislado en la fase orgánica pura de forma neutra.</li>
            </ul>
            </div>
            '''
        st.markdown(protocol_html, unsafe_allow_html=True)


def tab_simulador():
    st.markdown("<h2 style='text-align:center;'>🧮 Simulador Manual de pH vs Ionización</h2>", unsafe_allow_html=True)
    st.write("Ingrese los datos de las sustancias para visualizar su comportamiento ácido-base.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Sustancia A")
        name_a = st.text_input("Nombre Sustancia A", "Sustancia A")
        pka_a = st.text_input("pKa (separar con coma si son varios)", "7.0", key='pka_a')
        char_a = st.selectbox("Carácter Químico", ["Ácido", "Base", "Anfótera", "Ácido diprótico"], key='char_a')
    with c2:
        st.markdown("### Sustancia B")
        name_b = st.text_input("Nombre Sustancia B", "Sustancia B")
        pka_b = st.text_input("pKa B", "9.0", key='pka_b')
        char_b = st.selectbox("Carácter Químico B", ["Base", "Ácido", "Anfótera", "Ácido diprótico"], key='char_b')
        
    sim_ph = st.slider("pH del Medio (Simulador)", 0.0, 14.0, 7.0, 0.1, key='sim_ph')
    
    chart_data = []
    for ph_val in [x/10.0 for x in range(0, 141, 2)]:
        sp_a = calculate_ionization(pka_a, char_a, ph_val)
        sp_b = calculate_ionization(pka_b, char_b, ph_val)
        for k, v in sp_a.items():
            chart_data.append({"pH": ph_val, "% Especie": v, "Sustancia": f"{name_a} ({k})", "Categoría": name_a})
        for k, v in sp_b.items():
            chart_data.append({"pH": ph_val, "% Especie": v, "Sustancia": f"{name_b} ({k})", "Categoría": name_b})
            
    point_data = []
    sp_a_curr = calculate_ionization(pka_a, char_a, sim_ph)
    sp_b_curr = calculate_ionization(pka_b, char_b, sim_ph)
    for k, v in sp_a_curr.items():
        point_data.append({"pH": sim_ph, "% Especie": v, "Sustancia": f"{name_a} ({k})", "Categoría": name_a})
    for k, v in sp_b_curr.items():
        point_data.append({"pH": sim_ph, "% Especie": v, "Sustancia": f"{name_b} ({k})", "Categoría": name_b})

    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio"),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo"),
        color=alt.Color('Sustancia:N', scale=alt.Scale(scheme='set1'), legend=alt.Legend(orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == name_b, alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#000", strokeWidth=2).encode(x='pH:Q', y='% Especie:Q', color='Sustancia:N', tooltip=['pH:Q', '% Especie:Q', 'Sustancia:N'])
    rule = alt.Chart(alt.Data(values=[{"pH": sim_ph}])).mark_rule(strokeDash=[3, 3], color='black', strokeWidth=1).encode(x='pH:Q')
    
    st.altair_chart((base_chart + rule + point_chart).interactive(), use_container_width=True)
    
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


def tab4_reactivos(data):
    tests = load_pruebas_csv()
    if not tests:
        st.error("Archivo Pruebas Presuntivas.csv no encontrado.")
        return
        
    st.markdown("<div style='text-align:center;'>Seleccione una prueba del manual:</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        test_names = list(tests.keys())
        selected = st.selectbox("Prueba", test_names, label_visibility="collapsed")
        
    if selected:
        info = tests[selected]
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Reactivos Necesarios</h3>", unsafe_allow_html=True)
        reactivos_raw = info.get('Reactivos', '').split('\n')
        react_list = []
        for r in reactivos_raw:
            parts = r.split(':', 1)
            if len(parts) == 2:
                react_list.append({"Reactivo": parts[0].strip(), "Preparación / Cantidad": parts[1].strip()})
            elif r.strip():
                react_list.append({"Reactivo": r.strip(), "Preparación / Cantidad": "Directo / Sin preparación previa"})
        if react_list: st.table(react_list)
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Procedimiento Analítico</h3>", unsafe_allow_html=True)
        proc_raw = info.get('Procedimiento', '').split('\n')
        
        flow_html = '<div style="display:flex; justify-content:center; align-items:center; flex-wrap:wrap; gap:20px; margin-top:20px;">'
        for idx, p in enumerate(proc_raw):
            if not p.strip(): continue
            flow_html += f"""
            <div class="forensic-card" style="width:250px; padding:15px; margin:0; position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="font-size:0.85rem; text-align:center; color:#000;">{p}</div>
            </div>
            """
            if idx < len(proc_raw) - 1:
                flow_html += '<div style="font-size:2.5rem; color:#003366; display:flex; align-items:center;">➡️</div>'
        flow_html += '</div>'
        
        st.markdown(flow_html, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Resultados Esperados (Colores)</h3>", unsafe_allow_html=True)
        # Load from DB
        db = data
        colores_html = '<div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap;">'
        found_any = False
        for sus, sus_info in db.items():
            prueba_db = sus_info.get('Prueba presuntiva', '')
            # Extraer el nombre base de la prueba del CSV de datos (ej. "Prueba de Marquis")
            if prueba_db and (prueba_db in selected or selected in prueba_db or prueba_db.replace("Prueba de ", "") in selected):
                c = sus_info.get('Color característico', 'No se especifica en Clarke\'s [1]')
                c_lower = c.lower()
                fallback_color = "#95a5a6" # default greyish
                if "naranja" in c_lower: fallback_color = "#d35400"
                elif "rojo" in c_lower or "roja" in c_lower: fallback_color = "#c0392b"
                elif "azul" in c_lower: fallback_color = "#2980b9"
                elif "violeta" in c_lower or "púrpura" in c_lower or "morado" in c_lower: fallback_color = "#8e44ad"
                elif "verde" in c_lower: fallback_color = "#27ae60"
                elif "amarillo" in c_lower: fallback_color = "#f39c12"
                elif "rosa" in c_lower: fallback_color = "#fd79a8"
                elif "marrón" in c_lower or "cafe" in c_lower: fallback_color = "#8B4513"
                elif "negro" in c_lower: fallback_color = "#2c3e50"
                
                colores_html += f"<div class='metric-box' style='width: 150px; background: {fallback_color};'><h4 style='color:#FFF !important; margin:0;'>{sus}</h4><p style='color:#FFF; font-size:0.8rem; margin:0;'>{c}</p></div>"
                found_any = True
        colores_html += '</div>'
        if found_any:
            st.markdown(colores_html, unsafe_allow_html=True)
        else:
            st.info("No hay sustancias en la base de datos que usen exclusivamente esta prueba como primaria.")
            
                
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Interferencias y Limitaciones</h3>", unsafe_allow_html=True)
        st.table([
            {"Tipo de Falso": "Falso Positivo", "Descripción / Sustancias Interferentes": info.get('Falsos Positivos', '')},
            {"Tipo de Falso": "Falso Negativo", "Descripción / Sustancias Interferentes": info.get('Falsos Negativos', '')}
        ])
def main():
    inject_custom_css()
    st.markdown("<h1>Análisis Químico de Sustancias</h1>", unsafe_allow_html=True)
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'pH_vs_Ionizacion_Comparada_Datos.csv')
    data = load_data(csv_path)
    if not data:
        st.error("Error crítico: Dataset no disponible.")
        return
        
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>Panel de Control</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #3A4252;'>", unsafe_allow_html=True)
        sustancias_list = sorted(list(data.keys()))
        selected_sustancia = st.selectbox("🎯 Sustancia Objetivo (Analito)", sustancias_list, index=0)
        selected_adulterante = st.selectbox("✂️ Sustancia de Corte", sustancias_list, index=1 if len(sustancias_list) > 1 else 0)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_ph = st.slider("🧪 pH del Medio Extractor", 0.0, 14.0, 7.0, 0.1)
        st.markdown("<br><br><br><div style=\"background-color: #D3D3D3; padding: 15px; border-radius: 8px; border: 1px solid #003366; color: #000000; text-align: center; font-size: 0.8rem;\"><b>Realizado por:</b><br/>QFB Edgar Oswaldo Díaz Andrade<br/><br/><span style=\"color:#003366;\">Herramienta interactiva para perfilación presuntiva e instrumental.</span></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab_sim, tab4 = st.tabs(["📋 Comparativa", "🔍 Reactividad Cruzada", "⚗️ Gráfica Fisicoquímica L-L", "🧮 Simulador Manual", "🧪 Preparación de Reactivos"])
    with tab1: tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph)
    with tab2: tab2_arbol_decision()
    with tab3: tab3_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph)
    with tab_sim: tab_simulador()
    with tab4: tab4_reactivos(data)

    st.markdown('''
    <div class="nota-card" style="border-left-color: #E74C3C; margin-bottom: 20px;">
        <p style="color: #000000; text-align:center;"><b>⚠️ NOTA ANALÍTICA:</b> Todo resultado positivo presuntivo tiene que confirmarse por pruebas confirmatorias instrumentales (como GC-MS o ATR-FTIR).</p>
    </div>
    <div class="footer">
        <b>Referencias Bibliográficas:</b><br/>
        Moffat AC, Osselton MD, Widdop B, Watts J, editores. <i>Clarke's Analysis of Drugs and Poisons: In pharmaceuticals, body fluids and postmortem material</i>. 4a ed. Londres: Pharmaceutical Press; 2011.<br/>
        Oficina de las Naciones Unidas contra la Droga y el Delito (UNODC). <i>Métodos para el ensayo inmediato de drogas de uso indebido</i>. Manual para laboratorios nacionales de estupefacientes. ST/NAR/13/Rev.1. Naciones Unidas: Nueva York; 2006.<br/>
        Francisco RC. Tablas de Espectroscopía Infrarroja [3].<br/><span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
    </div>
    ''', unsafe_allow_html=True)

def set_css():
    st.markdown('''
    <style>
    /* Pearl white background */
    .stApp, .main {
        background-color: #FBFBF9 !important;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] { background-color: #E0E0E0 !important; text-align: center; color: #000000 !important;}
    
    /* Dark blue titles */
    h1, h2, h3, h4, h5, h6 { color: #003366 !important; text-shadow: none; text-align: center !important; width: 100%; display: block; }
    p, span, div, label, li { text-align: center; color: #000000; }
    
    ul { list-style-position: inside; text-align: center; padding: 0; }
    
    table { width: 100%; margin: 0 auto; text-align: center; transition: all 0.3s ease-in-out; color: #000000 !important; }
    th, td { text-align: center !important; color: #000000 !important; }
    
    img { transition: all 0.3s ease-in-out; border-radius: 8px; margin: 0 auto; display: block; }
    
    .forensic-card { 
        background-color: #FFFFFF; 
        border: 1px solid #CCCCCC; 
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        transition: all 0.3s ease-in-out; 
    }
    .forensic-card:hover { 
        transform: scale(1.02); 
        box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2); 
        border-color: #003366; 
    }
    
    img:hover { 
        transform: scale(1.02); 
        box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2); 
    }
    
    .nota-card { 
        background-color: #D3D3D3; 
        border-left: 5px solid #003366; 
        padding: 15px; 
        margin-top: 30px; 
        border-radius: 4px;
        transition: all 0.3s ease-in-out;
    }
    .nota-card:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 15px rgba(0, 51, 102, 0.4); 
        border: 1px solid #003366; 
        border-left: 5px solid #003366; 
    }
    
    .numeric-val { font-family: 'Courier New', Courier, monospace; color: #003366; font-weight: bold; }
    .color-box { height: 50px; width: 100%; border-radius: 6px; margin-bottom: 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border: 1px solid #CCCCCC; }
        .metric-box:hover { transform: scale(1.05); box-shadow: 0 8px 16px rgba(0,0,0,0.2); }
    </style>
    ''', unsafe_allow_html=True)


if __name__ == '__main__':
    main()

