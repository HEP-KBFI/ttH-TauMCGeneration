#!/bin/bash
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc630
if [ -r CMSSW_9_4_0_patch1/src ] ; then
 echo release CMSSW_9_4_0_patch1 already exists
else
scram p CMSSW CMSSW_9_4_0_patch1
fi
cd CMSSW_9_4_0_patch1/src
eval `scram runtime -sh`
scram b
cd ../../
echo "Doing the template for the premix config, this can take some minutes, and your grid password: "
voms-proxy-init
# do one PU config and for the rest use sed
cmsDriver.py step1 --fileout file:HHTo2T2V_step1.root --filein file:tree_lhe.root --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MC_v2_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --nThreads 8 --datamix PreMix --era Run2_2017 --python_filename HHTo2T2V_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 10 || exit $? ;

echo $CMSSW_BASE
source /cvmfs/cms.cern.ch/crab3/crab.sh
python do_fragments.py
### To submit to crab: you need wait the LHE/previous step be finished
### and to adapt the HHTo*_M*_*_cfg.py with the crab path
# source /cvmfs/cms.cern.ch/crab3/crab.sh
# bash procsToSub_premix_1.sh
# bash procsToSub_premix.sh
# bash procsToSub_premix.sh
## if you are submitting to crab: you shall be with the CMSSW enviroment loaded above
