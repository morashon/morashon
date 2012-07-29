#!/usr/bin/python
#parse an rg (rosegarden) xml (gunzipped .rg) file, extract lyrics and notes
#only deals with the first segment it finds so...

import sys, os
from xml.dom import minidom

ADDNOTEATEND = True             #to avoid the barf effect

def tick2tempo(tempos, t):
    if t >= tempos[-1][0]:
        return tempos[-1][1]
    for i in range(len(tempos)-1):
        tick, bpm, target = tempos[i]
        ntick, nbpm, ignore = tempos[i+1]
        if t >= tick and t < ntick:
            if target == None:
                return bpm
            if target > 0:
                nbpm = target
            tot = float(ntick - tick)
            f1 = (ntick - t) / tot
            f2 = (t - tick) / tot
            return bpm * f1 + nbpm * f2

def dur2sec(tempos, t, d):
    bpm1 = tick2tempo(tempos, t)
    bpm2 = tick2tempo(tempos, t+d)
    bpm = (bpm1 + bpm2) * 0.5
    tpm = bpm * 960
    tps = tpm / 60.0
    spt = 1.0 / tps
##    print "bpm1:", bpm1, "bpm2:", bpm2, "bpm:", bpm, "t:", t, "d:", d, "tpm:", tpm, "tps:", tps, "spt:", spt, "return:", d*spt
    return d * spt

def getProp(node, prop, typ):
    props = node.getElementsByTagName("property")
    for p in props:
        if p.getAttribute("name") == prop:
            return p.getAttribute(typ)

midiNotes = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
def midi2note(n):
    note = n % 12
    octave = n / 12
    print "note:", note, "octave:", octave
    n = midiNotes[note] + str(octave)
    return n

def makeRest(xml, song, dur):
    rest = xml.createElement("REST")
    rest.setAttribute("BEATS", str(dur))
    text = xml.createTextNode(" ")
    rest.appendChild(text)
    song.appendChild(rest)
    return rest
    
def makeNote(xml, song, text, note, dur):
    pitch = xml.createElement("PITCH")
    pitch.setAttribute("NOTE", midi2note(note))
    duration = xml.createElement("DURATION")
    duration.setAttribute("BEATS", str(dur))
    text = xml.createTextNode(text)
    duration.appendChild(text)
    pitch.appendChild(duration)
    song.appendChild(pitch)
    return pitch, duration

def main(x, xmlout, trackname, segIndex, transpose):
    song = xmlout.createElement("SINGING")
    song.setAttribute("BPM", "63.5677")
##    makeNote(xmlout, song, "No", 48, 0.5)
##    makeNote(xmlout, song, "No", 45, 0.25)
##    makeRest(xmlout, song, 0.25)
##    makeNote(xmlout, song, "No", 41, 0.5)

    segs = x.getElementsByTagName("segment")
    print len(segs), "segments found"
    if trackname:
        tracks = x.getElementsByTagName("track")
        for track in tracks:
            if track.getAttribute("label") == trackname:
                track = int(track.getAttribute("id"))
                print "found track with name", trackname, ":", track
                break
        found = False
        print "searching for segment:", segIndex
        for seg in segs:
            if int(seg.getAttribute("track")) == track:
                if type(segIndex)==type(0):
                    if segIndex == 0:
                        found = True
                        break
                    segIndex -= 1
                else:
                    if seg.getAttribute("label") == segIndex:
                        found = True
                        break
        if not found:
            print "requested segment not found"
            return
    else:
        seg = segs[0]
    track = int(seg.getAttribute("track"))
    tick = int(seg.getAttribute("start"))
    print "parsing track", track, "starts at tick", tick


    print "------------TEMPO-------------"
    bpm = float(x.getElementsByTagName("composition")[0].getAttribute("defaultTempo"))
    print "starting tempo:", bpm
    events = x.getElementsByTagName("tempo")
    tempos = [(0, bpm, None)]
    for ev in events:
        tick = int(ev.getAttribute("time"))
        bph = int(ev.getAttribute("bph"))
        bpm = bph/60.0
        target = None
        if ev.hasAttribute("target"):
            target = int(ev.getAttribute("target"))
        tempos.append((tick, bpm, None if target == None else 0 if target == 0 else target / 100000.0))
        print "new tempo at tick", tick, "bpm:", bpm,
        if target == None:
            print
        else:
            if (target != 0):
                print "ramps to:", target / 100000.0
            else:
                print "ramps to next change"

    print "-------------------------"
    tick = int(seg.getAttribute("start"))
    starttick = tick
    node = seg.firstChild
    lyric = ""
    partdur = 0
    prevdur = None
    totdur = 0
    prevnote = None
    prevrest = None
    prevtype = None
    while node:
        if node.localName in ("event", "chord"):
            if node.localName == "chord":
                events = node.getElementsByTagName("event")
            else:
                events = [node]
            dur = None
            for ev in events:
                typ = ev.getAttribute("type")
                if typ == "text":
                    lyric = getProp(ev, "text", "string")
