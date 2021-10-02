from functools import reduce


def log_text_ULS_dead_load(db: dict, lc: str, komb: str, path: tuple, gamma: str, i_point: int) -> str:
    """Return text for log-file with all relevant parameters for a load, which is not reduced by a factor psi.
    
    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    lc : str
        Number of loadcase
    gamma : str
        superior or inferior partial safety factor, used to check favourability ['GAMU' or 'GAMF']
    i_point : int
        Index of value in list at which the combination should take place

    Returns
    -------
    str
        Information about use of loadcase within the combination
    """

    gamma_text = 'gamma_F' if gamma == 'GAMF' else 'gamma_U'    # change gamma to a more readable format, where the last char is easily distinguishable
    
    exp_path = ['calc', 'LC', lc]
    exp_path.extend(path)
    val = reduce(dict.get, exp_path, db)[i_point]

    params = db['comb']['komb'][komb]['LC'][lc]
    act = db["load"]["act"][params[0]]

    return f'{lc:>3}: {val:>7.3f}*{act[gamma]:>4.2f}      = {(val*act[gamma]):>7.3f}  ({gamma_text}, {act["part"]}, {params[1]:>4}, {params[0]:>3})\n'



def log_text_ULS_live_load(db: dict, lc: str, komb: str, path: tuple, gamma: str, psi: str, i_point: int) -> str:
    """Return text for log-file with all relevant parameters for a load, which is reduced by a factor psi.
    
    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    lc : str
        Number of loadcase
    gamma : str
        superior or inferior partial safety factor ['GAMU' or 'GAMF']
    psi : str
        used combination factor ['PSI0', 'PSI1' or 'PSI2']
    i_point : int
        Index of value in list at which the combination should take place

    Returns
    -------
    str
        Information about use of loadcase within the combination
    """

    gamma_text = 'gamma_F' if gamma == 'GAMF' else 'gamma_U'    # change gamma to a more readable format, where the last char is easily distinguishable

    exp_path = ['calc', 'LC', lc]
    exp_path.extend(path)
    val = reduce(dict.get, exp_path, db)[i_point]

    params = db['comb']['komb'][komb]['LC'][lc]
    act = db["load"]["act"][params[0]]

    return f'{lc:>3}: {val:>7.3f}*{act[gamma]:>4.2f}*{act[psi]:>4.2f} = {(val*act[gamma]*act[psi]):>7.3f}  ({gamma_text}, {act["part"]}, {params[1]:>4}, {params[0]:>3})\n'



def log_text_SLS_dead_load(db: dict, lc: str, komb: str, path: tuple, i_point: int) -> str:
    """Return text for log-file with all relevant parameters for a load, which is not reduced by a factor psi.
    
    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    lc : str
        Number of loadcase
    i_point : int
        Index of value in list at which the combination should take place

    Returns
    -------
    str
        Information about use of loadcase within the combination
    """

    exp_path = ['calc', 'LC', lc]
    exp_path.extend(path)
    val = reduce(dict.get, exp_path, db)[i_point]
    
    params = db['comb']['komb'][komb]['LC'][lc]
    act = db["load"]["act"][params[0]]

    return f'{lc:>3}: {val:>7.3f}           = {val:>7.3f}  ({act["part"]}, {params[1]:>4}, {params[0]:>3})\n'



def log_text_SLS_live_load(db: dict, lc: str, komb: str, path: tuple, gamma: str, psi: str, i_point: int) -> str:
    """Return text for log-file with all relevant parameters for a load, which is reduced by a factor psi.

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    lc : str
        Number of loadcase
    gamma : str
        superior or inferior partial safety factor, used to check favourability ['GAMU' or 'GAMF']
    psi : str
        used combination factor ['PSI0', 'PSI1' or 'PSI2']
    i_point : int
        Index of value in list at which the combination should take place

    Returns
    -------
    str
        Information about use of loadcase within the combination
    """

    gamma_val = 0 if gamma == 'GAMF' else 1     # multiply favourable loads by zero

    exp_path = ['calc', 'LC', lc]
    exp_path.extend(path)
    val = reduce(dict.get, exp_path, db)[i_point]
    
    params = db['comb']['komb'][komb]['LC'][lc]
    act = db["load"]["act"][params[0]]

    return f'{lc:>3}: {val:>7.3f}*{gamma_val:>4.2f}*{act[psi]:>4.2f} = {(val*gamma_val*act[psi]):>7.3f}  ({act["part"]}, {params[1]:>4}, {params[0]:>3})\n'



