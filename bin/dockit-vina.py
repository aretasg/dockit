#!/usr/bin/env python

# todo: logging, tests, pdb file parser, test with crontab

import os
import sys
import argparse
import pandas as pd
from emm import run_emm

def pdb_parser(pdb_file):

    # checking if the file is in PDB format
    with open(os.path.abspath(args.pdb_file)) as input_file:
        atom_count = 0
        for line in input_file:
            if 'ATOM' in line or 'HETATM' in line:
                atom_count += 1
                break
        if atom_count == 0:
            print('Input file does not seem to be in PDB format.')
            return False
        else:
            return True

def vina_config():
    pass

if __name__ == "__main__":

    # CLI argument parser
    # -c flag creates a default conifguration file as an example; -v path
    parser = argparse.ArgumentParser(
        description='''
        Autodock Vina wrapper for performing highthrough-put molecular docking for multiple targets with flexible residue support.
        ''',
        epilog='Example usage in CLI: "python dockit-vina.py"')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-p', '--vina_path',
        help='Specify the flag to create default configuration file.',
        action='store_false')
    optional.add_argument('-c', '--config',
        help='Specify the flag to create default configuration file.',
        action='store_false')
    optional.add_argument('-v', '--verbose',
        help='Specify the flag to include verbose messages in console.',
        action='store_false')
    args = parser.parse_args()

    # checking if $VINAHOME and $AUTODOCKHOME is set
    if not 'VINAHOME' in os.environ:
        print('$VINAHOME environment variable is not set. Please refer to the help section.')
        sys.exit()

    if not 'AUTODOCKHOME' in os.environ:
        print('$AUTODOCKHOME environment variable is not set. Please refer to the help section.')
        sys.exit()

    # setting path to parameter folder
    # path = os.path.abspath(__file__)
    bin_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir, bin_ = os.path.split(bin_dir)

    # creating ligand and target directories
    ligands_dir = os.path.join(root_dir, 'ligands', 'PDB')
    if not os.path.exists(ligands_dir):
        os.makedirs(ligands_dir)

    targets_dir = os.path.join(root_dir, 'targets', 'PDB')
    if not os.path.exists(targets_dir):
        os.makedirs(targets_dir)

    # reading docking parameters
    param_dir = os.path.join(root_dir, 'docking_param.csv')
    param_df = pd.read_csv(param_dir)

    # checking if there are any ligand and targets files
    # todo: should also check if files are in PDB format
    if len([protein for protein in os.listdir(targets_dir) if protein.lower().endswith('.pdb')]) == 0:
        print('Failed to find PDB files in {0} direcotry'.format(targets_dir))
        sys.exit()

    if len([ligand for ligand in os.listdir(ligands_dir) if ligand.lower().endswith('.pdb')]) == 0:
        print('Failed to find PDB files in {0} direcotry'.format(ligands_dir))
        sys.exit()

    # performing ligand energy minimisation using Ambertools; converting to PDBQT
    energy_min_status = False
    if sys.platform == 'win32':
        print('Energy minimization of molecules in not supported on Windows. Skipping.')
    else:
        energy_min_status = True
        for ligand in os.listdir(ligands_dir):
            if ligand.lower().endswith('.pdb'):
                run_emm(os.path.join(ligands_dir, ligand))

    # creating ligand PDBQT dir
    ligands_pdbqt_dir = os.path.join(root_dir, 'ligands', 'PDBQT')
    if not os.path.exists(ligands_pdbqt_dir):
        os.makedirs(ligands_pdbqt_dir)

    # converting ligands to PDBQT
    pythonsh_dir = os.path.join('$AUTODOCKHOME', 'bin', 'pythonsh')

    for ligand in os.listdir(ligands_dir):
        if energy_min_status and '_min' in ligand:
            os.system('{0} {1} -l {2} -o {3} -A hydrogens -U nphs -v'.format(pythonsh_dir,
                os.path.join(root_dir, 'bin', 'prepare_ligand4.py'),
                os.path.join(ligands_dir, ligand),
                os.path.join(ligands_pdbqt_dir, ligand.replace('pdb', 'pdbqt').replace('.PDB', '.pdbqt'))))
        elif energy_min_status is False and '_min' not in ligand:
                os.system('{0} {1} -l {2} -o {3} -A hydrogens -U nphs -v'.format(pythonsh_dir,
                os.path.join(root_dir, 'bin', 'prepare_ligand4.py'),
                os.path.join(ligands_dir, ligand),
                os.path.join(ligands_pdbqt_dir, ligand.replace('pdb', 'pdbqt').replace('.PDB', '.pdbqt'))))

    # creating ligand PDBQT dir
    targets_pdbqt_dir = os.path.join(root_dir, 'targets', 'PDBQT')
    if not os.path.exists(targets_pdbqt_dir):
        os.makedirs(targets_pdbqt_dir)

    # converting targets to PDBQT
    for target in os.listdir(targets_dir):
        os.system('{0} {1} -r {2} -o {3} -A checkhydrogens -U nphs -v'.format(pythonsh_dir,
        os.path.join(root_dir, 'bin', 'prepare_receptor4.py'),
        os.path.join(targets_dir, target),
        os.path.join(targets_pdbqt_dir, target.replace('pdb', 'pdbqt').replace('.PDB', '.pdbqt'))))

    # creating result dir
    results_dir = os.path.join(root_dir, 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # generating vina config
    for index, row in param_df.iterrows():
        for ligand in os.listdir(ligands_pdbqt_dir):

            print(ligand)
            if not ligand.endswith('.pdbqt'):
                continue
            # creating a dir to store individual target results
            tar_result_dir = os.path.join(results_dir, row['target'])
            if not os.path.exists(tar_result_dir):
                os.makedirs(tar_result_dir)
            # config file dir
            config_dir = os.path.join(results_dir, row['target'], 'config_vina_{0}-{1}.txt'
                .format(row['target'], ligand))

            # creating config file
            with open(config_dir, 'w') as vina_config:
                vina_config.write("receptor = {0}\n".format(os.path.join(targets_pdbqt_dir, row['target'] + '.pdbqt')))
                vina_config.write("ligand = {0}\n".format(os.path.join(ligands_pdbqt_dir, ligand)))
                vina_config.write("\n")
                vina_config.write("out = {0}-{1}_vina.pdbqt\n".format(os.path.join(results_dir, row['target']), ligand))
                vina_config.write("\n")
                vina_config.write("center_x = {0}\n".format(row['x_center']))
                vina_config.write("center_y = {0}\n".format(row['y_center']))
                vina_config.write("center_z = {0}\n".format(row['z_center']))
                vina_config.write("\n")
                vina_config.write("size_x = {0}\n".format(row['x_size']))
                vina_config.write("size_y = {0}\n".format(row['y_size']))
                vina_config.write("size_z = {0}\n".format(row['z_size']))
                vina_config.write("\n")
                vina_config.write("exhaustiveness = {0}\n".format(row['exhaustiveness']))
                vina_config.write("\n")
                vina_config.write("num_modes = {0}\n".format(row['num_modes']))
                vina_config.write("\n")
                vina_config.write("seed = {0}\n".format(row['seed']))

            # running Vina
            vina_command = "{0} --config {1} > {2}_vina_out.txt".format(
                os.path.join('$VINAHOME', 'bin', 'vina'),
                config_dir,
                os.path.join(results_dir, row['target'], ligand))
            os.system(vina_command)

    # extracting results
    # os.system('python ')
