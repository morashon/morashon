#!/usr/bin/python
"""

makeScene

Take a scene file and break it into little markup text files
If the file exists and is identical, leave it alone
If it is different, replace it
rebuild xml & wav for any file that is changed (ala make)
combine wavs into master wav

"""

import sys, os

if len(sys.argv) < 2:
    print "makeScene.py scenefile.txt"
    exit()

text2vox = "./text2vox.py"
if not os.path.exists(text2vox):
    text2vox = "../text2vox.py"

scene = sys.argv[1]
f = open(scene)
lines = f.readlines()
f.close()
scene = scene[:-4]
index = 0
actors = {}
files = {}
for line in lines:
    line = line.strip()
    if line == "":
        continue
##    print line

    if ":" in line and "{" in line:                             #actor definition
        actor, parameters = line.split(":")
        actors[actor.strip()] = parameters.strip()
        continue
    actor = None
    if "{" in line:
        temp = line[1:].replace("}", "")
        if temp in actors:
            actor = temp
            line = actors[actor]
            name = scene + "_" + str(index) + "_" + actor + ".txt"
            index += 1
            files[name] = ""
    files[name] += line + "\n"

for fil in files:
##    print "-----------------------", fil
##    print files[fil],
    rewrite = False
    if os.path.exists(fil):
        f = open(fil)
        s = f.read()
        f.close()
        if s != files[fil]:
            rewrite = True
    else:
        rewrite = True

    if rewrite:
        print "-------->", fil, "is new or has changed -- writing to disk:"
        print files[fil]
        f = open(fil, "w")
        f.write(files[fil])
        f.close()
        print "   rebuilding wav file"
        cmd = text2vox + " " + fil + " " + fil[:-4] + ".wav"
        print cmd
        os.system(cmd)
    else:
        print "++++++++>", fil, "is unchanged"
