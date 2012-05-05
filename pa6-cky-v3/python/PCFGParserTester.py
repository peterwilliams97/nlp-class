import collections
import copy
import optparse

from ling.Tree import Tree
import ling.Trees as Trees
import pennParser.EnglishPennTreebankParseEvaluator as EnglishPennTreebankParseEvaluator
import io.PennTreebankReader as PennTreebankReader
import io.MASCTreebankReader as MASCTreebankReader

def PP(x, indent=4): 
    """Pretty print x"""
    import pprint
    pp = pprint.PrettyPrinter(indent=indent)
    pp.pprint(x)

def D(dct): 
    """Convert keys and values of dct strings recursively"""
    if isinstance(dct, dict):    return dict([(str(k),D(dct[k])) for k in dct])
    elif isinstance(dct, list):  return [D(x) for x in dct]
    elif isinstance(dct, tuple): return tuple([D(x) for x in dct])    
    return str(dct)   

def print_chart(chart, name, indent=4):
    """Print a CKY chart"""
    print '-' * 80
    print name
    if False:
        for i,row in enumerate(chart):
            for j, val in enumerate(row):
                if j > i:
                    print '%2d,%2d:' % (i,j),
                    if val: print
                    PP(D(val))    
    else:
        for span in range(len(chart) - 1, 0, -1):
            for begin in range(len(chart) - span):
                end = begin + span
                print '%2d,%2d:' % (begin,end)
                PP(D(chart[begin][end]), indent * (len(chart) - span)) 
    
class Parser:
    """*Effectively abstract) base class"""

    def train(self, train_trees):
        pass

    def get_best_parse(self, sentence):
        """
            Should return a Tree
        """
        pass

