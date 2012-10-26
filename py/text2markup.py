#this script attempts a rough first pass at cleaning up dialogue extracted from the script in preparation for markup

import sys, os

fin = sys.argv[1]
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

##f = open(fout, "w")

ix = 0
line = ""
while ix < len(s):
    c = s[ix]
##    print hex(ord(c))
    ix += 1
    if c in ("\n", ".", "!", "?", ":"):
        line = line.strip()
        if line:
            print line
        line = ""
    else:
        line += c

##f.close()
