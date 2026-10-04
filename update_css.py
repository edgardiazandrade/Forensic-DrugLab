with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = -1
end = -1
for i, line in enumerate(lines):
    if 'def set_css():' in line:
        start = i
    elif start != -1 and line.startswith('def '):
        end = i
        break

css = """def set_css():
    st.markdown('''
    <style>
    /* Pearl white background */
    .stApp, .main {
        background-color: #FBFBF9 !important;
        color: #000000 !important;
    }
    
    [data-testid="stSidebar"] { background-color: #F0F0F0 !important; text-align: center; color: #000000 !important;}
    
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
        background-color: #E6F2FF; 
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
    </style>
    ''', unsafe_allow_html=True)

"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(lines[:start])
    f.write(css)
    f.writelines(lines[end:])
print('CSS Updated!')
