#!/usr/bin/python

#simple script to invoke festival on a festive xml file and output a .wav

import sys, os
if len(sys.argv) < 3:
    print "fest2wav festival.xml output.wav"
    exit()

fxml = sys.argv[1]
fout = sys.argv[2]

scm = """
(define (do_nothing utt) utt)
(set! tts_hooks (list utt.synth do_nothing))
(save_waves_during_tts)
(tts "FESTIVAL.XML" "singing")
"""

f = open("fest2wav.scm", "w")
f.write(scm.replace("FESTIVAL.XML", fxml))
f.close()

if os.path.exists("tts_file_1.wav"):
    cmd = "rm tts_file_1.wav"       #yea that's how I roll
    os.system(cmd)

cmd = "festival -b fest2wav.scm"
os.system(cmd)

cmd = "mv tts_file_1.wav " + fout
os.system(cmd)

cmd = "rm fest2wav.scm"
os.system(cmd)
