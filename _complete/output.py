import json
from PyPDF2 import PdfFileMerger, PdfFileReader
import extract
import gnuplot
import os

import subprocess

def gnuplot_LC(file: str, LC: str):
    file = file.split('.')[0]

    with open(file + '.json') as f:
        db = json.load(f)

    # Main file
    extract.write_system(''.join((file, '_LC_', LC, '.gpd')), db)
    extract.write_internal_forces(''.join((file, '_LC_', LC, '.gpd')), db, LC, 'a')
    extract.write_max_internal_forces(''.join((file, '_LC_', LC, '.gpd')), db, LC, 'a')
    extract.write_reaction_forces(''.join((file, '_LC_', LC, '.gpd')), db, LC, 'a')

    # Additional information
    extract.write_support(''.join((file, '_LC_', LC, '_add.gpd')), db, 'w')
    extract.write_loads(''.join((file, '_LC_', LC, '_add.gpd')), db, LC, 'a')



def gnuplot_comb(file: str, LC: str, kled: str):
    file = file.split('.')[0]

    with open(file + '.json') as f:
        db = json.load(f)

    # Main file
    extract.write_system(''.join((file, '_comb_', LC, '_', kled, '.gpd')), db)
    extract.write_comb_internal_forces(''.join((file, '_comb_', LC, '_', kled, '.gpd')), db, LC, kled, 'a')
    extract.write_max_comb_internal_forces(''.join((file, '_comb_', LC, '_', kled, '.gpd')), db, LC, kled, 'a')
    extract.write_comb_reaction_forces(''.join((file, '_comb_', LC, '_', kled, '.gpd')), db, LC, kled, 'a')



def run_gnuplot(file: str, LCs: tuple, pdf: str = None):
    file = file.split('.')[0]

    if type(LCs) == list:
        filenames = ['multiplot.gp']

        for LC, plotting in LCs:
            if type(LC) == tuple or type(LC) == list:   # if Combination and KLED are given
                filename = ''.join((file, '_comb_', LC[0], '_', LC[1]))

                if filename + 'gpd' not in os.listdir():
                    gnuplot_comb(file, LC[0], LC[1])
                    filenames.append(filename + '.gpd')
            else:
                filename = ''.join((file, '_LC_', LC))

                if filename + '.gpd' not in os.listdir():
                    gnuplot_LC(file, LC)
                    filenames.extend([filename + '.gpd',  filename + '_add.gpd'])

        gnuplot.multiplot(file, filenames[0], LCs)

        filenames.append('multiplot.pdf')

    else: 
        LC = LCs[0]

        if type(LC) == tuple or type(LC) == list:   # if Combination and KLED are given
            gnuplot_comb(file, LC[0], LC[1])
            gnuplot.plot_comb(file, LC[0], LC[1], LCs[1])

            filename = ''.join((file, '_comb_', LC[0], '_', LC[1]))
            filenames = [filename + '.gp', filename + '.gpd', filename + '.pdf']
        else: 
            gnuplot_LC(file, LC)
            gnuplot.plot_LC(file, LC, LCs[1])

            filename = ''.join((file, '_LC_', LC))
            filenames = [filename + '.gp', filename + '.gpd', filename + '_add.gpd', filename + '.pdf']

    subprocess.run('gnuplot ' + filenames[0])

    if pdf and pdf in os.listdir():
        merger = PdfFileMerger()
        merger.append(PdfFileReader(pdf))
        merger.append(filenames[-1])
        merger.write(pdf)
        merger.close()
    elif pdf:
        os.rename(filenames[-1], pdf)
        filenames.pop()

    for file in filenames:
        os.remove(file)
    