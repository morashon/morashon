import curses
from curses.ascii import isdigit 
from nltk.corpus import cmudict 

d = cmudict.dict() 

def nsyl(word):
    if word.lower() in d:
        prons = [len(list(y for y in x if isdigit(y[-1]))) for x in d[word.lower()]]
        mn = 999
        for p in prons:
            if p < mn:
                mn = p
        return mn

if __name__ == "__main__":
    for i in ["it's", "something", "wonderful", "spectacular", "us"]:
        print i, nsyl(i), d[i]
