# Dockit

Perform high-throughput molecular docking with multiple targets and ligands using Vina-like engines

## Features
* Molecular docking with multiple target and ligands at the same time
* Flexible residue declaration support for targets
* Use other Vina-like engines e.g. [Qvina2/Qvina-W](https://qvina.github.io) or [Smina](https://github.com/mwojcikowski/smina)
* Optional ligand energy minimization using [obminimize](https://openbabel.org/wiki/Obminimize)
* Output CSV file with all docking results for all modes for easy access to the docking results
* Original PDBQT preparation method, as distributed with MGLTools
* Docker support. Run it anywhere!

## Installation (Docker or Conda)
### Docker
Dockit can be run with [Docker](https://docs.docker.com/get-docker/). You must have Docker & docker-compose installed
```
git clone https://github.com/aretasg/dockit
cd dockit
```

### Conda
Install [conda](https://docs.conda.io/en/latest/miniconda.html) first
```
git clone https://github.com/aretasg/dockit
cd dockit
conda env create -f environment.yml
conda activate dockit
```

## Example usage
1. Determine the search box size and centre positioning using [Chimera](https://www.cgl.ucsf.edu/chimera/download.html) (Structure/Binding Analysis > Vina) or similar
2. Define search box and docking parameters for each target in ```dockit_param.csv```
3. Copy protein and ligand PDB files into ```targets/PDB``` and ```ligands/PDB``` folders, respectively and run:
```
python app/dockit.py
```
or if using Docker
```
docker-compose up
```
* The calculation will take some time depending on the parameters chosen and the number of files. Results can be found in the ```results``` folder
* Visualise the ```results``` with a molecular viewer of your choice by loading ligand .pdbqt file in the ```results``` folder and target PDB or PDBQT file in ```targets``` directory
* CSV file ```dockit_results.csv``` is generated in ```results``` folder with all the docking results
* Run with ```-r``` flag to reset to the pre-run state - PDBQT and result files will be removed

## Argument description in dockit_param.csv
| Argument | Description | Required |
| -----------: | ----------------- | :----------: |
| `target` | file name of the target located in targets/PDB - excluding the extension | :heavy_exclamation_mark: |
| `x_center` | X coordinate of the seach box center | :heavy_exclamation_mark: |
| `y_center` | Y coordinate of the search box center | :heavy_exclamation_mark: |
| `z_center` | Z coordinate of the search box center | :heavy_exclamation_mark: |
| `x_size` | search box size in the X dimension (Angstroms) | :heavy_exclamation_mark: |
| `y_size` | search box size in the Y dimension (Angstroms) | :heavy_exclamation_mark: |
| `z_size` | search box size in the Z dimension (Angstroms) | :heavy_exclamation_mark: |
| `engine` | type of engine to use to run the docking (e.g. vina or qvina2) | :heavy_exclamation_mark: |
| `exhaustiveness` | exhaustiveness of the global search (roughly proportional to time, default=8) | 🤔 |
| `num_modes` | maximum number of binding modes to generate (default=9) | 🤔 |
| `seed` | explicit random seed | 🤔 |
| `cpu` | number of CPUs available to use for docking (default is to auto detect the number of core available) | 🤔 |
| `energy_range` | maximum energy difference between the best binding mode and the worst one displayed (default = 3 kcal/mol) | 🤔 |
| `flex_resi` | specify target residues to be treaded as flexible during docking | 🤔 |

## FAQ and limitations
* Dockit will dock every target against every ligand in ```targets/PDB``` and ```ligands/PDB```, respectively.
* Edit ```dockit_param.csv``` to change any parameters to be run with the docking engine, including search box parameters
* Run with ```-m``` flag perform energy minimization using obminimize with default settings
* Supports declaration of flexible residues for targets. Please look at ```dockit_param.csv``` for an example for how to declare flexible residues
* Supports other Vina-like engines e.g. Qvina2. Please specify the engine name or path to it in the ```engine``` column of ```dockit_param.csv```. Dockit comes installed with ```vina```, ```qvina2```, ```vinaw``` and ```smina```. You should be able to use any other engine that uses the same CLI as Vina
* The necessity of selecting the charges (Kollman/Gasteirger) is obsolete with Vina due to the scoring system being based on hydrophobic and hydrogen bond interactions compared to its predecessor AutoDock 4. Nevertheless, the default charge for targets and ligands are set as Kollman and Gasteirger, respectively
* Specify custom scoring system weights in the ```weight_*``` fields of ```dockit_param.csv```. More about the scoring system [here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3041641/#!po=22.7273)

## Authors
**Aretas Gaspariunas**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### Acknowledgments & Disclaimer
prepare_ligand4.py, prepare_receptor4.py and repare_flexreceptor4.py are distributed as part of MGLTools 1.5.6 and all the ownership together with AutoDock Vina is credited to their respective authors (Morris et al., 2009)
