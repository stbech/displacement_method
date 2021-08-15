import numpy as np
import json


def write_system(file: str, db: dict, mode: str = 'w') -> None: 
    offset = 0.05   # Abstand z-Linie von Systemlinie

    with open(file, mode) as f:
        f.write('### System: Staebe mit lokaler z-Achse\n')
        f.write('# x [m],  y [m]\n')
        for bar in (db['system']['bars']).items():
            f.write(f'# Stab {bar[0]}\n')
            for lr in ('l', 'r'):
                x = db['system']['nodes'][str(bar[1][lr])]['x']
                y = db['system']['nodes'][str(bar[1][lr])]['z']
                f.write(f'{x: 7.3f} {y: 7.3f}\n')
            f.write('\n')

            for lr in ('l', 'r'):
                x = db['system']['nodes'][str(bar[1][lr])]['x'] + np.sin(np.radians(bar[1]['alpha']))*offset
                y = db['system']['nodes'][str(bar[1][lr])]['z'] + np.cos(np.radians(bar[1]['alpha']))*offset
                f.write(f'{x: 7.3f} {y: 7.3f}\n')
            f.write('\n')
        f.write('\n')



support_Z = [
    (0, 0, 0.75, 1),
    (0, 0, -0.75, 1),
    (0.75, 1, -0.75, 1),
    (1.2, 1.3, -1.2, 1.3),
]

support_XZ = [
    (0    , 0, 0.75, 1),
    (0    , 0, -0.75, 1),
    (1.2  , 1, -1.2, 1),
    (-0.8 , 1, -1.1, 1.3),
    (-0.35, 1, -0.65, 1.3),
    ( 0.1 , 1, -0.2, 1.3),
    ( 0.55, 1,  0.25, 1.3),
    ( 1.00, 1,  0.7, 1.3),
]

support_XY = [
    (0, 1.2, 0, -1.2),
    (-0.3, 1.2, -0.3, -1.2),
    (-0.3, -0.8, -0.6, -1.1),
    (-0.3, -0.35, -0.6, -0.65),
    (-0.3,  0.1, -0.6, -0.2),
    (-0.3, 0.55, -0.6, 0.25),
    (-0.3,  1.0, -0.6, 0.7),
]

support_XYZ = [
    (0, 1.2, 0, -1.2),
    (0, -0.8, -0.3, -1.1),
    (0, -0.35, -0.3, -0.65),
    (0,  0.1, -0.3, -0.2),
    (0, 0.55, -0.3, 0.25),
    (0,  1.0, -0.3, 0.7),
]



def rotate_support(lines: list, angle: float):
    new_lines = []
    rad = np.radians(angle)
    for line in lines:
        x_1 = line[0]*np.cos(rad) - line[1]*np.sin(rad)
        y_1 = line[0]*np.sin(rad) + line[1]*np.cos(rad)
        x_2 = line[2]*np.cos(rad) - line[3]*np.sin(rad)
        y_2 = line[2]*np.sin(rad) + line[3]*np.cos(rad)

        new_lines.append((x_1, y_1, x_2, y_2))

    return new_lines



def get_support_type(supports: dict):
    if supports == {'x': -1, 'z': -1, 'y': -1}: 
        return support_XYZ
    elif supports == {'x': -1, 'z': -1, 'y': 0}: 
        return support_XZ
    elif supports == {'x': -1, 'z': 0, 'y': -1}: 
        return support_XY
    elif supports == {'x': 0, 'z': -1, 'y': -1}: 
        return rotate_support(support_XY, -90)
    elif supports == {'x': 0, 'z': -1, 'y': 0}: 
        print('t')
        return support_Z 
    elif supports == {'x': -1, 'z': 0, 'y': 0}: 
        return rotate_support(support_Z, 90)



def support_text(knot: tuple):
    lines = get_support_type(knot[1]['sup'])
    if not(lines):
        return []
    lines = rotate_support(lines, knot[1]['alpha'])
    text = [f'# Knoten {knot[0]}\n']
    
    x = knot[1]['x']
    y = knot[1]['z']
    for line in lines: 
        for i in range(2):
            text.append(f'{x: 7.3f} {y: 7.3f} {line[2*i]: 7.3f} {line[2*i+1]: 7.3f}\n')
        text.append('\n')

    return text



def write_support(file: str, db: dict, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Auflagersymbole\n')
        f.write('# x [m],  y [m],    d_x,    d_y\n')
        for i, knot in enumerate((db['system']['nodes']).items()):
            text = support_text(knot)
            #if i == len(db['system']['nodes'])-1:
             #   text.pop()
            f.writelines(text)
        f.write('\n')



#speicher ersten und letzen Wert jeder Größe in dict und schreib sie am Ende in Datei zusammen mit alpha und coord

def write_schnittgroessen(file: str, db: dict, lc: int, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Schnittgroessen und Verformung\n')
        f.write(f'# x_0 [m], y_0 [m],   x [m], alpha [deg], Groesse \n')
        for nr_stab, bar in db['system']['bars'].items():
            for s in ('N', 'V', 'M', 'w'):
                faktor = 1
                einheit = '[kN]'
                if s == 'M':
                    einheit = '[kNm]'
                elif s == 'w':
                    einheit = '[mm]'
                    faktor = 1000   # Umrechnung in mm

                f.write(f'# Stab {int(nr_stab):2n} {" "*(36-len(einheit))} {s} {einheit}\n')

                alpha = db['system']['bars'][nr_stab]['alpha']
                x_l = db['system']['nodes'][str(db['system']['bars'][nr_stab]['l'])]['x']
                z_l = db['system']['nodes'][str(db['system']['bars'][nr_stab]['l'])]['z']

                for i, point in enumerate(bar['points']):
                    x_i = x_l + np.cos(np.radians(alpha))*point
                    z_i = z_l - np.sin(np.radians(alpha))*point
                    s_i = db['calc'][str(lc)]['s'][nr_stab][s][i]

                    if i == 0:
                        f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {0: 7.3f}\n')
                    
                    f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {s_i*faktor: 7.3f}\n')

                f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {0: 7.3f}\n')
                f.write(f'\n')
        f.write('\n')



with open('db_bsp5.json') as f:
    db = json.load(f)

write_system('bsp_5.gpd', db)
write_support('bsp_5.gpd', db, 'a')
write_schnittgroessen('bsp_5.gpd', db, '1', 'a')