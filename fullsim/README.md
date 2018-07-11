# Scripts to do private productions of fullsim

The generation of MC is done in 4 steps:
<\n>
- LHE
<\n>
- premix step1
<\n>
- PreMix
<\n>
- miniAOD
<\n>
<\n>

The LHE step is directly submitted to crab doing:
<\n>

"""
bash submit_lhe.sh
"""

The processes and masses that are going to be submitted by the script above are entered on the file (see dprocs and gridpacks):
<\n>

"""
do_fragments_lhe.py
"""

All the config/submission files to the folowing steps are obtained by the bellow:

"""
bash configs_premix_miniaod.sh
"""

The subsequent steps depend on the jobs for the anterior steps to be finished, therefore I did not made crab submission to be automatic.

To help being at least a bit automatic this last script produces a list of submission files for each step on a bash script.
<\n>

You will need to have right to use CRAB, and have a valid Grid certificate
<\n>
Check here: https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookRunningGrid#GetCert
