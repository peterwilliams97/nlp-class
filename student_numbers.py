from __future__ import division
import math, re
import numpy as NP
import matplotlib.pyplot as plt

summary = '''
Preregistered: ~70,000
Registered: 42,223
Watched at least 1 video: 24,287
Watched all videos: 4,030
Got a statement of achievement: 1,466

Total number of videos downloaded: 860,854

# of students submitting PS's and average scores
PS1 8425 3.8
PS2 4527 4.1
PS3 3721 3.1
PS4 2994 3.7
PS5 2529 3.2
PS6 2005 3.6
PS7 1911 2.9
PS8 1654 3.8

Programming Assignment statistics:

PA # sub Max Avg Std
PA1 Spamlord: Train 6042 16.00 11.61 4.34
PA1 Spamlord: Test 5989 8.00 4.92 1.35 
PA2 Autocorrect: Laplace Unigram Dev 3576 3.00 2.87 0.48
PA2 Autocorrect: Laplace Unigram Test 3560 3.00 2.93 0.34
PA2 Autocorrect: Laplace Bigram Dev 3543 3.00 2.89 0.46
PA2 Autocorrect: Laplace Bigram Test 3532 3.00 2.83 0.49
PA2 Autocorrect: Stupid Backoff Dev 3481 3.00 2.77 0.57
PA2 Autocorrect: Stupid Backoff Test 3467 3.00 2.66 0.60
PA2 Autocorrect: Custom Dev 3374 3.00 2.67 0.72 
PA2 Autocorrect: Custom Test 3367 3.00 2.51 0.71
PA3 Sentiment: Development All Words 3184 10.00 9.02 1.76
PA3 Sentiment: Testing All Words 3177 10.00 9.29 1.41
PA3 Sentiment: Dev without Stop Words 3173 10.00 8.96 1.51
PA3 Sentiment: Test Without Stop Words 3170 10.00 9.26 1.39 
PA4 NER: Development Set F-Score 2770 10.00 6.46 2.43
PA4 NER: Test Set F-Score 2755 10.00 7.07 2.61
PA5 PCFG: Development Set 2246 16.00 11.01 5.45
PA5 PCFG: Test Set 2221 8.00 2.29 2.29
PA6 Parsing: Development Set 1357 12.00 7.97 4.28
PA6 Parsing: Test Set 1324 12.00 8.71 3.40
PA 7 IR: Development Postings 1710 3.00 2.81 0.71
PA 7 IR: Test Postings 1708 3.00 2.92 0.48
PA 7 IR: Development Boolean Retrieval 1707 3.00 2.86 0.61 
PA 7 IR: Test Boolean Retrieval 1706 3.00 2.90 0.53
PA 7 IR: Development TFIDF 1703 3.00 2.72 0.85
PA 7 IR: Test TFIDF 1700 3.00 2.79 0.73
PA 7 IR: Dev Cosine Ranked Retrieval 1670 3.00 2.19 1.31 
PA 7 IR: Test Cosine Ranked Retrieval 1662 3.00 2.29 1.26 
PA8 Jeopardy: Development Wiki 1477 6.00 3.74 1.83
PA8 Jeopardy: Testing Wiki 1449 7.00 2.97 2.02
PA8 Jeopardy: Development Googling 1363 5.00 3.48 1.88
PA8 Jeopardy: Testing Googling 1340 6.00 2.47 1.75
'''

# Use number of students submitting PS's (problem sets) and PA's 
# (programming assignments) as proxies for participation. 
weekly_ps = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(r'PS\s*(\d+)\s+(\d+)', summary)]
weekly_pa = [(int(m.group(1)), int(m.group(2))) for m in re.finditer(r'PA\s*(\d+).+?(\d+)', summary)]

# Weeks by number in summary: 1-8
weeks = sorted(set(w for w,_ in weekly_ps) | set(w for w,_ in weekly_pa))  

# ps_numbers = {week : number students completing PS for week}
ps_numbers = dict(weekly_ps)

# pa_numbers = {week : average number students completing PAs for week}
pa_numbers = {}
for k,v in weekly_pa:
    pa_numbers[k] = pa_numbers.get(k,[]) + [v]
pa_numbers = dict((k,sum(v)/len(v)) for k,v in pa_numbers.items())

#
# Data looks close enough to an exponential decay with week 1 as an outlier
# So compute a least squares fit of log of all weeks but 1
#

# Variable for least squares fit 
x = NP.array(weeks)
A = NP.vstack([x, NP.ones(len(x))]).T
y_ps = NP.array([ps_numbers[w] for w in weeks])
y_pa = NP.array([pa_numbers[w] for w in weeks])

# Compute least squares of log(y) vs x
# First point looks like an outlier so omit it
m1,c1 = NP.linalg.lstsq(A[1:,:], NP.log(y_ps[1:]))[0]
m2,c2 = NP.linalg.lstsq(A[1:,:], NP.log(y_pa[1:]))[0]
print 'm1=%.2f, c1=%.2f, week = %.2f x prev week' % (m1, c1, NP.exp(m1))
print 'm2=%.2f, c2=%.2f, week = %.2f x prev week' % (m2, c2, NP.exp(m1))

# Plot the data and fitted lines
# and save as attrition.png in current directory
plt.plot(x, y_ps, 'or', label='By problem sets', markersize=10)
plt.plot(x, y_pa, 'ob', label='By programming assignment', markersize=10)
plt.plot(x, NP.exp(m1*x+c1), 'r', label='Best fit - problems')
plt.plot(x, NP.exp(m2*x+c2), 'b', label='Best fit - assignments')
plt.xlabel('Week')
plt.ylabel('Number of students')
plt.title('NLP-Class Attrition by Week')
plt.legend()
#plt.show()
plt.savefig('attrition.png', dpi=200)

