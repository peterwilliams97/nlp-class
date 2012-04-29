import random

 
def lev_del(word):
    r = random.randint(0, len(word) -1)
    w = word[:r] + word[r+1:]
    assert(len(w) == len(word) - 1)
    return w
    
def lev_add(word):
    l = chr(ord('a') + random.randint(0,25))
    r = random.randint(1, len(word) -1)
    w = word[:r] + l + word[r:]
    assert(len(w) == len(word) + 1)
    return w
    
def lev_subst(word):
    l = chr(ord('a') + random.randint(0,25))
    r = random.randint(1, len(word) -1)
    w = word[:r] + l + word[r+1:]  
    assert(len(w) == len(word))
    return w

def lev2(word):
    r = random.randint(0,2)
    if r == 0: 
        return lev_del(lev_del(word))
    elif r == 1: 
        return lev_add(lev_add(word)) 
    else:
        return lev_subst(word)


for n in range(2,100):
    words = set([lev2('Levenshtein') for i in range(n)])
    text = 'What do the words %s all have in common?' % ', '.join(words)
    print '%3d: %3d %s' % (n, len(text), text)
    if len(text) > 140:
        break
    good_text = text
    
print '-' * 80
print good_text    
       