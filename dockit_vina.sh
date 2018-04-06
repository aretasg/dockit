#!/usr/bin/env bash

# help and usage information
while test $# -gt 0; do
        case "$1" in
                -h|--help)
                        echo " "
                        echo "Dockit-Vina"
                        echo "Description: Dockit-Vina is a an AutoDock Vina bash/Python wrapper
for faster docking procedure and more user-friendly experience (github.com/aretas2/dockit-vina).
* Have MGLTools 1.5.6 installed. If you are using Linux or Windows machine
please replace pyhtonsh in bin folder with the one in MGLTools bin bolder.
macOS users with default directory used for MGLTools installation can move to the
next step.
* Have either Python 2.7 or 3.6.
* To use Dockit-Vina you will need to place your protein(s) molecule
inside enzymes/PDB directory and ligand(s) molecules in ligands/PDB
directory;
* specify the search window parameters on command line;
* Docking results can be found in the results directory."
                        echo " "
                        echo "options:"
                        echo "-h, --help                show brief help"
                        echo "-xc x center position of the search box; default=45."
                        echo "-yc y center position of the search box; default=50."
                        echo "-zc z center position of the search box; default=50."
                        echo "-xs x size of the search box; default=20."
                        echo "-ys y size of the search box; default=20."
                        echo "-zs z size of the search box; default=16."
                        exit 0
                        ;;
                -xc)
                        shift
                        if test $# -gt 0; then
                                export XC=${1:-45}
                        else
                                echo "no x center coordinate specified"
                                exit 1
                        fi
                        shift
                        ;;
                -yc)
                        shift
                        if test $# -gt 0; then
                                export YC=${1:-50}
                        else
                                echo "no y center coordinate specified"
                                exit 1
                        fi
                        shift
                        ;;
                -zc)
                        shift
                        if test $# -gt 0; then
                                export ZC=${1:-50}
                        else
                                echo "no z center coordinate specified"
                                exit 1
                        fi
                        shift
                        ;;
                -xs)
                        shift
                        if test $# -gt 0; then
                                export XS=${1:-20}
                        else
                                echo "no x dimension specified for the search window"
                                exit 1
                        fi
                        shift
                        ;;
                -ys)
                        shift
                        if test $# -gt 0; then
                                export YS=${1:-20}
                        else
                                echo "no y dimension specified for the search window"
                                exit 1
                        fi
                        shift
                        ;;
                -zs)
                        shift
                        if test $# -gt 0; then
                                export ZS=${1:-16}
                        else
                                echo "no z dimension specified for the search window"
                                exit 1
                        fi
                        shift
                        ;;

                *)
                        echo "$1 is not a recognized flag!"
                        break
                        exit 1
                        ;;
        esac
done

if [ -z "$XC" ]; then
    echo "XC argument missing"
    exit 1
fi
if [ -z "$YC" ]; then
    echo "YC argument missing"
    exit 1
fi
if [ -z "$ZC" ]; then
    echo "ZC argument missing"
    exit 1
fi
if [ -z "$XS" ]; then
    echo "XS argument missing"
    exit 1
fi
if [ -z "$YS" ]; then
    echo "YS argument missing"
    exit 1
fi
if [ -z "$ZS" ]; then
    echo "ZS argument missing"
    exit 1
fi

# # input for search window size and positioning
# XC=${1:-45} # X CENTER
# YC=${2:-50} # Y CENTER
# ZC=${3:-50} # Z CENTER
# XS=${4:-20} # X SIZE
# YS=${5:-20} # Y SIZE
# ZS=${6:-16} # Z SIZE
# # python version to be used for scripts
# PYTHON=${7:-python}

# performing energy minimisation
mkdir -p ligands/PDB
cd ligands/PDB
if [ -d "$AMBERHOME" ]; then
    echo "Performing energy minimisation using Amber!"
    for f in *.pdb; do
        if [[ ${f: -8} == "_min.pdb" ]]; then
            echo "The ligand $f seems to be already minimized. Skipping!"
        else
            python ../../bin/emm.py -pdb $f
            rm -r ANTECHAMBER*
            rm -r ATOMTYPE.INF
            rm -r leap.log
            rm -r mdinfo
            rm -r NEWPDB.PDB
            rm -r PREP.INF
            id=$(echo "$f" | awk -F'[.]' '{print $1}')
            mv ./$id/$id"_min.pdb" .
            rm -rf $id
            rm -r $f
        fi
    done
else
    echo "Failed to detect Amber directory. Please set AMBERHOME dir if you want ligand(s) to be energy minimized e.g. source /Users/username/amber17/amber.sh"
fi

# preparing ligands
cd .. # back to ligands dir
for f in ./PDB/*.pdb; do
    ../bin/pythonsh ../bin/prepare_ligand4.py -l $f -A hydrogens -U nphs -v
done

# moving pdbqt to a folder
mkdir -p ./PDBQT
for f in ./*.pdbqt; do
    mv $f ./PDBQT
done

# preparing enzymes
mkdir -p ../enzymes/PDBQT
cd ../enzymes
for f in ./PDB/*.pdb; do
    ../bin/pythonsh ../bin/prepare_receptor4.py -r $f -A checkhydrogens -U nphs -v
done

# moving pdbqt to a folder
for f in ./*.pdbqt; do
    mv $f ./PDBQT
done

# creating vina config file
mkdir -p ../results
cd ./PDBQT
for f in *.pdbqt; do
    python ../../bin/prepare_vina_config.py -f $f -xc $XC -yc $YC -zc $ZC -xs $XS -ys $YS -zs $ZS -lo ../../results -lo1 ../../ligands/PDBQT
done

# running vina
echo "Running Vina with search box parameters: Center($XC, $YC, $ZC), Size($XS, $YS, $ZS)"
cd ../..
for f in results/*/config*; do
    python ./bin/dock.py -i $f
done
