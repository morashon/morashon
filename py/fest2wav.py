#!/usr/bin/python
#simple (hah) script to invoke festival on a festive xml file and output a .wav

import sys, os
from xml.dom import minidom

cleanup = []
if len(sys.argv) < 3:
    print "fest2wav festival.xml output.wav [voice]"
    exit()

fout = sys.argv[2]
voice = None
scm = ""
if len(sys.argv) > 3:
    voice = sys.argv[3]
    scm += "(voice_" + voice + ")\n"

fxml = sys.argv[1]
xml = minidom.parse(fxml)
if len(xml.getElementsByTagName("SINGING")) > 0:
    XMLMODE = "singing"
elif len(xml.getElementsByTagName("LIBRETTO")) > 0:
    XMLMODE = "libretto"
else:
    if len(xml.getElementsByTagName("SABLE")) > 0:
        XMLMODE = "sable"
        xmlspk = xml.getElementsByTagName("SPEAKER")
        if len(xmlspk):
            spkr = xmlspk[0].getAttribute("NAME")
            if voice and spkr != voice:
                print "changing SABLE speaker from", spkr, "to", voice
                xmlspk[0].setAttribute("NAME", voice)
                fxml = "_fest2wavtemp_.xml"
                cleanup.append(fxml)
                out = xml.toxml()
                f = open(fxml, "w")
                f.write(out)
                f.close()
        else:
            print "cannot change speaker, no SPEAKER tag"
    else:
        print "unknown festival XML mode -- we support SINGING and SABLE folks"
print "XMLMODE:", XMLMODE

WINE = False
if voice and voice.find("ogi_") == 0:
    WINE = True

if WINE:
    FESTIVAL = "wine cmd /C c:\\\\cmd_c c:\\\\festival\\\\src\\\\main\\\\festival.exe"
else:
    FESTIVAL = "~/src/festival/festlibretto2.1/festival/src/main/festival"
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
cleanup.append("_fest2wav_.scm")

if os.path.exists("tts_file_1.wav"):
    cmd = "rm tts_file_1.wav"       #yea that's how I roll
    os.system(cmd)

if WINE:
    cmd = "rm ~/.wine/drive_c/tts_file_*.wav"
    print cmd
    os.system(cmd)
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
    cmd = "cp ~/.wine/drive_c/tts_file_*.wav ."
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
        cleanup.append(tts)
    cmd += " " + fout
    print cmd
    os.system(cmd)

else:
    cmd = "mv tts_file_1.wav " + fout
    print cmd
    os.system(cmd)

for f in cleanup:
    cmd = "rm " + f
    print cmd
    os.system(cmd)
