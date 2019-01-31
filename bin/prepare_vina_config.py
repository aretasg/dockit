#!/usr/bin/env python

"""
@author: Aretas
"""

# creates a config files(s) for vina runs; accepts enzyme PDBQT as input
# accepts and xyz coordinate and xyz box size as arguments
# lo1 flag is for specifting folder directory with the ligand PDBQT library
# Please use with protein library as PWD for config file to be dumped accordingly

import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file',
    help='choose the PDBQT protein file', required=True)
parser.add_argument('-xc', '--x_center',
    help='choose x center coordinate', default=45)
parser.add_argument('-yc', '--y_center',
    help='choose the y center coordinate:', default=50)
parser.add_argument('-zc', '--z_center',
    help='choose the z center coordinate:', default=50)
parser.add_argument('-xs', '--x_size',
    help='choose the x size', default=20)
parser.add_argument('-ys', '--y_size',
    help='choose the y size', default=20)
parser.add_argument('-zs', '--z_size',
    help='choose the z size', default=16)
parser.add_argument('-lo', '--location',
    help='choose the directory to save the file to', required=True)
parser.add_argument('-lo1', '--location1',
    help='choose the directory of the ligand PDBQT files', default="ligands/PDBQT")

parser.add_argument('-m', '--num_modes',
    help='choose num_modes', default=15)
parser.add_argument('-e', '--exhaustiveness',
    help='choose exhaustiveness', default=15)
parser.add_argument('-s', '--seed',
    help='choose seed value', default=41436)

args = parser.parse_args()

x_center = float(args.x_center)
y_center = float(args.y_center)
z_center = float(args.z_center)
x_size = float(args.x_size)
y_size = float(args.y_size)
z_size = float(args.z_size)
location = args.location    # MD results folder
location1 = args.location1  # Ligand library location

pdbqt_location = os.path.realpath(args.file)
MD_folder = os.path.realpath(args.location)
ligand_location = os.path.realpath(args.location1)

m_obj = re.search(r'(.*).pdbqt', args.file)
if m_obj:
    protein_name = m_obj.groups()[0]

# print (pdbqt_location, MD_folder, ligand_location)
file_path = os.path.join(MD_folder, protein_name)

if not os.path.exists(file_path):
    os.makedirs(file_path)

for filename in os.listdir(ligand_location):
    ligand_name_search = re.search(r'(.*).pdbqt',filename)
    if ligand_name_search:
        ligand_name = ligand_name_search.groups()[0]

        completeName = os.path.join(file_path,"config_vina_{0}-{1}.txt"
            .format(protein_name, ligand_name))
        with open(completeName, "w") as file2:
            file2.write("receptor = {0}\n".format(pdbqt_location))
            file2.write("ligand = {0}.pdbqt\n".format(os.path.join(ligand_location, ligand_name)))
            file2.write("\n")
            file2.write("out = {0}-{1}_vina.pdbqt\n".format(os.path.join(file_path, protein_name), ligand_name))
            file2.write("\n")
            file2.write("center_x = {0}\n".format(x_center))
            file2.write("center_y = {0}\n".format(y_center))
            file2.write("center_z = {0}\n".format(z_center))
            file2.write("\n")
            file2.write("size_x = {0}\n".format(x_size))
            file2.write("size_y = {0}\n".format(y_size))
            file2.write("size_z = {0}\n".format(z_size))
            file2.write("\n")
            file2.write("exhaustiveness = {0}\n".format(args.exhaustiveness))
            file2.write("\n")
            file2.write("num_modes = {0}\n".format(args.num_modes))
            file2.write("\n")
            file2.write("seed = {0}\n".format(args.seed))

print('Done writting Vina configuration file!')
