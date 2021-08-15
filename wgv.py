import numpy as np
#import string

import json
from copy import deepcopy


#--------------------------------------------------------------------------------
### Helper Functions
#--------------------------------------------------------------------------------


def get_index(what: any, where: any):
    """Helper function: Search for an item in a sequence and return the index"""
    if what in where:
        return where.index(what)
    else:
        return None


#--------------------------------------------------------------------------------
### MATQS
#--------------------------------------------------------------------------------


def calculate_querschnittswerte(cross_sections: dict) -> dict:
    """Calculate area and second moment of area for all cross sections
    
    Assuming the cross section is a rectangle; calculation can be explicity overridden by specifing A or I
    """
    for cs in cross_sections.values():
        if ['A'] not in cs:
            cs['A'] = cs['b']*cs['h']        # A = b*h
        if ['I'] not in cs:
            cs['I'] = cs['b']*cs['h']**3/12  # I = b*h**3/12

    return cross_sections


#--------------------------------------------------------------------------------
### SYSTEM
#--------------------------------------------------------------------------------


def calculate_bars(bars: list, nodes: list) -> dict:
    """Calculate length and angle of bars as well as lokal x-coord for intermediate evaluation-points"""
    for bar in bars.values():
        dx_bar = nodes[bar['r']]['x'] - nodes[bar['l']]['x']
        dz_bar = nodes[bar['r']]['z'] - nodes[bar['l']]['z']
        
        bar['L'] = np.sqrt(dx_bar**2 + dz_bar**2)
        bar['alpha'] = np.degrees(np.arctan2(dx_bar, dz_bar)) - 90   # da Koordinatensystem gedreht
        # Unterteile Stab in 'elems' teile -> 'elems'-1 Zwischenpunkte + Anfangs- und Endpunkt
        bar['points'] = [x*bar['L']/(bar['elems']) for x in range(0,bar['elems']+1)]
        
    return bars



def springs(db: dict) -> list:
    """Extract all spring elements into a single list"""
    springs = []

    for n, node in db['system']['nodes'].items():
        for key, value in node['sup'].items():
            if value > 0:
                springs.append({'node': n, 'direction': key, 'value': value})

    return springs



def kinematic_transformation_matrix(db: dict) -> tuple:
    """Create kinematic transformation matrix 
    
    (Mapping of node deformations to internal deformations)
    """
    a_T = []    # transponierte Transformationsmatrix
    pos = []    # Stelle und Richtung der einzelnen Freiheitsgrade
    joints = [] # zusätzliche Freiheitsgrade infolge Gelenke
    bar_nrs = list(db['system']['bars'])

    for nr, node in db['system']['nodes'].items():      # Iteration über Knoten
        for key, value in node['sup'].items():          # Iteration über Auflagerbedingungen
            if value >= 0:                              # falls Wert negativ: Einspannung (Wert unberücksichtigt)
                pos.append((nr, key))
                V_vek = []

                for j, bar in db['system']['bars'].items(): # Suche zugehörige Stäbe
                    alpha = np.radians(bar['alpha'])
                    length = bar['L']

                    if bar['l'] == nr: 
                        if key == 'x': 
                            V_vek.extend((-np.cos(alpha), -np.sin(alpha)/length, -np.sin(alpha)/length))
                        if key == 'z': 
                            V_vek.extend((np.sin(alpha), -np.cos(alpha)/length, -np.cos(alpha)/length))
                        if key == 'y': 
                            if bar['fixa']['M'] >= 0:   # Falls Drehgelenk am Ende: Wert für später speichern
                                V_vek.extend((0, 0, 0))
                                joints.append((nr, key, j))#bar_nrs.index(j)))
                            else:
                                V_vek.extend((0, 1, 0))

                    elif bar['r'] == nr:
                        if key == 'x': 
                            V_vek.extend((np.cos(alpha), np.sin(alpha)/length, np.sin(alpha)/length))
                        if key == 'z': 
                            V_vek.extend((-np.sin(alpha), np.cos(alpha)/length, np.cos(alpha)/length))
                        if key == 'y': 
                            if bar['fixe']['M'] >= 0:
                                V_vek.extend((0, 0, 0))
                                joints.append((nr, key, j))#bar_nrs.index(j)))
                            else:
                                V_vek.extend((0, 0, 1))
                    
                    else:
                        V_vek.extend((0, 0, 0))

                for spring in db['system']['springs']:
                    if spring['node'] == nr: 
                        if key == 'x' and spring['direction'] == 'x': 
                            V_vek.append(1)
                        elif key == 'z' and spring['direction'] == 'z': 
                            V_vek.append(-1)
                        elif key == 'y' and spring['direction'] == 'y': 
                            V_vek.append(1)
                        else: 
                            V_vek.append(0)
                    else: 
                        V_vek.append(0) 
                
                a_T.append(V_vek)   
    
    for joint in joints:                # pro Gelenk neue Spalte einfügen
        index = 0
        
        for i in range(len(pos)):       # suche passende Spalte, sodass richtige Sortierung
            if pos[i][0] > joint[0]:
                index = i
                break

        pos.insert(index, joint)
        bar = bar_nrs.index(joint[2])
        if db['system']['bars'][joint[2]]['fixa']['M'] >= 0:
            a_T.insert(index, [0]*bar*3 + [0, 1, 0] + [0]*(len(a_T[0])-(bar+1)*3))
        else:
            a_T.insert(index, [0]*bar*3 + [0, 0, 1] + [0]*(len(a_T[0])-(bar+1)*3))

    return np.array(a_T).transpose(), pos    # kinematische Transformationsmatrix a



