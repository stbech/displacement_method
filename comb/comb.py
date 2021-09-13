def log_text_dead_load(db: dict, lc: str, gamma: str, i_point: int) -> str:
    """Return text for log-file with all relevant parameters for a load, which is not reduced by a factor psi."""

    gamma_text = 'gamma_F' if gamma == 'GAMF' else 'gamma_U'

    return f'{lc:>3}: {db[lc]["val"][i_point]:>6}*{db[lc][gamma]:>4.2f}      = {(db[lc]["val"][i_point]*db[lc][gamma]):>7.3f}  ({gamma_text}, {db[lc]["type"]}, {db[lc]["comb_type"]:>4}, {db[lc]["ACT"]:>3})\n'



def log_text_live_load(db: dict, lc: str, gamma: str, psi: str, i_point: int) -> str:
    """Return text for log-file with all relevant parameters for a load, which is reduced by a factor psi."""

    gamma_text = 'gamma_F' if gamma == 'GAMF' else 'gamma_U'

    return f'{lc:>3}: {db[lc]["val"][i_point]:>6}*{db[lc][gamma]:>4.2f}*{db[lc][psi]:>4.2f} = {(db[lc]["val"][i_point]*db[lc][gamma]*db[lc][psi]):>7.3f}  ({gamma_text}, {db[lc]["type"]}, {db[lc]["comb_type"]:>4}, {db[lc]["ACT"]:>3})\n'



def combine_dead_loads(db: dict, AG_nums: list, comb_dict: dict, i_point: int, logging: bool, max_res: bool) -> tuple:
    """Combine all dead loads.

    Combination types:
        - PERC: Deside for every loadcase on its own, whether it is favourable or not 
        - G/PERM: Combine all loadcases of an action, then decide whether they are favourable or not
        - AG_: Take only the most unfavourable loadcase defined within an action, even use it when it is favourable

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    AG_nums : list
        List of all AG_-types to combine
    comb_dict : dict
        Preprocessed loadcases with favourable and unfavourable values as defined by comb_DESI
    i_point : int
        Index of value in list at which the combination should take place
    logging : bool
        Decides whether information about the combination process should be tracked
    max_res : bool
        Decides whether the combination should be maximized (True) or minimized (False)

    Returns
    -------
    tuple (float, str)
        if logging = True: Combined dead loads and log of combination process
        or
    float
        if logging = False: Combined dead loads
    """

    if logging: 
        log = ''

    #TODO Entscheidung welches AG loggen
    for ag in AG_nums:      # iterate over permanent alternative load groups (AG_)
        for act_key, act in comb_dict[ag].items():  # iterate over actions
            # define inital value vor maximum (or minimum) superiour and inferiour value of AG_ as values of first loadcase
            sup = act[list(act)[0]]['sup']          
            inf = act[list(act)[0]]['inf']

            for key, val in act.items():        # iterate over loadcases
                # if a new loadcase has an higher absolute value, save loadcase and new value
                if (max_res and val['sup'] >= sup) or (not(max_res) and val['sup'] <= sup):
                    lc_sup = key
                    sup = val['sup']

                if (max_res and val['inf'] >= inf) or (not(max_res) and val['inf'] <= inf):
                    lc_inf = key
                    inf = val['inf']

            if act_key not in comb_dict['G']:
                comb_dict['G'][act_key] = {}

            # if maximum superiour and inferiour value belong to same loadcase, just append it once to other dead loads,
            # else twice with the not corresponding value set to zero
            if lc_sup == lc_inf:        
                comb_dict['G'][act_key][lc_sup] = {'sup': sup, 'inf': inf}
            else:
                comb_dict['G'][act_key][lc_sup] = {'sup': sup, 'inf': 0}
                comb_dict['G'][act_key][lc_inf] = {'sup': 0, 'inf': inf}
           

    dead_load = 0       # combined dead loads

    ### Combination of dead loads
    # PERC-loads (Distinction whether favourable or not based only on single loadcase) 
    for key in comb_dict.get('PERC', ()):
        sup = comb_dict['PERC'][key]['sup']
        inf = comb_dict['PERC'][key]['inf']

        if logging:
            if (max_res and sup > inf) or (not(max_res) and sup < inf): #TODO größer gleich Zeichen?
                log += log_text_dead_load(db, key, 'GAMU', i_point)
            else:
                log += log_text_dead_load(db, key, 'GAMF', i_point)
        
        # if the maximum (minimum) combination is required, add higher absolute value, else lower absolute 
        if (max_res and sup > inf) or (not(max_res) and sup < inf):
            dead_load += sup
        else:
            dead_load += inf


    # G/PERM-loads (Distinction whether favourable or not based on all loadcases within an action) 
    for act_key, act in comb_dict['G'].items():     # iterate over actions
        sup, inf = 0, 0     # inital values

        for LC in act.values():
            sup += LC['sup']
            inf += LC['inf']

        if logging:
            if (max_res and sup > inf) or (not(max_res) and sup < inf):
                for key in act:
                    # if load_case was of type AG_ and superiour value is zero, ignore it (dummy entry)
                    if db[key]['comb_type'].startswith('AG') and act[key]['sup'] == 0:  
                        continue
                    log += log_text_dead_load(db, key, 'GAMU', i_point)
            else:
                for key in act:
                    if db[key]['comb_type'].startswith('AG') and act[key]['inf'] == 0:
                        continue
                    log += log_text_dead_load(db, key, 'GAMF', i_point)
        
        # add higher absolute value to accumulated dead loads
        if (max_res and sup > inf) or (not(max_res) and sup < inf):
            dead_load += sup
        else:
            dead_load += inf


    if logging:     # if logging is activated return additonaly log
        return dead_load, log
    else:
        return dead_load



