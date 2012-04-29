import sys
import os
import re
import pprint

#my_first_pat = r'(\w+)\s*(?:@| at | where )\s*(\w+(?:\.w+)*)\s*(?:\.| dom | dot )\s*edu'

_RE_PARAMS = re.compile('__(\w+)__')

def _make_patttern(base_pattern, params_dict):
    """Replace the '__key__' tokens in base_pattern with params_dict[key].
        This is used for parametrized regex patterns
    """
    return _RE_PARAMS.sub(lambda m: params_dict[m.group(1)], base_pattern)  

_PATTERN_EMAIL = r'''
    __PATTERN__
    (\w+(?:__DOT__\w+)*)            # Name
    \s*                             # Optional space
    (?:@|\sat\s|\swhere\s)          # Separator Not needed so much with pre-processing
    \s*                             # Optional space
    (\w+(?:__DOT__\w+)*)           # Domain prefix  \. => (?:\.|\sdom\s|\sdo?t\s) ??
    \s*                             # Optional space
    __DOT__                         # Separator  Not needed so much with pre-processing
    \s*                             # Optional space
    ((?:edu|com|org|gov)(?:__DOT__\w{2-3})?)    # Ends in 'edu', 'com' etc with optional country
    (?:\W|$)                        # Make sure this is the end
    ''' 
    
_PATTERN_EMAIL0 = _make_patttern(_PATTERN_EMAIL, {'PATTERN': '', 'DOT': '(?:\.|\sdom\s|\sdo?t\s)'})     
if True:
    print _PATTERN_EMAIL0
    #exit()
    
regex_email0 = re.compile(r'''
    (\w+(?:\.\w+)*)         # Name
    \s*                     # Optional space
    (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
    \s*                     # Optional space
    (\w+(?:\.\w+)*)         # Domain prefix  \. => (?:\.|\sdom\s|\sdo?t\s) ??
    \s*                     # Optional space
    (?:\.|\sdom\s|\sdo?t\s)  # Separator  Not needed so much with pre-processing
    \s*                     # Optional space
    ((?:edu|com|org|gov)(?:\.w{2-3})?)    # Ends in 'edu', 'com' etc with optional country
    (?:\W|$)                # Make sure this is the end
    ''', 
    re.VERBOSE | re.IGNORECASE)
    
regex_email0 = re.compile(r'''
    (email\s*(?:to)?\*s:?\s*)?
    (\w+(?:(?(1)[\.\s]|\.)\w+)*)        # Name
    \s*                     # Optional space
    (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
    \s*                     # Optional space
    (\w+(?:(?(1)[\.\s]|\.)\w+)*)         # Domain prefix Allow sepators if there is email: prefix
    \s*                     # Optional space
    \.?                     # Optional .    
    \s*                     # Optional space
    ((?:edu|com|org|gov|mil|net|info)(?:\.w{2})?)    # Ends in 'edu', 'com' etc with optional country
                            # See http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains    
    (?:\W|$)                # Make sure this is the end
    ''', 
    re.VERBOSE | re.IGNORECASE)    
    
if False:    
    regex_email1 = re.compile(r'''
        (\w+(?:\.\w+)*)         # Name
        \s*                     # Optional space
        (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
        \s*                     # Optional space
        (?:
            (\w+(?:\.\w+)*)         # Domain prefix
            \s*                     # Optional space
            (?:\.|\sdom\s|\sdo?t\s)  # Separator  Not needed so much with pre-processing
            \s*                     # Optional space
            (edu|com)            # Ends in 'edu', 'com' etc
        |
            (stanford)\s+(edu) # <= Why does this not work?
        )
        ''', 
        re.VERBOSE | re.IGNORECASE)  

