# Dockit-Vina

A Python/bash wrapped CLI tool to perform high-throughput molecular docking using AutoDock Vina.

## Getting Started

### Dependecies & Installation

* Have MGLTools 1.5.6 installed. If you are using Linux or Windows machine please replace pyhtonsh in the bin folder with the one in the MGLTools bin bolder. macOS users with default directory used for MGLTools installation can keep the original pythonsh;
* To enable energy minimization feature please have AmberTools installed (http://ambermd.org/GetAmber.php) and AMBERHOME set (optional);
* If you are using Linux or Windows please download and compile vina (http://vina.scripps.edu/download.html) and replace it with the copy in the bin folder.
* Have pandas installed (if you don't this should be installed when running the dockit_vina.sh script if you have pip).

### Example usage:

* Determine the search box size and centre positioning using Chimera or AutoDock Tools;
* Copy the protein PDB and ligand PDB inside proteins/PDB and ligands/PDB folders, respectively. You can create the folders manually or by running the dockit_vina.sh script;
* While in the same directory as dockit_vina.sh file execute a command with search box parameters as arguments:
```
bash dockit_vina.sh -xc 9 -yc -5 -zc 18 -xs 14 -ys 20 -zs 25
```
* The calculation will take some time depending on the parameters chosen and the number of files; you can find your results in the results folder and view the progress in percentage by opening vina_out file.
* To visualise the results just load the protein and the ligand .pdbqt file in the results folder with a molecular viewer of your choice.
* A csv file with docking results is generated in results folder for each enzyme used in the docking.

### FAQ and limitations

* energy minimisation of the ligand before docking for more accurate representation of the bond lengths and angles using AmberTools is integrated in dockit_vina.sh but you will need AmberTools and $AMBERHOME set for it to work;
* to modify seed, exhaustiveness and num_mode parameters to be run with Vina edit the default values in bin/prepare_vina_config.py;
* As of now Dockit-Vina does not support flexible residues and target proteins are treated as rigid structures. However, it can be done by placing flexible residues in PDBQT file and appending dock.py command in dockit_vina.sh with --flex argument;
* The necessity of selecting the right charges (Kollman/Gasteirger) is absolete when using Vina due to it's scoring system being based hydrophobic and hydrogen bond interactions in contrast to its predecessor AutoDock 4. Nevertheless, if you wish to use AutoDock 4 instead of Vina the default charge for enzymes and ligands are set as Kollman and Gasteirger, respectively.

## Authors
* **Aretas Gaspariunas**

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Acknowledgments & Disclaimer
prepare_ligand4.py, prepare_receptor4.py, and pythonsh are distributed as part of MGLTools 1.5.6 and all the ownership together with AutoDock Vina is credited to their respective authors (Morris et al., 2009).
