from __future__ import division
import math

disc_text = [ 
    'disc, sound recording, recording, memory device, device, instrumentality, artifact, whole, object, physical entity, entity', 
    'disc, round shape, shape, attribute, abstract entity, entity'
]    

chair_text = [    
    'chair, seat, furniture, furnishing, instrumentality, artifact, whole, object, physical entity, entity', 
    'chair, position, occupation, activity, act, event, psychological feature, abstract entity, entity'
]

def get_words(text):
    return [w.strip() for w in text.split(',')]
    
disc = [get_words(text) for text in disc_text]   
chair = [get_words(text) for text in chair_text]

def get_path(word1, word2):
    matches = []
    for i1,w1 in enumerate(word1):
        for i2,w2 in enumerate(word2):
            if w1 == w2:
                matches.append((i1,i2))
                break
    return min(matches, key = lambda x: sum(x))

path_table = [(word1, word2, get_path(word1, word2)) for word1 in disc for word2 in chair]
# Sort by path length, shortest first
path_table.sort(key = lambda x: sum(x[2]))

for word1, word2, (n1,n2) in path_table:
    print '-' * 80
    print word1[:n1+1]
    print word2[:n2+1]
    print '1 + %d + %d = %d' % (n1, n2, 1+n1+n2)

# Shortest path    
_,_,(n1,n2) = path_table[0]
pathlen = 1+n1+n2
similarity = 1.0/pathlen    

print '=' * 80 
print 'pathlen = %d' % pathlen
print 'similarity = %.2f' % similarity







