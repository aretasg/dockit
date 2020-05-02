#!/usr/bin/env python

import logging
import os
import shutil
import sys
import argparse
import subprocess
import csv

from get_results import get_results


class AppLogger:

    @classmethod
    def get(cls, name, log_file, file_level=logging.INFO,
        stream_level=logging.WARNING):

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s : %(levelname)s : %(name)s : %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(stream_level)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        return logger


def pdb_parser(pdb_file):

    with open(os.path.abspath(pdb_file), 'r') as input_file:
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


def parse_param_csv(param_dir):

    with open(param_dir, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        param_dict = {}
        for row in csv_reader:
            if line_count == 0:
                header = row
                line_count += 1
            else:
                param_dict[line_count] = {header[i]: row[i] for i in range(len(header))}
                line_count += 1

    for key, value in param_dict.items():
        if key in ('target', 'x_center', 'y_center', 'z_center', 'size_x', 'size_y', 'size_z') and value == '':
            raise ValueError('Missing one or more arguments in dockit_param.csv')

    return param_dict


def vina_config(config_dir, targets_pdbqt_dir, ligands_pdbqt_dir, results_dir, ligand, row, engine, flex_resi=None):

    with open(config_dir, 'w') as vina_config:
        vina_config.write("receptor = {0}\n".format(os.path.join(targets_pdbqt_dir, row['target'] + '.pdbqt')))
        if flex_resi:
            vina_config.write("flex = {0}\n".format(flex_resi))
        vina_config.write("ligand = {0}\n".format(os.path.join(ligands_pdbqt_dir, ligand)))
        vina_config.write("out = {0}-{1}.pdbqt\n".format(
            os.path.join(results_dir, 'res_{0}_'.format(engine) + row['target']),
            ligand)
        )
        vina_config.write("center_x = {0}\n".format(row['x_center']))
        vina_config.write("center_y = {0}\n".format(row['y_center']))
        vina_config.write("center_z = {0}\n".format(row['z_center']))
        vina_config.write("size_x = {0}\n".format(row['x_size']))
        vina_config.write("size_y = {0}\n".format(row['y_size']))
        vina_config.write("size_z = {0}\n".format(row['z_size']))
        if row['exhaustiveness'] != '':
            vina_config.write("exhaustiveness = {0}\n".format(row['exhaustiveness']))
        if row['num_modes'] != '':
            vina_config.write("num_modes = {0}\n".format(row['num_modes']))
        if row['seed'] != '':
            vina_config.write("seed = {0}\n".format(row['seed']))
        if row['energy_range'] != '':
            vina_config.write("energy_range = {0}\n".format(row['energy_range']))
        if row['cpu'] != '':
            vina_config.write("cpu = {0}\n".format(row['cpu']))
        if row['weight_hydrogen'] != '':
            vina_config.write("weight_hydrogen = {0}\n".format(row['weight_hydrogen']))
        if row['weight_gauss1'] != '':
            vina_config.write("weight_gauss1 = {0}\n".format(row['weight_gauss1']))
        if row['weight_gauss2'] != '':
            vina_config.write("weight_gauss2 = {0}\n".format(row['weight_gauss2']))
        if row['weight_repulsion'] != '':
            vina_config.write("weight_repulsion = {0}\n".format(row['weight_repulsion']))
        if row['weight_hydrophobic'] != '':
            vina_config.write("weight_hydrophobic = {0}\n".format(row['weight_hydrophobic']))
        if row['weight_rot'] != '':
            vina_config.write("weight_rot = {0}\n".format(row['weight_rot']))


def reset_(path):

    try:
        shutil.rmtree(os.path.join(path, 'targets', 'PDBQT'))
        shutil.rmtree(os.path.join(path, 'ligands', 'PDBQT'))
        shutil.rmtree(os.path.join(path, 'results'))
    except OSError as e:
        raise e


def dockit(verbose, reset, minimization):

    path = os.path.dirname(os.path.realpath(__file__))
    logger = AppLogger.get(__name__, os.path.join(path, 'dockit.logs'),
        stream_level=logging.INFO)

    app_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir, app = os.path.split(app_dir)

    if verbose:
        stdout = None
        logger.info('Verbose=True. Set to False to silence console messages')
    else:
        stdout = open(os.devnull, 'w')

    if reset:
        logger.info('Resetting to pre-run state')
        reset_(root_dir)
        sys.exit()

    logger.info('Creating ligands and targets directories')
    ligands_dir = os.path.join(root_dir, 'ligands', 'PDB')
    if not os.path.exists(ligands_dir):
        os.makedirs(ligands_dir)

    targets_dir = os.path.join(root_dir, 'targets', 'PDB')
    if not os.path.exists(targets_dir):
        os.makedirs(targets_dir)

    logger.info('Checking for files in targets and ligands folders')
    if len([protein for protein in os.listdir(targets_dir) if protein.lower().endswith('.pdb')]) == 0:
        logger.error('Failed to find PDB files in {0} directory'.format(targets_dir))
        sys.exit()

    if len([ligand for ligand in os.listdir(ligands_dir) if ligand.lower().endswith('.pdb')]) == 0:
        logger.error('Failed to find PDB files in {0} directory'.format(ligands_dir))
        sys.exit()

    logger.info('Checking input file formats')
    for protein in os.listdir(targets_dir):
        if protein.lower().endswith('.pdb') and not pdb_parser(os.path.join(targets_dir, protein)):
            logger.error('File {0} not in PDB format'.format(protein))
            sys.exit()
    for ligand in os.listdir(ligands_dir):
        if ligand.lower().endswith('.pdb') and not pdb_parser(os.path.join(ligands_dir,ligand)):
            logger.error('File not in PDB format {0}'.format(ligand))
            sys.exit()

    os.chdir(ligands_dir)
    if minimization is True:
        logger.info('Minimizing ligands with obminimize')
        try:
            for ligand in os.listdir(ligands_dir):
                subprocess.Popen('obminimize -o pdb {0} > min_{0}'.format(ligand),
                    shell=True, stdout=stdout).wait()
                os.remove(ligand)
                os.rename('min_'+ligand, ligand)
        except Exception as e:
            logger.error('Failed to minimize ligands')
    else:
        pass

    logger.debug('Creating ligand PDBQT dir')
    ligands_pdbqt_dir = os.path.join(root_dir, 'ligands', 'PDBQT')
    if not os.path.exists(ligands_pdbqt_dir):
        os.makedirs(ligands_pdbqt_dir)

    logger.info('Converting ligands to PDBQT')
    for ligand in os.listdir(ligands_dir):
        if not ligand.lower().endswith('.pdb'):
            continue
        subprocess.Popen('{0} -l {1} -o {2} -A hydrogens -U nphs -v'.format(
            os.path.join(app_dir, 'prepare_ligand4.py'),
            ligand,
            os.path.join(ligands_pdbqt_dir, ligand.replace('pdb', 'pdbqt').replace('.PDB', '.pdbqt'))
            ), shell=True, stdout=stdout).wait()

    logger.debug('Creating target PDBQT dir')
    targets_pdbqt_dir = os.path.join(root_dir, 'targets', 'PDBQT')
    if not os.path.exists(targets_pdbqt_dir):
        os.makedirs(targets_pdbqt_dir)

    logger.info('Converting targets to PDBQT')
    os.chdir(targets_dir)
    for target in os.listdir(targets_dir):
        if not target.lower().endswith('.pdb'):
            continue
        subprocess.Popen('{0} -r {1} -o {2} -A checkhydrogens -U nphs -v'.format(
            os.path.join(app_dir, 'prepare_receptor4.py'),
            target,
            os.path.join(targets_pdbqt_dir, target.replace('pdb', 'pdbqt').replace('.PDB', '.pdbqt'))
            ), shell=True, stdout=stdout).wait()

    logger.debug('Creating results folder')
    results_dir = os.path.join(root_dir, 'results')
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    logger.debug('Reading dockit_param.csv')
    param_dir = os.path.join(root_dir, 'dockit_param.csv')
    param_dict = parse_param_csv(param_dir)

    logger.debug('Checking if listed targets in param exist')
    for index, row in param_dict.items():
        if row['target'] not in [i.rstrip('.pdbqt') for i in os.listdir(targets_pdbqt_dir)]:
            raise ValueError('{} does not exist'.format(row['target']))

    logger.info('Creating docking config files and initiating docking')
    for index, row in param_dict.items():
        for ligand in os.listdir(ligands_pdbqt_dir):

            if not ligand.endswith('.pdbqt'):
                continue
            ligand_name = ligand.rstrip('.pdbqt')

            # creating a dir to store individual target results
            tar_result_dir = os.path.join(results_dir, row['target'], ligand_name)
            if not os.path.exists(tar_result_dir):
                os.makedirs(tar_result_dir)

            flex_resi = None
            if row['flex_resi'] not in ('0', '', 'None', ' '):
                logger.info('Creating flexible residue PDBQT')
                try:
                    subprocess.Popen('{0} -r {1} -s {2} -g {3} -x {4} -v'.format(
                        os.path.join(app_dir, 'prepare_flexreceptor4.py'),
                        os.path.join(targets_pdbqt_dir, row['target'] + '.pdbqt'),
                        row['flex_resi'],
                        os.path.join(targets_pdbqt_dir, row['target'] + '.pdbqt'),
                        os.path.join(targets_pdbqt_dir, row['target'] + row['flex_resi'] + '.pdbqt')
                        ), shell=True, stdout=stdout).wait()
                    flex_resi = os.path.join(targets_pdbqt_dir, row['target'] + row['flex_resi'] + '.pdbqt')
                except Exception as e:
                    logger.warning('Failed to assign flexible residues. Skipping')
                    flex_resi = None
                if not os.path.isfile(flex_resi):
                    logger.warning('Failed to assign flexible residues. Skipping')
                    flex_resi = None

            engine = os.path.split(row['engine'])[-1]
            config_dir = os.path.join(tar_result_dir, '{0}_config_{1}-{2}.txt'
                .format(engine, row['target'], ligand_name))

            logger.debug('Creating config file')
            vina_config(config_dir, targets_pdbqt_dir, ligands_pdbqt_dir,
                tar_result_dir, ligand, row, engine, flex_resi=flex_resi)

            logger.info('Docking {0} to {1} using {2}'.format(ligand_name, row['target'], row['engine']))
            vina_command = "{0} --config {1} > {2}.txt".format(
                row['engine'],
                config_dir,
                os.path.join(tar_result_dir, engine + "_out_" + row['target'] + '-' + ligand.rstrip('.pdbqt'))
                )

            subprocess.Popen(vina_command, shell=True, stdout=stdout).wait()

    logger.info('Parsing results and writting to csv')
    get_results()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='''
        AutoDock Vina wrapper for performing high-throughput molecular docking
        with multiple targets and flexible residue support
        ''',
        epilog='Usage in CLI: "python dockit.py"')
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('-v', '--verbose',
        help='Specify the flag to include verbose messages',
        action='store_true')
    optional.add_argument('-m', '--minimize',
        help='Energy minimize ligands using obminimize with default settings',
        action='store_true')
    optional.add_argument('-r', '--reset',
        help='Restores input files to pre-run state preserving only input PDB files',
        action='store_true')
    args = parser.parse_args()

    dockit(args.verbose, args.reset, args.minimize)