def log_text_dead_load(db: dict, lc: str, komb: str, path: tuple, gamma: str, i_point: int, state: str) -> str:
    """Decide whether log text for dead loads should include partial safety factors

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    lc : str
        Number of loadcase
    gamma : str
        Superior or inferior partial safety factor ['GAMU' or 'GAMF']
    i_point : int
        Index of value in list at which the combination should take place
    state : str
        Ultimate or serviceability limit state

    Returns
    -------
    str
        Log text passed by underlying function
    """

    if state == 'ULS':
        return log_text_ULS_dead_load(db, lc, komb, path, gamma, i_point)
    else:
        return log_text_SLS_dead_load(db, lc, komb, path, i_point)



def log_text_live_load(db: dict, lc: str, komb: str, path: tuple, gamma: str, psi: str, i_point: int, state: str) -> str:
    """Decide whether log text for live loads should include partial safety factors

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    lc : str
        Number of loadcase
    gamma : str
        Superior or inferior partial safety factor ['GAMU' or 'GAMF']
    psi : str
        Used combination factor ['PSI0', 'PSI1' or 'PSI2']
    i_point : int
        Index of value in list at which the combination should take place
    state : str
        Ultimate or serviceability limit state

    Returns
    -------
    str
        Log text passed by underlying function
    """

    if state == 'ULS':
        return log_text_ULS_live_load(db, lc, komb, path, gamma, psi, i_point)
    else:
        return log_text_SLS_live_load(db, lc, komb, path, gamma, psi, i_point)



def combine_dead_loads(db: dict, AG_nums: list, comb_dict: dict, i_point: int, logging: bool, max_res: bool, state: str, path: tuple = None, komb: str = None) -> tuple:
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
    #TODO add state and path

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
                log += log_text_dead_load(db, key, komb, path, 'GAMU', i_point, state)
            else:
                log += log_text_dead_load(db, key, komb, path, 'GAMF', i_point, state)
        
        # if the maximum (minimum) combination is required, add higher absolute value, else lower absolute 
        if (max_res and sup > inf) or (not(max_res) and sup < inf):
            dead_load += sup
        else:
            dead_load += inf


    # G/PERM-loads (Distinction whether favourable or not based on all loadcases within an action) 
    for act_key, act in comb_dict['G'].items():     # iterate over actions
        sup, inf = 0, 0     # inital values

        for nr_LC in act.values():
            sup += nr_LC['sup']
            inf += nr_LC['inf']

        if logging:
            if (max_res and sup > inf) or (not(max_res) and sup < inf):
                for key in act:
                    # if load_case was of type AG_ and superiour value is zero, ignore it (dummy entry)
                    if db['comb']['komb'][komb]['LC'][key][1].startswith('AG') and act[key]['sup'] == 0:  
                        continue

                    log += log_text_dead_load(db, key, komb, path, 'GAMU', i_point, state)
            else:
                for key in act:
                    if db['comb']['komb'][komb]['LC'][key][1].startswith('AG') and act[key]['inf'] == 0:
                        continue

                    log += log_text_dead_load(db, key, komb, path, 'GAMF', i_point, state)
        
        # add higher absolute value to accumulated dead loads
        if (max_res and sup > inf) or (not(max_res) and sup < inf):
            dead_load += sup
        else:
            dead_load += inf


    if logging:     # if logging is activated return additonaly log
        return dead_load, log
    else:
        return dead_load



