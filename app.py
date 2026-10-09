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
    
    /* Tablas con fondo gris y texto azul oscuro */
    table { 
        width: 100%; 
        margin: 0 auto; 
        text-align: center; 
        transition: all 0.3s ease-in-out; 
        background-color: #E5E7EB; 
        border: 1px solid #D1D5DB; 
        border-radius: 8px; 
        color: #003366; 
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
    
    img:hover, table:hover { 
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
    is_multi = 'anf' in char_low or 'dip' in char_low
    
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

def get_solvent(info, pka, current_ph):
    pkas = parse_pkas(pka, info.get('Carácter', 'Base'))
    pka_val = pkas[0] if pkas else 7.0
    val = "No especificado"
    if current_ph < pka_val:
        for k, v in info.items():
            if '<' in k and 'Disolvente' in k and v:
                val = v.strip()
                break
    else:
        for k, v in info.items():
            if '>' in k and 'Disolvente' in k and v:
                val = v.strip()
                break
                
    # Reemplazar leyenda inmiscible por el solvente real (Agua / Solvente orgánico)
    val_low = val.lower()
    if 'inmiscible' in val_low or 'no extraible' in val_low or 'no extraíble' in val_low:
        if 'agua' in val_low or 'ionizada' in val_low:
            return "Agua (Fase Acuosa)"
        else:
            return "Agua"
    return val

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
    estado = "Forma Ionizada" if obj_is_ion >= 50.0 else "Forma Libre (Neutra)"
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
        if num and num != 'N/A':
            picos_ir.append({"Vibración (cm⁻¹)": num})
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
        if ion_val and ion_val != 'N/A':
            iones.append({"Relación m/z": ion_val})
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

def generate_extraction_protocol(name_obj, char_obj, pka_obj_str, solv_obj_acid, solv_obj_basic,
                                 name_cut, char_cut, pka_cut_str, solv_cut_acid, solv_cut_basic):
    if name_obj.strip().lower() == name_cut.strip().lower():
        st.info("ℹ️ Seleccione una sustancia objetivo y un adulterante distintos para calcular el protocolo de extracción.")
        return

    pkas_obj = parse_pkas(pka_obj_str, char_obj)
    pkas_cut = parse_pkas(pka_cut_str, char_cut)
    
    gcms_note_html = """<li style="margin-top:12px; background-color:#FFFFFF; padding:12px; border-radius:6px; border:1px solid #CBD5E1; border-left:4px solid #003366; text-align:left; list-style-type:none;"><b>⚠️ NOTA CRÍTICA PARA GC-MS:</b> Para el análisis por GC-MS, se debe utilizar <b>cloroformo de alta pureza</b> para reconstituir el extracto seco. Es indispensable <b>eliminar con extremo cuidado el agua agregando sulfato de sodio anhidro (Na<sub>2</sub>SO<sub>4</sub>)</b> y <b>filtrar minuciosamente</b> para eliminar todo residuo acuoso, protegiendo así la columna capilar y optimizando la ionización. Asimismo, la muestra reconstituida debe <b>diluirse adecuadamente (ej. proporción 1:50 a 1:100 o concentración ≤ 1 mg/mL)</b> antes de la inyección para evitar la <b>saturación del filamento y del detector de masas (MSD)</b>.</li>"""

    if not pkas_obj and not pkas_cut:
        protocol_html = f"""<div class="forensic-card">
<h4 style="color:#003366 !important; margin-top:0;">Protocolo de Extracción Directa por Solvente</h4>
<p>Ninguna de las sustancias presenta equilibrios ácido-base relevantes en el intervalo analítico de pH (sustancias neutras). La separación no depende del pH acuoso.</p>
<ul>
<li><b>Extracción diferencial:</b> Evaluar separación por solubilidad diferencial directa usando solvente afín (ej. {solv_obj_basic}).</li>
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
    
    pka_cut_val = pkas_cut[0] if pkas_cut else 7.0
    pka_obj_val = pkas_obj[0] if pkas_obj else 7.0
    
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

    if clean_intervals:
        clean_s, clean_e, _ = clean_intervals[0]
        opt_clean_ph = (clean_s + clean_e) / 2.0
        solv_cut_opt = solv_cut_acid if opt_clean_ph < pka_cut_val else solv_cut_basic
        
        char_obj_lower = char_obj.lower()
        if 'anf' in char_obj_lower or 'dip' in char_obj_lower:
            pi_val = sum(pkas_obj) / len(pkas_obj) if pkas_obj else 7.0
            step2_action = f"Ajustar cuidadosamente el pH a su punto de máxima neutralidad (aprox. <b>pH {pi_val:.1f}</b>) para liberar y precipitar/extraer al analito ({name_obj})."
            solv_step2 = solv_obj_basic if solv_obj_basic != "No especificado" else solv_obj_acid
        elif 'ácido' in char_obj_lower or 'acido' in char_obj_lower:
            target_ph = max(0.0, pka_obj_val - 2.0)
            step2_action = f"Acidificar fuertemente la fase acuosa a <b>pH &lt; {target_ph:.1f}</b> para protonar y volver neutro al analito ({name_obj})."
            solv_step2 = solv_obj_acid if solv_obj_acid != "No especificado" else "Cloroformo / Acetato de etilo"
        else: # Base
            target_ph = min(14.0, pka_obj_val + 2.0)
            step2_action = f"Alcalinizar la fase acuosa a <b>pH &gt; {target_ph:.1f}</b> para desprotonar y liberar al analito ({name_obj}) como base libre."
            solv_step2 = solv_obj_basic if solv_obj_basic != "No especificado" else "Cloroformo / Diclorometano"

        protocol_html = f"""<div class="forensic-card">
<h4 style="color: #003366 !important; margin-top:0;">PASO 1: Eliminación Selectiva del Adulterante ({name_cut})</h4>
<p>Ajustar el pH de la disolución acuosa a <b>pH {opt_clean_ph:.1f}</b> (dentro de la ventana de lavado).</p>
<ul>
<li>A este pH, el adulterante <b>{name_cut}</b> se encuentra en forma neutra (&gt;90%), mientras que el analito objetivo <b>{name_obj}</b> permanece ionizado (&gt;90%) retenido en la fase acuosa.</li>
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
        dir_s, dir_e, _ = direct_intervals[0]
        opt_dir_ph = (dir_s + dir_e) / 2.0
        solv_step1 = solv_obj_acid if opt_dir_ph < pka_obj_val else solv_obj_basic
        if solv_step1 == "No especificado": solv_step1 = "Cloroformo / Diclorometano"

        protocol_html = f"""<div class="forensic-card">
<h4 style="color: #003366 !important; margin-top:0;">PASO 1: Extracción Directa del Analito ({name_obj})</h4>
<p>Ajustar el pH de la disolución acuosa a <b>pH {opt_dir_ph:.1f}</b> (dentro de la ventana de extracción).</p>
<ul>
<li>A este pH, el analito <b>{name_obj}</b> se encuentra en su forma neutra (&gt;90%), mientras que el adulterante <b>{name_cut}</b> permanece ionizado (&gt;90%) y queda retenido en la fase acuosa.</li>
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
    "marquis": [
        {"test": "Prueba de Marquis", "color_desc": "Verde brillante / Esmeralda", "target": "2C-B", "bg": "#27AE60"},
        {"test": "Prueba de Marquis", "color_desc": "Negro violáceo inmediato", "target": "MDMA / MDA (Éxtasis)", "bg": "#1A1A1A"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja → Marrón rojizo", "target": "Metanfetamina", "bg": "linear-gradient(to right, #FF8C00, #D35400, #5C2C16)"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja brillante → Rojo anaranjado", "target": "Anfetamina", "bg": "#E67E22"},
        {"test": "Prueba de Marquis", "color_desc": "Naranja claro / Ocre", "target": "Fentanilo", "bg": "#D4AC0D"},
        {"test": "Prueba de Marquis", "color_desc": "Púrpura / Violeta oscuro", "target": "Opiáceos (Heroína / Morfina)", "bg": "#5B2C6F"},
        {"test": "Prueba de Marquis", "color_desc": "Violeta a Púrpura", "target": "Codeína", "bg": "#4A235A"},
        {"test": "Prueba de Marquis", "color_desc": "Rosa tenue a Rojo lento con calor", "target": "Salicilatos (Aspirina)", "bg": "#F1948A"}
    ],
    "mecke": [
        {"test": "Prueba de Mecke", "color_desc": "Verde azulado profundo virando a Negro", "target": "Heroína / Morfina / Codeína", "bg": "#117A65"},
        {"test": "Prueba de Mecke", "color_desc": "Verde oscuro a Verde azulado", "target": "MDMA / MDA", "bg": "#145A32"},
        {"test": "Prueba de Mecke", "color_desc": "Marrón a Pardo rojizo", "target": "Mescalina / Fenetilaminas", "bg": "#B9770E"}
    ],
    "simon": [
        {"test": "Prueba de Simon", "color_desc": "Azul cobalto intenso inmediato", "target": "Metanfetamina (Amina Secundaria)", "bg": "#0047AB"},
        {"test": "Prueba de Simon", "color_desc": "Azul cobalto intenso inmediato", "target": "MDMA (Amina Secundaria)", "bg": "#0047AB"},
        {"test": "Prueba de Simon", "color_desc": "Sin reacción / Incoloro o pálido", "target": "Anfetamina / MDA (Aminas Primarias - Negativo)", "bg": "#D1D5DB"}
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
        {"test": "Prueba de Mandelin", "color_desc": "Verde oliva a Verde oscuro", "target": "Metanfetamina / Anfetamina", "bg": "#2E4F28"},
        {"test": "Prueba de Mandelin", "color_desc": "Azul grisáceo a Violeta oscuro", "target": "Opiáceos (Morfina / Heroína)", "bg": "#2E4053"},
        {"test": "Prueba de Mandelin", "color_desc": "Naranja rojizo tenue", "target": "Ketamina", "bg": "#E59866"}
    ],
    "liebermann": [
        {"test": "Prueba de Liebermann", "color_desc": "Negro / Marrón oscuro", "target": "Heroína / Morfina", "bg": "#1C2833"},
        {"test": "Prueba de Liebermann", "color_desc": "Violeta a Púrpura", "target": "Paracetamol / Fenacetina", "bg": "#6C3483"},
        {"test": "Prueba de Liebermann", "color_desc": "Amarillo tenue a Incoloro", "target": "Cocaína", "bg": "#F9E79F"}
    ],
    "férrico": [
        {"test": "Prueba de Cloruro Férrico", "color_desc": "Violeta púrpura intenso", "target": "Salicilatos (tras hidrólisis) / Fenoles", "bg": "#512E5F"}
    ],
    "ferrico": [
        {"test": "Prueba de Cloruro Férrico", "color_desc": "Violeta púrpura intenso", "target": "Salicilatos (tras hidrólisis) / Fenoles", "bg": "#512E5F"}
    ],
    "mcnally": [
        {"test": "Prueba de McNally", "color_desc": "Rojo cereza / Rojo vino en interfase caliente", "target": "Salicilatos", "bg": "#922B21"}
    ],
    "amálico": [
        {"test": "Prueba de Murexida", "color_desc": "Púrpura rojizo brillante con vapor de amonio", "target": "Xantinas (Cafeína)", "bg": "#7D3C98"}
    ],
    "murexida": [
        {"test": "Prueba de Murexida", "color_desc": "Púrpura rojizo brillante con vapor de amonio", "target": "Xantinas (Cafeína)", "bg": "#7D3C98"}
    ],
    "zimmerman": [
        {"test": "Prueba de Zimmerman", "color_desc": "Rosa rojizo / Púrpura rojizo", "target": "Benzodiazepinas (Diazepam)", "bg": "#C0392B"}
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
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #003366;"><h4 style="color: #003366 !important; margin-top:0;">🎯 Analito Objetivo: {selected_sustancia}</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {char_obj}</p><p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_obj}</span></p><p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_obj}</p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_obj_curr:.2f}%</span></p><p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_obj_curr:.2f}%</span></p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #C0392B;"><h4 style="color: #C0392B !important; margin-top:0;">✂️ Adulterante: {selected_adulterante}</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {char_cut}</p><p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_cut}</span></p><p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_cut}</p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_cut_curr:.2f}%</span></p><p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_cut_curr:.2f}%</span></p></div>', unsafe_allow_html=True)
        
    chart_data = []
    for ph_val in [x/10.0 for x in range(0, 141, 2)]:
        i_o, n_o = calculate_ionization(pka_obj, char_obj, ph_val)
        i_c, n_c = calculate_ionization(pka_cut, char_cut, ph_val)
        chart_data.extend([
            {"pH": ph_val, "% Especie": i_o, "Sustancia": "Objetivo (Ionizado - Agua)", "Categoría": "Objetivo"}, 
            {"pH": ph_val, "% Especie": n_o, "Sustancia": "Objetivo (Neutro - Orgánico)", "Categoría": "Objetivo"}, 
            {"pH": ph_val, "% Especie": i_c, "Sustancia": "Corte (Ionizado - Agua)", "Categoría": "Adulterante"}, 
            {"pH": ph_val, "% Especie": n_c, "Sustancia": "Corte (Neutro - Orgánico)", "Categoría": "Adulterante"}
        ])
        
    point_data = [
        {"pH": selected_ph, "% Especie": i_obj_curr, "Sustancia": "Objetivo (Ionizado - Agua)", "Categoría": "Objetivo"}, 
        {"pH": selected_ph, "% Especie": n_obj_curr, "Sustancia": "Objetivo (Neutro - Orgánico)", "Categoría": "Objetivo"}, 
        {"pH": selected_ph, "% Especie": i_cut_curr, "Sustancia": "Corte (Ionizado - Agua)", "Categoría": "Adulterante"}, 
        {"pH": selected_ph, "% Especie": n_cut_curr, "Sustancia": "Corte (Neutro - Orgánico)", "Categoría": "Adulterante"}
    ]
    
    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo de la Especie", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=['Objetivo (Ionizado - Agua)', 'Objetivo (Neutro - Orgánico)', 'Corte (Ionizado - Agua)', 'Corte (Neutro - Orgánico)'], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=alt.Legend(title="Especies", titleColor="#003366", labelColor="#003366", orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == 'Adulterante', alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#fff", strokeWidth=2).encode(
        x='pH:Q', y='% Especie:Q', 
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=['Objetivo (Ionizado - Agua)', 'Objetivo (Neutro - Orgánico)', 'Corte (Ionizado - Agua)', 'Corte (Neutro - Orgánico)'], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=None), 
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
    is_diprotic = 'dipr' in char_low
    
    if is_diprotic and len(pkas) < 2:
        return False, [], f"⚠️ Ha seleccionado el carácter 'Diprótico' para {label}: Debe ingresar dos equilibrios en el formato adecuado '(ph1, ph2)' o '(pKa1, pKa2)' con coma y espacio (ejemplo: '1.5, 10.5')."
        
    if len(pkas) >= 2 and not is_diprotic:
        return False, [], f"⚠️ Ha ingresado dos valores para {label}: Para modelar ambos equilibrios en la curva de especiación, seleccione el carácter 'Diprótico' en el menú desplegable."

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
        man_char_obj = st.selectbox("Carácter Químico", ["Base débil", "Ácido débil", "Diprótico"], index=0, key="m_c_obj")
        man_pka_obj = st.text_input("pKa (uno o dos valores, ej: 8.6 o 1.5, 10.5)", value="8.6", key="m_p_obj")
        man_solv_obj_acid = st.text_input("Disolvente a pH < pKa (Medio Ácido)", value="Agua (Fase Acuosa)", key="m_s_oa")
        man_solv_obj_base = st.text_input("Disolvente a pH > pKa (Medio Básico)", value="Cloroformo / Diclorometano", key="m_s_ob")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='forensic-card' style='border-left: 4px solid #C0392B;'><h4 style='color:#C0392B !important; margin-top:0;'>✂️ Parámetros del Adulterante (Corte)</h4>", unsafe_allow_html=True)
        man_name_cut = st.text_input("Nombre del Adulterante", value="Fenacetina", key="m_n_cut")
        man_char_cut = st.selectbox("Carácter Químico", ["Base débil", "Ácido débil", "Diprótico"], index=1, key="m_c_cut")
        man_pka_cut = st.text_input("pKa (uno o dos valores, ej: 2.2 o 4.4, 5.2)", value="2.2", key="m_p_cut")
        man_solv_cut_acid = st.text_input("Disolvente a pH < pKa (Medio Ácido)", value="Diclorometano", key="m_s_ca")
        man_solv_cut_base = st.text_input("Disolvente a pH > pKa (Medio Básico)", value="Éter etílico", key="m_s_cb")
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
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #003366;"><h4 style="color: #003366 !important; margin-top:0;">🎯 {man_name_obj} (pH {man_ph:.1f})</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {man_char_obj} | <b>pKa:</b> <span class="numeric-val">{man_pka_obj}</span></p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_obj:.2f}%</span></p><p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_obj:.2f}%</span></p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="forensic-card" style="border-left: 4px solid #C0392B;"><h4 style="color: #C0392B !important; margin-top:0;">✂️ {man_name_cut} (pH {man_ph:.1f})</h4><p style="margin-bottom:5px;"><b>Carácter:</b> {man_char_cut} | <b>pKa:</b> <span class="numeric-val">{man_pka_cut}</span></p><hr style="border-color:#D1D5DB; margin: 10px 0;"><p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_cut:.2f}%</span></p><p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_cut:.2f}%</span></p></div>', unsafe_allow_html=True)

    chart_data = []
    for p in range(0, 141, 2):
        ph_val = p / 10.0
        io, no = calculate_ionization(man_pka_obj, man_char_obj, ph_val)
        ic, nc = calculate_ionization(man_pka_cut, man_char_cut, ph_val)
        chart_data.extend([
            {"pH": ph_val, "% Especie": io, "Sustancia": f"{man_name_obj} (Ionizado - Agua)", "Categoría": "Objetivo"},
            {"pH": ph_val, "% Especie": no, "Sustancia": f"{man_name_obj} (Neutro - Orgánico)", "Categoría": "Objetivo"},
            {"pH": ph_val, "% Especie": ic, "Sustancia": f"{man_name_cut} (Ionizado - Agua)", "Categoría": "Adulterante"},
            {"pH": ph_val, "% Especie": nc, "Sustancia": f"{man_name_cut} (Neutro - Orgánico)", "Categoría": "Adulterante"}
        ])
        
    point_data = [
        {"pH": man_ph, "% Especie": i_obj, "Sustancia": f"{man_name_obj} (Ionizado - Agua)", "Categoría": "Objetivo"},
        {"pH": man_ph, "% Especie": n_obj, "Sustancia": f"{man_name_obj} (Neutro - Orgánico)", "Categoría": "Objetivo"},
        {"pH": man_ph, "% Especie": i_cut, "Sustancia": f"{man_name_cut} (Ionizado - Agua)", "Categoría": "Adulterante"},
        {"pH": man_ph, "% Especie": n_cut, "Sustancia": f"{man_name_cut} (Neutro - Orgánico)", "Categoría": "Adulterante"}
    ]
    
    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo de la Especie", axis=alt.Axis(gridColor="#E2E8F0", labelColor="#003366", titleColor="#003366")),
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=[f"{man_name_obj} (Ionizado - Agua)", f"{man_name_obj} (Neutro - Orgánico)", f"{man_name_cut} (Ionizado - Agua)", f"{man_name_cut} (Neutro - Orgánico)"], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=alt.Legend(title="Especies", titleColor="#003366", labelColor="#003366", orient="bottom")),
        strokeDash=alt.condition(alt.datum.Categoría == 'Adulterante', alt.value([5, 5]), alt.value([0]))
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#fff", strokeWidth=2).encode(
        x='pH:Q', y='% Especie:Q',
        color=alt.Color('Sustancia:N', scale=alt.Scale(domain=[f"{man_name_obj} (Ionizado - Agua)", f"{man_name_obj} (Neutro - Orgánico)", f"{man_name_cut} (Ionizado - Agua)", f"{man_name_cut} (Neutro - Orgánico)"], range=['#003366', '#D97706', '#C0392B', '#4B5563']), legend=None),
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
        st.markdown("<hr style='border-color: #D1D5DB;'>", unsafe_allow_html=True)
        sustancias_list = list(data.keys())
        selected_sustancia = st.selectbox("🎯 Sustancia Objetivo (Analito)", sustancias_list, index=0)
        selected_adulterante = st.selectbox("✂️ Sustancia de Corte", sustancias_list, index=1 if len(sustancias_list) > 1 else 0)
        st.markdown("<br>", unsafe_allow_html=True)
        selected_ph = st.slider("🧪 pH del Medio Extractor", 0.0, 14.0, 7.0, 0.1)
        st.markdown("<br><br><br><div style=\"background-color: #E5E7EB; padding: 15px; border-radius: 8px; border: 1px solid #D1D5DB; text-align: center; font-size: 0.8rem; color: #003366;\"><b>Realizado por:</b><br/>QFB Edgar Oswaldo Díaz Andrade<br/><br/><span style=\"color:#334155;\">Herramienta interactiva para perfilación presuntiva e instrumental.</span></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 1. Ficha Comparativa", 
        "🌳 2. Árbol de Decisión", 
        "🧪 3. Preparación de Reactivos",
        "⚗️ 4. Fisicoquímica L-L", 
        "🔬 5. Simulador Manual L-L"
    ])
    with tab1: tab1_comparativa(data, selected_sustancia, selected_adulterante, selected_ph)
    with tab2: tab2_arbol_decision()
    with tab3: tab3_reactivos()
    with tab4: tab4_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph)
    with tab5: tab5_simulador_manual()

    st.markdown('''
    <div class="footer">
        <b>Referencias Bibliográficas:</b><br/>
        [1] Moffat AC, Osselton MD, Widdop B, Watts J, editores. <i>Clarke's Analysis of Drugs and Poisons: In pharmaceuticals, body fluids and postmortem material</i>. 4a ed. Londres: Pharmaceutical Press; 2011.<br/>
        [2] Oficina de las Naciones Unidas contra la Droga y el Delito (UNODC). <i>Métodos para el ensayo inmediato de drogas de uso indebido</i>. Manual para laboratorios nacionales de estupefacientes. ST/NAR/13/Rev.1. Naciones Unidas: Nueva York; 2006.<br/>
                <span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == '__main__':
    main()