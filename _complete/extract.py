import numpy as np
import json

import defaults

#TODO z-Achse auch in Zweitdatei auslagern
def write_system(file: str, db: dict, mode: str = 'w') -> None: 
    offset = 0.05   # Abstand z-Linie von Systemlinie

    with open(file, mode) as f:
        f.write('### System: Staebe\n')
        f.write('# x [m],  y [m], alpha [deg]\n')

        for bar in (db['system']['bars']).items():
            f.write(f'# Stab {bar[0]}\n')

            alpha = bar[1]['alpha']

            for lr in ('l', 'r'):
                x = db['system']['nodes'][str(bar[1][lr])]['x']
                y = db['system']['nodes'][str(bar[1][lr])]['z']
                f.write(f'{x: 7.3f} {y: 7.3f}       {alpha: 6.2f}\n')

            f.write('\n')

        f.write('\n')


def write_local_z_axis(file: str, db: dict, mode: str = 'w') -> None: 
    offset = 0.05   # Abstand z-Linie von Systemlinie

    with open(file, mode) as f:
        f.write('### System: lokale z-Achse\n')
        f.write('# x [m],  y [m]\n')

        for bar in (db['system']['bars']).items():
            f.write(f'# Stab {bar[0]}\n')

            for lr in ('l', 'r'):
                x = db['system']['nodes'][str(bar[1][lr])]['x'] + np.sin(np.radians(bar[1]['alpha']))*offset
                y = db['system']['nodes'][str(bar[1][lr])]['z'] + np.cos(np.radians(bar[1]['alpha']))*offset
                f.write(f'{x: 7.3f} {y: 7.3f}\n')

            f.write('\n')

        f.write('\n')



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
        return defaults.support_XYZ
    elif supports == {'x': -1, 'z': -1, 'y': 0}: 
        return defaults.support_XZ
    elif supports == {'x': -1, 'z': 0, 'y': -1}: 
        return defaults.support_XY
    elif supports == {'x': 0, 'z': -1, 'y': -1}: 
        return rotate_support(defaults.support_XY, -90)
    elif supports == {'x': 0, 'z': -1, 'y': 0}: 
        #print('t') #TODO was hat das zu bedeuten
        return defaults.support_Z 
    elif supports == {'x': -1, 'z': 0, 'y': 0}: 
        return rotate_support(defaults.support_Z, 90)



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
            f.writelines(text)

        f.write('\n')



#speicher ersten und letzen Wert jeder Größe in dict und schreib sie am Ende in Datei zusammen mit alpha und coord

def write_internal_forces(file: str, db: dict, lc: int, mode: str = 'w') -> None:
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

                alpha = bar['alpha']
                x_l = db['system']['nodes'][bar['l']]['x']
                z_l = db['system']['nodes'][bar['l']]['z']

                for i, point in enumerate(bar['points']):
                    s_i = db['calc']['LC'][str(lc)]['s'][nr_stab][s][i]

                    if i == 0:
                        f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {0: 7.3f}\n')
                    
                    f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {s_i*faktor: 7.3f}\n')

                f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {0: 7.3f}\n')
                f.write(f'\n')
        f.write('\n')



