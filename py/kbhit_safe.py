#reconstitute some old magic

import sys, select

def kbhit():
    r = select.select([sys.stdin], [], [], 0.01)
    return len(r[0]) > 0

if __name__ == "__main__":
    import time
    while not kbhit():
        print "doing something -- hit <enter> to quit"
        time.sleep(0.3)
