#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: Aretas
"""

### Performs energy minimisation (EMM) on a ligand PDB file using AmberTools16.
### You need to have AmberTools16 or 17 installed for the script to work
### Works with default settings
### Outputs a folder in the PDB input directory with all EMM related files
### $AMBERHOME path must be set for the amber16 directory
### export AMBERHOME=/home/myname/amber16

import os
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-pdb', '--pdb_file',
    help='choose a ligand PDB file', required=True)
parser.add_argument('-imin', '--imin',
    help='min.i setting; default = 1', default = 1)
parser.add_argument('-maxcyc', '--maxcyc',
    help='min.i setting; default = 1000', default = 1000)
parser.add_argument('-ncyc', '--ncyc',
    help='min.i setting; default = 500', default = 500)
parser.add_argument('-ntmin', '--ntmin',
    help='min.i setting; default = 0', default = 0)
parser.add_argument('-ntpr', '--ntpr',
    help='min.i setting; default = 50', default = 50)
parser.add_argument('-igb', '--igb',
    help='min.i setting; default = 0', default = 0)
parser.add_argument('-cut', '--cut',
    help='min.i setting; default = 999', default = 999)
parser.add_argument('-ntb', '--ntb',
    help='min.i setting; default = 0', default = 0)
parser.add_argument('-ntr', '--ntr',
    help='min.i setting; default = 0', default = 0)

args = parser.parse_args()
file_name = str(args.pdb_file)
amberhome = "$AMBERHOME"

m_obj = re.search(r'(.*).pdb', file_name)
if m_obj:
    pdb_id = m_obj.groups()[0]
else:
    print ("A file must be in PDB format!")

pdb_location = os.path.realpath(args.pdb_file)
file_path = pdb_location[:-4]
if not os.path.exists(file_path):
    os.makedirs(file_path)

### 1 prepi
prepi_filename = pdb_id + ".prepin"
command1 = "{2} -i {0} -fi pdb -fo prepi -o {1}".format(
    file_name, os.path.join(file_path, prepi_filename), os.path.join(amberhome, 'bin', 'antechamber'))

os.system(command1)

### 2 parmchk
frcmod_filename = pdb_id + ".frcmod"
command2 = "{2} -i {0} -f prepi -o {1}".format(
    os.path.join(file_path,prepi_filename), os.path.join(file_path,frcmod_filename),
    os.path.join(amberhome, 'bin', 'parmchk'))

os.system(command2)

### 3 tleap
complete_path = os.path.join(file_path,"model_prep")

with open(complete_path, "w") as file1:
    file1.write("source leaprc.gaff\n")
    file1.write("loadamberprep {0}\n".format(os.path.join(file_path, prepi_filename)))
    file1.write("loadamberparams {0}\n".format(os.path.join(file_path, frcmod_filename)))
    file1.write("model = loadpdb NEWPDB.PDB\n")
    file1.write("saveamberparm model {0}.prmtop {0}.inpcrd\n".format(os.path.join(file_path, pdb_id)))
    file1.write("quit\n")

command3 = "{0} -f {1}".format(os.path.join(amberhome, 'bin', 'tleap'), complete_path)

os.system(command3)

### creates min.i file in the ligand directory
file_path2 = re.sub('{0}$'.format(pdb_id), '', file_path)
mini_path = os.path.join(file_path2,"min.i")

with open(mini_path, "w") as file2:

    file2.write("nimization of molecule\n")
    file2.write("&cntrl\n")
    file2.write(" imin={0}, maxcyc={1}, ncyc={2}, ntmin={3},\n".format(
        args.imin, args.maxcyc, args.ncyc, args.ntmin))
    file2.write(" ntpr={0},\n".format(args.ntpr))
    file2.write(" cut={0}., igb={1}, ntb={2},\n".format(args.cut, args.igb, args.ntb))
    file2.write(" ntr={0}\n".format(args.ntr))
    file2.write("&end\n")
    file2.write("~\n")

### 4 minimization
command4 = '''{2} -O -i {1} -o {0}_min.log \
    -p {0}.prmtop -c {0}.inpcrd -ref {0}.inpcrd \
    -r {0}_min.rst'''.format(os.path.join(file_path, pdb_id), mini_path,
        os.path.join(amberhome, 'bin', 'sander'))

os.system(command4)

### 5 conversion to PDB format

complete_path = os.path.join(file_path,"rst2pdb.ptraj")

with open(complete_path, "w") as file3:

    file3.write("parm {0}.prmtop\n".format(os.path.join(file_path, pdb_id)))
    file3.write("trajin {0}_min.rst\n".format(os.path.join(file_path, pdb_id)))
    file3.write("trajout {0}_min.pdb\n".format(os.path.join(file_path, pdb_id)))
    file3.write("go")

command5 = "{0} -i {1}".format(os.path.join(amberhome, 'bin', 'cpptraj'),
    complete_path)

os.system(command5)
