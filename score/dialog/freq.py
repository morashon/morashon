#testing some frequency analysis code
import math
import matplotlib.mlab as mat

N = 128
P = 23.4
mul = (2 * math.pi) / P 
data = []
for i in range(N):
    val = math.sin(i * mul)
    data.append(val)
    print "%3d %+2.8f" % (i, val), "|", " " * int(52 + math.floor(val * 50 + 0.5)) + "."
##print data

print
print
spec = mat.specgram(data, NFFT=32, noverlap = 16)
print "X axis (times):", len(spec[2]), list(spec[2])
print "Y axis (freqs):", len(spec[1]), list(spec[1])
print "data:"
print
for i in range(len(spec[0])-1, -1, -1):
    s = "%3.3f" % (2.0 / spec[1][i]) if spec[1][i] else "DC "
    s = "%7s" % s
    print s, "|",
    for j in range(len(spec[2])):
        print "%1.4f" % spec[0][i][j],
    print
print "-" * (7 * (len(spec[2]) + 1) + 2)
print "times:  | ",
for j in range(len(spec[2])):
    print "%2.3f" % spec[2][j],
print
