import re
import numpy as np



#------------------------------------------------------------------------------------
# Ausgangsdatenbanken der einzelnen Module
#------------------------------------------------------------------------------------

def initiate_matqs() -> dict:
    matqs_db = {
        'matqs': {
            'materials': {},
            'cross_sections': {}, 
        },
    }
    return matqs_db



def initiate_system() -> dict:
    system_db = {
        'system': {
            'globals': {
                'HMIN': -10
            },
            'nodes': {},
            'bars': {},  
        } 
    }
    return system_db



def initiate_load() -> dict:
    load_db = {
        'load': {},
    }
    return load_db



def initiate_calc() -> dict:
    calc_db = {
        'calc': {},
    }
    return calc_db



def initiate_comb() -> dict:
    comb_db = {
        'comb': {},
    }
    return comb_db



#------------------------------------------------------------------------------------
# Hilfsfunktionen
#------------------------------------------------------------------------------------

def check_formula(string: str) -> bool:
    form_char = ( '*', '/', '+', '-',)
    found = False
    for char in form_char:
        if char in string:
            found = True

    return found



def split_no_string(string: str, sep: str = None) -> list:
    sep = " " if sep == None else sep   # if None split on and remove any whitespaces
    str_char = ("'", '"')               # ignore whitespace between these characters
    split_list = []
    start_index = 0
    recording = not(string[0] == sep)
    in_string, cur_str_char = False, None
    word = ""
    #TODO Exception falls Anführungszeichen nicht geschlossen
    for i, char in enumerate(string):
        if char in str_char:
            if not(in_string):
                cur_str_char = char
                in_string = not(in_string) 
            elif cur_str_char == char:
                cur_str_char = ""
                in_string = not(in_string)

        if not(in_string):
            if char == sep:
                start_index = i + 1
            if char == sep and recording:
                recording = False
                split_list.append(word)
                word = ""        

        if start_index == i:
            recording = True

        if recording:
            word += char

    if not(sep == " " and word == ""):
        split_list.append(word)
    
    if in_string:
        raise Exception()

    return split_list



def find_key(string: str, search_dict: dict, default_dict: dict, index: int = 1):
    return search_dict.get(string, default_dict[string][index])



def get_number(values: dict, other_numbers: dict, error_text: str) -> str:
    if 'NR' in values:
        nr = values['NR']
        
        if str(nr) in other_numbers and nr > 0:
            raise Exception(f'{error_text} {nr} already defined')
        elif str(abs(nr)) not in other_numbers and nr < 0:
            raise Exception(f'{error_text} {abs(nr)} can not be altered, because it is not defined')

        nr = str(abs(nr))
    else:
        if len(other_numbers):
            int_nrs = [int(x) for x in other_numbers]
            nr = str(min(set(range(1, len(other_numbers) + 2)) - set(int_nrs)))
        else:
            nr = '1'

    return nr



def check_literal(literal: str, lit_types: tuple, error_text: str) -> list:
    i = 0
    split_lits = []
    while i < len(literal[1:]):
        if literal[i] + literal[i+1] in lit_types:
            split_lits.append(literal[i] + literal[i+1])
            i += 1
        elif literal[i] in lit_types:
            split_lits.append(literal[i])

        i += 1

    if literal[-1] in lit_types and i != len(literal):
        split_lits.append(literal[-1])

    if len(''.join(split_lits)) != len(literal):
        raise Exception(f'Could not decode literal for {error_text}')
    
    return split_lits



#------------------------------------------------------------------------------------
# MATQS
#------------------------------------------------------------------------------------