regex_email2 = re.compile(r'''
    email\s*:?\s*
    (\w+(?:\.\w+)*)         # Name
    \s*                     # Optional space
    (?:@|\sat\s|\swhere\s)  # Separator Not needed so much with pre-processing
    \s*                     # Optional space
    (\w+(?:\s+\w+)*)         # Domain prefix
    \s*                     # Optional space
    (?:\.|\sdom\s|\sdo?t\s|\s)  # Separator  Not needed so much with pre-processing
    \s*                     # Optional space
    (edu|com)            # Ends in 'edu', 'com' etc
    ''', 
    re.VERBOSE | re.IGNORECASE)     

#regex_email = re.compile(r'(\w+\.\w+)') 
regex_email = regex_email0  
    
if False:    
    line = r'<dt>Professor David Cheriton <A href="mailto:cheriton@cs.stanford.edu">cheriton at cs.stanford.edu</A>'
    #line = r'cheriton@cs.stanford.edu'
    line = r'd-l-w-h-@-s-t-a-n-f-o-r-d-.-e-d-u'
    line = line.replace('-', '')
    print line
    #line = r'dlw-h@stanford.edu'
    matches = regex_email.findall(line)
    print matches
    exit()    
    
if False:
    line = r'em>ada&#x40;graphics.stanford.edu</em>'
    print line
    line = line.replace(r'&#x40;', '@') #
    print line
    matches = regex_email.findall(line)
    print matches
    exit()
    
if False:
    line = r"email: pal at cs stanford edu, but I receive more email than I can handle. Please don't be offended if I don't reply."
    print line
    matches = regex_email2.findall(line)
    print matches
    exit()
    
# obfuscate('stanford.edu','jurafsky'); 
regex_obfuscate = re.compile(r"obfuscate\('(.*)','(.*)'\)", re.IGNORECASE)
    
name_exclusions = ['server', 'www', 'ftp', 'http', 'name']  

def deobfuscate(line):
    m = regex_obfuscate.search(line)
    if not m:
        return line
    g = m.groups()
    if False:
        print line[:-1]
        print g
        exit()
     
    return '%s@%s' % (g[1], g[0])     

#import urllib
#import xml.sax.saxutils

RE_UNICODE = re.compile(r'&#(x[0-9a-f]{2,4}|\d{2,4});', re.IGNORECASE)

if False:
    m = RE_UNICIODE.search(r'&#x40;stanford.edu</em>')
    print m
    if m:
        print m.groups()
    exit()

# FIXME: Combine all the re.sub() !@#$    
    
def preprocess_unicode(line):
    def replacer(m):
        number = m.group(1)
        if number.lower()[0] == 'x':
            n = int(number[1:], 16)
        else:
            n = int(number)
        if n > 255:
            return ' ' # Cannot handle non-ASCII characters
        return chr(n)
        
    return RE_UNICODE.sub(replacer, line) 

CODES_MAP = { 
    'lt'    : '<',
    'gt'    : '>',
    'amp'   : '&',
    'nbsp'  : ' ',
    'quot'  : '"',
    'ldquo' : '"',
    'rdquo' : '"',
    'lsquo' : "'",
    'rsquo' : "'",
    'hellip': '...',
    'mdash' : '-',
    'ndash' : '-',
}
PATTERN_CODES = r'&(' + '|'.join(CODES_MAP.keys()) + ');'
RE_SPECIAL_CODES = re.compile(PATTERN_CODES, re.IGNORECASE) 

def preprocess_special_codes(line):
    def replacer(m):
        return CODES_MAP[m.group(1)]
        
    return RE_SPECIAL_CODES.sub(replacer, line)     

