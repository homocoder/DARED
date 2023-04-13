#!/bin/bash
echo "adding Python"
cd python
bash ./Miniconda3-latest-Linux-x86_64.sh -b -p miniconda3
export PATH="./miniconda3/bin:$PATH"
##ADD docopt for DR assign
./miniconda3/bin/conda install docopt -y
./miniconda3/bin/conda install pandas -y
