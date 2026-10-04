with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_app = []
# 1. Add IR Interpretation function
ir_interp_func = '''
def interpretar_ir(pico_str):
    try:
        p = float(pico_str)
    except:
        return "-"
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
'''

for i, line in enumerate(lines):
    if 'def render_ir' in line:
        new_app.append(ir_interp_func)
    
    # 2. Modify render_ir to use interpretation
    if 'picos_ir.append({"Vibración (cm⁻¹)": num})' in line:
        new_app.append('        if num: picos_ir.append({"Vibración (cm⁻¹)": num, "Interpretación (Tablas IR)": interpretar_ir(num)})\n')
        continue
        
    # 3. Add Tab 4 (Simulador Manual) and shift Tab 4 to Tab 5
    if 'tab1, tab2, tab3, tab4 = st.tabs' in line:
        new_app.append('    tab1, tab2, tab3, tab_sim, tab4 = st.tabs(["📋 Comparativa", "🔍 Reactividad Cruzada", "⚗️ Gráfica Fisicoquímica L-L", "🧮 Simulador Manual", "🧪 Preparación de Reactivos"])\n')
        continue

    if 'def tab4_reactivos():' in line:
        tab_sim = '''def tab_simulador():
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

'''
        new_app.append(tab_sim)
        new_app.append(line)
        continue
        
    if 'with tab4: tab4_reactivos()' in line:
        new_app.append('    with tab_sim: tab_simulador()\n')
        new_app.append(line)
        continue

    new_app.append(line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_app)

print('app.py Updated with new features!')