def combine_live_loads(db: dict, A_nums: list, comb_dict: dict, i_point: int, logging: bool, max_res: bool, state: str, path: tuple = None, komb: str = None) -> tuple:
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
    #TODO add state and path

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

    a_lcs = {'lead': {}, 'acco': {}}        # save number of leading and accompanying loadcase per A_-type

    for a in A_nums:            # iterate over alternative load groups (A_)
        a_lcs['acco'][a] = {}   # initiate empty dictionary

        for act_key, act in comb_dict[a].items():   # iterate over actions
            # define inital value vor maximum (or minimum) leading and accompanying value of A_ as values of first loadcase
                # set other value to zero
            lead_max = {'lead': act[list(act)[0]]['lead'], 'acco': 0}
            acco_max = {'lead': 0, 'acco': act[list(act)[0]]['acco']}
            
            for key, val in act.items():       
                # check all loadcases, whether a higher absolute value has been found and save loadcase number
                if (max_res and val['lead'] >= lead_max['lead']) or (not(max_res) and val['lead'] <= lead_max['lead']):
                    lc_lead = key
                    lead_max = val

                if (max_res and val['acco'] >= acco_max['acco']) or (not(max_res) and val['acco'] <= acco_max['acco']):
                    lc_acco = key
                    acco_max = val
            
            if act_key not in comb_dict['Q']:       # initate dictionary in live_loads if not existent
                comb_dict['Q'][act_key] = {}

            if lc_lead == lc_acco:                  # if resulting leading and accompanying loadcase are the same, only save one
                comb_dict['Q'][act_key][lc_lead] = lead_max #TODO check!
            else:
                comb_dict['Q'][act_key][lc_lead] = lead_max
                comb_dict['Q'][act_key][lc_acco] = acco_max

            a_lcs['lead'][lc_lead] = (act_key, a)   # save action and alternative load group 
            a_lcs['acco'][a][act_key] = lc_acco     # save accompanying load case


    live_load = 0       # inital value of resulting live loads

    #TODO falls Q-Ergebnis sehr klein < 0e-5 ? -> ignorieren und an log anhängen
    if comb_dict['Q']:      # only continue if live loads to combine
        # set initial leading action as first loadcase in first action
        act_1 = list(comb_dict['Q'])[0]
        lc_1 = list(comb_dict['Q'][act_1])[0]  
        lead_case = {'lc': lc_1, 'act': act_1, 'dif': comb_dict['Q'][act_1][lc_1]['lead'] - comb_dict['Q'][act_1][lc_1]['acco']}

        acco = 0    # initial value for sum of accompanying loads

        if logging:
            log_lcs = []    # save all loadcase numbers
