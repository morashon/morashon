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
    print "rg2vox song.rg tracklabel segmentlabel [voice [timbre [outfilename]]]"
    print "pitch defaults to 0: -1 means sing a semi higher and pitch down; 12 = chipmunk effect"
    exit()

opts = []
argv = []
for i in range(len(sys.argv)):
    if sys.argv[i][:2] == "--":
        opts.append(sys.argv[i])
    else:
        argv.append(sys.argv[i])
sys.argv = argv

cleanup = []
song = sys.argv[1]
track = sys.argv[2]
seg = sys.argv[3]
voice = None
if len(sys.argv) > 4:
    voice = sys.argv[4]

timbre = 0
if len(sys.argv) > 5:
    timbre = int(sys.argv[5])

outf = None
if len(sys.argv) > 6:
    outf = sys.argv[6]

def makeCmd(*args):
    s = ""
    for arg in args:
        arg = str(arg)
        if " " in arg:
            arg = '"' + arg + '"'
        s += arg + " "
    return s.strip()

rg2fest = "./rg2fest.py"
if not os.path.exists(rg2fest):
    rg2fest = "../rg2fest.py"

fest2wav = "./fest2wav.py"
if not os.path.exists(fest2wav):
    fest2wav = "../fest2wav.py"

if timbre:
    args = [rg2fest, song, seg, track, seg, -timbre, str(2 ** (-timbre/12.0))] #yo dat be momma math
else:
    args = [rg2fest, song, seg, track, seg]
for opt in opts:
    args.insert(1, opt)
cmd = makeCmd(*args)

cleanup.append(seg + ".xml")
print cmd
os.system(cmd)

if not outf:
    outf = seg
if voice:
    if '+' in voice:
        voices = voice.split('+')
        soxargs = ["sox", "-D", "-m"]
        for voice in voices:
            if '/' in voice:
                voice, factor = voice.split('/')
                factor = str(1.0 / float(factor))
            else:
                factor = str(1.0 / len(voices))
            fn = outf + '_' + voice + ".wav"
            cmd = makeCmd(fest2wav, seg + ".xml", fn, voice)
            cleanup.append(fn)
            print cmd
            os.system(cmd)
            cmd = makeCmd("sox","-D", fn,  "-ef", "-r44100", "f_" + fn)     #convert to 44.1 in case differing sample rates
            cleanup.append("f_" + fn)
            print cmd
            os.system(cmd)
            soxargs.append("-v")
            soxargs.append(factor)
            soxargs.append("f_" + fn)
        soxargs.append(outf + ".wav")
        print soxargs
        cmd = makeCmd(*soxargs)
        print cmd
        os.system(cmd)
    else:
        cmd = makeCmd(fest2wav, seg + ".xml", outf + ".wav", voice)
        print cmd
        os.system(cmd)
else:
    cmd = makeCmd(fest2wav, seg + ".xml", outf + ".wav")
    print cmd
    os.system(cmd)

if timbre:
    cmd = makeCmd("mv", outf + ".wav", outf + "_.wav")
    cleanup.append(outf + "_.wav")
    print cmd
    os.system(cmd)
    cmd = makeCmd("sox", outf + "_.wav", outf + ".wav", "speed", str(2 ** (timbre/12.0)) ) 
    print cmd
    os.system(cmd)

lst = os.listdir(".")
found = False
for fil in lst:
    if not fil[-4:].lower() == ".wav":
        continue
    if fil.find("conv-" + outf + "-") == 0:
        found = True
        print "Found what looks like the appropriate rosegarden sample wav:", fil
        cmd = makeCmd("sox", "-D", outf + ".wav", "-ef", "-r44100", fil)
        cleanup.append(outf + ".wav")
        print cmd
        os.system(cmd)
        break

if not found and os.path.exists(os.getenv("HOME") + "/rosegarden"):
    lst = os.listdir(os.getenv("HOME") + "/rosegarden")
    for fil in lst:
        if not fil[-4:].lower() == ".wav":
            continue
        if fil.find("conv-" + outf + "-") == 0:
            found = True
            break

    if found:
        print "Tricky Rosegarden! It put the file in ~/rosegarden.  Move it into the current directory, restart Rosegarden, and run this script again."
if not found:
    print "Couldn't find a suitable rosegarden file.  Import " + outf + ".wav into your project."

print "clean up", len(cleanup), "files"
for f in cleanup:
    print "cleanup:", f
    cmd = "rm " + f
##    os.system(cmd)
