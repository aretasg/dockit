# Dockit

Python CLI tool to perform high-throughput molecular docking using AutoDock Vina

## Features
* Molecular docking using multiple target and ligands
* Use other Vina-like engines
* Flexible residue declaration for targets
* Energy minimization using obminimize to generate more realistic ligand conformations
* Generates a csv file will all docking results for all modes for easy access to data
* Uses original PDBQT preparation method to take advantage of calibration with the Vina scoring system

## Dependencies & Installation
You must install [conda](https://docs.conda.io/en/latest/miniconda.html) first to set up the environment
```
git clone https://github.com/aretasg/dockit
cd dockit
conda env create --file=environment.yml
conda activate dockit
cd app
python dockit.py
```

### Example usage
1. Determine the search box size and centre positioning using Chimera (Structure/Binding Analysis > Vina) or similar
2. Copy the protein and ligand PDB files inside proteins/PDB and ligands/PDB folders, respectively
3. Define search box and docking parameters for each target in  ```dockit_param.csv``` and run:
```
python dockit.py
```
* The calculation will take some time depending on the parameters chosen and the number of files. Results can be found in the results folder
* Visualise the results with a molecular viewer of your choice by loading ligand .pdbqt file in the results folder and target PDB or PDBQT file in targets directory
* csv file ```dockit_results.csv``` is generated in results folder with all docking results
* Run with ```-r``` flag to reset to the pre-run state - PDBQT and result files will be removed

## FAQ and limitations
* Edit ```dockit_param.csv``` to change any parameters to be run with the docking engine, including search box parameters
* Supports declaration of flexible residues for targets. Please look at ```dockit_param.csv``` for an example for how to declare flexible residues
* Copy ```prepare_flexreceptor4.py``` from autodocktools-prepare location to conda ```dockit``` environment folder to enable flexible residue selection
* Supports other Vina-like engines e.g. qvina. Please specify the engine name or path to it in the engine column of ```dockit_param.csv```
* The necessity of selecting the charges (Kollman/Gasteirger) is obsolete with Vina due to the scoring system being based hydrophobic and hydrogen bond interactions in contrast to its predecessor AutoDock 4. Nevertheless, if you wish to use AutoDock 4 instead of Vina the default charge for enzymes and ligands are set as Kollman and Gasteirger, respectively

## Authors
**Aretas Gaspariunas**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### Acknowledgments & Disclaimer
prepare_ligand4.py, prepare_receptor4.py, and prepare_flexreceptor4.py are distributed as part of MGLTools 1.5.6 and all the ownership together with AutoDock Vina is credited to their respective authors (Morris et al., 2009)