def write_comb_internal_forces(file: str, db: dict, comb: int, kled: str, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Schnittgroessen und Verformung\n')
        f.write(f'# x_0 [m], y_0 [m],   x [m], alpha [deg], Minimum, Maximum \n')
        for nr_stab, bar in db['system']['bars'].items():
            for s in ('N', 'VZ', 'MY', 'w'):
                faktor = 1
                einheit = '[kN]'
                if s == 'M':
                    einheit = '[kNm]'
                elif s == 'w':
                    einheit = '[mm]'
                    faktor = 1000   # Umrechnung in mm

                f.write(f'# Stab {int(nr_stab):2n} {" "*(36-len(einheit))} {s[0]} {einheit}   {s[0]} {einheit}\n')
                if s not in db['comb']['komb'][str(comb)]['res']['bar']:
                    f.write(f'    0.000    0.000    0.000        0.000    0.000    0.000\n\n')
                    continue

                alpha = bar['alpha']
                x_l = db['system']['nodes'][bar['l']]['x']
                z_l = db['system']['nodes'][bar['l']]['z']

                values = db['comb']['komb'][str(comb)]['res']['bar'][s]

                for i, point in enumerate(bar['points']):
                    s_max = values['max'][kled][nr_stab][i] if 'max' in values else 0
                    s_min = values['min'][kled][nr_stab][i] if 'min' in values else 0

                    if i == 0:
                        f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}    0.000    0.000\n')
                    
                    f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}  {s_min*faktor: 7.3f}  {s_max*faktor: 7.3f}\n')

                f.write(f'  {x_l: 7.3f}  {z_l: 7.3f}  {point: 7.3f}      {alpha: 7.3f}    0.000    0.000\n')
                f.write(f'\n')
        f.write('\n')



