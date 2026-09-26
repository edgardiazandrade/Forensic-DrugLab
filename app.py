import streamlit as st
import csv
import os
import re
import math
import unicodedata
import altair as alt

st.set_page_config(page_title="Plataforma Pericial de Química Forense (PPQF)", layout="wide", initial_sidebar_state="expanded")

def inject_custom_css():
    st.markdown("""
    <style>
    /* Global Theme Overrides */
    .stApp { background-color: #1E222B; color: #E1E4EA; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    [data-testid="stSidebar"] { background-color: #171A21 !important; }
    h1, h2, h3, h4 { color: #9E9E9E !important; text-shadow: none; }
    .forensic-card { background-color: #262C38; border: 1px solid #3A4252; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease-in-out; }
    .forensic-card:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4); border: 1px solid #4A5568; }
    .numeric-val { font-family: 'Courier New', Courier, monospace; color: #E1E4EA; font-weight: bold; }
    .color-box { height: 50px; width: 100%; border-radius: 6px; margin-bottom: 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); border: 1px solid #111; }
    .biphasic-tube { height: 70px; width: 100%; border-radius: 6px; display: flex; flex-direction: column; overflow: hidden; border: 1px solid #111; box-shadow: inset 0 0 10px rgba(0,0,0,0.5); margin-bottom: 12px; }
    .biphasic-top { height: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #fff; text-shadow: 1px 1px 2px #000; border-bottom: 1px solid rgba(255,255,255,0.2); }
    .biphasic-bottom { height: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; color: #fff; text-shadow: 1px 1px 2px #000; }
    .footer { text-align: center; padding: 20px; font-size: 0.85rem; color: #8892B0; border-top: 1px solid #3A4252; margin-top: 40px; }
    .footer b { color: #9E9E9E; }
    div.row-widget.stRadio > div { background-color: #262C38; padding: 15px; border-radius: 8px; border: 1px solid #3A4252; }
    tbody tr:hover { background-color: #3A4252 !important; }
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
        st.error(f"Archivo de datos no encontrado: {filepath}")
        return data
        
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            return data
        headers = [h.strip() for h in headers]
        
        for row in reader:
            if not row or len(row) < 2: continue
            sustancia = row[1].strip()
            if not sustancia or sustancia.lower() == 'ph' or sustancia.isdigit() or sustancia == '0':
                continue
            
            row += [''] * (len(headers) - len(row))
            row_dict = dict(zip(headers, row))
            data[sustancia] = row_dict
    return data

def calculate_ionization(pka_str, character, ph):
    try:
        pka_val = float(pka_str.split(',')[0].strip())
    except Exception:
        return 0.0, 100.0
        
    character = character.strip().lower()
    if 'ácido' in character or 'acido' in character:
        try:
            power = pka_val - ph
            if power > 100: ion = 0.0
            elif power < -100: ion = 100.0
            else: ion = 100.0 / (1.0 + 10.0**power)
        except OverflowError:
            ion = 0.0 if (pka_val - ph) > 0 else 100.0
    else:
        try:
            power = ph - pka_val
            if power > 100: ion = 0.0
            elif power < -100: ion = 100.0
            else: ion = 100.0 / (1.0 + 10.0**power)
        except OverflowError:
            ion = 0.0 if (ph - pka_val) > 0 else 100.0
            
    neu = 100.0 - ion
    return ion, neu

def find_optimal_separation_window(info_obj, info_cut):
    window = []
    pka_obj = info_obj.get('pKa', '7')
    char_obj = info_obj.get('Carácter', 'Base')
    pka_cut = info_cut.get('pKa', '7')
    char_cut = info_cut.get('Carácter', 'Base')
    
    for ph_val in [x/10.0 for x in range(0, 141)]:
        i_obj, _ = calculate_ionization(pka_obj, char_obj, ph_val)
        i_cut, _ = calculate_ionization(pka_cut, char_cut, ph_val)
        diff = abs(i_obj - i_cut)
        if diff >= 90.0:
            window.append(ph_val)
            
    if window:
        return window[0], window[-1]
    return None, None

def find_image(sub_name, suffix):
    base_dir = os.path.dirname(__file__)
    img_dir = os.path.join(base_dir, 'Imagenes estructura')
    norm_name = normalize_name(sub_name)
    name_pattern = f"{norm_name}_{suffix}"
    
    for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
        path = os.path.join(img_dir, f"{name_pattern}{ext}")
        if os.path.exists(path): return path
            
    for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
        path = os.path.join(img_dir, f"{sub_name}_{suffix}{ext}")
        if os.path.exists(path): return path
            
    return None

def get_solvent(info, pka, current_ph):
    try:
        pka_val = float(pka.split(',')[0].strip())
    except Exception:
        pka_val = 7.0
    
    if current_ph < pka_val:
        for k, v in info.items():
            if '<' in k and 'Disolvente' in k:
                return v if v else "No especificado"
    else:
        for k, v in info.items():
            if '>' in k and 'Disolvente' in k:
                return v if v else "No especificado"
    return "No especificado"

def render_presumptive_card(test_name, color_desc, interpretation, bg_style, is_biphasic=False, top_bg="", bot_bg="", top_txt="", bot_txt=""):
    if is_biphasic:
        visual = f"""<div class="biphasic-tube">
<div class="biphasic-top" style="background: {top_bg};">{top_txt}</div>
<div class="biphasic-bottom" style="background: {bot_bg};">{bot_txt}</div>
</div>"""
    else:
        visual = f'<div class="color-box" style="background: {bg_style};"></div>'
        
    st.markdown(f"""
<div class="forensic-card">
{visual}
<div style="font-size: 1.1rem; font-weight: 600; color: #E1E4EA; margin-bottom: 5px;">{test_name}</div>
<div style="font-size: 0.9rem; color: #A0AABF; margin-bottom: 10px;"><b>Tono Visual:</b> {color_desc}</div>
<div style="font-size: 0.95rem; color: #E1E4EA; font-weight: bold;">{interpretation}</div>
</div>
    """, unsafe_allow_html=True)

def tab1_tamizaje(data, selected_sustancia, info):
    st.subheader("🧪 Flujo de Descarte Químico")
    
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### Árbol de Decisión Interactivo")
        paso1 = st.radio("Paso 1: Reactivo de Mayer (#901) - Identificación de Alcaloides", ["Seleccione...", "Precipitado blanco/crema", "Sin reacción (Claro)"], label_visibility="collapsed")
        
        if paso1 == "Precipitado blanco/crema":
            render_presumptive_card("Reactivo de Mayer (#901)", "Precipitado Blanco/Crema (#FDFEFE)", "✅ Positivo para Alcaloides / Bases Nitrogenadas", "#FDFEFE")
            
            paso2 = st.radio("Paso 2: Reactivo de Marquis (#902)", ["Seleccione...", "Violeta / Púrpura", "Naranja → Rojo → Marrón", "Negro directo", "Sin reacción (Claro)"], label_visibility="collapsed")
            
            if paso2 == "Violeta / Púrpura":
                render_presumptive_card("Reactivo de Marquis (#902)", "Violeta Oscuro (#5B2C6F)", "🚨 Sospecha: Opiáceos (Heroína, Morfina)", "#5B2C6F")
                st.info("💡 Confirmar con **Reactivo de Mecke (#924)**. Resultado esperado: Verde inmediato.")
            elif paso2 == "Naranja → Rojo → Marrón":
                render_presumptive_card("Reactivo de Marquis (#902)", "Gradiente Naranja a Marrón", "🚨 Sospecha: Anfetaminas / Metanfetamina", "linear-gradient(to right, #D9531E, #E74C3C, #5C2C16)")
            elif paso2 == "Negro directo":
                render_presumptive_card("Reactivo de Marquis (#902)", "Negro (#1A1A1A)", "🚨 Sospecha: MDMA / Éxtasis", "#1A1A1A")
            elif paso2 == "Sin reacción (Claro)":
                st.warning("⚠️ Sin reacción en Marquis. Derivar a ensayo específico para Cocaína.")
                paso3 = st.radio("Paso 3: Reactivo de Scott (#904)", ["Seleccione...", "1ra Azul → 2da Rosa → 3ra Bifásico (Rosa sobre Azul)"], label_visibility="collapsed")
                if paso3 == "1ra Azul → 2da Rosa → 3ra Bifásico (Rosa sobre Azul)":
                    render_presumptive_card(
                        "Prueba de Scott (#904)", 
                        "Azul Cobalto extraíble en fase orgánica", 
                        "🚨 Sospecha: Cocaína (Sal o Base)", 
                        "", is_biphasic=True, top_bg="#F5B7B1", bot_bg="#0077C8", top_txt="Acuosa (Rosa)", bot_txt="Orgánica (Azul)"
                    )
                    
        elif paso1 == "Sin reacción (Claro)":
            st.info("❌ Negativo a Mayer. Proceder con familia de depresores o alucinógenos.")
            paso2b = st.radio("Siguientes Pruebas:", ["Seleccione...", "Reactivo de Dille-Koppanyi (#905)", "Reactivo de Ehrlich (#907)"], label_visibility="collapsed")
            if paso2b == "Reactivo de Dille-Koppanyi (#905)":
                render_presumptive_card("Dille-Koppanyi (#905)", "Púrpura Claro (#D2B4DE)", "🚨 Sospecha: Barbitúricos", "#D2B4DE")
            elif paso2b == "Reactivo de Ehrlich (#907)":
                render_presumptive_card("Ehrlich / Van Urk (#907)", "Púrpura (#8E44AD)", "🚨 Sospecha: LSD / Indoles", "#8E44AD")
                
        st.markdown("<hr style='border-color: #3A4252;'>", unsafe_allow_html=True)
        st.markdown("### Ensayos para Material Vegetal")
        veg = st.radio("Reactivos Específicos:", ["Seleccione...", "Duquenois-Levine (#908)", "Reactivo KN (#909)"], label_visibility="collapsed")
        if veg == "Duquenois-Levine (#908)":
            render_presumptive_card(
                "Duquenois-Levine (#908)", 
                "Gris Pizarra sobre Violeta", 
                "🚨 Sospecha: Cannabis / THC", 
                "", is_biphasic=True, top_bg="#7F8C8D", bot_bg="#5B2C6F", top_txt="Gris", bot_txt="Violeta"
            )
        elif veg == "Reactivo KN (#909)":
            render_presumptive_card("Reactivo KN (#909)", "Marrón Rojizo (#A04000)", "🚨 Sospecha: Marihuana", "#A04000")

    with col2:
        st.markdown(f"### 🔍 Ficha Colorimétrica: <span style='color: #9E9E9E;'>{selected_sustancia}</span>", unsafe_allow_html=True)
        
        prueba = info.get('Prueba presuntiva', 'N/A')
        color = info.get('Color característico', 'N/A')
        
        nombre = selected_sustancia.lower()
        if "cocaína" in nombre or "cocaina" in nombre:
            render_presumptive_card("Prueba de Scott (#904)", f"Documentado: {color}", "Interpretación: Positivo para Cocaína", "", True, "#F5B7B1", "#0077C8", "Fase Acuosa", "Fase Orgánica")
        elif "metanfetamina" in nombre or "anfetamina" in nombre:
            render_presumptive_card("Marquis (#902)", f"Documentado: {color}", "Interpretación: Anfetaminas", "linear-gradient(to right, #D9531E, #E74C3C, #5C2C16)")
        elif "mdma" in nombre or "mda" in nombre:
            render_presumptive_card("Marquis (#902) / Mandelin", f"Documentado: {color}", "Interpretación: Entactógenos", "#1A1A1A")
        elif "lsd" in nombre:
            render_presumptive_card("Ehrlich (#907)", f"Documentado: {color}", "Interpretación: Indoles", "#8E44AD")
        elif "thc" in nombre:
            render_presumptive_card("Duquenois-Levine (#908)", f"Documentado: {color}", "Interpretación: Cannabinoides", "", True, "#7F8C8D", "#5B2C6F", "Fase Sup.", "Fase Inf.")
        elif "heroína" in nombre or "heroina" in nombre:
            render_presumptive_card("Marquis (#902)", f"Documentado: {color}", "Interpretación: Opiáceos", "#5B2C6F")
            render_presumptive_card("Mecke (#924)", "Verde (#1E8449)", "Confirmatorio para Opiáceos", "#1E8449")
        elif "ketamina" in nombre:
            render_presumptive_card("Reactivo de Morris", f"Documentado: {color}", "Interpretación: Positivo para Ketamina", "#8E44AD")
        elif "2cb" in nombre or "2c-b" in nombre:
            render_presumptive_card("Marquis (#902)", f"Documentado: {color}", "Interpretación: Fenetilaminas", "linear-gradient(to right, #F1C40F, #27AE60)")
        elif "efedrina" in nombre:
            render_presumptive_card("Liebermann", f"Documentado: {color}", "Interpretación: Precursores", "linear-gradient(to right, #E74C3C, #D35400)")
        elif "levamisol" in nombre:
            render_presumptive_card("Liebermann", f"Documentado: {color}", "Interpretación: Adulterante común", "linear-gradient(to right, #D35400, #A04000)")
        elif "aspirina" in nombre:
            render_presumptive_card("McNally", f"Documentado: {color}", "Interpretación: Salicilatos", "#C0392B")
        elif "metamizol" in nombre:
            render_presumptive_card("Cloruro Férrico", f"Documentado: {color}", "Interpretación: Derivados Pirazolónicos", "#8E44AD")
        else:
            fallback_color = "#555555"
            c_lower = color.lower()
            if "naranja" in c_lower: fallback_color = "#E67E22"
            elif "rojo" in c_lower or "roja" in c_lower: fallback_color = "#E74C3C"
            elif "azul" in c_lower: fallback_color = "#3498DB"
            elif "violeta" in c_lower or "púrpura" in c_lower or "morado" in c_lower: fallback_color = "#8E44AD"
            elif "verde" in c_lower: fallback_color = "#27AE60"
            elif "amarillo" in c_lower: fallback_color = "#F1C40F"
            elif "rosa" in c_lower: fallback_color = "#F1948A"
            elif "marrón" in c_lower or "cafe" in c_lower: fallback_color = "#8B4513"
            elif "negro" in c_lower: fallback_color = "#1A1A1A"
            
            test_title = prueba if prueba and prueba != "N/A" and prueba != "-" else "Prueba Presuntiva"
            render_presumptive_card(test_title, f"Documentado: {color}", "Interpretación: Reacción empírica", fallback_color)
            
        st.markdown(f"""
        <div class="forensic-card" style="border: 1px solid #E74C3C;">
            <h4 style="color: #E74C3C !important; font-size: 1rem;">⚠️ Precaución Técnica</h4>
            <p style="font-size: 0.85rem; color: #A0AABF; margin:0;">
            Las pruebas colorimétricas son presuntivas. Adulterantes o excipientes pueden generar falsos positivos. La confirmación instrumental (GC-MS / FTIR) es obligatoria en contexto pericial.
            </p>
        </div>
        """, unsafe_allow_html=True)


def tab2_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph):
    st.subheader("⚗️ Separación L-L y Purificación de Muestras")
    
    info_obj = data[selected_sustancia]
    info_cut = data[selected_adulterante]
    
    pka_obj = info_obj.get('pKa', '7')
    char_obj = info_obj.get('Carácter', 'Base')
    pka_cut = info_cut.get('pKa', '7')
    char_cut = info_cut.get('Carácter', 'Base')
    
    i_obj_curr, n_obj_curr = calculate_ionization(pka_obj, char_obj, selected_ph)
    i_cut_curr, n_cut_curr = calculate_ionization(pka_cut, char_cut, selected_ph)
    
    solv_obj = get_solvent(info_obj, pka_obj, selected_ph)
    solv_cut = get_solvent(info_cut, pka_cut, selected_ph)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
<div class="forensic-card" style="border-left: 4px solid #00E5FF;">
<h4 style="color: #00E5FF !important; margin-top:0;">🎯 Analito Objetivo: {selected_sustancia}</h4>
<p style="margin-bottom:5px;"><b>Carácter:</b> {char_obj}</p>
<p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_obj}</span></p>
<p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_obj}</p>
<hr style="border-color:#3A4252; margin: 10px 0;">
<p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_obj_curr:.2f}%</span></p>
<p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_obj_curr:.2f}%</span></p>
</div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
<div class="forensic-card" style="border-left: 4px solid #E74C3C;">
<h4 style="color: #E74C3C !important; margin-top:0;">✂️ Adulterante: {selected_adulterante}</h4>
<p style="margin-bottom:5px;"><b>Carácter:</b> {char_cut}</p>
<p style="margin-bottom:5px;"><b>pKa:</b> <span class="numeric-val">{pka_cut}</span></p>
<p style="margin-bottom:15px;"><b>Disolvente Recomendado (pH {selected_ph}):</b> {solv_cut}</p>
<hr style="border-color:#3A4252; margin: 10px 0;">
<p style="margin-bottom:5px;"><b>% Ionizado (Fase Acuosa):</b> <span class="numeric-val">{i_cut_curr:.2f}%</span></p>
<p style="margin-bottom:0;"><b>% Neutro (Fase Orgánica):</b> <span class="numeric-val">{n_cut_curr:.2f}%</span></p>
</div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Curvas de Ionización Competitivas (% de Especie vs pH)")
    
    chart_data = []
    for ph_val in [x/10.0 for x in range(0, 141, 2)]:
        i_o, n_o = calculate_ionization(pka_obj, char_obj, ph_val)
        i_c, n_c = calculate_ionization(pka_cut, char_cut, ph_val)
        chart_data.append({"pH": ph_val, "% Especie": i_o, "Sustancia": "Objetivo (Ionizado - Agua)", "Categoría": "Objetivo"})
        chart_data.append({"pH": ph_val, "% Especie": n_o, "Sustancia": "Objetivo (Neutro - Orgánico)", "Categoría": "Objetivo"})
        chart_data.append({"pH": ph_val, "% Especie": i_c, "Sustancia": "Corte (Ionizado - Agua)", "Categoría": "Adulterante"})
        chart_data.append({"pH": ph_val, "% Especie": n_c, "Sustancia": "Corte (Neutro - Orgánico)", "Categoría": "Adulterante"})
        
    point_data = [
        {"pH": selected_ph, "% Especie": i_obj_curr, "Sustancia": "Objetivo (Ionizado - Agua)", "Categoría": "Objetivo"},
        {"pH": selected_ph, "% Especie": n_obj_curr, "Sustancia": "Objetivo (Neutro - Orgánico)", "Categoría": "Objetivo"},
        {"pH": selected_ph, "% Especie": i_cut_curr, "Sustancia": "Corte (Ionizado - Agua)", "Categoría": "Adulterante"},
        {"pH": selected_ph, "% Especie": n_cut_curr, "Sustancia": "Corte (Neutro - Orgánico)", "Categoría": "Adulterante"}
    ]
    
    base_chart = alt.Chart(alt.Data(values=chart_data)).mark_line(interpolate='monotone', strokeWidth=3).encode(
        x=alt.X('pH:Q', scale=alt.Scale(domain=[0, 14]), title="pH del Medio", axis=alt.Axis(gridColor="#3A4252", labelColor="#E1E4EA", titleColor="#E1E4EA")),
        y=alt.Y('% Especie:Q', scale=alt.Scale(domain=[0, 100]), title="% Relativo de la Especie", axis=alt.Axis(gridColor="#3A4252", labelColor="#E1E4EA", titleColor="#E1E4EA")),
        color=alt.Color('Sustancia:N', scale=alt.Scale(
            domain=['Objetivo (Ionizado - Agua)', 'Objetivo (Neutro - Orgánico)', 'Corte (Ionizado - Agua)', 'Corte (Neutro - Orgánico)'], 
            range=['#00E5FF', '#F1C40F', '#E74C3C', '#E67E22']
        ), legend=alt.Legend(title="Especies", titleColor="#E1E4EA", labelColor="#E1E4EA", orient="bottom")),
        strokeDash=alt.condition(
            alt.datum.Categoría == 'Adulterante',
            alt.value([5, 5]),
            alt.value([0])
        )
    ).properties(height=450)
    
    point_chart = alt.Chart(alt.Data(values=point_data)).mark_circle(size=150, opacity=1, stroke="#fff", strokeWidth=2).encode(
        x='pH:Q',
        y='% Especie:Q',
        color=alt.Color('Sustancia:N', scale=alt.Scale(
            domain=['Objetivo (Ionizado - Agua)', 'Objetivo (Neutro - Orgánico)', 'Corte (Ionizado - Agua)', 'Corte (Neutro - Orgánico)'], 
            range=['#00E5FF', '#F1C40F', '#E74C3C', '#E67E22']
        ), legend=None),
        tooltip=['pH:Q', '% Especie:Q', 'Sustancia:N']
    )
    
    rule = alt.Chart(alt.Data(values=[{"pH": selected_ph}])).mark_rule(strokeDash=[3, 3], color='#E1E4EA', strokeWidth=1).encode(
        x='pH:Q'
    )
    
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

    col3, col4 = st.columns([1.5, 1])
    with col3:
        st.markdown("### Protocolo Automatizado de Extracción Diferencial")
        
        if selected_sustancia == selected_adulterante:
            st.info("Seleccione una sustancia objetivo y un adulterante distinto para generar el protocolo de separación.")
        elif ph_min is None:
            st.error("⚠️ **No es posible lograr una separación selectiva simple por extracción Líquido-Líquido.** No existe un intervalo de pH donde la diferencia de ionización supere el 90%.")
        else:
            opt_ph = (ph_min + ph_max) / 2
            i_opt_obj, _ = calculate_ionization(pka_obj, char_obj, opt_ph)
            
            obj_in_water = i_opt_obj >= 50.0
            
            if obj_in_water:
                if 'ácido' in char_obj or 'acido' in char_obj:
                    new_ph = opt_ph - 3 if opt_ph - 3 >= 0 else 0
                    action = f"Acidificar fuertemente a pH < {new_ph:.1f} para protonar y volver neutro al {selected_sustancia}."
                else:
                    new_ph = opt_ph + 3 if opt_ph + 3 <= 14 else 14
                    action = f"Alcalinizar a pH > {new_ph:.1f} para desprotonar y liberar al {selected_sustancia} como base libre."
                    
                protocol_html = f"""
<div class="forensic-card">
<h4 style="color: #E1E4EA !important;">PASO 1: Partición Inicial</h4>
<p>Ajustar el pH de la matriz o disolución acuosa a <b style="color:#00FF9D;">{opt_ph:.1f}</b> (dentro de la ventana verde).</p>
<p>A este pH, <b>{selected_sustancia}</b> estará ionizado (retención en agua) y <b>{selected_adulterante}</b> estará neutro (transferencia a orgánico).</p>
<ul>
<li>Añadir volumen igual de disolvente orgánico inmiscible (ej. {solv_cut}), agitar y decantar.</li>
<li><span style="color:#E74C3C;"><b>Acción:</b></span> El adulterante pasará a la fase orgánica. Lavar repetidamente y <b>desechar la fase orgánica</b>. Conservar únicamente la <b>fase acuosa</b>.</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 2: Aislamiento del Objetivo</h4>
<ul>
<li>{action}</li>
<li>Añadir solvente orgánico fresco, agitar y decantar.</li>
<li><b>Conservar la nueva fase orgánica</b> que ahora contiene el analito purificado y desechar el agua.</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 3: Secado y Preparación Instrumental</h4>
<ul>
<li>Pasar la fase orgánica por un filtro con sulfato de sodio anhidro (Na₂SO₄).</li>
<li>Evaporar a sequedad con corriente continua de nitrógeno (N₂).</li>
<li>Reconstituir el residuo en el disolvente apropiado grado cromatográfico para análisis GC-MS o depositar en ATR-FTIR.</li>
</ul>
</div>
"""
            else:
                protocol_html = f"""
<div class="forensic-card">
<h4 style="color: #E1E4EA !important;">PASO 1: Partición Inicial</h4>
<p>Ajustar el pH de la matriz o disolución acuosa a <b style="color:#00FF9D;">{opt_ph:.1f}</b> (dentro de la ventana verde).</p>
<p>A este pH, <b>{selected_sustancia}</b> estará neutro (transferencia a orgánico) y <b>{selected_adulterante}</b> estará ionizado (retención en agua).</p>
<ul>
<li>Añadir volumen igual de disolvente orgánico inmiscible (ej. {solv_obj}), agitar y decantar.</li>
<li><span style="color:#E74C3C;"><b>Acción:</b></span> Extraer con el solvente orgánico. El adulterante quedará atrapado en el agua. <b>Conservar la fase orgánica</b> que contiene al objetivo puro y descartar la fase acuosa.</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 2: Aislamiento</h4>
<ul>
<li>El analito objetivo ({selected_sustancia}) ya se encuentra aislado en la fase orgánica pura de forma neutra. (Se omite la retro-extracción a agua a menos que la matriz biológica sea altamente compleja).</li>
</ul>
<h4 style="color: #E1E4EA !important; margin-top:20px;">PASO 3: Secado y Preparación Instrumental</h4>
<ul>
<li>Pasar la fase orgánica por un filtro con sulfato de sodio anhidro (Na₂SO₄).</li>
<li>Evaporar a sequedad en baño térmico de calor suave con corriente continua de nitrógeno (N₂).</li>
<li>Reconstituir el residuo en el disolvente apropiado grado cromatográfico para análisis GC-MS o depositar en ATR-FTIR.</li>
</ul>
</div>
"""
            st.markdown(protocol_html, unsafe_allow_html=True)
            
    with col4:
        st.markdown("### Estructura de Interés")
        obj_is_ion, _ = calculate_ionization(pka_obj, char_obj, selected_ph)
        suffix = 'ion' if obj_is_ion >= 50.0 else 'base'
        img_path = find_image(selected_sustancia, suffix)
        if img_path:
            st.image(img_path, caption=f"Estado del Analito Objetivo a pH {selected_ph:.1f}", use_container_width=True)
        else:
            st.info(f"ℹ️ Estructura molecular ({suffix}) del objetivo no disponible.")

def tab3_confirmacion(selected_sustancia, info):
    st.subheader("📊 Confirmación Analítica e Instrumental")
    
    col_ir, col_ms = st.columns(2)
    
    with col_ir:
        st.markdown("""
        <div class="forensic-card">
            <h4 style="margin: 0;">Espectroscopía Infrarroja (FTIR-ATR)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        img_ir = find_image(selected_sustancia, 'Espectro_IR')
        if img_ir:
            st.image(img_ir, use_container_width=True)
        else:
            st.warning("⚠️ Espectrograma IR no digitalizado.")
            
        picos_ir = []
        for i in range(1, 7):
            num = info.get(f'P{i}', '').strip()
            asig = info.get(f'S{i}', '').strip()
            if num or asig:
                picos_ir.append({"Vibración (cm⁻¹)": num, "Modo / Asignación": asig})
        
        if picos_ir:
            st.markdown("<b>Bandas Diagnósticas Principales</b>", unsafe_allow_html=True)
            st.table(picos_ir)
            
    with col_ms:
        st.markdown("""
        <div class="forensic-card">
            <h4 style="margin: 0;">Espectrometría de Masas (GC-MS)</h4>
        </div>
        """, unsafe_allow_html=True)
        
        img_ms = find_image(selected_sustancia, 'GS-MS')
        if img_ms:
            st.image(img_ms, use_container_width=True)
        else:
            st.warning("⚠️ Espectro de masas no digitalizado.")
            
        iones = []
        for i in range(1, 9):
            ion_val = info.get(f'I{i}', '').strip()
            desc = info.get(f'D{i}', '').strip()
            if ion_val or desc:
                iones.append({"Relación m/z": ion_val, "Tipo de Fragmento": desc})
                
        if iones:
            st.markdown("<b>Patrón de Fragmentación</b>", unsafe_allow_html=True)
            st.table(iones)

def main():
    inject_custom_css()
    
    st.markdown("<h1>Plataforma Pericial de Química Forense</h1>", unsafe_allow_html=True)
    
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'pH_vs_Ionizacion_Comparada_Datos.csv')
    
    data = load_data(csv_path)
    
    if not data:
        st.error("Error crítico: Dataset 'pH_vs_Ionizacion_Comparada_Datos.csv' no disponible.")
        return
        
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>Panel de Control</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='border-color: #3A4252;'>", unsafe_allow_html=True)
        
        sustancias_list = list(data.keys())
        selected_sustancia = st.selectbox("🎯 Sustancia Objetivo (Analito)", sustancias_list, index=0)
        selected_adulterante = st.selectbox("✂️ Sustancia de Corte / Adulterante", sustancias_list, index=1 if len(sustancias_list) > 1 else 0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        selected_ph = st.slider("🧪 pH del Medio Extractor", 0.0, 14.0, 7.0, 0.1)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #262C38; padding: 15px; border-radius: 8px; border: 1px solid #3A4252; text-align: center; font-size: 0.8rem;">
            <b>Realizado por:</b><br/>QFB Edgar Oswaldo Díaz Andrade<br/><br/>
            <span style="color:#A0AABF;">Herramienta interactiva para perfilación presuntiva e instrumental.</span>
        </div>
        """, unsafe_allow_html=True)
    
    info_obj = data[selected_sustancia]
    
    tab1, tab2, tab3 = st.tabs(["📋 1. Tamizaje y Colorimetría", "⚗️ 2. Fisicoquímica y Extracción L-L", "📊 3. Confirmación Instrumental"])
    
    with tab1:
        tab1_tamizaje(data, selected_sustancia, info_obj)
        
    with tab2:
        tab2_fisicoquimica(data, selected_sustancia, selected_adulterante, selected_ph)
        
    with tab3:
        tab3_confirmacion(selected_sustancia, info_obj)
        
    st.markdown("""
    <div class="footer">
        <b>Referencias Bibliográficas:</b><br/>
        Moffat AC, Osselton MD, Widdop B, Watts J, editores. <i>Clarke's Analysis of Drugs and Poisons: In pharmaceuticals, body fluids and postmortem material</i>. 4a ed. Londres: Pharmaceutical Press; 2011.<br/>
        <span style="font-weight: bold; margin-top: 10px; display: inline-block;">Realizado por: QFB Edgar Oswaldo Díaz Andrade</span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
