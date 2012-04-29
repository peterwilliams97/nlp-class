import sys
import os
import re
import pprint

####################################################################################################
#                               Start of Peter's Code
####################################################################################################

# Debug print
#def D(msg): sys.stderr.write(msg + '\n')
def D(msg): pass

def _escape(s):
    """Escape characters that require it in regular expressions"""
    if s in '()[]{}.+*':
        return r'\%s' % s
    return s

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
  
def preprocess_general(line): 
    """Preprocessing that is applied to all text. 
        Convert to lower case, replace unicode characters and strip 
        HTML markup
        
             See http://studentaffairs.stanford.edu/resed/directory
    """
    line = line.lower()
    line = convert_unicode(line)
    return _RE_MARKUP.sub('', line)
    
# Regex for obfuscate('stanford.edu','jurafsky'); 
_RE_OBFUSCATE = re.compile(r"obfuscate\('(.*)','(.*)'\)")  

def get_emails_obfuscate(line):
    """Extract email addresses of the form obfuscate('stanford.edu','jurafsky')"""
    return ['%s@%s' % (m[1], m[0]) for m in _RE_OBFUSCATE.findall(line)]

# Some pre-filtering that is needed to remove some of subterfuges seen in email text    
_EMAIL_FILTER_MAP = {
    # Patterns to filter out 
    '-': '',            # dlwh
    '(': '',
    ')': '',            # dwf
    '[': '',
    ']': '',            # people
    '"': '',            # ouster
    'followed by': '',  # ouster
        
    # . aliases
     ';' : '.'          # jks
} 

# Regex used to apply _EMAIL_FILTER_MAP
_RE_EMAIL_FILTER = re.compile('|'.join([_escape(s) for s in _EMAIL_FILTER_MAP.keys()])) 

# Regex to convert known @ aliases to @
_RE_AT = re.compile(r'\s(?:at|where)\s', re.IGNORECASE)

# Regex to convert known . aliases to .
_RE_DOT = re.compile(r'\s(?:do?t|dom)\s', re.IGNORECASE)

# The main email detection regex
# Combines 
#   - tight match used if there is no 'email' prefix
#   - loose match used if there is an 'email' prefix
# In the loose case, matches on . will also match on space. The fragment (?(1)[\.\s]|\.) does this
#   by checking the backreference to the email capture (which must be discarded in the output)
#
# Assuming a tight match, the main pattern is 
#    <name> @ <domain prefix> [.] <domain suffix> 
# where 
#   <name> and <domain prefix> are text,numbers are (\w+(?:\s*\.\s*\w+)*)
# and 
#   <domain suffix>  is by lookup of the main top level domain with an optional country code
_RE_EMAIL = re.compile(r'''
    (email\s*(?:to)?\s*:?\s*)?          # 'email' prefix? If so then loosen matching below (Tested on pal)
    (\w+(?:\s*(?(1)[\.\s]|\.)\s*\w+)*)  # Name. Allow space separators if loose match
    \s*                                 # Optional space
    @                                   # Separator 
    \s*                                 # Optional space
    (\w+(?:\s*(?(1)[\.\s]|\.)\s*\w+)*)  # Domain prefix. Allow space separators if loose match
    \s*                                 # Optional space
    \.?                                 # Optional .    
    \s*                                 # Optional space
    ((?:edu|com|org|gov|mil|net|info)   # Ends in known TLD. See http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains 
    (?:\.[a-z]{2})?)                    # and optional country code
    (?:\b|$)                            # Make sure this is the end
    ''', 
    re.VERBOSE)    

# Names to exclude in  <name>@<domain> matches    
_NAME_EXCLUSIONS = ['server', 'www', 'ftp', 'http', 'name'] 
_RE_DOTS_SPACES = re.compile(r'[\.\s]+')
    
def get_emails(line):
    """Return 'someone@something' email addresses  extracted from line.
       line is expected to be preprocessed to lower case and html unicode codes substituted
    """   

    def preprocess(line):
        """Convert @ and . aliases to simplify email detection regex
            and filter out the injected noise characters
        """
        line = _RE_EMAIL_FILTER.sub(lambda m: _EMAIL_FILTER_MAP[m.group(0)], line)
        line = _RE_AT.sub('@', line)
        line = _RE_DOT.sub('.', line) 
        return line

    def postprocess(m):
        """Post process a match on _RE_EMAIL to undo the effects that were for matching only
            and are not required in the result
        """
        m = m[1:]  # Remove 'email'   
        
        # Replace space with . as capturing regex's allow spaces
        # Then collapse the resulting multiple . to a single .
        return tuple([_RE_DOTS_SPACES.sub('.', x) for x in m])

    # Alternate forms of @ and . are substituted in preprocess_email() to keep _RE_EMAIL simple    
    # Then there is some postprocessing and removal of addresses with names in _NAME_EXCLUSIONS        
    matches = [postprocess(m) for m in _RE_EMAIL.findall(preprocess(line))]
    return ['%s@%s.%s' % m for m in matches if m[0] not in _NAME_EXCLUSIONS]


# Simple regex to match modern American phone numbers which are the only types of phone numbers
# in the training set    
_RE_PHONE = re.compile('(\d{3})[\s\-\)]{1,3}(\d{3})[\s\-]{1,3}(\d{4})')

def get_phones(line):
    """Return ''###-###-#####'' phone number codes extracted from line""" 
    return ['%s-%s-%s' % m for m in _RE_PHONE.findall(line)]
    
def extract_personal_info(name, line):
    """Process a line of text from html file called name
        Returns a list of the phone numbers and email addresses found in line where each entry in 
        the list has the format:
            (name, 'p', '###-###-#####')
            (name, 'e', 'someone@something')
    """        
    # This just does some standard preprocessing and runs all our personal info extractors over line
    line = preprocess_general(line)
    return [(name,'e',email) for email in get_emails_obfuscate(line)]  \
         + [(name,'e',email) for email in get_emails(line)]  \
         + [(name,'p',phone) for phone in get_phones(line)]
  
""" 
TODO
This function takes in a filename along with the file object (or
an iterable of strings) and scans its contents against regex patterns.
It returns a list of (filename, type, value) tuples where type is either
and 'e' or a 'p' for e-mail or phone, and value is the formatted phone
number or e-mail.  The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***, as it will be called directly by
the submit script
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    
    # Run extract_personal_info() over every line in f and return accumulation of returned lists 
    return sum([extract_personal_info(name, line) for line in f], [])

####################################################################################################
#                               End of Peter's Code
####################################################################################################

"""
You should not need to edit this function, nor should you alter
its interface as it will be called directly by the submit script
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
          continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list = get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
