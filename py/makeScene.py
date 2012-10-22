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

BUILDPARTS = False
BUILDJUST = None
BUILDDIR = "build"
if not os.path.exists(BUILDDIR):
    cmd = "mkdir " + BUILDDIR
    print cmd
    os.system(cmd)

if len(sys.argv) < 2:
    print "makeScene.py scenefile.txt [changes]"
    print 'specify "changes" as last option to play modified files'
    exit()

text2vox = findPy("text2vox.py")
print "text2vox:", text2vox

CHANGES = False
PLAY = False
for e in sys.argv[1:]:
    if e[:2] == "--":
        try:
            opt, val = e.split("=")
            try:
                val = int(val)
            except:
                pass
        except:
            opt = e
            val = True
        if opt == "--force":
            BUILDJUST = val
        else:
            globals()[opt[2:].upper()] = val
    else:
        scene = e
print "BUILDJUST:", BUILDJUST, "CHANGES:", CHANGES, "PLAY:", PLAY

f = open(scene)
lines = f.readlines()
f.close()
scene = scene[:-4]
index = 0
actors = {}
files = OrderedDict()
os.chdir(BUILDDIR)

i = 0
while i < len(lines):
    line = lines[i]
    line = line.strip()
    if line == "":
        i += 1
        continue

    if ":" in line and "{" in line:        
        if line.find(":") < line.find("{"):                     #inline actor definition
            actor, parameters = line.split(":")
            actors[actor.strip()] = parameters.strip()
        else:                                                   #include file
            a, fn = line.split(":")
            f = open("../" + fn.strip().replace("}",""))
            for ln in f.readlines():
                lines.insert(i + 1, ln)
            f.close()
        i += 1
        continue

    actor = None
    if "{" in line:
        extra = ""
        temp = line[1:].replace("}", "")
        if ";" in temp:                                         #extra parameters for these lines (until next actor spec)
            extra = temp[temp.find(";") + 1:]
            temp = temp[:temp.find(";")]
        if temp in actors:
            actor = temp
            line = actors[actor]
            if extra:
                line = line.replace("}","") + ";" + extra + "}"
            name = scene + "_" + str(index) + "_" + actor + ".txt"
            index += 1
            files[name] = ""
    files[name] += line + "\n"
    i += 1

buildMaster = False
errors = 0
index = -1
for fil in files:
    index += 1
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

    if BUILDJUST != None:
        if type(BUILDJUST) == type(0):
            rewrite = BUILDJUST == index
        else:
            rewrite = BUILDJUST == fil

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
        cmd = text2vox + " " + fil + " " + wav + " >> " + scene + ".log"
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
        if BUILDJUST == None:
            print "++++++++>", fil, "is unchanged"

if (BUILDJUST == None) and (buildMaster and errors == 0):
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
else:
    if PLAY:
        cmd = "mplayer " + scene + ".wav"
        if type(PLAY) == type(0):
            cmd += " -ss " + str(PLAY)
        print cmd
        os.system(cmd)
