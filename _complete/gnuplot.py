from defaults import gnuplot_vars

def plot_system() -> list:
    return [
        'plot    file_main i 0 w l lc "black" notitle,\\\n',
        '        file_main i 0 u ($1+0.2*offset*sin($3)):($2+0.2*offset*cos($3)) w l lc "black" dt 2 notitle,\\\n'
    ]

def plot_support() -> list:
    return [ '        file_add  i 0 u ($1+factor_s*$3):($2+factor_s*$4) w l lc rgb "black" notitle,\\\n' ]



def plot_loads() -> list:
    return [
        '        file_add  i 1 u (x_vec($1, $4, $3)):(y_vec($2, $4, $3)):(cos($3)*$4*factor_L):(-sin($3)*$4*factor_L) w vec notitle as 100,\\\n',
        '        file_add  i 1 u (x_load($1, $4, $3, 1.5)):(y_load($2, $4, $3, 1.5)):(load($4)):($3 <= 0 ? $3+90 : $3-90) w labels notitle rotate variable center tc "orange",\\\n',
        '        file_add  i 2 u (x_load($1, $6, $3, 1)):(y_load($2, $6, $3, 1)):(dx_load($3, $4, $5, $6, $7)):(dy_load($3, $4, $5, $6, $7))  w vec notitle as 101,\\\n',
    ]



def plot_reaction_forces() -> list:
    return [
        '        file_main i 3 u (x_vec($1, $4, $3)):(y_vec($2, $4, $3)):(cos($3)*$4*factor_L):(-sin($3)*$4*factor_L) w vec notitle as 102,\\\n',
        '        file_main i 3 u (x_load($1, $4, $3, 1.5)):(y_load($2, $4, $3, 1.5)):($4 == 0.0 ? "" : load($4)):($3 <= 0 ? $3+90 : $3-90) w labels notitle rotate variable center tc "red",\\\n'
    ]



def plot_combined_reaction_forces() -> list:
    return [
        '        file_main i 3 u (x_vec($1, $4, $3)):(y_vec($2, $4, $3)):($4 == 0 & $5 == 0 ? 0 : cos($3)*10*factor_L):($4 == 0 & $5 == 0 ? 0 : -sin($3)*10*factor_L) w vec notitle as 102,\\\n',
        '        file_main i 3 u (x_load($1, 10, $3, 1.5)):(y_load($2, 10, $3, 1.5)):($4 == 0 ? "" : load($4)):($3 <= 0 ? $3+90 : $3-90) w labels notitle rotate variable center tc "blue",\\\n',
        '        file_main i 3 u (x_load($1, 10, $3, 2.0)):(y_load($2, 10, $3, 2.0)):($5 == 0 ? "" : load($5)):($3 <= 0 ? $3+90 : $3-90) w labels notitle rotate variable center tc "red",\\\n'
    ]



def plot_internal_forces(typ: str) -> list:
    if typ == 'N':
        heading = ['s = 0; s_text = "Normalkraft"; factor = factor_N\n',]
    elif typ == 'V':
        heading = ['s = 1; s_text = "Querkraft"; factor = factor_V\n',]
    elif typ == 'M':
        heading = ['s = 2; s_text = "Moment"; factor = factor_M\n',]
    elif typ == 'w':
        heading = ['s = 3; s_text = "Verformung"; factor = factor_w\n',]

    heading.append('set title s_text . " infolge LF " . lf left offset graph -0.5 font ",15"\n\n')

    if typ == 'M' or typ == 'V' or typ == 'N':
        text = ['        file_main i 1 u (x_plot($1, $3, $4, $5, factor)):(y_plot($2, $3, $4, $5, factor)) ev:4::s w l notitle lc "red",\\\n']
    elif typ == 'w':
        pass

    text.append('        file_main i 2 u ($1+0.5*offset*sin($3)):($2-0.5*offset*cos($3)):(min_max($4, $5)):3 ev:4::s w labels notitle rotate variable center tc "red",\\\n')

    return text, heading



def plot_combined_internal_forces(typ: str) -> list:
    if typ == 'N':
        heading = ['s = 0; s_text = "Normalkraft"; factor = factor_N\n',]
    elif typ == 'V':
        heading = ['s = 1; s_text = "Querkraft"; factor = factor_V\n',]
    elif typ == 'M':
        heading = ['s = 2; s_text = "Moment"; factor = factor_M\n',]
    elif typ == 'w':
        heading = ['s = 3; s_text = "Verformung"; factor = factor_w\n',]

    heading.append('set title s_text . " infolge LF-Kombination " . lf . "-" . kled left offset graph -0.5 font ",15"\n\n')

    if typ == 'M' or typ == 'V' or typ == 'N':
        text = [
            '        file_main i 1 u (x_plot($1, $3, $4, $5, factor)):(y_plot($2, $3, $4, $5, factor)) ev:4::s w l notitle lc "blue",\\\n',
            '        file_main i 1 u (x_plot($1, $3, $4, $5, factor)):(y_plot($2, $3, $4, $6, factor)) ev:4::s w l notitle lc "red",\\\n'
        ]
    elif typ == 'w':
        pass

    text.extend([
        '        file_main i 2 u ($1+0.5*offset*sin($3)):($2-0.5*offset*cos($3)):(comb_min($4, $5)):3 ev:4::s w labels notitle rotate variable center tc "blue",\\\n'
        '        file_main i 2 u ($1+0.5*offset*sin($3)):($2-0.5*offset*cos($3)):(comb_max($4, $5)):3 ev:4::s w labels notitle rotate variable center tc "red",\\\n'
    ])

    return text, heading



