from __future__ import division

# Attempt 1
# pos, neg
m = [59, 230]
f = [10, 270]

# Attempt 2
m = [26, 100]
f = [10, 130]

p_f_pos = f[0]/(sum(m) + sum(f))
print 'P(f,pos)=%.3f' % p_f_pos

p_pos = sum([x[0] for x in m,f])/sum([sum(x) for x in m,f])
#print 'P(pos)=%.3f' % p_pos

pcond_f_pos = p_f_pos/p_pos
print 'P(f|pos)=%.3f' % pcond_f_pos
