import json, sys
import base64
from Datum import Datum
import re

# Not a word
_NOT_A_WORD = '~'

def _KV(key, value):
    return '%s=%s' % (key, value)
    
def _COMBINE(kv_list):
    return ', '.join(kv_list)

_BOOL_STR = { False: 'N', True: 'Y' }
def _B(obj):
    return _BOOL_STR[bool(obj)]
    
_SENTENCE_ENDS = set([
    '?', '!', '.', ':', ';']) #, '"'])
def _end_sentence(word):
    if not word: return _NOT_A_WORD
    return _B(word[-1] in _SENTENCE_ENDS)
    
# )	O	PERSON    
_PUNCTUATION = set(['(', ')', '[', ']'])
def _punctuation(word):
    if not word: return _NOT_A_WORD
    return _B(word in _PUNCTUATION)
    
_RE_CASE_TITLE = re.compile(r'^[A-Z][a-z]+$')
_RE_CASE_UPPER = re.compile(r'^[A-Z]+$')
_RE_CASE_LOWER = re.compile(r'^[a-z]+$')
_RE_CASE_INITIAL = re.compile(r'^[A-Z]\.$')
def _title(word):
    if _RE_CASE_TITLE.search(word): return 1
    #if _RE_CASE_UPPER.search(word): return 2
    #if _RE_CASE_LOWER.search(word): return 3
    #if _RE_CASE_INITIAL.search(word): return 4
    return 0
    
_RE_CAPS = re.compile(r'^[^a-z]*$')
def _caps(word):
    if not word: return _NOT_A_WORD
    return _B(_RE_CAPS.search(word))    
    
# Words spelt in title-case that are not titles    
_FALSE_TITLES = set([
    'god', 'rd', 'road', 'st', 'street', 'lane', 'place', 'grove', 'park', 'government', 
    'january', 'february', 'march', 'june', 'july', 'august', 'september', 'october', 'november', 'december',
    'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']) 
def _not_title(word): 
    if not word: return _NOT_A_WORD
    return _B(word.lower() in _FALSE_TITLES) 

# Run of title-case names will give false positives    
_MAX_TITLE_RUN = 4    
def _title_run(words, location):
    max_run = min(_MAX_TITLE_RUN, len(words) - location)
    run = 0
    for run in range(1, max_run):
        if not _RE_CASE_TITLE.search(words[location + run]):
            break
    return str(run)    
    #return '+'.join([_title(w) for w in words[location+1:location+_MAX_TITLE_RUN]])
       
            
_RE_INITIAL = re.compile(r'[A-Z]\.')
def _initial(word):
    if not word: return _NOT_A_WORD
    return _B(_RE_INITIAL.search(word)) 
    
def _title2(word_n1, word):
    if not word: return _NOT_A_WORD
    titled = bool(_RE_CASE_TITLE.search(word))
    start_sentence = True
    if word_n1:
        start_sentence = word_n1[-1] in _SENTENCE_ENDS and not _RE_INITIAL.search(word)
    return _B(titled and start_sentence)  
    
_RE_NUMERIC = re.compile(r'\d')
def _numeric(word):
    if not word: return _NOT_A_WORD
    return _B(_RE_NUMERIC.search(word)) 

def _hyphenated(word): 
    if not word: return _NOT_A_WORD
    return '-' in word 
    
_PRONOUN_SUBJECTS = set(['we', 'i', 'you', 'they'])    
_PRONOUN_OBJECTS = set(['us', 'me', 'you', 'them']) 

def _pronoun_subject(word):
    if not word: return _NOT_A_WORD
    return word.lower() in _PRONOUN_SUBJECTS

def _pronoun_object(word):
    if not word: return _NOT_A_WORD
    return word.lower() in _PRONOUN_OBJECTS    
    
#in	O	O
#Troy	O	PERSON
_NON_PERSON_PREPOSITIONS = set(['in', 'on', 'the', 'at', 'annual'
    #'de' Charle de Gaulle
    # 'on'
    ])