class PCFGParser(Parser):

    def train(self, train_trees):
        # TODO: before you generate your grammar, the training
        #       trees need to be binarized so that rules are at
        #       most binary

        annotated_trees = [TreeAnnotations.annotate_tree(tree) for tree in train_trees]
        self.lexicon = Lexicon(annotated_trees)
        self.grammar = Grammar(annotated_trees)

        if True:
            print 'trees'
            for tree in annotated_trees: print tree
            print 'lexicon'
            lex = dict(((k,dict(v)) for k,v in self.lexicon.word_to_tag_counters.items())) 
            PP(lex)
            print 'grammar' 
            PP(self.grammar)
            #exit()

    def get_best_parse(self, sentence):
        """
            Should return a Tree.
            'sentence' is a list of strings (words) that form a sentence.
            
            function CKY(words, grammar) returns [most_probable_parse,prob] 
              score = new double[#(words)+1][#(words)+1][#(nonterms)] 
              back = new Pair[#(words)+1][#(words)+1][#nonterms]] 
              for i=0; i<#(words); i++ 
                for A in nonterms
                  if A -> words[i] in grammar 
                    score[i][i+1][A] = P(A -> words[i]) 
                //handle unaries
                boolean added = true 
                while added  
                  added = false 
                  for A, B in nonterms
                    if score[i][i+1][B] > 0 && A->B in grammar 
                      prob = P(A->B)*score[i][i+1][B] 
                      if prob > score[i][i+1][A] 
                        score[i][i+1][A] = prob
                        back[i][i+1][A] = B 
                        added = true
                        
              for span = 2 to #(words)
                for begin = 0 to #(words)- span
                    end = begin + span
                    for split = begin+1 to end-1
                        for A,B,C in nonterms
                            prob=score[begin][split][B]*score[split][end][C]*P(A->BC)
                            if prob > score[begin][end][A]
                                score[begin]end][A] = prob
                                back[begin][end][A] = new Triple(split,B,C)
                    //handle unaries
                    boolean added = true
                    while added
                        added = false
                        for A, B in nonterms
                        prob = P(A->B)*score[begin][end][B];
                            if prob > score[begin][end][A]
                                score[begin][end][A] = prob
                                back[begin][end][A] = B
                                added = true           
        """
        # TODO: implement this method
        print sentence
        lexicon = self.lexicon
        grammar = self.grammar
        nonterms = grammar.binary_rules_by_left_child
        
        print 'grammar.unary_rules_by_child'
        PP(dict([(k,[str(s) for s in v]) for k,v in grammar.unary_rules_by_child.items()]))
        rules = [str(s) for s in grammar.unary_rules_by_child['N']]
        print 'grammar.unary_rules_by_child[%s]=%s' % ('N', rules)
            
        n = len(sentence)
        m = len(nonterms)
        scores = [[{} for j in range(n+1)] for i in range(n+1)]
        back = [[{} for j in range(n+1)] for i in range(n+1)]
        
        # First the Lexicon
        for i in range(n):
            word = sentence[i]
            for tag in lexicon.get_all_tags():
                A = UnaryRule(tag, word)
                A.score = lexicon.score_tagging(word, tag)
                scores[i][i+1][A] = A.score 
                back[i][i+1][A] = None

            # handle unaries
            added = True
            while added:
                added = False
                # Don't modify the dict we are iterating
                these_scores = copy.copy(scores[i][i+1])
                for B in these_scores:
                    #print 'B*', B, these_scores[B]
                    for A in grammar.get_unary_rules_by_child(B.parent):
                        #print 'A**', A, these_scores.get(A, 0)
                        if these_scores[B] > 0:
                            prob = B.score * these_scores[B] 
                            #print '***', prob
                            if prob > these_scores.get(A, 0): 
                                scores[i][i+1][A] = prob
                                back[i][i+1][A] = [B] 
                                #print 'added %s => %s' % (A,B)
                                added = True
            
        # Do higher layers  
        for span in range(2, n + 1):
            for begin in range(n - span + 1):
                end = begin + span
                print '* begin,end = %d,%d' % (begin, end)
                for split in range(begin + 1, end):
                    B_scores = scores[begin][split]
                    C_scores = scores[split][end]
                    C_parents = [c.parent for c in C_scores]
                    for B in B_scores:
                        for A in grammar.get_binary_rules_by_left_child(B.parent):
                            C2_scores = [C for C in C_scores if C.parent == A.right_child]
                            for C in C2_scores:
                                # Now have A which has B as left child and C as right child 
                                #print 'C*', C, C_scores[C]
                                prob = B_scores[B] * C_scores[C] * A.score
                                if prob > scores[begin][end].get(A, 0):
                                    scores[begin][end][A] = prob
                                    back[begin][end][A] = [split, B, C]
                # Handle unaries
                added = True
                while added:
                    added = False
                    these_scores = copy.copy(scores[begin][end])
                    for B in these_scores:
                        for A in grammar.get_unary_rules_by_child(B.parent):
                            prob = B.score * these_scores[B] 
                            if prob > these_scores.get(A, 0): 
                                scores[begin][end][A] = prob
                                back[begin][end][A] = [B] 
                                #print 'added %s => %s' % (A,B)
                                added = True

        if False:
            #s = [[D(d) for d in r] for r in scores]
            #PP(s)
            print_chart(scores, 'scores')
            print_chart(back, 'back')
            exit()

        # Build tree from backpointers
        top = scores[0][n]
        PP(D(top))
        #print [k.parent for k in top]
        print 'top roots'
        top_roots = dict([(k,top[k]) for k in top if k.parent == 'ROOT'])
        PP(D(top_roots))

        def make_tree(begin, end, A, depth = 0):
            s = '   ' * (depth)
            print s, 'make_tree(%d, %d, "%s")' % (begin, end, str(A)),
            backptrs = back[begin][end][A]
            print D(backptrs)
            tag = A.parent
            if not backptrs: 
                print s, '**', str(A), tag, A.child
                return Tree(tag, [Tree(A.child)])
            if len(backptrs) == 1:
                [B] = backptrs
                child = make_tree(begin, end, B, depth+1)
                return Tree(tag, [child])
            elif len(backptrs) == 3:
                [split, B, C] = backptrs
                childB = make_tree(begin, split, B, depth+1)
                childC = make_tree(split, end, C, depth+1)
                return Tree(tag, [childB, childC]) 

        print '-' * 80
        out_trees = []
        for root in top_roots:
            tree = make_tree(0, n, root)
            print '!' * 80
            out_trees.append(tree)
            if False:
                print '^' * 80
                print Trees.PennTreeRenderer.render(tree)
                print '.' * 80
                exit()
 
        out_trees = [TreeAnnotations.unannotate_tree(tree) for tree in out_trees]
        print '^' * 80
        print Trees.PennTreeRenderer.render(out_trees[0])
        print ',' * 80
        return out_trees[0]


