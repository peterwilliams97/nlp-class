import sys, traceback, re, collections
from pprint import pprint

_RE_START_INFO_BOX = re.compile(r'\{\{Infobox')
_RE_END_INFO_BOX = re.compile(r'\}\}')
_RE_INFO_BOX_NAME = re.compile(r'\|name\s*=\s*(\S.+\S)\s*$')
_RE_INFO_BOX_WIFE = re.compile(r'\|spouse\s*=.*\[\[(.+)\]\]')

# Partial map of HTML unicode symbols
# http://blog.stevenlevithan.com/archives/multi-replace
# http://scribble-count.com/Ref/ASCII.htm
_UNIODE_MAP = { 
    'lt'    : '<',
    'gt'    : '>',
    'amp'   : '&',
    'nbsp'  : ' ',
    'quot'  : '"',
    'ldquo' : '"',
    'rdquo' : '"',
    'lsquo' : "'",
    'rsquo' : "'",
    'middot': chr(183),
    'hellip': '...',
    'mdash' : '-',
    'ndash' : '-',
}

# Add the HTML unicode numerical codes
# http://www.fileformat.info/info/unicode/char/40/index.htm
_UNICODE_PATTERNS = _UNIODE_MAP.keys() + ['#x[\da-f]{2,4}', '#\d{2,4}']

# Combine all the uncicode codes into regex
# We don't need to be comprehensive about this as long as we get @, -, and .
_RE_UNICODE = re.compile(r'&(%s);' % '|'.join(_UNICODE_PATTERNS)) 

# Catch all the unicode codes we missed
_RE_UNICODE_CATCH_ALL = re.compile(r'&[a-z]{2-6};')   

def convert_unicode(line):
    """Replace all Unicode &(%s); codes with their values"""
    def replacer(m):
        p = m.group(1)
        if p in _UNIODE_MAP.keys(): 
            return _UNIODE_MAP[p]
        else:
            n = int(p[2:], 16) if p[1] == 'x' else int(p[1:])
            return chr(n) if n <= 255 else ' '

    line = _RE_UNICODE.sub(replacer, line) 
    return _RE_UNICODE_CATCH_ALL.sub(' ', line) 
    
# HTML markup
_RE_MARKUP = re.compile(r'<.*?>')     

# Wiki parentheses
_RE_PARENTHESES = re.compile(r'\(.+?\)')     
  
def preprocess(line): 
    """Preprocessing that is applied to all text. 
        Convert to lower case, replace unicode characters and strip 
        HTML markup
        
             See http://studentaffairs.stanford.edu/resed/directory
    """
    #line = line.lower()
    line = convert_unicode(line)
    line = _RE_MARKUP.sub('', line)
    line = _RE_PARENTHESES.sub('', line)
    # Periods are word boundaries
    line = line.replace('.', ' ')
    line = line.replace(',', ' ')
    return line

if False:
    m = _RE_START_INFO_BOX.search('<text xml:space="preserve">{{Infobox Governor')
    print m.group(0)
    m = _RE_END_INFO_BOX.search('}}')
    print m.group(0)
    m = _RE_INFO_BOX_NAME.search('|name         = Arnold Schwarzenegger')
    print m.group(0)
    m = _RE_INFO_BOX_WIFE.search('|spouse       = {{nowrap|[[Maria Shriver]] (1986&amp;ndash;present)}}')
    print m.group(0)
    exit()
    
    class InfoBox:

        def __init__(self):
            self.in_info_box = False
            self.name = None
            self.spouse = None
            self.spouse_dict = {}
            
        def process(self, line):
            if not self.in_info_box:
                if '{{Infobox' in line:
                    self.in_info_box = True
                    self.name = None
                    self.spouse = None
            else:
                m = _RE_INFO_BOX_NAME.search(line)
                if m:    
                    self.name = m.group(1)
                m = _RE_INFO_BOX_WIFE.search(line)
                if m:
                    self.spouse = m.group(1)
                if line.startswith('}}'):
                    in_info_box = False
                    if name and spouse:
                        self.spouse_dict[self.name] = self.spouse