def combine_live_loads(db: dict, A_nums: list, comb_dict: dict, i_point: int, logging: bool, max_res: bool) -> tuple:
    """Combine all live loads.

    Combination types:
        - Q: Take loadcase only into account if it is unfavourable, set one loadcase as lead, 
            the others as accompanying by multiplying with a psi-factor
        - A_: Take only the most unfavourable loadcase defined within an action, but only if it is unfavourable

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    A_nums : list
        List of all A_-types to combine
    comb_dict : dict
        Preprocessed loadcases with favourable and unfavourable values as defined by comb_DESI
    i_point : int
        Index of value in list at which the combination should take place
    logging : bool
        Decides whether information about the combination process should be tracked
    max_res : bool
        Decides whether the combination should be maximized (True) or minimized (False)

    Returns
    -------
    tuple (float, str)
        if logging = True: Combined live loads and log of combination process
        or
    float
        if logging = False: Combined live loads
    """
    if logging: 
        log = ''

    a_lcs = {'lead': {}, 'acco': {}}

    for a in A_nums:
        for act_key, act in comb_dict[a].items():            
            #lead = act[list(act)[0]]['lead']
            #acco = act[list(act)[0]]['acco']

            lead_max = {'lead': act[list(act)[0]]['lead'], 'acco': 0}
            acco_max = {'lead': 0, 'acco': act[list(act)[0]]['acco']}
            
            for key, val in act.items():
                if (max_res and val['lead'] >= lead_max['lead']) or (not(max_res) and val['lead'] <= lead_max['lead']):
                    lc_lead = key
                    lead_max = val

                if (max_res and val['acco'] >= acco_max['acco']) or (not(max_res) and val['acco'] <= acco_max['acco']):
                    lc_acco = key
                    acco_max = val
            
            if act_key not in comb_dict['Q']:
                comb_dict['Q'][act_key] = {}

            if lc_lead == lc_acco:
                comb_dict['Q'][act_key][lc_lead] = lead_max
            else:
                comb_dict['Q'][act_key][lc_lead] = lead_max
                comb_dict['Q'][act_key][lc_acco] = acco_max

            a_lcs['lead'][lc_lead] = act_key
            a_lcs['acco'][act_key] = lc_acco


    live_load = 0

    #TODO falls Q-Ergebnis sehr klein < 0e-5 ? -> ignorieren und an log anhängen
    if comb_dict['Q']:
        act_1 = list(comb_dict['Q'])[0]
        lc_1 = list(comb_dict['Q'][act_1])[0]   # erster Lastfall in erster Einwirkung
        lead_action = {'lc': lc_1, 'act': act_1, 'dif': comb_dict['Q'][act_1][lc_1]['lead'] - comb_dict['Q'][act_1][lc_1]['acco']}

        acco = 0

        if logging:
            log_lcs = []

        for act_key, act in comb_dict['Q'].items():
            for lc_key, lc in act.items():
                dif = lc['lead'] - lc['acco']

                if (max_res and dif >= lead_action['dif']) or (not(max_res) and dif <= lead_action['dif']):
                    lead_action = {'lc': lc_key, 'act': act_key, 'dif': dif}
                
                acco += lc['acco']

                if logging:
                    log_lcs.append(lc_key)

        if lead_action['lc'] in a_lcs['lead']:
            act = a_lcs['lead'][lead_action['lc']]
            acco_lc = a_lcs['acco'][act]

            acco -= comb_dict['Q'][act][acco_lc]['acco']

            if acco_lc != lead_action['lc'] and logging:
                log_lcs.remove(acco_lc)
        else:
            for lc, act in a_lcs['lead'].items():
                if lc != a_lcs['acco'][act]:
                    acco -= comb_dict['Q'][act][lc]['acco']

                    if logging:
                        log_lcs.remove(lc)    

        if logging:
            log_lcs.remove(lead_action['lc'])

            if (max_res and db[lead_action['lc']]['val'][i_point] > 0) or (not(max_res) and db[lead_action['lc']]['val'][i_point] < 0):
                log += log_text_dead_load(db, lead_action['lc'], 'GAMU', i_point)
            else:
                log += log_text_dead_load(db, lead_action['lc'], 'GAMF', i_point)

            for lc in log_lcs:
                if (max_res and db[lc]['val'][i_point] > 0) or (not(max_res) and db[lc]['val'][i_point] < 0):
                    log += log_text_live_load(db, lc, 'GAMU', 'PSI0', i_point)
            
                else:
                    log += log_text_live_load(db, lc, 'GAMF', 'PSI0', i_point)       
            

        acco -= comb_dict['Q'][lead_action['act']][lead_action['lc']]['acco']               # Wert der mit psi_0 abgeminderten Leiteinwirkung abziehen
        live_load = acco + comb_dict['Q'][lead_action['act']][lead_action['lc']]['lead']    # Leiteinwirkung addieren

    #--------------
    if logging: 
        return live_load, log
    else:
        return live_load





def comb_ULS(db: dict, LCs: dict, max_res: bool, i_point: int, logging: bool = False) -> dict: 

    comb_dict = {'G': {}, 'Q': {}}
    AG_nums = []
    A_nums = []

    for LC in LCs:
        LC = str(LC)

        if db[LC]['comb_type'] == 'G' or db[LC]['comb_type'] == 'PERM':
            if db[LC]['ACT'] not in comb_dict['G']:
                comb_dict['G'][db[LC]['ACT']] = {}

            comb_dict['G'][db[LC]['ACT']][LC] = {'sup': db[LC]['val'][i_point]*db[LC]['GAMU'], 'inf': db[LC]['val'][i_point]*db[LC]['GAMF']}
          

        elif db[LC]['comb_type'] == 'PERC':
            if db[LC]['comb_type'] not in comb_dict:
                comb_dict[db[LC]['comb_type']] = {}

            comb_dict['PERC'][LC] = {'sup': db[LC]['val'][i_point]*db[LC]['GAMU'], 'inf': db[LC]['val'][i_point]*db[LC]['GAMF']}


        elif db[LC]['comb_type'].startswith('AG'):      #TODO ALEX = AG1
            if db[LC]['comb_type'] not in comb_dict:
                AG_nums.append(db[LC]['comb_type'])

                comb_dict[db[LC]['comb_type']] = {}

            if db[LC]['ACT'] not in comb_dict[db[LC]['comb_type']]:
                comb_dict[db[LC]['comb_type']][db[LC]['ACT']] = {}

            comb_dict[db[LC]['comb_type']][db[LC]['ACT']][LC] = {'sup': db[LC]['val'][i_point]*db[LC]['GAMU'], 'inf': db[LC]['val'][i_point]*db[LC]['GAMF']}


        elif db[LC]['comb_type'] == 'Q' or db[LC]['comb_type'] == 'COND':
            if db[LC]['ACT'] not in comb_dict['Q']:
                comb_dict['Q'][db[LC]['ACT']] = {}

            val = db[LC]['val'][i_point]

            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict['Q'][db[LC]['ACT']][LC] = {'lead': val*db[LC]['GAMU'], 'acco': val*db[LC]['GAMU']*db[LC]['PSI0']}
            else:
                comb_dict['Q'][db[LC]['ACT']][LC] = {'lead': val*db[LC]['GAMF'], 'acco': val*db[LC]['GAMF']*db[LC]['PSI0']}

        
        elif db[LC]['comb_type'].startswith('A'):      #TODO EXCL = A1
            comb_type = db[LC]['comb_type']
            if comb_type not in comb_dict:
                A_nums.append(comb_type)

                comb_dict[comb_type] = {}

            if db[LC]['ACT'] not in comb_dict[comb_type]:
                comb_dict[comb_type][db[LC]['ACT']] = {}

            val = db[LC]['val'][i_point]

            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict[comb_type][db[LC]['ACT']][LC] = {'lead': val*db[LC]['GAMU'], 'acco': val*db[LC]['GAMU']*db[LC]['PSI0']}
            else:
                comb_dict[comb_type][db[LC]['ACT']][LC] = {'lead': val*db[LC]['GAMF'], 'acco': val*db[LC]['GAMF']*db[LC]['PSI0']}


    #TODO log AG und A Entscheidung
    #-------------
    if logging: 
        g_load, g_log = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res)
        q_load, q_log = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res)
    else:
        g_load = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res)
        q_load = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res)
    #-----------

    if logging:
        return g_load + q_load, g_log + q_log
    else:
        return g_load + q_load



