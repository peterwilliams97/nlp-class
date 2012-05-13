s1 = 'We all live in that yellow submarine'
s2 = 'The yellow mustard in that submarine sandwich was not yellow'

w1 = set(s1.split())
w2 = set(s2.split())

intersection = w1 & w2
union = w1 | w2

print 'Jacard =%d/%d' % (len(intersection), len(union))
print intersection
print union

