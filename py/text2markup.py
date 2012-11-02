#this script attempts a rough first pass at cleaning up dialogue extracted from the script in preparation for markup

import sys, os
from findPy import *

try:
    fin = sys.argv[1]
    fout = sys.argv[2]
except:
    print "text2markup.py infile outfile"
    exit()
ftmp = fin + "__"

cmd = "python " + findPy("plainAscii.py") + " " + fin + " " + ftmp
print cmd
os.system(cmd)

f = open(ftmp)
s = f.read()
f.close()

cmd = "rm " + ftmp
print cmd
os.system(cmd)

f = open(fout, "w")
print >> f, "{include:../actors.txt}"
ix = 0
line = ""
while ix < len(s):
    c = s[ix]
    ix += 1
    if c == '"':
        continue
    if c == "'":
        if not (s[ix-2:ix-1].isalpha() and s[ix:ix+1].isalpha()):       #leave apostrophe, ignore single quotes with whitespace on either side
            continue
    if c == ",":
        c = " |"
    if c == ";":
        c = "."
    if c == ":":
        c = "."
    if c == "-":
        if s[ix:ix+1] == "-":
            c = "|"
            while s[ix:ix+1] == "-":
                ix += 1
        else:
            c = " "
    line += c
    if c in ("\n", ".", "!", "?", ":"):
        line = line.strip()
        if "(" in line:
            i = line.find("(")
            j = line.find(")")
            line = line[:i] + line[j+1:]
            line = line.strip()
        if line.find("_") == 0:
            line = "{" + line[1:-1] + "}"
            print >> f
        else:
            line = line.replace("Thisone", "Tea sewn")
            line = line.replace("Annai", "An I")
            line = line.replace("Morashon", "More eh shun")
        if line and len(line) > 1:
            print >> f, line
        line = ""

f.close()