class BaselineParser(Parser):

    def train(self, train_trees):
        self.lexicon = Lexicon(train_trees)
        self.known_parses = {}
        self.span_to_categories = {}
        for train_tree in train_trees:
            tags = train_tree.get_preterminal_yield()
            tags = tuple(tags)  # because lists are not hashable, but tuples are
            if tags not in self.known_parses:
                self.known_parses[tags] = {}
            if train_tree not in self.known_parses[tags]:
                self.known_parses[tags][train_tree] = 1
            else:
                self.known_parses[tags][train_tree] += 1
            self.tally_spans(train_tree, 0)

    def get_best_parse(self, sentence):
        tags = self.get_baseline_tagging(sentence)
        tags = tuple(tags)
        if tags in self.known_parses:
            return self.get_best_known_parse(tags, sentence)
        else:
            return self.build_right_branch_parse(sentence, list(tags))

    def build_right_branch_parse(self, words, tags):
        cur_position = len(words) - 1
        right_branch_tree = self.build_tag_tree(words, tags, cur_position)
        while cur_position > 0:
            cur_position -= 1
            right_branch_tree = self.merge(
                    self.build_tag_tree(words, tags, cur_position),
                    right_branch_tree)
        right_branch_tree = self.add_root(right_branch_tree)
        return right_branch_tree

    def merge(self, left_tree, right_tree):
        span = len(left_tree.get_yield()) + len(right_tree.get_yield())
        maxval = max(self.span_to_categories[span].values())
        for key in self.span_to_categories[span]:
            if self.span_to_categories[span][key] == maxval:
                most_freq_label = key
                break
        return Tree(most_freq_label, [left_tree, right_tree])

    def add_root(self, tree):
        return Tree('ROOT', [tree])

    def build_tag_tree(self, words, tags, cur_position):
        leaf_tree = Tree(words[cur_position])
        tag_tree = Tree(tags[cur_position], [leaf_tree])
        return tag_tree

    def get_best_known_parse(self, tags, sentence):
        # Simpler 
        # parses = self.known_parses[tags]
        # parse = max(parses.keys(), key = lambda k: parses[k])
        
        maxval = max(self.known_parses[tags].values())
        for key in self.known_parses[tags]:
            if self.known_parses[tags][key] == maxval:
                parse = key
                break
        parse = copy.deepcopy(parse)
        parse.set_words(sentence)
        return parse

    def get_baseline_tagging(self, sentence):
        return [self.get_best_tag(word) for word in sentence]

    def get_best_tag(self, word):
        # Simpler 
        # return max(self.lexicon.get_all_tags(), 
        #    key = lambda k: self.lexicon.score_tagging(word, k))
        best_score = 0
        best_tag = None
        for tag in self.lexicon.get_all_tags():
            score = self.lexicon.score_tagging(word, tag)
            if best_tag is None or score > best_score:
                best_score = score
                best_tag = tag
        return best_tag

    def tally_spans(self, tree, start):
        if tree.is_leaf() or tree.is_preterminal():
            return 1
        end = start
        for child in tree.children:
            child_span = self.tally_spans(child, end)
            end += child_span
        category = tree.label
        if category != "ROOT":
            if end-start not in self.span_to_categories:
                self.span_to_categories[end-start] = {}
            if category not in self.span_to_categories[end-start]:
                self.span_to_categories[end-start][category] = 1
            else:
                self.span_to_categories[end-start][category] += 1
        return end - start

