import curses
from curses.ascii import isdigit 
from nltk.corpus import cmudict 

d = cmudict.dict() 

exc = {
    "sappy" : 2
}

def nsyl(word):
    if word.lower() in exc:
        return exc[word.lower()]
    if word.lower() in d:
        prons = [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]
        mx = -1
        for p in prons:
            if p > mx:
                mx = p
        return mx

if __name__ == "__main__":
    for i in ["it's", "probably", "aren't", "us", "sappy"]:
        print i, nsyl(i), d[i]
