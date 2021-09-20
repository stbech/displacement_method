from superposition import comb_SLS, comb_ULS
#TODO KLED

def combine(db: dict, komb: str, kled: str, LCs: list):
    extr = db['comb']['komb'][komb]['extr']
    
    for etyp in db['comb']['komb'][komb]['res'].items():
        if etyp[0] == 'bar':
            internal = 's'

            bar_nrs = db['system']['bars']

            for zust in etyp[1].items():
                if zust[0] == 'MY':
                    force = 'M'
                elif zust[0] == 'VZ':
                    force = 'V'
                elif zust[0] == 'N':
                    force = 'N'

                for mami in zust[1]:
                    db['comb']['komb'][komb]['res'][etyp[0]][zust[0]][mami][kled] = {}

                    for bar in bar_nrs:
                        path = (internal, bar, force)

                        point_length = len(db['system']['bars'][bar]['points'])
                        res_list = []

                        for i in range(point_length):
                            if extr == 'DESI' and mami == 'max':
                                res = comb_ULS(db, path, komb, LCs, True, i)
                            elif extr == 'DESI' and mami == 'min':
                                res = comb_ULS(db, path, komb, LCs, False, i)
                            elif mami == 'max':
                                res = comb_SLS(db, path, komb, LCs, True, i, extr)
                            elif mami == 'max':
                                res = comb_SLS(db, path, komb, LCs, False, i, extr)
                        
                            res_list.append(res)
                    
                        db['comb']['komb'][komb]['res'][etyp[0]][zust[0]][mami][kled][bar] = res_list

    return db

    #print(db['comb']['komb'][komb]['res'])

        #res = comb_SLS(db, ('s', '1', 'V'), '1', True, 0, 'RARE', logging)#'RARE')