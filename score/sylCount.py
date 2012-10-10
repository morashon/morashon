import curses
from curses.ascii import isdigit 
import nltk 
from nltk.corpus import cmudict 

d = cmudict.dict() 

def nsyl(word):
    if word.lower() in d:
        prons = [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]
        mx = -1
        for p in prons:
            if p > mx:
                mx = p
        return p

if __name__ == "__main__":
    for i in ["it's", "something", "wonderful", "spectacular"]:
        print i, nsyl(i), d[i]
