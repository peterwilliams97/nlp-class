import re, sys

text = file('Vocab.gr', 'rt').read()

def get_pos(word):
    pattern = r'\d+\s+(\w+)\s+%s' % word
    return [m.group(1) for m in re.finditer(pattern, text)]

for word in sys.argv[1:]:
    pos = get_pos(word)
    print '%20s: %s' % (word, pos if pos else '')