def plot_LC(file: str, LC: str, parts: dict, show: bool = False):
    file = file.split('.')[0]

    factors = gnuplot_vars.copy()

    parts_text = []
    heading = []
    
    for typ, factor in parts.items():    
        if typ in ('V', 'N', 'M'):
            factors['factor_' + typ][0] = factor if factor else factors['factor_' + typ][0]
            typ_text, heading = plot_internal_forces(typ)
            parts_text.extend(typ_text)
        elif typ == 'Q':
            factors['factor_V'][0] = factor if factor else factors['factor_V'][0]
            typ_text, heading = plot_internal_forces('V')
            parts_text.extend(typ_text)
        elif typ == 'support':
            factors['factor_s'][0] = factor if factor else factors['factor_s'][0]
            parts_text.extend(plot_support())
        elif typ == 'load':
            factors['factor_L'][0] = factor if factor else factors['factor_L'][0]
            parts_text.extend(plot_loads())
        elif typ == 'reaction':
            parts_text.extend(plot_reaction_forces())

    text = [
        '# Text darstellen, Maßstab für System und Schnittgrößen\n\n',
        f'file = "{file}_LC_{LC}"\n',
        f'lf = "{LC}"\n\n',
    ]

    for name, val in factors.items():
        text.append(f'{name:8} = {val[0]:5.3f}   {val[1]}\n')
        if name in ('offset', 'factor_t'):
            text.append('\n')

    text.append('#-------------------------------------------------------------\n\n')

    if not show:
        text.extend((
            'set terminal pdfcairo size 29.7cm,21cm fontscale 0.4\n',
            'set encoding iso_8859_1\n',
            'set output file . ".pdf"\n',
        ))
    else: 
        text.append('set terminal wxt size 2000, 1500\n')

    text.append('\nload "behind.gp"\n\n')

    text.extend(heading)

    text.extend(plot_system())
    text.extend(parts_text)

    if show:
        text.append('\npause -1\n')

    with open(file + '_LC_' + LC + '.gp', 'w', encoding='utf-8') as f:
        f.writelines(text)



def plot_comb(file: str, comb: str, kled: str, parts: dict, show: bool = False):
    file = file.split('.')[0]

    factors = gnuplot_vars.copy()

    parts_text = []
    heading = []

    for typ, factor in parts.items():    
        if typ in ('V', 'N', 'M'):
            factors['factor_' + typ][0] = factor if factor else factors['factor_' + typ][0]
            typ_text, heading = plot_combined_internal_forces(typ)
            parts_text.extend(typ_text)
        elif typ == 'Q':
            factors['factor_V'][0] = factor if factor else factors['factor_V'][0]
            typ_text, heading = plot_combined_internal_forces('V')
            parts_text.extend(typ_text)
        elif typ == 'reaction':
            parts_text.extend(plot_combined_reaction_forces())

    text = [
        '# Text darstellen, Maßstab für System und Schnittgrößen\n\n',
        f'file = "{file}_comb_{comb}_{kled}"\n',
        f'lf = "{comb}"\n',
        f'kled = "{kled}"\n\n',
    ]

    for name, val in factors.items():
        text.append(f'{name:8} = {val[0]:5.3f}   {val[1]}\n')
        if name in ('offset', 'factor_t'):
            text.append('\n')

    text.append('#-------------------------------------------------------------\n\n')

    if not show:
        text.extend((
            'set terminal pdfcairo size 29.7cm,21cm fontscale 0.4\n',
            'set encoding iso_8859_1\n',
            'set output file . ".pdf"\n',
        ))
    else: 
        text.append('set terminal wxt size 2000, 1500\n')

    text.append('\nload "behind.gp"\n\n')

    text.extend(heading)

    text.extend(plot_system())
    text.extend(parts_text)

    if show:
        text.append('\npause -1\n')


    with open(''.join((file, '_comb_', comb, '_', kled, '.gp')), 'w', encoding='utf-8') as f:
        f.writelines(text)



