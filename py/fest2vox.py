#!/usr/bin/python
"""

script to invoke fest2wav with combined voice descriptions such as ogi_as_diphone+ogi_tll_diphone

"""

import sys, os
from findPy import *
if len(sys.argv) < 2:
    print "fest2vox singingOrLibretto.xml [voice [timbre [outfilename]]]"
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
festxml = sys.argv[1]
voice = None
if len(sys.argv) > 2:
    voice = sys.argv[2]

timbre = 0
if len(sys.argv) > 3:
    timbre = float(sys.argv[3])

outf = None
if len(sys.argv) > 4:
    outf = sys.argv[4]

def makeCmd(*args):
    s = ""
    for arg in args:
        arg = str(arg)
        if " " in arg:
            arg = '"' + arg + '"'
        s += arg + " "
    return s.strip()

fest2wav = findPy("fest2wav.py")

if not outf:
    outf = festxml[:-4]
if outf[-4:].lower() == ".wav":
    outf = outf[:-4]
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
            cmd = makeCmd(fest2wav, festxml, fn, voice)
            cleanup.append(fn)
            print cmd
            os.system(cmd)
            cmd = makeCmd("sox", "-D", fn,  "-ef", "-r44100", "f_" + fn)     #convert to 44.1 in case differing sample rates
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
        cmd = makeCmd(fest2wav, festxml, outf + ".wav", voice)
        print cmd
        os.system(cmd)
else:
    cmd = makeCmd(fest2wav, festxml, outf + ".wav")
    print cmd
    os.system(cmd)

if timbre:
    cmd = makeCmd("mv", outf + ".wav", outf + "_.wav")
    cleanup.append(outf + "_.wav")
    print cmd
    os.system(cmd)
    cmd = makeCmd("sox", "-D", outf + "_.wav", outf + ".wav", "speed", str(2 ** (timbre/12.0)) ) 
    print cmd
    os.system(cmd)

print "clean up", len(cleanup), "files"
for f in cleanup:
    print "cleanup:", f
    cmd = "rm " + f
    os.system(cmd)
