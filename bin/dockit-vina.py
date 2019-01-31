import os
import sys

# setting path to parameter folder
path = os.path.abspath(__file__)
path, file = os.path.split(path)
root_dir, bin_folder = os.path.split(path)
param_dir = os.path.join(root_dir, 'parameters')

# reading parameter folders
param_dict = {}
for param_file in os.listdir(param_dir):
    temp_dict = {}
    with open(os.path.join(param_dir, param_file), mode='r') as f:
        for line in f:
            param, value = line.split('=')
            if param not in temp_dict:
                temp_dict[param] = value.rstrip('\n')
            else:
                print('Repeating parameter found: {0}. Please check {1} file.'
                    .format(param, param_file))
                sys.exit()

    param_dict[param_file] = temp_dict

# creating proteins and ligands folders

# check if there are files in PDB folders if not warn and check PDBQT
# run energy minimization
# preparing ligands
# preparing proteins
# moving to PDBQT folder
# creating vina config file
# running vina
# generating summary of results
