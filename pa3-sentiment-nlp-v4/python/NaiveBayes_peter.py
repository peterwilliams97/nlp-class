# NLP Programming Assignment #3
# NaiveBayes
# 2012

#
# The area for you to implement is marked with TODO!
# Generally, you should not need to touch things *not* marked TODO
#
# Remember that when you submit your code, it is not run from the command line 
# and your main() will *not* be run. To be safest, restrict your changes to
# addExample() and classify() and anything you further invoke from there.
#

import sys
import getopt
import os
import math

_ENGLISH_STOP_WORDS = set([ 
    'a', 'a\'s', 'able', 'about', 'above', 'according', 'accordingly', 'across', 
    'actually', 'after', 'afterwards', 'again', 
    'against', # Seems to be a key word to omit
    'ain\'t', 'all', 
    'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 
    'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 
    'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 
    'appear', 
    #'appreciate', 
    'appropriate', 'are', 
    #'aren\'t', 
    'around', 'as', 
    'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 
    'b', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 
    'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 
    'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', 
    'c', 
    #'c\'mon', 
    'c\'s', 'came', 'can', 'can\'t', 'cannot', 'cant', 'cause', 
    'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 
    'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 
    'containing', 'contains', 'corresponding', 'could', 'couldn\'t', 'course', 
    'currently', 'd', 'definitely', 'described', 'despite', 'did', 
    #'didn\'t', 
    'different', 'do', 'does',
    #'doesn\'t', 'doing', 
    #'don\'t', 
    'done', 'down', 
    #'downwards', 
    'during', 'e', 'each', 'edu', 'eg', 'eight', 'either', 'else', 
    'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 
    'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 
    'example', 
    #'except', 
    'f', 'far', 'few', 'fifth', 'first', 'five', 'followed', 
    'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 
    'further', 'furthermore', 'g', 'get', 'gets', 'getting', 'given', 'gives', 
    'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'h', 'had', 
    #'hadn\'t', 
    'happens', 'hardly', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 
    'he', 'he\'s', 'hello', 'help', 'hence', 'her', 'here', 'here\'s', 'hereafter', 
    'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 
    'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', 'i', 'i\'d', 
    'i\'ll', 'i\'m', 'i\'ve', 'ie', 'if', 
    #'ignored', 
    'immediate', 'in', 'inasmuch', 
    'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 
    'instead', 'into', 'inward', 'is', 
    #'isn\'t',
    'it', 'it\'d', 'it\'ll', 'it\'s', 
    'its', 'itself', 'j', 'just', 'k', 'keep', 'keeps', 'kept', 'know', 'known', 
    'knows', 'l', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 
    'lest', 'let', 'let\'s', 'like', 
    #'liked',
    'likely', 'little', 'look', 
    'looking', 'looks', 'ltd', 'm', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 
    'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 
    'must', 'my', 'myself', 'n', 'name', 'namely', 'nd', 'near', 'nearly', 
    'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 
    'next', 'nine', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 
    #'not', 
    'nothing', 'novel', 'now', 'nowhere', 'o', 'obviously', 'of', 'off', 
    'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 
    'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 
    'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'p', 'particular', 
    'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 
    'presumably', 'probably', 'provides', 'q', 'que', 'quite', 'qv', 'r', 'rather', 
    'rd', 're', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 
    'relatively', 'respectively', 'right', 's', 'said', 'same', 'saw', 'say', 
    'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 
    'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 
    'seriously', 'seven', 'several', 'shall', 'she', 'should', 'shouldn\'t', 
    'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 
    'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 
    'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', 't', 't\'s', 
    'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 
    'that', 'that\'s', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 
    'then', 'thence', 'there', 'there\'s', 'thereafter', 'thereby', 'therefore', 
    'therein', 'theres', 'thereupon', 'these', 'they', 'they\'d', 'they\'ll', 
    'they\'re', 'they\'ve', 'think', 'third', 'this', 'thorough', 'thoroughly', 
    'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 
    'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 
    'try', 'trying', 'twice', 'two', 'u', 'un', 'under', 'unfortunately', 'unless', 
    'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 
    'uses', 'using', 'usually', 'uucp', 'v', 'value', 'various', 'very', 'via', 
    'viz', 'vs', 'w', 'want', 'wants', 'was', 'wasn\'t', 'way', 'we', 'we\'d', 
    'we\'ll', 'we\'re', 'we\'ve', 'welcome', 'well', 'went', 'were', 'weren\'t', 
    'what', 'what\'s', 'whatever', 'when', 'whence', 'whenever', 'where', 
    'where\'s', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 
    'wherever', 'whether', 'which', 'while', 'whither', 'who', 'who\'s', 'whoever', 
    'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 
    'without', 'won\'t', 'wonder', 'would', 'wouldn\'t', 'x', 'y', 'yes', 'yet', 
    'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 
    'yourselves', 'z', 
    #'zero', 
]) 

