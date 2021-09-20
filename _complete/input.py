import re
from parse import initiate_matqs, initiate_system, initiate_load, initiate_calc, initiate_comb
from parse import split_no_string, check_formula
from keywords import keywords
from process import calculate

#TODO mit Umlauten umgehen wie???

def parse_module(db: dict, module_name: str, lines: dict) -> None:
    m_int = re.compile(r'^\-?\d+$')                 # prüfe ob String ein Integer ist
    m_float = re.compile(r'^\-?\d+(?:\.\d+)?$')     # prüfe ob String ein Float ist
    #TODO Exponentialschreibweise ermöglichen?

    #TODO je nach Modul fortgeschrittenere Einträge löschen -> in parse_input erledigen
    #TODO falls mehrere Module gleichen Namens, module_db laden
    if module_name.lower() in db:
        module_db = {module_name.lower(): db[module_name.lower()]}
    else:
        if module_name == 'MATQS':
            module_db = initiate_matqs()
        elif module_name == 'SYSTEM':
            module_db = initiate_system()
        elif module_name == 'LOAD':
            module_db = initiate_load()
        elif module_name == 'CALC':
            module_db = initiate_calc()
        elif module_name == 'COMB':
            module_db = initiate_comb()

    #print(db)

    for line_nr, line in lines.items():
        try:
            words = split_no_string(line)
        except:
            raise Exception(f'Closing parenthesis missing in line {line_nr}.')
        #TODO Warnung wenn Zeile nicht komplett verstanden
        if (command := words[0]) not in keywords[module_name]:
            raise Exception(f'Command: "{command}" unknown at position 1 in line {line_nr}.')
            
        comm_words = keywords[module_name][command.upper()]['KEYS']
        
        line_dict = {}
        current_key = words[1]
        current_value = ""

        for word in words[2:]: 
            if word.upper() in comm_words.keys():
                line_dict[current_key] = current_value
                current_key = word.upper()
                current_value = ""
            else:
                current_value += word

        if current_value == "":
            raise Exception(f'Last key is missing a value in line {line_nr}.')   
        else: 
            line_dict[current_key] = current_value
        #TODO prüfe ob alle benötigten Angaben vorhanden -> alle benötigten keys vor Schleife zusammensuchen
        #TODO SPTS darf nur direkt hinter SPT stehen -> wie ist das erreichbar

        for key, value in line_dict.items():
            reqs = comm_words[key]

            if check_formula(value):
                try:
                    res = eval(value)
                    value = str(res)
                except:
                    raise Exception(f'Could not evaluate formula for key: {key} in line {line_nr}.')

            if reqs[0] == int:
                if not m_int.match(value):
                    raise Exception(f'Expected Integer for key: {key} in line {line_nr}.')
                else:
                    line_dict[key] = int(value)
            elif reqs[0] == float:
                if not m_float.match(value):
                    raise Exception(f'Expected Float for key: {key} in line {line_nr}.')
                else:
                    line_dict[key] = float(value)
            elif reqs[0] == str:
                line_dict[key] = value.strip('"\'')

        #TODO erzeuge DB
        #with warnings.catch_warnings():
        #    warnings.simplefilter("default")
        try:
            update_db = keywords[module_name][command.upper()]['FUNC'](db, module_db, line_dict, comm_words)
        #except UserWarning as inst:
        #    warnings.warn(inst.args[0] + f' (line {line_nr}).')
        except Exception as inst:
            if len(inst.args) >= 1:
                inst.args = (inst.args[0] + f' (line {line_nr}).',) + inst.args[1:]
            raise inst
            #raise type(inst)(str(inst) + f' in line {line_nr}. ')

        #if update_db == None:       #TODO entfernen, nur zur Kontrolle
        #    continue
        
        for key, value in update_db.items():
            module_db[module_name.lower()][key].update(value)

    return module_db



def parse_input_file(file: str, modules: str):
    module_names = ['MATQS', 'SYSTEM', 'LOAD', 'CALC', 'COMB']

    m_prog = re.compile(r'[\+|\-]?PROG', re.I)  # Initialisiere Regex-Muster
    m_ende = re.compile(r'ENDE', re.I)

    module_nr = None                    # Prüfe, ob die Angabe der zu berechnenden Module eine Zahl ist
    if modules.isnumeric():
        module_nr = int(modules)

    with open(file, encoding='utf-8') as f:
        prog_counter = 0
        current_prog_name, current_module_name = "", ""
        save_lines = False
        end_programm = False
        lines = {}
        db = {}

        for i, line in enumerate(f.readlines()):
            line_nr = i + 1

            line = line.strip()     #TODO Kommentare hinter der Zeile auch gleich entfernen
            if len(line) == 0 or line[0] == '$':        # leere Zeilen oder solche mit Kommentar direkt überspringen
                    continue
            
            # Suche Ende eines Moduls
            if (s_ende := m_ende.match(line)):          # wenn Modul beendet: Werte zurücksetzen und parsen einleiten
                if lines:                               # parsen nur, wenn Zeilen enthalten
                    module_db = parse_module(db, current_module_name, lines) 
                    db[list(module_db.keys())[0]] = module_db[list(module_db.keys())[0]] #TODO Beschreibung  
                    calculate(db, current_module_name)

                lines = {}
                save_lines = False

                if end_programm:        # Abbruch, falls nur ein bestimmtes Modul zu berechnen
                    break

            # Zeilen in Modul
            if save_lines:                          # falls in gesuchten Modul: Zeile speichern
                lines[line_nr] = line.strip()

            # suche Start eines Moduls
            if (s_prog_list:= list(m_prog.finditer(line))): # suche Anfang eines Moduls
                s_prog = s_prog_list[0]
                if '$' in line[:s_prog.span()[0]]:          # falls Kommentar vor "prog": ignorieren
                    continue

                for next_prog in s_prog_list[1:]:           # falls mehrere "prog": prüfe ob alle nach Kommentar, sonst Warnung
                    if '$' in line[:next_prog.span()[0]]:
                        break
                    else:
                        raise Warning(f"Multiple Occurrences of PROG in line {line_nr}.")

                if save_lines:                          # falls schon aktives Modul: warnen
                    raise Warning(f"Nested Modules in line {line_nr}.")

                # falls "prog" in Zeile nach anderem Zeichen, aber vor Kommentar: Warnung    
                if s_prog.span()[0] != 0:          
                    raise SyntaxWarning(f"Unrecognized Character before PROG at line {line_nr}.")
                else:
                    prog_counter += 1   # erhöhe Anzahl gefundener Module

                    current_prog_name = line[s_prog.span()[1]:].strip().split(" ")[0]
                    current_module_name = current_prog_name.split("_")[0].upper()
                    
                    if current_module_name not in module_names:             # Prüfe ob Modulname bekannt
                        raise Exception(f'Module name: "{current_module_name}" unknown in line {line_nr}.')

                    if modules == "":                                       # alle Module sollen berechnet werden
                        save_lines = True
                    elif line[s_prog.span()[0]] != '-' and modules == '+':  # nur Module ohne Minus sollen berechnet werden
                        save_lines = True
                    elif current_prog_name.upper() == modules.upper():      # nur Module mit bestimmten Namen sollen berechnet werden
                        save_lines = True
                        end_programm = True                 #TODO drinlassen? -> berechnet nur erstes mit Modul-Name
                    elif prog_counter == module_nr:                         # nur x-tes Modul des Programm berechnen
                        save_lines = True
                        end_programm = True

    return db       
       