def create_MAT(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    nr = get_number(values, module_db['matqs']['materials'], "Material")

    return {'materials' : {nr: {
        'E': find_key('E', values, defaults), 
        'gamma': find_key('GAM', values, defaults), 
        'alpha_T': find_key('ALFA', values, defaults),
        'bez': find_key('BEZ', values, defaults),
    }}}



def create_CS_QUER(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    nr = get_number(values, module_db['matqs']['cross_sections'], "Cross Section")
    mnr = str(find_key('MNR', values, defaults))

    if mnr not in module_db['matqs']['materials']:
        raise Exception(f'Material {mnr} not defined')
    #else:
        #E = module_db['matqs']['materials'][mnr]

    A = find_key('A', values, defaults)
    I_y = find_key('IY', values, defaults)
    if not('IY'):
        I_y = A**3/12
        

    return {'cross_sections' : {nr: {
        'MNR': mnr, 
        'A': A,
        'IY': I_y,
        'definition': 'QUER',
        'bez': find_key('BEZ', values, defaults),
    }}}



def create_CS_QB(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    nr = get_number(values, module_db['matqs']['cross_sections'], "Cross Section")
    mnr = str(find_key('MNR', values, defaults))

    if mnr not in module_db['matqs']['materials']:
        raise Exception(f'Material {mnr} not defined')
    #else:
        #E = module_db['matqs']['materials'][mnr]

    h = find_key('H', values, defaults)
    b = find_key('B', values, defaults)

    A = h*b
    I_y = b*h**3/12        

    return {'cross_sections' : {nr: {
        'MNR': mnr, 
        'A': A,
        'IY': I_y,
        'definition': 'QB',
        'bez': find_key('BEZ', values, defaults),
    }}}



def create_CS_QC(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    nr = get_number(values, module_db['matqs']['cross_sections'], "Cross Section")
    mnr = str(find_key('MNR', values, defaults))

    if mnr not in module_db['matqs']['materials']:
        raise Exception(f'Material {mnr} not defined')
    #else:
        #E = module_db['matqs']['materials'][mnr]

    d = find_key('D', values, defaults)
    t = find_key('T', values, defaults)
    r = 0 if t == 0 else d/2 - t

    A = np.pi*((d/2)**2-r**2)
    I_y = np.pi/4*((d/2)**4-r**4)      

    return {'cross_sections' : {nr: {
        'MNR': mnr, 
        'A': A,
        'IY': I_y,
        'definition': 'QC',
        'bez': find_key('BEZ', values, defaults),
        }}}



#------------------------------------------------------------------------------------
# SYSTEM
#------------------------------------------------------------------------------------

def change_SYSTEM_GLOBALS(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    value = find_key('HMIN', values, defaults)
    
    if value == 0:
        raise Exception('Bar divider HMIN cannot be zero')
    elif value%1 != 0 and value < 0:
        raise Exception('If bar divider HMIN is negativ, it must be an Integer')

    return {'globals': {'HMIN': value}}



def support(string: str) -> dict:
    sup = {'x': 0, 'z': 0, 'y': 0}
    
    if not(string):
        return sup

    lit_types = ('PP', 'PX', 'PZ', 'MY', 'MM', 'M', 'FF', 'F')
    error_text = 'FIX'
    try:
        sup_literals = check_literal(string, lit_types, error_text)
    except: 
        raise
    
    sup_types = sup_literals[:]

    for sup_type in sup_literals:
        if sup_type.upper() == 'PP':
            sup_types.remove(sup_type)
            sup_types.extend(['PX', 'PZ'])
        elif sup_type.upper() == 'FF' or sup_type.upper() == 'F':
            sup_types.remove(sup_type)
            sup_types.extend(['PX', 'PZ', 'MY'])
        elif sup_type.upper() == 'M' or sup_type.upper() == 'MM':
            sup_types.remove(sup_type)
            sup_types.append('MY')

    if len(sup_types) - len(set(sup_types)):
        raise Warning(f'Literal for FIX evaluates to duplicate supports')
    
    for sup_type in sup_types:
        if sup_type.upper() == 'PX':
            sup['x'] = -1
        elif sup_type.upper() == 'PZ':
            sup['z'] = -1
        elif sup_type.upper() == 'MY':
            sup['y'] = -1
        #else:
            #raise Exception(f'Unknown support literal {sup_type}')

    return sup



def create_SPT(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    try:
        sup = support(find_key('FIX', values, defaults))
    except:
        raise

    nr = get_number(values, module_db['system']['nodes'], "Node")

    x = find_key('X', values, defaults)
    z = find_key('Z', values, defaults)
    
    alpha = find_key('ALPH', values, defaults)

    if 'NX' in values or 'NZ' in values:
        if 'ALPH' in values:
            raise Exception(f'Either ALPH or NX and NZ can be defined')

        nx = find_key('NX', values, defaults)
        nz = find_key('NZ', values, defaults)
        alpha = np.degrees(np.arctan2(nx,nz)) - 90  

    bez = find_key('BEZ', values, defaults)

    if find_key('NR', values, defaults) < 0: 
        old_node = module_db['system']['nodes'][nr].copy()
        #TODO funktionert noch nicht für NX, NZ
        for key, dict_key, value in zip(('X', 'Z', 'FIX', 'ALPH', 'BEZ'), ('x', 'z', 'sup', 'alpha', 'bez'), (x, z, sup, alpha, bez)):
            if key in values:
                old_node[dict_key] =  value
        
        return {'nodes' : {nr: old_node}}

    return {'nodes' : {nr: {
        'x': x, 
        'z': z, 
        'sup': sup,
        'alpha': alpha,
        'bez': bez,
    }}}


#TODO SPTS mit Nummer, um später ändern zu können
def add_SPTS(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    if not(len(module_db['system']['nodes'])):
        raise Exception(f'SPTS before SPT defined')
        
    last_SPT = list(module_db['system']['nodes'])[-1]
    for key, value in values.items():
        if value < 0:
            values[key] = -1
    
    SPT = module_db['system']['nodes'][last_SPT]
    SPT['sup'] = {'x': find_key('CP', values, defaults), 'z': find_key('CQ', values, defaults), 'y': find_key('CM', values, defaults), }
    
    return {'nodes': {last_SPT: SPT}}



def node_joint(string: str, error_text: str) -> dict:
    joint = {'N': -1, 'V': -1, 'M': -1}
    
    if not(string):
        return joint

    lit_types = ('N', 'V', 'VZ', 'PP', 'M', 'MY', 'MM')

    try:
        joint_literals = check_literal(string, lit_types, error_text)
    except: 
        raise

    joint_types = joint_literals[:]

    for joint_type in joint_literals:
        if joint_type.upper() == 'PP':
            joint_types.remove(joint_type)
            joint_types.extend(['N', 'V'])
        elif joint_type.upper() == 'VZ':
            joint_types.remove(joint_type)
            joint_types.append('V')
        elif joint_type.upper() == 'MY' or joint_type.upper() == 'MM':
            joint_types.remove(joint_type)
            joint_types.append('M')

    if len(joint_types) - len(set(joint_types)):
        raise Warning(f'Literal for FIX evaluates to duplicate supports')
    
    for joint_type in joint_types:
        if joint_type.upper() == 'N':
            joint['N'] = 0
        elif joint_type.upper() == 'V':
            joint['V'] = 0
        elif joint_type.upper() == 'M':
            joint['M'] = 0

    return joint



def create_SLN(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    if 'matqs' not in db:   #TODO früher abfragen -> schon wenn Modul in parse_input begonnen wird
        raise Exception('No materials or cross sections defined')

    nr = get_number(values, module_db['system']['bars'], "Bar")
    
    if (npa := str(values['NPA'])) not in module_db['system']['nodes']:
        raise Exception(f'Node {values["NPA"]} for NPA not defined')
    if (npe := str(values['NPE'])) not in module_db['system']['nodes']:
        raise Exception(f'Node {values["NPE"]} for NPE not defined')

    qnr = str(find_key('QNR', values, defaults))

    if qnr not in db['matqs']['cross_sections']:
        raise Exception(f'Cross Section: {qnr} not defined')
    else: 
        cs = db['matqs']['cross_sections'][qnr]
        E = db['matqs']['materials'][cs['MNR']]['E']/1000       # Umrechnung von MN/m² in kN/m²

    fixa = node_joint(find_key('FIXA', values, defaults), 'FIXA')
    fixe = node_joint(find_key('FIXE', values, defaults), 'FIXE')
            
    sdiv = find_key('SDIV', values, defaults)

    if not(sdiv):
        sdiv = module_db['system']['globals']['HMIN']

    bez = find_key('BEZ', values, defaults)

    if find_key('NR', values, defaults) < 0: 
        old_node = module_db['system']['bars'][nr].copy()
        #TODO funktionert noch nicht für QNR
        for key, dict_key, value in zip(('NPA', 'NPE', 'SDIV', 'FIXA', 'FIXE', 'BEZ'), ('l', 'r', 'elems', 'fixa', 'fixe', 'bez'), (npa, npe, sdiv, fixa, fixe, bez)):
            if key in values:
                old_node[dict_key] =  value
        
        return {'nodes' : {nr: old_node}}

    return {'bars': {nr: {
        'l': npa,
        'r': npe,
        'EI': cs['IY']*E,
        'EA': cs['A']*E,
        'fixa': fixa,
        'fixe': fixe,
        'elems': sdiv,
        'bez': bez
    }}}



#------------------------------------------------------------------------------------
# LOAD
#------------------------------------------------------------------------------------
