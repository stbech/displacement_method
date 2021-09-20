import json
from extract import *

#TODO falls gpds schon für Richtigen Lastfall nicht nochmal erstellen

def gnuplot_LC(file: str, LC: str):
    file = file.split('.')[0]

    with open(file + '.json') as f:
        db = json.load(f)

    # Main file
    write_system(''.join((file, '_LC_', LC, '.gpd')), db)
    write_internal_forces(''.join((file, '_LC_', LC, '.gpd')), db, LC, 'a')

    # Additional information
    write_local_z_axis(''.join((file, '_LC_', LC, '_add.gpd')), db)
    write_support(''.join((file, '_LC_', LC, '_add.gpd')), db, 'a')
    