def preprocess(line):
    if False:
        line = line.replace(r'&#x40;', '@') # levoy: <em>ada&#x40;graphics.stanford.edu</em>
        line = line.replace('&lt;', '<').replace('&gt;', '>')
        line = line.replace('&ldquo;', '"').replace('&rdquo;', '"')  # seen in ouster
        return line
    else: 
                        
        #line2 = xml.sax.saxutils.unescape(line) 
        line2 = line
        line3 = preprocess_unicode(line2)        
        if False:
            if line3 != line2:
                print line2
                print line3
                exit()
        line2 = line3
        line2 = preprocess_special_codes(line2) # Picks up a few left by xml.sax.saxutils.unescape()
        #line2 = line2.replace('&ldquo;', '"').replace('&rdquo;', '"')  # seen in ouster
        #line2 = line2.replace(r'&#x40;', '@') # levoy: <em>ada&#x40;graphics.stanford.edu</em>
        if '&ldquo;'  in line2 or '&lt;' in line2 or '&#x40;'  in line2:
            print '=' * 80
            print line
            print line2
            exit()
        return line2    

RE_AT = re.compile(r'\s(?:at|where)\s', re.IGNORECASE)
RE_DOT = re.compile(r'\s(?:do?t|dom)\s', re.IGNORECASE)
        
def get_emails(line):
    emails_found = []
    
    line = line.lower()
    
    # This line must come first so that other lines do not change &#x40;'
    line = preprocess(line)
   
     # Handle separately
    line = deobfuscate(line)
    
    line = line.replace('-', '') # dwf
    line = line.replace('(', '').replace(')', '') # ouster
    line = line.replace('"', '').replace('followed by', '') # ouster
    
    line = RE_AT.sub('@', line)
    line = RE_DOT.sub('.', line)
         
    #line = line.replace(' at ', '@')
    #line = line.replace(' dot ', '.')
    #line = line.replace(' dt ', '.')   # ullman
    
    line = line.replace(';', '.')  # jks Gives false +ve on manning if no '&lt;' => '<' above
    
    matches = regex_email.findall(line)
    if False:
        if not matches:
            matches = regex_email2.findall(line)
            if matches:
                #print 'before:', matches
                matches = [tuple([re.sub('\s+', '.', x) for x in m]) for m in matches]
                #print 'after: ', matches
    if len(matches):
        for m in matches:
            # Filter multiple matches in regex.
            #m = tuple([x for x in m if x])
            
            if len(m) != 3:
                print '-' * 80
            print m
            
            # Replace space with . as capturing regex's allow spaces
            m = tuple([re.sub('\sdom\s|\sdo?t\s|\s', '.', x) for x in m])
            print m
            #if any(['engler' in x for x in m]):
            #    exit()
                
            m = m[1:]  # Remove email    
            
            if m[0].lower() in name_exclusions:
                continue
            email = '%s@%s.%s' % (m)
            emails_found.append(email)
    
    return emails_found

regex_phone_approx = re.compile(r'''
    (\d{3})\D{0,3}(\d{3})\D{0,3}(\d{4})
    ''', 
    re.VERBOSE)  
    
regex_phone = re.compile(r'''
    (\d{3})[\s\-\)]{1,3}(\d{3})[\s\-]{1,3}(\d{4})
    ''', 
    re.VERBOSE)
    
if False:
    line = '6507234377 650-723-4377'
    matches = regex_phone_approx.findall(line)
    print line
    print matches
    exit()
    
def get_phones(line):
    phones_found = []
    matches = regex_phone.findall(line)
    for m in matches:
        print '-' * 80
        print m
        phones_found.append('%s-%s-%s' % m)
    return phones_found    

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
    if True:
        res = []
        for line in f:
            emails_found = get_emails(line)
            for email in emails_found:
                res.append((name,'e',email))
            phones_found = get_phones(line)
            for phone in phones_found:
                res.append((name,'p',phone))    
        return res
    else:
        emails = [(name,'e',email) for line in f for email in get_emails(line)]
        #emails = []
        phones = [(name,'p',phone) for line in f for phone in get_phones(line)]
        return emails + phones

if False:
    def test_file(fname):
        f = open(fname, 'r')
        f_guesses = process_file(fname, f)
        print fname, f_guesses
    
    test_file(r'..\data\dev\pal')   
    exit()

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
