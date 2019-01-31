#!/usr/bin/env python

"""
@author: Aretas
"""

import os
import sys
import subprocess
import argparse

# CLI argument parser
parser = argparse.ArgumentParser(
    description='''
    ''',
    epilog='Example usage in CLI: "python dockit-vina.py"')
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('optional arguments')
# required.add_argument('-i', '--fasta',
#     help='Specify the FASTA file with a peptide sequence(s) for foldability '
#     'prediciton.', required=True)
optional.add_argument('-p', '--python_path',
    help='Specify alternative python path', type=str)
optional.add_argument('-v', '--verbose',
    help='Specify the flag to include verbose messages in console.',
    action='store_false')
args = parser.parse_args()

# setting path to parameter folder
path = os.path.abspath(__file__)
root_dir, file = os.path.split(path)
param_dir = os.path.join(root_dir, 'parameters')
if not os.path.exists(param_dir):
    os.makedirs(param_dir)

# creating ligand and proteins directories
ligands_dir = os.path.join(root_dir, 'ligands', 'PDB')
if not os.path.exists(ligands_dir):
    os.makedirs(ligands_dir)

proteins_dir = os.path.join(root_dir, 'proteins', 'PDB')
if not os.path.exists(proteins_dir):
    os.makedirs(proteins_dir)

# find a list of proteins name and read param file only for them

# reading parameter folders
param_dict = {}
for param_file in os.listdir(param_dir):
    temp_dict = {}
    with open(os.path.join(param_dir, param_file), mode='r') as f:
        for line in f:
            param, value = line.replace(' ', '').split('=')
            if param not in temp_dict:
                temp_dict[param] = value.rstrip('\n')
            else:
                print('Repeating parameter found: {0}. Please check {1} file.'
                    .format(param, param_file))
                sys.exit()

    param_dict[param_file] = temp_dict

if param_dict == {}:
    print("No parameter files found for any of the structures in 'parameters' folder.")
    sys.exit()

print(param_dict)

# checking if there are any ligand and proteins files
if len([protein for protein in os.listdir(proteins_dir) if protein.lower().endswith('.pdb')]) == 0:
    print('Failed to find PDB files in {0} direcotry'.format(proteins_dir))
    sys.exit()

if len([ligand for ligand in os.listdir(proteins_dir) if ligand.lower().endswith('.pdb')]) == 0:
    print('Failed to find PDB files in {0} direcotry'.format(ligands_dir))
    sys.exit()

# performing energy minimisation using Amber
if sys.platform == 'win32':
    print('Energy minimization of molecules in not supported on Windows. Skipping.')
elif os.environ['AMBERHOME']:
    for ligand in os.listdir(ligands_dir):
        if ligand.lower().endswith('_min.pdb'):
            print('{0} seems to be already minimized. Skipping!'.format(ligand))
            continue
        elif not ligand.startswith('.'):
            output = subprocess.check_output('python {0} -pdb {1}'.format(
                os.path.join(root_dir, 'bin', 'emm.py'), os.path.join(ligands_dir, ligand)), shell=True)

            # removing files from the minimization run
            remove_list = ['ATOMTYPE.INF', 'leap.log', 'mdinfo', 'NEWPDB.PDB',
                'PREP.INF', 'min.i']
            for file in remove_list:
                os.remove(file)

            for file in os.listdir(root_dir):
                if file.startswith('ANTECHAMBER'):
                    os.remove(file)

            # remove folder (rework emm.py script paths)

            if args.verbose is True:
                print(output.decode('utf-8'))
        else:
            pass
else:
    print('Please set AMBERHOME path variable to enable energy minimization feature. Skipping.')
