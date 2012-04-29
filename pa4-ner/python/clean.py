import sys

filename = sys.argv[1]
text = file(filename, 'rt').read()
lines = text.split('\n')
lines = [ln.strip() for ln in lines if ln.strip()]

ALLOWED = set(['O', 'PERSON'])
def append_match(line):
    
    parts = line.split('\t')
    if len(parts) != 3:
       return line
       
    actual, predicted = parts[1:3]
    if predicted not in ALLOWED or actual not in ALLOWED:
        return line
        
    
    result = '---'
    if predicted < actual:
        result = '<<<'
    if predicted > actual:
        result = '>>>'
        
    #print [predicted,actual,result] 
    #if predicted != actual: exit()     
        
    return '\t'.join(parts[:3] + [result])

lines = [append_match(ln) for ln in lines]    

text_out = '\n'.join(lines)
file(filename, 'wt').write(text_out)