class TreeAnnotations:

    @classmethod
    def annotate_tree(cls, unannotated_tree):
        """
            Currently, the only annotation done is a lossless binarization
        """

        # TODO: change the annotation from a lossless binarization to a
        # finite-order markov process (try at least 1st and 2nd order)
        # mark nodes with the label of their parent nodes, giving a second
        # order vertical markov process

        return TreeAnnotations.binarize_tree(unannotated_tree)

    @classmethod
    def binarize_tree(cls, tree):
        label = tree.label
        if tree.is_leaf():
            return Tree(label)
        if len(tree.children) <= 2:    
            children = [TreeAnnotations.binarize_tree(child) for child in tree.children]
            return Tree(label, children)
       
        intermediate_label = '@%s->' % label
        intermediate_tree = TreeAnnotations.binarize_tree_helper(tree, 0, intermediate_label)
        return Tree(label, intermediate_tree.children)

    @classmethod
    def binarize_tree_helper(cls, tree, num_children_generated, intermediate_label):
        left_tree = tree.children[num_children_generated]
        children = []
        children.append(TreeAnnotations.binarize_tree(left_tree))
        if num_children_generated < len(tree.children) - 1:
            right_tree = TreeAnnotations.binarize_tree_helper(
                    tree, num_children_generated + 1, intermediate_label + '_' + left_tree.label)
            children.append(right_tree)
        return Tree(intermediate_label, children)

    @classmethod
    def at_filter(cls, string):
        return string.startswith('@')

    @classmethod
    def unannotate_tree(cls, annotated_tree):
        """
            Remove intermediate nodes (labels beginning with "@")
            Remove all material on node labels which follow their base
            symbol (cuts at the leftmost -, ^, or : character)
            Examples: a node with label @NP->DT_JJ will be spliced out,
            and a node with label NP^S will be reduced to NP
        """
        debinarized_tree = Trees.splice_nodes(annotated_tree, TreeAnnotations.at_filter)
        unannotated_tree = Trees.FunctionNodeStripper.transform_tree(debinarized_tree)
        return unannotated_tree

class Lexicon:
    """
        Simple default implementation of a lexicon, which scores word,
        tag pairs with a smoothed estimate of P(tag|word)/P(tag).

        Instance variables:
            word_to_tag_counters
            total_tokens
            total_word_types
            tag_counter
            word_counter
            type_tag_counter
    """

    def __init__(self, train_trees):
        """
            Builds a lexicon from the observed tags in a list of training
            trees.
        """
        self.total_tokens = 0.0
        self.total_word_types = 0.0
        self.word_to_tag_counters = collections.defaultdict(lambda: collections.defaultdict(lambda: 0.0))
        self.tag_counter = collections.defaultdict(lambda: 0.0)
        self.word_counter = collections.defaultdict(lambda: 0.0)
        self.type_to_tag_counter = collections.defaultdict(lambda: 0.0)

        for train_tree in train_trees:
            words = train_tree.get_yield()
            tags = train_tree.get_preterminal_yield()
            for word, tag in zip(words, tags):
                self.tally_tagging(word, tag)
                
    def tally_tagging(self, word, tag):
        """Add word:tag to lexicon?"""
        if not self.is_known(word):
            self.total_word_types += 1
            self.type_to_tag_counter[tag] += 1
        self.total_tokens += 1
        self.tag_counter[tag] += 1
        self.word_counter[word] += 1
        self.word_to_tag_counters[word][tag] += 1

    def get_all_tags(self):
        return self.tag_counter.keys()

    def is_known(self, word):
        return word in self.word_counter

    def score_tagging(self, word, tag):
        p_tag = float(self.tag_counter[tag]) / self.total_tokens
        c_word = float(self.word_counter[word])
        c_tag_and_word = float(self.word_to_tag_counters[word][tag])
        if c_word < 10:
            c_word += 1
            c_tag_and_word += float(self.type_to_tag_counter[tag]) / self.total_word_types
        p_word = (1.0 + c_word) / (self.total_tokens + self.total_word_types)
        p_tag_given_word = c_tag_and_word / c_word
        return p_tag_given_word / p_tag * p_word
        
    def __str__(self):
        wc =  dict(self.word_counter)
        wtc = dict(((k,dict(v)) for k,v in self.word_to_tag_counters.items())) 
        return 'word_counter=%s\nword_to_tag_counters=%s' % (wc, wtc)

