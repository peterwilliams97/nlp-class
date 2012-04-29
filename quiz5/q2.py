from __future__ import division
#  -*- coding: latin-1 -*-

"""
 P(c|d,?) = expS?ifi(c,d)/SexpS?ifi(c',d). 
P(PERSON | by Goéric) =
P(LOCATION | by Goéric) =
P(DRUG | by Goéric) =

Weight	Feature
 1.5	f1(c, d) = [c = LOCATION & wi-1 = in & isCapitalized(wi)]
-0.5	f2(c, d) = [c = LOCATION & hasAccentedLatinChar(wi)]
 0.7	f3(c, d) = [c = DRUG & ends(wi, c)]
"""
import re
from math import *

LOCATION,PERSON,DRUG = 0,1,2
CLASSES = [PERSON,LOCATION,DRUG]
CLASS_NAMES = {LOCATION:'LOCATION', PERSON:'PERSON', DRUG:'DRUG'}

def accented(w):
    return 'é' in w

def capitalized(w):    
    return bool(re.search(r'^[A-Z][^A-Z]*$', w))

# Attempt 1    
lamb_funcs = [
    (1.5,  lambda c,d,i: c == LOCATION and d[i-1] == 'in' and capitalized(d[i])), 
    (-0.5, lambda c,d,i: c == LOCATION and accented(d[i])), 
    ( 0.7, lambda c,d,i: c == DRUG and d[i][-1].lower() == 'c') 
]

# Attempt 2 
lamb_funcs = [
    (1.8,  lambda c,d,i: c == LOCATION and d[i-1] == 'in' and capitalized(d[i])), 
    (-0.6, lambda c,d,i: c == LOCATION and accented(d[i])), 
    ( 0.3, lambda c,d,i: c == DRUG and d[i][-1].lower() == 'c') 
]
 
def pc(c, d, i):
    return exp(sum([l*int(f(c,d,i)) for l,f in lamb_funcs]))
    
def p(c, d, i):
    return pc(c, d, i)/sum([pc(c1,d, i) for c1 in CLASSES])    
    
d = 'by Goéric'.split()
i = 1

for c in CLASSES:
    print '%20s : %.2f' % (CLASS_NAMES[c], p(c,d,i))
    