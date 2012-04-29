from __future__ import division
"""
Empirical count Ee(f) = SUM(f(c,d)) c in C, d in D
Model expectation Em(f) SUM(P(c,d)f(c,d)) c in C, d in D

"""

from math import *


classes = ('V', 'N', 'O')
data = ['V', 'V', 'V', 'N', 'N']

def s(x): return '%4.2f' % x

def f(c, d):
    return int(d=='N' and c==d)
    
def P(c,d,lam):
    num = exp(lam*f(c,d))
    den = sum([exp(lam*f(c1,d)) for c1 in classes])
    p = num/den
    print '>>', s(lam), c, d, f(c,d), s(num), s(den), s(p), s(log(p))
    return p
    
Ee = sum([f(c,d) for c in classes for d in data])

def Em(lam):
    return sum([f(c,d)*P(c,d,lam) for c in classes for d in data])
    
  
answers = [4/3, 3/5, 2, 15]

print 'Ee = %f' % Ee  
for lam_e in sorted(answers):
    print '-' * 80
    print '%5.2f %f ' % (lam_e, Em(log(lam_e)))
exit()
    
def logP(lam):
    return sum([log(P(c,d,lam)) for c in classes for d in data])

def Plog(lam_e):
    lam = log(lam_e)
    return logP(lam_e)
    
#print logP(0.1)    

answers = [4/3, 2, 15, 2/3]

for lam_e in answers:
    print '-' * 80
    print '%5.2f %f ' % (lam_e, Plog(lam_e))
