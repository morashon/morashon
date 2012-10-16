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
from findPy import *
from ordereddict import OrderedDict

BUILDPARTS = True

if len(sys.argv) < 2:
    print "makeScene.py scenefile.txt [changes]"
    print 'specify "changes" as last option to play modified files'
    exit()

text2vox = findPy("text2vox.py")

scene = sys.argv[1]
CHANGES = False
if len(sys.argv) > 2 and sys.argv[2].lower() == "changes":
    CHANGES = True
f = open(scene)
lines = f.readlines()
f.close()
scene = scene[:-4]
index = 0
actors = {}
files = OrderedDict()
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

buildMaster = False
errors = 0
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
        buildMaster = True
        print "-------->", fil, "is new or has changed -- writing to disk:"
        print files[fil]
        f = open(fil, "w")
        f.write(files[fil])
        f.close()
        print "   rebuilding wav file"
        wav = fil[:-4] + ".wav"
        cmd = "rm " + wav
        print cmd
        os.system(cmd)
        cmd = text2vox + " " + fil + " " + wav + " > " + scene + ".log"
        print cmd
        os.system(cmd)
        if not os.path.exists(wav):
            print "***ERROR*** failed to build", wav, "-- renaming to force rebuild"
            cmd = "mv " + fil + " " + fil[:-4] + "_error.txt"
            print cmd
            os.system(cmd)
            errors += 1
        else:
            if CHANGES:
                cmd = "mplayer " + fil[:-4] + ".wav"
                print cmd
                os.system(cmd)
    else:
        print "++++++++>", fil, "is unchanged"

if buildMaster and errors == 0:
    print "Building master wav file"
    cmd = "sox "
    for fil in files:
        print fil
        cmd += fil[:-4] + ".wav "
    cmd += scene + ".wav"
    print cmd
    os.system(cmd)

    if BUILDPARTS:
        print "Building parts for each actor"
        for actor in actors:
            someAudio = False
            cmd = "sox "
            for fil in files:
                if not "_" + actor + ".txt" in fil:
                    cmd += "-v 0 "
                else:
                    someAudio = True
                cmd += fil[:-4] + ".wav "
            cmd += scene + "_" + actor + ".wav"
            if someAudio:
                print cmd
                os.system(cmd)

if errors:
    print errors, "errors encountered -- will not rebuild master"