def parse_infobox(f):
    """Generator for extracting info box fields from f which is a text file, hence
        a generator of text lines
    """
    in_info_box = False

    for i,line in enumerate(f):
        if not in_info_box:
            if '{{Infobox' in line:
                in_info_box = True
                name = None
                wife = None
                #print i, 'start info box'
                continue
        else:
            #print '     ', line,
            m = _RE_INFO_BOX_NAME.search(line)
            if m:
                name = m.group(1)
                #print i, ' wife=', wife, '---',  m.group(0),
                continue
            m = _RE_INFO_BOX_WIFE.search(line)
            if m:
                wife = m.group(1)
                #print i, ' wife=', wife, '---',  m.group(0),
                continue
            if line.startswith('}}'):
                in_info_box = False
                #print i, ' end info box', name, wife
                if name and wife:
                    yield (name, wife)

_RE_CASE_TITLE = re.compile(r'^[A-Z][a-z]+$')
def is_title(word):
    return bool(_RE_CASE_TITLE.search(word))

_stop_words = file('stop.words', 'rt').read()  
_STOP_WORDS_LIST = ' '.join(_stop_words.split('\n')).split()
_STOP_WORDS_LIST = set([w.strip() for w in _STOP_WORDS_LIST if w.strip()])

def is_stop_word(w):
   return w.lower() in _STOP_WORDS_LIST
    
def decode_text(text):
    words = text.split()
    words = [w for w in words if not is_stop_word(w)]
    persons = []

    # First extract the person from [[person|other name]]
    start = end = -1
    for i,w in enumerate(words):
        if w[:2] == '[[':
            start = i
            words[i] = w[2:]
        if start >= 0:    
            if '|' in w:
                end = i+1
                words[i] = w.split('|')[0]
            elif w[-2:] == ']]':
                end = i+1
                words[i] = w[:-2]
        if start >= 0 and end >= 0:
            if all(is_title(v) for v in words[start:end]):
                persons.append((start,end))
            start = end = -1
    
    # Remove the [[ and ]]
    if False:
        for start,end in persons:
            #print words[end-1], 
            words[start] = words[start][2:]
            words[end-1] = words[end-1][:-2]
            #print '=>', words[end-1] 

    return words,persons

def get_person_in_range(persons, i0, i1, words):
    """Persons is a list of (start,end) tuples sorted by start
        Return person such that i0 <= start < end <= i1
    """
    # First try the [[]] fields
    for start,end in persons:
        #if start > i1:       return -1, -1
        if i0 <= start and end <= i1:
            return start,end, 1
            
    do_show = 'Dunnell' in words
    if do_show: print '!!!!'
    
    # Next 2 consecutive title case words    
    matches = []
    last_was_title = False
    for j in range(i0+1,i1):
        this_is_title = is_title(words[j])
        if do_show:  print words[j], this_is_title
        if last_was_title and this_is_title:
            return j-1, j+1, 2
        last_was_title = this_is_title
    return -1, -1, 3 

def get_spouses(text):
    words,persons = decode_text(text)
    n = len(words)
    #print words
    #print '-' * 80, n
    
    #do_test = 'Goldfinger' in text
    #if do_test: print '$$$$'
    
    spouses = []
    def get_person(i0, i1):
        start,end,rank = get_person_in_range(persons, i0, i1, words)
        result = ' '.join(words[start:end]) if start >= 0 else None
        if 'Dunnell' in words:
            print '>>>', words[i0:i1], result 
        return result,rank

    for i,w in enumerate(words):
        if w.lower() == 'married':
            #if do_test: print '@@@@', words[max(0,i-5):min(i+6,n)]
            spouse,rank = get_person(max(0,i-6), i)
            if spouse:
                spouses.append((spouse,rank))
            spouse,rank = get_person(i+1, min(i+6,n))
            if spouse:
                spouses.append((spouse,rank))    
    return spouses

# Also use [[First Last]]
#   
def find_married_pairs(f):
    pairs = []
    last_lines = collections.deque([''] * 3) 
    for line in f:
        last_lines.popleft()
        last_lines.append(line)
        if 'married' in last_lines[1].lower():
            spouse1,spouse2 = get_spouses(''.join(last_lines))
            if spouse1 and spouse2:
                pairs.append((spouse1,spouse2))
    return pairs 
 
