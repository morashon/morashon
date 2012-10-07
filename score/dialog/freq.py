#testing some frequency analysis code
import math

N = 64
P = 32
mul = (2 * math.pi) / P 
data = []
for i in range(N):
    val = math.sin(i * mul)
    print "%3d %+2.8f" % (i, val), "|", " " * int(52 + math.floor(val * 50 + 0.5)) + "."