class Grammar:
    """
        Simple implementation of a PCFG grammar, offering the ability to
        look up rules by their child symbols. Rule probability estimates
        are just relative frequency estimates off of training trees.

        self.binary_rules_by_left_child
        self.binary_rules_by_right_child
        self.unary_rules_by_child
    """

    def __init__(self, train_trees):
        self.unary_rules_by_child = collections.defaultdict(lambda: [])
        self.binary_rules_by_left_child = collections.defaultdict(lambda: [])
        self.binary_rules_by_right_child = collections.defaultdict(lambda: [])

        unary_rule_counter = collections.defaultdict(lambda: 0)
        binary_rule_counter = collections.defaultdict(lambda: 0)
        symbol_counter = collections.defaultdict(lambda: 0)

        for train_tree in train_trees:
            self.tally_tree(train_tree, symbol_counter, unary_rule_counter, binary_rule_counter)
        for unary_rule in unary_rule_counter:
            unary_prob = float(unary_rule_counter[unary_rule]) / symbol_counter[unary_rule.parent]
            unary_rule.score = unary_prob
            self.add_unary(unary_rule)
        for binary_rule in binary_rule_counter:
            binary_prob = float(binary_rule_counter[binary_rule]) / symbol_counter[binary_rule.parent]
            binary_rule.score = binary_prob
            self.add_binary(binary_rule)

    def __unicode__(self):
        rule_strings = []
        for left_child in self.binary_rules_by_left_child:
            for binary_rule in self.get_binary_rules_by_left_child(left_child):
                rule_strings.append(str(binary_rule))
        for child in self.unary_rules_by_child:
            for unary_rule in self.get_unary_rules_by_child(child):
                rule_strings.append(str(unary_rule))
               
        return '%s\n' % '\n'.join(rule_strings)
        
    def __str__(self):   
        return unicode(self).encode('utf-8')

    def add_binary(self, binary_rule):
        self.binary_rules_by_left_child[binary_rule.left_child].append(binary_rule)
        self.binary_rules_by_right_child[binary_rule.right_child].append(binary_rule)

    def add_unary(self, unary_rule):
        self.unary_rules_by_child[unary_rule.child].append(unary_rule)

    def get_binary_rules_by_left_child(self, left_child):
        return self.binary_rules_by_left_child[left_child]

    def get_binary_rules_by_right_child(self, right_child):
        return self.binary_rules_by_right_child[right_child]

    def get_unary_rules_by_child(self, child):
        return self.unary_rules_by_child[child]

    def tally_tree(self, tree, symbol_counter, unary_rule_counter, binary_rule_counter):
        if tree.is_leaf():
            return
        if tree.is_preterminal():
            return
        if len(tree.children) == 1:
            unary_rule = self.make_unary_rule(tree)
            symbol_counter[tree.label] += 1
            unary_rule_counter[unary_rule] += 1
        if len(tree.children) == 2:
            binary_rule = self.make_binary_rule(tree)
            symbol_counter[tree.label] += 1
            binary_rule_counter[binary_rule] += 1
        if len(tree.children) < 1 or len(tree.children) > 2:
            raise Exception('Attempted to construct a Grammar with ' \
                    + 'an illegal tree (most likely not binarized): ' + str(tree))
        for child in tree.children:
            self.tally_tree(child, symbol_counter, unary_rule_counter, binary_rule_counter)

    def make_unary_rule(self, tree):
        return UnaryRule(tree.label, tree.children[0].label)

    def make_binary_rule(self, tree):
        return BinaryRule(tree.label, tree.children[0].label, tree.children[1].label)

class BinaryRule:
    """
        A binary grammar rule with score representing its probability.
    """

    def __init__(self, parent, left_child, right_child):
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child
        self.score = 0.0

    def __str__(self):
        return '%s->%s %s %% %s' % (self.parent, self.left_child, self.right_child, self.score)

    def __hash__(self):
        result = hash(self.parent)
        result = 29 * result + hash(self.left_child)
        result = 29 * result + hash(self.right_child)
        return result

    def __eq__(self, o):
        if self is o:
            return True

        if not isinstance(o, BinaryRule):
            return False

        if (self.left_child != o.left_child):
            return False
        if (self.right_child != o.right_child):
            return False
        if (self.parent != o.parent):
            return False
        return True