#TODO alle Lastfälle je ACT zusammenfassen, dann Leiteinwirkung bestimmen
        for act_key, act in comb_dict['Q'].items():     # iterate over actions
            for lc_key, lc in act.items():              # iterate over loadcases
                # the leading loadcase is the loadcase with the maximum difference between leading and accompanying value 
                dif = lc['lead'] - lc['acco']           
                
                if (max_res and dif >= lead_case['dif']) or (not(max_res) and dif <= lead_case['dif']):
                    lead_case = {'lc': lc_key, 'act': act_key, 'dif': dif}    # set leading loadcase to case with highest difference
                
                acco += lc['acco']      # sum up accompanying values

                if logging:             # add loadcase number
                    log_lcs.append(lc_key)
        

        for lc, act in a_lcs['lead'].items():               # iterate over alternative load groups
                acco_lc = a_lcs['acco'][act[1]][act[0]]     # get loadcase number of accompanying value of the group

                if lc != acco_lc:                           # if both loadcases are the same, no value removing is required
                    if lc != lead_case['lc']:               # leading group loadcase is not overall leading: leading group loadcase not required
                        acco -= comb_dict['Q'][act[0]][lc]['acco']    # remove accompanying value of leading group loadcase

                        if logging:
                            log_lcs.remove(lc) 
                    else:                           # leading group loadcase is overall leading: accompanying group loadcase not required
                        acco -= comb_dict['Q'][act[0]][acco_lc]['acco']    # remove accompanying value of accompanying group loadcase

                        if logging:
                            log_lcs.remove(acco_lc) 


        if logging:
            log_lcs.remove(lead_case['lc'])     # remove leading loadcase to print as first log

            # define combination factors used for logging
            psi_acco = 'PSI0'       # combination factor for ULS and SLS-RARE

            if state.endswith('-PERM'):
                psi_lead, psi_acco = 'PSI2', 'PSI2'       #TODO falsch, da keine LEW?
            elif state.endswith('-FREQ'):
                psi_lead, psi_acco = 'PSI1', 'PSI2'     

            exp_path = ['calc', 'LC', lead_case['lc']]
            exp_path.extend(path)
            val = reduce(dict.get, exp_path, db)[i_point]

            # log leading loadcase with GAMU if unfavourable or GAMF if favourable
            if (max_res and val > 0) or (not(max_res) and val < 0):
                # if ULS or SLS-Rare no combination factor is required for leading loadcase, hence log like a dead load
                if state.endswith('-PERM') or state.endswith('FREQ'):
                    log += log_text_live_load(db, lead_case['lc'], komb, path, 'GAMU', psi_lead, i_point, state)
                else:
                    log += log_text_dead_load(db, lead_case['lc'], komb, path, 'GAMU', i_point, state)
            else:
                if state.endswith('-PERM') or state.endswith('FREQ'):
                    log += log_text_live_load(db, lead_case['lc'], komb, path, 'GAMF', psi_lead, i_point, state)
                else:
                    log += log_text_dead_load(db, lead_case['lc'], komb, path, 'GAMF', i_point, state)


            # for all accompanying loadcases log with according combination factor
            for lc in log_lcs:
                exp_path = ['calc', 'LC', lc]
                exp_path.extend(path)
                val = reduce(dict.get, exp_path, db)[i_point]

                if (max_res and val > 0) or (not(max_res) and val < 0):
                    log += log_text_live_load(db, lc, komb, path, 'GAMU', psi_acco, i_point, state)
                else:
                    log += log_text_live_load(db, lc, komb, path, 'GAMF', psi_acco, i_point, state)       
            
        # remove accompanying value of leading loadcase from sum
        acco -= comb_dict['Q'][lead_case['act']][lead_case['lc']]['acco'] 
        # add leading value of leading loadcase              
        live_load = acco + comb_dict['Q'][lead_case['act']][lead_case['lc']]['lead']    

    #--------------
    if logging: 
        return live_load, log
    else:
        return live_load





