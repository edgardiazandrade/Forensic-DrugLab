import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate the end of tab2
start_tab3 = text.find('    st.markdown("<h3 style=\'text-align:center;\'>Protocolo Automatizado de Extracci')
if start_tab3 != -1:
    # First, let's remove everything from start_tab3 to the end of tab2_arbol_decision
    # which is basically up to def tab_simulador()
    end_tab3 = text.find('def tab_simulador():', start_tab3)
    if end_tab3 != -1:
        text = text[:start_tab3] + "\n" + text[end_tab3:]

tab3_code = """
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
        i_opt_obj, _ = calculate_ionization(pka_obj, char_obj, opt_ph)
        obj_in_water = i_opt_obj >= 50.0
        
        if obj_in_water:
            if 'cido' in char_obj.lower():
                new_ph = opt_ph - 3 if opt_ph - 3 >= 0 else 0
                action = f"Acidificar fuertemente a pH < {new_ph:.1f} para protonar y volver neutro al {selected_sustancia}."
            else:
                new_ph = opt_ph + 3 if opt_ph + 3 <= 14 else 14
                action = f"Alcalinizar a pH > {new_ph:.1f} para desprotonar y liberar al {selected_sustancia} como base libre."
                
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

"""

# Insert it before tab_simulador
text = text.replace('def tab_simulador():', tab3_code + '\ndef tab_simulador():')

# Also limit IR and MS images
text = text.replace("st.image(img_ir, use_container_width=True)", "st.image(img_ir, width=400)")
text = text.replace("st.image(img_ms, use_container_width=True)", "st.image(img_ms, width=400)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Restored tab3")
