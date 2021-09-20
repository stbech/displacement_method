import re
import numpy as np
import warnings



#------------------------------------------------------------------------------------
# Ausgangsdatenbanken der einzelnen Module
#------------------------------------------------------------------------------------

def initiate_matqs() -> dict:
    matqs_db = {
        'matqs': {
            'globals': {
                'NKL': 1,
            },
            'materials': {},
            'cross_sections': {}, 
        },
    }
    return matqs_db



def initiate_system() -> dict:
    system_db = {
        'system': {
            'globals': {
                'HMIN': -10,
            },
            'nodes': {},
            'bars': {},  
        } 
    }
    return system_db



def initiate_load() -> dict:
    load_db = {
        'load': {
            'act': {},
            'LC': {},
        },
    }
    return load_db



def initiate_calc() -> dict:
    calc_db = {
        'calc': {
            'LC': {},
        },
    }
    return calc_db



def initiate_comb() -> dict:
    comb_db = {
        'comb': {
            'globals': {
                'KMOD': False,
            },
            'komb': {},
        },
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

def change_MATQS_GLOBALS(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    value = find_key('NKL', values, defaults)

    if value < 1 or value > 3:
        raise Exception('Service class NKL can only take values 1, 2 or 3')

    return {'globals': {'NKL': value}}



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



def create_CS_PROF(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    #TODO nicht implementiert
    raise Exception('PROF not yet implemented')



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



def intermediate_points(sdiv: float, length: float):
    # Unterteile Stab in 'sdiv' Teile -> 'sdiv'-1 Zwischenpunkte + Anfangs- und Endpunkt
    if sdiv > 0:
        sdiv = -(length//sdiv + 1) if length%sdiv != 0 else -length//sdiv
    
    sdiv = int(-sdiv)
    points = [x*length/sdiv for x in range(0,sdiv+1)]

    return points



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
    #TODO Einteilung der Stababschnitte aus wgv übernehmen
    if 'matqs' not in db:   #TODO früher abfragen -> schon wenn Modul in parse_input begonnen wird
        raise Exception('No materials or cross sections defined')

    nr = get_number(values, module_db['system']['bars'], "Bar")

    nodes = module_db['system']['nodes']
    
    if (npa := str(values['NPA'])) not in nodes:
        raise Exception(f'Node {values["NPA"]} for NPA not defined')
    if (npe := str(values['NPE'])) not in nodes:
        raise Exception(f'Node {values["NPE"]} for NPE not defined')

    dx_bar = nodes[npe]['x'] - nodes[npa]['x']
    dz_bar = nodes[npe]['z'] - nodes[npa]['z']
    
    length = np.sqrt(dx_bar**2 + dz_bar**2)
    bar_alpha = np.degrees(np.arctan2(dx_bar, dz_bar)) - 90   # da Koordinatensystem gedreht

    qnr = str(find_key('QNR', values, defaults))

    if qnr not in db['matqs']['cross_sections']:
        raise Exception(f'Cross Section: {qnr} not defined')
    else: 
        cs = db['matqs']['cross_sections'][qnr]
        E = db['matqs']['materials'][cs['MNR']]['E']*1000       # Umrechnung von MN/m² in kN/m²

    fixa = node_joint(find_key('FIXA', values, defaults), 'FIXA')
    fixe = node_joint(find_key('FIXE', values, defaults), 'FIXE')
            
    sdiv = find_key('SDIV', values, defaults)

    if not(sdiv):
        sdiv = module_db['system']['globals']['HMIN']
    else:
        if sdiv == 0:
            raise Exception('Bar divider SDIV cannot be zero')
        elif sdiv%1 != 0 and sdiv < 0:
            raise Exception('If bar divider SDIV is negativ, it must be an Integer')

    points = intermediate_points(sdiv, length)

    bez = find_key('BEZ', values, defaults)

    if find_key('NR', values, defaults) < 0: 
        old_node = module_db['system']['bars'][nr].copy()
        #TODO funktionert noch nicht für QNR
        for key, dict_key, value in zip(('NPA', 'NPE', 'SDIV', 'FIXA', 'FIXE', 'BEZ'), ('l', 'r', 'elems', 'fixa', 'fixe', 'bez'), (npa, npe, sdiv, fixa, fixe, bez)):
            if key in values:
                old_node[dict_key] = value
        
        return {'nodes' : {nr: old_node}}

    return {'bars': {nr: {
        'l': npa,
        'r': npe,
        'L': length,
        'alpha': bar_alpha,
        'EI': cs['IY']*E,
        'EA': cs['A']*E,
        'fixa': fixa,
        'fixe': fixe,
        #'elems': sdiv,
        'points': points,
        'bez': bez
    }}}



#------------------------------------------------------------------------------------
# LOAD
#------------------------------------------------------------------------------------

default_act = {
    'G': {
        'GAMU': 1.35,
        'GAMF': 1.00,
        'PSI0': 1.00,
        'PSI1': 1.00,
        'PSI2': 1.00,
        'kled': 'PERM',
        'sup': 'PERM',
    },
    'Q': {      #TODO feiner aufdrösseln nach Lastart(vordefinierte Werte für Q_, W, S (_L, _H))
        'GAMU': 1.50,
        'GAMF': 0.00,
        'PSI0': 0.70,
        'PSI1': 0.50,
        'PSI2': 0.30,
        'kled': 'MEDI',
        'sup': 'COND',
    }
}


def create_ACT(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 

    elems = {
        'GAMU': find_key('GAMU', values, defaults),
        'GAMF': find_key('GAMF', values, defaults),
        'PSI0': find_key('PSI0', values, defaults),
        'PSI1': find_key('PSI1', values, defaults),
        'PSI2': find_key('PSI2', values, defaults),
        'kled': find_key('KLED', values, defaults),
        'sup': find_key('SUP', values, defaults),
    }

    act = find_key('TYP', values, defaults).upper()
    #TODO check TYP
    part = find_key('PART', values, defaults)

    if part not in ('G', 'Q'):
        raise Exception(f'Only G or Q are valid literals for PART')

    for key, val in elems.items(): 
        if val == None:
            elems[key] = default_act[part][key]
        elif type(val) == str and key != 'bez':
            elems[key] = elems[key].upper()
        
    if elems['kled'] not in ('PERM', 'LONG', 'MEDI', 'SHOR', 'MSHO', 'VSHO'):
        raise Exception(f'{elems["kled"]} is not a valid literal for KLED')

    if part == 'G':
        for key in elems:
            if key == 'sup':
                continue
            if default_act['G'][key] != elems[key]:
                if key.startswith('PSI'):
                    warnings.warn(f'{key} {elems[key]} seems not fitting for dead load, but has no impact (in ACT {act}).')
                else:
                    warnings.warn(f'{key} {elems[key]} seems not fitting for dead load (in ACT {act}).')

        if elems['sup'] not in ('PERM', 'PERC', 'ALEX'):
            raise Exception(f'Dead loads can only have PERM, PERC or ALEX for SUP')

    elif part == 'Q':
        for key in ('GAMU', 'GAMF'):
            if default_act['Q'][key] != elems[key]:
                warnings.warn(f'{key} {elems[key]} seems not fitting for live load (in ACT {act}).')

        if elems['kled'] == 'PERM':
                warnings.warn(f'KLED {elems["kled"]} seems not fitting for live load (in ACT {act}).')

        for key in ('PSI0', 'PSI1', 'PSI2'):
            if elems[key] > 1:
                warnings.warn(f'The value for {key} is greater than one (in ACT {act}).')
            if elems[key] < 0:
                warnings.warn(f'The value for {key} is smaller than zero (in ACT {act}).')

        if elems['sup'] not in ('COND', 'EXCL'):
            raise Exception(f'Live loads can only have COND or EXCL for SUP')

    elems['part'] = part
    elems['bez'] = find_key('BEZ', values, defaults)

    return {'act': {act: elems}}



def create_LF(db: dict, module_db: dict, values: dict, defaults: dict) -> dict: 
    nr = get_number(values, module_db['load']['LC'], "Loadcase")

    act = find_key('TYP', values, defaults).upper()

    if act not in module_db['load']['act']:
        raise Exception(f'Action {act} not defined')

    fakt = find_key('FAKT', values, defaults)
    fakg = find_key('FAKG', values, defaults)
    bez = find_key('BEZ', values, defaults)

    return {'LC': {nr: {
        'act': act,
        'fakt': fakt,
        'fakg': fakg,
        'bez': bez,
        'node': [],
        'bar': [],
    }}}



def add_KNOT(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    if not(len(module_db['load']['LC'])):
        raise Exception(f'KNOT before LF defined')
        
    last_LC = list(module_db['load']['LC'])[-1]
    LC = module_db['load']['LC'][last_LC]

    if LC['fakg'] != 0:
        warnings.warn('Loads for loadcases with FAKG unequal 0 are ignored (in LF {last_LC}).')

    nr = str(find_key('NR', values, defaults))

    if nr not in db['system']['nodes']:
        raise Exception(f'Node {nr} not defined')

    val = find_key('P1', values, defaults)*LC['fakt']
    typ = find_key('TYP', values, defaults).upper()

    force_keys = ('PG', 'PZZ', 'PXX', 'PZ', 'PX')
    mom_keys = ('MYY', 'MY')
    not_supported = ('WXX', 'WZZ', 'DYY', 'WX', 'WZ', 'DY')


    if typ in force_keys:
        if 'P2' in values or 'P3' in values:
            warnings.warn(f'For TYP {typ} only the value of P1 is used (in LF {last_LC}).')

        if typ == 'PZ' or typ == 'PX':
            alpha_zero = db['system']['nodes'][nr]['alpha']
        else:
            alpha_zero = 0

        moment = 0
        
        if typ == 'PG' or typ.startswith('PZ'):
            alpha = alpha_zero + 90
            
            if 'EXX' in values:
                moment = -val*values['EXX']

        elif typ.startswith('PX'):
            alpha = alpha_zero + 180

            if 'EZZ' in values:
                moment = val*values['EZZ']

        nodal_loading = [{'nr': nr, 'val': val, 'type': 'F', 'alpha': alpha}]

        if moment:
            nodal_loading.append({'nr': nr, 'val': moment, 'type': 'M', 'alpha': 0})


    elif typ in mom_keys:
        if 'P2' in values or 'P3' in values:
            warnings.warn(f'For TYP {typ} only the value of P1 is used (in LF {last_LC}).')
        if 'EXX' in values or 'EZZ' in values:
            warnings.warn(f'Eccentricity for moments makes no sense (in LF {last_LC}).')

        nodal_loading = [{'nr': nr, 'val': val, 'type': 'M', 'alpha': 0}]


    elif typ == 'PP' or typ == 'P':
        if 'P3' in values:
            warnings.warn(f'For TYP {typ} only the values of P1 and P2 are used (in LF {last_LC}).')

        val2 = find_key('P2', values, defaults)*LC['fakt']

        moment = 0
        alpha = 0 if typ == 'PP' else db['system']['nodes'][nr]['alpha']

        if val2 == 0:
            if 'EXX' in values:
                moment += -val2*values['EXX']

            nodal_loading = [{'nr': nr, 'val': val, 'type': 'F', 'alpha': alpha + 180}]
        elif val == 0:
            if 'EZZ' in values:
                moment += val*values['EZZ']

            nodal_loading = [{'nr': nr, 'val': val2, 'type': 'F', 'alpha': alpha + 90}]
        else:
            nodal_loading = [{'nr': nr, 'val': val, 'type': 'F', 'alpha': alpha + 180}, {'nr': nr, 'val': val2, 'type': 'F', 'alpha': alpha + 90}]

        if moment:
            nodal_loading.append({'nr': nr, 'val': moment, 'type': 'M', 'alpha': 0})


    elif typ == 'VV' or typ == 'V':
        val2 = find_key('P2', values, defaults)*LC['fakt']

        moment = find_key('P3', values, defaults)*LC['fakt']
        alpha = 0 if typ == 'VV' else db['system']['nodes'][nr]['alpha']

        if val2 == 0:
            if 'EZZ' in values:
                moment += val*values['EZZ']

            nodal_loading = [{'nr': nr, 'val': val, 'type': 'F', 'alpha': alpha + 180}]
        elif val == 0:
            if 'EXX' in values:
                moment += -val2*values['EXX']

            nodal_loading = [{'nr': nr, 'val': val2, 'type': 'F', 'alpha': alpha + 90}]
        else:
            if 'EXX' in values:
                moment += -val2*values['EXX']

            if 'EZZ' in values:
                moment += val*values['EZZ']

            nodal_loading = [{'nr': nr, 'val': val, 'type': 'F', 'alpha': alpha + 180}, {'nr': nr, 'val': val2, 'type': 'F', 'alpha': alpha + 90}]

        if moment:
            nodal_loading.append({'nr': nr, 'val': moment, 'type': 'M', 'alpha': 0})


    elif typ in not_supported:
        raise Exception(f'Support displacements currently not supported')
    else:
        raise Exception(f'Unknown literal {typ} for TYP')

    
    LC['node'].extend(nodal_loading)

    return {'LC': {last_LC: LC}}


#TODO multiply with fakt -> erledigt prüfe Ergebnisse
def add_STAB(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    if not(len(module_db['load']['LC'])):
        raise Exception(f'STAB before LF defined')
        
    last_LC = list(module_db['load']['LC'])[-1]
    LC = module_db['load']['LC'][last_LC]

    if LC['fakg'] != 0:
        warnings.warn('Loads for loadcases with FAKG unequal 0 are ignored (in LF {last_LC}).')

    nr = str(find_key('NR', values, defaults))

    if nr not in db['system']['bars']:
        raise Exception(f'Bar {nr} not defined')

    start = find_key('PA', values, defaults)*LC['fakt']

    if 'PE' not in values:
        end = start
    else:
        end = values['PE']*LC['fakt']

    typ = find_key('TYP', values, defaults).upper()

    for key in ('A', 'L', 'MESS'):
        if key in values:
            raise Exception('Sectionwise defined functions currently not supported')


    not_supported = ('EX', 'KY', 'DT', 'DTZ')

    if typ == 'PG' or typ == 'PZZ':
        bar_alpha = np.radians(db['system']['bars'][nr]['alpha'])
        bar_loading = {'nr': nr, 'type': typ, 'p_zl': np.cos(bar_alpha)*start, 'p_zr': np.cos(bar_alpha)*end, 'p_xl': -np.sin(bar_alpha)*start, 'p_xr': -np.sin(bar_alpha)*end}

    elif typ == 'PXX':
        bar_alpha = np.radians(db['system']['bars'][nr]['alpha'])
        bar_loading = {'nr': nr, 'type': typ, 'p_zl': np.sin(bar_alpha)*start, 'p_zr': np.sin(bar_alpha)*end, 'p_xl': np.cos(bar_alpha)*start, 'p_xr': np.cos(bar_alpha)*end}

    elif typ == 'PZ':
        bar_loading = {'nr': nr, 'type': typ, 'p_zl': start, 'p_zr': end, 'p_xl': 0, 'p_xr': 0}

    elif typ == 'PX':
        bar_loading = {'nr': nr, 'type': typ, 'p_zl': 0, 'p_zr': 0, 'p_xl': start, 'p_xr': end}

    elif typ in not_supported:
        raise Exception(f'Bar curvature and elongation currently not supported')
    else:
        raise Exception(f'Unknown literal {typ} for TYP')

    
    LC['bar'].append(bar_loading)
    
    return {'LC': {last_LC: LC}}



def add_STEL(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:

    raise Exception(f'STEL is currently not supported')



def copy_LC(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:

    if not(len(module_db['load']['LC'])):
        raise Exception(f'COPY before LF defined')
        
    last_LC = list(module_db['load']['LC'])[-1]
    LC = module_db['load']['LC'][last_LC]

    nr = str(find_key('NR', values, defaults))

    if nr not in module_db['load']['LC']:
        raise Exception(f'Loadcase {nr} not defined')

    copy_LC = module_db['load']['LC'][nr]

    fakt = find_key('FAKT', values, defaults)

    for node in copy_LC['node']:
        LC['node'].append(node.copy())
        LC['node'][-1]['val'] *= fakt*LC['fakt'] #LC['node'][-1]['val']

    for bar in copy_LC['bar'].copy():
        LC['bar'].append(bar.copy())
        
        for key in ('p_zl', 'p_zr', 'p_xl', 'p_xr'):
            LC['bar'][-1][key] *= fakt*LC['fakt']

    return {'LC': {last_LC: LC}}


#TODO TYP in LF nicht benötigt machen, stattdessen am Ende des Moduls oder erst bei COMB prüfen ob alle LF einer Einwirkung zugeordnet

#------------------------------------------------------------------------------------
# CALC
#------------------------------------------------------------------------------------

def add_LC_calc(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    nr = find_key('NR', values, defaults)

    #TODO Eigengewicht berechnen hier oder in load am Ende des Moduls (prüfe am Ende von load auch ob Lastfälle ohne Last)

    if nr.upper() == 'ALLE':
        LC_calc = {}

        for LC in db['load']['LC']:
            LC_calc[LC] = None

    elif re.match(r'^(?:\d\s*,\s*)*\d$', nr):
        LC_calc = {}

        for LC in nr.split(','):
            LC = LC.strip()

            if LC not in db['load']['LC']:
                raise Exception(f'Loadcase {LC} not defined')
            else:
                LC_calc[LC] = None

    elif nr.isdecimal():
        if nr not in db['load']['LC']:
            raise Exception(f'Loadcase {nr} not defined')
        
        LC_calc = {nr: None}

    else:
        raise Exception(f'Literal {nr} for LF unknown')

    
    return {'LC': LC_calc}



#------------------------------------------------------------------------------------
# COMB
#------------------------------------------------------------------------------------

def change_COMB_GLOBALS(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    value = find_key('KLED', values, defaults).upper()

    if value == 'JA':
        return {'globals': {'KMOD': True}}
    elif value == 'NEIN':
        return {'globals': {'KMOD': False}}
    else:
        raise Exception(f'Unknown literal {value} for KLED')



def create_KOMB(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:
    nr = get_number(values, module_db['comb']['komb'], "Combination")

    extr = find_key('EXTR', values, defaults).upper()

    if extr not in ('STAN', 'DESI', 'RARE', 'FREQ', 'PERM'):
        raise Exception(f'Unknown literal {extr} for EXTR')

    return {'komb': {nr: {
        'extr': extr,
        'acts': [],
        'LC': {},
        'res': {},
    }}}



def change_ACT(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:

    if not(len(module_db['comb']['komb'])):
        raise Exception(f'ACT before KOMB defined')

    act = find_key('TYP', values, defaults)

    if act not in db['load']['act']:
        raise Exception(f'Action {act} not defined')

    last_komb = list(module_db['comb']['komb'])[-1]
    komb = module_db['comb']['komb'][last_komb]
    
    komb['acts'].append(act)

    return {'komb': {last_komb: komb}}



def add_LC_comb(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:

    if not(len(module_db['comb']['komb'])):
        raise Exception(f'LF before KOMB defined')

    nr = str(find_key('NR', values, defaults))

    if nr not in db['load']['LC'] and nr not in ('-1', '0'):
        raise Exception(f'Loadcase {nr} not defined')

    last_komb = list(module_db['comb']['komb'])[-1]
    komb = module_db['comb']['komb'][last_komb]

    if nr in komb['LC']:
        warnings.warn(f'Loadcase {nr} multiple times in KOMB {last_komb}. Only last apperance will be considered.')

    if len(module_db['comb']['komb'][last_komb]['acts']):
        last_act = module_db['comb']['komb'][last_komb]['acts'][-1] 
    else:
        last_act = db['load']['LC'][nr]['act']

    sup = find_key('TYPE', values, defaults)

    if sup:
        part = db['load']['act'][last_act]['part']  
        sup = sup.upper()

        if (part == 'G') and not(sup in ('G', 'PERM', 'PERC', 'ALEX') or sup.startswith('AG')):
            raise Exception(f'Loadcases with PART G in ACT can only have G, PERM, PERC, ALEX or AG* for TYPE')
        elif (part == 'Q') and not(sup in ('Q', 'COND', 'EXCL') or sup.startswith('A')):
            raise Exception(f'Loadcases with PART Q in ACT can only have Q, COND, EXCL or A* for TYPE')

        if sup.startswith('AG'):
            if not(sup[2:].isdecimal() and len(sup[2:]) <= 2):
                raise Exception(f'Unknown literal {sup} for TYPE')
        elif sup.startswith('A') and sup != 'ALEX':
            if not(sup[1:].isdecimal() and len(sup[1:]) <= 2):
                raise Exception(f'Unknown literal {sup} for TYPE')
    else:
        sup = db['load']['act'][last_act]['sup']

    if nr == '-1': 
        for nr_LC, LC in db['load']['LC'].items():
            if LC['act'] == last_act:
                komb['LC'][nr_LC] = (last_act, sup.upper())
    elif nr == '0': 
        for nr_LC, LC in db['load']['LC'].items():
            if LC['act'].startswith(last_act + '_') or LC['act'] == last_act:
                komb['LC'][nr_LC] = (last_act, sup.upper())
    else:
        komb['LC'][nr] = (last_act, sup.upper())

    return {'komb': {last_komb: komb}}



def add_SUPP(db: dict, module_db: dict, values: dict, defaults: dict) -> dict:

    if not(len(module_db['comb']['komb'])):
        raise Exception(f'SUPP before KOMB defined')

    nr_komb = str(find_key('KOMB', values, defaults))
    
    if nr_komb not in module_db['comb']['komb']:
        raise Exception(f'Combination {nr_komb} not defined')

    komb = module_db['comb']['komb'][nr_komb]

    etyp = find_key('ETYP', values, defaults).upper()
    extr = find_key('EXTR', values, defaults).upper()
    zust = find_key('ZUST', values, defaults).upper()
    #bez =find_key('BEZ', values, defaults)

    if extr not in ('MAX', 'MIN', 'MAMI'):
        raise Exception(f'Unknown literal {extr} for EXTR')

    if etyp == 'KNOT':
        if 'node' not in komb['res']:
            komb['res']['node'] = {}

        if zust in ('PX', 'PZ', 'MY', 'UX', 'UZ', 'URY'):
            if extr == 'MAMI':
                komb['res']['bar'][zust] = {'max': {}, 'min': {}}
            elif extr == 'MIN':
                komb['res']['bar'][zust] = {'min': {}}
            elif extr == 'MAX':
                komb['res']['bar'][zust] = {'max': {}}
        else:
            raise Exception(f'Unknown literal {zust} for ZUST')

    elif etyp == 'STAB':
        if 'bar' not in komb['res']:
            komb['res']['bar'] = {}

        if zust in ('N', 'VZ', 'MY', 'UX', 'UZ', 'URY'):
            if extr == 'MAMI':
                komb['res']['bar'][zust] = {'max': {}, 'min': {}}
            elif extr == 'MIN':
                komb['res']['bar'][zust] = {'min': {}}
            elif extr == 'MAX':
                komb['res']['bar'][zust] = {'max': {}}
        else:
            raise Exception(f'Unknown literal {zust} for ZUST')

    elif etyp == 'FEDE':
        if 'spring' not in komb['res']:
            komb['res']['spring'] = {}

        if zust in ('P', 'PT', 'M'):
            if extr == 'MAMI':
                komb['res']['bar'][zust] = {'max': {}, 'min': {}}, 
            elif extr == 'MIN':
                komb['res']['bar'][zust] = {'min': {}}
            elif extr == 'MAX':
                komb['res']['bar'][zust] = {'max': {}}
        else:
            raise Exception(f'Unknown literal {zust} for ZUST')

    else:
        raise Exception(f'Unknown literal {etyp} for ETYP')

    return {'komb': {nr_komb: komb}}


#TODO zur Ausgabe: suche nach DESI und nimm erste KOMB-NR mit DESI
#TODO falls keine LF zu bestimmten ACT: wähle alle aus