with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix CSS
css_old_start = text.find('def inject_custom_css():')
if css_old_start != -1:
    css_old_end = text.find('def normalize_name', css_old_start)
    
    new_css = '''def inject_custom_css():
    st.markdown("""
    <style>
    /* Pearl white background */
    .stApp, .main { background-color: #FBFBF9 !important; color: #000000 !important; }
    [data-testid="stSidebar"] { background-color: #F0F0F0 !important; text-align: center; color: #000000 !important;}
    h1, h2, h3, h4, h5, h6 { color: #003366 !important; text-shadow: none; text-align: center !important; width: 100%; display: block; }
    p, span, div, label, li { text-align: center; color: #000000; }
    ul { list-style-position: inside; text-align: center; padding: 0; }
    table { width: 100%; margin: 0 auto; text-align: center; transition: all 0.3s ease-in-out; color: #000000 !important; }
    th, td { text-align: center !important; color: #000000 !important; }
    img { transition: all 0.3s ease-in-out; border-radius: 8px; margin: 0 auto; display: block; }
    .forensic-card { background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s ease-in-out; }
    .forensic-card:hover { transform: scale(1.02); box-shadow: 0 8px 16px rgba(0, 51, 102, 0.2); border-color: #003366; }
    .nota-card { background-color: #E6F2FF; border-left: 5px solid #003366; padding: 15px; margin-top: 30px; border-radius: 4px; transition: all 0.3s ease-in-out; }
    .nota-card:hover { transform: scale(1.02); box-shadow: 0 0 15px rgba(0, 51, 102, 0.4); border: 1px solid #003366; border-left: 5px solid #003366; }
    .numeric-val { font-family: 'Courier New', Courier, monospace; color: #003366; font-weight: bold; }
    .color-box { height: 50px; width: 100%; border-radius: 6px; margin-bottom: 12px; box-shadow: inset 0 0 10px rgba(0,0,0,0.1); border: 1px solid #CCCCCC; }
    </style>
    """, unsafe_allow_html=True)
'''
    text = text[:css_old_start] + new_css + text[css_old_end:]

# Fix sort
text = text.replace('sustancias_list = list(data.keys())', 'sustancias_list = sorted(list(data.keys()))')

# Fix tab4
text = text.replace('def tab4_reactivos():', 'def tab4_reactivos(data):')
text = text.replace('db = load_csv_data()', 'db = data')
text = text.replace('with tab4: tab4_reactivos()', 'with tab4: tab4_reactivos(data)')

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
