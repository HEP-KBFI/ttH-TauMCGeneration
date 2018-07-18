#!/usr/bin/env python
import os, sys, time,math
import os, subprocess, sys
from collections import OrderedDict
from collections import OrderedDict

def run_cmd(command):
  print "executing command = '%s'" % command
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

## final states
dprocsLHE = OrderedDict()
dprocsLHE["HHTo4T_M400"]    = [ "HHTo4T_madgraph_pythia8_CP5_M400", "/HHTo4T_madgraph_pythia8_CP5_M400/acarvalh-lhe_v1p1_RAWSIMoutput-01dbc76b9163f272d689ee584026b335/USER"]
dprocsLHE["HHTo4V_M400"]    = ["HHTo4V_madgraph_pythia8_CP5_M400", "/HHTo4V_madgraph_pythia8_CP5_M400/acarvalh-lhe_v1p1_RAWSIMoutput-22e69d704b5e82645b7125cea1446972/USER"]
dprocsLHE["HHTo2T2V_M400"]  = ["HHTo2T2V_madgraph_pythia8_CP5_M400", "/HHTo2T2V_madgraph_pythia8_CP5_M400/acarvalh-lhe_v1p1_RAWSIMoutput-6d90d178de2038a93c1664826fb8a3d9/USER"]
dprocsLHE["HHTo4T_M700"]  = ["HHTo4T_madgraph_pythia8_CP5_M700", "/HHTo4T_madgraph_pythia8_CP5_M700/acarvalh-lhe_v1p1_RAWSIMoutput-521d60010e233dbb24cfe815e6a59168/USER"]
dprocsLHE["HHTo4V_M700"]  = ["HHTo4V_madgraph_pythia8_CP5_M700", "/HHTo4V_madgraph_pythia8_CP5_M700/acarvalh-lhe_v1p1_RAWSIMoutput-4b6fe354d9a11009055ccc6da85be52e/USER"]
dprocsLHE["HHTo2T2V_M700"]  = ["HHTo2T2V_madgraph_pythia8_CP5_M700", "/HHTo2T2V_madgraph_pythia8_CP5_M700/acarvalh-lhe_v1p1_RAWSIMoutput-6235d203fc6e120cc078921dfab0586b/USER"]

def write_crab(type, name,  DAS, configFile, fixCERN_T2 = False) :
    if fixCERN_T2 : comment = ""
    else : comment = "# "
    return "from WMCore.Configuration import Configuration\
\n\
step = '%s'\n\
part = 'p1'\n\
\n\
config = Configuration()\n\
\n\
config.section_('General')\n\
config.General.requestName = '_'.join(['%s', step, part])\n\
\n\
config.section_('JobType')\n\
config.JobType.pluginName = 'Analysis'\n\
config.JobType.psetName = '%s' \n\
config.JobType.maxMemoryMB = 2500\n\
config.JobType.numCores = 8\n\
\n\
config.section_('Data')\n\
config.Data.inputDataset = '%s'\n\
#config.Data.inputDBS = 'phys03'\n\
config.Data.ignoreLocality = True\n\
config.Data.splitting = 'Automatic'\n\
config.Data.publication = True\n\
config.Data.outputDatasetTag = '{}_v1{}'.format(step, part)\n\
\n\
config.section_('Site')\n\
config.Site.storageSite = 'T2_EE_Estonia'\n\
%sconfig.Site.whitelist = ['T2_CH_CERN']\n\
" % (type, name, configFile, DAS, comment)


cms_base = run_cmd("echo $CMSSW_BASE")
cms_base = cms_base.replace("\n","")

### declare list of keys --- read from output of LHE instead
#procs = ["HHTo4T", "HHTo2T2V", "HHTo4V"]
#masses = [400, 700]
### do configs and crab to step 1
template_step1 = "HHTo2T2V_1_cfg.py"
procsToSub = open("procsToSub_premix_1.sh", 'w')
procsToSubAod = open("procsToSub_premix.sh", 'w')
procsToSubMiniAod = open("procsToSub_premix.sh", 'w')
for pp in [procsToSub, procsToSubAod, procsToSubMiniAod] :
    pp.write("#!/bin/bash \n\n")
    pp.write("cd %s/src \n" % (cms_base))
    pp.write("eval `scram runtime -sh`\n")
    pp.write("scram b\n")
    pp.write("voms-proxy-init\n")
#for proc in procs :
#    for mass in masses :
with open("pufiles.txt", 'r') as pufile :
    for line in pufile :
        if "/" in line : linePU = line
for key in dprocsLHE.keys() :
        nameprc = dprocsLHE[key][0]
        confFile = template_step1.replace("HHTo2T2V", nameprc)
        with open(confFile, 'w') as out_file:
            with open(template_step1, 'r') as in_file:
                for line in in_file:
                    if "HHTo2T2V" in line : out_file.write(line.replace("HHTo2T2V", nameprc))
                    elif "['pufiles.txt']" in line : out_file.write(line.replace("['pufiles.txt']", linePU))
                    else : out_file.write(line)

        print ("done file: ", confFile)
        ## do crab submission file
        newFile = "submit_"+nameprc+"_premix_step1.py"
        ## the whitelist to pu stage SHOULD be a plave where the PU file is located on DISK
        file = open(newFile, 'w')
        file.write(write_crab('premix_step1', dprocsLHE[key][0], dprocsLHE[key][1], confFile, fixCERN_T2 = True))
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
        file.write(write_crab('premix', dprocsLHE[key][0], "PLACEHOLDER", nameprc+"_premix_cfg.py"))
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
        file.write(write_crab('miniaod', dprocsLHE[key][0], "PLACEHOLDER", nameprc+"_miniaod_cfg.py"))
        file.close()
        procsToSubMiniAod.write("crab submit "+newFile+"\n")
procsToSub.close()
procsToSubAod.close()
procsToSubMiniAod.close()