def comb_SLS(db: dict, LCs: dict, max_res: bool, i_point: int, comb: str, logging: bool = False) -> dict: 
    #TODO log text anpassen
    comb_dict = {'G': {}, 'Q': {}}
    AG_nums = []
    A_nums = []

    for LC in LCs:
        LC = str(LC)

        if db[LC]['comb_type'] == 'G' or db[LC]['comb_type'] == 'PERM':
            if db[LC]['ACT'] not in comb_dict['G']:
                comb_dict['G'][db[LC]['ACT']] = {}

            comb_dict['G'][db[LC]['ACT']][LC] = {'sup': db[LC]['val'][i_point], 'inf': db[LC]['val'][i_point]}
          

        elif db[LC]['comb_type'] == 'PERC':
            if db[LC]['comb_type'] not in comb_dict:
                comb_dict[db[LC]['comb_type']] = {}

            comb_dict['PERC'][LC] = {'sup': db[LC]['val'][i_point], 'inf': db[LC]['val'][i_point]}


        elif db[LC]['comb_type'].startswith('AG'):      #TODO ALEX = AG1
            if db[LC]['comb_type'] not in comb_dict:
                AG_nums.append(db[LC]['comb_type'])

                comb_dict[db[LC]['comb_type']] = {}

            if db[LC]['ACT'] not in comb_dict[db[LC]['comb_type']]:
                comb_dict[db[LC]['comb_type']][db[LC]['ACT']] = {}

            comb_dict[db[LC]['comb_type']][db[LC]['ACT']][LC] = {'sup': db[LC]['val'][i_point], 'inf': db[LC]['val'][i_point]}


        elif db[LC]['comb_type'] == 'Q' or db[LC]['comb_type'] == 'COND':
            if db[LC]['ACT'] not in comb_dict['Q']:
                comb_dict['Q'][db[LC]['ACT']] = {}

            val = db[LC]['val'][i_point]
            #TODO ungünstige rauswerfen oder mit 0 multiplizieren
            if comb == 'PERM':      #TODO gleich nur noch einen Wert angeben
                lead_fac, acco_fac = db[LC]['PSI2'], db[LC]['PSI2']
            elif comb == 'FREQ':
                lead_fac, acco_fac = db[LC]['PSI1'], db[LC]['PSI2']
            elif comb == 'RARE':
                lead_fac, acco_fac = 1, db[LC]['PSI0']

            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict['Q'][db[LC]['ACT']][LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}
            else:
                comb_dict['Q'][db[LC]['ACT']][LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}

        
        elif db[LC]['comb_type'].startswith('A'):      #TODO EXCL = A1
            comb_type = db[LC]['comb_type']
            if comb_type not in comb_dict:
                A_nums.append(comb_type)

                comb_dict[comb_type] = {}

            if db[LC]['ACT'] not in comb_dict[comb_type]:
                comb_dict[comb_type][db[LC]['ACT']] = {}

            val = db[LC]['val'][i_point]

            if comb == 'PERM':
                lead_fac, acco_fac = db[LC]['PSI2'], db[LC]['PSI2']
            elif comb == 'FREQ':
                lead_fac, acco_fac = db[LC]['PSI1'], db[LC]['PSI2']
            elif comb == 'RARE':
                lead_fac, acco_fac = 1, db[LC]['PSI0']

            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict[comb_type][db[LC]['ACT']][LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}
            else:
                comb_dict[comb_type][db[LC]['ACT']][LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}


    #TODO log AG und A Entscheidung
    #-------------
    if logging: 
        g_load, g_log = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res)
        q_load, q_log = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res)
    else:
        g_load = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res)
        q_load = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res)
    #-----------

    if logging:
        return g_load + q_load, g_log + q_log
    else:
        return g_load + q_load
        



