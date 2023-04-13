#!/bin/bash

export CVS_PASSFILE="tmp.cvspass"
export CVSROOT=":pserver:aod@cvs01.osf.alma.cl:2401/project21/CVS"
echo "/1 $CVSROOT A=d3K%d" > $CVS_PASSFILE

cvs checkout AIV/science/DSO/jy_per_k.txt
cvs checkout AIV/science/DSO/jy_per_k_fit.txt
cvs checkout AIV/science/PadData/almaAntPos.txt
cvs checkout AIV/science/PadData/antennaMoves.txt
cvs checkout AIV/science/qa2
cvs checkout AIV/science/analysis_scripts

rm -v AIV/science/*/*pyc
rm -f $CVS_PASSFILE
