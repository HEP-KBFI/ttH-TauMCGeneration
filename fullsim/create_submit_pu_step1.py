#!/usr/bin/env python
import os, sys, time,math
import os, subprocess, sys
from collections import OrderedDict
import fileinput
import glob
import ROOT ## to test if the file is sane for resubmission
workingDir = os.getcwd()
import commands

resubmision = True
# 4T 400 try resubmit
# 4T 700 try resubmit
# 2T2V 700 try resubmit
# 2T2V 400 try resubmit
# 4V 400

def run_cmd(command):
  print "executing command = '%s'" % command
  p = subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  stdout, stderr = p.communicate()
  return stdout

crab_folder = "HHTo4T_madgraph_pythia8_CP5_M400"
saveTo = "/hdfs/local/acaan/HH_MC/premix_step1/HHTo4T/"+crab_folder
run_cmd("mkdir -p "+saveTo)
# /hdfs/cms/store/user/acarvalh/HHTo4T_madgraph_pythia8_CP5_M400/lhe_v1p1/180710_223826/0000/
# /hdfs/cms/store/user/acarvalh/HHTo4V_madgraph_pythia8_CP5_M400/lhe_v1p1/180711_133815/0000/
#  /hdfs/cms/store/user/acarvalh/HHTo2T2V_madgraph_pythia8_CP5_M400/lhe_v1p1/180710_223855/0000/
mom = "/hdfs/cms/store/user/acarvalh/%s/lhe_v1p1/*/*/" % (crab_folder)
mom_premix = "%s_premix" % (crab_folder)
toProcess = glob.glob(mom+'*.root')

cms_base = run_cmd("echo $CMSSW_BASE")
cms_base = cms_base.replace("\n","")

run_cmd("mkdir "+mom_premix)
path_to_file = "template_1_cfg.py"
toProcess = glob.glob(mom+'*.root')
submitall = open(crab_folder+"submitall.sh","w")
submitall.write("#!/bin/bash \n\n")
#counterTosleep = 0
for pp, proc in enumerate(toProcess) :
    #if pp > 3 : continue
    #print proc
    #for proc in toProcess :
    if not "_inLHE" in proc :
        for piece in proc.split("/")[10].split("_") :
            if ".root" in piece :
                nsample = piece.replace(".root","")
                continue
        #nsample =  int(proc.split("/")[10].split("_")[6].replace(".root",""))
        nameproc = crab_folder+"_"+str(nsample)+".root" #
        print (nameproc, nsample)
        newFile = mom_premix+"/"+nameproc.replace(".root","_step1_cfg.py")
        lineinput = ""
        rootname = nameproc.replace(".root","_step1.root")
        if lineinput == "" : lineinput = lineinput +"'file:"+proc+"'"
        else : lineinput = lineinput +", 'file:"+proc+"'"
        with open(newFile, 'w') as out_file:
            with open(path_to_file, 'r') as in_file:
                for line in in_file:
                    if "input.root" in line : out_file.write(line.replace("'file:input.root'","["+lineinput+"]"))
                    elif "output.root" in line : out_file.write(line.replace("output.root",rootname))
                    elif "/store" in line :
                        out_file.write(line.replace("/store","root://cms-xrd-global.cern.ch//store"))
                    else : out_file.write(line)
        #### do also submission file
        bashname = workingDir+"/"+mom_premix+"/"+nameproc.replace(".root","_step1.sh")
        configname = workingDir+"/"+mom_premix+"/"+nameproc.replace(".root","_step1_cfg.py")
        fullrootname = workingDir+"/"+rootname
        ppp = open(bashname,"w")
        ppp.write("#!/bin/bash \n\n")
        ppp.write("cd %s/src \n" % (cms_base))
        ppp.write("eval `scram runtime -sh`\n")
        ppp.write("cd - \n")
        #ppp.write("cd %s\n" % (mom_premix))
        ### create your proxy (voms-proxy-init) copy the certificale locally and update the bellow
        ppp.write("export X509_USER_PROXY=/home/acaan/ttH-TauMCGeneration/fullsim/x509up_u1000049\n")
        ppp.write("cmsRun %s \n" % (configname))
        ppp.write("mv %s %s" % (fullrootname, saveTo))
        ppp.close()
        todo = "sbatch --mem=6g %s " % (bashname)
        #print (todo)
        #print ("rootname", fullrootname)
        if resubmision :
            if not os.path.isfile(saveTo+"/"+rootname) :
                submitall.write(todo+"\n")
                print ("to resubmit")
            else :
                statinfo = os.stat(saveTo+"/"+rootname)
                if statinfo.st_size < 1001674 :
                    submitall.write(todo+"\n")
                    print ("to resubmit")
        else :
            submitall.write(todo+"\n")
            #counterTosleep = counterTosleep + 1
            #if counterTosleep == 40 :
            #    submitall.write("sleep 10m\n")
            #    counterTosleep = 0
submitall.close()
print ("to submit all execute: ", crab_folder+"submitall.sh")
