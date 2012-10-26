#this script attempts a rough first pass at cleaning up dialogue extracted from the script in preparation for markup

import sys, os

try:
    fin = sys.argv[1]
    fout = sys.argv[2]
except:
    print "text2markup.py infile outfile"
    exit()
ftmp = fin + "__"

cmd = "python plainAscii.py " + fin + " " + ftmp
print cmd
os.system(cmd)

f = open(ftmp)
s = f.read()
f.close()

cmd = "rm " + ftmp
print cmd
os.system(cmd)

f = open(fout, "w")

ix = 0
line = ""
while ix < len(s):
    c = s[ix]
##    print hex(ord(c))
    ix += 1
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
        if line:
            print >> f, line
        line = ""

f.close()