# Don't exclude ?-
_MY_EXCLUSIONS = set(['&nbsp', ';', '.', ',', '"', "'", '(', ')', '&', '-'])
_EXCLUSIONS = _MY_EXCLUSIONS | _ENGLISH_STOP_WORDS

_CLASS_INDEX = {'pos': 0, 'neg': 1} 

_NEGATIVE_WORDS = [
    'embarrassing', 'horrid', 'predictable', 'ridiculous', 'unoriginal',
    'loathing', 'badness', 'half-assed'
]
_NEGATIVE_BIGRAMS = [
    'but why'
]    
_NEGATIVE_TRIGRAMS = [
    'what the hell'
]

def _B(w1, w2):
    return '%s %s' % (w1, w2)

def _T(w1, w2, w3):
    return '%s %s %s' % (w1, w2, w3)   
    
def _exclude(words):
    return [w for w in words if w not in _EXCLUSIONS] 
    
def _dump(word_counts, fold):
    def word_score(k):
        p,n = word_counts[k]
        return math.log(p+1) - math.log(n+1)
    
    def count_line(k):
        p,n = word_counts[k]
        return '%-20s %3d %3d %.2f' % (k, p, n, word_score(k))
   
    wckeys = sorted(word_counts.keys(), key=word_score)
    text = '\n'.join([count_line(k) for k in wckeys])  
    file('word.counts.%d' % fold, 'wt').write(text)