def _non_person_preposition(word): 
    if not word: return _NOT_A_WORD
    return _B(word.lower() in _NON_PERSON_PREPOSITIONS) 
   
_PERSON_VERBS = set(['say', 'says', 'said'])  
def _person_verb(word):
    if not word: return _NOT_A_WORD
    return word.lower() in _PERSON_VERBS

_VERBS = ['can', 'will', 'might', 'has', 'did', 'be', 'was', 'could'
            'would'] 
def _verb(word): 
    if not word: return _NOT_A_WORD
    word = word.lower()
    return word in _VERBS or word[:-2] == 'ed' or word[:-3] == 'ing'
  
_CONJUNCTIONS = ['and', 'or']    
def _conjunction(word): 
    if not word: return _NOT_A_WORD
    return word.lower() in _CONJUNCTIONS

_CONJUNCTIONS2 = ['by', 'from', 'to']    
def _conjunction2(word): 
    if not word: return _NOT_A_WORD
    return word.lower() in _CONJUNCTIONS2
    
_ENDINGS = ['ing', 'ly', 'ally', 'ed']    
_VOWELLS = 'eaoiu'    
def _vowells(word):
    if not word: return _NOT_A_WORD
    word = word.lower()
    return sum([word.count(c) for c in _VOWELLS])
    
def _vowell_shape(word):
    if not word: return _NOT_A_WORD
    word = word.lower()
    shape = 0
    if word[0] in _VOWELLS: shape += 1
    if word[-1] in _VOWELLS: shape += 2
    return shape

def _syllables(word):
    if not word: return _NOT_A_WORD
    word = word.lower()
    v = [c in _VOWELLS for c in word] 
    count = sum([v[i] != v[i] for i in range(1,len(v))])
    return str(count)
    
    
# Coach	O	PERSON    
_HONORS = set([
    'mr', 'mrs', 'miss', 'ms', 'sir', 'dr', 'herr', 'frau',
    'sister', 'prof', 'professor',
    'king' 'queen', 'prince', 'princess', 'lord', 'viscount', 
    'captain', 'sargent', 'colonel', 'lieutenant'
    'coach', 
    'emperor', 'cardinal',
    'broker', 'director', 'manager',
    'governor'])
def _honor(word):
    if not word: return _NOT_A_WORD
    word = word.lower()
    return word in _HONORS or (word + '.')in _HONORS 
    
_HONORS2 = set(['junior', 'jr', 'senior', '3rd', 'ii', 'iii', 'iv'])
def _honor2(word):
    if not word: return _NOT_A_WORD
    word = word.lower()
    return word in _HONORS2 or (word + '.')in _HONORS     
    
# Motel	O	PERSON	<<<    
_COMPANY_IDS = set(['ltd', 'pty', 'inc', 'ab', 'ag', 'sa', 'spa', 'corp', 'company', 'corporation', 'prison', 'park', 'golf', 
'bank', 'hotel', 'motel',
'festival', 'airport', 'prison'])
def _company_id(word):
    if not word: return _NOT_A_WORD
    word = word.lower()
    return word.lower() in _COMPANY_IDS   
    
_ARTICLES = ['the', 'a'] 
def _article(word):
    if not word: return _NOT_A_WORD
    return word.lower() in _ARTICLES   
    
_stop_words = file('stop.words', 'rt').read()  
_STOP_WORDS_LIST = ' '.join(_stop_words.split('\n')).split()
_STOP_WORDS_LIST = set([w.strip() for w in _STOP_WORDS_LIST if w.strip()])

def _stop_word(w):
   return w.lower() in _STOP_WORDS_LIST

