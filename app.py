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
    .stApp { background-color: #1E222B; color: #E1E4EA; font-family: 'Segoe UI', sans-serif; text-align: center; }
    [data-testid="stSidebar"] { background-color: #171A21 !important; text-align: center; }
    
    h1, h2, h3, h4, h5, h6 { color: #9E9E9E !important; text-shadow: none; text-align: center !important; width: 100%; display: block; }
    p, span, div, label { text-align: center; }
    
    ul { list-style-position: inside; text-align: center; padding: 0; }
    li { text-align: center; }
    
    table { width: 100%; margin: 0 auto; text-align: center; transition: all 0.3s ease-in-out; }
    th, td { text-align: center !important; }
    
    img { transition: all 0.3s ease-in-out; border-radius: 8px; margin: 0 auto; display: block; }
    
    .forensic-card { 
        background-color: #22262F; 
        border: 1px solid #3A4252; 
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        transition: all 0.3s ease-in-out; 
    }
    .forensic-card:hover { 
        transform: scale(1.02); 
        box-shadow: 0 8px 16px rgba(255, 255, 255, 0.2); 
        border-color: #FFF; 
    }
    
    img:hover { 
        transform: scale(1.02); 
        box-shadow: 0 8px 16px rgba(255, 255, 255, 0.2); 
    }
    
    .nota-card { 
        background-color: #22262F; 
        border-left: 5px solid #E74C3C; 
        padding: 15px; 
        margin-top: 30px; 
        border-radius: 4px;
        transition: all 0.3s ease-in-out;
    }
    .nota-card:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.8); 
        border: 1px solid #E74C3C; 
        border-left: 5px solid #E74C3C; 
    }
    
    .numeric-val { font-family: 'Courier New', Courier, monospace; color: #E1E4EA; font-weight: bold; }
    .color-box { height: 50px; width: 100%; border-radius: 6px; margin-bottom: 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); border: 1px solid #111; }
    .biphasic-tube { height: 70px; width: 100%; border-radius: 6px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #111; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); margin-bottom: 12px; }
    .biphasic-top { height: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #fff; text-shadow: 1px 1px 2px #000; border-bottom: 1px solid rgba(255,255,255,0.2); }
    .biphasic-bottom { height: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #fff; text-shadow: 1px 1px 2px #000; }
    .footer { text-align: center; padding: 20px; font-size: 0.85rem; color: #8892B0; border-top: 1px solid #3A4252; margin-top: 40px; width: 100%; }
    .footer b { color: #9E9E9E; }
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

def calculate_ionization(pka_str, character, ph):
    parts = [p.strip() for p in str(pka_str).split(',') if p.strip()]
    if not parts:
        return 0.0, 100.0
    
    character = character.strip().lower()
    
    if len(parts) == 1:
        try: pka_val = float(parts[0])
        except Exception: return 0.0, 100.0
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
        return ion, 100.0 - ion
    
    elif len(parts) >= 2:
        try:
            pk1, pk2 = sorted([float(parts[0]), float(parts[1])])
        except Exception:
            return 0.0, 100.0
            
        if 'anfótera' in character or 'anfotera' in character:
            try:
                denom = 1.0 + 10.0**(pk1 - ph) + 10.0**(ph - pk2)
                neutral = 100.0 / denom
                ion = 100.0 - neutral
            except OverflowError:
                if ph < pk1: neutral, ion = 0.0, 100.0
                elif ph > pk2: neutral, ion = 0.0, 100.0
                else: neutral, ion = 100.0, 0.0
            return ion, neutral
        elif 'ácido' in character or 'acido' in character:
            try:
                denom = 1.0 + 10.0**(ph - pk1) + 10.0**(2*ph - pk1 - pk2)
                neutral = 100.0 / denom
                ion = 100.0 - neutral
            except OverflowError:
                neutral = 100.0 if ph < pk1 else 0.0
                ion = 100.0 - neutral
            return ion, neutral
        else:
            try:
                denom = 1.0 + 10.0**(pk2 - ph) + 10.0**(pk1 + pk2 - 2*ph)
                neutral = 100.0 / denom
                ion = 100.0 - neutral
            except OverflowError:
                neutral = 100.0 if ph > pk2 else 0.0
                ion = 100.0 - neutral
            return ion, neutral

def find_optimal_separation_window(info_obj, info_cut):
    if "No extraíble" in info_obj.get('Disolvente        <', '') or "No extraíble" in info_obj.get('>       Disolvente', '') or "No extraíble" in info_cut.get('Disolvente        <', '') or "No extraíble" in info_cut.get('>       Disolvente', ''):
        return None, None
    window = []
    pka_obj, char_obj = info_obj.get('pKa', '7'), info_obj.get('Carácter', 'Base')
    pka_cut, char_cut = info_cut.get('pKa', '7'), info_cut.get('Carácter', 'Base')
    for ph_val in [x/10.0 for x in range(0, 141)]:
        i_obj, _ = calculate_ionization(pka_obj, char_obj, ph_val)
        i_cut, _ = calculate_ionization(pka_cut, char_cut, ph_val)
        if abs(i_obj - i_cut) >= 90.0: window.append(ph_val)
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
    st.markdown(f'''<div class="forensic-card">{visual}<div style="font-size: 1.1rem; font-weight: 600; color: #E1E4EA; margin-bottom: 5px; text-align:center;">{test_name}</div><div style="font-size: 0.9rem; color: #A0AABF; margin-bottom: 10px; text-align:center;"><b>Tono Visual:</b> {color_desc}</div><div style="font-size: 0.95rem; color: #00FF9D; font-weight: bold; text-align:center;">{interpretation}</div></div>''', unsafe_allow_html=True)

def render_structure(sustancia, info, selected_ph):
    pka, char = info.get('pKa', '7'), info.get('Carácter', 'Base')
    obj_is_ion, _ = calculate_ionization(pka, char, selected_ph)
    suffix = 'ion' if obj_is_ion >= 50.0 else 'base'
    img_path = find_image(sustancia, suffix)
    if img_path: st.image(img_path, use_container_width=True)
    else: st.info("ℹ️ Estructura molecular no disponible.")

def render_presumptive_info(sustancia, info):
    prueba = info.get('Prueba presuntiva', 'N/A')
    color = info.get('Color característico', 'N/A')
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
    if "cocaína" in nombre or "cocaina" in nombre: render_presumptive_card("Scott (#904)", f"Doc: {color}", "Cocaína", "", True, "#F5B7B1", "#0077C8", "Acuosa", "Orgánica")
    elif "metanfetamina" in nombre or "anfetamina" in nombre: render_presumptive_card("Marquis (#902)", f"Doc: {color}", "Anfetaminas", "linear-gradient(to right, #D9531E, #E74C3C, #5C2C16)")
    elif "mdma" in nombre or "mda" in nombre: render_presumptive_card("Marquis (#902)", f"Doc: {color}", "Entactógenos", "#1A1A1A")
    elif "lsd" in nombre: render_presumptive_card("Ehrlich (#907)", f"Doc: {color}", "Indoles", "#8E44AD")
    elif "thc" in nombre: render_presumptive_card("Duquenois-Levine", f"Doc: {color}", "Cannabinoides", "", True, "#7F8C8D", "#5B2C6F", "Sup.", "Inf.")
    elif "heroína" in nombre or "heroina" in nombre: render_presumptive_card("Marquis (#902)", f"Doc: {color}", "Opiáceos", "#5B2C6F")
    else: render_presumptive_card(prueba, f"Doc: {color}", "Prueba base", fallback_color)

def render_ir(sustancia, info):
    img_ir = find_image(sustancia, 'Espectro_IR')
    if img_ir: st.image(img_ir, use_container_width=True)
    else: st.warning("⚠️ Espectro IR no disponible.")
    picos_ir = []
    for i in range(1, 7):
        num = info.get(f"P{i}", "").strip()
        if num: picos_ir.append({"Vibración (cm⁻¹)": num})
    if picos_ir: st.table(picos_ir)

def render_ms(sustancia, info):
    img_ms = find_image(sustancia, 'GS-MS')
    if img_ms: st.image(img_ms, use_container_width=True)
    else: st.warning("⚠️ Espectro GC-MS no disponible.")
    iones = []
    for i in range(1, 9):
        ion_val = info.get(f"I{i}", "").strip()
        if ion_val: iones.append({"Relación m/z": ion_val})
    if iones: st.table(iones)

def tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph):
    st.markdown("<h2 style='text-align:center;'>📋 Ficha Comparativa (Sustancia vs Adulterante)</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<h3 style='color:#00E5FF; text-align:center;'>🎯 Analito Objetivo:<br>{selected_sustancia}</h3>", unsafe_allow_html=True)
    with c2: st.markdown(f"<h3 style='color:#E74C3C; text-align:center;'>✂️ Adulterante:<br>{selected_adulterante}</h3>", unsafe_allow_html=True)
    
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
        st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div>", unsafe_allow_html=True)
        
        if st.session_state.odv_origen == "veg":
            st.markdown("<div style='text-align:center;'><h4>Paso 1: Pruebas Botánicas</h4></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c2:
                if visual_button("#908 Duquenois-Levine", "", "btn_veg_duq", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#6A2C70", top_txt="Gris", bot_txt="Púrpura"): st.session_state.odv_veg = "duq"
            with c3:
                if visual_button("#909 Reactivo KN", "#8B2500", "btn_veg_kn"): st.session_state.odv_veg = "kn"
            
            if st.session_state.odv_veg == "duq":
                st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>Resultado #908</h4></div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2: render_presumptive_card("Duquenois-Levine (#908)", "Púrpura en capa de cloroformo", "[SOSPECHA: Marihuana / Hachís / THC]", "", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#6A2C70", top_txt="Gris Pizarra", bot_txt="Púrpura Violáceo")
            elif st.session_state.odv_veg == "kn":
                st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>Resultado #909</h4></div>", unsafe_allow_html=True)
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
                st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>PASO 2.A: #902 Reactivo de Marquis</h4></div>", unsafe_allow_html=True)
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
                    st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>Resultados y Confirmación Opiáceos</h4></div>", unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1: render_presumptive_card("Reactivo de Marquis (#902)", "Violeta Oscuro", "[SOSPECHA: OPIÁCEOS]", "#6B1D5D")
                    with cc2: render_presumptive_card("Confirmar: Mecke (#924)", "Verde Inmediato", "[CONFIRMACIÓN SUGERIDA: OPIÁCEOS]", "#1E7E34")
                elif st.session_state.odv_marquis == "o":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>Resultados y Confirmación Anfetaminas</h4></div>", unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1: render_presumptive_card("Reactivo de Marquis (#902)", "Secuencia Naranja → Rojo", "[SOSPECHA: ANFETAMINAS / METANFETAMINA]", "linear-gradient(to right, #FF8C00, #FF0000, #663300)")
                    with cc2: render_presumptive_card("Confirmar: Simon (#923)", "Azul Inmediato", "[CONFIRMACIÓN SUGERIDA: METANFETAMINA]", "#0047AB")
                elif st.session_state.odv_marquis == "b":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 2, 1])
                    with cc2: render_presumptive_card("Reactivo de Marquis (#902)", "Negro Inmediato", "[SOSPECHA: MDMA / MDA]", "#1A1A1A")
                elif st.session_state.odv_marquis == "neg":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>PASO 3: #904 Reactivo de Scott (Cocaína)</h4></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                    scott_html = "<div style=\"display:flex; justify-content:space-between; margin-bottom:5px;\"><div style=\"width:32%; height:50px; background:#00A8FF; border:1px solid #111; border-radius:4px; text-align:center; color:#fff; font-size:0.6rem; line-height:50px;\">1. Azul</div><div style=\"width:32%; height:50px; background:#E8A5B8; border:1px solid #111; border-radius:4px; text-align:center; color:#fff; font-size:0.6rem; line-height:50px;\">2. Rosa</div><div style=\"width:32%; height:50px; background:linear-gradient(to bottom, #E8A5B8 50%, #0047AB 50%); border:1px solid #111; border-radius:4px; text-align:center; color:#fff; font-size:0.55rem; line-height:25px;\">3. Rosa<br>Azul</div></div>"
                    with c2:
                        if visual_button("Positivo", "", "btn_scott_pos", custom_html=scott_html): st.session_state.odv_scott = "pos"
                    with c3:
                        if visual_button("Negativo", "#22262F", "btn_scott_neg"): st.session_state.odv_scott = "neg"
                        
                    if st.session_state.odv_scott == "pos":
                        st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div>", unsafe_allow_html=True)
                        cc1, cc2, cc3 = st.columns([1, 2, 1])
                        with cc2: render_presumptive_card("Reactivo de Scott (#904)", "Secuencia de 3 Ampolletas", "[SOSPECHA: COCAÍNA (HCl / Base Libre)]", "", custom_html=scott_html)
                    elif st.session_state.odv_scott == "neg":
                        st.warning("Tamizaje presuntivo negativo en ruta de alcaloides. Remitir al laboratorio.")
                        
            elif st.session_state.odv_mayer == "neg":
                st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>PASO 2.B: #905 Reactivo de Dille-Koppanyi</h4></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                with c2:
                    if visual_button("Positivo (Púrpura)", "#C8A2C8", "btn_dil_pos"): st.session_state.odv_dille = "pos"
                with c3:
                    if visual_button("Negativo (Sin reacción)", "#22262F", "btn_dil_neg"): st.session_state.odv_dille = "neg"
                    
                if st.session_state.odv_dille == "pos":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 2, 1])
                    with cc2: render_presumptive_card("Reactivo de Dille-Koppanyi (#905)", "Púrpura Claro", "[SOSPECHA: BARBITÚRICOS]", "#C8A2C8")
                elif st.session_state.odv_dille == "neg":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div><div style='text-align:center;'><h4>PASO 3.B: #907 Reactivo de Ehrlich</h4></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                    with c2:
                        if visual_button("Positivo (Púrpura)", "#9B30FF", "btn_ehr_pos"): st.session_state.odv_ehrlich = "pos"
                    with c3:
                        if visual_button("Negativo (Sin reacción)", "#22262F", "btn_ehr_neg"): st.session_state.odv_ehrlich = "neg"
                        
                    if st.session_state.odv_ehrlich == "pos":
                        st.markdown("<div style='text-align:center; font-size:24px; color:#A0AABF;'>⬇</div>", unsafe_allow_html=True)
                        cc1, cc2, cc3 = st.columns([1, 2, 1])
                        with cc2: render_presumptive_card("Reactivo de Ehrlich (#907)", "Púrpura Violáceo", "[SOSPECHA: LSD / INDOLES]", "#9B30FF")
                    elif st.session_state.odv_ehrlich == "neg":
                        st.warning("Tamizaje botánico y químico negativo. Muestra remitida a laboratorio para análisis instrumental.")
                        
    st.markdown('''
    <div class="nota-card">
        <h4 style="color: #E74C3C !important; margin: 0 0 10px 0; text-align:center;">NOTA OFICIAL</h4>
        <p style="margin: 0; font-size: 0.9rem; color: #A0AABF; text-align:center;">NOTA: Cualquier resultado presuntivo tiene que ser enviado a un laboratorio para realizar pruebas confirmatorias instrumentales como IR o GC-MS.</p>
    </div>
    ''', unsafe_allow_html=True)

def tab3_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph):
    st.markdown("<h2 style='text-align:center;'>⚗️ Separación L-L y Purificación de Muestras</h2>", unsafe_allow_html=True)
    info_obj, info_cut = data[selected_sustancia], data[selected_adulterante]
    pka_obj, char_obj = info_obj.get('pKa', '7'), info_obj.get('Carácter', 'Base')
    pka_cut, char_cut = info_cut.get('pKa', '7'), info_cut.get('Carácter', 'Base')
    i_obj_curr, n_obj_curr = calculate_ionization(pka_obj, char_obj, selected_ph)
    i_cut_curr, n_cut_curr = calculate_ionization(pka_cut, char_cut, selected_ph)
    solv_obj, solv_cut = get_solvent(info_obj, pka_obj, selected_ph), get_solvent(info_cut, pka_cut, selected_ph)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #00E5FF;"><h4 style="color: #00E5FF !important; margin-top:0;">🎯 Analito Objetivo: {selected_sustancia}</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {char_obj}</p><p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_obj}</span></p><p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_obj}</p><hr style="border-color:#3A4252; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_obj_curr:.2f}%</span></p><p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_obj_curr:.2f}%</span></p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #E74C3C;"><h4 style="color: #E74C3C !important; margin-top:0;">✂️ Adulterante: {selected_adulterante}</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {char_cut}</p><p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_cut}</span></p><p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_cut}</p><hr style="border-color:#3A4252; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_cut_curr:.2f}%</span></p><p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_cut_curr:.2f}%</span></p></div>', unsafe_allow_html=True)
        
    chart_data = []
    for ph_val in [x/10.0 for x in range(0, 141, 2)]:
        i_o, n_o = calculate_ionization(pka_obj, char_obj, ph_val)
        i_c, n_c = calculate_ionization(pka_cut, char_cut, ph_val)
        chart_data.extend([{"pH": ph_val, "% Especie": i_o, "Sustancia": "Objetivo (Ionizado - Agua)", "Categoría": "Objetivo"}, {"pH": ph_val, "% Especie": n_o, "Sustancia": "Objetivo (Neutro - Orgánico)", "Categoría": "Objetivo"}, {"pH": ph_val, "% Especie": i_c, "Sustancia": "Corte (Ionizado - Agua)", "Categoría": "Adulterante"}, {"pH": ph_val, "% Especie": n_c, "Sustancia": "Corte (Neutro - Orgánico)", "Categoría": "Adulterante"}])
        
    point_data = [{"pH": selected_ph, "% Especie": i_obj_curr, "Sustancia": "Objetivo (Ionizado - Agua)", "Categoría": "Objetivo"}, {"pH": selected_ph, "% Especie": n_obj_curr, "Sustancia": "Objetivo (Neutro - Orgánico)", "Categoría": "Objetivo"}, {"pH": selected_ph, "% Especie": i_cut_curr, "Sustancia": "Corte (Ionizado - Agua)", "Categoría": "Adulterante"}, {"pH": selected_ph, "% Especie": n_cut_curr, "Sustancia": "Corte (Neutro - Orgánico)", "Categoría": "Adulterante"}]
    
    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio", axis=alt.Axis(gridColor="#3A4252", labelColor="#E1E4EA", titleColor="#E1E4EA")),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo de la Especie", axis=alt.Axis(gridColor="#3A4252", labelColor="#E1E4EA", titleColor="#E1E4EA")),
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=['Objetivo (Ionizado - Agua)', 'Objetivo (Neutro - Orgánico)', 'Corte (Ionizado - Agua)', 'Corte (Neutro - Orgánico)'], range=['#00E5FF', '#F1C40F', '#E74C3C', '#E67E22']), legend=alt.Legend(title="Especies", titleColor="#E1E4EA", labelColor="#E1E4EA", orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == 'Adulterante', alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#fff", strokeWidth=2).encode(x='pH:Q', y='% Especie:Q', color=alt.Color('Sustancia:N', scale=alt.Scale(domain=['Objetivo (Ionizado - Agua)', 'Objetivo (Neutro - Orgánico)', 'Corte (Ionizado - Agua)', 'Corte (Neutro - Orgánico)'], range=['#00E5FF', '#F1C40F', '#E74C3C', '#E67E22']), legend=None), tooltip=['pH:Q', '% Especie:Q', 'Sustancia:N'])
    rule = alt.Chart(alt.Data(values=[{"pH": selected_ph}])).mark_rule(strokeDash=[3, 3], color='#E1E4EA', strokeWidth=1).encode(x='pH:Q')
    
    ph_min, ph_max = find_optimal_separation_window(info_obj, info_cut)
    if ph_min is not None:
        shade = alt.Chart(alt.Data(values=[{"start": ph_min, "end": ph_max}])).mark_rect(opacity=0.1, color='#00FF9D').encode(x='start:Q', x2='end:Q')
        layered_chart = (shade + base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
    else:
        layered_chart = (base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
    st.altair_chart(layered_chart, use_container_width=True)

    st.markdown("<h3 style='text-align:center;'>Protocolo Automatizado de Extracción Diferencial</h3>", unsafe_allow_html=True)
    if selected_sustancia == selected_adulterante: 
        st.info("Seleccione una sustancia objetivo y un adulterante distinto para generar el protocolo.")
    elif "No extraíble" in solv_obj or "No extraíble" in solv_cut:
        st.error("⚠️ **No es posible la extracción L-L convencional.**")
        st.markdown('''
        <div class="nota-card" style="border-left-color: #E74C3C;">
            <p style="color: #A0AABF; text-align:center;"><b>Motivo:</b> Una o ambas sustancias no son fácilmente extraíbles con solventes orgánicos inmiscibles debido a su naturaleza estructural (ej. sales de amonio cuaternario, polaridad extrema o insolubilidad en solventes orgánicos comunes).</p>
        </div>
        ''', unsafe_allow_html=True)
    elif ph_min is None: 
        st.error("⚠️ **No es posible lograr una separación selectiva simple por extracción Líquido-Líquido.**")
        st.markdown('''
        <div class="nota-card" style="border-left-color: #F1C40F;">
            <p style="color: #A0AABF; text-align:center;"><b>Motivo:</b> Los pKa de ambas sustancias son demasiado cercanos, o su comportamiento de ionización a lo largo del gradiente de pH (ej. sustancias anfóteras) impide que exista una diferencia de ionización ≥ 90% en ninguna condición acuosa. Se recomienda utilizar extracción en fase sólida (SPE) o cromatografía preparativa.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        opt_ph = (ph_min + ph_max) / 2
        i_opt_obj, _ = calculate_ionization(pka_obj, char_obj, opt_ph)
        obj_in_water = i_opt_obj >= 50.0
        
        if obj_in_water:
            action = f"Acidificar fuertemente a pH < {max(0, opt_ph - 3):.1f} para protonar y volver neutro al {selected_sustancia}." if 'ácido' in char_obj or 'acido' in char_obj else f"Alcalinizar a pH > {min(14, opt_ph + 3):.1f} para desprotonar y liberar al {selected_sustancia} como base libre."
            protocol_html = f'''<div class="forensic-card">
<h4 style="color: #E1E4EA !important;">PASO 1: Partición Inicial</h4>
<p>Ajustar el pH a <b style="color:#00FF9D;">{opt_ph:.1f}</b>.</p>
<ul>
<li>Añadir volumen igual de disolvente orgánico inmiscible (ej. {solv_cut}), agitar y decantar.</li>
<li><span style="color:#E74C3C;"><b>Acción:</b></span> El adulterante pasará a la fase orgánica. <b>Desechar la fase orgánica</b>. Conservar únicamente la <b>fase acuosa</b>.</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 2: Aislamiento del Objetivo</h4>
<ul>
<li>{action}</li>
<li>Añadir solvente orgánico fresco, agitar y decantar.</li>
<li><b>La sustancia objetivo ({selected_sustancia}) se encuentra ahora purificada y aislada en la fase orgánica.</b> Conservar esta nueva fase orgánica.</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 3: Secado y Reconstitución</h4>
<ul>
<li>Llevar a sequedad total la fase orgánica.</li>
<li>Reconstituir el extracto seco para la lectura confirmatoria instrumental pertinente (GC-MS / FTIR).</li>
</ul>
</div>'''
        else:
            protocol_html = f'''<div class="forensic-card">
<h4 style="color: #E1E4EA !important;">PASO 1: Partición Inicial</h4>
<p>Ajustar el pH a <b style="color:#00FF9D;">{opt_ph:.1f}</b>.</p>
<ul>
<li>Añadir volumen igual de disolvente orgánico inmiscible (ej. {solv_obj}), agitar y decantar.</li>
<li><span style="color:#E74C3C;"><b>Acción:</b></span> Extraer con el solvente orgánico. El adulterante quedará atrapado en el agua. <b>Conservar la fase orgánica</b>.</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 2: Aislamiento</h4>
<ul>
<li><b>La sustancia objetivo ({selected_sustancia}) ya se encuentra purificada y aislada directamente en esta fase orgánica.</b></li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 3: Secado y Reconstitución</h4>
<ul>
<li>Llevar a sequedad total la fase orgánica.</li>
<li>Reconstituir el extracto seco para la lectura confirmatoria instrumental pertinente (GC-MS / FTIR).</li>
</ul>
</div>'''
        st.markdown(protocol_html, unsafe_allow_html=True)

def tab4_reactivos():
    st.markdown("<h2 style='text-align:center;'>🧪 Preparación de Reactivos y Pruebas</h2>", unsafe_allow_html=True)
    tests = load_pruebas_csv()
    if not tests:
        st.error("Archivo Pruebas Presuntivas.csv no encontrado.")
        return
        
    st.markdown("<div style='text-align:center;'>Seleccione una prueba del manual de UNODC:</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        test_names = list(tests.keys())
        selected = st.selectbox("Prueba", test_names, label_visibility="collapsed")
        
    if selected:
        info = tests[selected]
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Reactivos Necesarios</h3>", unsafe_allow_html=True)
        reactivos_raw = info['Reactivos'].split('\n')
        react_list = []
        for r in reactivos_raw:
            parts = r.split(':', 1)
            if len(parts) == 2:
                react_list.append({"Reactivo": parts[0].strip(), "Preparación / Cantidad": parts[1].strip()})
            else:
                react_list.append({"Reactivo": r.strip(), "Preparación / Cantidad": "Directo / Sin preparación previa"})
        if react_list: st.table(react_list)
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Procedimiento Analítico</h3>", unsafe_allow_html=True)
        proc_raw = info['Procedimiento'].split('\n')
        
        flow_html = '<div style="display:flex; justify-content:center; align-items:center; flex-wrap:wrap; gap:20px; margin-top:20px;">'
        for idx, p in enumerate(proc_raw):
            flow_html += f'''
            <div class="forensic-card" style="width:250px; padding:15px; margin:0; position:relative; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="font-size:0.85rem; text-align:center; color:#E1E4EA;">{p}</div>
            </div>
            '''
            if idx < len(proc_raw) - 1:
                flow_html += '<div style="font-size:2.5rem; color:#00E5FF; display:flex; align-items:center;">➡️</div>'
        flow_html += '</div>'
        
        st.markdown(flow_html, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Interferencias y Limitaciones</h3>", unsafe_allow_html=True)
        st.table([
            {"Tipo de Falso": "Falso Positivo", "Descripción / Sustancias Interferentes": info['Falsos Positivos']},
            {"Tipo de Falso": "Falso Negativo", "Descripción / Sustancias Interferentes": info['Falsos Negativos']}
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
        sustancias_list = list(data.keys())
        selected_sustancia = st.selectbox("🎯 Sustancia Objetivo (Analito)", sustancias_list, index=0)
        selected_adulterante = st.selectbox("✂️ Sustancia de Corte", sustancias_list, index=1 if len(sustancias_list) > 1 else 0)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_ph = st.slider("🧪 pH del Medio Extractor", 0.0, 14.0, 7.0, 0.1)
        st.markdown("<br><br><br><div style=\"background-color: #22262F; padding: 15px; border-radius: 8px; border: 1px solid #3A4252; text-align: center; font-size: 0.8rem;\"><b>Realizado por:</b><br/>QFB Edgar Oswaldo Díaz Andrade<br/><br/><span style=\"color:#A0AABF;\">Herramienta interactiva para perfilación presuntiva e instrumental.</span></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 1. Ficha Comparativa", "🌳 2. Árbol de Decisión", "⚗️ 3. Fisicoquímica L-L", "🧪 4. Preparación de Reactivos"])
    with tab1: tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph)
    with tab2: tab2_arbol_decision()
    with tab3: tab3_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph)
    with tab4: tab4_reactivos()

    st.markdown('''
    <div class="footer">
        <b>Referencias Bibliográficas:</b><br/>
        Moffat AC, Osselton MD, Widdop B, Watts J, editores. <i>Clarke's Analysis of Drugs and Poisons: In pharmaceuticals, body fluids and postmortem material</i>. 4a ed. Londres: Pharmaceutical Press; 2011.<br/>
        Oficina de las Naciones Unidas contra la Droga y el Delito (UNODC). <i>Métodos para el ensayo inmediato de drogas de uso indebido</i>. Manual para laboratorios nacionales de estupefacientes. ST/NAR/13/Rev.1. Naciones Unidas: Nueva York; 2006.<br/>
        <span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
