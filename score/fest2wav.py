#!/usr/bin/python
#simple (hah) script to invoke festival on a festive xml file and output a .wav

import sys, os

if len(sys.argv) < 3:
    print "fest2wav festival.xml output.wav [voice]"
    exit()

fxml = sys.argv[1]
fout = sys.argv[2]
voice = None
scm = ""
if len(sys.argv) > 3:
    voice = sys.argv[3]
    scm += "(voice_" + voice + ")\n"

WINE = False
if voice and voice.find("ogi_") == 0:
    WINE = True

if WINE:
    FESTIVAL = "wine cmd /C c:\\\\cmd_c c:\\\\festival\\\\src\\\\main\\\\festival.exe"
else:
    FESTIVAL = "festival"
print "WINE:", WINE

scm += """
(define (do_nothing utt) utt)
(set! tts_hooks (list utt.synth do_nothing))
(save_waves_during_tts)
(tts "FESTIVAL.XML" "singing")
"""

f = open("_fest2wav_.scm", "w")
f.write(scm.replace("FESTIVAL.XML", fxml))
f.close()

if os.path.exists("tts_file_1.wav"):
    cmd = "rm tts_file_1.wav"       #yea that's how I roll
    os.system(cmd)

if WINE:
    cmd = "cp _fest2wav_.scm ~/.wine/drive_c"
    print cmd
    os.system(cmd)
    cmd = "cp " + fxml + " ~/.wine/drive_c"
    print cmd
    os.system(cmd)
cmd = FESTIVAL + " -b _fest2wav_.scm"
print cmd
os.system(cmd)
if WINE:
    cmd = "cp ~/.wine/drive_c/tts_file_1.wav ."
    print cmd
    os.system(cmd)

cmd = "mv tts_file_1.wav " + fout
print cmd
os.system(cmd)

cmd = "rm _fest2wav_.scm"
print cmd
##os.system(cmd)
