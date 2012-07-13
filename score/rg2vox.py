#!/usr/bin/python
"""

script to invoke rg2fest, fest2wav automagically, using our segment naming conventions

The logic:
    rg2vox song.rg trackname segname

    create festival xml from specified track/segment
    convert to .wav with name seg.wav
    look for file in current dir with form conv-seg-blah (possibly truncated) -- this is a Rosegarden converted file
    if it exists, replace it (using sox to convert to 44.1 float mono)
    if it does not exist, suggest that seg.wav be imported

    if scripts are not in this dir, look one dir up
"""

import sys, os
if len(sys.argv) < 4:
    print "rg2vox song.rg tracklabel segmentlabel"
    exit()

def makeCmd(*args):
    s = ""
    for arg in args:
        arg = str(arg)
        if " " in arg:
            arg = '"' + arg + '"'
        s += arg + " "
    return s.strip()

song = sys.argv[1]
track = sys.argv[2]
seg = sys.argv[3]

rg2fest = "./rg2fest.py"
if not os.path.exists(rg2fest):
    rg2fest = "../rg2fest.py"

fest2wav = "./fest2wav.py"
if not os.path.exists(fest2wav):
    fest2wav = "../fest2wav.py"

cmd = makeCmd(rg2fest, song, seg, track, seg)
print cmd
os.system(cmd)

cmd = makeCmd(fest2wav, seg + ".xml", seg + ".wav")
print cmd
os.system(cmd)

lst = os.listdir(".")
found = False
for fil in lst:
    if not fil[-4:].lower() == ".wav":
        continue
    if fil.find("conv-" + seg + "-") == 0:
        found = True
        print "Found what looks like the appropriate rosegarden sample wav:", fil
        cmd = makeCmd("sox", "-D", seg + ".wav", "-ef", "-r44100", fil)
        print cmd
        os.system(cmd)
        break

if not found:
    lst = os.listdir(os.getenv("HOME") + "/rosegarden")
    for fil in lst:
        if not fil[-4:].lower() == ".wav":
            continue
        if fil.find("conv-" + seg + "-") == 0:
            found = True
            break

    if found:
        print "Tricky Rosegarden! It put the file in ~/rosegarden.  Move it into the current directory, restart Rosegarden, and run this script again."
    else:
        print "Couldn't find a suitable rosegarden file.  Import " + seg + ".wav into your project."