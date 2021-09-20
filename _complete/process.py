import displace_method
from combination import combine
import json
from copy import deepcopy



#--------------------------------------------------------------------------------
### Methods for Loading in Saving Database
#--------------------------------------------------------------------------------


def save_database(db: dict, filename: str) -> None:
    """Save database zu json-file"""     
    json_db = deepcopy(db)

    # Alle numpy-Arrays müssen in eine Liste umgewandelt werden
    if 'wgv' in json_db['system']:
        json_db['system']['wgv']['a'] = db['system']['wgv']['a'].tolist()
        json_db['system']['wgv']['k'] = db['system']['wgv']['k'].tolist()
        json_db['system']['wgv']['K'] = db['system']['wgv']['K'].tolist()

    for lc in json_db['load']['LC']:
        if 'wgv' in json_db['load']['LC'][lc]:
            json_db['load']['LC'][lc]['wgv']['s_0'] = db['load']['LC'][lc]['wgv']['s_0'].tolist()
            json_db['load']['LC'][lc]['wgv']['P_0'] = db['load']['LC'][lc]['wgv']['P_0'].tolist()
            json_db['load']['LC'][lc]['wgv']['P_bar'] = db['load']['LC'][lc]['wgv']['P_bar'].tolist()
            json_db['load']['LC'][lc]['wgv']['P'] = db['load']['LC'][lc]['wgv']['P'].tolist()

    for lc in json_db['calc']['LC']:
        if json_db['calc']['LC'][lc]:
            json_db['calc']['LC'][lc]['V'] = db['calc']['LC'][lc]['V'].tolist()
            json_db['calc']['LC'][lc]['v'] = db['calc']['LC'][lc]['v'].tolist()
            json_db['calc']['LC'][lc]['s_II'] = db['calc']['LC'][lc]['s_II'].tolist()
            json_db['calc']['LC'][lc]['s_I'] = db['calc']['LC'][lc]['s_I'].tolist()

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(json_db, f, indent=4)



def load_database(filename: str) -> dict:
    """Load database from json-file"""
    with open(filename, 'r') as f:
        db = json.load(f)
    
    # Umwandlung nicht benötigt

    return db


#--------------------------------------------------------------------------------
### Main Methods
#--------------------------------------------------------------------------------


# kein return: diese Funktionen allein für Manipulation der DB verantwortlich
# für alle: Eingabedatei in db umsetzen

def calculate_matqs(db: dict):
    #calculate_querschnittswerte()
    pass    # Querschnitte: Fläche und Trägheitsmoment


#TODO system erst berechnen, wenn alle Stäbe über mehrere Module berechnet -> also erst wenn ase
def calculate_system(db: dict):
    #db['system']['bars'] = displace_method.calculate_bars(db['system']['bars'], db['system']['nodes'])
    db['system']['springs'] = displace_method.springs(db)

    db['system']['wgv'] = dict()
    a, pos = displace_method.kinematic_transformation_matrix(db)
    db['system']['wgv']['a'] = a
    db['system']['wgv']['node_deforms'] = pos

    db['system']['wgv']['k'] = displace_method.stiffness_matrix(db)
    db['system']['wgv']['K'] = displace_method.total_stiffness_matrix(db)
 


def calculate_load(db: dict):
    for item in db['load']['LC'].items():
        db['load']['LC'][item[0]]['wgv'] = dict()
        db['load']['LC'][item[0]]['wgv']['s_0'] = displace_method.festhaltekraftgroessen(db, item[0])
        db['load']['LC'][item[0]]['wgv']['P_0'] = displace_method.ersatzknotenkraefte(db, item[0])
        db['load']['LC'][item[0]]['wgv']['P_bar'] = displace_method.knotenkraefte(db, item[0])
        db['load']['LC'][item[0]]['wgv']['P'] = displace_method.load_vector(db, item[0])



def calculate_calc(db:dict):
    for key, item in db['calc']['LC'].items():
        if item == None:
            db['calc']['LC'][key] = dict()
            db['calc']['LC'][key] = dict()
            db['calc']['LC'][key]['V'] = displace_method.node_deformations(db, key)
            db['calc']['LC'][key]['v'] = displace_method.stabendweggroessen(db, key)
            db['calc']['LC'][key]['s_II'] = displace_method.stabendkraftgroessen(db, key)
            db['calc']['LC'][key]['s_I'] = displace_method.convert_kraftgroessen(db, key)
            db['calc']['LC'][key]['s'] = displace_method.schnittgroessen(db, key)

            w_dict = displace_method.deflection(db, key)
            #db['calc'][key]['s']['w'] = dict()
            for bar, w_list in w_dict.items():
                db['calc']['LC'][key]['s'][bar]['w'] = w_list
            # WGV auflösen, Schnittgrößen speichern



def calculate_comb(db: dict):
    for komb_nr, komb in db['comb']['komb'].items():
        if db['comb']['globals']['KLED']:
            kled = {'PERM': [], 'LONG': [], 'MEDI': [], 'SHOR': [], 'MSHO': [], 'VSHO': []}

            for nr_lc, lc in komb['LC'].items():
                kled_act = db['load']['act'][lc[0]]['kled']
                kled[kled_act].append(nr_lc)

            LCs = []

            for key, value in kled.items():
                if value:
                    LCs.extend(value)
                    db = combine(db, komb_nr, key, LCs)

        else:
            db = combine(db, komb_nr, 'STAN', LCs)



def calculate(db: dict, module_name: str):
    if module_name == 'MATQS':
        pass#calculate_matqs(db)
    elif module_name == 'SYSTEM':
        calculate_system(db)
    elif module_name == 'LOAD':
        calculate_load(db)
    elif module_name == 'CALC':
        calculate_calc(db)
    elif module_name == 'COMB':
        calculate_comb(db)
