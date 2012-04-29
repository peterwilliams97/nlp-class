from __future__ import division
from math import *
"""
    Empirical count Ee(f) = SUM(f(c,d)) over c, d in observations
    Model expectation Em(f) = SUM(P(c,d)f(c,d)) over c in classes, d in data
"""
   
# Calculations    
def Ee(observations, f):
    return sum([f(c,d) for (d,c) in observations])/len(observations)
    
def Em(data, classes, f, lam):
    def P(c, d):
        num = exp(lam*f(c,d))
        den = sum([exp(lam*f(c1,d)) for c1 in classes])
        return num/den
    return sum([f(c,d)*P(c,d) for d in data for c in classes])
    
def solve(data, classes, observations, f, answers):    
    print 'Ee = %f' % Ee(observations, f)  
    for x in answers:
        em = Em(data, classes, f, log(x))
        print 'Em = %f X=%5.2f' % (em, x)
        
# Given information
_classes = ('V', 'N', 'O')
_data = ['breeze']
_observations = [
    ('breeze', 'V'), 
    ('breeze', 'V'), 
    ('breeze', 'V'), 
    ('breeze', 'N'),
    ('breeze', 'N'),
    ]

def _f(c, d):
    return int(c=='N')

_answers = [4/3, 3/5, 2, 15]        

solve(_data, _classes, _observations, _f, _answers)    
