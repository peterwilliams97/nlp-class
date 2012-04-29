from __future__ import division
from math import *

def sumlog(col):
    return sum([log(x) for x in col])

# Name positive negative    
# Attempt 1
text = ''' 
I	0.09	0.18
always	0.09	0.05
like	0.19	0.04
foreign	0.04	0.11
films	0.09	0.12 
'''

# Attempt 2
text = ''' 
I	0.13	0.29
always	0.08	0.06
like	0.19	0.03
foreign	0.07	0.21
films	0.11	0.14
'''

lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
text_rows = [[x for x in ln.split() if x] for ln in lines]
rows = [(title, float(pos), float(neg)) for title,pos,neg in text_rows]
rows = [(t,p,n,log(p),log(n),log(p)-log(n)) for t,p,n in rows]   
cols = zip(*rows)

summary = tuple(['Total', 0, 0, sumlog(cols[1]), sumlog(cols[2]), 
    sumlog(cols[1])-sumlog(cols[2])])
all_rows = rows + [summary]

print '%10s %4s %4s %6s %6s %6s' % ('word', 'pos', 'neg', 'log(p)', 'log(n)', 'log(p)-log(n)') 
for r in all_rows:
    print '%10s %.2f %.2f %6.2f %6.2f %6.2f' % r
    
 
   