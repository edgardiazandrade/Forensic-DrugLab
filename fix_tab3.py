with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

bad = '''i_opt_obj, _ = calculate_ionization(pka_obj, char_obj, opt_ph)
        obj_in_water = i_opt_obj >= 50.0'''

good = '''sp_opt_obj = calculate_ionization(pka_obj, char_obj, opt_ph)
        obj_in_water = sp_opt_obj.get('Neutro', 0.0) < 50.0'''

text = text.replace(bad, good)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
