#parse script file and produce version with requested part in bold
#convention: dialog begins with underscore,as in _thisone: blah
#non-dialog should be in italics

import sys, os

if len(sys.argv) < 4:
    print "parts.py script.txt charactername outfile.html"
    exit()

fn = sys.argv[1]

char = sys.argv[2].lower()
if char[0] != "_":
    char = "_" + char

fout = open(sys.argv[3], "w")
fout.write('<html>\n<body style="font-size:large">\n')

f = open(fn)
oldmode = "direction"
mode = "direction"
fout.write("<i>\n")
for line in f.readlines():
    line = line.strip()
    if not line: continue
    s = ""
    if line[:1] == '_':
        mode = "dialog"
        if mode != oldmode:
            s += "</i>\n<br/>\n"
        if line.lower().find(char) == 0:
            s += "<b>" + line[1:] + "</b><br/>\n"
        else:
            s += line[1:] + "<br/>\n"
    else:
        mode = "direction"
        if mode != oldmode:
            s += "<br/>\n<i>\n"
        s += line + "<br/>\n"
    fout.write(s)
    oldmode = mode

fout.write('</body>\n</html>\n')

f.close()
fout.close()