test_db = {
    '1': {'ACT': 'G_2', 'type': 'G', 'comb_type': 'G', 'val': [ 20.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '2': {'ACT': 'G_2', 'type': 'G', 'comb_type': 'G', 'val': [-10.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '3': {'ACT': 'Q_A', 'type': 'Q', 'comb_type': 'Q', 'val': [ 12.00,], 'GAMU': 1.50, 'GAMF': 0.00, 'PSI0': 0.70, 'PSI1': 0.50, 'PSI2': 0.30},
    '4': {'ACT': 'S'  , 'type': 'Q', 'comb_type': 'Q', 'val': [ -40.00,], 'GAMU': 1.50, 'GAMF': 0.00, 'PSI0': 0.50, 'PSI1': 0.20, 'PSI2': 0.00},
    '5': {'ACT': 'W'  , 'type': 'Q', 'comb_type': 'A1', 'val': [ -25.00,], 'GAMU': 1.50, 'GAMF': 0.00, 'PSI0': 0.60, 'PSI1': 0.20, 'PSI2': 0.00},
    '6': {'ACT': 'W'  , 'type': 'Q', 'comb_type': 'A1', 'val': [ -30.00,], 'GAMU': 1.50, 'GAMF': 0.00, 'PSI0': 0.60, 'PSI1': 0.20, 'PSI2': 0.00},
    '7': {'ACT': 'T'  , 'type': 'Q', 'comb_type': 'A1', 'val': [ -25.00,], 'GAMU': 1.50, 'GAMF': 0.00, 'PSI0': 0.60, 'PSI1': 0.20, 'PSI2': 0.00},
    '8': {'ACT': 'T'  , 'type': 'Q', 'comb_type': 'A1', 'val': [ -30.00,], 'GAMU': 1.50, 'GAMF': 0.00, 'PSI0': 0.60, 'PSI1': 0.20, 'PSI2': 0.00},
    #'5': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [ 30.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    #'6': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [ 25.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    #'7': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [-20.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    #'8': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [-15.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    #'9': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'G', 'val': [-35.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
}

test_db = {         # ständige Lasten mit ständiger Alternativgruppe (max: 32.8, min: -46.25)
    '1': {'ACT': 'G_2', 'type': 'G', 'comb_type': 'G', 'val': [ 20.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '2': {'ACT': 'G_2', 'type': 'G', 'comb_type': 'G', 'val': [-10.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '3': {'ACT': 'G_1', 'type': 'G', 'comb_type': 'G', 'val': [ 12.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '4': {'ACT': 'G_1', 'type': 'G', 'comb_type': 'G', 'val': [  6.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '5': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [ 30.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '6': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [ 25.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '7': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [-20.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '8': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'AG1', 'val': [-15.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
    '9': {'ACT': 'G_3', 'type': 'G', 'comb_type': 'G', 'val': [-35.00,], 'GAMU': 1.35, 'GAMF': 1.00, 'PSI0': 1.00, 'PSI1': 1.00, 'PSI2': 1.00},
}

LCs = {'1': 'G_2', '2': 'G_2', '3': 'Q_A', '4': 'S', '5': 'W', '6': 'W', '7': 'T', '8': 'T', '9': 1}#'6': 0, '7': 0}#'4': 'G_1', '5': 'G_3', '6': 'G_3', '7': 'G_3', '8': 'G_3', }#'9': 'G_3'}
logging = True
max_res = True

# was passiert, wenn keine G oder Q lasten vorhanden sind

if logging:
    val, log = comb_ULS(test_db, LCs, max_res, 0, logging)
    val, log = comb_SLS(test_db, LCs, max_res, 0, 'PERM', logging)
    print('\nErgebnis:')
    print(f'{val:5.3f}')
    print(' LC:   val*gamma*(psi) = res     (gamma, PART, SUPP, ACT)')
    print('--------------------------------------------------------')
    print(log)
else:
    val = comb_ULS(test_db, LCs, max_res, 0)
    val = comb_SLS(test_db, LCs, max_res, 0, 'PERM')
    print('\nErgebnis:')
    print(val)
