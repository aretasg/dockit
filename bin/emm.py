#!/usr/bin/env python

import argparse
import os
import sys

def run_emm(pdb_path, imin=1, maxcyc=1000, ncyc=500, ntpr=50, cut=999, igb=0, ntb=0):

    amberhome = '$AMBERHOME'
    path = os.path.abspath(__file__)
    input_path, filename = os.path.split(os.path.abspath(pdb_path))
    pdb_id = filename.rstrip('.pdb').rstrip('.PDB')

    # creating directory to store results
    result_dir = os.path.join(input_path, pdb_id)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    # running prepi
    prepi_filename = pdb_id + '.prepin'
    prepi_command = '{0} -i {1} -fi pdb -fo prepi -o {2}'.format(
        os.path.join(amberhome, 'bin', 'antechamber'),
        os.path.abspath(pdb_path),
        os.path.join(result_dir, prepi_filename))

    os.system(prepi_command)
    # sys.exit()

    # running parmchk
    frcmod_filename = pdb_id + '.frcmod'
    frcmod_command = '{0} -i {1} -f prepi -o {2}'.format(
        os.path.join(amberhome, 'bin', 'parmchk2'),
        os.path.join(result_dir, prepi_filename),
        os.path.join(result_dir, frcmod_filename))

    os.system(frcmod_command)

    # running tleap
    model_prep_path = os.path.join(result_dir,"model_prep")

    with open(model_prep_path, 'w') as model_prep_file:
        model_prep_file.write(
            'source leaprc.gaff\nloadamberprep {0}\nloadamberparams {1}\nmodel = '
            'loadpdb NEWPDB.PDB\nsaveamberparm model {2}.prmtop {2}.inpcrd\nquit\n'
            .format(os.path.join(result_dir, prepi_filename),
                os.path.join(result_dir, frcmod_filename),
                os.path.join(result_dir, pdb_id)))

    tleap_command = '{0} -f {1}'.format(os.path.join(amberhome, 'bin', 'tleap'),
        model_prep_path)

    os.system(tleap_command)

    # creates min.i file in the input directory
    mini_path = os.path.join(result_dir, 'min.i')

    with open(mini_path, "w") as mini_file:
        mini_file.write('nimization of molecule\n&cntrl\n imin={0}, maxcyc={1}, '
            'ncyc={2},\n ntpr={3},\n cut={4}., igb={5}, ntb={6},\n&end\n~\n'
            .format(imin, maxcyc, ncyc, ntpr, cut, igb, ntb))

    # minimization
    mini_command = ('{0} -O -i {1} -o {2}_min.log -p {2}.prmtop -c {2}.inpcrd -ref '
        '{2}.inpcrd -r {2}_min.rst'.format(os.path.join(amberhome, 'bin', 'sander'),
            mini_path, os.path.join(result_dir, pdb_id)))

    os.system(mini_command)

    # conversion to PDB format
    ptraj_path = os.path.join(result_dir, 'rst2pdb.ptraj')

    with open(ptraj_path, "w") as ptraj_file:
        ptraj_file.write('parm {0}.prmtop\ntrajin {0}_min.rst\ntrajout {0}_min.pdb\ngo'
            .format(os.path.join(result_dir, pdb_id)))

    ptraj_command = '{0} -i {1}'.format(os.path.join(amberhome, 'bin', 'cpptraj'),
        ptraj_path)

    os.system(ptraj_command)

    # removing files run files
    for filename in os.listdir(result_dir):
        if not filename.lower().endswith('.pdb'):
            os.remove(os.path.join(result_dir, filename))

    ext = ['.PDB', '.INF', '.log']
    for filename in os.listdir(os.getcwd()):
        if filename.startswith('ANTE') or filename.endswith(tuple(ext)) or filename == 'mdinfo':
            os.remove(os.path.join(os.getcwd(), filename))

    # replacing input pdb file with minimized version
    os.rename(os.path.join(result_dir, pdb_id + '_min.pdb'),
        os.path.join(input_path, pdb_id + '_min.pdb'))
    # os.remove(os.path.abspath(pdb_path))
    os.rmdir(result_dir)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
            description='''
        Performs energy minimization on a small ligand PDB file using AmberTools.\n
        * AmberTools must be installed for the script to work (intended to be used with Ambertools 18);\n
        * Works with default settings;\n
        * Replaces input file with minimized version. If you want to keep original make a copy.\n
        * $AMBERHOME path must be set for the amber directory e.g.
            'export AMBERHOME=/home/myname/amber18'
    ''',epilog='Example usage: "emm.py -pdb foo.pdb"')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    required.add_argument('-pdb', '--pdb_file',
        help='choose a ligand PDB file for energy minimization', required=True)
    optional.add_argument('-imin', '--imin',
        help='Specify to turn on/off minimization; default = 1 (on)', default = 1)
    optional.add_argument('-maxcyc', '--maxcyc',
        help='Specify the number of steps; default = 1000', default = 1000)
    optional.add_argument('-ncyc', '--ncyc',
        help='''if ncyc < maxcyc Sander uses steepest desent algorithm. Otherwise
            conjugate gradient method is used; default = 500''', default = 500)
    optional.add_argument('-ntpr', '--ntpr',
        help='Specify for how many steps trajectory files are written; default = 50', default = 50)
    optional.add_argument('-igb', '--igb',
        help='Specify dielectric model; default = 0 (constant dielectric model)', default = 0)
    optional.add_argument('-cut', '--cut',
        help='Specify non-bonded cut-off. A larger cut-off introduces less error; default = 999', default = 999)
    optional.add_argument('-ntb', '--ntb',
        help='Specify if system is periodic 1 and 0, yes and no, respectively; default = 0', default = 0)

    args = parser.parse_args()

    # checking if environment variable is set for Ambertools
    if not 'AMBERHOME' in os.environ:
        print('$AMBERHOME environment variable is not set. Please refer to the help section.')
        sys.exit()

    # checking if input is pdb
    if not '.pdb' in args.pdb_file.lower():
        print("Input file must be a PDB file with '.pdb' extension.")
        sys.exit()

    # checking if the file is not empty
    if os.stat(os.path.abspath(args.pdb_file)).st_size == 0:
        print('Input file is empty.')
        sys.exit()

    # checking if the file is in PDB format
    with open(os.path.abspath(args.pdb_file)) as input_file:
        atom_count = 0
        for line in input_file:
            if 'ATOM' in line or 'HETATM' in line:
                atom_count += 1
                break
        if atom_count == 0:
            print('Input file does not seem to be in PDB format.')
            sys.exit()

    run_emm(args.pdb_file, args.imin, args.maxcyc, args.ncyc, args.ntpr,
        args.cut, args.igb, args.ntb)