##                    print "lyric syllable at beat", tick / 960.0, "is: ------------------------------------", lyric
                if typ in ("rest", "note"):
                    if dur:
                        print "********** Problem -- you got multiple notes or rests. Using the first one"
                        continue
                    dur = int(ev.getAttribute("duration"))
                    print "++++++++++++++++++++++++"
                    print "tempo at beat", tick / 960.0, "is:", tick2tempo(tempos, tick)
                    dursec = dur2sec(tempos, tick, dur)
                    totdur += dursec
                    print "duration:", partdur + dursec, "seconds"
                    if typ == "note":

                        tie = getProp(ev, "tiedforward", "bool") == "true"
                        #if tied forward, keep duration for later
                        if tie:
                            partdur += dursec
                            print "================================================= this note is tied fwd:", partdur
                        else:
                            #if no lyric, assume multi-syllable
                            if lyric == "":
                                if prevnote:
                                    note = int(getProp(ev, "pitch", "int"))
                                    temp = prevnote.getAttribute("NOTE")
                                    temp += "," + str(midi2note(note+transpose))
                                    prevnote.setAttribute("NOTE", temp)
                                    temp = prevdur.getAttribute("BEATS")
                                    temp += "," + str(partdur + dursec)
                                    partdur = 0
                                    prevdur.setAttribute("BEATS", temp)
                            else:
                                note = int(getProp(ev, "pitch", "int"))
                                print "note:", note
                                print "lyric:", lyric
                                prevnote, prevdur = makeNote(xmlout, song, lyric, note+transpose, partdur + dursec)
                                lyric = ""
                                partdur = 0
                                prevtype = "note"
                    else:
                        print "rest"
                        if prevtype == "rest":
                            temp = float(prevrest.getAttribute("BEATS"))
                            temp += dursec
                            prevrest.setAttribute("BEATS", str(temp))
                        else:
                            prevrest = makeRest(xmlout, song, dursec)
                            prevtype = "rest"
                    last = tick
            if dur:
                tick += dur
        node = node.nextSibling

    print
    print "total duration:", (tick-starttick) / 960.0, "beats,", totdur, "seconds"

    if ADDNOTEATEND:
        makeRest(xmlout, song, 4.0)
        makeNote(xmlout, song, "ae", 30, 0.1)
        
    xmlout.appendChild(song)
    return xmlout

if len(sys.argv) < 3:
    print "rg2fest.py yoursong.rg output_festival[.xml] [trackname [segment [transpose]]]"
    print "no trackname? use first segment I find"
    print "I WILL OVERWRITE your rg.xml file!"
    exit()

cmd = "gunzip -c " + sys.argv[1] + " > " + sys.argv[1] + ".xml"
print cmd
os.system(cmd)
x = minidom.parse(sys.argv[1] + ".xml")
trackname = None
seg = 0
transpose = 0
segs = 1 if trackname else 100000

if len(sys.argv) > 3:
    trackname = sys.argv[3]
if len(sys.argv) > 4:
    seg = sys.argv[4]
    try:
        seg = int(seg) - 1
    except:
        print "seg label:", seg
    segs = 1
if len(sys.argv) > 5:
    transpose = int(sys.argv[5])

base = sys.argv[2]
if base[-4:].lower() == ".xml":
    base = base[:-4]

if type(seg) == type(0):
    rng = range(seg, seg + segs)
else:
    rng = [seg]
for i in rng:
    print "---i:", i, seg, segs
    y = minidom.Document()
    xml = main(x, y, trackname, i, transpose)
    if xml:
        out = xml.toprettyxml()
        if type(i) == type(0):
            fn = base + "." + str(i+1) + ".xml"
        else:
            fn = base + ".xml"
        f = open(fn, 'w')
        f.write(out)
        f.close()
    else:
        break

cmd = "rm " + sys.argv[1] + ".xml"
print cmd
os.system(cmd)
