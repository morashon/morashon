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

BASE = 130
DROP = BASE / 5.0
BIGDROP = DROP * 2
SCALE = 7.0
SENTENCEPAUSE = 0.6
RESTPAUSE = 0.25
FIXBEGINNING = True

def each(seq):
    return range(len(seq))

def scale2freq(n):
    return BASE * 2.0 ** (n / SCALE)

def parseWord(word):
    if "|" in word:
        s = word.replace("|", "")
        if len(s):
            dur = float(s)
        else:
            dur = RESTPAUSE * word.count("|")
        return "|", 1, [], [dur]
            
    parts = word.split(";")
    word = parts[-1]
    freqs = []
    durs = []
    for section in parts[:-1]:
        if "%" in section:
            for part in section.replace("%","").split(","):
                dur = 100.0 / float(part)
                durs.append(dur)
        else:
            for part in section.split(","):
                freqs.append([])
                for p in part.split("_"):
                    freq = scale2freq(float(p))
                    freqs[-1].append(freq)
    cnt = sylCount.nsyl(word)
    if not cnt:
        cnt = 1
    return word, cnt, freqs, durs

def addRest(doc, node, t=0.25):
    x = doc.createElement("REST")
    x.setAttribute("SECONDS", str(t))
    x.appendChild(doc.createTextNode(""))
    node.appendChild(x)

def addWord(doc, node, word, freq, dur):
    #note freq, dur should be strings, and may include multiple comma-separated values
    pitch = doc.createElement("PITCH")
    pitch.setAttribute("FREQ", freq)
    duration = doc.createElement("DURATION")
    duration.setAttribute("SECONDS", dur)
    text = doc.createTextNode(word)
    duration.appendChild(text)
    pitch.appendChild(duration)
    node.appendChild(pitch)

argv = []
for i in range(len(sys.argv)):
    if sys.argv[i][:2] == "--":
        if "--base=" in sys.argv[i].lower():
            BASE = int(sys.argv[i][7:])
            print "BASE frequency set to:", BASE
        if "--scale=" in sys.argv[i].lower():
            SCALE = int(sys.argv[i][8:])
            print "SCALE set to:", SCALE
    else:
        argv.append(sys.argv[i])
sys.argv = argv

if len(sys.argv) < 2:
    print "text2fest.py markupfile.txt festfile.xml [start end]"
    print "start, end are sentence indexes"
    exit()

fin = sys.argv[1]
fout = sys.argv[2]
start = None
if len(sys.argv) > 3:
    start = int(sys.argv[3])
    end = int(sys.argv[4])

xdoc = minidom.Document()
xbody = xdoc.createElement("LIBRETTO")
xbody.setAttribute("DURATIONSMULTIPLY", "true")
xdoc.appendChild(xbody)

f = open(fin)
s = f.read()
f.close()
if s[0] == "{":
    a, s = s.split("}")
    a = a[1:].split(";")
    for e in a:
        key, val = e.split("=")
        if key.upper() == "BASE":
            BASE = int(val)
        if key.upper() == "SCALE":
            SCALE = int(val)

print "BASE:", BASE
print "SCALE:", SCALE

s = s.replace("?",".")
s = s.replace("!", ".")
s = s.replace("\n", " ")
r = s.split(". ")

print "R:", r

if FIXBEGINNING:
    addWord(xdoc, xbody, "oh", "50,40", "0.1")
    addRest(xdoc, xbody, 1.0)

if start != None:
    r = r[start-1:end]

for line in r:
    dur = 1.0
    line = line.strip()
    if line == "":
        continue
    print "---->", line
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

    for ix in each(data):                                   #then compute fend's
        word, syls, freqs, durs = data[ix]
        for j in each(freqs):                               #for each syllable
            f = freqs[j]
            nxt = None
            if len(f) < 2:
                if j < len(freqs) - 1:                      #interpolate to next fbeg in next syllable
                    nxt = freqs[j+1][0]
                elif ix < len(data) - 1:
                    nxt = data[ix+1][2][0][0]                 #interpolate to next fbeg in next word
                if nxt:
                    interp = (f[0] * 2 + nxt) / 3.0 - DROP  #yes that's how we roll
                    f.append(interp)
                else:                                       #end of story
                    f.append(f[0] - BIGDROP)

    for word, syls, freqs, durs in data:
        print word, "syls:", syls, "freqs:", freqs, "durs:", durs
        if word == "|":
            addRest(xdoc, xbody, durs[0])
        else:
            s = ""
            for i in range(syls):
                fbeg, fend = freqs.pop(0)
                s  += "," + str(fbeg) + "," + str(fend)
            freqatt = s[1:]
            s = ""
            for i in range(syls):
                if len(durs):
                    dur = durs.pop(0)
                s  += "," + str(dur)
            duratt = s[1:]
            addWord(xdoc, xbody, word, freqatt, duratt)
    addRest(xdoc, xbody, SENTENCEPAUSE)


out = xdoc.toprettyxml()
f = open(fout, 'w')
f.write(out)
f.close()
