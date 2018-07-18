#!/usr/bin/env python
import os, subprocess, sys
from array import array
from ROOT import *
from math import sqrt, sin, cos, tan, exp
import numpy as np
import glob

procP1=glob.glob("/eos/cms//store/mc/RunIISummer17PrePremix/Neutrino_E-10_gun/GEN-SIM-DIGI-RAW/MC_v2_94X_mc2017_realistic_v9-v1/*/*.root")
print len(procP1)

procsToSub = open("pufiles.txt", 'w')
procsToSub.write("[")
for proc in procP1 :
   procsToSub.write("'")
   #procsToSub.write(proc.replace("/eos/cms//","/"))
   #procsToSub.write(proc)
   procsToSub.write(proc.replace("/eos/cms//","file:/eos/cms/"))
   procsToSub.write("', ")
procsToSub.write("]")