_RE_TITLE = re.compile(r'<title>\s*(.+)\s*</title>') 
def find_married_pairs2(f):
    pairs = []
    last_lines = collections.deque([''] * 3) 
    name = None
    in_page = False
    for line in f:
        if not in_page:
            if '<page>' in line:
                in_page = True
                name = None
        else:
            if '</page>' in line:
                in_page = False
            else:         
                if not name:
                    m = _RE_TITLE.search(line)
                    if m:
                        name = m.group(1)
                        continue
                # Strip the markup
                line = preprocess(line)        
                last_lines.popleft()
                last_lines.append(line)
                if 'married' in last_lines[1].lower():
                    spouses = get_spouses(''.join(last_lines))
                    if spouses:
                        if len(spouses) > 1:
                            print ' ***', spouses
                            pairs.append((spouses[0][0], spouses[1][0], 0))
                        else:    
                            spouse,rank = spouses[0]
                            pairs.append((name,spouse,rank))    
    return pairs    

class Wiki:

    # reads in the list of wives
    def addWives(self, wivesFile):
        try:
            input = open(wivesFile)
            wives = input.readlines()
            input.close()
        except IOError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            sys.exit(1)    
        return wives

    # read through the wikipedia file and attempts to extract the matching husbands. note that you will need to provide
    # two different implementations based upon the useInfoBox flag. 
    def processFile(self, f, wives, useInfoBox):

        husbands = [] 
        
        if useInfoBox: 
            wife_husband_map = dict((wife,name) for name,wife in parse_infobox(f)) 
            #print wife_husband_map
            #exit()
        else:
            pairs = find_married_pairs2(f)
            married_map = {}
            for k,v,r in sorted(pairs):
                print k,v,r
                if k >= 2:
                    married_map[k] = married_map.get(k, []) + [(v,r)]
                married_map[v] = married_map.get(v, []) + [(k,r)]
            #exit()    
            #dict([(v,(k,r)) for k,v,r in pairs] + [(k,(v,r)) for k,v,r in pairs])
            #pprint(married_map)
            for k in married_map:
                married_map[k] = min(married_map[k], key = lambda x : x[1])[0] 
            def short_wife(wife):
                return ' '.join(wife.split(' ')[:-1])
            married_map2 = dict((short_wife(k),v) for k,v in married_map.items())
            pprint(married_map)

        # TODO:
        # Process the wiki file and fill the husbands Array
        # +1 for correct Answer, 0 for no answer, -1 for wrong answers
        # add 'No Answer' string as the answer when you dont want to answer

        for wife in wives:
            wife = wife.strip()
            if useInfoBox: 
                if wife in wife_husband_map:
                    husband = 'Who is %s?' % wife_husband_map[wife] 
                else:
                    husband = 'No Answer'
            else:
                if wife in married_map:
                    husband = 'Who is %s?' % married_map[wife] 
                elif wife in married_map2:
                    husband = 'Who is %s?' % married_map2[wife]     
                else:
                    husband = 'No Answer'
            print 'Q = "%s", A = "%s"' % (wife, husband)  
            husbands.append(husband)
        f.close()
        return husbands

    # scores the results based upon the aforementioned criteria
    def evaluateAnswers(self, useInfoBox, husbandsLines, goldFile):
        correct = 0
        wrong = 0
        noAnswers = 0
        score = 0 
        try:
            goldData = open(goldFile)
            goldLines = goldData.readlines()
            goldData.close()
            
            goldLength = len(goldLines)
            husbandsLength = len(husbandsLines)
            
            if goldLength != husbandsLength:
                print('Number of lines in husbands file should be same as number of wives!')
                sys.exit(1)
            for i in range(goldLength):
                if husbandsLines[i].strip() in set(goldLines[i].strip().split('|')):
                    correct += 1
                    score += 1
                elif husbandsLines[i].strip() == 'No Answer':
                    noAnswers += 1
                else:
                    wrong += 1
                    score -= 1
                    #print husbandsLines[i].strip(), set(goldLines[i].strip().split('|'))
                    
        except IOError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
        if useInfoBox:
            print('Using Info Box...')
        else:
            print('No Info Box...')
        print('Correct Answers: ' + str(correct))
        print('No Answers: ' + str(noAnswers))
        print('Wrong Answers: ' + str(wrong))
        print('Total Score: ' + str(score)) 

if __name__ == '__main__':
    wikiFile = '../data/small-wiki.xml'
    wivesFile = '../data/wives.txt'
    goldFile = '../data/gold.txt'
    useInfoBox = False
    wiki = Wiki()
    wives = wiki.addWives(wivesFile)
    husbands = wiki.processFile(open(wikiFile), wives, useInfoBox)
    wiki.evaluateAnswers(useInfoBox, husbands, goldFile)
    