def write_max_internal_forces(file: str, db: dict, lc: int, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Extremwerte der Schnittgroessen und Verformung\n')
        f.write(f'# x_m [m], y_m [m], alpha [deg], Minimum, Maximum \n')
        for nr_stab, bar in db['system']['bars'].items():
            f.write(f'# Stab {int(nr_stab):2n}\n')

            for s in ('N', 'V', 'M', 'w'):
                faktor = 1
                einheit = '[kN]'

                if s == 'M':
                    einheit = '[kNm]'
                elif s == 'w':
                    einheit = '[mm]'
                    faktor = 1000   # Umrechnung in mm

                f.write(f'#{" "*(45-len(einheit))} {s} {einheit}\n')

                alpha = bar['alpha']
                nodes = bar['l'], bar['r']

                x_m = (db['system']['nodes'][nodes[1]]['x'] + db['system']['nodes'][nodes[0]]['x'])/2
                z_m = (db['system']['nodes'][nodes[1]]['z'] + db['system']['nodes'][nodes[0]]['z'])/2

                forces = db['calc']['LC'][str(lc)]['s'][nr_stab][s]

                f.write(f'  {x_m: 7.3f}  {z_m: 7.3f}      {alpha: 7.3f}  {min(forces)*faktor: 7.3f}  {max(forces)*faktor: 7.3f}\n\n')

        f.write('\n')



def write_max_comb_internal_forces(file: str, db: dict, comb: int, kled: str, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Extremwerte der Schnittgroessen und Verformung\n')
        f.write(f'# x_m [m], y_m [m], alpha [deg], Minimum, Maximum \n')
        for nr_stab, bar in db['system']['bars'].items():
            f.write(f'# Stab {int(nr_stab):2n}\n')

            for s in ('N', 'VZ', 'MY', 'w'):
                faktor = 1
                einheit = '[kN]'

                if s == 'M':
                    einheit = '[kNm]'
                elif s == 'w':
                    einheit = '[mm]'
                    faktor = 1000   # Umrechnung in mm

                f.write(f'#{" "*(36-len(einheit))} {s[0]} {einheit}   {s[0]} {einheit}\n')
                if s not in db['comb']['komb'][str(comb)]['res']['bar']:
                    f.write(f'    0.000    0.000        0.000    0.000    0.000\n\n')
                    continue

                alpha = bar['alpha']
                nodes = bar['l'], bar['r']

                x_m = (db['system']['nodes'][nodes[1]]['x'] + db['system']['nodes'][nodes[0]]['x'])/2
                z_m = (db['system']['nodes'][nodes[1]]['z'] + db['system']['nodes'][nodes[0]]['z'])/2

                values = db['comb']['komb'][str(comb)]['res']['bar'][s]
                minimum = min(values['min'][kled][nr_stab]) if 'min' in values else min(values['max'][kled][nr_stab])
                maximum = max(values['max'][kled][nr_stab]) if 'max' in values else max(values['min'][kled][nr_stab])

                f.write(f'  {x_m: 7.3f}  {z_m: 7.3f}      {alpha: 7.3f}  {minimum*faktor: 7.3f}  {maximum*faktor: 7.3f}\n\n')

        f.write('\n')

                

def write_reaction_forces(file: str, db: dict, lc: int, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Auflagerkraefte\n')
        f.write(f'# x_m [m], y_m [m], alpha [deg], size [kN] \n')

        for node_nr, node in db['calc']['LC'][lc]['C'].items():
            if 'x' in node or 'z' in node:
                f.write(f'# Knoten {node_nr}\n')
            node_vals = db['system']['nodes'][node_nr]
            x = node_vals['x']
            z = node_vals['z']
            alpha = node_vals['alpha']

            if 'x' in node:
                f.write(f'  {x: 7.3f}  {z: 7.3f}      {alpha: 7.3f}    {node["x"][0]: 7.3f}\n')
            if 'z' in node:
                f.write(f'  {x: 7.3f}  {z: 7.3f}      {alpha-90: 7.3f}    {node["z"][0]: 7.3f}\n')

            f.write('\n')



def write_comb_reaction_forces(file: str, db: dict, comb: int, kled: str, mode: str = 'w') -> None:
    with open(file, mode) as f:
        f.write('### Auflagerkraefte\n')
        f.write(f'# x_m [m], y_m [m], alpha [deg],  min [kN],  max [kN] \n')

        for node_nr in db['calc']['LC'][list(db['calc']['LC'])[0]]['C']:
            mima = {}

            for s in ('PX', 'PZ'):
                if s not in db['comb']['komb'][str(comb)]['res']['node']:
                    mima[s[1]] = (0, 0)
                    continue

                maximum = db['comb']['komb'][str(comb)]['res']['node'][s]['max'][kled][node_nr][0]
                minimum = db['comb']['komb'][str(comb)]['res']['node'][s]['min'][kled][node_nr][0]
                mima[s[1]] = (minimum, maximum)
            
            node_vals = db['system']['nodes'][node_nr]
            x = node_vals['x']
            z = node_vals['z']
            alpha = node_vals['alpha']

            if node_vals['sup']['x'] != 0 or node_vals['sup']['z'] != 0:
                f.write(f'# Knoten {node_nr}\n')
            
            if node_vals['sup']['x'] != 0:
                f.write(f'  {x: 7.3f}  {z: 7.3f}      {alpha: 7.3f}    {mima["X"][0]: 7.3f}    {mima["X"][1]: 7.3f}\n')
            if node_vals['sup']['z'] != 0:
                f.write(f'  {x: 7.3f}  {z: 7.3f}      {alpha-90: 7.3f}    {mima["Z"][0]: 7.3f}    {mima["Z"][1]: 7.3f}\n')

            f.write('\n')



def write_loads(file: str, db: dict, lc: int, mode: str = 'w') -> None:
    vectors = []
    lines = []
    lines_global = []

    for node in db['load']['LC'][str(lc)]['node']:
        node_vals = db['system']['nodes'][node['nr']]
        if node['type'] == 'F':
            vectors.append(f'{node_vals["x"]:>7.3f}  {node_vals["z"]:>7.3f} {node["alpha"]:>7.2f}    {node["val"]:>7.3f}\n')

    if vectors: 
        vectors.append('\n')

    for bar in db['load']['LC'][str(lc)]['bar']:
        bar_vals = db['system']['bars'][bar['nr']]
        node_start = db['system']['nodes'][bar_vals['l']]
        node_end = db['system']['nodes'][bar_vals['r']]

        if bar['type'] == 'PZZ' or bar['type'] == 'PG' or bar['type'] == 'PXX':
            alpha = 0 if bar['type'] == 'PXX' else 90
            val_l = np.sqrt(bar['p_zl']**2 + bar['p_xl']**2)
            val_r = np.sqrt(bar['p_zr']**2 + bar['p_xr']**2)

            vectors.append(f'{node_start["x"]:>7.3f}  {node_start["z"]:>7.3f} {alpha:>7.2f}    {val_l:>7.3f}\n')
            vectors.append(f'{  node_end["x"]:>7.3f}  {  node_end["z"]:>7.3f} {alpha:>7.2f}    {val_r:>7.3f}\n\n')

            lines.append(f'  {node_start["x"]:>7.3f}  {node_start["z"]:>7.3f}  {alpha:>7.2f}  {bar_vals["alpha"]:>7.2f}     {bar_vals["L"]:>7.3f}     {val_l:>7.3f}     {val_r:>7.3f}\n')
            lines.append(f'  {node_start["x"]:>7.3f}  {node_start["z"]:>7.3f}  {alpha:>7.2f}  {bar_vals["alpha"]:>7.2f}     {bar_vals["L"]:>7.3f}       0.000       0.000\n\n')

        elif bar['type'] == 'PZP' or bar['type'] == 'PXP':
            if bar['type'] == 'PZP':
                z_l = z_r = min(node_start["z"], node_end["z"])
                x_l = node_start['x']
                x_r = node_end['x']
            else:
                x_l = x_r = min(node_start["x"], node_end["x"])
                z_l = node_start['z']
                z_r = node_end['z']

            alpha = 90 if bar['type'] == 'PZP' else 0
            length = x_r - x_l + z_r - z_l
            val_l = np.sqrt(bar['p_zl']**2 + bar['p_xl']**2)
            val_r = np.sqrt(bar['p_zr']**2 + bar['p_xr']**2)

            x_l = min(node_start["x"], node_end["x"])

            vectors.append(f'{x_l:>7.3f}  {z_l:>7.3f} {alpha:>7.2f}    {val_l:>7.3f}\n')
            vectors.append(f'{x_r:>7.3f}  {z_r:>7.3f} {alpha:>7.2f}    {val_r:>7.3f}\n\n')

            lines.append(f'  {x_l:>7.3f}  {z_l:>7.3f}  {alpha:>7.2f}  {alpha-90:>7.2f}     {length:>7.3f}     {val_l:>7.3f}     {val_r:>7.3f}\n')
            lines.append(f'  {x_l:>7.3f}  {z_l:>7.3f}  {alpha:>7.2f}  {alpha-90:>7.2f}     {length:>7.3f}       0.000       0.000\n\n')

        #TODO stimmt wahrscheinlich noch nicht
        elif bar['type'] == 'PZ' or bar['type'] == 'PX':
            alpha = bar_vals['alpha']
            val_l = np.sqrt(bar['p_zl']**2 + bar['p_xl']**2)
            val_r = np.sqrt(bar['p_zr']**2 + bar['p_xr']**2)

            vectors.append(f'{x_l:>7.3f}  {z_l:>7.3f} {alpha+90:>7.2f}  {val_l:>7.3f}\n')
            vectors.append(f'{x_r:>7.3f}  {z_r:>7.3f} {alpha+90:>7.2f}  {val_r:>7.3f}\n\n')

            lines.append(f'  {x_l:>7.3f}  {z_l:>7.3f}  {alpha+90:>7.2f}  {alpha:>7.2f}     {length:>7.3f}     {val_l:>7.3f}     {val_r:>7.3f}\n')
            lines.append(f'  {x_l:>7.3f}  {z_l:>7.3f}  {alpha+90:>7.2f}  {alpha:>7.2f}     {length:>7.3f}       0.000       0.000\n\n')


    with open(file, mode) as f:
        f.write('### Lastvektoren (Vektoren fuer Knotenlast sowie Linienlastanfang und -ende)\n')
        f.write('# x [m],  y [m],   alpha, size [kN]\n')

        f.writelines(vectors)
        if not vectors:
            f.write('0 0 0 0\n')

        f.write('\n### Linien (obere und untere Begrenzungslinie der Linienlasten)\n')
        f.write('# x_l [m], y_l [m], alpha_l, alpha_b, length [m], val_l [kN], val_r [kN]\n')

        f.writelines(lines)
        if not lines:
            f.write('0 0 0 0 0 0 0\n')
