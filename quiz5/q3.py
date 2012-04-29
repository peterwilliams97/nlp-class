from __future__ import division
#  -*- coding: latin-1 -*-

"""
President/O Obama/PER met/O with/O former/O President/O George/PER H.W./PER Bush/PER and/O former/O Florida/LOC Gov./O Jeb/PER Bush/PER in/O the/O Oval/LOC Office/LOC on/O Friday,/O joining/O in/O a/O bipartisan/O gathering/O in/O an/O election/O year./O 

Features
f1(c, d) = [c = LOCATION & isCapitalized(wi)]
f2(c, d) = [c = LOCATION & classOf(wi-1) = LOCATION]
f3(c, d) = [c = PERSON & isCapitalized(wi)]
f4(c, d) = [c = PERSON & classOf(wi-1) = PERSON]
f5(c, d) = [c = PERSON & wi-1 = "President" ]
"""
import re
from math import *

def capitalized(w):   
    return bool(re.search(r'^[A-Z].+$', w))
    

if False:    
    print capitalized('H.')
    exit()    

funcs = [
    lambda c,c1,w,w1: c == 'LOC' and capitalized(w), 
    lambda c,c1,w,w1: c == 'LOC' and c1 == 'LOC', 
    lambda c,c1,w,w1: c == 'PER' and capitalized(w),
    lambda c,c1,w,w1: c == 'PER' and c1 == 'PER',
    lambda c,c1,w,w1: c == 'PER' and w1 == 'President',    
]
 
text0 = 'President/O Obama/PER met/O with/O former/O President/O George/PER H.W./PER Bush/PER and/O former/O Florida/LOC Gov./O Jeb/PER Bush/PER in/O the/O Oval/LOC Office/LOC on/O Friday,/O joining/O in/O a/O bipartisan/O gathering/O in/O an/O election/O year./O'

text = 'President/O Obama/PER met/O with/O former/O President/O George/PER H.W./PER Bush/PER and/O former/O Florida/LOC Gov./O Jeb/PER Bush/PER in/O the/O Oval/LOC Office/LOC on/O Friday,/O joining/O in/O a/O bipartisan/O gathering/O in/O an/O election/O year./O'

assert(text == text0)

pairs = text.split()
word_class = [p.split('/') for p in pairs]
 
def emperical_expectation(f):
    c1, w1 = '',''
    expectation = 0
    for w,c in word_class:
        #print w,c, int(f(c,c1,w,w1))
        expectation += int(f(c,c1,w,w1))
        c1,w1 = c,w
    return expectation
    
if False:
    e = emperical_expectation(funcs[2])
    print '%5d : %3d' % (2, e)
    exit()
    
for i,f in enumerate(funcs):
    print '%5d : %3d' % (i, emperical_expectation(f))
    
print 'Total : %3d' % sum([emperical_expectation(f) for f in funcs])    

    