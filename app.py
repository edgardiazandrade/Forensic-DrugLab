import streamlit as st
import csv
import os
import re
import math
import unicodedata
import base64
import altair as alt

st.set_page_config(page_title="Análisis Químico de Sustancias", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    st.markdown("""
    <style>
    /* Fondo blanco perla y texto azul oscuro */
    .stApp { 
        background-color: #FBFBF9 !important; 
        color: #003366 !important; 
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; 
        text-align: center; 
    }
    [data-testid="stSidebar"] { 
        background-color: #F0F2F5 !important; 
        text-align: center; 
        border-right: 1px solid #D1D5DB !important;
    }
    
    /* Encabezados en azul oscuro fuerte */
    h1, h2, h3, h4, h5, h6 { 
        color: #003366 !important; 
        text-shadow: none; 
        text-align: center !important; 
        width: 100%; 
        display: block; 
        font-weight: 700 !important;
    }
    p, span, div, label { 
        color: #003366; 
        text-align: center; 
    }
    
    ul { list-style-position: inside; text-align: center; padding: 0; color: #003366; }
    li { text-align: center; color: #003366; }
    
    /* Tablas fijas sin movimiento */
    table, [data-testid="stTable"], .stTable { 
        width: 100%; 
        margin: 0 auto; 
        text-align: center; 
        background-color: #E5E7EB; 
        border: 1px solid #D1D5DB; 
        border-radius: 8px; 
        color: #003366; 
        transform: none !important;
        transition: none !important;
    }
    table:hover, [data-testid="stTable"]:hover, .stTable:hover {
        transform: none !important;
        box-shadow: none !important;
    }
    th { 
        background-color: #D1D5DB !important; 
        color: #003366 !important; 
        font-weight: bold; 
        border-bottom: 2px solid #9CA3AF !important; 
        text-align: center !important; 
    }
    td { 
        text-align: center !important; 
        color: #003366 !important; 
        border-bottom: 1px solid #D1D5DB !important; 
    }
    
    img { transition: all 0.3s ease-in-out; border-radius: 8px; margin: 0 auto; display: block; border: 1px solid #D1D5DB; }
    
    /* Cuadros grises */
    .forensic-card { 
        background-color: #E5E7EB; 
        border: 1px solid #D1D5DB; 
        border-radius: 8px; 
        padding: 20px; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0, 51, 102, 0.06); 
        transition: all 0.3s ease-in-out; 
        color: #003366;
    }
    .forensic-card:hover { 
        transform: scale(1.02); 
        box-shadow: 0 8px 16px rgba(0, 51, 102, 0.15); 
        border-color: #003366; 
    }
    
    img:hover { 
        transform: scale(1.02); 
        box-shadow: 0 8px 16px rgba(0, 51, 102, 0.15); 
    }
    
    .nota-card { 
        background-color: #E5E7EB; 
        border: 1px solid #D1D5DB;
        border-left: 5px solid #C0392B; 
        padding: 15px; 
        margin-top: 30px; 
        border-radius: 4px;
        transition: all 0.3s ease-in-out;
        color: #003366;
    }
    .nota-card:hover { 
        transform: scale(1.02); 
        box-shadow: 0 0 15px rgba(192, 57, 43, 0.3); 
        border-color: #C0392B; 
    }
    
    
    .badge-navy {
        display: inline-block;
        background-color: #003366;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin: 4px 4px;
    }
    .badge-teal {
        display: inline-block;
        background-color: #0F766E;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin: 4px 4px;
    }
    .badge-red {
        display: inline-block;
        background-color: #C0392B;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 700;
        margin: 4px 4px;
    }

    .numeric-val { font-family: 'Courier New', Courier, monospace; color: #002244; font-weight: bold; }
    .color-box { height: 50px; width: 100%; border-radius: 6px; margin-bottom: 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.15); border: 1px solid #CBD5E1; }
    .biphasic-tube { height: 70px; width: 100%; border-radius: 6px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #CBD5E1; box-shadow: inset 0 0 10px rgba(0,0,0,0.15); margin-bottom: 12px; }
    .biphasic-top { height: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #fff; text-shadow: 1px 1px 2px #000; border-bottom: 1px solid rgba(255,255,255,0.3); font-weight: bold; }
    .biphasic-bottom { height: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #fff; text-shadow: 1px 1px 2px #000; font-weight: bold; }
    
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center; 
        background-color: #E5E7EB; 
        border-radius: 8px; 
        padding: 4px; 
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] { 
        color: #003366 !important; 
        font-weight: 600; 
        border-radius: 6px; 
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #D1D5DB !important; 
        color: #003366 !important; 
        font-weight: bold; 
    }

    /* Botones */
    .stButton > button {
        background-color: #E5E7EB !important;
        color: #003366 !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton > button:hover {
        background-color: #D1D5DB !important;
        color: #002244 !important;
        border-color: #003366 !important;
        box-shadow: 0 4px 8px rgba(0, 51, 102, 0.15) !important;
        transform: translateY(-1px) !important;
    }

    /* Selectbox y Sliders */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #003366 !important;
        border-color: #CBD5E1 !important;
    }
    div[data-baseweb="select"] span {
        color: #003366 !important;
    }
    label[data-testid="stWidgetLabel"] p {
        color: #003366 !important;
        font-weight: 600 !important;
    }

    .footer { text-align: center; padding: 20px; font-size: 0.85rem; color: #003366; border-top: 1px solid #D1D5DB; margin-top: 40px; width: 100%; }
    .footer b { color: #003366; }
    </style>
    """, unsafe_allow_html=True)

def render_html(html_str):
    clean_lines = [line.strip() for line in html_str.splitlines() if line.strip()]
    st.markdown("\n".join(clean_lines), unsafe_allow_html=True)

def render_analytical_note():
    st.markdown('''
    <div style="background-color: #E5E7EB; border: 1px solid #D1D5DB; border-left: 5px solid #C0392B; padding: 15px; border-radius: 4px; margin-top: 30px; text-align: center; color: #003366;">
        <b>⚠️ NOTA ANALÍTICA:</b> Todo resultado positivo presuntivo tiene que confirmarse por pruebas confirmatorias instrumentales (como GC-MS o ATR-FTIR).
    </div>
    ''', unsafe_allow_html=True)

def normalize_name(name):
    name = name.lower().strip()
    name = ''.join(c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn')
    name = re.sub(r'[^a-z0-9]', '', name)
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

def parse_pkas(pka_str, character):
    if not pka_str or str(pka_str).strip() in ['N/A', '-', '', 'None']:
        return []
    parts = [x.strip() for x in str(pka_str).split(',') if x.strip()]
    vals = []
    for p in parts:
        try: vals.append(float(p))
        except: pass
    
    char_low = str(character).lower()
    if 'xantina' in char_low:
        return [0.6, vals[0]] if vals else [0.6, 10.4]
    is_multi_species = 'anf' in char_low or 'dip' in char_low
    # Regla 6: Si tiene dos valores pero no corresponde a dos especies, usar el primero
    if not is_multi_species and len(vals) > 1:
        return [vals[0]]
    return vals

def calculate_ionization(pka_str, character, ph):
    pkas = parse_pkas(pka_str, character)
    if not pkas:
        return 0.0, 100.0  # Especie no ionizable / neutra
    
    char_low = str(character).strip().lower()
    is_multi = 'anf' in char_low or 'dip' in char_low or 'xantina' in char_low
    
    if is_multi and len(pkas) >= 2:
        pka1, pka2 = sorted(pkas[:2])
        try:
            h = 10.0**(-ph)
            k1 = 10.0**(-pka1)
            k2 = 10.0**(-pka2)
            denom = h**2 + h*k1 + k1*k2
            if denom == 0: return 50.0, 50.0
            alpha_cation = (h**2) / denom
            alpha_neutral = (h*k1) / denom
            alpha_anion = (k1*k2) / denom
            ion = (alpha_cation + alpha_anion) * 100.0
            neutral = alpha_neutral * 100.0
            return max(0.0, min(100.0, ion)), max(0.0, min(100.0, neutral))
        except (OverflowError, ZeroDivisionError):
            return 50.0, 50.0
            
    pka_val = pkas[0]
    if 'ácido' in char_low or 'acido' in char_low:
        try:
            power = pka_val - ph
            if power > 100: ion = 0.0
            elif power < -100: ion = 100.0
            else: ion = 100.0 / (1.0 + 10.0**power)
        except OverflowError:
            ion = 0.0 if (pka_val - ph) > 0 else 100.0
    else: # Base
        try:
            power = ph - pka_val
            if power > 100: ion = 0.0
            elif power < -100: ion = 100.0
            else: ion = 100.0 / (1.0 + 10.0**power)
        except OverflowError:
            ion = 0.0 if (ph - pka_val) > 0 else 100.0
            
    return max(0.0, min(100.0, ion)), max(0.0, min(100.0, 100.0 - ion))

def find_image(sub_name, suffix):
    img_dir = os.path.join(os.path.dirname(__file__), 'Imagenes estructura')
    if not os.path.exists(img_dir): return None
    norm_sub = normalize_name(sub_name)
    norm_suffix = normalize_name(suffix)
    for f in os.listdir(img_dir):
        f_base, _ = os.path.splitext(f)
        if normalize_name(f_base) == f"{norm_sub}{norm_suffix}":
            return os.path.join(img_dir, f)
    for f in os.listdir(img_dir):
        f_norm = normalize_name(f)
        if f_norm.startswith(norm_sub) and norm_suffix in f_norm:
            return os.path.join(img_dir, f)
    return None

def render_image_fixed(img_path, fixed_height=250):
    if not img_path or not os.path.exists(img_path):
        return False
    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(img_path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        html = f'''<div style="height:{fixed_height}px; width:100%; display:flex; align-items:center; justify-content:center; background-color:#E5E7EB; border:1px solid #D1D5DB; border-radius:8px; overflow:hidden; margin:0 auto 10px auto;"><img src="data:{mime};base64,{b64}" style="max-height:100%; max-width:100%; object-fit:contain; border-radius:4px; display:block; margin:auto;" /></div>'''
        st.markdown(html, unsafe_allow_html=True)
        return True
    except Exception:
        return False

def render_placeholder_fixed(msg, fixed_height=250):
    html = f'''<div style="height:{fixed_height}px; width:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; background-color:#E5E7EB; border:1px dashed #9CA3AF; border-radius:8px; margin:0 auto 10px auto; color:#003366;"><div style="font-size:2rem; margin-bottom:5px;">ℹ️</div><div style="font-size:0.9rem; font-weight:600; text-align:center; padding:0 10px;">{msg}</div></div>'''
    st.markdown(html, unsafe_allow_html=True)

def _pick_organic_solvent(solv_acid, solv_basic, char_str):
    for s in [solv_basic, solv_acid]:
        s_str = str(s).strip()
        s_low = s_str.lower()
        if s_str and s_str != "No especificado" and "agua" not in s_low and "inmiscible" not in s_low and "no extra" not in s_low:
            return s_str
    char_low = str(char_str).lower()
    if 'ácido' in char_low or 'acido' in char_low:
        return "Cloroformo / Acetato de etilo"
    return "Cloroformo / Diclorometano"

def get_solvent(info, pka, current_ph):
    char_str = info.get('Carácter', 'Base')
    solv_lt = "No especificado"
    solv_gt = "No especificado"
    for k, v in info.items():
        if '<' in k and 'Disolvente' in k and v:
            solv_lt = v.strip()
        elif '>' in k and 'Disolvente' in k and v:
            solv_gt = v.strip()

    if ('no extra' in solv_lt.lower() or 'inmiscible' in solv_lt.lower()) and ('no extra' in solv_gt.lower() or 'inmiscible' in solv_gt.lower()):
        return "Agua (Fase Acuosa — Insoluble en CHCl3/Éter)"

    ion_pct, _ = calculate_ionization(pka, char_str, current_ph)
    if ion_pct >= 50.0:
        return "Agua (Fase Acuosa)"
    return _pick_organic_solvent(solv_lt, solv_gt, char_str)

def format_test_name(raw_name):
    if not raw_name or str(raw_name).strip() in ['N/A', '', '-']:
        return "Prueba Presuntiva"
    name = str(raw_name).strip()
    name = re.sub(r'\(?\s*#\d+\s*\)?', '', name).strip()
    name = re.sub(r'^Reactivo\s+de\s+', '', name, flags=re.I).strip()
    name = re.sub(r'^Reactivo\s+', '', name, flags=re.I).strip()
    name = re.sub(r'^Prueba\s+de\s+', '', name, flags=re.I).strip()
    return f"Prueba de {name}"

def visual_button(label, bg_style, key, is_biphasic=False, top_bg="", bot_bg="", top_txt="", bot_txt="", custom_html=""):
    if custom_html:
        visual = custom_html
    elif is_biphasic:
        visual = f'<div style="height:50px; width:100%; border-radius:6px; display:flex; flex-direction:column; overflow:hidden; border:1px solid #CBD5E1; margin-bottom:10px;"><div style="height:50%; background:{top_bg}; color:#fff; font-size:0.6rem; text-align:center; line-height:25px; font-weight:bold;">{top_txt}</div><div style="height:50%; background:{bot_bg}; color:#fff; font-size:0.6rem; text-align:center; line-height:25px; font-weight:bold;">{bot_txt}</div></div>'
    else:
        visual = f'<div style="height:50px; width:100%; border-radius:6px; background:{bg_style}; border:1px solid #CBD5E1; margin-bottom:10px;"></div>'
    st.markdown(visual, unsafe_allow_html=True)
    return st.button(label, key=key, use_container_width=True)

def render_presumptive_card(test_name, color_desc, interpretation, bg_style, is_biphasic=False, top_bg="", bot_bg="", top_txt="", bot_txt="", custom_html=""):
    if custom_html:
        visual = custom_html
    elif is_biphasic:
        visual = f'<div class="biphasic-tube"><div class="biphasic-top" style="background: {top_bg};">{top_txt}</div><div class="biphasic-bottom" style="background: {bot_bg};">{bot_txt}</div></div>'
    else:
        visual = f'<div class="color-box" style="background: {bg_style};"></div>'
    st.markdown(f'''<div class="forensic-card">{visual}<div style="font-size: 1.1rem; font-weight: 600; color: #003366; margin-bottom: 5px; text-align:center;">{test_name}</div><div style="font-size: 0.9rem; color: #334155; margin-bottom: 10px; text-align:center;"><b>Tono Visual:</b> {color_desc}</div><div style="font-size: 0.95rem; color: #003366; font-weight: bold; text-align:center;">{interpretation}</div></div>''', unsafe_allow_html=True)

def render_structure(sustancia, info, selected_ph):
    pka, char = info.get('pKa', '7'), info.get('Carácter', 'Base')
    obj_is_ion, _ = calculate_ionization(pka, char, selected_ph)
    suffix = 'ion' if obj_is_ion >= 50.0 else 'base'
    img_path = find_image(sustancia, suffix)
    if img_path:
        render_image_fixed(img_path, fixed_height=240)
    else:
        render_placeholder_fixed("Estructura molecular no disponible", fixed_height=240)
    
    # Subtítulo con nombre y estado libre/ionizado
    estado = "Forma Ionizada" if obj_is_ion >= 50.0 else "Forma No Ionizada"
    estado_color = "#C0392B" if obj_is_ion >= 50.0 else "#003366"
    st.markdown(f'<div style="text-align:center; font-weight:600; color:#003366; font-size:0.95rem; margin-top:2px; margin-bottom:8px;">{sustancia} — <span style="color:{estado_color};">{estado}</span> <span style="font-size:0.85rem; color:#4B5563;">(pH {selected_ph:.1f})</span></div>', unsafe_allow_html=True)

def render_presumptive_info(sustancia, info):
    prueba = info.get('Prueba presuntiva', 'N/A')
    color = info.get('Color característico', 'N/A')
    c_lower = color.lower()
    fallback_color = "#9CA3AF"
    if "naranja" in c_lower: fallback_color = "#E67E22"
    elif "rojo" in c_lower or "roja" in c_lower: fallback_color = "#C0392B"
    elif "azul" in c_lower: fallback_color = "#3498DB"
    elif "violeta" in c_lower or "púrpura" in c_lower or "morado" in c_lower: fallback_color = "#8E44AD"
    elif "verde" in c_lower: fallback_color = "#27AE60"
    elif "amarillo" in c_lower: fallback_color = "#F1C40F"
    elif "rosa" in c_lower: fallback_color = "#F1948A"
    elif "marrón" in c_lower or "cafe" in c_lower: fallback_color = "#8B4513"
    elif "negro" in c_lower: fallback_color = "#1A1A1A"
    
    nombre = sustancia.lower()
    if "cocaína" in nombre or "cocaina" in nombre:
        render_presumptive_card("Prueba de Scott", color, "Cocaína", "", True, "#F5B7B1", "#0047AB", "Acuosa (Rosa)", "Orgánica (Azul)")
    elif "metanfetamina" in nombre or "anfetamina" in nombre:
        render_presumptive_card("Prueba de Marquis", color, "Anfetaminas", "linear-gradient(to right, #D9531E, #C0392B, #5C2C16)")
    elif "mdma" in nombre or "mda" in nombre:
        render_presumptive_card("Prueba de Marquis", color, "Entactógenos", "#1A1A1A")
    elif "lsd" in nombre:
        render_presumptive_card("Prueba de Ehrlich", color, "Indoles", "#8E44AD")
    elif "thc" in nombre:
        render_presumptive_card("Prueba de Duquenois-Levine", color, "Cannabinoides", "", True, "#7F8C8D", "#5B2C6F", "Sup. (Gris)", "Inf. (Púrpura)")
    elif "heroína" in nombre or "heroina" in nombre:
        render_presumptive_card("Prueba de Marquis", color, "Opiáceos", "#5B2C6F")
    else:
        render_presumptive_card(format_test_name(prueba), color, "Respuesta presuntiva", fallback_color)

def render_ir(sustancia, info):
    img_ir = find_image(sustancia, 'Espectro_IR')
    if img_ir:
        render_image_fixed(img_ir, fixed_height=260)
    else:
        render_placeholder_fixed("Espectro IR no disponible", fixed_height=260)
    picos_ir = []
    for i in range(1, 7):
        num = info.get(f"P{i}", "").strip()
        if num and num not in ['N/A', '-']:
            picos_ir.append({
                "Vibración (cm⁻¹)": num
            })
    if picos_ir:
        st.table(picos_ir)

def render_ms(sustancia, info):
    img_ms = find_image(sustancia, 'GS-MS')
    if img_ms:
        render_image_fixed(img_ms, fixed_height=260)
    else:
        render_placeholder_fixed("Espectro GC-MS no disponible", fixed_height=260)
    iones = []
    for i in range(1, 9):
        ion_val = info.get(f"I{i}", "").strip()
        if ion_val and ion_val not in ['N/A', '-']:
            iones.append({
                "Relación m/z": ion_val
            })
    if iones:
        st.table(iones)

def get_separation_intervals(pka_obj_str, char_obj, pka_cut_str, char_cut):
    points = []
    for p in range(0, 141):
        ph = p / 10.0
        io, _ = calculate_ionization(pka_obj_str, char_obj, ph)
        ic, _ = calculate_ionization(pka_cut_str, char_cut, ph)
        if abs(io - ic) >= 90.0:
            kind = 'clean' if io >= 50.0 else 'direct'
            points.append((ph, kind))
    if not points:
        return []
    intervals = []
    start, prev_ph, cur_kind = points[0][0], points[0][0], points[0][1]
    for ph, kind in points[1:]:
        if round(ph - prev_ph, 2) > 0.15 or kind != cur_kind:
            intervals.append((start, prev_ph, cur_kind))
            start, cur_kind = ph, kind
        prev_ph = ph
    intervals.append((start, prev_ph, cur_kind))
    return intervals

def _get_optimal_neutral_ph_action(name, char_str, pkas_list):
    char_low = str(char_str).lower()
    pka_val = pkas_list[0] if pkas_list else 7.0
    if 'xantina' in char_low:
        return 7.0, f"Ajustar la fase acuosa a <b>pH neutro (pH 7.0)</b>, donde <b>{name}</b> se encuentra en su forma no ionizada (&gt;99%)."
    elif 'anf' in char_low or 'dip' in char_low or len(pkas_list) >= 2:
        pi_val = sum(pkas_list) / len(pkas_list) if pkas_list else 7.0
        return pi_val, f"Ajustar cuidadosamente el pH a su punto isoeléctrico de máxima especie no ionizada (aprox. <b>pH {pi_val:.1f}</b>) para liberar al compuesto (<b>{name}</b>)."
    elif 'ácido' in char_low or 'acido' in char_low:
        target_ph = max(1.0, round(pka_val - 2.0, 1))
        return target_ph, f"Acidificar la fase acuosa a <b>pH &le; {target_ph:.1f}</b> para protonar y transformar a su forma no ionizada a <b>{name}</b>."
    else:
        target_ph = min(13.0, round(pka_val + 2.0, 1))
        return target_ph, f"Alcalinizar la fase acuosa a <b>pH &ge; {target_ph:.1f}</b> para desprotonar y liberar a <b>{name}</b> en su forma no ionizada."

def generate_extraction_protocol(name_obj, char_obj, pka_obj_str, solv_obj_acid, solv_obj_basic,
                                 name_cut, char_cut, pka_cut_str, solv_cut_acid, solv_cut_basic):
    if name_obj.strip().lower() == name_cut.strip().lower():
        st.info("ℹ️ Seleccione una sustancia objetivo y un adulterante distintos para calcular el protocolo de extracción.")
        return

    pkas_obj = parse_pkas(pka_obj_str, char_obj)
    pkas_cut = parse_pkas(pka_cut_str, char_cut)
    
    gcms_note_html = """<li style="margin-top:12px; background-color:#FFFFFF; padding:12px; border-radius:6px; border:1px solid #CBD5E1; border-left:4px solid #003366; text-align:left; list-style-type:none;"><b>⚠️ NOTA CRÍTICA PARA GC-MS:</b> Para el análisis por GC-MS, se debe utilizar <b>cloroformo de alta pureza</b> para reconstituir el extracto seco. Es indispensable <b>eliminar con extremo cuidado el agua agregando sulfato de sodio anhidro (Na<sub>2</sub>SO<sub>4</sub>)</b> y <b>filtrar minuciosamente</b> para eliminar todo residuo acuoso, protegiendo así la columna capilar y optimizando la ionización. Asimismo, la muestra reconstituida debe <b>diluirse adecuadamente (ej. proporción 1:50 a 1:100 o concentración ≤ 1 mg/mL)</b> antes de la inyección para evitar la <b>saturación del filamento y del detector de masas (MSD)</b>.</li>"""

    org_solv_obj = _pick_organic_solvent(solv_obj_acid, solv_obj_basic, char_obj)
    org_solv_cut = _pick_organic_solvent(solv_cut_acid, solv_cut_basic, char_cut)

    # Caso especial: Metamizol (sal sulfonato sódica permanentemente hidrofílica e insoluble en CHCl3/Éter)
    obj_is_metamizol = "metamizol" in name_obj.strip().lower()
    cut_is_metamizol = "metamizol" in name_cut.strip().lower()

    if cut_is_metamizol and not obj_is_metamizol:
        target_ph, action_str = _get_optimal_neutral_ph_action(name_obj, char_obj, pkas_obj)
        badge_html = f"""<div style="background-color:#E5E7EB; border:2px solid #003366; border-radius:8px; padding:12px; margin-bottom:15px; text-align:center;">
<div><span style='font-weight:bold; color:#003366;'>🎯 Separación por Retención Hidrofílica Permanente (Metamizol):</span> <span style='font-size:1.15rem; font-weight:bold; color:#002244;'>pH óptimo &approx; {target_ph:.1f}</span> <span style='font-size:0.85rem; color:#4B5563;'>({name_obj} extraído en fase orgánica; Metamizol retenido en agua)</span></div>
</div>"""
        render_html(badge_html)
        protocol_html = f"""<div class="forensic-card">
<h4 style="color: #003366 !important; margin-top:0;">PASO 1: Extracción Selectiva del Analito ({name_obj}) frente a {name_cut}</h4>
<p>{action_str}</p>
<ul>
<li>El adulterante <b>{name_cut}</b> es una sal metanosulfonato sódica (–SO<sub>3</sub><sup>-</sup>Na<sup>+</sup>) permanentemente hidrofílica e insoluble en cloroformo y éter, por lo que permanece retenido en la <b>fase acuosa</b> independientemente del pH.</li>
<li>Añadir solvente orgánico adecuado para extraer el analito: <b>{org_solv_obj}</b>.</li>
<li>Agitar vigorosamente y dejar separar las fases.</li>
<li><span style="color:#003366; font-weight:bold;">ACCIÓN:</span> <b>Separar y conservar la fase orgánica</b> (contiene a <b>{name_obj}</b> purificado). Desechar la fase acuosa (contiene al Metamizol retenido).</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 2: Secado y Aislamiento</h4>
<ul>
<li>Secar la fase orgánica recolectada sobre sulfato de sodio anhidro (Na<sub>2</sub>SO<sub>4</sub>) y filtrar.</li>
<li><b>Llevar a sequedad total</b> la fase orgánica bajo corriente controlada de nitrógeno.</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 3: Reconstitución y Lectura Instrumental</h4>
<ul>
<li><b>Reconstituir el residuo seco</b> para su análisis confirmatorio en <b>FTIR</b> (cristal ATR) o <b>GC-MS</b>.</li>
{gcms_note_html}
</ul>
</div>"""
        render_html(protocol_html)
        return

    if obj_is_metamizol and not cut_is_metamizol:
        target_ph, action_str = _get_optimal_neutral_ph_action(name_cut, char_cut, pkas_cut)
        badge_html = f"""<div style="background-color:#E5E7EB; border:2px solid #003366; border-radius:8px; padding:12px; margin-bottom:15px; text-align:center;">
<div><span style='font-weight:bold; color:#003366;'>🧹 Lavado Orgánico de Adulterante ({name_cut}):</span> <span style='font-size:1.15rem; font-weight:bold; color:#002244;'>pH óptimo &approx; {target_ph:.1f}</span> <span style='font-size:0.85rem; color:#4B5563;'>(Metamizol retenido en fase acuosa; {name_cut} eliminado en fase orgánica)</span></div>
</div>"""
        render_html(badge_html)
        protocol_html = f"""<div class="forensic-card">
<h4 style="color: #003366 !important; margin-top:0;">PASO 1: Eliminación del Adulterante ({name_cut}) hacia Fase Orgánica</h4>
<p>{action_str}</p>
<ul>
<li>A este pH, <b>{name_cut}</b> pasa a su forma no ionizada extraíble, mientras que el <b>{name_obj}</b> permanece cuantitativamente en la <b>fase acuosa</b> por su grupo sulfonato iónico.</li>
<li>Añadir solvente orgánico para arrastrar el corte: <b>{org_solv_cut}</b>.</li>
<li>Agitar vigorosamente y permitir la separación de fases.</li>
<li><span style="color:#C0392B; font-weight:bold;">ACCIÓN:</span> <b>Desechar la fase orgánica</b> (contiene a {name_cut}). <b>Conservar la fase acuosa</b> donde permanece purificado el {name_obj}.</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 2: Recuperación de {name_obj} desde la Fase Acuosa</h4>
<ul>
<li>Neutralizar la fase acuosa purificada (pH 6.5 – 7.0) y evaporar suavemente a sequedad o recristalizar en etanol/metanol absoluto.</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 3: Análisis Confirmatorio</h4>
<ul>
<li>Analizar el residuo sólido purificado directamente en el cristal de diamante ATR por <b>FTIR</b> o mediante inyección metanólica en <b>GC-MS</b> (donde se detecta su producto térmico diagnóstico 4-metilaminoantipirina).</li>
{gcms_note_html}
</ul>
</div>"""
        render_html(protocol_html)
        return

    if not pkas_obj and not pkas_cut:
        protocol_html = f"""<div class="forensic-card">
<h4 style="color:#003366 !important; margin-top:0;">Protocolo de Extracción Directa por Solvente</h4>
<p>Ninguna de las sustancias presenta equilibrios ácido-base relevantes en el intervalo analítico de pH (sustancias neutras). La separación no depende del pH acuoso.</p>
<ul>
<li><b>Extracción diferencial:</b> Evaluar separación por solubilidad diferencial directa usando solvente orgánico afín (ej. {org_solv_obj}).</li>
<li>Separar la fase orgánica y mantener.</li>
<li><b>Llevar a sequedad total</b> la fase orgánica (evaporación suave bajo flujo de nitrógeno).</li>
<li>Reconstituir el extracto para lectura en <b>FTIR / GC-MS</b>.</li>
{gcms_note_html}
</ul>
</div>"""
        render_html(protocol_html)
        return

    intervals = get_separation_intervals(pka_obj_str, char_obj, pka_cut_str, char_cut)
    if not intervals:
        st.error(f"⚠️ **Separación no viable por extracción simple Líquido-Líquido:** Debido a la cercanía de los valores de pKa de **{name_obj}** y **{name_cut}**, las curvas de especiación se solapan y no existe ningún intervalo de pH con diferencia de ionización $\\ge 90\\%$. **Se debe recurrir a separación cromatográfica instrumental como GC-MS (Cromatografía de Gases acoplada a Espectrometría de Masas)**, HPLC o extracción en fase sólida (SPE), ya que la separación en columna capilar de GC-MS permite resolver la mezcla y generar espectros de masas individuales sin requerir purificación L-L previa.")
        return

    clean_intervals = [it for it in intervals if it[2] == 'clean']
    direct_intervals = [it for it in intervals if it[2] == 'direct']
    
    badge_items = []
    if clean_intervals:
        for s, e, _ in clean_intervals:
            badge_items.append(f"<div style='margin-bottom:4px;'><span style='font-weight:bold; color:#003366;'>🧹 Ventana de Lavado de Adulterante:</span> <span style='font-size:1.15rem; font-weight:bold; color:#002244;'>pH {s:.1f} — {e:.1f}</span> <span style='font-size:0.85rem; color:#4B5563;'>(Analito retenido en agua &gt;90%, Adulterante neutro)</span></div>")
    if direct_intervals:
        for s, e, _ in direct_intervals:
            badge_items.append(f"<div><span style='font-weight:bold; color:#003366;'>🎯 Ventana de Extracción de Analito:</span> <span style='font-size:1.15rem; font-weight:bold; color:#002244;'>pH {s:.1f} — {e:.1f}</span> <span style='font-size:0.85rem; color:#4B5563;'>(Analito neutro &gt;90%, Adulterante retenido en agua)</span></div>")
            
    badge_html = f"""<div style="background-color:#E5E7EB; border:2px solid #003366; border-radius:8px; padding:12px; margin-bottom:15px; text-align:center;">
{''.join(badge_items)}
</div>"""
    render_html(badge_html)

    def _practical_midpoint(s, e):
        cs = max(1.0, min(13.0, s))
        ce = max(1.0, min(13.0, e))
        if cs <= ce:
            return round((cs + ce) / 2.0, 1)
        return round((s + e) / 2.0, 1)

    if clean_intervals:
        best_clean = max(clean_intervals, key=lambda it: it[1] - it[0])
        clean_s, clean_e, _ = best_clean
        opt_clean_ph = _practical_midpoint(clean_s, clean_e)
        solv_cut_opt = org_solv_cut
        
        _, step2_action = _get_optimal_neutral_ph_action(name_obj, char_obj, pkas_obj)
        solv_step2 = org_solv_obj

        protocol_html = f"""<div class="forensic-card">
<h4 style="color: #003366 !important; margin-top:0;">PASO 1: Eliminación Selectiva del Adulterante ({name_cut})</h4>
<p>Ajustar el pH de la disolución acuosa a <b>pH {opt_clean_ph:.1f}</b> (dentro de la ventana de lavado).</p>
<ul>
<li>A este pH, el adulterante <b>{name_cut}</b> se encuentra en forma no ionizada (&gt;90%), mientras que el analito objetivo <b>{name_obj}</b> permanece ionizado (&gt;90%) retenido en la fase acuosa.</li>
<li>Añadir solvente orgánico para extraer el corte: <b>{solv_cut_opt}</b>.</li>
<li>Agitar vigorosamente y permitir la completa decantación de fases.</li>
<li><span style="color:#C0392B; font-weight:bold;">ACCIÓN:</span> <b>Desechar la fase orgánica</b> (que arrastra el adulterante eliminado). <b>Conservar únicamente la fase acuosa</b> (donde permanece purificado el analito {name_obj}).</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 2: Extracción y Recuperación del Analito ({name_obj})</h4>
<ul>
<li>{step2_action}</li>
<li>Añadir solvente orgánico fresco y adecuado: <b>{solv_step2}</b>.</li>
<li>Agitar vigorosamente y permitir la decantación.</li>
<li><span style="color:#003366; font-weight:bold;">ACCIÓN:</span> <b>Separar y conservar esta nueva fase orgánica</b>. El analito objetivo ({name_obj}) se encuentra ahora purificado y aislado en ella.</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 3: Secado, Reconstitución y Lectura en FTIR / GC-MS</h4>
<ul>
<li>Filtrar la fase orgánica sobre sulfato de sodio anhidro (Na<sub>2</sub>SO<sub>4</sub>).</li>
<li><b>Llevar a sequedad total</b> la fase orgánica (evaporación suave bajo flujo de nitrógeno).</li>
<li><b>Reconstituir el extracto seco</b> en disolvente apropiado o colocar directamente en cristal de diamante ATR para lectura confirmatoria en <b>FTIR</b> o inyección en <b>GC-MS</b>.</li>
{gcms_note_html}
</ul>
</div>"""
    else:
        best_dir = max(direct_intervals, key=lambda it: it[1] - it[0])
        dir_s, dir_e, _ = best_dir
        opt_dir_ph = _practical_midpoint(dir_s, dir_e)
        solv_step1 = org_solv_obj

        protocol_html = f"""<div class="forensic-card">
<h4 style="color: #003366 !important; margin-top:0;">PASO 1: Extracción Directa del Analito ({name_obj})</h4>
<p>Ajustar el pH de la disolución acuosa a <b>pH {opt_dir_ph:.1f}</b> (dentro de la ventana de extracción).</p>
<ul>
<li>A este pH, el analito <b>{name_obj}</b> se encuentra en su forma no ionizada (&gt;90%), mientras que el adulterante <b>{name_cut}</b> permanece ionizado (&gt;90%) y queda retenido en la fase acuosa.</li>
<li>Añadir solvente orgánico adecuado para el analito: <b>{solv_step1}</b>.</li>
<li>Agitar y dejar separar las fases.</li>
<li><span style="color:#003366; font-weight:bold;">ACCIÓN:</span> <b>Separar y conservar la fase orgánica</b> (que contiene al analito {name_obj} purificado). Desechar la fase acuosa con el adulterante.</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 2: Secado y Aislamiento</h4>
<ul>
<li>Secar la fase orgánica recolectada sobre sulfato de sodio anhidro (Na<sub>2</sub>SO<sub>4</sub>).</li>
<li><b>Llevar a sequedad total</b> la fase orgánica bajo corriente controlada de nitrógeno.</li>
</ul>
<h4 style="color: #003366 !important; margin-top:20px;">PASO 3: Reconstitución y Lectura Instrumental</h4>
<ul>
<li><b>Reconstituir el residuo seco</b> para su análisis instrumental confirmatorio en <b>FTIR</b> (colocar en cristal ATR) o <b>GC-MS</b>.</li>
{gcms_note_html}
</ul>
</div>"""
        
    render_html(protocol_html)

def tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph):
    st.markdown("<h2 style='text-align:center;'>📋 Ficha Comparativa (Sustancia vs Adulterante)</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<h3 style='color:#003366; text-align:center;'>🎯 Analito Objetivo:<br>{selected_sustancia}</h3>", unsafe_allow_html=True)
    with c2: st.markdown(f"<h3 style='color:#C0392B; text-align:center;'>✂️ Adulterante:<br>{selected_adulterante}</h3>", unsafe_allow_html=True)
    
    st.markdown(f"<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Estructura Molecular (pH {selected_ph:.1f})</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_structure(selected_sustancia, data[selected_sustancia], selected_ph)
    with c2: render_structure(selected_adulterante, data[selected_adulterante], selected_ph)
    
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Prueba Presuntiva</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_presumptive_info(selected_sustancia, data[selected_sustancia])
    with c2: render_presumptive_info(selected_adulterante, data[selected_adulterante])
    
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Espectro Infrarrojo (FTIR-ATR)</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_ir(selected_sustancia, data[selected_sustancia])
    with c2: render_ir(selected_adulterante, data[selected_adulterante])
    
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Espectro de Masas (GC-MS)</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: render_ms(selected_sustancia, data[selected_sustancia])
    with c2: render_ms(selected_adulterante, data[selected_adulterante])

    render_analytical_note()

def tab2_arbol_decision():
    st.markdown("<h2 style='text-align:center;'>🌳 Flujo de Descarte Analítico</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔄 Reiniciar Árbol de Decisión", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key.startswith("odv_"): del st.session_state[key]
                
    for key in ["odv_origen", "odv_veg", "odv_duq", "odv_kn", "odv_mayer", "odv_marquis", "odv_scott", "odv_dille", "odv_ehrlich"]:
        if key not in st.session_state: st.session_state[key] = None
        
    st.markdown("<hr style='border-color:#D1D5DB;'><div style='text-align:center;'><h4>Paso 0: ¿Qué tipo de indicio físico es?</h4></div>", unsafe_allow_html=True)
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
                if visual_button("Prueba de Duquenois-Levine", "", "btn_veg_duq", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#6A2C70", top_txt="Gris", bot_txt="Púrpura"): st.session_state.odv_veg = "duq"
            with c3:
                if visual_button("Prueba de KN", "#8B2500", "btn_veg_kn"): st.session_state.odv_veg = "kn"
            
            if st.session_state.odv_veg == "duq":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultado</h4></div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([1, 2, 1])
                with c2: render_presumptive_card("Prueba de Duquenois-Levine", "Púrpura en capa de cloroformo", "[SOSPECHA: Marihuana / Hachís / THC]", "", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#6A2C70", top_txt="Gris Pizarra", bot_txt="Púrpura Violáceo")
            elif st.session_state.odv_veg == "kn":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultado</h4></div>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    if visual_button("Positivo Marihuana", "#8B2500", "btn_kn_m"): st.session_state.odv_kn = "m"
                with c2:
                    if visual_button("Positivo Hachís", "#4A1500", "btn_kn_h"): st.session_state.odv_kn = "h"
                with c3:
                    if visual_button("Negativo", "#9CA3AF", "btn_kn_neg"): st.session_state.odv_kn = "neg"
                if st.session_state.odv_kn == "m": render_presumptive_card("Prueba de KN", "Marrón Rojizo", "[SOSPECHA: Marihuana]", "#8B2500")
                elif st.session_state.odv_kn == "h": render_presumptive_card("Prueba de KN", "Marrón Rojizo Oscuro", "[SOSPECHA: Hachís / Aceite THC]", "#4A1500")
                elif st.session_state.odv_kn == "neg": st.info("Negativo para cannabinoides.")
                
        elif st.session_state.odv_origen == "polvo":
            st.markdown("<div style='text-align:center;'><h4>PASO 1: Prueba de Mayer (Alcaloides)</h4></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
            with c2:
                if visual_button("Positivo (Blanco/Crema)", "#FDFEFE", "btn_may_pos"): st.session_state.odv_mayer = "pos"
            with c3:
                if visual_button("Negativo (Sin Reacción)", "#9CA3AF", "btn_may_neg"): st.session_state.odv_mayer = "neg"
                
            if st.session_state.odv_mayer == "pos":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 2.A: Prueba de Marquis</h4></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    if visual_button("Violeta / Púrpura", "#6B1D5D", "btn_marq_v"): st.session_state.odv_marquis = "v"
                with c2:
                    if visual_button("Naranja → Rojo", "linear-gradient(to right, #FF8C00, #FF0000, #663300)", "btn_marq_o"): st.session_state.odv_marquis = "o"
                with c3:
                    if visual_button("Negro", "#1A1A1A", "btn_marq_b"): st.session_state.odv_marquis = "b"
                with c4:
                    if visual_button("Negativo", "#9CA3AF", "btn_marq_neg"): st.session_state.odv_marquis = "neg"
                    
                if st.session_state.odv_marquis == "v":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultados y Ensayos Complementarios (Opiáceos)</h4></div>", unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1: render_presumptive_card("Prueba de Marquis", "Violeta Oscuro", "[SOSPECHA: OPIÁCEOS]", "#6B1D5D")
                    with cc2: render_presumptive_card("Ensayo Complementario: Prueba de Mecke", "Verde Inmediato", "[ORIENTACIÓN COMPLEMENTARIA: OPIÁCEOS]", "#1E7E34")
                elif st.session_state.odv_marquis == "o":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>Resultados y Ensayos Complementarios (Anfetaminas)</h4></div>", unsafe_allow_html=True)
                    cc1, cc2 = st.columns(2)
                    with cc1: render_presumptive_card("Prueba de Marquis", "Secuencia Naranja → Rojo", "[SOSPECHA: ANFETAMINAS / METANFETAMINA]", "linear-gradient(to right, #FF8C00, #FF0000, #663300)")
                    with cc2: render_presumptive_card("Ensayo Complementario: Prueba de Simon", "Azul Inmediato", "[ORIENTACIÓN COMPLEMENTARIA: METANFETAMINA]", "#0047AB")
                elif st.session_state.odv_marquis == "b":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 2, 1])
                    with cc2: render_presumptive_card("Prueba de Marquis", "Negro Inmediato", "[SOSPECHA: MDMA / MDA]", "#1A1A1A")
                elif st.session_state.odv_marquis == "neg":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 3: Prueba de Scott (Cocaína)</h4></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                    scott_html = "<div style=\"display:flex; justify-content:space-between; margin-bottom:5px;\"><div style=\"width:32%; height:50px; background:#00A8FF; border:1px solid #CBD5E1; border-radius:4px; text-align:center; color:#fff; font-size:0.6rem; line-height:50px; font-weight:bold;\">1. Azul</div><div style=\"width:32%; height:50px; background:#E8A5B8; border:1px solid #CBD5E1; border-radius:4px; text-align:center; color:#fff; font-size:0.6rem; line-height:50px; font-weight:bold;\">2. Rosa</div><div style=\"width:32%; height:50px; background:linear-gradient(to bottom, #E8A5B8 50%, #0047AB 50%); border:1px solid #CBD5E1; border-radius:4px; text-align:center; color:#fff; font-size:0.55rem; line-height:25px; font-weight:bold;\">3. Rosa<br>Azul</div></div>"
                    with c2:
                        if visual_button("Positivo", "", "btn_scott_pos", custom_html=scott_html): st.session_state.odv_scott = "pos"
                    with c3:
                        if visual_button("Negativo", "#9CA3AF", "btn_scott_neg"): st.session_state.odv_scott = "neg"
                        
                    if st.session_state.odv_scott == "pos":
                        st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                        cc1, cc2, cc3 = st.columns([1, 2, 1])
                        with cc2: render_presumptive_card("Prueba de Scott", "Secuencia de 3 Ampolletas", "[SOSPECHA: COCAÍNA (HCl / Base Libre)]", "", custom_html=scott_html)
                    elif st.session_state.odv_scott == "neg":
                        st.warning("Tamizaje presuntivo negativo en ruta de alcaloides. Remitir al laboratorio.")
                        
            elif st.session_state.odv_mayer == "neg":
                st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 2.B: Prueba de Dille-Koppanyi</h4></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                with c2:
                    if visual_button("Positivo (Púrpura)", "#C8A2C8", "btn_dil_pos"): st.session_state.odv_dille = "pos"
                with c3:
                    if visual_button("Negativo (Sin reacción)", "#9CA3AF", "btn_dil_neg"): st.session_state.odv_dille = "neg"
                    
                if st.session_state.odv_dille == "pos":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                    cc1, cc2, cc3 = st.columns([1, 2, 1])
                    with cc2: render_presumptive_card("Prueba de Dille-Koppanyi", "Púrpura Claro", "[SOSPECHA: BARBITÚRICOS]", "#C8A2C8")
                elif st.session_state.odv_dille == "neg":
                    st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div><div style='text-align:center;'><h4>PASO 3.B: Prueba de Ehrlich</h4></div>", unsafe_allow_html=True)
                    c1, c2, c3, c4 = st.columns([1, 2, 2, 1])
                    with c2:
                        if visual_button("Positivo (Púrpura)", "#9B30FF", "btn_ehr_pos"): st.session_state.odv_ehrlich = "pos"
                    with c3:
                        if visual_button("Negativo (Sin reacción)", "#9CA3AF", "btn_ehr_neg"): st.session_state.odv_ehrlich = "neg"
                        
                    if st.session_state.odv_ehrlich == "pos":
                        st.markdown("<div style='text-align:center; font-size:24px; color:#003366;'>⬇</div>", unsafe_allow_html=True)
                        cc1, cc2, cc3 = st.columns([1, 2, 1])
                        with cc2: render_presumptive_card("Prueba de Ehrlich", "Púrpura Violáceo", "[SOSPECHA: LSD / INDOLES]", "#9B30FF")
                    elif st.session_state.odv_ehrlich == "neg":
                        st.warning("Tamizaje botánico y químico negativo. Muestra remitida a laboratorio para análisis instrumental.")
                        
    render_analytical_note()

REAGENT_RESULTS = {
    "mayer": [
        {"test": "Prueba de Mayer", "color_desc": "Precipitado blanco a blanco-crema inmediato", "target": "Alcaloides y Aminas Terciarias (Cocaína, Heroína, Codeína, Ketamina)", "bg": "#F8FAFC"},
        {"test": "Prueba de Mayer", "color_desc": "Solución transparente (Sin precipitado)", "target": "Compuestos Neutros o Ácidos (Barbitúricos, THC - Negativo)", "bg": "#9CA3AF"}
    ],
    "marquis": [
        {"test": "Prueba de Marquis", "color_desc": "Amarillo → Verde brillante / Esmeralda", "target": "2C-B", "bg": "#27AE60"},
        {"test": "Prueba de Marquis", "color_desc": "Negro violáceo inmediato", "target": "MDMA / MDA (Éxtasis)", "bg": "#1A1A1A"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja → Marrón rojizo", "target": "Metanfetamina", "bg": "linear-gradient(to right, #FF8C00, #D35400, #5C2C16)"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja brillante → Marrón", "target": "Anfetamina", "bg": "#E67E22"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja claro / Ocre", "target": "Fentanilo", "bg": "#D4AC0D"},
        {"test": "Prueba de Marquis", "color_desc": "Púrpura / Violeta oscuro", "target": "Opiáceos (Heroína / Morfina)", "bg": "#5B2C6F"},
        {"test": "Prueba de Marquis", "color_desc": "Violeta a Púrpura", "target": "Codeína", "bg": "#4A235A"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja al calentar a 100 °C", "target": "Ibuprofeno / Naproxeno", "bg": "#E67E22"}
    ],
    "mecke": [
        {"test": "Prueba de Mecke", "color_desc": "Verde azulado profundo virando a Negro", "target": "Heroína / Morfina / Codeína", "bg": "#117A65"},
        {"test": "Prueba de Mecke", "color_desc": "Verde oscuro a Verde azulado", "target": "MDMA / MDA", "bg": "#145A32"},
        {"test": "Prueba de Mecke", "color_desc": "Marrón a Pardo rojizo", "target": "Mescalina / Fenetilaminas", "bg": "#B9770E"}
    ],
    "simon": [
        {"test": "Prueba de Simon", "color_desc": "Azul cobalto intenso inmediato", "target": "Metanfetamina / Efedrina (Aminas Secundarias)", "bg": "#0047AB"},
        {"test": "Prueba de Simon", "color_desc": "Azul cobalto intenso inmediato", "target": "MDMA (Amina Secundaria)", "bg": "#0047AB"},
        {"test": "Prueba de Simon", "color_desc": "Sin reacción / Incoloro", "target": "Anfetamina / MDA (Aminas Primarias - Negativo)", "bg": "#D1D5DB"}
    ],
    "scott": [
        {"test": "Prueba de Scott", "color_desc": "Bifásico: Rosa superior (acuosa) / Azul inferior (cloroformo)", "target": "Cocaína (HCl / Base Libre)", "bg": "", "is_biphasic": True, "top_bg": "#F5B7B1", "bot_bg": "#0047AB", "top_txt": "Fase Acuosa (Rosa)", "bot_txt": "Fase Cloroformo (Azul)"}
    ],
    "duquenois": [
        {"test": "Prueba de Duquenois-Levine", "color_desc": "Bifásico: Capa superior gris / Capa inferior púrpura violácea", "target": "Cannabinoides (THC / Marihuana / Hachís)", "bg": "", "is_biphasic": True, "top_bg": "#7F8C8D", "bot_bg": "#6A2C70", "top_txt": "Fase Acuosa (Gris)", "bot_txt": "Fase Cloroformo (Púrpura)"}
    ],
    "kn": [
        {"test": "Prueba de KN", "color_desc": "Marrón rojizo", "target": "Marihuana (Material vegetal)", "bg": "#8B2500"},
        {"test": "Prueba de KN", "color_desc": "Marrón rojizo oscuro / Vino", "target": "Hachís / Aceite de Cannabis", "bg": "#4A1500"}
    ],
    "ehrlich": [
        {"test": "Prueba de Ehrlich", "color_desc": "Púrpura violáceo intenso", "target": "LSD / Derivados indólicos / Psilocibina", "bg": "#8E44AD"}
    ],
    "dille": [
        {"test": "Prueba de Dille-Koppanyi", "color_desc": "Púrpura claro / Violeta", "target": "Barbitúricos (Fenobarbital)", "bg": "#C8A2C8"}
    ],
    "mandelin": [
        {"test": "Prueba de Mandelin", "color_desc": "Verde → Azul oscuro / Negro violáceo", "target": "MDA / MDMA", "bg": "#1B4F72"},
        {"test": "Prueba de Mandelin", "color_desc": "Verde oliva a Verde oscuro", "target": "Metanfetamina / Anfetamina", "bg": "#2E4F28"},
        {"test": "Prueba de Mandelin", "color_desc": "Azul grisáceo a Violeta oscuro", "target": "Opiáceos (Morfina / Heroína / Codeína)", "bg": "#2E4053"}
    ],
    "forrest": [
        {"test": "Prueba de Forrest", "color_desc": "Azul-verde", "target": "Ketamina / Imipramina", "bg": "#117A65"},
        {"test": "Yodoplatinato Acidificado", "color_desc": "Precipitado púrpura-rojizo a azul-grisáceo", "target": "Ketamina y Alcaloides Terciarios", "bg": "#5B2C6F"}
    ],
    "formaldehído": [
        {"test": "Formaldehído-Ácido Sulfúrico", "color_desc": "Naranja brillante a 100 °C", "target": "Clonazepam / Diazepam / Flunitrazepam", "bg": "#E67E22"},
        {"test": "Formaldehído-Ácido Sulfúrico", "color_desc": "Incoloro / Sin reacción a 100 °C", "target": "Alprazolam (Negativo)", "bg": "#D1D5DB"}
    ],
    "liebermann": [
        {"test": "Prueba de Liebermann", "color_desc": "Violeta a Púrpura", "target": "Fenacetina / Paracetamol", "bg": "#6C3483"},
        {"test": "Prueba de Liebermann", "color_desc": "Rojo-Naranja brillante", "target": "Efedrina / Levamisol", "bg": "#D35400"},
        {"test": "Prueba de Liebermann", "color_desc": "Negro / Marrón oscuro", "target": "Heroína / Morfina / Naproxeno", "bg": "#1C2833"},
        {"test": "Prueba de Liebermann", "color_desc": "Amarillo tenue (Cocaína HCl)", "target": "Cocaína", "bg": "#F9E79F"}
    ],
    "férrico": [
        {"test": "Prueba de Cloruro Férrico", "color_desc": "Violeta púrpura intenso", "target": "Metamizol / Salicilatos (tras hidrólisis)", "bg": "#512E5F"}
    ],
    "ferrico": [
        {"test": "Prueba de Cloruro Férrico", "color_desc": "Violeta púrpura intenso", "target": "Metamizol / Salicilatos (tras hidrólisis)", "bg": "#512E5F"}
    ],
    "mcnally": [
        {"test": "Prueba de McNally", "color_desc": "Rojo cereza tras hidrólisis y calentamiento a 100 °C", "target": "Ácido Acetilsalicílico (Aspirina) / Salicilatos", "bg": "#922B21"}
    ],
    "amálico": [
        {"test": "Prueba de Murexida", "color_desc": "Púrpura rojizo brillante con vapor de amonio", "target": "Xantinas (Cafeína)", "bg": "#7D3C98"}
    ],
    "murexida": [
        {"test": "Prueba de Murexida", "color_desc": "Púrpura rojizo brillante con vapor de amonio", "target": "Xantinas (Cafeína)", "bg": "#7D3C98"}
    ],
    "zimmerman": [
        {"test": "Prueba de Zimmerman", "color_desc": "Rosa rojizo / Púrpura rojizo", "target": "Benzodiazepinas (Diazepam)", "bg": "#C0392B"}
    ],
    "cobalto": [
        {"test": "Prueba de Nitrato de Cobalto (1%)", "color_desc": "Rosa a Violeta", "target": "GHB (Gamma-hidroxibutirato)", "bg": "#9B59B6"}
    ]
}

def tab3_reactivos():
    st.markdown("<h2 style='text-align:center;'>🧪 Preparación de Reactivos y Pruebas</h2>", unsafe_allow_html=True)
    tests = load_pruebas_csv()
    if not tests:
        st.error("Archivo Pruebas Presuntivas.csv no encontrado.")
        return
        
    st.markdown("<div style='text-align:center; color:#334155; margin-bottom:15px;'>Seleccione una prueba analítica estandarizada:</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        test_names = list(tests.keys())
        selected = st.selectbox("Prueba", test_names, label_visibility="collapsed")
        
    if selected:
        info = tests[selected]
        
        st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Reactivos Necesarios</h3>", unsafe_allow_html=True)
        reactivos_raw = info['Reactivos'].split('\n')
        react_list = []
        for r in reactivos_raw:
            parts = r.split(':', 1)
            if len(parts) == 2:
                react_list.append({"Reactivo": parts[0].strip(), "Preparación / Cantidad": parts[1].strip()})
            else:
                react_list.append({"Reactivo": r.strip(), "Preparación / Cantidad": "Directo / Sin preparación previa"})
        if react_list: st.table(react_list)
        
        st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Procedimiento Analítico</h3>", unsafe_allow_html=True)
        proc_raw = [p.strip() for p in info['Procedimiento'].split('\n') if p.strip()]
        
        flow_html = '<div style="display:flex; justify-content:center; align-items:stretch; flex-wrap:wrap; gap:16px; margin:20px 0;">'
        for idx, p in enumerate(proc_raw):
            clean_text = re.sub(r'^\d+\.\s*', '', p)
            flow_html += f'''
            <div class="forensic-card" style="width:230px; padding:15px; margin:0; display:flex; flex-direction:column; align-items:center; justify-content:center;">
                <div style="width:36px; height:36px; border-radius:50%; background:#003366; color:#ffffff; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-bottom:10px; font-size:1rem;">{idx+1}</div>
                <div style="font-size:0.85rem; text-align:center; color:#003366; line-height:1.4;">{clean_text}</div>
            </div>
            '''
            if idx < len(proc_raw) - 1:
                flow_html += '<div style="font-size:2rem; color:#003366; display:flex; align-items:center; justify-content:center;">➡️</div>'
        flow_html += '</div>'
        st.markdown(flow_html, unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Resultados Esperados con Color</h3>", unsafe_allow_html=True)
        matched_results = []
        sel_lower = selected.lower()
        for k, res_list in REAGENT_RESULTS.items():
            if k in sel_lower:
                matched_results = res_list
                break
                
        if matched_results:
            n_cols = min(len(matched_results), 4)
            cols = st.columns(n_cols)
            for idx, item in enumerate(matched_results):
                with cols[idx % n_cols]:
                    render_presumptive_card(
                        item['test'],
                        item['color_desc'],
                        f"Positivo: {item['target']}",
                        item.get('bg', '#9CA3AF'),
                        is_biphasic=item.get('is_biphasic', False),
                        top_bg=item.get('top_bg', ''),
                        bot_bg=item.get('bot_bg', ''),
                        top_txt=item.get('top_txt', ''),
                        bot_txt=item.get('bot_txt', '')
                    )
        else:
            st.info("Información de viraje específico en proceso de catalogación experimental.")
        
        st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Interferencias y Limitaciones</h3>", unsafe_allow_html=True)
        st.table([
            {"Tipo de Falso": "Falso Positivo", "Descripción / Sustancias Interferentes": info.get('Falsos Positivos', 'No reportado')},
            {"Tipo de Falso": "Falso Negativo", "Descripción / Sustancias Interferentes": info.get('Falsos Negativos', 'No reportado')}
        ])

    render_analytical_note()

def tab4_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph):
    st.markdown("<h2 style='text-align:center;'>⚗️ Separación L-L y Purificación de Muestras</h2>", unsafe_allow_html=True)
    info_obj, info_cut = data[selected_sustancia], data[selected_adulterante]
    pka_obj, char_obj = info_obj.get('pKa', '7'), info_obj.get('Carácter', 'Base')
    pka_cut, char_cut = info_cut.get('pKa', '7'), info_cut.get('Carácter', 'Base')
    
    i_obj_curr, n_obj_curr = calculate_ionization(pka_obj, char_obj, selected_ph)
    i_cut_curr, n_cut_curr = calculate_ionization(pka_cut, char_cut, selected_ph)
    
    solv_obj = get_solvent(info_obj, pka_obj, selected_ph)
    solv_cut = get_solvent(info_cut, pka_cut, selected_ph)
    
    if "metamizol" in selected_sustancia.lower() or "metamizol" in selected_adulterante.lower():
        st.info("ℹ️ **Nota Pericial de Partición (Metamizol / Dipirona):** Aunque el anillo pirazolónico presenta un $pK_a = 1.84$, el Metamizol es una **sal metanosulfonato sódica ($\\text{-SO}_3^-\\text{Na}^+$)** permanentemente iónica e hidrofílica (soluble 1 en 1.5 de agua, prácticamente insoluble en cloroformo y éter). Por tanto, permanece retenido en la **Fase Acuosa** en todo el intervalo de pH, permitiendo extraer selectivamente alcaloides lipofílicos hacia la fase orgánica.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #003366;"><h4 style="color: #003366 !important; margin-top:0;">🎯 Analito Objetivo: {selected_sustancia}</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {char_obj}</p><p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_obj}</span></p><p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_obj}</p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Especie Ionizada (Fase Acuosa):</b> <span class="numeric-val">{i_obj_curr:.2f}%</span></p><p style="margin-bottom:0;"><b>% Especie No Ionizada (Fase Orgánica):</b> <span class="numeric-val">{n_obj_curr:.2f}%</span></p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #C0392B;"><h4 style="color: #C0392B !important; margin-top:0;">✂️ Adulterante: {selected_adulterante}</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {char_cut}</p><p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_cut}</span></p><p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_cut}</p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Especie Ionizada (Fase Acuosa):</b> <span class="numeric-val">{i_cut_curr:.2f}%</span></p><p style="margin-bottom:0;"><b>% Especie No Ionizada (Fase Orgánica):</b> <span class="numeric-val">{n_cut_curr:.2f}%</span></p></div>', unsafe_allow_html=True)
        
    chart_data = []
    for ph_val in [x/10.0 for x in range(0, 141, 2)]:
        i_o, n_o = calculate_ionization(pka_obj, char_obj, ph_val)
        i_c, n_c = calculate_ionization(pka_cut, char_cut, ph_val)
        chart_data.extend([
            {"pH": ph_val, "% Especie": i_o, "Sustancia": "Objetivo (Ionizada - Agua)", "Categoría": "Objetivo"}, 
            {"pH": ph_val, "% Especie": n_o, "Sustancia": "Objetivo (No Ionizada - Orgánico)", "Categoría": "Objetivo"}, 
            {"pH": ph_val, "% Especie": i_c, "Sustancia": "Corte (Ionizada - Agua)", "Categoría": "Adulterante"}, 
            {"pH": ph_val, "% Especie": n_c, "Sustancia": "Corte (No Ionizada - Orgánico)", "Categoría": "Adulterante"}
        ])
        
    point_data = [
        {"pH": selected_ph, "% Especie": i_obj_curr, "Sustancia": "Objetivo (Ionizada - Agua)", "Categoría": "Objetivo"}, 
        {"pH": selected_ph, "% Especie": n_obj_curr, "Sustancia": "Objetivo (No Ionizada - Orgánico)", "Categoría": "Objetivo"}, 
        {"pH": selected_ph, "% Especie": i_cut_curr, "Sustancia": "Corte (Ionizada - Agua)", "Categoría": "Adulterante"}, 
        {"pH": selected_ph, "% Especie": n_cut_curr, "Sustancia": "Corte (No Ionizada - Orgánico)", "Categoría": "Adulterante"}
    ]
    
    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo de la Especie", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=['Objetivo (Ionizada - Agua)', 'Objetivo (No Ionizada - Orgánico)', 'Corte (Ionizada - Agua)', 'Corte (No Ionizada - Orgánico)'], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=alt.Legend(title="Especies", titleColor="#003366", labelColor="#003366", orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == 'Adulterante', alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#fff", strokeWidth=2).encode(
        x='pH:Q', y='% Especie:Q', 
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=['Objetivo (Ionizada - Agua)', 'Objetivo (No Ionizada - Orgánico)', 'Corte (Ionizada - Agua)', 'Corte (No Ionizada - Orgánico)'], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=None), 
        tooltip=['pH:Q', '% Especie:Q', 'Sustancia:N']
    )
    rule = alt.Chart(alt.Data(values=[{"pH": selected_ph}])).mark_rule(strokeDash=[3, 3], color='#003366', strokeWidth=1).encode(x='pH:Q')
    
    intervals = get_separation_intervals(pka_obj, char_obj, pka_cut, char_cut)
    if intervals:
        shade_data = [{"start": s, "end": e} for s, e, _ in intervals]
        shade = alt.Chart(alt.Data(values=shade_data)).mark_rect(opacity=0.15, color='#003366').encode(x='start:Q', x2='end:Q')
        layered_chart = (shade + base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
    else:
        layered_chart = (base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
    st.altair_chart(layered_chart, use_container_width=True)

    st.markdown("<h3 style='text-align:center;'>Protocolo Automatizado de Extracción Diferencial</h3>", unsafe_allow_html=True)
    pkas_obj = parse_pkas(pka_obj, char_obj)
    pkas_cut = parse_pkas(pka_cut, char_cut)
    pka_o = pkas_obj[0] if pkas_obj else 7.0
    pka_c = pkas_cut[0] if pkas_cut else 7.0
    
    solv_obj_acid = get_solvent(info_obj, pka_obj, pka_o - 2.0)
    solv_obj_basic = get_solvent(info_obj, pka_obj, pka_o + 2.0)
    solv_cut_acid = get_solvent(info_cut, pka_cut, pka_c - 2.0)
    solv_cut_basic = get_solvent(info_cut, pka_cut, pka_c + 2.0)
    
    generate_extraction_protocol(selected_sustancia, char_obj, pka_obj, solv_obj_acid, solv_obj_basic,
                                 selected_adulterante, char_cut, pka_cut, solv_cut_acid, solv_cut_basic)

def validate_manual_pka(pka_input, char_input, label):
    raw = str(pka_input).strip()
    if not raw:
        return False, [], f"⚠️ Ingrese al menos un valor de pKa (o pH de referencia) para {label}."
    
    # Validar delimitadores incorrectos
    if ';' in raw or '-' in raw or '/' in raw:
        return False, [], f"⚠️ Formato incorrecto para {label}: Separe los valores en el formato adecuado '(ph1, ph2)' o '(pKa1, pKa2)' con una coma y espacio obligatorio (ejemplo: '1.5, 10.5')."
        
    parts = [p.strip() for p in raw.split(',') if p.strip()]
    if ',' in raw and len(parts) > 1 and ', ' not in raw:
        return False, [], f"⚠️ Formato inadecuado para {label}: Debe incluir un espacio obligatorio después de la coma en el formato adecuado '(ph1, ph2)' o '(pKa1, pKa2)' (ejemplo: '1.5, 10.5')."
        
    pkas = []
    for p in parts:
        try:
            val = float(p)
            if val < 0.0 or val > 14.0:
                return False, [], f"⚠️ No se ingresaron valores de pH / pKa válidos para {label}: El valor ({val}) debe encontrarse dentro de la escala analítica de 0.0 a 14.0."
            pkas.append(val)
        except ValueError:
            return False, [], f"⚠️ No se ingresaron valores válidos para {label}: El valor '{p}' no es numérico. Ingrese valores numéricos en el formato adecuado '(ph1, ph2)' o '(pKa1, pKa2)' (ejemplo: '8.6' o '1.5, 10.5')."
            
    char_low = char_input.lower()
    is_diprotic = 'anf' in char_low or 'dipr' in char_low
    
    if is_diprotic and len(pkas) < 2:
        return False, [], f"⚠️ Ha seleccionado el carácter 'Anfótero (2 pKa)' para {label}: Debe ingresar dos equilibrios en el formato adecuado '(ph1, ph2)' o '(pKa1, pKa2)' con coma y espacio (ejemplo: '1.5, 10.5')."
        
    if len(pkas) >= 2 and not is_diprotic:
        return False, [], f"⚠️ Ha ingresado dos valores para {label}: Para modelar ambos equilibrios en la curva de especiación, seleccione el carácter 'Anfótero (2 pKa)' en el menú desplegable."

    if len(pkas) >= 2:
        p1, p2 = pkas[0], pkas[1]
        if p1 >= p2:
            return False, [], f"⚠️ En {label}, el primer valor ({p1}) debe ser estrictamente menor que el segundo ({p2}) en el formato adecuado '(ph1, ph2)' o '(pKa1, pKa2)'."
        if abs(p2 - p1) < 1.0:
            return False, [], f"⚠️ No es posible simular con la ecuación para {label} por tener valores de pKa / pH muy juntos ({p1} y {p2}, diferencia < 1.0). Cuando los equilibrios distan menos de 1.0 unidad de pH, las especies se interfieren y no es viable una resolución matemática secuencial."
            
    return True, pkas, None

def tab5_simulador_manual():
    st.markdown("<h2 style='text-align:center;'>🔬 Simulador Manual de Extracción L-L</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:#334155; margin-bottom:20px;'>Configure manualmente los parámetros fisicoquímicos para modelar curvas de especiación personalizadas, detectar ventanas de separación y generar protocolos de extracción.</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='forensic-card' style='border-left: 4px solid #003366;'><h4 style='color:#003366 !important; margin-top:0;'>🎯 Parámetros del Analito Objetivo</h4>", unsafe_allow_html=True)
        man_name_obj = st.text_input("Nombre del Analito Objetivo", value="Cocaína", key="m_n_obj")
        man_char_obj = st.selectbox("Carácter Químico", ["Base débil", "Ácido débil", "Anfótero (2 pKa)"], index=0, key="m_c_obj")
        man_pka_obj = st.text_input("pKa (uno o dos valores, ej: 8.6 o 1.5, 10.5)", value="8.6", key="m_p_obj")
        man_solv_obj_acid = st.text_input("Disolvente a pH < pKa (Medio Ácido)", value="Agua (Fase Acuosa)", key="m_s_oa")
        man_solv_obj_base = st.text_input("Disolvente a pH > pKa (Medio Básico)", value="Cloroformo / Diclorometano", key="m_s_ob")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='forensic-card' style='border-left: 4px solid #C0392B;'><h4 style='color:#C0392B !important; margin-top:0;'>✂️ Parámetros del Adulterante (Corte)</h4>", unsafe_allow_html=True)
        man_name_cut = st.text_input("Nombre del Adulterante", value="Fenacetina", key="m_n_cut")
        man_char_cut = st.selectbox("Carácter Químico", ["Base débil", "Ácido débil", "Anfótero (2 pKa)"], index=0, key="m_c_cut")
        man_pka_cut = st.text_input("pKa (uno o dos valores, ej: 2.2 o 4.4, 5.2)", value="2.2", key="m_p_cut")
        man_solv_cut_acid = st.text_input("Disolvente a pH < pKa (Medio Ácido)", value="Agua (Fase Acuosa)", key="m_s_ca")
        man_solv_cut_base = st.text_input("Disolvente a pH > pKa (Medio Básico)", value="Cloroformo / Éter etílico", key="m_s_cb")
        st.markdown("</div>", unsafe_allow_html=True)
        
    man_ph = st.slider("🧪 pH de Simulación Actual", 0.0, 14.0, 7.0, 0.1, key="m_ph_slider")
    
    valid_obj, pkas_val_obj, err_obj = validate_manual_pka(man_pka_obj, man_char_obj, f"Analito Objetivo ({man_name_obj})")
    valid_cut, pkas_val_cut, err_cut = validate_manual_pka(man_pka_cut, man_char_cut, f"Adulterante ({man_name_cut})")
    
    if not valid_obj:
        st.warning(err_obj)
        return
    if not valid_cut:
        st.warning(err_cut)
        return

    i_obj, n_obj = calculate_ionization(man_pka_obj, man_char_obj, man_ph)
    i_cut, n_cut = calculate_ionization(man_pka_cut, man_char_cut, man_ph)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #003366;"><h4 style="color: #003366 !important; margin-top:0;">🎯 {man_name_obj} (pH {man_ph:.1f})</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {man_char_obj} | <b>pKa:</b> <span class="numeric-val">{man_pka_obj}</span></p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Especie Ionizada (Fase Acuosa):</b> <span class="numeric-val">{i_obj:.2f}%</span></p><p style="margin-bottom:0;"><b>% Especie No Ionizada (Fase Orgánica):</b> <span class="numeric-val">{n_obj:.2f}%</span></p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #C0392B;"><h4 style="color: #C0392B !important; margin-top:0;">✂️ {man_name_cut} (pH {man_ph:.1f})</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {man_char_cut} | <b>pKa:</b> <span class="numeric-val">{man_pka_cut}</span></p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Especie Ionizada (Fase Acuosa):</b> <span class="numeric-val">{i_cut:.2f}%</span></p><p style="margin-bottom:0;"><b>% Especie No Ionizada (Fase Orgánica):</b> <span class="numeric-val">{n_cut:.2f}%</span></p></div>', unsafe_allow_html=True)

    chart_data = []
    for p in range(0, 141, 2):
        ph_val = p / 10.0
        io, no = calculate_ionization(man_pka_obj, man_char_obj, ph_val)
        ic, nc = calculate_ionization(man_pka_cut, man_char_cut, ph_val)
        chart_data.extend([
            {"pH": ph_val, "% Especie": io, "Sustancia": f"{man_name_obj} (Ionizada - Agua)", "Categoría": "Objetivo"},
            {"pH": ph_val, "% Especie": no, "Sustancia": f"{man_name_obj} (No Ionizada - Orgánico)", "Categoría": "Objetivo"},
            {"pH": ph_val, "% Especie": ic, "Sustancia": f"{man_name_cut} (Ionizada - Agua)", "Categoría": "Adulterante"},
            {"pH": ph_val, "% Especie": nc, "Sustancia": f"{man_name_cut} (No Ionizada - Orgánico)", "Categoría": "Adulterante"}
        ])
        
    point_data = [
        {"pH": man_ph, "% Especie": i_obj, "Sustancia": f"{man_name_obj} (Ionizada - Agua)", "Categoría": "Objetivo"},
        {"pH": man_ph, "% Especie": n_obj, "Sustancia": f"{man_name_obj} (No Ionizada - Orgánico)", "Categoría": "Objetivo"},
        {"pH": man_ph, "% Especie": i_cut, "Sustancia": f"{man_name_cut} (Ionizada - Agua)", "Categoría": "Adulterante"},
        {"pH": man_ph, "% Especie": n_cut, "Sustancia": f"{man_name_cut} (No Ionizada - Orgánico)", "Categoría": "Adulterante"}
    ]
    
    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo de la Especie", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=[f"{man_name_obj} (Ionizada - Agua)", f"{man_name_obj} (No Ionizada - Orgánico)", f"{man_name_cut} (Ionizada - Agua)", f"{man_name_cut} (No Ionizada - Orgánico)"], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=alt.Legend(title="Especies", titleColor="#003366", labelColor="#003366", orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == 'Adulterante', alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#fff", strokeWidth=2).encode(
        x='pH:Q', y='% Especie:Q',
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=[f"{man_name_obj} (Ionizada - Agua)", f"{man_name_obj} (No Ionizada - Orgánico)", f"{man_name_cut} (Ionizada - Agua)", f"{man_name_cut} (No Ionizada - Orgánico)"], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=None),
        tooltip=['pH:Q', '% Especie:Q', 'Sustancia:N']
    )
    rule = alt.Chart(alt.Data(values=[{"pH": man_ph}])).mark_rule(strokeDash=[3, 3], color='#003366', strokeWidth=1).encode(x='pH:Q')
    
    intervals = get_separation_intervals(man_pka_obj, man_char_obj, man_pka_cut, man_char_cut)
    if intervals:
        shade_data = [{"start": s, "end": e} for s, e, _ in intervals]
        shade = alt.Chart(alt.Data(values=shade_data)).mark_rect(opacity=0.15, color='#003366').encode(x='start:Q', x2='end:Q')
        layered_chart = (shade + base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
    else:
        layered_chart = (base_chart + rule + point_chart).properties(background='transparent').configure_view(strokeWidth=0)
        
    st.altair_chart(layered_chart, use_container_width=True)
    
    st.markdown("<h3 style='text-align:center;'>Protocolo Automatizado de Extracción Diferencial</h3>", unsafe_allow_html=True)
    generate_extraction_protocol(man_name_obj, man_char_obj, man_pka_obj, man_solv_obj_acid, man_solv_obj_base,
                                 man_name_cut, man_char_cut, man_pka_cut, man_solv_cut_acid, man_solv_cut_base)

def render_step_flow(steps):
    flow_html = '<div style="display:flex; justify-content:center; align-items:stretch; flex-wrap:wrap; gap:14px; margin:20px 0;">'
    for idx, step in enumerate(steps):
        title_html = f'<div style="font-weight:700; font-size:0.9rem; color:#002244; margin-bottom:6px;">{step["title"]}</div>' if step.get("title") else ""
        conc_badge = f'<div style="margin-top:8px; padding:4px 8px; background-color:#D1D5DB; border-radius:6px; font-family:\'Courier New\', monospace; font-size:0.8rem; font-weight:bold; color:#002244;">{step["conc"]}</div>' if step.get("conc") else ""
        flow_html += f'''
        <div class="forensic-card" style="width:235px; padding:15px; margin:0; display:flex; flex-direction:column; align-items:center; justify-content:space-between;">
            <div style="width:36px; height:36px; border-radius:50%; background:#003366; color:#ffffff; display:flex; align-items:center; justify-content:center; font-weight:bold; margin-bottom:10px; font-size:1rem;">{idx+1}</div>
            {title_html}
            <div style="font-size:0.84rem; text-align:center; color:#003366; line-height:1.4;">{step["desc"]}</div>
            {conc_badge}
        </div>
        '''
        if idx < len(steps) - 1:
            flow_html += '<div style="font-size:1.8rem; color:#003366; display:flex; align-items:center; justify-content:center;">➡️</div>'
    flow_html += '</div>'
    render_html(flow_html)



def render_analytical_note_tox():
    st.markdown('''
    <div class="nota-card">
        <b>⚠️ NOTA ANALÍTICA:</b> Etiquetar cada solución con identificación, concentración, matriz, lote, fecha de preparación y responsable de su elaboración. Tapar con Parafilm y conservar de <b>4 °C a 8 °C</b> hasta su uso.
    </div>
    ''', unsafe_allow_html=True)

SOLVENT_PROPERTIES = {
    "1-Propanol": {
        "nombre": "1-Propanol",
        "densidad_g_ml": 0.804
    },
    "Etanol": {
        "nombre": "Etanol",
        "densidad_g_ml": 0.789
    },
    "Metanol": {
        "nombre": "Metanol",
        "densidad_g_ml": 0.791
    },
    "Isopropanol": {
        "nombre": "Isopropanol",
        "densidad_g_ml": 0.786
    },
    "Acetona": {
        "nombre": "Acetona",
        "densidad_g_ml": 0.784
    },
    "Acetaldehído": {
        "nombre": "Acetaldehído",
        "densidad_g_ml": 0.788
    },
    "Tolueno": {
        "nombre": "Tolueno",
        "densidad_g_ml": 0.867
    }
}


# ==============================================================================
# PESTAÑA 1: PREPARACIÓN DE REACTIVOS
# ==============================================================================

def tab_cgms_preparacion():
    st.markdown("<h2 style='text-align:center;'>🧪 Preparación de Reactivos</h2>", unsafe_allow_html=True)

    opciones_menu = [
        "Estandar interno - 1-propanol 100 mg/dl",
        "Control Bajo (CB) — Etanol 50 mg/dL",
        "Control Medio (CM) — Etanol 100 mg/dL",
        "Control Alto (CA) — Etanol 400 mg/dL"
    ]

    col_sel, col_pur, col_vf = st.columns([2, 1, 1])
    with col_sel:
        seleccion = st.selectbox("Seleccione el reactivo a preparar:", opciones_menu, index=0)
    with col_pur:
        pureza_usuario = st.number_input(
            "Pureza del reactivo (%):",
            min_value=1.0,
            max_value=100.0,
            value=100.0,
            step=0.1,
            format="%.2f",
            key="tab1_pureza"
        )
    with col_vf:
        es_ei_sel = "Estandar interno" in seleccion or "Estándar Interno" in seleccion
        default_vf = 50.0 if es_ei_sel else 100.0
        v_final_ml = st.number_input(
            "Volumen matraz final (mL):",
            min_value=5.0,
            max_value=5000.0,
            value=default_vf,
            step=10.0,
            format="%.0f",
            key=f"tab1_vf_{'ei' if es_ei_sel else 'ctrl'}"
        )

    # Sección para poner cantidad de Estándar Interno y Muestra o Control (relación en vial)
    st.markdown("<hr style='border-color:#D1D5DB;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin-top:0; margin-bottom:10px;'>⚖️ Relación de Volúmenes en Vial (Estándar Interno y Muestra o Control)</h4>", unsafe_allow_html=True)
    c_v1, c_v2, c_v3 = st.columns(3)
    with c_v1:
        vol_muestra_ul = st.number_input(
            "Cantidad de Muestra o Control (µL):",
            min_value=1.0,
            max_value=5000.0,
            value=200.0,
            step=10.0,
            format="%.0f",
            key="tab1_v_muestra"
        )
    with c_v2:
        vol_ei_ul = st.number_input(
            "Cantidad de Estándar Interno (µL):",
            min_value=1.0,
            max_value=5000.0,
            value=1800.0,
            step=50.0,
            format="%.0f",
            key="tab1_v_ei"
        )
    r_inv = vol_ei_ul / vol_muestra_ul if vol_muestra_ul > 0 else 1.0
    if vol_ei_ul >= vol_muestra_ul and vol_muestra_ul > 0:
        rel_str_tab1 = f"1:{r_inv:.0f}" if abs(r_inv - round(r_inv)) < 0.05 else f"1:{r_inv:.2f}"
    else:
        dir_r = vol_muestra_ul / vol_ei_ul if vol_ei_ul > 0 else 1.0
        rel_str_tab1 = f"{dir_r:.0f}:1" if abs(dir_r - round(dir_r)) < 0.05 else f"{dir_r:.2f}:1"

    with c_v3:
        render_html(f"""
        <div style="background:#E5E7EB; padding:10px; border-radius:6px; border:1px solid #CBD5E1; margin-top:4px;">
            <b>Relación (Muestra / E.I.):</b> <span class="numeric-val">{rel_str_tab1}</span><br>
            <span style="font-size:0.82rem; color:#334155;">Ajusta la concentración final esperada en matriz del Estándar Interno.</span>
        </div>
        """)

    # Determinar parámetros según selección, pureza, volumen final y relación
    if "Estandar interno" in seleccion or "Estándar Interno" in seleccion:
        reactivo_nombre = "1-Propanol"
        densidad = 0.804
        conc_inicial_mg_dl = densidad * 100000.0 * (pureza_usuario / 100.0)

        # Matraz 1 (Solución Madre) = 100 mL
        # Matraz 2 (Matraz Final) = v_final_ml
        # Alícuota transferida = 1000 µL = 1.0 mL
        # En matriz se busca 100.0 mg/dL -> en Matraz 2: 100.0 * (vol_muestra_ul / vol_ei_ul)
        conc_solucion_ei = 100.0 * (vol_muestra_ul / vol_ei_ul) if vol_ei_ul > 0 else 100.0
        conc_final_matriz = 100.0
        conc_madre = conc_solucion_ei * (v_final_ml / 1.0)

        # Masa en Matraz 1 (100 mL = 1 dL): masa = conc_madre (mg)
        vol_base_100 = (conc_madre / 0.804)  # en µL
        vol_ajustado = vol_base_100 * (100.0 / pureza_usuario)
        vol_str = f"{vol_ajustado:.1f} µL"

        reactivos_tabla = [
            {"Reactivo / Material": "1-Propanol (para Matraz 1)", "Cantidad": vol_str, "Concentración": f"{conc_inicial_mg_dl:,.2f} mg/dL"},
            {"Reactivo / Material": "Matraz Aforado 1 (Solución Madre)", "Cantidad": "100 mL", "Concentración": f"{conc_madre:.2f} mg/dL"},
            {"Reactivo / Material": "Solución Madre de E.I. (para Matraz 2)", "Cantidad": "1000 µL", "Concentración": f"{conc_madre:.2f} mg/dL"},
            {"Reactivo / Material": f"Matraz Aforado 2 (Matraz Final)", "Cantidad": f"{v_final_ml:.0f} mL", "Concentración": f"{conc_final_matriz:.2f} mg/dL (en matriz)"}
        ]
        pasos = [
            {
                "title": "Matraz 1 (100 mL): Solución Madre",
                "desc": f"En un matraz aforado de 100 mL con agua destilada a la mitad, agregar {vol_str} de 1-propanol (al {pureza_usuario:.2f}% de pureza).",
                "conc": f"Alícuota: {vol_str}"
            },
            {
                "title": "Aforo Matraz 1 (100 mL)",
                "desc": "Aforar el matraz de 100 mL con agua destilada, tapar con Parafilm y homogeneizar por inversión.",
                "conc": f"{conc_madre:.2f} mg/dL"
            },
            {
                "title": f"Matraz 2 ({v_final_ml:.0f} mL): Dilución Final",
                "desc": f"En un matraz aforado de {v_final_ml:.0f} mL con agua destilada a la mitad, agregar 1000 µL de la Solución Madre (Matraz 1).",
                "conc": "Alícuota: 1000 µL"
            },
            {
                "title": f"Aforo Matraz 2 ({v_final_ml:.0f} mL)",
                "desc": f"Aforar el matraz de {v_final_ml:.0f} mL con agua destilada, tapar con Parafilm y guardar de 4 °C a 8 °C ({vol_ei_ul:.0f} µL E.I. + {vol_muestra_ul:.0f} µL muestra).",
                "conc": f"{conc_final_matriz:.2f} mg/dL (en matriz)"
            }
        ]

    elif "Control Bajo" in seleccion:
        reactivo_nombre = "Etanol"
        densidad = 0.789
        conc_inicial_mg_dl = densidad * 100000.0 * (pureza_usuario / 100.0)
        conc_obj = 50.0
        vol_base_100 = (conc_obj * v_final_ml * 1000.0) / 78900.0
        vol_ajustado = vol_base_100 * (100.0 / pureza_usuario)
        vol_str = f"{vol_ajustado:.1f} µL"

        reactivos_tabla = [
            {"Reactivo / Material": "Etanol", "Cantidad": vol_str, "Concentración": f"{conc_inicial_mg_dl:,.2f} mg/dL"},
            {"Reactivo / Material": "Agua Destilada", "Cantidad": f"C.b.p. {v_final_ml:.0f} mL", "Concentración": "—"},
            {"Reactivo / Material": f"Matraz Aforado (Control Bajo)", "Cantidad": f"{v_final_ml:.0f} mL", "Concentración": f"{conc_obj:.2f} mg/dL"}
        ]
        pasos = [
            {
                "title": f"Pre-llenado ({v_final_ml:.0f} mL)",
                "desc": f"En un matraz aforado de {v_final_ml:.0f} mL (rotulado como Control Bajo - CB), llenar con agua destilada a la mitad de su capacidad.",
                "conc": f"Matraz: {v_final_ml:.0f} mL"
            },
            {
                "title": "Adición de Etanol",
                "desc": f"Agregar {vol_str} de etanol (al {pureza_usuario:.2f}% de pureza).",
                "conc": f"Alícuota: {vol_str}"
            },
            {
                "title": f"Aforo y Conservación ({v_final_ml:.0f} mL)",
                "desc": f"Aforar a {v_final_ml:.0f} mL con agua destilada, tapar con Parafilm y guardar de 4 °C a 8 °C hasta su uso.",
                "conc": f"{conc_obj:.2f} mg/dL"
            }
        ]

    elif "Control Medio" in seleccion:
        reactivo_nombre = "Etanol"
        densidad = 0.789
        conc_inicial_mg_dl = densidad * 100000.0 * (pureza_usuario / 100.0)
        conc_obj = 100.0
        vol_base_100 = (conc_obj * v_final_ml * 1000.0) / 78900.0
        vol_ajustado = vol_base_100 * (100.0 / pureza_usuario)
        vol_str = f"{vol_ajustado:.1f} µL"

        reactivos_tabla = [
            {"Reactivo / Material": "Etanol", "Cantidad": vol_str, "Concentración": f"{conc_inicial_mg_dl:,.2f} mg/dL"},
            {"Reactivo / Material": "Agua Destilada", "Cantidad": f"C.b.p. {v_final_ml:.0f} mL", "Concentración": "—"},
            {"Reactivo / Material": f"Matraz Aforado (Control Medio)", "Cantidad": f"{v_final_ml:.0f} mL", "Concentración": f"{conc_obj:.2f} mg/dL"}
        ]
        pasos = [
            {
                "title": f"Pre-llenado ({v_final_ml:.0f} mL)",
                "desc": f"En un matraz aforado de {v_final_ml:.0f} mL (rotulado como Control Medio - CM), llenar con agua destilada a la mitad de su capacidad.",
                "conc": f"Matraz: {v_final_ml:.0f} mL"
            },
            {
                "title": "Adición de Etanol",
                "desc": f"Agregar {vol_str} de etanol (al {pureza_usuario:.2f}% de pureza).",
                "conc": f"Alícuota: {vol_str}"
            },
            {
                "title": f"Aforo y Conservación ({v_final_ml:.0f} mL)",
                "desc": f"Aforar a {v_final_ml:.0f} mL con agua destilada, tapar con Parafilm y guardar de 4 °C a 8 °C hasta su uso.",
                "conc": f"{conc_obj:.2f} mg/dL"
            }
        ]

    else:  # Control Alto
        reactivo_nombre = "Etanol"
        densidad = 0.789
        conc_inicial_mg_dl = densidad * 100000.0 * (pureza_usuario / 100.0)
        conc_obj = 400.0
        vol_base_100 = (conc_obj * v_final_ml * 1000.0) / 78900.0
        vol_ajustado = vol_base_100 * (100.0 / pureza_usuario)
        vol_str = f"{vol_ajustado:.1f} µL"

        reactivos_tabla = [
            {"Reactivo / Material": "Etanol", "Cantidad": vol_str, "Concentración": f"{conc_inicial_mg_dl:,.2f} mg/dL"},
            {"Reactivo / Material": "Agua Destilada", "Cantidad": f"C.b.p. {v_final_ml:.0f} mL", "Concentración": "—"},
            {"Reactivo / Material": f"Matraz Aforado (Control Alto)", "Cantidad": f"{v_final_ml:.0f} mL", "Concentración": f"{conc_obj:.2f} mg/dL"}
        ]
        pasos = [
            {
                "title": f"Pre-llenado ({v_final_ml:.0f} mL)",
                "desc": f"En un matraz aforado de {v_final_ml:.0f} mL (rotulado como Control Alto - CA), llenar con agua destilada a la mitad de su capacidad.",
                "conc": f"Matraz: {v_final_ml:.0f} mL"
            },
            {
                "title": "Adición de Etanol",
                "desc": f"Agregar {vol_str} de etanol (al {pureza_usuario:.2f}% de pureza).",
                "conc": f"Alícuota: {vol_str}"
            },
            {
                "title": f"Aforo y Conservación ({v_final_ml:.0f} mL)",
                "desc": f"Aforar a {v_final_ml:.0f} mL con agua destilada, tapar con Parafilm y guardar de 4 °C a 8 °C hasta su uso.",
                "conc": f"{conc_obj:.2f} mg/dL"
            }
        ]

    # Cuadro de Parámetros del Reactivo (Densidad, Pureza del usuario y Concentración inicial en mg/dL)
    st.markdown("<hr style='border-color:#D1D5DB;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        render_html(f"""
        <div class="forensic-card" style="border-left: 5px solid #C0392B;">
            <h4 style="margin-top:0;">⚗️ Parámetros del Reactivo ({reactivo_nombre})</h4>
            <p style="margin-bottom:6px;"><b>Densidad:</b> <span class="numeric-val">{densidad:.3f} g/mL</span></p>
            <p style="margin-bottom:6px;"><b>Pureza:</b> <span class="numeric-val">{pureza_usuario:.2f} %</span></p>
            <p style="margin-bottom:0;"><b>Concentración inicial:</b> <span class="numeric-val">{conc_inicial_mg_dl:,.2f} mg/dL</span></p>
        </div>
        """)

    # Tabla de reactivos necesarios
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Reactivos Necesarios</h3>", unsafe_allow_html=True)
    st.table(reactivos_tabla)

    # Procedimiento paso a paso
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>Procedimiento Analítico</h3>", unsafe_allow_html=True)
    render_step_flow(pasos)

    render_analytical_note_tox()

# ==============================================================================
# PESTAÑA 2: CALCULADORA DE ESTÁNDARES Y CONTROLES
# ==============================================================================

def apply_preset(preset_name):
    if preset_name in ["EI_M2", "EI"]:
        st.session_state.calc_rol = "Estándar Interno (1-Propanol)"
        st.session_state.calc_solvente = "1-Propanol"
        st.session_state.calc_modo_inic = "Por Densidad (g/mL) y Pureza (%)"
        st.session_state.calc_densidad = 0.804
        st.session_state.calc_pureza = 100.0
        st.session_state.calc_num_dil = "2 Diluciones (2 Matraces: Solución Madre + Matraz Final)"
        st.session_state.calc_conc_obj = 100.0
        st.session_state.calc_v_madre = 100.0
        st.session_state.calc_v_final = 50.0
        st.session_state.calc_alicuota_madre_ul = 1000.0
        st.session_state.calc_v_muestra = 200.0
        st.session_state.calc_v_ei = 1800.0
    elif preset_name == "CB":
        st.session_state.calc_rol = "Control Bajo (CB)"
        st.session_state.calc_solvente = "Etanol"
        st.session_state.calc_modo_inic = "Por Densidad (g/mL) y Pureza (%)"
        st.session_state.calc_densidad = 0.789
        st.session_state.calc_pureza = 100.0
        st.session_state.calc_num_dil = "1 Dilución (1 Matraz)"
        st.session_state.calc_conc_obj = 50.0
        st.session_state.calc_v_final = 100.0
    elif preset_name == "CM":
        st.session_state.calc_rol = "Control Medio (CM)"
        st.session_state.calc_solvente = "Etanol"
        st.session_state.calc_modo_inic = "Por Densidad (g/mL) y Pureza (%)"
        st.session_state.calc_densidad = 0.789
        st.session_state.calc_pureza = 100.0
        st.session_state.calc_num_dil = "1 Dilución (1 Matraz)"
        st.session_state.calc_conc_obj = 100.0
        st.session_state.calc_v_final = 100.0
    elif preset_name == "CA":
        st.session_state.calc_rol = "Control Alto (CA)"
        st.session_state.calc_solvente = "Etanol"
        st.session_state.calc_modo_inic = "Por Densidad (g/mL) y Pureza (%)"
        st.session_state.calc_densidad = 0.789
        st.session_state.calc_pureza = 100.0
        st.session_state.calc_num_dil = "1 Dilución (1 Matraz)"
        st.session_state.calc_conc_obj = 400.0
        st.session_state.calc_v_final = 100.0


def init_calc_state():
    defaults = {
        "calc_rol": "Estándar Interno (1-Propanol)",
        "calc_solvente": "1-Propanol",
        "calc_modo_inic": "Por Densidad (g/mL) y Pureza (%)",
        "calc_densidad": 0.804,
        "calc_conc_inic_manual": 80400.0,
        "calc_pureza": 100.0,
        "calc_num_dil": "1 Dilución (1 Matraz)",
        "calc_conc_obj": 100.0,
        "calc_v_madre": 100.0,
        "calc_v_final": 1000.0,
        "calc_alicuota_madre_ul": 1000.0,
        "calc_v_muestra": 200.0,
        "calc_v_ei": 1800.0
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def on_rol_change():
    rol = st.session_state.calc_rol
    if "Estándar Interno" in rol:
        st.session_state.calc_solvente = "1-Propanol"
        st.session_state.calc_densidad = 0.804
        st.session_state.calc_conc_obj = 100.0
        st.session_state.calc_num_dil = "2 Diluciones (2 Matraces: Solución Madre + Matraz Final)"
        st.session_state.calc_v_madre = 100.0
        st.session_state.calc_v_final = 50.0
        st.session_state.calc_alicuota_madre_ul = 1000.0
    elif "Control Bajo" in rol:
        st.session_state.calc_solvente = "Etanol"
        st.session_state.calc_densidad = 0.789
        st.session_state.calc_conc_obj = 50.0
        st.session_state.calc_v_final = 100.0
        st.session_state.calc_num_dil = "1 Dilución (1 Matraz)"
    elif "Control Medio" in rol:
        st.session_state.calc_solvente = "Etanol"
        st.session_state.calc_densidad = 0.789
        st.session_state.calc_conc_obj = 100.0
        st.session_state.calc_v_final = 100.0
        st.session_state.calc_num_dil = "1 Dilución (1 Matraz)"
    elif "Control Alto" in rol:
        st.session_state.calc_solvente = "Etanol"
        st.session_state.calc_densidad = 0.789
        st.session_state.calc_conc_obj = 400.0
        st.session_state.calc_v_final = 100.0
        st.session_state.calc_num_dil = "1 Dilución (1 Matraz)"


def on_solvente_change():
    solv = st.session_state.calc_solvente
    if solv in SOLVENT_PROPERTIES:
        st.session_state.calc_densidad = SOLVENT_PROPERTIES[solv]["densidad_g_ml"]
        st.session_state.calc_conc_inic_manual = SOLVENT_PROPERTIES[solv]["densidad_g_ml"] * 100000.0


def tab_cgms_calculadora():
    init_calc_state()

    st.markdown("<h2 style='text-align:center;'>🧮 Calculadora de Estándares y Controles</h2>", unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button("📌 E.I. 1-Propanol (2 Matraces)", use_container_width=True):
            apply_preset("EI_M2")
            st.rerun()
    with b2:
        if st.button("🟢 Control Bajo (50 mg/dL)", use_container_width=True):
            apply_preset("CB")
            st.rerun()
    with b3:
        if st.button("🟡 Control Medio (100 mg/dL)", use_container_width=True):
            apply_preset("CM")
            st.rerun()
    with b4:
        if st.button("🔴 Control Alto (400 mg/dL)", use_container_width=True):
            apply_preset("CA")
            st.rerun()

    st.markdown("<hr style='border-color:#D1D5DB;'>", unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns(2)

    with col_cfg1:
        st.markdown("<div class='forensic-card' style='border-left: 4px solid #003366; padding:12px;'><h4 style='color:#003366 !important; margin:0;'>🧪 1. Parámetros del Reactivo Inicial</h4></div>", unsafe_allow_html=True)

        rol_actual = st.selectbox(
            "Estándar o Control:",
            [
                "Estándar Interno (1-Propanol)",
                "Control Bajo (CB)",
                "Control Medio (CM)",
                "Control Alto (CA)",
                "Personalizado"
            ],
            key="calc_rol",
            on_change=on_rol_change
        )

        solv_sel = st.selectbox(
            "Reactivo:",
            list(SOLVENT_PROPERTIES.keys()),
            key="calc_solvente",
            on_change=on_solvente_change
        )

        modo_inic = st.radio(
            "Definir concentración inicial por:",
            [
                "Por Densidad (g/mL) y Pureza (%)",
                "Por Concentración Inicial (mg/dL) y Pureza (%)"
            ],
            key="calc_modo_inic"
        )

        c_in1, c_in2 = st.columns(2)
        with c_in1:
            if modo_inic.startswith("Por Densidad"):
                densidad_val = st.number_input(
                    "Densidad (g/mL):",
                    min_value=0.100,
                    max_value=3.000,
                    step=0.001,
                    format="%.3f",
                    key="calc_densidad"
                )
                conc_base_100_mg_dl = densidad_val * 100000.0
            else:
                conc_base_100_mg_dl = st.number_input(
                    "Concentración base al 100% (mg/dL):",
                    min_value=1.0,
                    max_value=300000.0,
                    step=100.0,
                    format="%.2f",
                    key="calc_conc_inic_manual"
                )
                densidad_val = conc_base_100_mg_dl / 100000.0

        with c_in2:
            pureza_val = st.number_input(
                "Pureza (%):",
                min_value=1.0,
                max_value=100.0,
                step=0.1,
                format="%.2f",
                key="calc_pureza"
            )

        conc_inic_efectiva_mg_dl = conc_base_100_mg_dl * (pureza_val / 100.0)

        st.markdown(
            f"<div style='background:#E5E7EB; padding:10px; border-radius:6px; border:1px solid #CBD5E1; margin-top:8px;'>"
            f"<b>Densidad:</b> <span class='numeric-val'>{densidad_val:.3f} g/mL</span> &nbsp;|&nbsp; "
            f"<b>Pureza:</b> <span class='numeric-val'>{pureza_val:.2f} %</span><br>"
            f"<b>Concentración inicial:</b> <span class='numeric-val' style='color:#C0392B;'>{conc_inic_efectiva_mg_dl:,.2f} mg/dL</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_cfg2:
        st.markdown("<div class='forensic-card' style='border-left: 4px solid #C0392B; padding:12px;'><h4 style='color:#C0392B !important; margin:0;'>⚗️ 2. Diluciones, Relación en Vial y Matraz Aforado</h4></div>", unsafe_allow_html=True)

        es_ei = "Estándar Interno" in rol_actual

        # Sección para poner cantidad de Estándar Interno y Muestra o Control
        c_rel1, c_rel2 = st.columns(2)
        with c_rel1:
            v_muestra_ul = st.number_input(
                "Cantidad de Muestra o Control (µL):",
                min_value=1.0,
                max_value=5000.0,
                step=10.0,
                format="%.0f",
                key="calc_v_muestra"
            )
        with c_rel2:
            v_ei_ul = st.number_input(
                "Cantidad de Estándar Interno (µL):",
                min_value=1.0,
                max_value=5000.0,
                step=50.0,
                format="%.0f",
                key="calc_v_ei"
            )

        r_inv_calc = v_ei_ul / v_muestra_ul if v_muestra_ul > 0 else 1.0
        if v_ei_ul >= v_muestra_ul and v_muestra_ul > 0:
            rel_str_tab2 = f"1:{r_inv_calc:.0f}" if abs(r_inv_calc - round(r_inv_calc)) < 0.05 else f"1:{r_inv_calc:.2f}"
        else:
            dir_calc = v_muestra_ul / v_ei_ul if v_ei_ul > 0 else 1.0
            rel_str_tab2 = f"{dir_calc:.0f}:1" if abs(dir_calc - round(dir_calc)) < 0.05 else f"{dir_calc:.2f}:1"

        if es_ei:
            conc_esperada_matriz_mg_dl = st.number_input(
                "Concentración esperada en la matriz (mg/dL):",
                min_value=0.01,
                max_value=50000.0,
                step=5.0,
                format="%.2f",
                key="calc_conc_obj"
            )
            # Para el Estándar Interno, la concentración de preparación en solución se ajusta por la relación Muestra/E.I.
            conc_solucion_trabajo_mg_dl = conc_esperada_matriz_mg_dl * (v_muestra_ul / v_ei_ul) if v_ei_ul > 0 else conc_esperada_matriz_mg_dl
            conc_final_mostrada_mg_dl = conc_esperada_matriz_mg_dl
            etiqueta_conc_final = f"{conc_final_mostrada_mg_dl:.2f} mg/dL (en matriz, relación Muestra/E.I. {rel_str_tab2})"
        else:
            conc_esperada_matriz_mg_dl = st.number_input(
                "Concentración deseada del Control (mg/dL):",
                min_value=0.01,
                max_value=50000.0,
                step=5.0,
                format="%.2f",
                key="calc_conc_obj"
            )
            conc_solucion_trabajo_mg_dl = conc_esperada_matriz_mg_dl
            conc_final_mostrada_mg_dl = conc_esperada_matriz_mg_dl
            etiqueta_conc_final = f"{conc_final_mostrada_mg_dl:.2f} mg/dL"

        if es_ei:
            st.info("ℹ️ Para el **Estándar Interno**, se utiliza el protocolo estandarizado de **2 Diluciones (2 Matraces: Solución Madre + Matraz Final)**.")
            num_diluciones = 2
            st.session_state.calc_num_dil = "2 Diluciones (2 Matraces: Solución Madre + Matraz Final)"
        else:
            num_dil_str = st.selectbox(
                "Cantidad de Diluciones:",
                [
                    "1 Dilución (1 Matraz)",
                    "2 Diluciones (2 Matraces: Solución Madre + Matraz Final)"
                ],
                key="calc_num_dil"
            )
            num_diluciones = 1 if num_dil_str.startswith("1") else 2

        if num_diluciones == 1:
            v_final_ml = st.number_input(
                "Volumen del Matraz Aforado (mL):",
                min_value=1.0,
                max_value=5000.0,
                step=10.0,
                format="%.0f",
                key="calc_v_final"
            )
            v_madre_ml = None
        else:
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                v_madre_ml = st.number_input(
                    "Volumen Matraz 1 — Solución Madre (mL):",
                    min_value=1.0,
                    max_value=5000.0,
                    step=10.0,
                    format="%.0f",
                    key="calc_v_madre"
                )
            with c_m2:
                v_final_ml = st.number_input(
                    "Volumen Matraz 2 — Matraz Final (mL):",
                    min_value=1.0,
                    max_value=5000.0,
                    step=10.0,
                    format="%.0f",
                    key="calc_v_final"
                )

            alicuota_madre_ul = st.number_input(
                "Alícuota de Solución Madre (Matraz 1) a transferir al Matraz 2 (µL):",
                min_value=1.0,
                max_value=float(v_final_ml * 1000.0),
                step=50.0,
                format="%.0f",
                key="calc_alicuota_madre_ul"
            )

    # ==========================================================================
    # RESULTADOS DE LA CALCULADORA POR PASO
    # ==========================================================================
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>📊 Concentración y Volúmenes por Matraz</h3>", unsafe_allow_html=True)

    if num_diluciones == 1:
        vol_puro_corregido_ul = (conc_solucion_trabajo_mg_dl * v_final_ml * 1000.0) / conc_inic_efectiva_mg_dl

        c_l, c_m, c_r = st.columns([1, 2, 1])
        with c_m:
            render_html(f"""
            <div class="forensic-card" style="border-top: 5px solid #003366;">
                <span class="badge-navy">PASO 1 DE 1 — MATRAZ ÚNICO</span>
                <h3 style="margin:8px 0;">Matraz Aforado de {v_final_ml:.0f} mL</h3>
                <p style="margin-bottom:6px;"><b>Concentración inicial de {SOLVENT_PROPERTIES[solv_sel]['nombre']}:</b> <span class="numeric-val">{conc_inic_efectiva_mg_dl:,.2f} mg/dL</span></p>
                <p style="margin-bottom:6px;"><b>Alícuota de {SOLVENT_PROPERTIES[solv_sel]['nombre']} a agregar:</b> <span class="numeric-val" style="font-size:1.15rem; color:#C0392B;">{vol_puro_corregido_ul:.1f} µL</span></p>
                <p style="margin-bottom:6px;"><b>Volumen de aforo del matraz:</b> <span class="numeric-val">{v_final_ml:.0f} mL</span></p>
                <hr style="border-color:#D1D5DB; margin:10px 0;">
                <p style="margin-bottom:0; font-size:1.05rem;"><b>Concentración Final ({v_final_ml:.0f} mL):</b><br>
                    <span class="numeric-val" style="font-size:1.25rem; color:#003366;">{etiqueta_conc_final}</span>
                </p>
            </div>
            """)

        pasos_calc = [
            {
                "title": f"Matraz Aforado ({v_final_ml:.0f} mL)",
                "desc": f"En un matraz aforado de {v_final_ml:.0f} mL, llenar con agua destilada a la mitad de su capacidad.",
                "conc": f"Matraz: {v_final_ml:.0f} mL"
            },
            {
                "title": f"Adición de {SOLVENT_PROPERTIES[solv_sel]['nombre']}",
                "desc": f"Agregar {vol_puro_corregido_ul:.1f} µL de {SOLVENT_PROPERTIES[solv_sel]['nombre']} (al {pureza_val:.2f}% de pureza).",
                "conc": f"Alícuota: {vol_puro_corregido_ul:.1f} µL"
            },
            {
                "title": "Aforo Final",
                "desc": f"Aforar a {v_final_ml:.0f} mL con agua destilada, tapar con Parafilm y conservar de 4 °C a 8 °C.",
                "conc": f"{conc_final_mostrada_mg_dl:.2f} mg/dL"
            }
        ]
        render_step_flow(pasos_calc)

    else:
        factor_dil_2 = (v_final_ml * 1000.0) / alicuota_madre_ul
        conc_madre_mg_dl = conc_solucion_trabajo_mg_dl * factor_dil_2
        vol_puro_corregido_ul = (conc_madre_mg_dl * v_madre_ml * 1000.0) / conc_inic_efectiva_mg_dl

        col_m1, col_m2 = st.columns(2)

        with col_m1:
            render_html(f"""
            <div class="forensic-card" style="border-top: 5px solid #003366;">
                <span class="badge-navy">PASO 1 DE 2 — MATRAZ 1 (SOLUCIÓN MADRE)</span>
                <h4 style="margin:8px 0;">Matraz Aforado de {v_madre_ml:.0f} mL</h4>
                <p style="margin-bottom:6px;"><b>Concentración inicial de {SOLVENT_PROPERTIES[solv_sel]['nombre']}:</b> <span class="numeric-val">{conc_inic_efectiva_mg_dl:,.2f} mg/dL</span></p>
                <p style="margin-bottom:6px;"><b>Alícuota de {SOLVENT_PROPERTIES[solv_sel]['nombre']} a agregar:</b> <span class="numeric-val" style="font-size:1.15rem; color:#C0392B;">{vol_puro_corregido_ul:.1f} µL</span></p>
                <p style="margin-bottom:6px;"><b>Volumen de aforo del Matraz 1:</b> <span class="numeric-val">{v_madre_ml:.0f} mL</span></p>
                <hr style="border-color:#D1D5DB; margin:10px 0;">
                <p style="margin-bottom:0; font-size:1.05rem;"><b>Concentración del Matraz 1 ({v_madre_ml:.0f} mL):</b><br>
                    <span class="numeric-val" style="font-size:1.25rem; color:#003366;">{conc_madre_mg_dl:.2f} mg/dL</span>
                </p>
            </div>
            """)

        with col_m2:
            render_html(f"""
            <div class="forensic-card" style="border-top: 5px solid #0F766E;">
                <span class="badge-teal">PASO 2 DE 2 — MATRAZ 2 (MATRAZ FINAL)</span>
                <h4 style="margin:8px 0;">Matraz Aforado de {v_final_ml:.0f} mL</h4>
                <p style="margin-bottom:6px;"><b>Concentración de Solución Madre (Matraz 1):</b> <span class="numeric-val">{conc_madre_mg_dl:.2f} mg/dL</span></p>
                <p style="margin-bottom:6px;"><b>Alícuota de Solución Madre a transferir:</b> <span class="numeric-val" style="font-size:1.15rem; color:#0F766E;">{alicuota_madre_ul:.0f} µL</span></p>
                <p style="margin-bottom:6px;"><b>Volumen de aforo del Matraz 2:</b> <span class="numeric-val">{v_final_ml:.0f} mL</span></p>
                <hr style="border-color:#D1D5DB; margin:10px 0;">
                <p style="margin-bottom:0; font-size:1.05rem;"><b>Concentración Final del Matraz 2 ({v_final_ml:.0f} mL):</b><br>
                    <span class="numeric-val" style="font-size:1.25rem; color:#003366;">{etiqueta_conc_final}</span>
                </p>
            </div>
            """)

        pasos_calc_2 = [
            {
                "title": f"Matraz 1 ({v_madre_ml:.0f} mL): Solución Madre",
                "desc": f"En un matraz aforado de {v_madre_ml:.0f} mL con agua destilada a la mitad, agregar {vol_puro_corregido_ul:.1f} µL de {SOLVENT_PROPERTIES[solv_sel]['nombre']}.",
                "conc": f"Alícuota: {vol_puro_corregido_ul:.1f} µL"
            },
            {
                "title": f"Aforo Matraz 1 ({v_madre_ml:.0f} mL)",
                "desc": f"Aforar el Matraz 1 a {v_madre_ml:.0f} mL con agua destilada, tapar con Parafilm y homogenizar.",
                "conc": f"{conc_madre_mg_dl:.2f} mg/dL"
            },
            {
                "title": f"Matraz 2 ({v_final_ml:.0f} mL): Dilución",
                "desc": f"En un matraz aforado de {v_final_ml:.0f} mL con agua destilada a la mitad, agregar {alicuota_madre_ul:.0f} µL de la Solución Madre (Matraz 1).",
                "conc": f"Alícuota: {alicuota_madre_ul:.0f} µL"
            },
            {
                "title": f"Aforo Matraz 2 ({v_final_ml:.0f} mL)",
                "desc": f"Aforar el Matraz 2 a {v_final_ml:.0f} mL con agua destilada, tapar con Parafilm y conservar de 4 °C a 8 °C.",
                "conc": f"{conc_final_mostrada_mg_dl:.2f} mg/dL"
            }
        ]
        render_step_flow(pasos_calc_2)

    render_analytical_note_tox()


# ==============================================================================
# PESTAÑA 3: ANÁLISIS TOXICOLÓGICOS Y VENENOS (CONWAY, CARBOXI, AGLUTINACIÓN, VIH, CN, As, P)
# ==============================================================================

ANALISIS_TOXICOLOGICOS_DB = {
    "1. Microdifusión en Cámara de Conway (Alcoholes)": {
        "titulo": "Microdifusión en Cámara de Conway — Prueba de Dicromato de Potasio (Alcoholes)",
        "fundamento": (
            "Se basa en una reacción de <b>óxido-reducción (REDOX)</b> acoplada a una separación física por <b>microdifusión pasiva en cámara cerrada (Cámara de Conway)</b>. "
            "En la unidad sellada e incubada, los alcoholes volátiles de la muestra biológica (sangre u orina en el compartimento exterior) se evaporan y difunden por la fase gaseosa hacia el compartimento central, donde reaccionan con una <b>solución de dicromato de potasio (K<sub>2</sub>Cr<sub>2</sub>O<sub>7</sub>) en ácido sulfúrico (H<sub>2</sub>SO<sub>4</sub>) al 50% v/v</b>. "
            "El etanol (CH<sub>3</sub>CH<sub>2</sub>OH) se oxida a acetaldehído y finalmente a ácido acético (CH<sub>3</sub>COOH), mientras que el ion dicromato hexavalente (<b>Cr<sub>2</sub>O<sub>7</sub><sup>2-</sup>, Cr<sup>6+</sup> de color naranja brillante</b>) se reduce a ion crómico trivalente (<b>Cr<sup>3+</sup>, de color verde esmeralda / verde-azulado</b>)."
        ),
        "reaccion_general": "2 K₂Cr₂O₇ (Naranja, Cr⁶⁺) + 8 H₂SO₄ + 3 CH₃CH₂OH  ⟶  2 Cr₂(SO₄)₃ (Verde, Cr³⁺) + 3 CH₃COOH + 2 K₂SO₄ + 11 H₂O",
        "reactivos": [
            {
                "Reactivo": "Dicromato de Potasio (K₂Cr₂O₇) en H₂SO₄ al 50% v/v (Reactivo Oxidante)",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL (frasco ámbar)",
                "Preparación (Balanza Analítica y Micropipeta)": "Medir con micropipeta 5.0 mL (5000 µL) de agua destilada y, en baño de hielo, añadir lentamente 5.0 mL (5000 µL) de H₂SO₄ concentrado (50% v/v). Pesar en balanza analítica 0.1225 g (122.5 mg para 0.25 N en Conway) o hasta saturación (~0.350 g) de K₂Cr₂O₇ y disolver hasta completar 10 mL."
            },
            {
                "Reactivo": "Carbonato de Sodio (Na₂CO₃) al 20% p/v (Agente liberador)",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 2.000 g de Na₂CO₃ anhidro en balanza analítica y disolver en agua destilada hasta aforar a 10 mL."
            },
            {
                "Reactivo": "Estándar Control Positivo de Etanol (100 mg/dL)",
                "Estabilidad / Escala": "Almacenable en refrigeración — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Medir con micropipeta 12.7 µL de etanol absoluto (ρ = 0.789 g/mL) y aforar a 10 mL con agua destilada."
            }
        ],
        "pasos": [
            {
                "title": "Sellado y Disposición",
                "desc": "Engrasar el borde de la Cámara de Conway con vaselina. Colocar 1000 µL del reactivo de K₂Cr₂O₇ en H₂SO₄ al 50% v/v (naranja) en la celdilla central.",
                "conc": "Centro: 1000 µL Reactivo"
            },
            {
                "title": "Carga de Muestra",
                "desc": "En el compartimento exterior colocar 1000 µL de sangre u orina y 500 µL de Na₂CO₃ al 20% en el extremo opuesto del anillo exterior (o en tubo para líquidos: 50–100 µL de muestra + 1000 µL de agua + 1000 µL de reactivo).",
                "conc": "Exterior: 1000 µL Muestra"
            },
            {
                "title": "Difusión Térmica",
                "desc": "Cerrar herméticamente la cámara, mezclar suavemente el anillo exterior por rotación e incubar de 30 a 45 minutos a 37 °C (o 1–2 h a temperatura ambiente).",
                "conc": "Incubación: 37 °C"
            },
            {
                "title": "Lectura Cromática",
                "desc": "Observar el viraje de color en la celdilla central de naranja brillante (Cr⁶⁺) a verde o verde-azulado (Cr³⁺).",
                "conc": "Naranja ⟶ Verde"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO</span>
            <h4 style="margin:8px 0;">Viraje a Verde Esmeralda / Verde-Azulado (Cr³⁺)</h4>
            <div style="display:flex; justify-content:center; align-items:center; margin:12px 0;">
                <div style="width:120px; height:120px; border-radius:50%; background:#D97706; border:4px solid #6B7280; display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 12px rgba(0,0,0,0.25);">
                    <div style="width:62px; height:62px; border-radius:50%; background:linear-gradient(135deg, #059669, #0F766E); border:3px solid #E5E7EB; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:0.7rem; font-weight:bold;">
                        Centro<br>VERDE
                    </div>
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Celdilla Central:</b> Cambia homogéneamente de naranja brillante a <b>verde esmeralda o verde-azulado</b> por reducción a Cr<sup>3+</sup>.<br>
                <b>Anillo Exterior:</b> Muestra biológica oscura/rojiza aislada físicamente.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO</span>
            <h4 style="margin:8px 0;">Permanencia del Naranja Brillante (Cr⁶⁺)</h4>
            <div style="display:flex; justify-content:center; align-items:center; margin:12px 0;">
                <div style="width:120px; height:120px; border-radius:50%; background:#991B1B; border:4px solid #6B7280; display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 12px rgba(0,0,0,0.25);">
                    <div style="width:62px; height:62px; border-radius:50%; background:linear-gradient(135deg, #F59E0B, #EA580C); border:3px solid #E5E7EB; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:0.7rem; font-weight:bold;">
                        Centro<br>NARANJA
                    </div>
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Celdilla Central:</b> Conserva su color <b>naranja brillante</b> original sin cambio cromático.<br>
                <b>Interpretación:</b> Ausencia de alcoholes o reductores volátiles en la muestra.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "No es específica para etanol: producen igualmente coloración verde el acetaldehído, metanol, 1-propanol (n-propanol) y 2-propanol (isopropanol), así como formaldehído y acetona (cetoacidosis diabética). En prueba directa sin cámara de microdifusión, los aminofenoles y polifenoles orto/para dan color verde a pardo."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "Fuga del vapor de alcohol por sellado deficiente de la tapa de la Cámara de Conway; muestras almacenadas en tubos destapados donde el analito volátil se evaporó antes del análisis."},
            {"Tipo": "Interferencia Crítica", "Causa / Sustancia Interferente": "Uso de torundas con alcohol etílico o isopropílico durante la venopunción, o salpicadura accidental de la muestra biológica hacia la celdilla central."}
        ]
    },

    "2. Carboxihemoglobina — Prueba de Hoppe-Seyler (COHb)": {
        "titulo": "Determinación de Carboxihemoglobina (COHb) — Prueba Alcalina de Hoppe-Seyler",
        "fundamento": (
            "Se fundamenta en la <b>estabilidad diferencial de los complejos de la hemoglobina frente a la desnaturalización alcalina fuerte (NaOH al 15%)</b>. "
            "La <b>oxihemoglobina normal (O<sub>2</sub>Hb)</b> es inestable en medio fuertemente básico: al añadir NaOH, la proteína globina se desnaturaliza rápidamente y el hierro hemo (Fe<sup>2+</sup>) se oxida a Fe<sup>3+</sup> formando <b>hematina alcalina</b>, de color <b>marrón verdoso o café sucio</b>. "
            "Por el contrario, la <b>carboxihemoglobina (COHb)</b> presenta un enlace de coordinación Fe<sup>2+</sup>—CO sumamente estable que protege la estructura tridimensional de la globina y retarda su desnaturalización, manteniendo su coloración <b>rojo cereza o rosa brillante</b> durante al menos 60 segundos."
        ),
        "reaccion_general": "O₂Hb (Rojo) + NaOH (15%) ⟶ Hematina Alcalina (Café/Marrón inmediato)   |   COHb (Rojo cereza) + NaOH (15%) ⟶ Permanece Rojo Cereza (> 60 s)",
        "reactivos": [
            {
                "Reactivo": "Hidróxido de Sodio (NaOH) al 15% p/v",
                "Estabilidad / Escala": "Almacenable en frasco plástico — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 1.500 g de lentejas de NaOH en balanza analítica. Disolver poco a poco en 6.0 mL (6000 µL) de agua destilada (reacción exotérmica) y, una vez frío, aforar a 10 mL con agua destilada."
            },
            {
                "Reactivo": "Agua Destilada (Medio de hemólisis)",
                "Estabilidad / Escala": "Almacenable — 10 mL (5 mL por tubo)",
                "Preparación (Balanza Analítica y Micropipeta)": "Medir 5.0 mL (5000 µL) para el tubo problema y 5.0 mL (5000 µL) para el tubo testigo negativo."
            },
            {
                "Reactivo": "Sangre Testigo Negativo",
                "Estabilidad / Escala": "Muestra de referencia fresca",
                "Preparación (Balanza Analítica y Micropipeta)": "100 µL (2 gotas) de sangre normal oxigenada libre de carboxihemoglobina para comparación simultánea."
            }
        ],
        "pasos": [
            {
                "title": "Dilución Hemolítica",
                "desc": "Colocar 5.0 mL (5000 µL) de agua destilada en dos tubos de ensayo: Tubo 1 (Muestra problema) y Tubo 2 (Testigo negativo).",
                "conc": "5.0 mL H₂O / tubo"
            },
            {
                "title": "Adición de Sangre",
                "desc": "Añadir 100 µL (2 gotas) de sangre problema al Tubo 1 y 100 µL (2 gotas) de sangre testigo al Tubo 2. Mezclar hasta obtener un tono rosáceo tenue.",
                "conc": "Alícuota: 100 µL"
            },
            {
                "title": "Desnaturalización Alcalina",
                "desc": "Añadir de 150 a 250 µL (3 a 5 gotas) de NaOH al 15% a cada tubo y agitar suavemente.",
                "conc": "NaOH 15%: 150–250 µL"
            },
            {
                "title": "Observación Comparativa",
                "desc": "Comparar inmediatamente y a los 60 segundos el color de la muestra frente al tubo testigo sobre un fondo blanco.",
                "conc": "Lectura: 0 a 60 s"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO (COHb ≥ 20–25%)</span>
            <h4 style="margin:8px 0;">Persistencia del Color Rojo Cereza / Rosa Brillante</h4>
            <div style="height:65px; width:100%; border-radius:8px; background:linear-gradient(90deg, #E11D48, #F43F5E, #BE123C); border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; text-shadow:1px 1px 2px #000; margin:12px 0;">
                Tubo Problema: Rojo Cereza / Rosa Intenso Homogéneo (&gt; 60 s)
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Aspecto Visual:</b> Solución traslúcida homogénea de color <b>rojo brillante o rojo cereza</b> que resiste el cambio de color durante al menos 60 segundos tras añadir el NaOH al 15%.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO (SANGRE NORMAL)</span>
            <h4 style="margin:8px 0;">Viraje Inmediato a Marrón Verdoso / Café Sucio</h4>
            <div style="height:65px; width:100%; border-radius:8px; background:linear-gradient(90deg, #57534E, #4D4C38, #78350F); border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; text-shadow:1px 1px 2px #000; margin:12px 0;">
                Tubo Testigo / Negativo: Marrón Verdoso / Café Pajizo (&lt; 10 s)
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Aspecto Visual:</b> La solución pierde el tono rojizo en menos de 10 segundos y se torna <b>marrón verdosa, café sucia o amarillo pajizo</b> por formación de hematina alcalina.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "Hemoglobina Fetal (HbF) en sangre de recién nacidos y lactantes (naturalmente resistente a la desnaturalización alcalina). Exceso de sangre en la dilución inicial que enmascara el viraje a café."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "Niveles de COHb menores al 20% (fumadores o exposición leve, donde el color marrón de la O₂Hb predomina); lectura tardía (> 5–10 min, cuando la COHb termina desnaturalizándose); sangre intensamente putrefacta."},
            {"Tipo": "Interferencia por Metahemoglobina", "Causa / Sustancia Interferente": "Agentes oxidantes (cloratos, nitritos, nitratos, anilina, dapsona, benzocaína, herbicidas de urea) oxidan el Fe²⁺ del grupo hemo a Fe³⁺ (metahemoglobina), tornando la sangre marrón desde antes de agregar el NaOH (se diferencia añadiendo 200 µL de KCN al 10% a 1 mL de sangre, lo que produce color rojo inmediato)."}
        ]
    },

    "3. Venenos: Cianuros (CN⁻) — Prueba de Azul de Prusia": {
        "titulo": "Análisis de Venenos: Cianuros (CN⁻) — Reacción de Azul de Prusia (Sulfato Ferroso B / FeCl₃)",
        "fundamento": (
            "Al alcalinizar la muestra (o el destilado de ácido cianhídrico <b>HCN</b>) con <b>NaOH al 10% p/v</b> y añadir una solución recién preparada de <b>sulfato ferroso (FeSO<sub>4</sub> al 10% p/v)</b>, los iones cianuro (CN<sup>-</sup>) reaccionan con el Fe<sup>2+</sup> formando el anión complejo soluble <b>hexacianoferrato (II), [Fe(CN)<sub>6</sub>]<sup>4-</sup></b>. "
            "En presencia de iones férricos (<b>Fe<sup>3+</sup></b>, formados por oxidación parcial o añadidos directamente con <b>cloruro férrico FeCl<sub>3</sub> al 5% p/v preparado al momento</b>) y al agregar suficiente <b>HCl al 10% v/v</b> para disolver el precipitado verdoso-castaño de hidróxidos de hierro, se revela un color y precipitado azul intenso insoluble de <b>ferrocianuro férrico, Fe<sub>4</sub>[Fe(CN)<sub>6</sub>]<sub>3</sub> (Azul de Prusia)</b>. "
            "Adicionalmente, el FeCl<sub>3</sub> al 5% (50 g/L) detecta directamente <b>tiocianatos (SCN<sup>-</sup>, metabolito del cianuro)</b> formando un complejo rojo sangre [Fe(SCN)]<sup>2+</sup> (LOD = 50 mg/L)."
        ),
        "reaccion_general": "1) 6 CN⁻ + Fe²⁺ (en NaOH 10%) ⟶ [Fe(CN)₆]⁴⁻   |   2) 3 [Fe(CN)₆]⁴⁻ + 4 Fe³⁺ (en HCl 10%) ⟶ Fe₄[Fe(CN)₆]₃ ↓ (Azul de Prusia)",
        "reactivos": [
            {
                "Reactivo": "Sulfato Ferroso (FeSO₄·7H₂O) al 10% p/v",
                "Estabilidad / Escala": "⚠️ PREPARAR AL MOMENTO — Escala de 1 mL (No almacenable, se oxida al aire)",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.100 g (100 mg) de FeSO₄·7H₂O en balanza analítica y disolver inmediatamente antes de usar en 1000 µL (1.0 mL) de agua destilada recién hervida y enfriada."
            },
            {
                "Reactivo": "Cloruro Férrico (FeCl₃) al 5% p/v (50 g/L)",
                "Estabilidad / Escala": "⚠️ PREPARAR AL MOMENTO — Escala de 1 mL (No almacenable, se hidroliza)",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.050 g (50.0 mg) de FeCl₃ anhidro —o 0.0825 g (82.5 mg) de FeCl₃·6H₂O hexahidratado— en balanza analítica y disolver al momento en 1000 µL (1.0 mL) de agua destilada con micropipeta."
            },
            {
                "Reactivo": "Hidróxido de Sodio (NaOH) al 10% p/v",
                "Estabilidad / Escala": "Almacenable en frasco plástico — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 1.000 g de NaOH en balanza analítica y disolver en agua destilada hasta aforar a 10 mL."
            },
            {
                "Reactivo": "Ácido Clorhídrico (HCl) al 10% v/v",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Medir con micropipeta 1000 µL (1.0 mL) de HCl concentrado y llevar a 10 mL con agua destilada."
            },
            {
                "Reactivo": "Picrato de Sodio (Prueba complementaria de Steyn en papel)",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.500 g (500 mg) de bicarbonato de sodio (NaHCO₃) y 0.050 g (50 mg) de ácido pícrico en balanza analítica y disolver hasta aforar a 10 mL con agua destilada."
            }
        ],
        "pasos": [
            {
                "title": "Alcalinización (1 : 2)",
                "desc": "Diluir 500 µL de la muestra (o destilado alcalino) con 1000 µL de solución de NaOH al 10% p/v (proporción 1 mL muestra : 2 mL NaOH 10%).",
                "conc": "500 µL Muestra + 1000 µL NaOH"
            },
            {
                "title": "Adición de FeSO₄ (y FeCl₃)",
                "desc": "Añadir 1000 µL de la solución recién preparada de FeSO₄ al 10% p/v (y 50 µL de FeCl₃ al 5% preparado al momento para aportar Fe³⁺ inmediato).",
                "conc": "1000 µL FeSO₄ 10%"
            },
            {
                "title": "Disolución con HCl 10%",
                "desc": "Agregar suficiente solución de HCl al 10% v/v gota a gota hasta disolver por completo el precipitado de hidróxido ferroso/férrico.",
                "conc": "HCl 10% v/v c.b.p."
            },
            {
                "title": "Lectura de Azul de Prusia",
                "desc": "Observar la aparición de una coloración o precipitado azul intenso (Azul de Prusia) que confirma la presencia de cianuro.",
                "conc": "Azul de Prusia ↓"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO A CIANUROS (CN⁻)</span>
            <h4 style="margin:8px 0;">Precipitado o Coloración Azul de Prusia Intenso</h4>
            <div style="height:65px; width:100%; border-radius:8px; background:linear-gradient(180deg, #1E3A8A 20%, #172554 60%, #0F172A 100%); border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; text-shadow:1px 1px 2px #000; margin:12px 0;">
                Azul de Prusia Profundo + Sedimento Floculento Azul Oscuro (Fe₄[Fe(CN)₆]₃ ↓)
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Cambio de Color y Forma:</b> Tras disolver el hidróxido ferroso con HCl al 10%, aparece un <b>color azul profundo (Azul de Prusia)</b> con <b>precipitado floculento azul intenso</b>.<br>
                <i>(En papel de Picrato de Sodio/Steyn a 30 °C: el papel amarillo vira a naranja ⟶ naranja-marrón ⟶ rojo; para Tiocianatos con FeCl₃ 5%: color rojo profundo).</i>
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO A CIANUROS</span>
            <h4 style="margin:8px 0;">Solución Amarilla Pálida o Incolora Límpida (Sin Precipitado)</h4>
            <div style="height:65px; width:100%; border-radius:8px; background:linear-gradient(90deg, #FEF9C3, #FEF08A); border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; margin:12px 0;">
                Amarillo Pálido Transparente (Sin coloración ni precipitado azul)
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Aspecto Visual:</b> Al disolver los hidróxidos de hierro con HCl al 10%, la solución queda <b>transparente e incolora o amarillo muy pálido</b>, sin rastro de color azul.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Especificidad / Falsos Positivos", "Causa / Sustancia Interferente": "La reacción de Azul de Prusia con FeSO₄/HCl es altamente específica para cianuro libre y carece de interferencias comunes (salvo ferrocianuros o ferricianuros preexistentes si no se destila antes el HCN). En cambio, en la prueba de papel de Picrato de Sodio (Steyn) dan falso positivo compuestos con grupos ciano como cimetidina, difenoxilato e isoaminilo."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "No preparar al momento la solución de FeSO₄ al 10% en agua recién hervida y enfriada; volatilización previa del HCN (p. eb. 25.6 °C) en muestras mal cerradas; o exceso extremo de HCl concentrado."},
            {"Tipo": "Interferencias de Matriz", "Causa / Sustancia Interferente": "El sulfuro de hidrógeno (H₂S) de tejidos putrefactos forma FeS negro en el paso alcalino con NaOH, pero se disuelve completamente al añadir el HCl al 10%, permitiendo observar el Azul de Prusia sin interferencia."}
        ]
    },

    "4. Venenos: Arsénico (As), Fósforo (P) y Cianuro (CN⁻) — Prueba de Nitrato de Plata": {
        "titulo": "Análisis de Venenos (As, P y CN⁻) — Reacción con Nitrato de Plata (AgNO₃)",
        "fundamento": (
            "El <b>Nitrato de Plata (AgNO<sub>3</sub>)</b> permite identificar y diferenciar venenos volátiles y aniones tanto en <b>fase vapor (Ensayos de Scherer y Gutzeit)</b> como por <b>precipitación y solubilidad en solución (con HNO<sub>3</sub> 2 mol/L y NH<sub>4</sub>OH concentrado)</b>:<br>"
            "• <b>Fósforo blanco / Fosfuros (P / PH<sub>3</sub> — Ensayo de Scherer):</b> En medio ácido (H<sub>2</sub>SO<sub>4</sub> al 10% v/v) sin zinc, el gas fosfina (PH<sub>3</sub>) reduce directamente el papel impregnado con AgNO<sub>3</sub> a <b>plata metálica negra (Ag<sup>0</sup>)</b>.<br>"
            "• <b>Arsénico (As / AsH<sub>3</sub> — Ensayos de Gutzeit, Dietilditiocarbamato de Plata y Reinsch):</b> Con Zinc en ácido se genera gas arsina (AsH<sub>3</sub>), que con AgNO<sub>3</sub> forma un complejo <b>amarillo (AsAg<sub>3</sub>·3AgNO<sub>3</sub>)</b> que vira a <b>negro (Ag<sup>0</sup>)</b> con agua, o complejo rojo-violeta específico al burbujear en solución de <b>dietilditiocarbamato de plata</b> en efedrina/cloroformo. En el <i>Ensayo de Reinsch</i> (lámina de cobre electrolítico en HCl conc. a ebullición), el As deposita una película negra mate que <b>se disuelve selectivamente en cianuro de potasio (KCN) al 10% (100 g/L)</b>, diferenciándose de Sb y Bi (LOD = 5 mg/L).<br>"
            "• <b>En Solución y Confirmación de Cianuro:</b> El ion <b>CN<sup>-</sup></b> da precipitado <b>blanco cuajado (AgCN↓)</b> soluble en NH<sub>4</sub>OH (confirmable en fase vapor mediante papel de <b>Ácido Pícrico 0.5% – Carbonato de Sodio 5% [Prueba de Steyn]</b>, que vira de amarillo a rojo-naranja); el <b>arseniato (AsO<sub>4</sub><sup>3-</sup>)</b> da precipitado <b>rojo ladrillo (Ag<sub>3</sub>AsO<sub>4</sub>↓)</b>; y el <b>fosfato (PO<sub>4</sub><sup>3-</sup>)</b> da precipitado <b>amarillo (Ag<sub>3</sub>PO<sub>4</sub>↓)</b>."
        ),
        "reaccion_general": "Gas: AsH₃ / PH₃ + 6 AgNO₃ ⟶ Complejo Amarillo ⟶ (+H₂O) 6 Ag⁰ ↓ (Negro)   |   Solución: CN⁻ + Ag⁺ ⟶ AgCN ↓ (Blanco) | AsO₄³⁻ + 3Ag⁺ ⟶ Ag₃AsO₄ ↓ (Rojo ladrillo) | PO₄³⁻ + 3Ag⁺ ⟶ Ag₃PO₄ ↓ (Amarillo)",
        "reactivos": [
            {
                "Reactivo": "Nitrato de Plata (AgNO₃) Concentrado al 50% p/v (Para tirilla Gutzeit)",
                "Estabilidad / Escala": "⚠️ PREPARAR AL MOMENTO — Escala de 1 mL (Se fotorreduce rápidamente)",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.500 g (500 mg) de AgNO₃ en balanza analítica y disolver al momento en 1000 µL (1.0 mL) de agua destilada libre de cloruros con micropipeta."
            },
            {
                "Reactivo": "Nitrato de Plata (AgNO₃) Acuoso al 1% p/v (10 g/L) / 5% p/v",
                "Estabilidad / Escala": "Almacenable en frasco ámbar — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.100 g (100 mg para solución de 10 g/L en tubo) o 0.500 g (500 mg para solución al 5%) de AgNO₃ en balanza analítica y aforar a 10 mL con agua destilada libre de cloruros."
            },
            {
                "Reactivo": "Acetato de Plomo al 10% p/v + Ácido Acético 2 mol/L (Trampa de sulfuros H₂S)",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL (Relación 10 : 1)",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 1.000 g de acetato de plomo en 10 mL de agua hervida y purificada. Para impregnar el papel filtro trampa de H₂S, mezclar 9.0 mL (9000 µL) de acetato de plomo al 10% con 900 µL de ácido acético 2 mol/L (LOD para sulfuros = 50 mg/L)."
            },
            {
                "Reactivo": "Ácido Sulfúrico (H₂SO₄) al 10% v/v + Granallas de Zinc libre de As",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL (y 0.5 g de Zn sólido para As)",
                "Preparación (Balanza Analítica y Micropipeta)": "Medir con micropipeta 1000 µL (1.0 mL) de H₂SO₄ concentrado y aforar a 10 mL con agua destilada. Pesar 0.500 g de Zinc únicamente para la reducción de Arsénico (Gutzeit)."
            },
            {
                "Reactivo": "Ácido Nítrico (HNO₃) 2 mol/L e Hidróxido de Amonio (NH₄OH) concentrado",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL de HNO₃ 2 mol/L: medir 1280 µL de HNO₃ concentrado (65%) con micropipeta y aforar a 10 mL con agua destilada. Usar 100 µL de NH₄OH concentrado para pruebas de solubilidad del precipitado de plata."
            }
        ],
        "pasos": [
            {
                "title": "Generación en Tubo",
                "desc": "A 1000 µL de muestra en un tubo añadir 3000 µL de H₂SO₄ al 10% v/v (para Fósforo/Scherer calentar suavemente sin Zn; para Arsénico/Gutzeit añadir 0.5 g de Zn).",
                "conc": "H₂SO₄ 10%: 3000 µL"
            },
            {
                "title": "Trampa de Sulfuros (Pb²⁺)",
                "desc": "Insertar en el cuello del tubo papel o algodón impregnado con la mezcla 10:1 de Acetato de Plomo al 10% y Ácido Acético 2 mol/L para retener vapores de H₂S.",
                "conc": "Filtro Pb(AcO)₂ 10%"
            },
            {
                "title": "Tirilla con AgNO₃",
                "desc": "Colocar en la boca del tubo papel filtro con 20 µL de AgNO₃ (al 50% recién preparado para Gutzeit/As; al 1–5% para Scherer/P) y observar el ennegrecimiento.",
                "conc": "Tirilla: 20 µL AgNO₃"
            },
            {
                "title": "Precipitación en Solución",
                "desc": "En 1000 µL de solución clara añadir 100 µL de AgNO₃ (10 g/L), centrifugar el precipitado y probar su solubilidad añadiendo 100 µL de NH₄OH concentrado.",
                "conc": "100 µL AgNO₃ + 100 µL NH₄OH"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADOS POSITIVOS (EN TIRILLA Y EN SOLUCIÓN)</span>
            <h4 style="margin:8px 0;">Ennegrecimiento de Tirilla (Ag⁰) y Precipitados Diferenciales</h4>
            <div style="display:flex; justify-content:space-between; gap:8px; margin:12px 0;">
                <div style="flex:1; height:60px; border-radius:6px; background:linear-gradient(135deg, #FACC15 35%, #18181B 65%); border:1px solid #94A3B8; color:#FFF; font-size:0.72rem; font-weight:bold; display:flex; align-items:center; justify-content:center; text-shadow:1px 1px 2px #000; padding:4px;">
                    Tirilla (As / P):<br>Amarillo ⟶ Negro (Ag⁰)
                </div>
                <div style="flex:1; height:60px; border-radius:6px; background:#F8FAFC; border:2px solid #94A3B8; color:#003366; font-size:0.72rem; font-weight:bold; display:flex; align-items:center; justify-content:center; padding:4px;">
                    Solución CN⁻:<br>Precipitado Blanco (AgCN↓)
                </div>
                <div style="flex:1; height:60px; border-radius:6px; background:#9A3412; border:1px solid #94A3B8; color:#FFF; font-size:0.72rem; font-weight:bold; display:flex; align-items:center; justify-content:center; padding:4px;">
                    Solución AsO₄³⁻:<br>Rojo Ladrillo (Ag₃AsO₄↓)
                </div>
                <div style="flex:1; height:60px; border-radius:6px; background:#EAB308; border:1px solid #94A3B8; color:#003366; font-size:0.72rem; font-weight:bold; display:flex; align-items:center; justify-content:center; padding:4px;">
                    Solución PO₄³⁻:<br>Amarillo (Ag₃PO₄↓)
                </div>
            </div>
            <p style="font-size:0.86rem; margin-bottom:0;">
                <b>En Tirilla:</b> Mancha amarilla que vira a <b>negro metálico (As)</b> o ennegrecimiento directo sin Zn <b>(P)</b>.<br>
                <b>En Solución:</b> Precipitado <b>blanco cuajado soluble en NH<sub>4</sub>OH (CN<sup>-</sup>)</b>, <b>rojo ladrillo (AsO<sub>4</sub><sup>3-</sup>)</b> o <b>amarillo (PO<sub>4</sub><sup>3-</sup>)</b>.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO</span>
            <h4 style="margin:8px 0;">Tirilla Blanca Inalterada y Solución Transparente</h4>
            <div style="height:60px; width:100%; border-radius:8px; background:#FFFFFF; border:2px dashed #94A3B8; display:flex; align-items:center; justify-content:center; color:#475569; font-weight:bold; margin:12px 0;">
                Papel Reactivo Blanco Sin Mancha  |  Solución Límpida e Incolora (Sin Precipitado)
            </div>
            <p style="font-size:0.86rem; margin-bottom:0;">
                <b>Aspecto Visual:</b> La tirilla de AgNO<sub>3</sub> conserva su color blanco original sin oscurecerse y la solución permanece transparente sin precipitado.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "Los vapores de sulfuro de hidrógeno (H₂S, LOD = 50 mg/L) de muestras en putrefacción ennegrecen el AgNO₃ formando Ag₂S negro (se eliminan con el papel filtro previo de Acetato de Plomo al 10%). En solución directa, los cloruros (Cl⁻) dan precipitado blanco soluble en NH₄OH, los bromuros (Br⁻) precipitado blanco-crema poco soluble y los yoduros (I⁻) precipitado amarillo cuajado insoluble en NH₄OH."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "Presencia de oxidantes fuertes (HNO₃ libre o hipoclorito) en el tubo generador que oxidan la fosfina (PH₃) o arsina (AsH₃) impidiendo su volatilización; o exceso de ácido nítrico al precipitar Ag₃AsO₄ o Ag₃PO₄ en solución."},
            {"Tipo": "Interferencias", "Causa / Sustancia Interferente": "El antimonio (SbH₃, estibina) también oscurece la tirilla de AgNO₃ (en el ensayo de Reinsch, la mancha de As sobre cobre se disuelve en KCN 100 g/L mientras que Sb y Bi no se disuelven). Compuestos con grupos orto/para-dihidroxifenol o ácido ascórbico reducen el AgNO₃ amoniacal a Ag⁰ negro en solución."}
        ]
    },

    "5. Venenos: Fósforo (P) y Arsénico (As) — Prueba con Molibdato de Amonio": {
        "titulo": "Análisis de Venenos (P y As) — Reacción con Molibdato de Amonio",
        "fundamento": (
            "Tras someter la muestra (o el destilado/tirilla de Scherer) a una <b>digestión ácida oxidante con ácido nítrico concentrado (HNO<sub>3</sub>, 500 µL) y ácido sulfúrico concentrado (H<sub>2</sub>SO<sub>4</sub>, 200 µL) a 100 °C durante 30 minutos</b>, el fósforo elemental, fosfuros o compuestos organofosforados se oxidan a <b>ion ortofosfato (PO<sub>4</sub><sup>3-</sup>)</b> —y el arsénico a <b>ion arseniato (AsO<sub>4</sub><sup>3-</sup>)</b>—.<br>"
            "Al enfriar y añadir <b>1000 µL (1.0 mL) de solución de Molibdato de Amonio al 10% p/v</b> seguido de calentamiento en baño de agua a <b>100 °C por 5 minutos</b>, se forma una <b>solución o precipitado cristalino amarillo brillante</b> de dodecamolibdofosfato de amonio, <b>(NH<sub>4</sub>)<sub>3</sub>[P(Mo<sub>3</sub>O<sub>10</sub>)<sub>4</sub>]↓</b> (o arsenomolibdato de amonio). "
            "Al añadir una gota de reductor recién preparado (ácido ascórbico o SnCl<sub>2</sub>), el Mo<sup>6+</sup> del complejo se reduce parcialmente a Mo<sup>5+</sup> formando <b>Azul de Molibdeno</b>."
        ),
        "reaccion_general": "H₃PO₄ (ó H₃AsO₄) + 12 (NH₄)₂MoO₄ + 21 HNO₃  ⟶  (NH₄)₃[P/As(Mo₃O₁₀)₄] ↓ (Amarillo Brillante) + 21 NH₄NO₃ + 12 H₂O",
        "reactivos": [
            {
                "Reactivo": "Solución de Molibdato de Amonio al 10% p/v",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar en balanza analítica 1.000 g de molibdato de amonio [(NH₄)₆Mo₇O₂₄·4H₂O] y disolver en agua destilada (o medio nítrico diluido) hasta aforar a 10 mL. Se emplean 1000 µL (1.0 mL) por prueba."
            },
            {
                "Reactivo": "Ácido Nítrico Concentrado (HNO₃) y Ácido Sulfúrico Concentrado (H₂SO₄)",
                "Estabilidad / Escala": "Almacenables — Dosificación exacta con micropipeta por prueba",
                "Preparación (Balanza Analítica y Micropipeta)": "Medir con micropipeta 500 µL (0.5 mL) de HNO₃ concentrado y 200 µL (0.2 mL) de H₂SO₄ concentrado por cada tubo de ensayo (muestra y blanco)."
            },
            {
                "Reactivo": "Solución Reductora Confirmatoria (Ácido Ascórbico o SnCl₂ al 5% p/v)",
                "Estabilidad / Escala": "⚠️ PREPARAR AL MOMENTO — Escala de 1 mL (No almacenable, se oxida al aire)",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.050 g (50.0 mg) de ácido ascórbico (o SnCl₂·2H₂O) en balanza analítica y disolver al momento en 1000 µL (1.0 mL) de agua destilada con micropipeta."
            }
        ],
        "pasos": [
            {
                "title": "Digestión Ácida Oxidante",
                "desc": "A la muestra en un tubo de ensayo agregar con micropipeta 500 µL (0.5 mL) de HNO₃ concentrado y 200 µL (0.2 mL) de H₂SO₄ concentrado (tratar un blanco en paralelo).",
                "conc": "500 µL HNO₃ + 200 µL H₂SO₄"
            },
            {
                "title": "Calentamiento (30 min)",
                "desc": "Calentar el tubo a 100 °C en baño de agua durante 30 minutos para oxidar el fósforo/fosfuros u organofosforados a PO₄³⁻ (o As a AsO₄³⁻) y dejar enfriar.",
                "conc": "100 °C por 30 min"
            },
            {
                "title": "Adición de Molibdato 10%",
                "desc": "A la solución fría añadir 1000 µL (1.0 mL) de solución de Molibdato de Amonio al 10% p/v.",
                "conc": "Molibdato 10%: 1000 µL"
            },
            {
                "title": "Revelado a 100 °C (5 min)",
                "desc": "Colocar nuevamente en el baño de agua a 100 °C durante 5 minutos (en fosfatos libres precipita desde 40–50 °C) y observar el precipitado amarillo brillante.",
                "conc": "100 °C por 5 min"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO A FÓSFORO (P) O ARSÉNICO (As)</span>
            <h4 style="margin:8px 0;">Solución o Precipitado Amarillo Brillante (+ Confirmación Azul de Molibdeno)</h4>
            <div style="display:flex; gap:10px; margin:12px 0;">
                <div style="flex:1; height:65px; border-radius:8px; background:linear-gradient(180deg, #FEF9C3 25%, #FACC15 65%, #EAB308 100%); border:1px solid #CA8A04; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; font-size:0.82rem; padding:6px;">
                    1° Solución / Precipitado Amarillo Brillante Intenso ↓
                </div>
                <div style="flex:1; height:65px; border-radius:8px; background:linear-gradient(135deg, #1D4ED8, #1E3A8A); border:1px solid #1E40AF; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; font-size:0.82rem; padding:6px;">
                    2° Confirmación (+50 µL Reductor): Azul de Molibdeno
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Cambio de Color y Forma:</b> Formación de una <b>solución o precipitado cristalino amarillo brillante</b> de fosfomolibdato de amonio (o arsenomolibdato a 100 °C). Al añadir 50 µL del reductor recién preparado vira a <b>Azul de Molibdeno</b>.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO</span>
            <h4 style="margin:8px 0;">Solución Totalmente Incolora y Transparente (Igual al Blanco)</h4>
            <div style="height:65px; width:100%; border-radius:8px; background:linear-gradient(90deg, #F8FAFC, #F1F5F9); border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#475569; font-weight:bold; margin:12px 0;">
                Líquido Transparente e Incoloro (Ausencia de Color o Precipitado Amarillo)
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Aspecto Visual:</b> La solución permanece <b>completamente transparente e incolora</b> igual al tubo blanco tras el calentamiento a 100 °C por 5 minutos.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "Plaguicidas organofosforados (especialmente si la muestra es un líquido inmiscible en agua) y fármacos fosforados como ciclofosfamida y triclofós dan reacción positiva amarilla brillante. Fosfatos biológicos endógenos si se analiza tejido o fluido sin destilación previa del fósforo blanco/fosfina. Silicatos (SiO₃²⁻) extraídos del vidrio forman silicomolibdato amarillo."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "Digestión oxidante incompleta con HNO₃/H₂SO₄ (los fosfitos H₃PO₃ y arsenitos H₃AsO₃ trivalentes no reaccionan con el molibdato de amonio hasta oxidarse a estado pentavalente +5). Presencia de tartratos, citratos, oxalatos o fluoruros que secuestran al molibdeno."},
            {"Tipo": "Interferencia Térmica (P vs. As)", "Causa / Sustancia Interferente": "A 100 °C tanto el ortofosfato (PO₄³⁻) como el arseniato (AsO₄³⁻) forman precipitados amarillos isomorfos; para diferenciarlos sin separación previa, el fosfato precipita desde 40–50 °C mientras que el arseniato requiere ebullición a 100 °C."}
        ]
    }
}


ANALISIS_SEROLOGICOS_DB = {
    "1. Aglutinación Directa en Placa (Grupo Sanguíneo ABO y Factor Rh)": {
        "titulo": "Serología Hematológica Forense — Aglutinación Directa (Grupo Sanguíneo ABO / Rh)",
        "fundamento": (
            "Se basa en una <b>reacción inmunológica específica antígeno-anticuerpo de hemaglutinación directa</b>. "
            "Las membranas de los eritrocitos contienen glicoproteínas y glicolípidos antigénicos (<b>aglutinógenos A, B y D/Rh</b>). "
            "Al enfrentarse con anticuerpos monoclonales específicos tipo <b>IgM (hemoclasificadores Anti-A, Anti-B y Anti-D)</b>, la estructura pentamérica de la IgM (con 10 sitios de unión) forma puentes intercelulares que enlazan múltiples eritrocitos simultáneamente en una <b>red tridimensional visible como grumos macroscópicos ('arenilla')</b>. "
            "Requiere eritrocitos con membrana íntegra; si la muestra presenta hemólisis total, los antígenos quedan sueltos en el plasma y no se forman grumos."
        ),
        "reaccion_general": "Eritrocitos (Antígeno A / B / D) + Anticuerpo Monoclonal IgM (Anti-A / Anti-B / Anti-D)  ⟶  Red Tridimensional de Hemaglutinación (Grumos Macroscópicos)",
        "reactivos": [
            {
                "Reactivo": "Solución Salina Fisiológica Isotónica (NaCl al 0.9% p/v)",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Pesar 0.090 g (90 mg) de NaCl grado analítico en balanza analítica y disolver en agua destilada hasta aforar a 10 mL."
            },
            {
                "Reactivo": "Suero Hemoclasificador Monoclonal Anti-A (Color Azul)",
                "Estabilidad / Escala": "Almacenable en refrigeración (2–8 °C)",
                "Preparación (Balanza Analítica y Micropipeta)": "Reactivo monoclonal comercial listo para uso. Medir 50 µL (1 gota) por determinación."
            },
            {
                "Reactivo": "Suero Hemoclasificador Monoclonal Anti-B (Color Amarillo)",
                "Estabilidad / Escala": "Almacenable en refrigeración (2–8 °C)",
                "Preparación (Balanza Analítica y Micropipeta)": "Reactivo monoclonal comercial listo para uso. Medir 50 µL (1 gota) por determinación."
            },
            {
                "Reactivo": "Suero Hemoclasificador Monoclonal Anti-D / Rh (Incoloro)",
                "Estabilidad / Escala": "Almacenable en refrigeración (2–8 °C)",
                "Preparación (Balanza Analítica y Micropipeta)": "Reactivo monoclonal comercial listo para uso. Medir 50 µL (1 gota) por determinación."
            }
        ],
        "pasos": [
            {
                "title": "Marcaje de Placa",
                "desc": "Limpiar un portaobjetos o placa de vidrio y rotular cuatro áreas circulares: Anti-A, Anti-B, Anti-D (Rh) y Autocontrol (Salina).",
                "conc": "4 Áreas en Placa"
            },
            {
                "title": "Adición de Reactivos",
                "desc": "Depositar 50 µL (1 gota) de Anti-A, Anti-B, Anti-D y Solución Salina al 0.9% en sus círculos correspondientes.",
                "conc": "50 µL Reactivo / área"
            },
            {
                "title": "Adición de Eritrocitos",
                "desc": "Agregar 50 µL (1 gota) de sangre entera íntegra (o suspensión globular al 5% en salina) junto a cada reactivo y mezclar con aplicadores individuales.",
                "conc": "50 µL Muestra / área"
            },
            {
                "title": "Balanceo y Lectura",
                "desc": "Balancear suavemente la placa con movimiento circular durante 30 a 60 segundos (máximo 2 minutos) y observar la presencia de grumos.",
                "conc": "Lectura: 30–60 s"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO (CAMBIO DE FORMA: AGLUTINACIÓN)</span>
            <h4 style="margin:8px 0;">Formación de Grumos Rojos ("Arenilla") en Medio Claro</h4>
            <div style="display:flex; justify-content:center; gap:20px; margin:12px 0;">
                <div style="width:95px; height:95px; border-radius:50%; background:radial-gradient(circle at 25% 30%, #991B1B 8%, transparent 10%), radial-gradient(circle at 65% 25%, #B91C1C 9%, transparent 11%), radial-gradient(circle at 45% 55%, #7F1D1D 10%, transparent 12%), radial-gradient(circle at 30% 72%, #991B1B 8%, transparent 10%), radial-gradient(circle at 72% 68%, #B91C1C 9%, transparent 11%), radial-gradient(circle at 55% 35%, #991B1B 7%, transparent 9%), radial-gradient(circle at 38% 42%, #B91C1C 8%, transparent 10%), #F8FAFC; border:3px solid #003366; box-shadow: inset 0 0 8px rgba(0,0,0,0.15);"></div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Morfología Visual:</b> Los eritrocitos se agrupan formando <b>grumos o cúmulos rojizos nítidos (aspecto de arenilla o ladrillo molido)</b> mientras el líquido circundante queda <b>totalmente transparente/claro</b>.<br>
                <b>Interpretación ABO/Rh:</b> Grumos en A = <b>Grupo A</b> | Grumos en B = <b>Grupo B</b> | Grumos en A y B = <b>Grupo AB</b> | Grumos en D = <b>Rh (+)</b>.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO (SIN AGLUTINACIÓN)</span>
            <h4 style="margin:8px 0;">Suspensión Roja Líquida Totalmente Homogénea</h4>
            <div style="display:flex; justify-content:center; gap:20px; margin:12px 0;">
                <div style="width:95px; height:95px; border-radius:50%; background:#DC2626; border:3px solid #003366; box-shadow: inset 0 0 10px rgba(0,0,0,0.25);"></div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Morfología Visual:</b> El círculo permanece como una <b>suspensión líquida roja opaca y uniforme</b>, sin formación de cúmulos ni clarificación del fondo.<br>
                <b>Interpretación ABO/Rh:</b> Sin grumos en A ni en B = <b>Grupo O</b> | Sin grumos en D = <b>Rh (-)</b> | Autocontrol debe ser siempre homogéneo.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "Fenómeno de Rouleaux ('pilas de monedas' por exceso de proteínas plasmáticas o deshidratación; se corrige lavando los eritrocitos con solución salina al 0.9%). Autoaglutininas frías, contaminación bacteriana (pan-aglutinación) o lectura tardía > 2 minutos por desecación periférica."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "Hemólisis total de la muestra (al destruirse los eritrocitos no hay células que agrupar y se observa un líquido rojo traslúcido continuo, simulando un falso Grupo O Rh -). Efecto prozona o antígenos Rh débiles (Du)."},
            {"Tipo": "Interferencia Crítica", "Causa / Sustancia Interferente": "Contaminación cruzada por usar el mismo aplicador entre Anti-A y Anti-B (provoca falso Grupo AB). No aplicable directamente sobre manchas secas en tela."}
        ]
    },

    "2. Determinación de VIH-1 y VIH-2 (Inmunocromatografía en Placa)": {
        "titulo": "Serología e Inmunología Forense — Detección de Anticuerpos Anti-VIH-1 y VIH-2 (Flujo Lateral)",
        "fundamento": (
            "Se basa en un <b>inmunoensayo inmunocromatográfico tipo 'Sándwich' de doble antígeno</b> sobre membrana de nitrocelulosa. "
            "Los anticuerpos específicos (IgG/IgM) presentes en la muestra se unen en la almohadilla de conjugado a antígenos recombinantes de VIH marcados con <b>oro coloidal</b> (colorante rojo-púrpura). "
            "El complejo migra por capilaridad hasta las líneas de captura (<b>T1: gp120/gp41 para VIH-1; T2: gp36 para VIH-2</b>), donde queda inmovilizado formando una banda coloreada visible. "
            "El conjugado libre continúa hasta la <b>línea de Control (C)</b>, la cual siempre debe revelarse para validar la prueba. Todo resultado con banda en T debe reportarse pericialmente como <b>'REACCIONAL'</b> (sujeto a confirmación por Western Blot o PCR)."
        ),
        "reaccion_general": "Anticuerpo Muestra (IgG/IgM Anti-VIH) + Antígeno-Oro Coloidal ⟶ Migra por Capilaridad ⟶ Captura en Antígeno Fijo (Línea T: gp120/gp41/gp36) + Control (Línea C)",
        "reactivos": [
            {
                "Reactivo": "Cassette de Inmunoplaca VIH-1/2 (Membrana de Nitrocelulosa)",
                "Estabilidad / Escala": "Almacenable entre 2 °C y 30 °C (en sobre sellado)",
                "Preparación (Balanza Analítica y Micropipeta)": "Atemperar el cassette sellado a temperatura ambiente antes de abrir para evitar condensación de humedad sobre la nitrocelulosa."
            },
            {
                "Reactivo": "Buffer Diluyente de Corrimiento (PBS pH 7.4 + Tensioactivo)",
                "Estabilidad / Escala": "Almacenable — Preparación de 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "En caso de preparar 10 mL de buffer: pesar en balanza analítica 80.0 mg de NaCl, 14.4 mg de Na₂HPO₄, 2.4 mg de KH₂PO₄ y 2.0 mg de KCl; disolver en 8 mL de agua destilada, añadir 10 µL de Tween-20 con micropipeta y aforar a 10 mL."
            }
        ],
        "pasos": [
            {
                "title": "Preparación de Muestra",
                "desc": "Colocar el cassette en superficie plana. Si la sangre está coagulada, centrifugar previamente para obtener suero claro.",
                "conc": "Suero / Plasma / Sangre"
            },
            {
                "title": "Adición de Muestra (S)",
                "desc": "Con micropipeta, depositar exactamente de 10 a 20 µL de muestra en el pocillo de muestra (S).",
                "conc": "Alícuota: 10–20 µL"
            },
            {
                "title": "Adición de Buffer",
                "desc": "Agregar inmediatamente de 80 a 120 µL (2 a 3 gotas) de solución buffer diluyente e iniciar el cronómetro.",
                "conc": "Buffer: 80–120 µL"
            },
            {
                "title": "Lectura de Bandas",
                "desc": "Interpretar las líneas de color estrictamente entre los 15 y 20 minutos (no leer después de 20 minutos).",
                "conc": "Lectura: 15–20 min"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO REACCIONAL (POSITIVO DE TAMIZAJE)</span>
            <h4 style="margin:8px 0;">Aparición de 2 Bandas Coloreadas (Línea C + Línea T)</h4>
            <div style="width:220px; height:70px; margin:12px auto; background:#FFFFFF; border:3px solid #64748B; border-radius:8px; display:flex; align-items:center; justify-content:space-around; padding:0 20px;">
                <div style="text-align:center;">
                    <div style="font-size:0.75rem; font-weight:bold; color:#003366;">C</div>
                    <div style="width:10px; height:38px; background:#BE185D; border-radius:2px;"></div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:0.75rem; font-weight:bold; color:#003366;">T</div>
                    <div style="width:10px; height:38px; background:#BE185D; border-radius:2px;"></div>
                </div>
                <div style="width:28px; height:28px; border-radius:50%; background:#FEE2E2; border:2px solid #94A3B8; font-size:0.65rem; display:flex; align-items:center; justify-content:center; font-weight:bold;">S</div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Aspecto Visual:</b> Presencia de <b>dos líneas rojo-púrpura/magenta</b> (una en la zona de Control <b>C</b> y otra en la zona de Prueba <b>T1/T2</b>, incluso si la banda T es tenue). Se reporta como <b>REACCIONAL</b>.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NO REACTIVO (NEGATIVO) / INVÁLIDO</span>
            <h4 style="margin:8px 0;">1 Sola Banda en Control (C) | Sin Banda en C = Inválido</h4>
            <div style="width:220px; height:70px; margin:12px auto; background:#FFFFFF; border:3px solid #64748B; border-radius:8px; display:flex; align-items:center; justify-content:space-around; padding:0 20px;">
                <div style="text-align:center;">
                    <div style="font-size:0.75rem; font-weight:bold; color:#003366;">C</div>
                    <div style="width:10px; height:38px; background:#BE185D; border-radius:2px;"></div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:0.75rem; font-weight:bold; color:#003366;">T</div>
                    <div style="width:10px; height:38px; background:#F1F5F9; border:1px dashed #CBD5E1; border-radius:2px;"></div>
                </div>
                <div style="width:28px; height:28px; border-radius:50%; background:#FEE2E2; border:2px solid #94A3B8; font-size:0.65rem; display:flex; align-items:center; justify-content:center; font-weight:bold;">S</div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>No Reactivo (Negativo):</b> Aparece <b>únicamente la banda en C</b> y la zona T permanece totalmente blanca.<br>
                <b>Inválido:</b> Si no aparece la línea C (repetir en un cassette nuevo).
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "Enfermedades autoinmunes (lupus, artritis reumatoide por factores reumatoides), vacunaciones recientes (influenza, hepatitis B), embarazos múltiples (anticuerpos anti-HLA) o lectura después de los 20 minutos ('líneas fantasma' por oxidación/secado)."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "Período de ventana inmunológica (infección reciente menor a 3–4 semanas sin niveles detectables de anticuerpos) o inmunosupresión severa."},
            {"Tipo": "Interferencias", "Causa / Sustancia Interferente": "Hemólisis severa (tiñe el fondo de la membrana de nitrocelulosa de rojo oscuro impidiendo leer las bandas) y lipemia elevada (las grasas obstruyen los poros y detienen el flujo capilar)."}
        ]
    }
}


def render_ficha_forense_db(db_dict, header_title, key_prefix):
    if header_title:
        st.markdown(f"<h2 style='text-align:center;'>{header_title}</h2>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:#334155; margin-bottom:15px; font-weight:600;'>Seleccione el análisis</div>", unsafe_allow_html=True)

    c_l, c_m, c_r = st.columns([1, 2, 1])
    with c_m:
        prueba_sel = st.selectbox(
            "Seleccione el análisis",
            list(db_dict.keys()),
            index=0,
            label_visibility="collapsed",
            key=f"sel_{key_prefix}"
        )

    datos = db_dict[prueba_sel]

    # 1. Resumen del Fundamento y Reacción Química General
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>📖 Resumen del Fundamento y Reacción Química</h3>", unsafe_allow_html=True)
    render_html(f"""
    <div class="forensic-card" style="border-left: 5px solid #003366;">
        <h4 style="margin-top:0;">{datos['titulo']}</h4>
        <p style="font-size:0.94rem; line-height:1.5; margin-bottom:12px;">{datos['fundamento']}</p>
        <div style="background:#FFFFFF; padding:10px 14px; border-radius:6px; border:1px solid #CBD5E1; font-family:'Courier New', monospace; font-weight:bold; font-size:0.88rem; color:#002244;">
            {datos['reaccion_general']}
        </div>
    </div>
    """)

    # 2. Tabla de Reactivos con su Preparación (10 mL almacenables / 1 mL al momento)
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>🧪 Reactivos y Preparación (Escala 10 mL / 1 mL al Momento)</h3>", unsafe_allow_html=True)
    st.table(datos["reactivos"])

    # 3. Cómo se realiza la prueba (Procedimiento Paso a Paso)
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>🔄 Procedimiento de la Prueba</h3>", unsafe_allow_html=True)
    render_step_flow(datos["pasos"])

    # 4. Resultados Visuales (Positivo vs. Negativo: Cambio de Color o de Forma)
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>👁️ Resultados Visuales (Positivo vs. Negativo)</h3>", unsafe_allow_html=True)
    col_pos, col_neg = st.columns(2)
    with col_pos:
        render_html(datos["visual_pos_html"])
    with col_neg:
        render_html(datos["visual_neg_html"])

    # 5. Tabla de Interferencias
    st.markdown("<hr style='border-color:#D1D5DB;'><h3 style='text-align:center;'>⚠️ Tabla de Interferencias, Falsos Positivos y Falsos Negativos</h3>", unsafe_allow_html=True)
    st.table(datos["interferencias"])


def tab_analisis_toxicologicos():
    render_ficha_forense_db(ANALISIS_TOXICOLOGICOS_DB, "Toxicología", "tox")


def tab_analisis_serologicos():
    render_ficha_forense_db(ANALISIS_SEROLOGICOS_DB, "Serología", "sero")


# ==============================================================================
# PESTAÑA BALÍSTICA QUÍMICA: RESIDUOS DE DISPARO POR ARMA DE FUEGO (GSR)
# ==============================================================================

def render_analytical_note_gsr():
    st.markdown('''
    <div class="nota-card">
        <b>⚠️ NOTA PERICIAL DE CONTROL ANALÍTICO:</b> Antes de procesar cualquier indicio, correr obligatoriamente el <b>Blanco de Reactivos</b> para descartar contaminación química o degradación de reactivos. Toda interpretación de residuos de disparo debe considerar la <b>ventana temporal de 6 horas</b> (tras la cual los residuos disminuyen significativamente), la dinámica de dispersión de la nube (1.5 a 2.0 m) y la ausencia de especificidad intrínseca de los metales para hechos balísticos por posibles interferencias ocupacionales.
    </div>
    ''', unsafe_allow_html=True)


# ==============================================================================
# BASE DE DATOS DE ANÁLISIS DE RESIDUOS DE DISPARO POR ARMA DE FUEGO (GSR)
# ==============================================================================

ANALISIS_GSR_DB = {
    "1. Prueba de Griess (Nitritos — NO₂⁻)": {
        "titulo": "Prueba de Griess — Identificación de Nitritos (NO₂⁻)",
        "fundamento": (
            "La <b>Prueba de Griess</b> es la técnica por excelencia para la identificación de <b>iones nitrito (NO<sub>2</sub><sup>-</sup>)</b>, "
            "subproductos de la combustión de la pólvora. Se fundamenta en un proceso secuencial de <b>diazotación y acoplamiento azoico</b> en medio ácido:<br>"
            "• <b>Diazotación:</b> El ion nitrito reacciona con el <b>ácido sulfanílico</b> (amina aromática primaria) en medio de ácido acético, generando un catión diazonilo reactivo ([R-N≡N]⁺).<br>"
            "• <b>Acoplamiento Azoico:</b> La sal de diazonio ataca electrofílicamente al <b>clorhidrato de α-naftilamina</b>, produciendo un <b>azo-colorante</b> altamente conjugado que absorbe luz verde-azul y refleja un color <b>rosa brillante, rojo o magenta</b>.<br>"
            "• <b>Fisicoquímica:</b> Al percutir el fulminante, la combustión alcanza entre <b>1500 y 2000 °C en 0.2 segundos</b>, generando presiones de hasta <b>104 kPa</b> en el cañón que expulsan una nube de partículas de <b>5 a 100 µm</b>."
        ),
        "reaccion_general": "1) Ácido Sulfanílico + NO₂⁻ + 2H⁺ (CH₃COOH 10%) ⟶ Sal de Diazonio [R-N≡N]⁺   |   2) [R-N≡N]⁺ + α-Naftilamina ⟶ Azo-Colorante (Rosa Brillante / Magenta Instantáneo)",
        "reactivos": [
            {
                "Reactivo": "Reactivo 1 (Solución Ácida): Ácido Sulfanílico al 0.5% p/v en Ácido Acético al 10% v/v",
                "Estabilidad / Escala": "Almacenable en frasco ámbar y refrigeración — Escala 10 mL (o 100 mL)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: medir con micropipeta 1.0 mL (1000 µL) de ácido acético glacial y diluir a 10 mL con agua destilada (10% v/v). Pesar en balanza analítica 0.050 g (50.0 mg) de ácido sulfanílico y disolver en la solución. (Para 100 mL: disolver 0.5 g de ácido sulfanílico en 100 mL de ácido acético al 10%)."
            },
            {
                "Reactivo": "Reactivo 2 (Agente de Acoplamiento): Clorhidrato de α-Naftilamina al 0.5% p/v",
                "Estabilidad / Escala": "Almacenable en frasco ámbar en refrigeración — Escala 10 mL (Desechar si se torna oscuro)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: pesar en balanza analítica 0.050 g (50.0 mg) de clorhidrato de α-naftilamina y disolver en 10 mL de metanol o etanol al 95%. (Para 100 mL: disolver 0.5 g de clorhidrato de α-naftilamina en 100 mL de metanol o etanol al 95%)."
            },
            {
                "Reactivo": "Controles Obligatorios: Blanco de Reactivos, Control Positivo (NaNO₂ 0.1%) y Negativo",
                "Estabilidad / Escala": "Obligatorios por serie analítica — Escala 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "• Blanco: Reactivos 1 + 2 sobre tela o hisopo limpio (Incoloro/Blanco). • Control Positivo: Solución de Nitrito de Sodio (NaNO₂) al 0.1% p/v (10.0 mg en 10 mL) o residuo de disparo conocido ⟶ Rosa/Rojo intenso. • Control Negativo: Agua destilada o área sin disparo ⟶ Sin cambio."
            }
        ],
        "pasos": [
            {
                "title": "Humectación del Hisopo",
                "desc": "Humedecer un hisopo de algodón estéril con agua destilada o con 1 gota (50 µL) del Reactivo 1 (ácido sulfanílico).",
                "conc": "Hisopo + 50 µL R1/H₂O"
            },
            {
                "title": "Hisopado de Superficie",
                "desc": "Frotar enérgicamente la zona sospechosa. En vehículos o paredes, realizar hisopado periférico documentando cara externa (entrada) o interna (salida).",
                "conc": "Periferia del Orificio"
            },
            {
                "title": "Acoplamiento Azoico",
                "desc": "Si se usó agua, añadir 1 gota de Reactivo 1; inmediatamente agregar 1 gota (50 µL) de Reactivo 2 (clorhidrato de α-naftilamina).",
                "conc": "+ 50 µL Reactivo 2"
            },
            {
                "title": "Lectura Inmediata",
                "desc": "Observar instantáneamente el desarrollo cromático sobre el hisopo. El viraje inmediato a rosa brillante o magenta confirma nitritos.",
                "conc": "Rosa / Magenta Instantáneo"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO</span>
            <h4 style="margin:8px 0;">Puntos o Manchas de Color Rosa Brillante, Rojo o Magenta</h4>
            <div style="display:flex; justify-content:center; align-items:center; margin:12px 0;">
                <div style="width:200px; height:50px; border-radius:25px; background:linear-gradient(90deg, #F8FAFC 15%, #F43F5E 50%, #BE185D 100%); border:2px solid #94A3B8; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; font-size:0.84rem; text-shadow:1px 1px 2px #000; box-shadow: inset 0 0 8px rgba(0,0,0,0.2);">
                    Hisopo: Rosa Brillante / Magenta
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Aceptación:</b> 1) <b>Cromatismo:</b> Aparición de puntos o manchas de color <b>rosa brillante, rojo o magenta</b>; 2) <b>Persistencia:</b> El color es estable, aunque puede oscurecerse levemente por oxidación ambiental.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO / RECHAZO</span>
            <h4 style="margin:8px 0;">Ausencia de Color o Viraje Anómalo a Amarillo / Marrón</h4>
            <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin:12px 0;">
                <div style="flex:1; height:50px; border-radius:25px; background:#FFFFFF; border:2px dashed #94A3B8; display:flex; align-items:center; justify-content:center; color:#475569; font-weight:bold; font-size:0.8rem;">
                    Negativo: Incoloro / Blanco
                </div>
                <div style="flex:1; height:50px; border-radius:25px; background:linear-gradient(90deg, #FEF08A, #A16207); border:2px solid #94A3B8; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; font-size:0.8rem; text-shadow:1px 1px 2px #000;">
                    Rechazo: Amarillo / Marrón
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Rechazo:</b> 1) <b>Ausencia de color:</b> El soporte permanece sin cambio; 2) <b>Viraje a amarillo/marrón:</b> Indica reactivo oxidado o interferencia de materia orgánica no nitrada.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "1) Manipulación y/o contacto con fertilizantes agrícolas (nitritos/nitratos), orina e incluso maquillaje.\n2) Transferencia de residuos por forcejeo con el atacante.\n3) Conservadores de alimentos (embutidos/curados) y medicamentos vasodilatadores (nitroglicerina)."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "1) Detonación en área abierta: los residuos se dispersan con mayor facilidad por corrientes de aire.\n2) Presencia de aire, así como su dirección e intensidad.\n3) Tiempo transcurrido: después de 6 h los residuos disminuyen significativamente.\n4) Lavado o lluvia intensa (los nitritos son sales hidrosolubles eliminadas por el agua).\n5) Armas con buen ajuste no desprenden suficiente pólvora/residuos, especialmente con un solo disparo.\n6) Oxidación ambiental previa de nitritos (NO₂⁻) a nitratos (NO₃⁻)."}
        ]
    },

    "2. Prueba de Lunge (Nitratos y Oxidantes — NO₃⁻)": {
        "titulo": "Prueba de Lunge — Detección de Nitratos y Oxidantes (Difenilamina en Ácido Sulfúrico)",
        "fundamento": (
            "La <b>Prueba de Lunge</b> se basa en una reacción de <b>óxido-reducción en medio ácido fuerte por transferencia de electrones</b>. "
            "Es sumamente sensible para superficies duras, cristales, muros, paneles vehiculares y para el <b>interior del cañón del arma de fuego</b> para confirmar o descartar disparo reciente:<br>"
            "• <b>Oxidación de la Difenilamina:</b> El <b>ácido sulfúrico concentrado (H₂SO₄ al 95–98%)</b> activa los nitratos (NO₃⁻); la difenilamina se oxida primero a <b>difenilbenzidina</b> (incolora) y luego a un <b>catión quinoidal altamente conjugado</b>.<br>"
            "• <b>Cromóforo Azul:</b> El catión quinoidal resultante absorbe luz en el espectro visible, reflejando de forma inmediata un color <b>azul profundo, azul intenso o azul-violeta</b>.<br>"
            "• <b>Fisicoquímica:</b> Si la deflagración fue completa y muy eficiente, los nitratos pasan a nitritos, lo que explica resultados Griess (+) y Lunge (-); por el contrario, en muestras antiguas o en cañones con residuos oxidados predomina Lunge (+)."
        ),
        "reaccion_general": "2 C₁₂H₁₁N (Difenilamina) + NO₃⁻ + H₂SO₄ (conc. 95-98%) ⟶ Difenilbenzidina (Incolora) ⟶ Catión Quinoidal Conjugado (Color Azul Intenso / Violeta en < 5 s)",
        "reactivos": [
            {
                "Reactivo": "Reactivo de Lunge: Difenilamina al 0.5% p/v en H₂SO₄ Concentrado (95–98%)",
                "Estabilidad / Escala": "⚠️ ALTAMENTE CORROSIVO — Escala 10 mL (o 100 mL)",
                "Preparación (Balanza Analítica y Micropipeta)": "Trabajar en campana de extracción con guantes de nitrilo gruesos. Pesar en balanza analítica 0.050 g (50.0 mg) de difenilamina grado analítico (o 0.5 g para 100 mL). Añadir lentamente sobre los cristales 10 mL (o 100 mL) de H₂SO₄ concentrado (95–98%). La solución debe quedar completamente incolora; si se torna azul en el frasco está contaminada con nitratos del ambiente y debe desecharse."
            },
            {
                "Reactivo": "Controles Obligatorios: Blanco de Reactivos, Control Positivo (KNO₃ 1%) y Negativo",
                "Estabilidad / Escala": "Obligatorios por corrida analítica — Escala 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "• Blanco: Reactivo de Lunge sin muestra (Incoloro/Transparente). • Control Positivo: Solución de Nitrato de Potasio (KNO₃) al 1% p/v (100.0 mg en 10 mL de agua destilada) ⟶ Azul profundo inmediato. • Control Negativo: Agua destilada o algodón limpio ⟶ Incoloro / Sin cambio."
            }
        ],
        "pasos": [
            {
                "title": "Verificación del Reactivo",
                "desc": "En campana de extracción, comprobar que el Reactivo de Lunge esté totalmente incoloro antes de iniciar el ensayo.",
                "conc": "Blanco: Incoloro"
            },
            {
                "title": "Hisopado Periférico / Ánima",
                "desc": "Realizar hisopado enérgico en la periferia del orificio en superficies duras (vehículos, muros) o en el interior del cañón/ánima del arma.",
                "conc": "Zona de Impacto / Cañón"
            },
            {
                "title": "Adición de Lunge",
                "desc": "Añadir de 1 a 2 gotas (50–100 µL) del Reactivo de Lunge directamente sobre el hisopo con guantes de protección.",
                "conc": "50–100 µL Lunge"
            },
            {
                "title": "Lectura Rápida (< 5 s)",
                "desc": "Evaluar el viraje en menos de 5 segundos. La aparición de color azul profundo o violeta confirma nitratos u oxidantes.",
                "conc": "Lectura: < 5 segundos"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO</span>
            <h4 style="margin:8px 0;">Aparición Inmediata (&lt; 5 s) de Color Azul Intenso / Azul-Violeta</h4>
            <div style="display:flex; justify-content:center; align-items:center; margin:12px 0;">
                <div style="width:200px; height:50px; border-radius:25px; background:linear-gradient(90deg, #1E3A8A 15%, #1D4ED8 55%, #31102F 95%); border:2px solid #94A3B8; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; font-size:0.84rem; text-shadow:1px 1px 2px #000; box-shadow: inset 0 0 10px rgba(0,0,0,0.3);">
                    Azul Profundo / Violeta (&lt; 5 s)
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Aceptación:</b> 1) <b>Cromatismo:</b> Color <b>azul intenso o azul-negruzco</b>; 2) <b>Cinética:</b> Debe aparecer en <b>menos de 5 segundos</b>. Si aparece después de 1 minuto se debe a oxidación por el oxígeno del aire.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO / RECHAZO</span>
            <h4 style="margin:8px 0;">Incoloro, Carbonización Directa a Café/Negro o Blanco Azul</h4>
            <div style="display:flex; justify-content:center; align-items:center; gap:10px; margin:12px 0;">
                <div style="flex:1; height:50px; border-radius:10px; background:#FEF9C3; border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#003366; font-weight:bold; font-size:0.76rem; padding:4px;">
                    Negativo: Incoloro / Amarillo
                </div>
                <div style="flex:1; height:50px; border-radius:10px; background:linear-gradient(135deg, #451A03, #09090B); border:1px solid #CBD5E1; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-weight:bold; font-size:0.76rem; padding:4px;">
                    Rechazo: Carbonización Inmediata
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Rechazo:</b> 1) <b>Ausencia de color</b>; 2) <b>Carbonización directa</b> a café o negro (materia orgánica quemada por el H₂SO₄ sin pasar por el azul); 3) <b>Blanco contaminado:</b> reactivo azul antes de tocar la muestra.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "1) Si el arma no es limpiada con frecuencia o de manera correcta, existirán residuos acumulados en el ánima aunque no se haya disparado recientemente.\n2) Oxidantes fuertes: cloratos, permanganatos, dicromatos y sales férricas (óxido de hierro/herrumbre).\n3) Fertilizantes nitrogenados, residuos de tabaco/ceniza y productos de limpieza con cloro."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "1) Detección e interferencia por cenizas de cigarro.\n2) Composición y cantidad de la pólvora impregnada en el área de interés.\n3) Limpieza del arma con solventes derivados del petróleo que desplazan los nitratos.\n4) Deflagración extremadamente eficiente que redujo la totalidad de nitratos a nitritos."}
        ]
    },

    "3. Prueba de Walker (Patrón Térmico en Prendas)": {
        "titulo": "Prueba de Walker — Patrón de Dispersión Térmica en Prendas (Papel Fotográfico)",
        "fundamento": (
            "La <b>Prueba de Walker</b> es el procedimiento analítico clásico para identificar y mapear la <b>distribución topográfica de nitritos ('tatuaje' o rosa de deflagración)</b> "
            "en prendas de vestir alrededor del orificio de entrada para determinar la <b>distancia del disparo</b>:<br>"
            "• <b>Soporte Específico:</b> Utiliza <b>papel fotográfico brillante desensibilizado</b> (fijado y lavado para eliminar sales de plata, dejando solo la capa de gelatina que retiene los nitritos).<br>"
            "• <b>Transferencia Térmica con Ácido Acético:</b> Se coloca una compresa con <b>ácido acético (CH₃COOH al 10–20%)</b> sobre la prenda y se aplica calor de plancha (1 a 2 min). El vapor ácido arrastra los nitritos de la fibra textil a la gelatina sensibilizada con ácido sulfanílico y α-naftilamina.<br>"
            "• <b>Criterio de Distancia:</b> La prueba es presuntamente <b>positiva si el disparo fue próximo (&lt; 1 metro)</b> y presuntamente <b>negativa si la distancia fue mayor a 1 metro</b>."
        ),
        "reaccion_general": "Nitritos (en Fibras textiles) + Vapor CH₃COOH (10–20%) + Calor (1–2 min) ⟶ Gelatina de Papel (Ác. Sulfanílico + α-Naftilamina) ⟶ Patrón Concéntrico de Punteo Naranja-Rojizo / Rosa",
        "reactivos": [
            {
                "Reactivo": "Soporte: Papel Fotográfico Brillante Desensibilizado",
                "Estabilidad / Escala": "Preparación previa en cuarto oscuro — Insumo estructural",
                "Preparación (Balanza Analítica y Micropipeta)": "Fijar el papel fotográfico en baño de tiosulfato de sodio y lavar con agua destilada para eliminar las sales de plata fotosensibles. Impregnar secuencialmente con las Soluciones A y B y secar al abrigo de la luz."
            },
            {
                "Reactivo": "Solución A: Ácido Sulfanílico al 0.5% p/v en Agua Destilada",
                "Estabilidad / Escala": "Almacenable — Escala 10 mL (o 100 mL)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: pesar en balanza analítica 0.050 g (50.0 mg) de ácido sulfanílico y disolver en 10 mL de agua destilada con calor suave si es necesario. (Para 100 mL: disolver 0.5 g en 100 mL de agua destilada)."
            },
            {
                "Reactivo": "Solución B: Clorhidrato de α-Naftilamina al 0.5% p/v en Alcohol al 95%",
                "Estabilidad / Escala": "Almacenable en frasco ámbar — Escala 10 mL (o 100 mL)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: pesar en balanza analítica 0.050 g (50.0 mg) de clorhidrato de α-naftilamina y disolver en 10 mL de metanol o etanol al 95%. (Para 100 mL: disolver 0.5 g en 100 mL de alcohol al 95%)."
            },
            {
                "Reactivo": "Solución de Transferencia Térmica: Ácido Acético al 10% o 20% v/v",
                "Estabilidad / Escala": "Almacenable — Escala 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: medir con micropipeta 1.0 mL (1000 µL para el 10%) o 2.0 mL (2000 µL para el 20%) de ácido acético glacial y aforar a 10 mL con agua destilada."
            },
            {
                "Reactivo": "Controles Obligatorios de Papel: Blanco, Control Positivo (NaNO₂ 0.5%) y Negativo",
                "Estabilidad / Escala": "Obligatorios por cada pliego de papel revelado",
                "Preparación (Balanza Analítica y Micropipeta)": "• Blanco de Papel: Papel tratado + Ácido Acético + Calor sin prenda ⟶ Totalmente blanco. • Control Positivo: Tocar un borde con NaNO₂ al 0.5% p/v (50.0 mg en 10 mL) ⟶ Punto Rosa/Rojo instantáneo. • Control Negativo: Zona procesada con tela limpia ⟶ Blanco."
            }
        ],
        "pasos": [
            {
                "title": "Disposición del Papel",
                "desc": "Colocar el papel fotográfico desensibilizado y sensibilizado sobre una mesa plana con la cara de gelatina hacia arriba.",
                "conc": "Gelatina hacia Arriba"
            },
            {
                "title": "Montaje Cara a Cara",
                "desc": "Extender la prenda sin estirarla artificialmente y colocar la zona del orificio cara a cara contra el papel fotográfico.",
                "conc": "Orificio Cara a Cara"
            },
            {
                "title": "Compresa con Ácido Acético",
                "desc": "Colocar encima una gasa delgada humedecida uniformemente con ácido acético al 10% o 20% (sin exceso de líquido).",
                "conc": "Gasa CH₃COOH 10–20%"
            },
            {
                "title": "Transferencia Térmica",
                "desc": "Aplicar una plancha doméstica a temperatura media durante 1 a 2 minutos para arrastrar los nitritos hacia la gelatina.",
                "conc": "Plancha: 1 a 2 minutos"
            },
            {
                "title": "Revelado y Mapeo",
                "desc": "Retirar la prenda y evaluar la nitidez del 'tatuaje' de puntos rosados o naranja-rojizos para medir el diámetro de dispersión.",
                "conc": "Punteo Concéntrico"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO — "ROSA DE DEFLAGRACIÓN / TATUAJE"</span>
            <h4 style="margin:8px 0;">Punteo Nítido Naranja-Rojizo o Rosa Intenso Concéntrico</h4>
            <div style="display:flex; justify-content:center; align-items:center; margin:12px 0;">
                <div style="width:140px; height:110px; background:#FFFFFF; border:2px solid #64748B; border-radius:8px; display:flex; align-items:center; justify-content:center; box-shadow: inset 0 0 8px rgba(0,0,0,0.1); background-image: radial-gradient(circle at 50% 50%, #1E293B 7%, transparent 9%), radial-gradient(circle at 38% 42%, #E11D48 2.5%, transparent 3.5%), radial-gradient(circle at 62% 38%, #F43F5E 3%, transparent 4%), radial-gradient(circle at 44% 64%, #BE185D 2.5%, transparent 3.5%), radial-gradient(circle at 58% 60%, #E11D48 3%, transparent 4%), radial-gradient(circle at 32% 54%, #FB7185 2.5%, transparent 3.5%), radial-gradient(circle at 68% 52%, #E11D48 2.5%, transparent 3.5%), radial-gradient(circle at 50% 30%, #F43F5E 2.5%, transparent 3.5%), radial-gradient(circle at 48% 72%, #E11D48 2%, transparent 3%), radial-gradient(circle at 28% 35%, #FB7185 2%, transparent 3%), radial-gradient(circle at 72% 66%, #F43F5E 2%, transparent 3%);">
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Aceptación:</b> 1) <b>Cromatismo:</b> Puntos color <b>naranja-rojizo o rosa intenso</b>; 2) <b>Morfología ('El Tatuaje'):</b> Puntos nítidos con distribución concéntrica o dispersa alrededor del orificio (disparo próximo &lt; 1 m); 3) <b>Fijación:</b> Tatuaje indeleble en la gelatina.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO / RECHAZO</span>
            <h4 style="margin:8px 0;">Papel Blanco (&gt; 1 m), Mancha Borrosa o Quemadura Marrón</h4>
            <div style="display:flex; justify-content:center; align-items:center; gap:8px; margin:12px 0;">
                <div style="flex:1; height:60px; background:#FFFFFF; border:2px dashed #94A3B8; border-radius:6px; display:flex; align-items:center; justify-content:center; color:#475569; font-size:0.72rem; font-weight:bold; padding:4px;">
                    Negativo (&gt; 1 m): Blanco
                </div>
                <div style="flex:1; height:60px; background:radial-gradient(circle, #FDA4AF 30%, #FFF1F2 80%); border:1px solid #F43F5E; border-radius:6px; display:flex; align-items:center; justify-content:center; color:#881337; font-size:0.72rem; font-weight:bold; padding:4px;">
                    Rechazo: Sangrado Ácido
                </div>
                <div style="flex:1; height:60px; background:linear-gradient(135deg, #FEF3C7, #92400E); border:1px solid #78350F; border-radius:6px; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:0.72rem; font-weight:bold; padding:4px;">
                    Rechazo: Quemadura Térmica
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Rechazo:</b> 1) <b>Ausencia de puntos:</b> Papel blanco (disparo a más de 1 metro o sin residuos); 2) <b>Difuminación (efecto 'sangrado'):</b> Exceso de ácido acético o calor; 3) <b>Quemadura:</b> Papel marrón por plancha excesiva; 4) <b>Fondo rosa contaminado</b>.
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "1) Manipulación y/o contacto con fertilizantes, orina e incluso maquillaje.\n2) Transferencia de residuos por forcejeo con el atacante.\n(Nota técnica: estos contaminantes producen manchas difusas amorfas y NO el 'punteo' concéntrico característico de los granos de pólvora)."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "1) Detonación en área abierta (dispersión de residuos por corrientes de aire).\n2) Presencia de aire, así como su dirección e intensidad.\n3) Distancia al blanco (mayor a 1 metro).\n4) Tiempo transcurrido: después de 6 h los residuos disminuyen significativamente.\n5) Frotamiento mecánico de las prendas con otros objetos.\n6) Armas con buen ajuste no desprenden suficiente pólvora/residuos con un solo disparo."}
        ]
    },

    "4. Prueba de Rodizonato de Sodio (Plomo y Bario en Manos)": {
        "titulo": "Prueba de Rodizonato de Sodio — Plomo (Pb²⁺) y Bario (Ba²⁺) en Manos",
        "fundamento": (
            "La <b>Prueba de Rodizonato de Sodio</b> es el método químico forense para identificar metales pesados del fulminante —específicamente <b>Plomo (Pb<sup>2+</sup>)</b> y <b>Bario (Ba<sup>2+</sup>)</b>— "
            "que se vaporizan, funden y depositan sobre las manos del tirador (<i>'triángulo de la muerte': dorso y palma entre pulgar e índice</i>):<br>"
            "• <b>Sustitución de Harrison Gilroy:</b> Se utiliza Rodizonato de Sodio debido a que el antimonio no se puede determinar de forma rutinaria por la falta de reactivos específicos (yoduro de trifenilmetilarsonio), además de su toxicidad e inestabilidad.<br>"
            "• <b>Quelación Inicial (Buffer pH 2.8):</b> El rodizonato reacciona a pH 2.8 formando quelatos: con <b>Plomo (Pb²⁺)</b> da color <b>rojo escarlata / rosa intenso</b>, y con <b>Bario (Ba²⁺)</b> color <b>rojo-marrón</b>.<br>"
            "• <b>Confirmación Ácida Diferencial (HCl al 5%):</b> Al añadir HCl al 5%, el complejo de plomo <b>vira obligatoriamente a azul-violeta o morado</b>; por el contrario, el complejo de bario <b>se decolora / desaparece</b>.<br>"
            "• <b>Morfología Esférica al Estereoscopio (Obligatoria):</b> Se deben observar micropartículas con <b>forma esférica o globular</b> (metal fundido y solidificado a 1500–2000 °C) con un <b>núcleo metálico central</b> y un <b>halo reaccional ('corona')</b> por difusión capilar."
        ),
        "reaccion_general": "Pb²⁺/Ba²⁺ + Rodizonato (Buffer pH 2.8) ⟶ Quelato Rosa Escarlata (Pb) / Rojo-Marrón (Ba)  ⟶  (+ HCl 5%)  ⟶  Halo Azul-Violeta / Morado (Confirma Pb²⁺) | Decoloración (Ba²⁺)",
        "reactivos": [
            {
                "Reactivo": "Solución de Levantamiento: Ácido Sulfúrico (H₂SO₄) al 2% v/v + Telas libres de asbesto",
                "Estabilidad / Escala": "Almacenable — Escala 10 mL (4 fragmentos de tela blanca de algodón)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: medir con micropipeta 200 µL (0.2 mL) de H₂SO₄ concentrado y aforar a 10 mL con agua destilada. Cortar fragmentos de tela blanca libre de asbesto (un fragmento individual para palma y otro para dorso de cada mano)."
            },
            {
                "Reactivo": "Solución Amortiguadora: Buffer Tartrato a pH 2.8",
                "Estabilidad / Escala": "Almacenable — Escala 10 mL (o 100 mL)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: pesar en balanza analítica 0.190 g (190.0 mg) de bitartrato de potasio y 0.150 g (150.0 mg) de ácido tartárico; disolver hasta aforar a 10 mL con agua destilada. (Para 100 mL: disolver 1.9 g de bitartrato de potasio y 1.5 g de ácido tartárico en 100 mL de agua destilada)."
            },
            {
                "Reactivo": "Solución de Rodizonato de Sodio (C₆Na₂O₆ al ~0.2% p/v — Color 'Té Cargado')",
                "Estabilidad / Escala": "⚠️ PREPARAR AL MOMENTO — Escala 1 mL (Pierde sensibilidad en < 1 hora)",
                "Preparación (Balanza Analítica y Micropipeta)": "Disolver una pequeña cantidad (punta de espátula, ~2.0 mg) de rodizonato de sodio en 1000 µL (1.0 mL) de agua destilada recién hervida y enfriada hasta obtener un color 'té cargado' o naranja oscuro. Desechar si se torna verde o negro."
            },
            {
                "Reactivo": "Solución Confirmatoria: Ácido Clorhídrico (HCl) al 5% v/v",
                "Estabilidad / Escala": "Almacenable — Escala 10 mL (o 100 mL)",
                "Preparación (Balanza Analítica y Micropipeta)": "Para 10 mL: medir con micropipeta 500 µL (0.5 mL) de HCl concentrado y mezclar con 9.5 mL (9500 µL) de agua destilada. (Para 100 mL: mezclar 5 mL de HCl concentrado con 95 mL de agua destilada)."
            },
            {
                "Reactivo": "Controles Obligatorios: Blanco, Control Positivo de Plomo (Pb) y Negativo",
                "Estabilidad / Escala": "Obligatorios por corrida analítica — Escala 10 mL",
                "Preparación (Balanza Analítica y Micropipeta)": "• Blanco: Buffer pH 2.8 + Rodizonato sin muestra ⟶ Amarillo/Naranja pálido propio del reactivo. • Control Positivo (Pb): Solución de Nitrato de Plomo al 1% p/v (100.0 mg en 10 mL) ⟶ Rosa que vira a Azul/Violeta con HCl 5%. • Control Negativo: Algodón/tela limpia con agua ⟶ Naranja sin cambio."
            }
        ],
        "pasos": [
            {
                "title": "Levantamiento en Manos",
                "desc": "Humedecer un fragmento de tela con H₂SO₄ al 2% y frotar firmemente dorso y palma de cada mano (triángulo de la muerte).",
                "conc": "4 Telas (H₂SO₄ 2%)"
            },
            {
                "title": "Buffer pH 2.8 y Rodizonato",
                "desc": "Añadir sobre la tela 1 a 2 gotas (50–100 µL) de buffer pH 2.8 y enseguida 1 a 2 gotas de rodizonato recién preparado.",
                "conc": "pH 2.8 + Rodizonato"
            },
            {
                "title": "Estereoscopio (Morfología)",
                "desc": "Bajo luz oblicua, buscar micropartículas esféricas con núcleo metálico central y halo reaccional rosa escarlata (Pb²⁺) o rojo-marrón (Ba²⁺).",
                "conc": "Esfera + Halo Rosa"
            },
            {
                "title": "Confirmación con HCl 5%",
                "desc": "Añadir 1 gota de HCl al 5% sobre los puntos reactivos. Si el halo vira a azul-violeta se confirma Plomo; si se decolora es Bario.",
                "conc": "Viraje a Azul-Violeta"
            }
        ],
        "visual_pos_html": """
        <div class="forensic-card" style="border-top: 5px solid #0F766E;">
            <span class="badge-teal">RESULTADO POSITIVO A PLOMO (Pb²⁺) AL ESTEREOSCOPIO</span>
            <h4 style="margin:8px 0;">Micropartícula Esférica + Halo Rosa Escarlata ⟶ Viraje a Azul-Violeta con HCl 5%</h4>
            <div style="display:flex; justify-content:center; align-items:center; gap:18px; margin:12px 0;">
                <div style="text-align:center;">
                    <div style="width:85px; height:85px; border-radius:50%; background:radial-gradient(circle, #334155 16%, #E11D48 38%, #FDA4AF 65%, #FEF3C7 100%); border:2px solid #003366; margin:0 auto 4px auto; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"></div>
                    <div style="font-size:0.75rem; font-weight:bold; color:#003366;">1° pH 2.8: Halo Rosa (Pb)<br>/ Rojo-Marrón (Ba)</div>
                </div>
                <div style="font-size:1.5rem; font-weight:bold; color:#003366;">+ HCl 5% ⟶</div>
                <div style="text-align:center;">
                    <div style="width:85px; height:85px; border-radius:50%; background:radial-gradient(circle, #334155 16%, #4338CA 38%, #7E22CE 65%, #F8FAFC 100%); border:2px solid #003366; margin:0 auto 4px auto; box-shadow: 0 2px 6px rgba(0,0,0,0.2);"></div>
                    <div style="font-size:0.75rem; font-weight:bold; color:#003366;">2° Confirmación Pb²⁺:<br>Halo Azul-Violeta</div>
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios Obligatorios:</b> 1) <b>Secuencia Cromática:</b> Viraje obligatorio de Rosa a <b>Azul-Violeta</b> tras el HCl al 5% (el Bario se decolora); 2) <b>Morfología Esférica:</b> Partícula esférica o globular fundida con <b>núcleo metálico central y corona de difusión capilar</b>.
            </p>
        </div>
        """,
        "visual_neg_html": """
        <div class="forensic-card" style="border-top: 5px solid #C0392B;">
            <span class="badge-red">RESULTADO NEGATIVO / RECHAZO</span>
            <h4 style="margin:8px 0;">Color Naranja Natural, Mancha Difusa sin Esferas o Viraje Falso</h4>
            <div style="display:flex; justify-content:center; align-items:center; gap:8px; margin:12px 0;">
                <div style="flex:1; height:56px; border-radius:8px; background:#FDE68A; border:1px solid #D97706; display:flex; align-items:center; justify-content:center; color:#003366; font-size:0.72rem; font-weight:bold; padding:4px;">
                    Negativo: Naranja Propio
                </div>
                <div style="flex:1; height:56px; border-radius:8px; background:linear-gradient(90deg, #F472B6, #EC4899); border:1px dashed #9D174D; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:0.72rem; font-weight:bold; padding:4px;">
                    Rechazo: Mancha Difusa
                </div>
                <div style="flex:1; height:56px; border-radius:8px; background:linear-gradient(135deg, #065F46, #111827); border:1px solid #000; display:flex; align-items:center; justify-content:center; color:#FFFFFF; font-size:0.72rem; font-weight:bold; padding:4px;">
                    Rechazo: Reactivo Verde/Negro
                </div>
            </div>
            <p style="font-size:0.88rem; margin-bottom:0;">
                <b>Criterios de Rechazo:</b> 1) <b>Ausencia de cambio:</b> La tela mantiene el color naranja; 2) <b>Ausencia de morfología:</b> Mancha difusa sin esferas (contaminación por contacto); 3) <b>Viraje falso:</b> Azul directo sin pasar por rosa (hierro); 4) <b>Reactivo verde o negro</b> (degradado).
            </p>
        </div>
        """,
        "interferencias": [
            {"Tipo": "Falsos Positivos", "Causa / Sustancia Interferente": "1) Falso positivo a plomo en personas que desempeñan labores de contacto metálico: hojalateros, plomeros, mecánicos (soldaduras y baterías/acumuladores).\n2) El bario es componente común de raticidas y fuegos artificiales (pirotecnia).\n3) Transferencia de residuos por forcejeo con el atacante.\n4) Desaconsejado en prendas: botones, cierres y remaches metálicos o tintes textiles reaccionan con el rodizonato."},
            {"Tipo": "Falsos Negativos", "Causa / Sustancia Interferente": "1) Lavado de manos con agua y jabón o frotamiento de manos contra la ropa (eliminación mecánica de partículas).\n2) Tiempo transcurrido: después de 6 h los residuos disminuyen significativamente.\n3) Tamaño limitado de la muestra y bajo número de detonaciones (con un solo disparo disminuye la probabilidad).\n4) Armas de diseño cerrado o con buen ajuste (revólveres dejan más residuos que pistolas automáticas)."}
        ]
    }
}


# ==============================================================================
# RENDERIZADOR DE PRUEBAS DE BALÍSTICA QUÍMICA (GSR)
# ==============================================================================


def tab_analisis_gsr():
    render_ficha_forense_db(ANALISIS_GSR_DB, "", "gsr")
    render_analytical_note_gsr()



# ==============================================================================
# FUNCIÓN PRINCIPAL (MAIN)
# ==============================================================================


# ==============================================================================
# FUNCIÓN PRINCIPAL UNIFICADA (MAIN)
# ==============================================================================

def main():
    inject_custom_css()
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'pH_vs_Ionizacion_Comparada_Datos.csv')
    data = load_data(csv_path)

    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>Panel de Control</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #D1D5DB;'>", unsafe_allow_html=True)
        
        # 1. Elección de la página en el Panel de Control
        modulo_seleccionado = st.radio(
            "Seleccione el Área Forense:",
            ["⚗️ Análisis Químico", "🧪 Toxicología", "🔫 Residuos de Arma de Fuego"],
            index=0,
            key="sidebar_modulo_nav"
        )
        st.markdown("<hr style='border-color: #D1D5DB;'>", unsafe_allow_html=True)
        
        # 2. Parámetros de análisis químico: sólo fijos cuando se muestre Análisis Químico
        if modulo_seleccionado == "⚗️ Análisis Químico":
            st.markdown("<div style='font-size:0.92rem; font-weight:bold; color:#003366; margin-bottom:8px;'>🎯 Parámetros (Análisis Químico)</div>", unsafe_allow_html=True)
            sustancias_list = list(data.keys()) if data else []
            selected_sustancia = st.selectbox("🎯 Sustancia Objetivo (Analito)", sustancias_list, index=0) if sustancias_list else "Cocaína"
            selected_adulterante = st.selectbox("✂️ Sustancia de Corte", sustancias_list, index=1 if len(sustancias_list) > 1 else 0) if sustancias_list else "Fenacetina"
            selected_ph = st.slider("🧪 pH del Medio Extractor", 0.0, 14.0, 7.0, 0.1)
            st.markdown("<hr style='border-color: #D1D5DB;'>", unsafe_allow_html=True)

        st.markdown(
            "<div style=\"background-color: #E5E7EB; padding: 15px; border-radius: 8px; border: 1px solid #D1D5DB; text-align: center; font-size: 0.85rem; color: #003366;\">"
            "<b>Realizado por:</b><br/>QFB Edgar Oswaldo Díaz Andrade"
            "</div>", 
            unsafe_allow_html=True
        )

    # ==========================================================================
    # DESPLIEGUE SEGÚN LA PÁGINA SELECCIONADA EN EL PANEL DE CONTROL
    # ==========================================================================
    if modulo_seleccionado == "⚗️ Análisis Químico":
        st.markdown("<h1>Análisis Químico de Sustancias</h1>", unsafe_allow_html=True)
        if not data:
            st.error("Error crítico: Dataset no disponible.")
            return

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 1. Ficha Comparativa", 
            "🌳 2. Árbol de Decisión", 
            "🧪 3. Pruebas Presuntivas y Reactivos",
            "⚗️ 4. Fisicoquímica L-L", 
            "🔬 5. Simulador Manual L-L"
        ])
        with tab1: tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph)
        with tab2: tab2_arbol_decision()
        with tab3: tab3_reactivos()
        with tab4: tab4_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph)
        with tab5: tab5_simulador_manual()

        # Referencias completas (Clarke's y UNODC) para Análisis Químico
        st.markdown('''
        <div class="footer">
            <b>Referencias Bibliográficas:</b><br/>
            [1] Moffat AC, Osselton MD, Widdop B, Watts J, editores. <i>Clarke\'s Analysis of Drugs and Poisons: In pharmaceuticals, body fluids and postmortem material</i>. 4a ed. Londres: Pharmaceutical Press; 2011.<br/>
            [2] Oficina de las Naciones Unidas contra la Droga y el Delito (UNODC). <i>Métodos para el ensayo inmediato de drogas de uso indebido</i>. Manual para laboratorios nacionales de estupefacientes. ST/NAR/13/Rev.1. Naciones Unidas: Nueva York; 2006.<br/>
            <span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
        </div>
        ''', unsafe_allow_html=True)

    elif modulo_seleccionado == "🧪 Toxicología":
        # Página de Toxicología
        st.markdown("<h1>Toxicología Forense</h1>", unsafe_allow_html=True)
        
        # División de la página de Toxicología en tres: Toxicología, CG-MS HS y Serología
        sub_tox1, sub_tox2, sub_tox3 = st.tabs([
            "🔬 Toxicología",
            "📊 CG-MS HS",
            "🩸 Serología"
        ])
        
        with sub_tox1:
            tab_analisis_toxicologicos()
            
        with sub_tox2:
            # CG-MS HS dividido en dos: Preparación de Reactivos y Calculadora
            cgms_tab1, cgms_tab2 = st.tabs([
                "🧪 Preparación de Reactivos", 
                "🧮 Calculadora"
            ])
            with cgms_tab1:
                tab_cgms_preparacion()
            with cgms_tab2:
                tab_cgms_calculadora()
                
        with sub_tox3:
            tab_analisis_serologicos()

        # Referencias para Toxicología (únicamente Clarke's, sin UNODC)
        st.markdown('''
        <div class="footer">
            <b>Referencias Bibliográficas:</b><br/>
            [1] Moffat AC, Osselton MD, Widdop B, Watts J, editores. <i>Clarke\'s Analysis of Drugs and Poisons: In pharmaceuticals, body fluids and postmortem material</i>. 4a ed. Londres: Pharmaceutical Press; 2011.<br/>
            <span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
        </div>
        ''', unsafe_allow_html=True)

    else:
        # Página de Residuos de Disparo por Arma de Fuego (GSR)
        st.markdown("<h1>Residuos de Disparo por Arma de Fuego (GSR)</h1>", unsafe_allow_html=True)
        tab_analisis_gsr()

        st.markdown('''
        <div class="footer">
            <b>Referencias Bibliográficas:</b><br/>
            [1] González Lozano, R. U., Rebollar López, E. J., & Pérez Cabrera, M. F. (2023). <i>Falsos positivos y falsos negativos de las técnicas colorimétricas para la identificación de residuos provenientes de armas de fuego</i>. <b>Revista Mexicana de Ciencias Penales</b> (INACIPE), 6(20), 123–136. DOI: 10.57042/rmcp.v6i20.635<br/>
            <span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
        </div>
        ''', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