class NaiveBayes:
    class TrainSplit:
        """Represents a set of training/testing data. 
            self.train is a list of Examples, as is self.test. 
        """
        def __init__(self):
            self.train = []
            self.test = []

    class Example:
        """Represents a document with a label. klass is 'pos' or 'neg' by convention.
           words is a list of strings.
        """
        def __init__(self):
            self.klass = ''
            self.words = []

    def __init__(self):
        """NaiveBayes initialization"""
        self.FILTER_STOP_WORDS = False
        self.stopList = set(self.readFile('../data/english.stop'))
        
        if False:
            # Write English stop words to python script
            print '----------------'
            lines = []
            ln = ''
            words = ["'%s', " % x.replace("'", r"\'") for x in sorted(self.stopList)]
            for w in words:
                if len(ln) + len(w) > 80:
                    lines.append((' ' *4) + ln)
                    ln = ''
                ln += w
            lines.append(ln)
  
            file('stop.word.list', 'wt').write('\n'.join(lines))
            exit()
            
        self.numFolds = 10
        
        # PW: word_counts[word] = (num_pos, num_neg)
        self.word_counts = {}
        self.bigram_counts = {}
        self.bigram_keys = set([])
        self.trigram_counts = {}
        self.trigram_keys = set([])

    #############################################################################
    # TODO TODO TODO TODO TODO 
  
    def classify(self, words):
        """ TODO
          'words' is a list of words to classify. Return 'pos' or 'neg' classification.
        """
        def word_score(w):
            """Returns +1 smoothed log(pos/neg) for w """
            p,n = self.word_counts.get(w, [0,0])
            return math.log(p+1) - math.log(n+1)
            
        def bigram_score(i):
            """Returns +1 smoothed log(pos/neg) for w """
            k = _B(words[i-1],words[i])
            if k not in self.bigram_keys:
                return (word_score(words[i-1]) + word_score(words[i-1])) / 20.0 
            p,n = self.bigram_counts.get(k, [0,0])
            return math.log(p+0.5) - math.log(n+0.5) 

        def trigram_score(i):
            """Returns +1 smoothed log(pos/neg) for w """
            k = _T(words[i-2],words[i-1],words[i])
            if k not in self.trigram_keys:
                return (bigram_score(i-1) + bigram_score(i)) 
            p,n = self.trigram_counts.get(k, [0,0])
            # High laplace is like weighting down trigrams?
            return math.log(p+0.2) - math.log(n+0.2)
        
        words = _exclude(words)
        score = sum([trigram_score(i) for i in range(2,len(words))])
        return 'pos' if score > 0 else 'neg'

    def addExample(self, klass, words):
        """
         * TODO
         * Train your model on an example document with label klass ('pos' or 'neg') and
         * words, a list of strings.
         * You should store whatever data structures you use for your classifier 
         * in the NaiveBayes class.
         * Returns nothing
        """
        words = _exclude(words)
        kls = _CLASS_INDEX[klass]
        for w in words:
            count = self.word_counts.get(w, [0,0])
            count[kls] += 1
            self.word_counts[w] = count
        #print 'words=%4d, word_counts=%6d' % (len(words), len(self.word_counts)) 

        w0 = words[0]
        for w in words[1:]:
            k = _B(w0,w)
            count = self.bigram_counts.get(k, [0,0])
            count[kls] += 1
            self.bigram_counts[k] = count
            self.bigram_keys.add(k)
            w0 = w
            
        w0 = words[0]
        w1 = words[1]
        for w in words[2:]:
            k = _T(w0,w1,w)
            count = self.trigram_counts.get(k, [0,0])
            count[kls] += 1
            self.trigram_counts[k] = count
            self.trigram_keys.add(k)
            w0 = w1
            w1 = w    

    # TODO TODO TODO TODO TODO 
    #############################################################################
 
    def readFile(self, fileName):
        """
         * Code for reading a file.  you probably don't want to modify anything here, 
         * unless you don't like the way we segment files.
        """
        contents = []
        f = open(fileName)
        for line in f:
            contents.append(line)
        f.close()
        result = self.segmentWords('\n'.join(contents)) 
        return result
  
    def segmentWords(self, s):
        """
        * Splits lines on whitespace for file reading
        """
        return s.split()
  
    def trainSplit(self, trainDir):
        """Takes in a trainDir, returns one TrainSplit with train set."""
        split = self.TrainSplit()
        posTrainFileNames = os.listdir('%s/pos/' % trainDir)
        negTrainFileNames = os.listdir('%s/neg/' % trainDir)
        for fileName in posTrainFileNames:
            example = self.Example()
            example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
            example.klass = 'pos'
            split.train.append(example)
        for fileName in negTrainFileNames:
            example = self.Example()
            example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
            example.klass = 'neg'
            split.train.append(example)
        return split

    def train(self, split):
        for example in split.train:
            words = example.words
            if self.FILTER_STOP_WORDS:
                words = self.filterStopWords(words)
            self.addExample(example.klass, words)

    def crossValidationSplits(self, trainDir):
        """Returns a list of TrainSplits corresponding to the cross validation splits."""
        splits = [] 
        posTrainFileNames = os.listdir('%s/pos/' % trainDir)
        negTrainFileNames = os.listdir('%s/neg/' % trainDir)
        #for fileName in trainFileNames:
        for fold in range(0, self.numFolds):
            split = self.TrainSplit()
            for fileName in posTrainFileNames:
                example = self.Example()
                example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
                example.klass = 'pos'
                if fileName[2] == str(fold):
                    split.test.append(example)
                else:
                    split.train.append(example)
            for fileName in negTrainFileNames:
                example = self.Example()
                example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
                example.klass = 'neg'
                if fileName[2] == str(fold):
                    split.test.append(example)
                else:
                    split.train.append(example)
            splits.append(split)
            return splits

    def test(self, split):
        """Returns a list of labels for split.test."""
        labels = []
        for example in split.test:
            words = example.words
            if self.FILTER_STOP_WORDS:
                words = self.filterStopWords(words)
            guess = self.classify(words)
            labels.append(guess)
        return labels
  
    def buildSplits(self, args):
        """Builds the splits for training/testing"""
        trainData = [] 
        testData = []
        splits = []
        trainDir = args[0]
        if len(args) == 1: 
          print '[INFO]\tPerforming %d-fold cross-validation on data set:\t%s' % (self.numFolds, trainDir)

          posTrainFileNames = os.listdir('%s/pos/' % trainDir)
          negTrainFileNames = os.listdir('%s/neg/' % trainDir)
          for fold in range(0, self.numFolds):
            split = self.TrainSplit()
            for fileName in posTrainFileNames:
              example = self.Example()
              example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
              example.klass = 'pos'
              # !@#$
              example.filename = '%s/pos/%s' % (trainDir, fileName)
              if fileName[2] == str(fold):
                split.test.append(example)
              else:
                split.train.append(example)
            for fileName in negTrainFileNames:
              example = self.Example()
              example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
              example.klass = 'neg'
              # !@#$
              example.filename = '%s/neg/%s' % (trainDir, fileName)
              if fileName[2] == str(fold):
                split.test.append(example)
              else:
                split.train.append(example)
            splits.append(split)
            
        elif len(args) == 2:
          split = self.TrainSplit()
          testDir = args[1]
          print '[INFO]\tTraining on data set:\t%s testing on data set:\t%s' % (trainDir, testDir)
          posTrainFileNames = os.listdir('%s/pos/' % trainDir)
          negTrainFileNames = os.listdir('%s/neg/' % trainDir)
          for fileName in posTrainFileNames:
            example = self.Example()
            example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
            example.klass = 'pos'
            split.train.append(example)
          for fileName in negTrainFileNames:
            example = self.Example()
            example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
            example.klass = 'neg'
            split.train.append(example)

          posTestFileNames = os.listdir('%s/pos/' % testDir)
          negTestFileNames = os.listdir('%s/neg/' % testDir)
          for fileName in posTestFileNames:
            example = self.Example()
            example.words = self.readFile('%s/pos/%s' % (testDir, fileName)) 
            example.klass = 'pos'
            split.test.append(example)
          for fileName in negTestFileNames:
            example = self.Example()
            example.words = self.readFile('%s/neg/%s' % (testDir, fileName)) 
            example.klass = 'neg'
            split.test.append(example)
          splits.append(split)
        return splits
  
    def filterStopWords(self, words):
        """Filters stop words."""
        filtered = []
        for word in words:
            if not word in self.stopList and word.strip() != '':
                filtered.append(word)
        return filtered

def main():
    nb = NaiveBayes()
    (options, args) = getopt.getopt(sys.argv[1:], 'f')
    if ('-f','') in options:
        nb.FILTER_STOP_WORDS = True

    splits = nb.buildSplits(args)
    totAccuracy = 0.0
    for fold, split in enumerate(splits):
        classifier = NaiveBayes()
        accuracy = 0.0
        for example in split.train:
            words = example.words
            if nb.FILTER_STOP_WORDS:
                words = classifier.filterStopWords(words)
            classifier.addExample(example.klass, words)
            
        #_dump(classifier.trigram_counts, fold)    
      
        for example in split.test:
            words = example.words
            if nb.FILTER_STOP_WORDS:
                words = classifier.filterStopWords(words)
            guess = classifier.classify(words)
            if example.klass == guess:
                accuracy += 1.0
            #else:
            #    print example.filename
 
        accuracy = accuracy / len(split.test)
        totAccuracy += accuracy
        print '[INFO]\tFold %d Accuracy: %f' % (fold, accuracy) 
    avgAccuracy = totAccuracy / len(splits)
    print '[INFO]\tAccuracy: %f' % avgAccuracy

if __name__ == "__main__":
    main()