def multiplot(file: str, gp_name: str, LCs: list):
    file = file.split('.')[0]

    factors = gnuplot_vars.copy()

    last_LC = LC = LCs[0][0]

    if type(LC) == tuple:
        text = [
            '# Text darstellen, Maßstab für System und Schnittgrößen\n\n',
            f'file = "{file}_comb_{LC[0]}_{LC[1]}"\n',
            f'lf = "{LC[0]}"\n',
            f'kled = "{LC[1]}"\n\n',
        ]
    else:
        text = [
            '# Text darstellen, Maßstab für System und Schnittgrößen\n\n',
            f'file = "{file}_LC_{LC}"\n',
            f'lf = "{LC}"\n\n',
        ]


    # first plot
    parts_text = []
    heading = []

    for typ, factor in LCs[0][1].items():    
        if typ in ('V', 'N', 'M'):
            factors['factor_' + typ][0] = factor if factor else factors['factor_' + typ][0]
            typ_text, heading = plot_combined_internal_forces(typ) if type(LC) == tuple else plot_internal_forces(typ)
            parts_text.extend(typ_text)
        elif typ == 'Q':
            factors['factor_V'][0] = factor if factor else factors['factor_V'][0]
            typ_text, heading = plot_combined_internal_forces('V') if type(LC) == tuple else plot_internal_forces(typ)
            parts_text.extend(typ_text)
        elif typ == 'reaction':
            reaction_forces = plot_combined_reaction_forces()  if type(LC) == tuple else plot_reaction_forces()
            parts_text.extend(reaction_forces)
        elif typ == 'support' and type(LC) != tuple:
            factors['factor_s'][0] = factor if factor else factors['factor_s'][0]
            parts_text.extend(plot_support())
        elif typ == 'load' and type(LC) != tuple:
            factors['factor_L'][0] = factor if factor else factors['factor_L'][0]
            parts_text.extend(plot_loads())

    for name, val in factors.items():
        text.append(f'{name:8} = {val[0]:5.3f}   {val[1]}\n')
        if name in ('offset', 'factor_t'):
            text.append('\n')

    text.append('#-------------------------------------------------------------\n\n')

    text.extend((
        'set terminal pdfcairo size 29.7cm,21cm fontscale 0.3\n',
        'set encoding iso_8859_1\n',
        'set output "multiplot" . ".pdf"\n',
    ))
    

    text.append('\nload "behind.gp"\n')

    text.append(f'\nset multiplot layout {2},{len(LCs)//2 + len(LCs)%2}\n\n')

    text.extend(heading)

    text.extend(plot_system())
    text.extend(parts_text)

    # all following plots
    for LC, parts in LCs[1:]:
        if type(LC) == tuple and last_LC != LC:
            text = [
                '# Text darstellen, Maßstab für System und Schnittgrößen\n\n',
                f'file = "{file}_comb_{LC[0]}_{LC[1]}"\n',
                f'lf = "{LC[0]}"\n',
                f'kled = "{LC[1]}"\n\n',
            ]
        elif last_LC != LC:
            text = [
                '# Text darstellen, Maßstab für System und Schnittgrößen\n\n',
                f'file = "{file}_LC_{LC}"\n',
                f'lf = "{LC}"\n\n',
            ]

        last_LC = LC

        parts_text = []
        heading = []
        text.append('\n')

        for typ, factor in parts.items():    
            if typ in ('V', 'N', 'M'):
                if factor:
                    text.append(f'{"factor_"+typ:8} = {factor:5.3f}   {factors["factor_"+typ][1]}\n')
                
                typ_text, heading = plot_combined_internal_forces(typ) if type(LC) == tuple else plot_internal_forces(typ)
                parts_text.extend(typ_text)
            elif typ == 'Q':
                if factor:
                    text.append(f'{"factor_V":8} = {factor:5.3f}   {factors["factor_V"][1]}\n')

                typ_text, heading = plot_combined_internal_forces('V') if type(LC) == tuple else plot_internal_forces(typ)
                parts_text.extend(typ_text)
            elif typ == 'reaction':
                reaction_forces = plot_combined_reaction_forces()  if type(LC) == tuple else plot_reaction_forces()
                parts_text.extend(reaction_forces)
            elif typ == 'support' and type(LC) != tuple:
                if factor:
                    text.append(f'{"factor_s":8} = {factor:5.3f}   {factors["factor_s"][1]}\n')

                parts_text.extend(plot_support())
            elif typ == 'load' and type(LC) != tuple:
                if factor:
                    text.append(f'{"factor_L":8} = {factor:5.3f}   {factors["factor_L"][1]}\n')

                parts_text.extend(plot_loads())

        text.extend(('\n', *heading))

        text.extend(plot_system())
        text.extend(parts_text)

    text.append('\nunset multiplot\n')


    with open(gp_name, 'w', encoding='utf-8') as f:
        f.writelines(text)