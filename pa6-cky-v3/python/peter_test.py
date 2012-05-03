import collections
import copy
import optparse
import os

import ling.Tree as Tree
import ling.Trees as Trees
import pennParser.EnglishPennTreebankParseEvaluator as EnglishPennTreebankParseEvaluator
import io.PennTreebankReader as PennTreebankReader
import io.MASCTreebankReader as MASCTreebankReader

from PCFGParserTester import *

if __name__ == '__main__':
    opt_parser = optparse.OptionParser()
    opt_parser.add_option('--path', dest='path', default='../data/parser')
    opt_parser.add_option('--maxLength', dest='max_length', default='20')
    opt_parser.add_option('--testData', dest='test_data', default='')

    options, args = opt_parser.parse_args()
    options = vars(options)

    print 'PCFGParserTest options:'
    for k, v in options.items():
        print '  %-12s: %s' % (k, v)
    print ''
    MAX_LENGTH = int(options['max_length'])

    parser = BaselineParser()
    print 'Using parser: %s' % parser.__class__.__name__

    base_path = '../data/parser/miniTest/'

    print 'Data will be loaded from: %s' % base_path

    train_trees = []
    validation_trees = []
    test_trees = []

    # training data: first 3 of 4 datums
    print 'Loading training trees from %s ...' % base_path
    train_trees = read_trees(base_path, 7, 7)
    print 'done.'
    
    print '%d train_trees ' % len(train_trees)
    tree = train_trees[0]
    annotated_tree = TreeAnnotations.annotate_tree(tree)
    unannotated_tree = TreeAnnotations.unannotate_tree(annotated_tree)

    for key in ['tree', 'annotated_tree', 'unannotated_tree']:
        print '-' * 80
        val = locals()[key]
        print key 
        print val
        print Trees.PennTreeRenderer.render(val)
     

    # test data: last of 4 datums
    print "Loading test trees..."
    test_trees = read_trees(base_path, 4, 4)
    print "done."

    print ""
    print "Training parser..."
    parser.train(train_trees)

    print "Testing parser"
    test_parser(parser, test_trees)
