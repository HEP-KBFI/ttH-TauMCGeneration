#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630
if [ -r CMSSW_9_3_6/src ] ; then
 echo release CMSSW_9_3_6 already exists
else
scram p CMSSW CMSSW_9_3_6
fi
cd CMSSW_9_3_6/src
eval `scram runtime -sh`
git cms-init
git cms-addpkg GeneratorInterface/Pythia8Interface
wget https://raw.githubusercontent.com/kandrosov/cmssw/9d21b36d1528279681ea7c17cff7d925d19b979e/GeneratorInterface/Pythia8Interface/interface/ResonanceDecayFilterHook.h -O GeneratorInterface/Pythia8Interface/interface/ResonanceDecayFilterHook.h
wget https://raw.githubusercontent.com/kandrosov/cmssw/9d21b36d1528279681ea7c17cff7d925d19b979e/GeneratorInterface/Pythia8Interface/src/Py8InterfaceBase.cc -O GeneratorInterface/Pythia8Interface/src/Py8InterfaceBase.cc
wget https://raw.githubusercontent.com/kandrosov/cmssw/9d21b36d1528279681ea7c17cff7d925d19b979e/GeneratorInterface/Pythia8Interface/src/ResonanceDecayFilterHook.cc -O GeneratorInterface/Pythia8Interface/src/ResonanceDecayFilterHook.cc
scram b
cd -
echo $CMSSW_BASE
source /cvmfs/cms.cern.ch/crab3/crab.sh
python do_fragments_lhe.py
echo "Submit all to crab"
## if you are submitting by hand remember: you shall be with the CMSSW enviroment loaded above
filename="procsToSub_lhe.txt"
while read -r line
do
    name="$line"
    echo "Submitting - $name"
    crab submit $name
done < "$filename"
