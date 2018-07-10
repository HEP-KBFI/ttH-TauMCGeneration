#!/usr/bin/env python
import os, sys, time,math
import os, subprocess, sys
from collections import OrderedDict
import fileinput

def run_cmd(command):
  print "executing command = '%s'" % command
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

#run_cmd("cmsrel CMSSW_10_0_4") # ; cd CMSSW_10_0_4/src ; cmsenv
cms_base = run_cmd("echo $CMSSW_BASE")
cms_base = cms_base.replace("\n","/")
print cms_base
repoForFragments = cms_base+"/src/Configuration/GenProduction/python"
dprocs = OrderedDict()

## final states
dprocs["HHTo4T"]    = ["ResonanceDecayFilter_example_HHTo4T_madgraph_pythia8_CP5_cff.py", "'https://raw.githubusercontent.com/cms-sw/genproductions/master/python/ThirteenTeV/Higgs/HH/ResonanceDecayFilter_example_HHTo4T_madgraph_pythia8_CP5_cff.py'"]
#dprocs["HHTo4V"]    = [1,     3004,      "Flips",       True]
dprocs["HHTo2T2V"]  = ["ResonanceDecayFilter_example_HHTo2T2V_madgraph_pythia8_CP5_cff.py",    "'https://raw.githubusercontent.com/cms-sw/genproductions/master/python/ThirteenTeV/Higgs/HH/ResonanceDecayFilter_example_HHTo2T2V_madgraph_pythia8_CP5_cff.py'"]

## processes and masses
gridpacks = [
  [400, "/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/madgraph/V5_2.4.2/Radion_hh_narrow_M400/v1/Radion_hh_narrow_M400_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz"],
  [700, "/cvmfs/cms.cern.ch/phys_generator/gridpacks/2017/13TeV/madgraph/V5_2.4.2/Radion_hh_narrow_M700/v1/Radion_hh_narrow_M700_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz"]
]

run_cmd("mkdir -p "+repoForFragments)
header = "import FWCore.ParameterSet.Config as cms"
toProcess = []
for key in dprocs.keys() :
    path_to_file = cms_base+"/src/Configuration/GenProduction/python"+"/"+dprocs[key][0]
    #print "wget "+dprocs[key][1]+" -O "+ path_to_file
    run_cmd("wget "+dprocs[key][1]+" -O "+path_to_file)
    for mass in gridpacks :
        call_gridpacks =  "\
\n\
externalLHEProducer = cms.EDProducer(\"ExternalLHEProducer\",\n\
args = cms.vstring('%s'),\n\
nEvents = cms.untracked.uint32(5000),\n\
numberOfParameters = cms.uint32(1),\n\
outputFile = cms.string('cmsgrid_final.lhe'),\n\
scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')\n\
)\n\n" % (mass[1])
        newFile = path_to_file.replace("_cff.py","_M"+str(mass[0])+"_cff.py")
        with open(newFile, 'w') as out_file:
            with open(path_to_file, 'r') as in_file:
                for line in in_file:
                    if header in line : out_file.write(line + call_gridpacks)
                    else : out_file.write(line)
        toProcess = toProcess + [dprocs[key][0].replace("_cff.py","_M"+str(mass[0])+"_cff.py")]
        print ("done file: ", newFile)
run_cmd("cd $CMSSW_BASE/src ; scram b -j 8")

print toProcess
procsToSub = open("procsToSub_lhe.txt", 'w')
for pp, process in enumerate(toProcess) :
   ## do the LHE
   nameprc = process.replace("ResonanceDecayFilter_example_","")
   nameprc = nameprc.replace("_cff.py","")
   process1 = "cmsDriver.py Configuration/GenProduction/python/%s \
   --fileout file:tree_lhe.root \
   --mc --eventcontent RAWSIM,LHE \
   --datatier GEN-SIM,LHE --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision \
   --step LHE,GEN,SIM --era Run2_2017 \
   --python_filename %s_lhe.py --no_exec -n 5" % (process, nameprc)
   #run_cmd(process1)
   newFile = "submit_"+nameprc+"_lhe.py"
   writeSubmit ="\
from WMCore.Configuration import Configuration\n\
\n\
step = 'lhe'\n\
part = 'p1'\n\
\n\
config = Configuration()\n\
\n\
config.section_('General')\n\
config.General.requestName = '_'.join(['%s', step, part])\n\
\n\
config.section_('JobType')\n\
config.JobType.pluginName = 'PrivateMC'\n\
config.JobType.psetName = '%s_lhe.py'\n\
config.section_('Data')\n\
config.Data.outputPrimaryDataset = '%s'\n\
config.Data.splitting = 'EventBased'\n\
config.Data.unitsPerJob =  1000\n\
config.Data.totalUnits = 500000\n\
config.Data.publication = True\n\
config.Data.outputDatasetTag = '{}_v1{}'.format(step, part)\n\
\n\
config.section_('Site')\n\
config.Site.storageSite = 'T2_EE_Estonia'\n\
#config.Site.whitelist = ['T2_EE_Estonia']\n\
" % (nameprc, nameprc, nameprc)
   file = open(newFile, 'w')
   file.write(writeSubmit)
   file.close()
   print ("submission file ", newFile)
   procsToSub.write(newFile+"\n")
procsToSub.close()
   #os.system('crab submit %s' % (newFile))
   #if pp == len(toProcess) - 1 :
   #    print "Run one file to do the template file for the premix (%s) = 5 events ~ 11:40" % (nameprc)
   #    run_cmd('cmsRun %s_lhe.py' % (nameprc))


##
#    --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring
