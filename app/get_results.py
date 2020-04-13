#!/usr/bin/env python

import os
import re
import sys
import csv


def parse_result_pdbqt(pdbqt_dir, engine):

    with open(pdbqt_dir, 'r') as pdbqt_file:
        results = {}
        mode = 1
        for line in pdbqt_file:
            if line.startswith('REMARK VINA RESULT:'):
                affinity, lb, ub = line.split()[3:6]
                results[mode] = {'affinity': affinity, 'lb': lb, 'ub': ub, 'engine': engine}
                mode += 1

        return results


def parse_smina_result_pdbqt(pdbqt_dir, engine):

    with open(pdbqt_dir, 'r') as pdbqt_file:
        results = {}
        mode = 1
        ub = None
        for line in pdbqt_file:
            if line.startswith('REMARK minimizedAffinity'):
                affinity = line.split()[2]
            elif line.startswith('REMARK minimizedRMSD'):
                lb = line.split()[2]
                results[mode] = {'affinity': affinity, 'lb': lb, 'ub': ub, 'engine': engine}
                mode += 1

        return results


def collect_results(path):

    docking_res_dict = {}

    for subdir, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.pdbqt'):
                m_obj = re.search(r'res_(.*)_(.*).pdbqt', file)
                if m_obj:
                    engine = m_obj.groups()[0]
                    target, ligand = m_obj.groups()[1].split('-')
                print(engine)
                results = parse_result_pdbqt(os.path.join(subdir, file), engine)
                if not results:
                    results = parse_smina_result_pdbqt(os.path.join(subdir, file), engine)

                if target not in docking_res_dict:
                    docking_res_dict[target] = {ligand: results}
                else:
                    docking_res_dict[target][ligand] = results

    return docking_res_dict


def dump_csv(docking_data, results_dir):

    csv_dir = os.path.join(results_dir, 'dockit_results.csv')
    with open(csv_dir, mode='w') as csv_file:
        headers = ['target', 'ligand', 'mode', 'affinity (kcal/mol)', 'rmsd l.b.', 'rmsd u.b.', 'engine']
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for target, ligand in docking_data.items():
            for lig, result in ligand.items():
                for mode, res in result.items():
                    writer.writerow([target, lig, mode, res['affinity'], res['lb'], res['ub'], res['engine']])


def get_results():

    app_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir, app = os.path.split(app_dir)
    results_dir = os.path.join(root_dir, 'results')

    if not os.path.isdir(results_dir):
        print('Results folder not found.')
        return None

    docking_data = collect_results(results_dir)
    dump_csv(docking_data, results_dir)


if __name__ == "__main__":

    get_results()
