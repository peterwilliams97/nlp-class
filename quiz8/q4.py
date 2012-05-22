from __future__ import division
import math
from pprint import pprint

def norm(arr):
    return math.sqrt(sum(x**2 for x in arr))

question_text = {
"fish": 
'''
subj-of-A 3 
mod-of-B 2 
obj-of-B 4 
mod-of-C 2 
''',

"bird": 
'''
subj-of-A 3 
subj-of-D 1 
mod-of-C 4 
''',

"ant":
'''
subj-of-A 5 
mod-of-C 2 
subj-of-D 1 
obj-of-B 1 
'''
}

def parse_val(text):
    lines = text.split('\n')
    lines = [ln.strip() for ln in lines]
    lines = [ln for ln in lines if ln]
    data = [ln.split() for ln in lines]
    data = dict((k,int(v)) for k,v in data)
    return data
    
data = dict((k,parse_val(v)) for k,v in question_text.items())
pprint(data)

pos_keys = set(sum([v.keys() for v in data.values()], []))

def get_vector(val_dict):
    return dict((k,val_dict.get(k,0)) for k in pos_keys)

def get_cosine(key1, key2):
    vector1 = get_vector(data[key1])
    vector2 = get_vector(data[key2])
    prod = sum(vector1[k] * vector2[k] for k in pos_keys)
    print key1, vector1, norm(vector1.values())
    print key2, vector2, norm(vector2.values())
    print prod
    return prod/(norm(vector1.values())*norm(vector1.values()))
    
key1 = "fish"
key2 = "bird"     
print 'cosine(%s,%s) = %.2f' % (key1, key2, get_cosine(key1, key2))    
    
    
    
     






