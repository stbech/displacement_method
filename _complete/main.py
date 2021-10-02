from input import parse_input_file
from process import save_database
from output import run_gnuplot
import os


if __name__ == '__main__':
    db = parse_input_file('_input.dat', '+')
    #print(db['load']['act'])
    save_database(db, '_input.json')

    #gnuplot_LC('_input.dat', '1')

    #plotting_comb = {'reaction': None, 'M': None}
    #plotting_LC = {'support', 'load', 'reaction', 'M': None}

    #if '_input.pdf' in os.listdir():
    #    os.remove('_input.pdf')
#
    #for i in range(1):
    #    lc = []
#
    #    lc.append((str(i+1), {'reaction': None, 'load': None}))
#
    #    for s in ('N', 'V', 'M'):
    #        lc.append((str(i+1), {s: 0.2}))
    #    
    #    run_gnuplot('_input.dat', lc, '_input.pdf')