#!/usr/bin/env python

import os
import sys
import argparse
from emm import run_emm

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

# checking if $VINAHOME is set
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

proteins_dir = os.path.join(root_dir, 'targets', 'PDB')
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

if len([ligand for ligand in os.listdir(ligands_dir) if ligand.lower().endswith('.pdb')]) == 0:
    print('Failed to find PDB files in {0} direcotry'.format(ligands_dir))
    sys.exit()

# performing ligand energy minimisation using Ambertools; converting to PDBQT
if sys.platform == 'win32':
    print('Energy minimization of molecules in not supported on Windows. Skipping.')
else:
    for ligand in os.listdir(ligands_dir):
        emm.run_emm(os.path.abspath(ligand))

# converting targets to PDBQT

# generating vina config

# performing docking

# extracting results