def comb_ULS(db: dict, path: tuple, komb: str, LCs: list, max_res: bool, i_point: int, logging: bool = False) -> tuple: 
    """Combination for Ultimate limit state

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    path: tuple
        #TODO add
    LCs : dict
        Loadcases to combine
    max_res : bool
        Decides whether the combination should be maximized (True) or minimized (False)
    i_point : int
        Index of value in list at which the combination should take place
    logging : bool, optional
        Decides whether information about the combination process should be tracked, by default False        

    Returns
    -------
    tuple (float, str)
        if logging = True: Combined live and dead loads and log of combination process
        or
    float
        if logging = False: Combined live and dead loads
    """

    comb_dict = {'G': {}, 'Q': {}}      # initiate dictionary for saving favourable and unfavourable values of loadcases
    AG_nums = []
    A_nums = []
    
    for nr_LC in LCs:
        act, sup = db['comb']['komb'][komb]['LC'][nr_LC]
        exp_path = ['calc', 'LC', nr_LC]
        exp_path.extend(path)
        val = reduce(dict.get, exp_path, db)[i_point]

        # if combination type is G, save superior and inferior value of loadcase, grouped by actions
        if sup == 'G' or sup == 'PERM':
            if act not in comb_dict['G']:
                comb_dict['G'][act] = {}

            comb_dict['G'][act][nr_LC] = {'sup': val*db['load']['act'][act]['GAMU'], 'inf': val*db['load']['act'][act]['GAMF']}
          
        # if combination type is PERC, just save superior and inferior value of loadcase
        elif sup == 'PERC':
            if sup not in comb_dict:
                comb_dict[sup] = {}

            comb_dict['PERC'][nr_LC] = {'sup': val*db['load']['act'][act]['GAMU'], 'inf': val*db['load']['act'][act]['GAMF']}

        # if combination type is AG_, save superior and inferior value of loadcase to own dictionary, grouped by action
        elif sup.startswith('AG') or sup == 'ALEX':   
            comb_type = 'AG1' if sup == 'ALEX' else sup     # convert ALEX to AG1

            if comb_type not in comb_dict:
                AG_nums.append(comb_type)       # save number of permanent alternative load group

                comb_dict[comb_type] = {}

            # group loadcases by action
            if act not in comb_dict[comb_type]:
                comb_dict[comb_type][act] = {}

            comb_dict[comb_type][act][nr_LC] = {'sup': val*db['load']['act'][act]['GAMU'], 'inf': val*db['load']['act'][act]['GAMF']}

        # if combination type is Q, save leading and accompanying value of loadcase
        elif sup == 'Q' or sup == 'COND':
            if act not in comb_dict['Q']:
                comb_dict['Q'][act] = {}

            val = val

            # if load is unfavourable multiply by GAMU else multiply by GAMF
            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict['Q'][act][nr_LC] = {'lead': val*db['load']['act'][act]['GAMU'], 'acco': val*db['load']['act'][act]['GAMU']*db['load']['act'][act]['PSI0']}
            else:
                comb_dict['Q'][act][nr_LC] = {'lead': val*db['load']['act'][act]['GAMF'], 'acco': val*db['load']['act'][act]['GAMF']*db['load']['act'][act]['PSI0']}

        # if combination type is A_, save leading and accompanying value of loadcase to own dictionary, grouped by action
        elif sup.startswith('A') or sup == 'EXCL':     
            comb_type = 'A1' if sup == 'EXCL' else sup  # convert EXCL to A1

            if comb_type not in comb_dict:
                A_nums.append(comb_type)    # save number of alternative load group

                comb_dict[comb_type] = {}

            if act not in comb_dict[comb_type]:
                comb_dict[comb_type][act] = {}

            val = val

            # if load is unfavourable multiply by GAMU else multiply by GAMF
            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict[comb_type][act][nr_LC] = {'lead': val*db['load']['act'][act]['GAMU'], 'acco': val*db['load']['act'][act]['GAMU']*db['load']['act'][act]['PSI0']}
            else:
                comb_dict[comb_type][act][nr_LC] = {'lead': val*db['load']['act'][act]['GAMF'], 'acco': val*db['load']['act'][act]['GAMF']*db['load']['act'][act]['PSI0']}


    #TODO log AG und A Entscheidung
    #-------------
    if logging: 
        g_load, g_log = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res, 'ULS', path, komb)
        q_load, q_log = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res, 'ULS', path, komb)
    else:
        g_load = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res, 'ULS')
        q_load = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res, 'ULS')
    #-----------

    if logging:
        return g_load + q_load, g_log + q_log
    else:
        return g_load + q_load



