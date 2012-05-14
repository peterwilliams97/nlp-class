from __future__ import division

text = 'N N N R R N R R N R R N R'
text = 'N R R N N N R R N N N N N N R'
results = [p == 'R' for p in text.split()]
N = len(results)

def get_precision(n):
    return sum(results[:n])/n
   
precisions = [get_precision(n) for n in range(1,N+1)]

relevant_precisions = [precisions[i] for i in range(N) if results[i]]
average_precision = sum(relevant_precisions)/len(relevant_precisions)

print 'Average precsion = %.3f' % average_precision
    

