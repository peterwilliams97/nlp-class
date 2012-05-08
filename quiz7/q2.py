import copy

rules = [
    ('S',  ['NP', 'VP'],  0.9),
    ('S',  ['VP'],        0.1),
    ('VP', ['V', 'NP'],   0.5),
    ('VP', ['V'],         0.1),
    ('VP', ['V', '@VP_V'],0.3),
    ('VP', ['V', 'PP'],   0.1),
    ('@VP_V', ['NP', 'NP'],1.0),
    ('NP', ['NP', 'NP'],  0.1),
    ('NP', ['NP', 'PP'],  0.2),
    ('NP', ['N'],         0.7),
    ('PP', ['P', 'NP'],   1.0),
]

for a,b,c in rules:
    print '%10s: %15s %.1f -- %d' % (a,b,c, len(b))

unary_rules = [(a,b,c) for a,b,c in rules if len(b) == 1]
binary_rules = [(a,b,c) for a,b,c in rules if len(b) == 2]

print '-' * 80
for a,b,c in unary_rules:
    print '%10s: %15s %.1f' % (a,b,c)
    
print '-' * 80
for a,b,c in binary_rules:
    print '%10s: %15s %.1f' % (a,b,c)  

print '-' * 80    
c12 = { 
    'NP': 0.3,
    'V' : 0.2,
    'P' : 0.1
}

c23 = { 
    'PP': 0.3,
    '@VP_V' : 0.4,
    'NP' : 0.5
}

def apply_unary_rules(cell):
    modified = True
    while modified:
        modified = False
        keys = copy.copy(cell.keys())
        for k in keys:
            for a,B,p in unary_rules:
                b = B[0]
                if b == k:
                    prob = cell[b] * p
                    if prob > cell.get(a, 0.0):
                        print '  %s -> %s' % (b, a)
                        cell[a] = prob
                        modified = True

def apply_binary_rules(B_cell, C_cell):
    A_cell = {}
    for B in B_cell:
        for C in C_cell:
            for A,(b,c),p in binary_rules:
                if b == B and c == C:
                    prob = B_cell[b] * C_cell[c] * p
                    if prob > A_cell.get(A, 0.0):
                        print '  %s -> %s %s' % (A, B, C)
                        A_cell[A] = prob
    return A_cell                    
                       
                        
for cell in c12,c23:
    print '^' * 80
    print cell
    apply_unary_rules(cell)
    print cell
    print '.' * 80

print '=' * 80      
c13 = apply_binary_rules(c12,c23)
print c13
print '-' * 80     
apply_unary_rules(c13)
print c13
   