def comb_SLS(db: dict, path: tuple, komb: str, LCs: list, max_res: bool, i_point: int, comb: str, logging: bool = False) -> tuple: 
    """Combination for Serviceability limit state

    Parameters
    ----------
    db : dict
        Dictionary containing all defined loadcases and actions
    path : tuple
        #TODO add
    LCs : dict
        Loadcases to combine
    max_res : bool
        Decides whether the combination should be maximized (True) or minimized (False)
    i_point : int
        Index of value in list at which the combination should take place
    comb : str
        Abbreviation of desired combination formula (RARE, FREQ, PERM)
    logging : bool, optional
        Decides whether information about the combination process should be tracked, by default False        

    Returns
    -------
    tuple (float, str)
        if logging = True: Combined live and dead loads and log of combination process
        or
    float
        if logging = False: Combined live and dead loads
    """

    #TODO log text anpassen

    comb_dict = {'G': {}, 'Q': {}}      # initiate dictionary for saving favourable and unfavourable values of loadcases
    AG_nums = []
    A_nums = []
    #TODO falsch Lastfälle nach KLED auswählen
    for nr_LC in LCs:
        act, sup = db['comb']['komb'][komb]['LC'][nr_LC]
        exp_path = ['calc', 'LC', nr_LC]
        exp_path.extend(path)
        val = reduce(dict.get, exp_path, db)[i_point]

        # if combination type is G, save superior and inferior value of loadcase, grouped by actions
        if sup == 'G' or sup == 'PERM':
            if act not in comb_dict['G']:
                comb_dict['G'][act] = {}
            #TODO Werte gleich -> einfachere Überlagerung?
            comb_dict['G'][act][nr_LC] = {'sup': val, 'inf': val}
          
        # if combination type is PERC, just save superior and inferior value of loadcase
        elif sup == 'PERC':
            if sup not in comb_dict:
                comb_dict[sup] = {}

            comb_dict['PERC'][nr_LC] = {'sup': val, 'inf': val}

        # if combination type is AG_, save superior and inferior value of loadcase to own dictionary, grouped by action
        elif sup.startswith('AG'):     
            comb_type = 'AG1' if sup == 'ALEX' else sup     # convert ALEX to AG1

            if comb_type not in comb_dict:
                AG_nums.append(comb_type)       # save number of permanent alternative load group

                comb_dict[comb_type] = {}

            # group loadcases by action
            if act not in comb_dict[comb_type]:
                comb_dict[comb_type][act] = {}

            comb_dict[comb_type][act][nr_LC] = {'sup': val, 'inf': val}

        # if combination type is Q, save leading and accompanying value of loadcase
        elif sup == 'Q' or sup == 'COND':
            if act not in comb_dict['Q']:
                comb_dict['Q'][act] = {}

            # get combination factor for required combination formula
            if comb == 'PERM':      #TODO gleich nur noch einen Wert angeben
                lead_fac, acco_fac = db['load']['act'][act]['PSI2'], db['load']['act'][act]['PSI2']
            elif comb == 'FREQ':
                lead_fac, acco_fac = db['load']['act'][act]['PSI1'], db['load']['act'][act]['PSI2']
            elif comb == 'RARE':
                lead_fac, acco_fac = 1, db['load']['act'][act]['PSI0']
            
            # if load is unfavourable multiply by leading factor else multiply by accompanying factor
            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict['Q'][act][nr_LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}
            else:
                val = 0     # set value to zero, because it is favourable, do not ignore so that it shows in log
                comb_dict['Q'][act][nr_LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}

        # if combination type is A_, save leading and accompanying value of loadcase to own dictionary, grouped by action
        elif sup.startswith('A'):
            comb_type = 'A1' if sup == 'EXCL' else sup  # convert EXCL to A1

            if comb_type not in comb_dict:
                A_nums.append(comb_type)        # save number of alternative load group

                comb_dict[comb_type] = {}

            if act not in comb_dict[comb_type]:
                comb_dict[comb_type][act] = {}

            # get combination factor for required combination formula
            if comb == 'PERM':
                lead_fac, acco_fac = db['load']['act'][act]['PSI2'], db['load']['act'][act]['PSI2']
            elif comb == 'FREQ':
                lead_fac, acco_fac = db['load']['act'][act]['PSI1'], db['load']['act'][act]['PSI2']
            elif comb == 'RARE':
                lead_fac, acco_fac = 1, db['load']['act'][act]['PSI0']

            # if load is unfavourable multiply by leading factor else multiply by accompanying factor
            if (max_res and val > 0) or (not(max_res) and val < 0):
                comb_dict[comb_type][act][nr_LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}
            else:
                val = 0     # set value to zero, because it is favourable, do not ignore so that it shows in log
                comb_dict[comb_type][act][nr_LC] = {'lead': val*lead_fac, 'acco': val*acco_fac}


    #TODO log AG und A Entscheidung
    #-------------
    if logging: 
        g_load, g_log = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res, 'SLS-' + comb, path, komb)
        q_load, q_log = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res, 'SLS-' + comb, path, komb)
    else:
        g_load = combine_dead_loads(db, AG_nums, comb_dict, i_point, logging, max_res, 'SLS-' + comb)
        q_load = combine_live_loads(db, A_nums, comb_dict, i_point, logging, max_res, 'SLS-' + comb)
    #-----------

    if logging:
        return g_load + q_load, g_log + q_log
    else:
        return g_load + q_load
        

