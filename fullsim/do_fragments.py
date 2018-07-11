#!/usr/bin/env python
import os, sys, time,math
import os, subprocess, sys
from collections import OrderedDict

def run_cmd(command):
  print "executing command = '%s'" % command
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

def write_crab(type, name, fixCERN_T2 = False) :
    if fixCERN_T2 : comment = " "
    else : comment = "# "
    return writeSubmit ="\
from WMCore.Configuration import Configuration\
\n\
step = '%s'\n \
part = 'p1'\n\
\n\
config = Configuration()\n\
\n\
config.section_('General')\n\
config.General.requestName = '_'.join(['%s', step, part])\n\
\n\
config.section_('JobType')\n\
config.JobType.pluginName = 'Analysis'\n\
config.JobType.psetName = '%s_%s_cfg.py' \n\
config.JobType.maxMemoryMB = 2600\n\
config.JobType.numCores = 8\n\
\n\
config.section_('Data')\n\
config.Data.inputDataset = '/TTTo2L2Nu_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/matze-lhe_v1p3-1c481b2669c85226f78b96c950275ca9/USER--PLACEHOLDER : take it from crab output on lhe stage'\n\
config.Data.inputDBS = 'phys03'\n\
config.Data.ignoreLocality = True\n\
config.Data.splitting = 'Automatic'\n\
config.Data.publication = True\n\
config.Data.outputDatasetTag = '{}_v1{}'.format(step, part)\n\
\n\
config.section_('Site')\n\
config.Site.storageSite = 'T2_EE_Estonia'\n\
#config.Site.whitelist = ['T2_CH_CERN']\n\
" % (type, name, type, name, comment)

### declare list of keys --- read from output of LHE instead
procs = ["HHTo4T", "HHTo2T2V", "HHTo4V"]
masses = [400, 700]
### do configs and crab to step 1
template_step1 = "HHTo2T2V_1_cfg.py"
procsToSub = open("procsToSub_premix_step1.txt", 'w')
procsToSubAod = open("procsToSub_premix.txt", 'w')
procsToSubMiniAod = open("procsToSub_premix.txt", 'w')
for pp in [procsToSub, procsToSubAod, procsToSubMiniAod]
for proc in procs :
    for mass in masses :
        nameprc = proc+"_M"+str(mass)
        newFile = template_step1.replace("HHTo2T2V", nameprc)
        with open(newFile, 'w') as out_file:
            with open(template_step1, 'r') as in_file:
                for line in in_file:
                    if "HHTo2T2V" in line : out_file.write(line.replace("HHTo2T2V", nameprc))
                    else : out_file.write(line)
        print ("done file: ", newFile)
        ## do crab submission file
        newFile = "submit_"+nameprc+"_premix_step1.py"
        ## the whitelist to pu stage SHOULD be a plave where the PU file is located on DISK
        file = open(newFile, 'w')
        file.write(write_crab('premix_step1', nameprc))
        file.close()
        print ("submission file ", newFile)
        procsToSub.write("crab submit "+newFile+"\n")
        ### do configs to step2
        process1 = "cmsDriver.py step2 --filein file:%s_step1.root\
 --fileout file:%s_premix.root --mc --eventcontent AODSIM --runUnscheduled \
 --datatier AODSIM --conditions 94X_mc2017_realistic_v11 \
 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 8 --era Run2_2017 \
 --python_filename %s_premix_cfg.py --no_exec -n 10 " % (nameprc, nameprc, nameprc)
        print process1
        #run_cmd(process1)
        newFile = "submit_"+nameprc+"_premix.py"
        file = open(newFile, 'w')
        file.write(write_crab('premix', nameprc, fixCERN_T2 = True))
        file.close()
        procsToSubAod.write("crab submit "+newFile+"\n")
        ### do configs to MiniAOD
        process1 = "cmsDriver.py step1 --fileout file:%s_miniAOD.root \
 --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM \
 --conditions 94X_mc2017_realistic_v11 --step PAT --nThreads 8 \
 --era Run2_2017 --python_filename %s_miniaod_cfg.py --no_exec -n 10 " % (nameprc, nameprc)
        #run_cmd(process1)
        print process1
        newFile = "submit_"+nameprc+"_miniaod.py"
        file = open(newFile, 'w')
        file.write(write_crab('miniaod', nameprc))
        file.close()
        procsToSubMiniAod.write("crab submit "+newFile+"\n")

procsToSub.close()
procsToSubAod.close()
procsToSubMiniAod.close()


## step 2 configs and crab
# #cmsDriver.py step2 --filein file:HHTo2T2V_step1.root --fileout file:HHTo2T2V_premix.root --mc --eventcontent AODSIM --runUnscheduled --datatier AODSIM --conditions 94X_mc2017_realistic_v11 --step RAW2DIGI,RECO,RECOSIM,EI --nThreads 8 --era Run2_2017 --python_filename HHTo2T2V_premix_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 10 || exit $? ;




#    --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring \
