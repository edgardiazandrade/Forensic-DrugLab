with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_app = []
skip = False
for line in lines:
    if 'def tab4_reactivos():' in line:
        new_app.append(line)
        new_app.append('''    tests = load_pruebas_csv()
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
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Resultados Esperados (Colores)</h3>", unsafe_allow_html=True)
        # Load from DB
        db = load_csv_data()
        colores_html = '<div style="display:flex; justify-content:center; gap:20px; flex-wrap:wrap;">'
        found_any = False
        for sus, sus_info in db.items():
            prueba_db = sus_info.get('Prueba presuntiva', '')
            if prueba_db == selected or (selected.split(" ")[-1] in prueba_db and len(selected.split(" ")[-1]) > 3):
                c = sus_info.get('Color característico', 'N/A')
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
            
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Reactivos Necesarios</h3>", unsafe_allow_html=True)
        reactivos_raw = info.get('Reactivos', '').split('\\n')
        react_list = []
        for r in reactivos_raw:
            parts = r.split(':', 1)
            if len(parts) == 2:
                react_list.append({"Reactivo": parts[0].strip(), "Preparación / Cantidad": parts[1].strip()})
            elif r.strip():
                react_list.append({"Reactivo": r.strip(), "Preparación / Cantidad": "Directo / Sin preparación previa"})
        if react_list: st.table(react_list)
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Procedimiento Analítico</h3>", unsafe_allow_html=True)
        proc_raw = info.get('Procedimiento', '').split('\\n')
        
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
        
        st.markdown("<hr style='border-color:#3A4252;'><h3 style='text-align:center;'>Interferencias y Limitaciones</h3>", unsafe_allow_html=True)
        st.table([
            {"Tipo de Falso": "Falso Positivo", "Descripción / Sustancias Interferentes": info.get('Falsos Positivos', '')},
            {"Tipo de Falso": "Falso Negativo", "Descripción / Sustancias Interferentes": info.get('Falsos Negativos', '')}
        ])
''')
        skip = True
        continue
    
    if skip and 'def main():' in line:
        skip = False
        
    if not skip:
        new_app.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_app)

print('app.py Updated with new colors in Tab 4!')
