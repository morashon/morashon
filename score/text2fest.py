#!/usr/bin/python
"""
process marked up text to produce a festival-ready xml file (using LIBRETTO tag, which allows pitch for beg and end of each syllable)

Markup: tempo and intonation hold for each sentence.

examples:
_Annai: +20 7 Thisone, 3 will you 5 come 7 with us?
_Thisone: Come -30 7 where_2
_Annai: We're 7 starting a new 3 life. 7 Off 5 the 3 grid.  +15 Our 7 own 3 grid in fact.  It's something 7,3,3 wonderful.  5,7,3,3 Spectacular.

interpolation logic:
    if no beg specified, use previous (do this in a pass)
    if no end specified, interp to next beg, or bigdrop
    add little drop to all ends

"""
import sys, os
from xml.dom import minidom
import sylCount

BASE = 120
DROP = 10
BIGDROP = 40

def each(seq):
    return range(len(seq))

def parseWord(word):
    parts = word.split(";")
    word = parts[-1]
    freqs = []
    durs = []
    for section in parts[:-1]:
        if "-" in section or "+" in section:
            for part in section.split(","):
                durs.append(float(part))
        else:
            for part in section.split(","):
                freqs.append([])
                for p in part.split("_"):
                    freqs[-1].append(float(p))
    cnt = sylCount.nsyl(word)
    if not cnt:
        cnt = 1
    return word, cnt, freqs, durs

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
    dur = 1.0
    line = line.strip()
    if line == "":
        continue
    print line
    words = line.split()

    data = []

    for word in words:
        data.append(parseWord(word))

    f = BASE
    for word, syls, freqs, durs in data:                    #first, fill in missing fbeg's
        for i in range(syls):
            if i >= len(freqs):
                freqs.append([f])
            else:
                f = freqs[i][0]
        print word, "new freqs with begs:", freqs

    for ix in each(data):                                   #then compute fend's
        word, syls, freqs, durs = data[ix]
        print "fixing", word, freqs
        for j in each(freqs):                               #for each syllable
            print "     syllable:", j
            f = freqs[j]
            nxt = None
            if len(f) < 2:
                if j < len(freqs) - 1:                      #interpolate to next fbeg in next syllable
                    nxt = freqs[j+1][0]
                    print "--------------------interpolate to next syl:", nxt
                elif ix < len(data) - 1:
                    nxt = data[ix+1][2][0][0]                 #interpolate to next fbeg in next word
                    print "--------------------interpolate to next word:", nxt
                if nxt:
                    interp = (f[0] * 2 + nxt) / 3.0 - DROP  #yes that's how we roll
                    print "--------------=======------interp:", f[0], nxt, interp
                    f.append(interp)
                else:                                       #end of story
                    f.append(f[0] - BIGDROP)
        print word, "new freqs with fends:", freqs

    for word, syls, freqs, durs in data:
        print word, "syls:", syls, "freqs:", freqs, "durs:", durs

        pitch = xdoc.createElement("PITCH")
        s = ""
        for i in range(syls):
            fbeg, fend = freqs.pop(0)
            s  += "," + str(fbeg) + "," + str(fend)
        pitch.setAttribute("FREQ", s[1:])
        duration = xdoc.createElement("DURATION")
        s = ""
        for i in range(syls):
            if len(durs):
                dur = 1.0 / (1.0 + durs.pop(0) * 0.01)
            s  += "," + str(dur)
        duration.setAttribute("SECONDS", s[1:])
        text = xdoc.createTextNode(word)
        duration.appendChild(text)
        pitch.appendChild(duration)
        xbody.appendChild(pitch)


out = xdoc.toprettyxml()
f = open(fout, 'w')
f.write(out)
f.close()

