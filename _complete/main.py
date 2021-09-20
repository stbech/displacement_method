from input import parse_input_file
from process import save_database

from output import gnuplot_LC

if __name__ == '__main__':
    #db = parse_input_file('_input.dat', '+')
    #print(db['load']['act'])
    #save_database(db, '_input.json')

    gnuplot_LC('_input.dat', '1')