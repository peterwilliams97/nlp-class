"""
    Build  S2.py for NLP class PA5
    
    Typical usage:
        python make_S2.py > S2.gr
        
    In the pa5-pcfg-v2 assignment, *.gr are grammar files that give production
    rules in a grammar and probabilities for those rules (see README.txt in this
    directory).
    
    S2.gr is the baseline grammar that generates any sentence over the lexicon
    Vocab.gr
    
    This script generates S2.gr as a trigram language model with back-off to 
    bigrams and +1 smoothed unigrams. This seems like a reasonable behavior
    for a grammar that only generates every allowed sentence.
    
"""
# Files from exercise
VOCAB_FILE = 'Vocab.gr'
DATA_FILE = 'dev.sen'

def get_lines(filename):
    """Reads filename and returns contents as a list of strings, one for 
        each line in the file
    """
    text = file(filename, 'rt').read()
    lines = text.split('\n')
    lines = [ln.strip() for ln in lines]
    return [ln for ln in lines if ln]

def get_terminals():
    """Reads pre-terminals and their terminal the vocab file and
        return them as dict of 
            key = preterminal 
            value = set of all terminals for preterminal
    """
    terminals = {}
    for line in get_lines(VOCAB_FILE):
        parts = line.split('\t')
        if len(parts) == 3: 
            k,v = parts[1:3]
            terminals[k] = terminals.get(k, set([])) | set([v])
    return terminals

def get_data(all_words):
    """Reads dev data from the data file and return them as list
        of lists of words. Only words that are in all_words are
        returned.
    """
    def decode_line(line):
        from collections import deque
        word_list = []
        tokens = deque(line.split())
        word_parts = []
        while tokens:
            word_parts.append(tokens.popleft())
            word = ' '.join(word_parts)
            if word in all_words:
                word_list.append(word)
                word_parts = []
        return word_list

    return [decode_line(line) for line in get_lines(DATA_FILE)]

def inc(a_dict, key):
    """Increment value of a_dict[key] by 1 if it exists or set it to
        1 if it does not
    """
    a_dict[key] = a_dict.get(key, 0) + 1
 
def get_unigram_counts(data):
    """Return dict of unigram counts for words in data
        key: ngram
        value: number of times the ngram appears in data
    """
    counts = {}
    for words in data:
        for i in range(0, len(words)):
            inc(counts, (words[i]))
    return counts

def get_bigram_counts(data):
    """Return dict of bigram counts for words in data
        key: ngram
        value: number of times the ngram appears in data
    """
    counts = {}
    for words in data:
        for i in range(1, len(words)):
            inc(counts, (words[i-1], words[i]))
    return counts

def get_trigram_counts(data):
    """Return dict of trigram counts for words in data
        key: ngram
        value: number of times the ngram appears in data
    """
    counts = {}
    for words in data:
        for i in range(2, len(words)):
            inc(counts, (words[i-2], words[i-1], words[i]))
    return counts

if __name__ == '__main__':
    # Read in the terminals and the dev data
    terminals = get_terminals()
    all_words = set(sum([list(v) for v in terminals.values()], []))
    data = get_data(all_words)

    # ngram counts by terminal e.g. 'speak'
    raw_unigram_counts = get_unigram_counts(data)
    raw_bigram_counts = get_bigram_counts(data)
    raw_trigram_counts = get_trigram_counts(data)

    # Compute ngram    counts by pre-terminal. e.g. 'verb'
    # Note unigram counts are +1 smoothed
    unigram_counts = {}
    bigram_counts = {}
    trigram_counts = {}

    for k1,v1 in terminals.items():
        unigram_counts[k1] = 1 + sum([raw_unigram_counts.get(w1,0) 
            for w1 in v1])
        for k2,v2 in terminals.items():
            bigram_counts[(k1,k2)] = sum([raw_bigram_counts.get((w1,w2),0) 
                for w1 in v1 
                    for w2 in v2])
            for k3,v3 in terminals.items():
                trigram_counts[(k1,k2,k3)] = sum([raw_trigram_counts.get((w1,w2,w3),0) 
                    for w1 in v1 
                        for w2 in v2
                            for w3 in v3])

    # Write S2.gr to stdout
    # Probalilities are weighted pre-terminal counts
    # Weights are 1:10:60
    # This is a funny weighting scheme. See WEIGHT_* in code below but
    #  I think it applies the necessary ratios
    # WEIGHT_UNIGRAM = 1 is implicit
    WEIGHT_BIGRAM = 10
    WEIGHT_TRIGRAM = 60
    print '1\tS2'
    for k1 in sorted(terminals.keys()):
        print '%d\tS2\t_%s' % (unigram_counts[k1], k1)
    for k1 in sorted(terminals.keys()):
        n1 = unigram_counts[k1]
        print '%d\t_%s\t%s' % (1, k1, k1)
        for k2 in sorted(terminals.keys()):
            n2 = bigram_counts[(k1,k2)]
            if n2:
                print '%d\t_%s\t%s _%s' % (WEIGHT_BIGRAM * n2, k1, k1, k2)
            for k3 in sorted(terminals.keys()):
                n3 = trigram_counts[(k1,k2,k3)]
                if n3:
                    print '%d\t_%s\t%s %s _%s' % (WEIGHT_TRIGRAM * n3, k1, k1, k2, k3)
