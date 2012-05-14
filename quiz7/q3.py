from __future__ import division
import math 

def L(x): 
    return math.log(x, 10)
    
def norm(lst):
    return math.sqrt(sum(x**2 for x in lst))

# Given data
text = '''
term	Dawn	Beatrice	She	Regeneration
happiness	37	30	0	3
surprise	40	10	6	0
family	31	0	12	17
adventure	0	5	13	07
'''

text = '''
term	Dawn	Beatrice	She	Regeneration
happiness	37	30	0	3
surprise	40	10	6	0
family	31	0	12	17
adventure	0	5	13	0
'''

# Build data structures
#  docs = list of docs
#  terms = list of terms
#  counts[doc][term] = count of term in doc 
lines = text.split('\n')
lines = [ln.strip() for ln in lines if ln.strip()]
words = [ln.split('\t') for ln in lines]
docs = words[0][1:]
terms = []
counts = dict((k,{}) for k in docs)
for wrd in words[1:]:
    term, vals = wrd[0], [int(w) for w in wrd[1:]]
    for i,doc in enumerate(docs):
        counts[doc][term] = vals[i]
    terms.append(term)    

# doc_total_words[doc] = Total # word in doc   
doc_total_words = dict((doc,sum(counts[doc].values())) for doc in docs)

# doc_counts[term] = # of docs that term occurs in 
doc_counts = dict((term, sum(1 if counts[doc][term] else 0 for doc in docs)) for term in terms)
  
# N = total number of docs
N = len(docs)  
# Inverse doc frequency
idf = dict((term, L(N) - L(doc_counts[term])) for term in terms)

print 'N = %d' % N
print 'doc_counts = %s' % doc_counts
print 'idf = %s' % idf

def get_tf(count): return 1.0 + L(count) if count else 0.0

# Compute tf-idf        
tfidf = dict(
        (doc, dict(
                (term, get_tf(counts[doc][term]) * idf[term]) 
              for term in terms)) 
        for doc in docs)
        
# per-document l2 norms
l2norm = dict((doc, norm(tfidf[doc].values())) for doc in docs)         

# tf-idf normalized to unit document length        
tfidf_norm = dict(
        (doc, dict(
                (term, tfidf[doc][term] /l2norm[doc]) 
              for term in terms)) 
        for doc in docs)
        
def cosine(doc1, doc2):
    return sum(tfidf_norm[doc1][term] * tfidf_norm[doc2][term] for term in terms)

#
# Print out results    
#    
print '-' * 80 
print 'Original table'   
print '%20s : %s' % ('term', ' '.join(['%10s' % k for k in docs]))  
for term in terms:
    print '%20s : %s' % (term, ' '.join(['%10d' % counts[doc][term] for doc in docs])) 
print '%20s : %s' % ('Total', ' '.join(['%10d' % doc_total_words[doc] for doc in docs]))    

print '-' * 80 
print 'tfidf table'   
print '%20s : %s' % ('term', ' '.join(['%10s' % k for k in docs]))  
for term in terms:
    print '%20s : %s' % (term, ' '.join(['%10.4f' % tfidf[doc][term] for doc in docs]))   

print '-' * 80 
print 'normalized tfidf table'   
print '%20s : %s' % ('term', ' '.join(['%10s' % k for k in docs]))  
for term in terms:
    print '%20s : %s' % (term, ' '.join(['%10.4f' % tfidf_norm[doc][term] for doc in docs]))      

print '-' * 80 
doc1 = 'Beatrice' 
doc2 = 'Regeneration' 
print 'cosine("%s", "%s") = %.2f' % (doc1,doc2, cosine(doc1, doc2))

