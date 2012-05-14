s1 = 'We all live in that yellow submarine'
s2 = 'The yellow mustard in that submarine sandwich was not yellow'

s1 = 'To be or not to be'
s2 = 'To think and therefore to be'

w1 = set(s1.lower().split())
w2 = set(s2.lower().split())

intersection = w1 & w2
union = w1 | w2

print s1
print s2
print 'w1 =', sorted(w1)
print 'w2 =', sorted(w2)
print 'intersection =', sorted(intersection)
print 'union =', sorted(union)
print 'Jacard = %d/%d' % (len(intersection), len(union))
