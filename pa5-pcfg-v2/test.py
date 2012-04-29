word_text = '''1	JJ	bloody
1	JJ	weary
1	JJ	unable
1	JJ	trusty
1	JJ	further
1	JJ	sacred
1	JJ	tropical
1	JJ	indigenous
1	JJ	temperate
1	JJ	hot
1	JJ	lucky
1	JJ	simple
1	JJ	tiny
1	JJ	hard	
1	JJ	sensational
1	JJ	comparable
1	JJ	angolian
1	JJ	yellow
1	JJ	plodding
'''

import re
RE_JJ = re.compile(r'JJ\s+(\w+)')
def get_jj(line):
	return RE_JJ.search(line).group(1)

def get_lines(text):
	return [ln.strip() for ln in text.split('\n') if ln.strip()]

word_lines = get_lines(word_text)
words = [get_jj(ln) for ln in word_lines]

text = file('dev.sen', 'rt').read()
lines = get_lines(text)

def get_matching_lines(word):
	return [ln for ln in lines if word in ln]

for w in words:
	matching_lines = get_matching_lines(w)
	ln = matching_lines[0] if matching_lines else ''
	print '%20s : %d %s' % (w, len(matching_lines), ln)


