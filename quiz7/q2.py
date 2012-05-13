from __future__ import division
from math import *

N = 806791
text = '''
term	document frequency	Doc 1	Doc 2	Doc 3
car	18165	27	4	24
auto	6723	3	33	0
insurance	19241	0	39	29
best	25235	14	0	17
'''
lines = text.split('\n')
lines = [ln.strip() for ln in lines if ln.strip()]
words = [ln.split('\t') for ln in lines]
keys = words[0][1:]
W = len(keys)
data = {}
for wrd in words[1:]:
    row = [int(w) for w in wrd[1:]]
    data[wrd[0]] = dict([(keys[i],row[i]) for i in range(W)])

print '%20s : %s' % ('', '\t'.join(keys)  )  
for k,v in data.items():
    print '%20s : %s' % (k, '\t'.join([str(v[x]) for x in keys]))    


df = sum(v['Doc 3'] for v in data.values())   
idf = log(N, 10) - log(df, 10)
tf = 1.0 + log(data['best']['Doc 3'], 10)
tfidf = tf * idf  

print 'tfidf = %.3f' % tfidf
