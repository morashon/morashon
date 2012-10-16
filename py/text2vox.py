#!/usr/bin/python
"""

text2vox

convert markup to wav, fixing things, possibly using multiple voices

"""

import sys, os
from findPy import *

cleanup = []

text2fest = findPy("text2fest.py")
fest2vox = findPy("fest2vox.py")

if len(sys.argv) < 2:
    print "text2vox markup.txt outputfile.wav [voice [timbre]]"
    print "yeah, that's sensible"
    exit()

opts = []
argv = []
for i in range(len(sys.argv)):
    if sys.argv[i][:2] == "--":
        opts.append(sys.argv[i])
    else:
        argv.append(sys.argv[i])
sys.argv = argv

for opt in opts:
    text2fest += " " + opt
    fest2vox += " " + opt

markup = sys.argv[1]
outf = sys.argv[2]
voice = ""
if len(sys.argv) > 3:
    voice = sys.argv[3]
timbre = ""
if len(sys.argv) > 4:
    timbre = sys.argv[4]

volume = 1.0

f = open(markup)
a = f.readline()
if a[:1] == "{":
    a = a.strip().replace("}","")
    a = a[1:].split(";")
    for e in a:
        key, val = e.split("=")
        if key.lower() == "timbre":
            timbre = val
        if key.lower() == "voice":
            voice = val.strip()
        if key.lower() == "volume":
            volume = float(val.strip())
f.close()
cmd = text2fest + " " + markup + " _text2vox_.xml"
print cmd
os.system(cmd)
cleanup.append("_text2vox_.xml")

cmd = fest2vox + " _text2vox_.xml " + (voice if voice else "kal_diphone") + " " + (timbre if timbre else "0") + " " + outf
print cmd
os.system(cmd)

cmd = "sox -D -v " + str(volume) + " " + outf + " -ef -r44100 _text2vox_.wav trim 0.9"
print cmd
os.system(cmd)
cmd = "mv _text2vox_.wav " + outf
print cmd
os.system(cmd)    

print "clean up", len(cleanup), "files"
for f in cleanup:
    cmd = "rm " + f
    print "cleanup:", f
    os.system(cmd)
    
