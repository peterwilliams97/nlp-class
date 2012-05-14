from __future__ import division
import math

def log10(x): return math.log(x,10)

N = 806791 
doc_count = 25235   
count = 17

idf = log10(N) - log10(doc_count)
tf = 1.0 + log10(count)
tfidf = tf * idf

print 'tfidf = %.3f' % tfidf

