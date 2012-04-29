import re

_RE_TOKEN = re.compile('[^a-zA-Z]+')

def tokenize(text):
    "Tokenize text by splitting on non-alphabetic characters"
    return [x for x in _RE_TOKEN.split(text) if x]
      
def get_variants(types): 
    """types is a set of words
        Returns dict of types that differ only in case
            key = lowercase variant of a word
            value = all case variants of key in types
    """
    case_variations = {}
    for w in types:
        case_variations[w.lower()] = case_variations.get(w.lower(), set([])) | set([w])
    return dict([(k,v) for (k,v) in case_variations.items() if len(v) > 1])   

if __name__ == '__main__':
    import sys

    # Read text from file
    text = file(sys.argv[1], 'rt').read()
   
    #
    # Compute tokens, types, types without case variations, case variants and count of types that   
    # only in case
    #
    tokens = tokenize(text)                     # words in text
    types = set(tokens)                         # unique words in text with case variants
    normalized = set(tokenize(text.lower()))    # unique words in text without case variants   
    variants = get_variants(types)              # dict of case variants
    case_only = sum([len(x) - 1 for x in variants.values()]) # number types differing only in case

    #
    # Print results to stdout
    #
    def show_types(types, title):
        print '-' * 40, '%s: %d' % (title, len(types))
        print sorted(types, key = lambda x: (x.lower(), x))
    
    print '=' * 40, 'original text: %d tokens' % len(tokens)
    print text
    show_types(types, 'total types')
    show_types(normalized, 'normalized types')
    print '=' * 40, 'variants: %d' % len(variants)
    for k in sorted(variants.keys()):
        print '%20s : %d %s' % (k, len(variants[k]), sorted(variants[k], reverse=True))
    print 'types that vary only in case: %d' % case_only    

  