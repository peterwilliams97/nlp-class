from __future__ import division
#  -*- coding: latin-1 -*-

"""
                       GOLD PERSON GOLD other
    SYSTEM GUESS PERSON     15      4
    SYSTEM GUESS other      18      6
"""

tp = 15
fp = 4
fn = 18
tn = 6

recall = tp/(tp + fn)
precision = tp/(tp + fp)
f1 = 2.0/(1.0/recall + 1.0/precision)

print '   recall %.3f' % recall
print 'precision %.3f' % precision
print '       f1 %.3f' % f1
