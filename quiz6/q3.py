from __future__ import division
from math import *
"""
    Empirical count Ee(f) = SUM(f(c,d)) over c, d in observations
    Model expectation Em(f) = SUM(P(c,d)f(c,d)) over c in classes, d in data
"""
   
def v(l):
    return exp(l - (l**2)/2)
  
def E(lam):
    e = exp(lam)/(2.0 + exp(lam))  
    p = exp(-(lam**2)/2.0)
    return e * p,  p, e  
    
def E_(lam):
    p = exp(-(lam**2)/2.0)
    v = exp(lam) *p
    e = v/(2.0 + v) 
    
    return e , 0, 0    

answers = [3, 9, 3/4, 5/8]

print 0.8

for x in answers:
    post, prior, expect = E(log(x))
    print 'x=%5.2f E(x)=%5.2f =%5.2f*%5.2f' % (x, post, prior, expect)
