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

#Attempt 1   
text = ''' 
 	"good"	"poor"	"great"	(class)
d1.	3	0	3	pos
d2.	0	1	2	pos
d3.	1	3	0	neg
d4.	1	5	2	neg
d5.	0	2	0	neg 
'''

#Attempt 1   
text = ''' 
 	"good"	"poor"	"great"	(class)
d1.	3	0	3	pos
d2.	0	1	2	pos
d3.	1	3	0	neg
d4.	1	5	2	neg
d5.	0	2	0	neg 
'''

title('text')
print text

lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
rows = [get_words(ln) for ln in lines]

vals = rows[0][:-1]
vals = [v.strip('"') for v in vals] 
title('vals')
print '   ', vals
data = [(r[-1], r[1:-1]) for r in rows[1:]]
title('data')
for d in sorted(data): print d

prior = {}
for k,v in data:
    prior[k] = prior.get(k, 0) + 1.0/len(data)
title('priors')    
for k in sorted(prior.keys()): 
    print k, prior[k]

keys = prior.keys() 
title('keys')
print keys

base_counts = [(k, [int(w) for w in v]) for k,v in data]
if False:
    title('base_counts')    
    for d in sorted(base_counts): 
        print d

def run_test(test_words, BINARY):        
    counts = {}
    for k,v in sorted(base_counts):
        #print ' ', k,v
        for i in range(len(v)):
            w = vals[i]
            cnt = counts.get(w, [0,0])
            #print '   ', i, w, cnt, 
            if BINARY:
                cnt[keys.index(k)] += 1 if v[i] else 0
            else:
                cnt[keys.index(k)] += v[i] 
            
            counts[w] = cnt
            #print ' =>', counts[w]

    title('counts')  
    for k in sorted(counts.keys()): 
        print '%20s : %s' % (k, counts[k])   
    
    CNT_N = sum([n for n,p in counts.values()])
    CNT_P = sum([p for n,p in counts.values()])
    V = len(counts.keys())
    print '%20s : %s' % ('CNT_N, CNT_P', [CNT_N, CNT_P]) 
    print '%20s : %s' % ('V', V) 
       
    def get_likelihood(w):
        n,p = counts.get(w, [0,0])
        if n+p == 0:
            return 0
        #print '  ', n, p
        dn = CNT_N + V
        dp = CNT_P + V    
        print '%20s %3d %3d -- %5.2f %5.2f : %5.2f' % (w, n,p, 
            (n+1)/dn, (p+1)/dp, ((n+1)/dn)/((p+1)/dp))
        return log((p+1)/dp) - log((n+1)/dn)
     
    title('posterior')
    
    if BINARY:
        test_words = set(test_words)
    test_words = sorted(test_words)    
    print test_words    

    r_prior = log(prior['pos']) - log(prior['neg'])  
    r_likelihood = [get_likelihood(w) for w in test_words]
    r_posterior = r_prior + sum(r_likelihood)
    print '%.2f = %.2f + %s' % (r_posterior, r_prior, F(r_likelihood))

    title('answer')
    print 'positive' if r_posterior > 0 else 'negative'    


print '\n\n' + '=' * 80        
test = 'A good, good plot and great characters, but poor acting.'    
title('test') 
print test
words = get_words(test)
title('test words') 
print words 

for b in False,True:    
    print '\n\n' + '=' * 80
    print 'BINARY=%s'% b
    print '=' * 80
    run_test(words, b) 

    

 
   