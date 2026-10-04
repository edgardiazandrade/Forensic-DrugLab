with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the note from tab1 and tab2
note_html = """
    st.markdown('''
    <div class="nota-card" style="border-left-color: #E74C3C;">
        <p style="color: #000000; text-align:center;"><b>⚠️ Nota:</b> Todo resultado positivo presuntivo tiene que confirmarse por pruebas confirmatorias instrumentales (GC-MS, FTIR).</p>
    </div>
    ''', unsafe_allow_html=True)"""

text = text.replace(note_html, '')

# Add the note right before the footer
footer_marker = """    st.markdown('''
    <div class="footer">
        <b>Referencias Bibliográficas:</b>"""
        
new_footer = """    st.markdown('''
    <div class="nota-card" style="border-left-color: #E74C3C; margin-bottom: 20px;">
        <p style="color: #000000; text-align:center;"><b>⚠️ NOTA ANALÍTICA:</b> Todo resultado positivo presuntivo tiene que confirmarse por pruebas confirmatorias instrumentales (como GC-MS o ATR-FTIR).</p>
    </div>
    <div class="footer">
        <b>Referencias Bibliográficas:</b>"""

if footer_marker in text:
    text = text.replace(footer_marker, new_footer)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Note moved to the bottom successfully.')