class UnaryRule:
    """
        A unary grammar rule with score representing its probability.
    """
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child
        self.score = 0.0

    def __str__(self):
        return '%s->%s %% %s' % (self.parent, self.child, self.score)

    def __hash__(self):
        return 29 * hash(self.parent) + hash(self.child)

    def __eq__(self, o):
        if self is o:
            return True

        return isinstance(o, UnaryRule) and self.child == o.child \
                and self.parent == o.parent

MAX_LENGTH = 20

def test_parser(parser, test_trees):
    evaluator = EnglishPennTreebankParseEvaluator.LabeledConstituentEval(
            ['ROOT'], set(["''", "``", ".", ":", ","]))
    for test_tree in test_trees:
        test_sentence = test_tree.get_yield()
        if len(test_sentence) > 20:
            continue
        guessed_tree = parser.get_best_parse(test_sentence)
        print 'Guess:\n%s' % Trees.PennTreeRenderer.render(guessed_tree)
        print 'Gold:\n%s' % Trees.PennTreeRenderer.render(test_tree)
        evaluator.evaluate(guessed_tree, test_tree)
    print ''
    return evaluator.display(True)

def read_trees(base_path, low=None, high=None):
    trees = PennTreebankReader.read_trees(base_path, low, high)
    return [Trees.StandardTreeNormalizer.transform_tree(tree) for tree in trees]

def read_masc_trees(base_path, low=None, high=None):
    print "Reading MASC from %s" % base_path
    trees = MASCTreebankReader.read_trees(base_path, low, high)
    return [Trees.StandardTreeNormalizer.transform_tree(tree) for tree in trees]

if __name__ == '__main__':
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('--path', dest='path', default='../data/parser')
    opt_parser.add_option('--data', dest='data', default = 'masc')
    opt_parser.add_option('--parser', dest='parser', default='BaselineParser')
    opt_parser.add_option('--maxLength', dest='max_length', default='20')
    opt_parser.add_option('--testData', dest='test_data', default='')

    options, args = opt_parser.parse_args()
    options = vars(options)

    print 'PCFGParserTest options:'
    for k, v in options.items():
        print '  %-12s: %s' % (k, v)
    print ''
    MAX_LENGTH = int(options['max_length'])

    parser = globals()[options['parser']]()
    print 'Using parser: %s' % parser.__class__.__name__

    base_path = options['path']
    # pre_base_path = base_path
    data_set = options['data']
    if not base_path.endswith('/'):
        base_path += '/'

    print 'Data will be loaded from: %s' % base_path

    train_trees = []
    validation_trees = []
    test_trees = []

    if data_set == 'miniTest':
        base_path += 'parser/%s' % data_set

        # training data: first 3 of 4 datums
        print 'Loading training trees...'
        train_trees = read_trees(base_path, 1, 3)
        print 'done.'

        # test data: last of 4 datums
        print 'Loading test trees...'
        test_trees = read_trees(base_path, 4, 4)
        print 'done.'

    if data_set == 'masc':
        base_path += 'parser/'

        # training data: MASC train
        print 'Loading MASC training trees... from: %smasc/train' % base_path
        train_trees.extend(read_masc_trees('%smasc/train' % base_path, 0, 38))
        print 'done.'
        print 'Train trees size: %d' % len(train_trees)
        print 'First train tree: %s' % \
                Trees.PennTreeRenderer.render(train_trees[0])
        print 'Last train tree: %s' % \
                Trees.PennTreeRenderer.render(train_trees[-1])

        # test data: MASC devtest
        print 'Loading MASC test trees...'
        test_trees.extend(read_masc_trees('%smasc/devtest' % base_path, 0, 11))
        #test_trees.extend(read_masc_trees('%smasc/blindtest' % base_path, 0, 8))
        print 'done.'
        print 'Test trees size: %d' % len(test_trees)
        print 'First test tree: %s' % \
                Trees.PennTreeRenderer.render(test_trees[0])
        print 'Last test tree: %s' % \
                Trees.PennTreeRenderer.render(test_trees[-1])

    if data_set not in ['miniTest', 'masc']:
        raise Exception('Bad data set: %s: use miniTest or masc.' % data_set)

    print ''
    print 'Training parser...'
    parser.train(train_trees)

    print 'Testing parser'
    test_parser(parser, test_trees)
