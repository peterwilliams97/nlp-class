from __future__ import division
from math import *

def title(t):
    print t + ' ' + ('-' * (70 - len(t)))

def sumlog(col):
    return sum([log(x) for x in col])
    
def l2(x):
    return log(x,2)
    
def pointwise_mutual_info(near, term1, term2):
    return l2(near) - l2(term1) - l2(term2)
        
def PMI(n,t1,t2): 
    return pointwise_mutual_info(n, t1, t2)

# Attempt 1    
special_effects = 437    
good = 3124
bad = 1791
special_effects_near_good = 36
special_effects_near_bad = 18

# Attempt 2    
special_effects = 437    
good = 3124
bad = 1791
special_effects_near_good = 36
special_effects_near_bad = 18

pmi_good = PMI(special_effects_near_good, special_effects, good)
pmi_bad = PMI(special_effects_near_bad, special_effects, bad)

print 'pmi_good = %.1f' % pmi_good   
print 'pmi_bad  = %.1f' % pmi_bad 
print 'turney   = %.1f' % (pmi_good - pmi_bad)