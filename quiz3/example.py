from __future__ import division
from math import *

def F(a):
    return str(['%.2f' % x for x in a]).replace("'", '')
    
def title(t):
    print t + ' ' + ('-' * (70 - len(t)))

def sumlog(col):
    return sum([log(x) for x in col])
    
def get_words(line):    
    return [x.rstrip(',') for x in line.split() if x]
    
# Name positive negative 

# Attempt 1   
text = ''' 
1.	fun, couple, love, love	comedy
2.	fast, furious, shoot	action
3.	couple, fly, fast, fun, fun	comedy
4.	furious, shoot, shoot, fun	action
5.	fly, fast, shoot, love	action 
'''

# Attempt 2   
text = ''' 
1.	fun, couple, love, love	comedy
2.	fast, furious, shoot	action
3.	couple, fly, fast, fun, fun	comedy
4.	furious, shoot, shoot, fun	action
5.	fly, fast, shoot, love	action
'''

text = text.strip()
title('text')
print text

lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
rows = [get_words(ln) for ln in lines]

data = [(r[-1], r[1:-1]) for r in rows]
title('data')
for d in sorted(data): print d

prior = {}
for k,v in data:
    prior[k] = prior.get(k, 0) + 1.0/len(data)
title('priors')    
for k in sorted(prior.keys()): 
    print k, prior[k]

keys = sorted(prior.keys()) 
title('keys')
print keys

counts = {}
for k,v in data:
    for w in v:
        cnt = counts.get(w, [0 for i in keys])
        cnt[keys.index(k)] += 1
        counts[w] = cnt
        
count_totals = [sum([cnt[keys.index(k)] for cnt in counts.values()])
                for k in keys] 
title('counts')    
for k in sorted(counts.keys()): 
    print '%20s : %s' % (k, counts[k])
print '%20s : %s' % ('Totals', count_totals)    

def get_likelihood(v):
    return [(v[i]+1)/(count_totals[i]+len(counts)) 
                for i in range(len(count_totals))]
   
likelihood = dict([(k, get_likelihood(v)) for k,v in counts.items()])
    
title('likelihood')    
for k in sorted(likelihood.keys()): 
    print '%20s : %s' % (k, F(likelihood[k])) 

def get_posterior(k, line):
    words = get_words(line)
    lk = [likelihood[w][keys.index(k)] for w in words]
    return log(prior[k]) + sumlog(lk)

#
#
#    
test = 'fun, couple, shoot, fast'    
title('test') 
print test

title('get_posterior')
posteriors = dict([(k, get_posterior(k, test)) for k in keys])
for k in keys: 
    words = get_words(test)
    llk = [log(likelihood[w][keys.index(k)]) for w in words]
    print '%20s : %.2f (%.2f: %s)' % (k, posteriors[k], log(prior[k]), F(llk))     
 
title('answer')    
print max(posteriors.keys(), key = lambda k: posteriors[k])

 
   