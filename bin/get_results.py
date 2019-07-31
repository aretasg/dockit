#!/usr/bin/env python

import os
import statistics
import re
import sys
import pandas as pd

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(re.sub('bin', '', FILE_DIR), 'results')

def reading_result_pdbqt(pdbqt_dir, protein_ligand):

    with open (pdbqt_dir) as pdbqt_file:
        results = {}
        mode = 1
        for line in pdbqt_file:
            if line.startswith('REMARK VINA RESULT:'):
                results[mode] = line.split()[3:6]
                mode += 1

        affinity_list = [float(value[0]) for key, value in results.items()]
        rmsdlb_list = [float(value[1]) for key, value in results.items() if key != 1]
        rmsdub_list = [float(value[2]) for key, value in results.items() if key != 1]

        data2write = {protein_ligand[1] : {'affinity_mean' : statistics.mean(affinity_list),
                'affinity_SD' : statistics.stdev(affinity_list),
                'rmsd_l.b._mean' : statistics.mean(rmsdlb_list),
                'rmsd_l.b._SD' : statistics.stdev(rmsdlb_list),
                'rmsd_u.b._mean' : statistics.mean(rmsdub_list),
                'rmsd_u.b._SD' : statistics.stdev(rmsdub_list),
                'modes' : len(results)}}

        return data2write

def collecting_results(path):

    docking_data = {}

    for subdir, dirs, files in os.walk(path):
        for file in files:
            # print (os.path.join(subdir, file))
            if file.endswith('_vina.pdbqt'):
                m_obj = re.search(r'(.*)_vina.pdbqt', file)
                if m_obj:
                    protein_ligand = m_obj.groups()[0].split('-')
                else:
                    print('Failed to find PDBQT results files.')
                    sys.exit()

                data2write = reading_result_pdbqt(os.path.join(subdir, file), protein_ligand)

                if protein_ligand[0] not in docking_data.keys():
                    docking_data[protein_ligand[0]] = data2write
                else:
                    docking_data[protein_ligand[0]].update(data2write)

    return docking_data

def dump_csv(docking_data):

    # creating pandas dataframe
    for key, value in docking_data.items():
        df = pd.DataFrame(value)
        df = df.transpose().round(3)
        df = df[['affinity_mean', 'affinity_SD', 'rmsd_l.b._mean', 'rmsd_l.b._SD',
             'rmsd_u.b._mean', 'rmsd_u.b._SD', 'modes']]
        df.to_csv(os.path.join(RESULTS_PATH,'{0}_results_summary.csv'.format(key)))

    return True

def main():

    if not os.path.isdir(RESULTS_PATH):
        print('Results folder not found.')
        return None
    # extracting results from vina files
    docking_data = collecting_results(RESULTS_PATH)

    # dumping csv
    dump_csv(docking_data)

    return True

if __name__ == "__main__":

    main()