class FeatureFactory:
    """
    Add any necessary initialization steps for your features here
    Using this constructor is optional. Depending on your
    features, you may not need to intialize anything.
    """
    def __init__(self):
        pass

    """
        Words is a list of the words in the entire corpus, previousLabel is the label
        for position-1 (or O if it's the start of a new sentence), and position
        is the word you are adding features for. PreviousLabel must be the
        only label that is visible to this method. 
    """

    def computeFeatures(self, words, previousLabel, position):
        n = len(words)
        features = []
        currentWord = words[position]
        word_n1 = words[position-1] if position >= 1 else ''
        word_p1 = words[position+1] if position < n-1  else ''
        word_p2 = words[position+2] if position < n-2  else ''

        """ Baseline Features """
        f_word = _KV('word', currentWord)
        f_word_p1 = _KV('word_p1', word_p1)
        f_prevLabel = _KV('prevLabel', previousLabel)   
        
        #features.append("word=" + currentWord)
        #features.append("prevLabel=" + previousLabel)
        #features.append("word=" + currentWord + ", prevLabel=" + previousLabel)
    
        """
            Warning: If you encounter "line search failure" error when
            running the program, considering putting the baseline features
            back. It occurs when the features are too sparse. Once you have
            added enough features, take out the features that you don't need. 
        """

        """ TODO: Add your features here """
        
        f_caps = _KV('caps', _caps(currentWord))
        f_title = _KV('title', _title(currentWord))
        f_title_n1 = _KV('title_n1', _title(word_n1))
        f_title_p1 = _KV('title_p1', _title(word_p1))
        f_title_p2 = _KV('title_p2', _title(word_p2))
        f_title2 = _KV('title', _title2(word_n1, currentWord))
        f_not_title = _KV('not_title', _not_title(currentWord))
        f_title_run = _KV('title_run', _title_run(words, position))
        f_vowell_shape = _KV('vowell_shape', _vowell_shape(currentWord))
          
        f_end_sentence_n1 = _KV('end_sentence', _end_sentence(word_n1))
        f_numeric = _KV('numeric', _numeric(currentWord))
        f_letterFirst = _KV('letterFirst', currentWord[0].lower())
        f_letterLast = _KV('letterLast', currentWord[-1].lower())
        f_letterLast_n1 = _KV('letterLast_n1', word_n1[-1].lower() if word_n1 else '~')
        f_letterFirst_p1 = _KV('letterFirst_p1', word_p1[0].lower() if word_p1 else '~')
        f_who_p1 = _KV('letterFirst_p1', word_p1.lower() == 'who' if word_p1 else '~')
        f_is_n1 = _KV('is1_n1', word_n1.lower() in ['is'] if word_n1 else '~')
        f_verb_n1 = _KV('verb_n1', _verb(word_n1))
        f_verb_p1 = _KV('verb_p1', _verb(word_p1))
        f_person_verb_p1 = _KV('person_verb_p1', _person_verb(word_p1))
        f_conjunction_n1 = _KV('conjunction_n1', _conjunction(word_n1))
        f_conjunction_p1 = _KV('conjunction_p1', _conjunction(word_p1))
        f_len = _KV('len', str(len(currentWord)))
        f_vowells = _KV('vowells', _vowells(currentWord))
        f_possessive_p1 = _KV('possessive_p1', word_p1[:-2] == "'s" if word_p1 else '~')
        f_possessive = _KV('possessive', currentWord[:-2] == "'s")
        f_honor_n1 = _KV('honor_n1', _honor(word_n1))
        f_hyphenated = _KV('hyphenated', _hyphenated(currentWord))
        f_comma_p1 = _KV('comma_p1', word_p1 == ',' if word_p1 else '~')
        
        f_pronoun_subject_n1 = _KV('pronoun_subject_n1', _pronoun_subject(word_n1))
        f_pronoun_subject_p1 = _KV('pronoun_subject_p1', _pronoun_subject(word_p1))
        f_pronoun_object_n1 = _KV('pronoun_object_n1', _pronoun_object(word_n1))
        f_pronoun_object_p1 = _KV('pronoun_object_p1', _pronoun_object(word_p1))
        
        f_article_n1 = _KV('article_n1', _article(word_n1))

        f_initial = _KV('initial', _initial(currentWord))
        f_initial_n1 = _KV('initial_n1', _initial(word_n1))

        f_stop_word = _KV('stop_word', _stop_word(currentWord))
        
        f_non_person_preposition_n1 = _KV('non_person_preposition_n1', _non_person_preposition(word_n1))
        f_honor = _KV('honor', _honor(currentWord))
        f_honor_n1 = _KV('honor_n1', _honor(word_n1))
        
        f_company_id = _KV('company_id', _company_id(currentWord))
        f_company_id_p1 = _KV('company_id_p1', _company_id(word_p1))
        
        # START HERE !@#$
        #
        features.append(f_word)
        features.append(f_prevLabel)
        features.append(_COMBINE([f_word, f_prevLabel]))  

        features.append(f_word_p1)
        features.append(_COMBINE([f_word, f_word_p1]))  

        features.append(f_len)
        
        #features.append(f_caps)
        features.append(f_title)
        features.append(_COMBINE([f_title, f_prevLabel]))

        features.append(f_not_title)
        features.append(_COMBINE([f_title, f_not_title]))
        features.append(_COMBINE([f_title, f_prevLabel]))

        features.append(f_title2)
        features.append(_COMBINE([f_title, f_title2]))
        features.append(_COMBINE([f_title2, f_prevLabel]))
        
        features.append(f_vowell_shape)
        features.append(_COMBINE([f_title, f_vowell_shape]))
        features.append(_COMBINE([f_vowell_shape, f_prevLabel]))
        
        
        # Does not help
        # Helps when no f_word
        features.append(f_title_run)
        features.append(_COMBINE([f_title, f_title_run]))
        features.append(_COMBINE([f_title2, f_title_run]))
        features.append(_COMBINE([f_title_run, f_prevLabel]))
        
        features.append(f_company_id)
        features.append(_COMBINE([f_title, f_company_id]))
        features.append(_COMBINE([f_title, f_prevLabel]))
        
        #features.append(f_person_verb_p1)
        #features.append(_COMBINE([f_title, f_person_verb_p1]))
        #features.append(_COMBINE([f_person_verb_p1, f_prevLabel]))
        
        features.append(f_company_id_p1)
        features.append(_COMBINE([f_title, f_company_id_p1]))

        features.append(f_non_person_preposition_n1)
        #features.append(_COMBINE([f_title, f_non_person_preposition_n1]))

        #features.append(f_honor)
        features.append(f_honor_n1)
        #features.append(_COMBINE([f_title, f_honor_n1]))

        features.append(f_who_p1)
        features.append(f_article_n1)

        features.append(f_initial)
        features.append(f_initial_n1)
        features.append(_COMBINE([f_initial, f_initial_n1]))

        features.append(f_stop_word)

        # harm recall and precision
        #features.append(f_title_n1)
        #features.append(_COMBINE([f_title, f_title_n1]))
        #features.append(f_title_p1)
        #features.append(_COMBINE([f_title, f_title_p1]))
        #features.append(_COMBINE([f_title_p1, f_prevLabel]))
        #features.append(f_title_p2)
        #features.append(_COMBINE([f_title, f_title_p2]))
        #features.append(_COMBINE([f_title_p2, f_prevLabel]))
        
        #features.append(f_end_sentence_n1)
        #features.append(_COMBINE([f_title, f_end_sentence_n1]))

        # not helping
        #features.append(f_pronoun_subject_n1)
        #features.append(f_pronoun_subject_p1)
        #features.append(f_pronoun_object_n1)
        #features.append(f_pronoun_object_p1)

        features.append(f_numeric)
        features.append(_COMBINE([f_title, f_numeric]))

        #features.append(f_letterFirst)
        #features.append(f_letterLast)

        #features.append(f_is_n1)
        #features.append(_COMBINE([f_is_n1, f_prevLabel]))
        
        features.append(f_conjunction_n1)
        features.append(f_conjunction_p1)
        features.append(_COMBINE([f_conjunction_n1, f_conjunction_p1]))

        #features.append(f_possessive_p1)
 
        #features.append(f_verb_p1)
        #features.append(_COMBINE([f_verb_p1, f_prevLabel]))

        #features.append(f_comma_p1)

        #features.append(f_hyphenated)

        #features.append(f_honor_n1)
        #features.append(_COMBINE([f_honor_n1, f_prevLabel]))

        #features.append(f_verb_n1)
        #features.append(_COMBINE([f_verb_n1, f_prevLabel]))
        #features.append(_COMBINE([f_verb_n1, f_verb_p1]))

        #features.append(_COMBINE([f_len, f_prevLabel]))

        #features.append(f_vowells)

        # Reduces F1
        #features.append(f_letterLast_n1)
        #features.append(f_letterFirst_p1)
        
        #features.append(_COMBINE([f_letterFirst, f_prevLabel]))
        
        # Reduce recall, F1. Increase precision
        #features.append("titleCase_n1=" + _title(word_n1))
        #features.append("titleCase_p1=" + _title(word_p1))

        return features

    """ Do not modify this method """
    def readData(self, filename):
        data = [] 
        
        for line in open(filename, 'r'):
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data

    """ Do not modify this method """
    def readTestData(self, ch_aux):
        data = [] 
        
        for line in ch_aux.splitlines():
            line_split = line.split()
            # remove emtpy lines
            if len(line_split) < 2:
                continue
            word = line_split[0]
            label = line_split[1]

            datum = Datum(word, label)
            data.append(datum)

        return data


    """ Do not modify this method """
    def setFeaturesTrain(self, data):
        newData = []
        words = []

        for datum in data:
            words.append(datum.word)

        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        previousLabel = "O"
        for i in range(0, len(data)):
            datum = data[i]

            newDatum = Datum(datum.word, datum.label)
            newDatum.features = self.computeFeatures(words, previousLabel, i)
            newDatum.previousLabel = previousLabel
            newData.append(newDatum)

            previousLabel = datum.label

        return newData

    """
        Compute the features for all possible previous labels
        for Viterbi algorithm. Do not modify this method
    """
    def setFeaturesTest(self, data):
        newData = []
        words = []
        labels = []
        labelIndex = {}

        for datum in data:
            words.append(datum.word)
            if not labelIndex.has_key(datum.label):
                labelIndex[datum.label] = len(labels)
                labels.append(datum.label)
        
        ## This is so that the feature factory code doesn't
        ## accidentally use the true label info
        for i in range(0, len(data)):
            datum = data[i]

            if i == 0:
                previousLabel = "O"
                datum.features = self.computeFeatures(words, previousLabel, i)

                newDatum = Datum(datum.word, datum.label)
                newDatum.features = self.computeFeatures(words, previousLabel, i)
                newDatum.previousLabel = previousLabel
                newData.append(newDatum)
            else:
                for previousLabel in labels:
                    datum.features = self.computeFeatures(words, previousLabel, i)

                    newDatum = Datum(datum.word, datum.label)
                    newDatum.features = self.computeFeatures(words, previousLabel, i)
                    newDatum.previousLabel = previousLabel
                    newData.append(newDatum)

        return newData

    """
        write words, labels, and features into a json file
        Do not modify this method
    """
    def writeData(self, data, filename):
        outFile = open(filename + '.json', 'w')
        for i in range(0, len(data)):
            datum = data[i]
            jsonObj = {}
            jsonObj['_label'] = datum.label
            jsonObj['_word'] = base64.b64encode(datum.word)
            jsonObj['_prevLabel'] = datum.previousLabel

            featureObj = {}
            features = datum.features
            for j in range(0, len(features)):
                feature = features[j]
                featureObj['_'+feature] = feature
            jsonObj['_features'] = featureObj
            
            outFile.write(json.dumps(jsonObj) + '\n')
            
        outFile.close()

