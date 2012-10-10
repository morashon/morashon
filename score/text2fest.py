"""
process marked up text to produce a festival-ready xml file (using LIBRETTO tag, which allows pitch for beg and end of each syllable)

Markup: tempo and intonation hold for each sentence.

examples:
_Annai: +20 7 Thisone, 3 will you 5 come 7 with us?
_Thisone: Come -30 7 where_2
_Annai: We're 7 starting a new 3 life. 7 Off 5 the 3 grid.  +15 Our 7 own 3 grid in fact.  It's something 7,3,3 wonderful.  5,7,3,3 Spectacular.

"""
import sys, os
from xml.dom import minidom

