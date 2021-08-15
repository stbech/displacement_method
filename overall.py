import wgv
import json
from copy import deepcopy



#--------------------------------------------------------------------------------
### Methods for Loading in Saving Database
#--------------------------------------------------------------------------------


def save_database(db: dict, filename: str) -> None:
    """Save database zu json-file"""     
    json_db = deepcopy(db)

    # Alle numpy-Arrays müssen in eine Liste umgewandelt werden
    json_db['system']['wgv']['a'] = db['system']['wgv']['a'].tolist()
    json_db['system']['wgv']['k'] = db['system']['wgv']['k'].tolist()
    json_db['system']['wgv']['K'] = db['system']['wgv']['K'].tolist()

    for lc in json_db['load']['LC']:
        json_db['load']['LC'][lc]['wgv']['s_0'] = db['load']['LC'][lc]['wgv']['s_0'].tolist()
        json_db['load']['LC'][lc]['wgv']['P_0'] = db['load']['LC'][lc]['wgv']['P_0'].tolist()
        json_db['load']['LC'][lc]['wgv']['P_bar'] = db['load']['LC'][lc]['wgv']['P_bar'].tolist()
        json_db['load']['LC'][lc]['wgv']['P'] = db['load']['LC'][lc]['wgv']['P'].tolist()

    for lc in json_db['calc']:
        json_db['calc'][lc]['V'] = db['calc'][lc]['V'].tolist()
        json_db['calc'][lc]['v'] = db['calc'][lc]['v'].tolist()
        json_db['calc'][lc]['s_II'] = db['calc'][lc]['s_II'].tolist()
        json_db['calc'][lc]['s_I'] = db['calc'][lc]['s_I'].tolist()

    with open(filename, 'w') as f:
        json.dump(json_db, f, indent=4)



def load_database( filename: str) -> dict:
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



def calculate_system(db: dict):
    # EI und EA berechnen, falls nicht explizit vorgegeben
    db['system']['bars'] = wgv.calculate_bars(db['system']['bars'], db['system']['nodes'])
    db['system']['springs'] = wgv.springs(db)

    db['system']['wgv'] = dict()
    a, pos = wgv.kinematic_transformation_matrix(db)
    db['system']['wgv']['a'] = a
    db['system']['wgv']['node_deforms'] = pos

    db['system']['wgv']['k'] = wgv.stiffness_matrix(db)
    db['system']['wgv']['K'] = wgv.total_stiffness_matrix(db)
 


def calculate_load(db: dict):
    for item in db['load']['LC'].items():
        db['load']['LC'][item[0]]['wgv'] = dict()
        db['load']['LC'][item[0]]['wgv']['s_0'] = wgv.festhaltekraftgroessen(db, item[0])
        db['load']['LC'][item[0]]['wgv']['P_0'] = wgv.ersatzknotenkraefte(db, item[0])
        db['load']['LC'][item[0]]['wgv']['P_bar'] = wgv.knotenkraefte(db, item[0])
        db['load']['LC'][item[0]]['wgv']['P'] = wgv.load_vector(db, item[0])



def calculate_calc(db:dict):
    for key, item in db['calc'].items():
        if item == None:
            db['calc'][key] = dict()
            db['calc'][key] = dict()
            db['calc'][key]['V'] = wgv.node_deformations(db, key)
            db['calc'][key]['v'] = wgv.stabendweggroessen(db, key)
            db['calc'][key]['s_II'] = wgv.stabendkraftgroessen(db, key)
            db['calc'][key]['s_I'] = wgv.convert_kraftgroessen(db, key)
            db['calc'][key]['s'] = wgv.schnittgroessen(db, key)

            w_dict = wgv.deflection(db, key)
            #db['calc'][key]['s']['w'] = dict()
            for bar, w_list in w_dict.items():
                db['calc'][key]['s'][bar]['w'] = w_list
            # WGV auflösen, Schnittgrößen speichern



def calculate_maxima(db: dict):
    pass    # Überlagerungsvorschrift, Werte an allen Teilungspunkten bestimmen (max, min; N, M, Q) (was gewünscht)