def element_stiffness_matrix(EA: float, EI: float, l: float) -> list:
    """Create reduced element stiffness matrix
    
    Mapping of independent internal displacements (u_Delta, tau_l, tau_r) to internal forces (N_r, M_l, M_r) for a single bar
    """
    u_delta = [EA/l, 0, 0]
    tau_l = [0, 4*EI/l, 2*EI/l]
    tau_r = [0, 2*EI/l, 4*EI/l]

    return [u_delta, tau_l, tau_r]   # Element-Steifigkeitsmatrix k_e



def stiffness_matrix(db:dict) -> np.matrix:
    """Combination of element stiffness matrizes for all bars and springs"""
    k = []
    n_springs = len(db['system']['springs'])
    k_size = len(db['system']['bars'])*3 + n_springs    # calculate size of k
    
    for i, bar in enumerate(db['system']['bars'].values()):
        k_e = element_stiffness_matrix(bar['EA'], bar['EI'], bar['L'])
        
        for j in range(3):
            k.append([0, 0, 0]*i + k_e[j] + [0]*(k_size-(i+1)*3))

    for i, spring in enumerate(db['system']['springs']):
        k.append([0]*(k_size-n_springs+i) + [spring['value']] + [0]*(n_springs-i-1))

    return np.array(k)  # Steifigkeitsmatrix k



def total_stiffness_matrix(db: dict) -> np.matrix:
    """Calculate total stiffness matrix
    
    Mapping of node deformations to external loads.
    K = a^T*k*a
    """
    return np.matmul(np.matmul(db['system']['wgv']['a'].transpose(), db['system']['wgv']['k']), db['system']['wgv']['a'])


#--------------------------------------------------------------------------------
### LOAD
#--------------------------------------------------------------------------------


#TODO rename
def festhaltekraftgroessen(db: dict, lc_nr: int) -> np.array:
    """Calculate ...
    
    Calculate reaction forces due to beam loading on a girder, which is clamped at both ends;
    Using sign convention II: positive direction of moments and twists ist counterclockwise
    """
    s_0 = np.zeros(len(db['system']['wgv']['a']))
    bar_nrs = list(db['system']['bars'])
    lc = db['load']['LC'][lc_nr]

    for bar in lc['bar']:      #TODO Temperatur gleichförmig, ungleichförmig, Einzellasten (mehrere superponieren)
        length = db['system']['bars'][bar['nr']]['L']
        #alpha = np.radians(db['system']['bars'][bar['nr']]['alpha'])
        pos = bar_nrs.index(bar['nr'])*3

        s_0[pos] += -1/6*length*(bar['p_xl']+2*bar['p_xr'])           # N_r^0
        s_0[pos+1] += length**2/60*(3*bar['p_zl'] + 2*bar['p_zr'])    # M_l^0
        s_0[pos+2] += -length**2/60*(2*bar['p_zl'] + 3*bar['p_zr'])   # M_r^0

    return s_0


