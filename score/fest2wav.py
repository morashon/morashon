#!/usr/bin/python
#simple (hah) script to invoke festival on a festive xml file and output a .wav

import sys, os
from xml.dom import minidom

if len(sys.argv) < 3:
    print "fest2wav festival.xml output.wav [voice]"
    exit()

fxml = sys.argv[1]
xml = minidom.parse(fxml)
if len(xml.getElementsByTagName("SINGING")) > 0:
    XMLMODE = "singing"
else:
    if len(xml.getElementsByTagName("SABLE")) > 0:
        XMLMODE = "sable"
    else:
        print "unknown festival XML mode -- we support SINGING and SABLE folks"
print "XMLMODE:", XMLMODE

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
(tts "FESTIVAL.XML" "XMLMODE")
"""

f = open("_fest2wav_.scm", "w")
f.write(scm.replace("FESTIVAL.XML", fxml).replace("XMLMODE", XMLMODE))
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

ttss = []
files = os.listdir('.')
for fi in files:
    if fi.find("tts_file_") == 0:
        ttss.append(fi)
ttss.sort()
if len(ttss) > 1:
    print "multiple tts files, combining", ttss
    cmd = "sox"
    for tts in ttss:
        cmd += " " + tts
    cmd += " " + fout
    print cmd
    os.system(cmd)
    for tts in ttss:
        cmd = "rm " + tts
        print cmd
        os.system(cmd)
else:
    cmd = "mv tts_file_1.wav " + fout
    print cmd
    os.system(cmd)

cmd = "rm _fest2wav_.scm"
print cmd
os.system(cmd)
