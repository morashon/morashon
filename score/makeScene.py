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

scene = sys.argv[1]
f = open(scene)
lines = scene.readlines()
f.close()

for line in lines:
    line = line.strip()
    print line