#TODO rename
def ersatzknotenkraefte(db: dict, lc_nr: int) -> np.array:
    """Calculate ...

    Calculate reaction forces due to beam loadings on a single span girder
    """
    P_0 = np.zeros(len(db['system']['wgv']['a'][1]))
    lc = db['load']['LC'][lc_nr]
    deg_of_freedom = db['system']['wgv']['node_deforms']

    for bar in lc['bar']:      #TODO Temperatur gleichförmig, ungleichförmig, Einzellasten (mehrere superponieren)
        length = db['system']['bars'][bar['nr']]['L']
        alpha = np.radians(db['system']['bars'][bar['nr']]['alpha'])

        knot_l = db['system']['bars'][bar['nr']]['l']
        P_zl = length/6*(2*bar['p_zl'] + bar['p_zr'])
        P_xl = length/6*(2*bar['p_xl'] + bar['p_xr'])
        #TODO zuerst nach passendem bar, dann nach allgemeinem Knoten suchen, nötig? -> nur für Normal und Querkraft?
        if (index := get_index((knot_l, 'x', bar['nr']), deg_of_freedom)) != None: 
             P_0[index] += np.sin(alpha)*P_zl + np.cos(alpha)*P_xl
        elif (index := get_index((knot_l, 'x'), deg_of_freedom)) != None: 
             P_0[index] += np.sin(alpha)*P_zl + np.cos(alpha)*P_xl

        if (index := get_index((knot_l, 'z', bar['nr']), deg_of_freedom)) != None: 
            P_0[index] += np.cos(alpha)*P_zl - np.sin(alpha)*P_xl  
        elif (index := get_index((knot_l, 'z'), deg_of_freedom)) != None: 
            P_0[index] += np.cos(alpha)*P_zl - np.sin(alpha)*P_xl

        knot_r = db['system']['bars'][bar['nr']]['r']
        P_zr = length/6*(bar['p_zl'] + 2*bar['p_zr'])
        P_xr = length/6*(bar['p_xl'] + 2*bar['p_xr'])

        if (index := get_index((knot_r, 'x', bar['nr']), deg_of_freedom)) != None: 
            P_0[index] += np.sin(alpha)*P_zr + np.cos(alpha)*P_xr
        elif (index := get_index((knot_r, 'x'), deg_of_freedom)) != None: 
            P_0[index] += np.sin(alpha)*P_zr + np.cos(alpha)*P_xr

        if (index := get_index((knot_r, 'z', bar['nr']), deg_of_freedom)) != None: 
            P_0[index] += np.cos(alpha)*P_zr - np.sin(alpha)*P_xr 
        elif (index := get_index((knot_r, 'z'), deg_of_freedom)) != None: 
            P_0[index] += np.cos(alpha)*P_zr - np.sin(alpha)*P_xr 

    return P_0


#TODO rename
def knotenkraefte(db: dict, lc_nr: int) -> np.array:
    """Calculate ...
    
    Combine nodal forces into a single vector
    """
    P_bar = np.zeros(len(db['system']['wgv']['a'][1]))
    lc = db['load']['LC'][lc_nr]
    deg_of_freedom = db['system']['wgv']['node_deforms']

    for node in lc['node']:      #TODO Auflagersenkung, -drehung
        if node['type'] == 'F':
            alpha = np.radians(node['alpha'])
            if (index := get_index((node['nr'], 'x'), deg_of_freedom)) != None: 
                P_bar[index] += -np.cos(alpha)*node['val']
            if (index := get_index((node['nr'], 'z'), deg_of_freedom)) != None:
                P_bar[index] += np.sin(alpha)*node['val']

        if node['type'] == 'M':         #TODO Warnung, dass Last nicht eindeutig aufgebracht werden kann, wenn Vollgelenk
            if (index := get_index((node['nr'], 'y'), deg_of_freedom)) != None:
                P_bar[index] += node['val']

    return P_bar



def load_vector(db: dict, lc: int) -> np.array:
    """Combination of all load-dependend vectors
    
    P = P_bar + P_0 - a_T*s_0
    """
    arrays = db['load']['LC'][lc]['wgv']
    return arrays['P_bar'] + arrays['P_0'] - np.transpose(db['system']['wgv']['a']).dot(arrays['s_0']) # P


#--------------------------------------------------------------------------------
### CALC
#--------------------------------------------------------------------------------


def node_deformations(db: dict, lc: int) -> np.array:
    """Calculate node deformation due to specified load_case
    
    V = K^(-1)*P
    """
    return np.linalg.inv(db['system']['wgv']['K']).dot(db['load']['LC'][lc]['wgv']['P'])


#TODO rename
def stabendweggroessen(db: dict, lc: int) -> np.array:
    """Calculate internal displacements due to node deformations 
    
    v = a*V
    """
    return db['system']['wgv']['a'].dot(db['calc'][lc]['V'])


#TODO rename
def stabendkraftgroessen(db: dict, lc: int) -> np.array:
    """Calculate internal forces due to internal displacements
    
    s = k*v + s_0
    """
    return db['system']['wgv']['k'].dot(db['calc'][lc]['v']) + db['load']['LC'][lc]['wgv']['s_0']


#TODO rename
def convert_kraftgroessen(db: dict, lc: int) -> np.array:
    """Convert internal forces into normal sign convention (I)
    
    Flip sign for every moment at the left end of a beam
    """
    n_bars = len(db['system']['bars'])
    s_I = np.copy(db['calc'][lc]['s_II'])

    for i in range(1,n_bars*2+2,3):
        s_I[i] *= -1

    return s_I


