#!/usr/bin/env python
import os, sys, time,math
import os, subprocess, sys
from collections import OrderedDict
import fileinput
import glob
workingDir = os.getcwd()
def run_cmd(command):
  print "executing command = '%s'" % command
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

crab_folder = "HHTo2T2V_madgraph_pythia8_CP5_M400"
in_hdfs = "/hdfs/local/acaan/HH_MC/premix/HHTo4T/"
hdfs_folder = "/home/acaan/ttH-TauMCGeneration/fullsim/HHTo4T/AODSIM/" # "/hdfs/local/acaan/HH_MC/premix/HHTo4T/"
hdfs_folder_miniAOD = "/home/acaan/ttH-TauMCGeneration/fullsim/HHTo4T/miniAODSIM/"
hdfs_input = "/hdfs/local/acaan/HH_MC/premix_step1/HHTo4T/"
#hdfs_input = "/home/acaan/ttH-TauMCGeneration/fullsim/premix_step1/HHTo4T/" #"/hdfs/local/acaan/HH_MC/premix_step1/HHTo4T/"

cms_base = run_cmd("echo $CMSSW_BASE")
cms_base = cms_base.replace("\n","")

toProcess = glob.glob(hdfs_input+crab_folder+'/*.root')
toProcess_inLHE = glob.glob(hdfs_input+crab_folder+'/*_inLHE*.root')
run_cmd("mkdir -p "+crab_folder+"_aod/")
run_cmd("mkdir -p "+hdfs_folder+"/"+crab_folder)
run_cmd("mkdir -p "+hdfs_folder_miniAOD+"/"+crab_folder)

path_to_file = "template_aod_cfg.py"
path_to_file_miniaod = "template_miniaod_cfg.py"

submitall = open(crab_folder+"submit_aod.sh","w")
countSubmit = 0
submitall.write("#!/bin/bash \n\n")
countJoin = 0
join = 2 # files
countfiles = 0
allfiles = len(toProcess) - len(toProcess_inLHE)
#allfiles = len(toProcess_inLHE)
for pp, proc in enumerate(toProcess) :
    if "_inLHE" in proc : continue
    #if countSubmit > 21 : continue

    if ((os.stat(proc).st_size < 2000000000 and not "_inLHE" in proc) or (os.stat(proc).st_size < 1400000 and "_inLHE" in proc)) : continue
    #if os.path.isfile(output_file) :
    #    if (os.stat(output_file).st_size > 400000000 and not "_inLHE" in proc) : continue

    if countJoin == 0:
        if "_inLHE" in proc :
            fileToWrite = crab_folder+"_aod/"+crab_folder+"_inLHE_"+str(countSubmit)+"_aod_cfg.py"
            fileToWrite_miniaod = crab_folder+"_aod/"+crab_folder+"_inLHE_"+str(countSubmit)+"_miniaod_cfg.py"
        else :
            fileToWrite = crab_folder+"_aod/"+crab_folder+"_"+str(countSubmit)+"_aod_cfg.py"
            fileToWrite_miniaod = crab_folder+"_aod/"+crab_folder+"_"+str(countSubmit)+"_miniaod_cfg.py"
        filesJoinRm = ""
        filesJoin = ""

    filesJoin += "\'file:"+str(proc)+"\',"
    countJoin += 1
    countfiles+=1

    if countJoin == join or countfiles == int(allfiles)-1 :
        output_file = hdfs_folder+crab_folder+"/"+crab_folder+str(countJoin)+"_"+str(countSubmit)+"_aod.root"
        output_file_miniaod = output_file.replace("AODSIM", "miniAODSIM").replace("aod", "miniaod")

        fileToWriteSh = fileToWrite.replace("_cfg.py",".sh")
        submitall.write("sbatch --mem=4g "+fileToWriteSh+"\n")
        countSubmit+=1

        filesJoin = filesJoin[:-1] ### remove the last coma
        with open(fileToWrite, 'w') as out_file:
            with open(path_to_file, 'r') as in_file:
                for line in in_file:
                    if "input.root" in line :
                        out_file.write(line.replace("'file:input.root'",filesJoin))
                    elif "output.root" in line :
                        out_file.write(line.replace("output.root", output_file))
                    else : out_file.write(line)

        with open(fileToWrite_miniaod, 'w') as out_file:
            with open(path_to_file_miniaod, 'r') as in_file:
                for line in in_file:
                    if "input.root" in line :
                        out_file.write(line.replace("'file:input.root'","'file:"+output_file+"'"))
                    elif "output.root" in line :
                        out_file.write(line.replace("output.root", output_file_miniaod))
                    else : out_file.write(line)
        #### do also submission file
        pp = open(fileToWriteSh,"w")
        pp.write("#!/bin/bash \n\n")
        pp.write("source /cvmfs/cms.cern.ch/cmsset_default.sh \n")
        pp.write("export SCRAM_ARCH=slc6_amd64_gcc630\n")
        pp.write("if [ -r CMSSW_9_4_7/src ] ; then\n")
        pp.write(" echo release CMSSW_9_4_7 already exists\n")
        pp.write("else\n")
        pp.write("scram p CMSSW CMSSW_9_4_7\n")
        pp.write("fi\n")
        pp.write("cd CMSSW_9_4_7/src\n")
        pp.write("eval `scram runtime -sh`\n")
        pp.write("scram b\n")
        pp.write("cd ../.. \n")
        pp.write("cmsRun %s \n" % (fileToWrite))
        pp.write("if [ ! -f %s ]; then\n" % output_file)
        pp.write("   echo \"File not found!\" %s \n" % output_file)
        pp.write("   exit 0 \n" )
        pp.write("fi \n" )
        pp.write("cmsRun %s \n" % (fileToWrite_miniaod))
        pp.write("if [ ! -f %s ]; then\n" % output_file_miniaod)
        pp.write("   echo \"File not found!\" %s \n" % output_file_miniaod)
        pp.write("   exit 0 \n" )
        pp.write("fi \n" )
        pp.write("size=$( perl -e \'print -s shift\' \"%s\" )\n" % output_file_miniaod )
        pp.write("if [ $size -gt 2000000 ]\n" )
        pp.write("then\n" )
        pp.write("    echo $size\n" )
        pp.write("else \n" )
        pp.write("    return 0\n" )
        pp.write("fi\n" )
        pp.write("rm %s \n" % output_file )
        countJoin = 0

submitall.close()
print ("to submit all ", countSubmit, "files with: ", crab_folder+"submit_aod.sh")
