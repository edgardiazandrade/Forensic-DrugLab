import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = '''        if obj_in_water:
            if 'cido' in char_obj.lower():
                new_ph = opt_ph - 3 if opt_ph - 3 >= 0 else 0
                action = f"Acidificar fuertemente a pH < {new_ph:.1f} para protonar y volver neutro al {selected_sustancia}."
            else:
                new_ph = opt_ph + 3 if opt_ph + 3 <= 14 else 14
                action = f"Alcalinizar a pH > {new_ph:.1f} para desprotonar y liberar al {selected_sustancia} como base libre."'''

new_logic = '''        if obj_in_water:
            if 'anf' in char_obj.lower() or 'dip' in char_obj.lower():
                try:
                    pkas = [float(x.strip()) for x in str(pka_obj).split(',')]
                    pi = sum(pkas)/len(pkas)
                except:
                    pi = 7.0
                action = f"Ajustar cuidadosamente el pH a su punto de máxima neutralidad (aprox. pH {pi:.1f}) para precipitar o extraer al {selected_sustancia}."
            elif 'cido' in char_obj.lower():
                try: pka_val = float(str(pka_obj).split(',')[0])
                except: pka_val = opt_ph - 3
                new_ph = pka_val - 2 if pka_val - 2 >= 0 else 0
                action = f"Acidificar fuertemente (pH < {new_ph:.1f}) para protonar y volver neutro al {selected_sustancia}."
            else:
                try: pka_val = float(str(pka_obj).split(',')[0])
                except: pka_val = opt_ph + 3
                new_ph = pka_val + 2 if pka_val + 2 <= 14 else 14
                action = f"Alcalinizar (pH > {new_ph:.1f}) para desprotonar y liberar al {selected_sustancia} como base libre."'''

text = text.replace(old_logic, new_logic)

# For tab_simulador, the variable names are name_a, char_a, pka_a, etc.
old_logic_sim = '''        if obj_in_water:
            if 'cido' in char_a.lower():
                new_ph = opt_ph - 3 if opt_ph - 3 >= 0 else 0
                action = f"Acidificar fuertemente a pH < {new_ph:.1f} para protonar y volver neutro al {name_a}."
            else:
                new_ph = opt_ph + 3 if opt_ph + 3 <= 14 else 14
                action = f"Alcalinizar a pH > {new_ph:.1f} para desprotonar y liberar al {name_a} como base libre."'''

new_logic_sim = '''        if obj_in_water:
            if 'anf' in char_a.lower() or 'dip' in char_a.lower():
                try:
                    pkas = [float(x.strip()) for x in str(pka_a).split(',')]
                    pi = sum(pkas)/len(pkas)
                except:
                    pi = 7.0
                action = f"Ajustar cuidadosamente el pH a su punto de máxima neutralidad (aprox. pH {pi:.1f}) para precipitar o extraer al {name_a}."
            elif 'cido' in char_a.lower():
                try: pka_val = float(str(pka_a).split(',')[0])
                except: pka_val = opt_ph - 3
                new_ph = pka_val - 2 if pka_val - 2 >= 0 else 0
                action = f"Acidificar fuertemente (pH < {new_ph:.1f}) para protonar y volver neutro al {name_a}."
            else:
                try: pka_val = float(str(pka_a).split(',')[0])
                except: pka_val = opt_ph + 3
                new_ph = pka_val + 2 if pka_val + 2 <= 14 else 14
                action = f"Alcalinizar (pH > {new_ph:.1f}) para desprotonar y liberar al {name_a} como base libre."'''

text = text.replace(old_logic_sim, new_logic_sim)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Updated protocol logic")