#TODO rename
def schnittgroessen(db: dict, lc: int) -> dict:
    """Calculate internal forces for all intermediate points """
    bars = db['system']['bars']
    bar_nrs = list(bars)
    #n_bars = len(bars)
    s = db['calc'][lc]['s_I']
    loads = db['load']['LC'][lc]['bar']
    s_bars = {}

    for key, bar in bars.items():       # initialisiere Schnittgrößen mit Werten infolge der Stabendkraftgrößen
        i = bar_nrs.index(key)     
        s_bars[key] = dict()
        length = bar['L']

        # Schnittgrößen infolge Stabendkraftgrößen
        s_bars[key]['N'] = [s[i*3]]*(bar['elems']+1)
        s_bars[key]['V'] = [(s[i*3+2]-s[i*3+1])/length]*(bar['elems']+1)        # konstanter Mittelwert ohne Last
        s_bars[key]['M'] = [s[i*3+1]*(1-x/length) + s[i*3+2]*x/length for x in bar['points']]
        # Berechnung von M und V am freigeschnittenen Stabelement über Gleichgewichtsbeziehungen

    for load in loads:
        bar = load['nr']
        length = bars[bar]['L']
        p_xl, p_xr = load['p_xl'], load['p_xr']
        p_zl, p_zr = load['p_zl'], load['p_zr']

        for i, x in enumerate(bars[bar]['points']):
            s_bars[bar]['N'][i] += 1/2*((p_xr-p_xl)/length*x**2 + 2*p_xl*x - (p_xl+p_xr)*length)
            s_bars[bar]['V'][i] += 1/2*(-(p_zr-p_zl)/length*x**2 - 2*p_zl*x + 1/3*(2*p_zl+p_zr)*length)
            s_bars[bar]['M'][i] += length**2/6*(((1-x/length) - (1-x/length)**3)*p_zl + (x/length -(x/length)**3)*p_zr)
            # Berechnung am freigeschnittenen Stabelement
        
    return s_bars


#TODO werden in anderen Programmen Längsverschiebungen mitbetrachtet?
#TODO rename
def deflection(db: dict, lc: int) -> dict:
    """Calculate deflection for all intermediate points"""
    bars = db['system']['bars']
    bar_nrs = list(bars)
    #n_bars = len(bars)
    loads = db['load']['LC'][lc]['bar']
    deg_of_freedom = db['system']['wgv']['node_deforms']
    w_bars = {}

    # Funktionen zur Ermittlung Verformung eines beidseitig eingespannten Trägers
    w_tau = lambda x, phi, L: -phi/L**2*x**3 + 2*phi/L*x**2 - phi*x                     # Verformung infolge Stabendverdrehung
    w_triang = lambda xi, p_z, L, EI: p_z/(40*EI)*L**4 * (xi**5/3 - xi**3 + 2*xi**2/3)  # Verformung infolge Dreieckslast

    for key, bar in bars.items():       
        i = bar_nrs.index(key)
        length = bar['L']
        alpha = np.radians(bar['alpha'])
        
        # Verformung infolge Stabendtangentenwinkel
        tau_l = db['calc'][lc]['v'][3*i+1]
        tau_r = db['calc'][lc]['v'][3*i+2]
        
        w_bars[key] = [w_tau(x, tau_l, length) + w_tau(length-x, -tau_r, length) for x in bar['points']]

        # Verformung infolge Knotenverschiebung
        dv = {'x': [0, 0], 'z': [0, 0]}
        for j, lr in enumerate(('l', 'r')):
            for v in ('x', 'z'):
                if (index := get_index((bar[lr], v), deg_of_freedom)) != None:
                    dv[v][j] = db['calc'][lc]['V'][index]

        # Stabanfangs- und Endverschiebung quer zur Stabrichtung
        w_l = dv['x'][0]*np.sin(alpha) + dv['z'][0]*np.cos(alpha)
        w_r = dv['x'][1]*np.sin(alpha) + dv['z'][1]*np.cos(alpha)

        for j, x in  enumerate(bar['points']):
            w_bars[key][j] += w_l + (w_r - w_l)*x/length

    # Verformung infolge Last 
    for load in loads:
        bar = load['nr']
        length = bars[bar]['L']
        EI = bars[bar]['EI']
        p_zl, p_zr = load['p_zl'], load['p_zr']

        for i, x in enumerate(bars[bar]['points']):
            w_bars[bar][i] += w_triang(x/length, p_zr, length, EI) + w_triang(1-x/length, p_zl, length, EI)

    return w_bars






