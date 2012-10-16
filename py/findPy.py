import os
def findPy(p):
    for e in ("./", "../", "../../"):
        for f in ("", "py/"):
            if os.path.exists(e + f + p):
                return e + f + p
    print "cannot find", p, "anywhere"
    exit()
