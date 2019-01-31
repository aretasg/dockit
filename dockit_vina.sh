#!/usr/bin/env bash

# creating ligand and proteins directories
mkdir -p ligands/PDB
mkdir -p proteins/PDB

# help and usage information
while test $# -gt 0; do
        case "$1" in
                -h|--help)
                        echo
                        echo "Dockit-Vina"
                        echo "Description: Dockit-Vina is a an AutoDock Vina bash/Python wrapper
for faster docking procedure and more user-friendly experience (github.com/aretas2/dockit-vina).
* Have MGLTools 1.5.6 installed. If you are using Linux or Windows machine
please replace pyhtonsh in the bin folder with the one in MGLTools bin bolder.
macOS users with default directory used for MGLTools installation can move to the
next step.
* Have either Python 2.7 or 3.6.
* To use Dockit-Vina you will need to place your protein molecule(s)
inside proteins/PDB directory and ligand molecule(s) in ligands/PDB
directory;
* specify the search window parameters on command line;
* Docking results can be found in the results folder."
                        echo
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
    echo "x center argument missing"
    exit 1
fi
if [ -z "$YC" ]; then
    echo "y center argument missing"
    exit 1
fi
if [ -z "$ZC" ]; then
    echo "z center argument missing"
    exit 1
fi
if [ -z "$XS" ]; then
    echo "x size argument missing"
    exit 1
fi
if [ -z "$YS" ]; then
    echo "y size argument missing"
    exit 1
fi
if [ -z "$ZS" ]; then
    echo "z size argument missing"
    exit 1
fi

# checking if there are any ligand and proteins files
if [ -n "$(ls -A proteins/PDB 2>/dev/null)" ] && [ -n "$(ls -A ligands/PDB 2>/dev/null)" ]
then
  echo "Found files in the proteins and ligands folders. Proceeding."
else
  echo "No files proteins and/or ligands found."
  exit 1
fi

# performing energy minimisation using Amber
cd ligands/PDB
if [ -d "$AMBERHOME" ]; then
    echo "Performing energy minimisation using Amber!"
    for f in *.pdb; do
        if [[ ${f: -8} == "_min.pdb" ]]; then
            echo "The ligand $f seems to be already minimized. Skipping!"
        else
            python ../../bin/emm.py -pdb $f
            # rm -r ANTECHAMBER*
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
    echo "Failed to detect Amber directory. Please install Amber and set AMBERHOME (e.g. source /Users/username/amber18/amber.sh) directory to enable ligand energy minimization feature!"
fi
echo

# preparing ligands
cd .. # back to ligands dir
for f in ./PDB/*.pdb; do
    ../bin/pythonsh ../bin/prepare_ligand4.py -l $f -A hydrogens -U nphs -v
done
echo

# moving pdbqt to a folder
mkdir -p ./PDBQT
for f in ./*.pdbqt; do
    mv $f ./PDBQT
    # replacing "-" with "_"
    cd PDBQT
    mv -v "$f" "$(echo $f | sed 's/-/\_/g')"
    cd ..
done

# preparing proteins
mkdir -p ../proteins/PDBQT
cd ../proteins
for f in ./PDB/*.pdb; do
    ../bin/pythonsh ../bin/prepare_receptor4.py -r $f -A checkhydrogens -U nphs -v
done
echo

# moving pdbqt to a folder
for f in ./*.pdbqt; do
    mv $f ./PDBQT
    cd PDBQT
    mv -v "$f" "$(echo $f | sed 's/-/\_/g')"
    cd ..
done

# creating vina config file
mkdir -p ../results
cd ./PDBQT
for f in *.pdbqt; do
    python ../../bin/prepare_vina_config.py -f $f -xc $XC -yc $YC -zc $ZC -xs $XS -ys $YS -zs $ZS -lo ../../results -lo1 ../../ligands/PDBQT
done
echo

# running vina
echo "Running Vina with search box parameters: Center($XC, $YC, $ZC), Size($XS, $YS, $ZS)."
cd ../..
for f in results/*/config*; do
    python ./bin/dock.py -i $f
done
echo

# generating docking results summary .csv file
if python -c "import pandas" &> /dev/null; then
    echo 'pandas module found.'
else
    echo 'pandas module not found. Installing pandas.'
    python -m pip install pandas
fi

cd bin
echo 'Writting results.'
python get_results.py
echo 'DONE! Thank you for using dockit-vina.'
