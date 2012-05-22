from __future__ import division
import math

def log2(x):
    return math.log(x,2)


ppmi = 2.3219
sentences = 100000
stanford_university_university = 0.5
"""
ppmi = log(stanford_university/sentences)/((stanford/sentences)*(university/sentences))
(stanford_university*sentences)/(stanford*university) = 2.0 ** ppmi
(stanford_university/university) * (sentences/stanford) = 2.0 ** ppmi
stanford = (stanford_university/university) * sentences *  2.0 ** -ppmi
"""
stanford = stanford_university_university * sentences *  2.0 ** -ppmi

print 'Stanford = %.2f = %d' % (stanford, int(stanford))








