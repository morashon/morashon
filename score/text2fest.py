#!/usr/bin/python
"""
process marked up text to produce a festival-ready xml file (using LIBRETTO tag, which allows pitch for beg and end of each syllable)

Markup: tempo and intonation hold for each sentence.

examples:
_Annai: +20 7 Thisone, 3 will you 5 come 7 with us?
_Thisone: Come -30 7 where_2
_Annai: We're 7 starting a new 3 life. 7 Off 5 the 3 grid.  +15 Our 7 own 3 grid in fact.  It's something 7,3,3 wonderful.  5,7,3,3 Spectacular.

"""
import sys, os
from xml.dom import minidom
import sylCount

def parseWord(word):
    cnt = sylCount.nsyl(word)
    return [1] * cnt

if len(sys.argv) < 2:
    print "text2fest.py markupfile.txt festfile.xml"
    exit()

fin = sys.argv[1]
fout = sys.argv[2]
xdoc = minidom.Document()
xbody = xdoc.createElement("LIBRETTO")
xbody.setAttribute("DURATIONSMULTIPLY", "true")
xdoc.appendChild(xbody)

f = open(fin)
r = f.readlines()
for line in r:
    line = line.strip()
    if line == "":
        continue
    print line
    words = line.split()
    for word in words:
##        syls = sylCount.nsyl(word)
        syls = parseWord(word)
        print word, "has", len(syls), "syllables"
        pitch = xdoc.createElement("PITCH")
        s  = "120,90"
        for i in range(len(syls)-1):
            s += ",120,90"
        pitch.setAttribute("FREQ", s)
        duration = xdoc.createElement("DURATION")
        s = "1.0"
        for i in range(len(syls)-1):
            s += ",1.0"
        duration.setAttribute("SECONDS", s)
        text = xdoc.createTextNode(word)
        duration.appendChild(text)
        pitch.appendChild(duration)
        xbody.appendChild(pitch)

out = xdoc.toprettyxml()
f = open(fout, 'w')
f.write(out)
f.close()

