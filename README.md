# Dockit

Python CLI tool to perform high-throughput molecular docking using AutoDock Vina

## Features
* Molecular docking using multiple target and ligands
* Use other Vina-like engines like [Qvina2](https://qvina.github.io) or [Smina](https://github.com/mwojcikowski/smina)
* Flexible residue declaration support for targets
* Energy minimization using [obminimize](https://openbabel.org/wiki/Obminimize) to generate more realistic ligand conformations
* Docker support. Run it anywhere!
* Generates a csv file with all docking results for all modes for easy access to the docking results
* Uses original PDBQT preparation method, as found in MGLTools, to take advantage of the calibration with Vina scoring system

## Installation (Docker or Conda)
### Docker
Dockit can be run with [Docker](https://docs.docker.com/get-docker/). You must have Docker & docker-compose installed
```
git clone https://github.com/aretasg/dockit
cd dockit
```

### Conda
You must install [conda](https://docs.conda.io/en/latest/miniconda.html) first to set up the environment
```
git clone https://github.com/aretasg/dockit
cd dockit
conda env create -f environment.yml
conda activate dockit
python app/dockit.py
```
The last command will create ligands/PDB and targets/PDB directories, alternatively, they can be created manually

### Example usage
1. Determine the search box size and centre positioning using [Chimera](https://www.cgl.ucsf.edu/chimera/download.html) (Structure/Binding Analysis > Vina) or similar
2. Define search box and docking parameters for each target in ```dockit_param.csv```
3. Copy protein and ligand PDB files into targets/PDB and ligands/PDB folders, respectively and run:
```
python app/dockit.py
```
or if using with docker
```
docker-compose up
```
* The calculation will take some time depending on the parameters chosen and the number of files. Results can be found in the results folder
* Visualise the ```results``` with a molecular viewer of your choice by loading ligand .pdbqt file in the ```results``` folder and target PDB or PDBQT file in ```targets``` directory
* csv file ```dockit_results.csv``` is generated in ```results``` folder with all docking results
* Run with ```-r``` flag to reset to the pre-run state - PDBQT and result files will be removed

## Argument description in dockit_param.csv
target,x_center,y_center,z_center,x_size,y_size,z_size,exhaustiveness,num_modes,seed,cpu,energy_range,flex_resi,engine
| Argument | Description | Required |
| -----------: | ----------------- | :----------: |
| `target` | file name of the target located in targets/PDB - excluding the extension | :heavy_exclamation_mark: |
| `x_center` | X coordinate of the seach box center | :heavy_exclamation_mark: |
| `y_center` | Y coordinate of the search box center | :heavy_exclamation_mark: |
| `z_center` | Z coordinate of the search box center | :heavy_exclamation_mark: |
| `x_size` | search box size in the X dimension (Angstroms) | :heavy_exclamation_mark: |
| `y_size` | search box size in the Y dimension (Angstroms) | :heavy_exclamation_mark: |
| `z_size` | search box size in the Z dimension (Angstroms) | :heavy_exclamation_mark: |
| `engine` | type of engine to use to run the docking (vina or qvina2) | :heavy_exclamation_mark: |
| `exhaustiveness` | exhaustiveness of the global search (roughly proportional to time, default=8) | 🤔 |
| `num_modes` | maximum number of binding modes to generate (default=9) | 🤔 |
| `seed` | explicit random seed | 🤔 |
| `cpu` | number of CPUs available to use for docking (default is to auto detect the number of core available) | 🤔 |
| `energy_range` | maximum energy difference between the best binding mode and the worst one displayed (default = 3 kcal/mol) | 🤔 |
| `flex_resi` | specify target residues to be treaded as flexible during docking | 🤔 |

## FAQ and limitations
* Edit ```dockit_param.csv``` to change any parameters to be run with the docking engine, including search box parameters
* Supports declaration of flexible residues for targets. Please look at ```dockit_param.csv``` for an example for how to declare flexible residues
* Supports other Vina-like engines e.g. Qvina2. Please specify the engine name or path to it in the engine column of ```dockit_param.csv```
* The necessity of selecting the charges (Kollman/Gasteirger) is obsolete with Vina due to the scoring system being based on hydrophobic and hydrogen bond interactions compared to its predecessor AutoDock 4. Nevertheless, the default charge for targets and ligands are set as Gasteirger for both

## Authors
**Aretas Gaspariunas**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### Acknowledgments & Disclaimer
prepare_ligand4.py, prepare_receptor4.py, and prepare_flexreceptor4.py are distributed as part of MGLTools 1.5.6 and all the ownership together with AutoDock Vina is credited to their respective authors (Morris et al., 2009)
