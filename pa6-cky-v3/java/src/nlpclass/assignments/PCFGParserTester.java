package nlpclass.assignments;

import nlpclass.io.MASCTreebankReader;
import nlpclass.io.PennTreebankReader;
import nlpclass.ling.Tree;
import nlpclass.ling.Trees;
import nlpclass.parser.EnglishPennTreebankParseEvaluator;
import nlpclass.util.*;
//import nlpclass.classify.ProbabilisticClassifier;

import java.io.BufferedReader;
import java.io.IOException;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Harness for PCFG Parser project.
 *
 * @author Dan Klein
 */
public class PCFGParserTester {

    // Parser interface ===========================================================

    /**
     * Parsers are required to map sentences to trees.  How a parser is
     * constructed and trained is not specified.
     */
    public static interface Parser {
        public void train(List<Tree<String>> trainTrees);
        public Tree<String> getBestParse(List<String> sentence);
    }

    // PCFGParser =================================================================

    /**
     * The PCFG Parser you will implement.
     */
    public static class PCFGParser implements Parser {
    
        private Grammar grammar;
        private Lexicon lexicon;

        public void train(List<Tree<String>> trainTrees) {
            // TODO: before you generate your grammar, the training trees
            // need to be binarized so that rules are at most binary

            List<Tree<String>> annotatedTrees = new ArrayList<Tree<String>>();
            for (Tree<String> tree: trainTrees) {
                 annotatedTrees.add(TreeAnnotations.annotateTree(tree));
            }
            
            /*
            System.out.println("trainTrees: " );
            for (Tree<String> tree: trainTrees)  System.out.println("  " + tree);
            System.out.println("annotatedTrees: " );
            for (Tree<String> tree: annotatedTrees)  System.out.println("  " + tree);
             */
            lexicon = new Lexicon(annotatedTrees);
            grammar = new Grammar(annotatedTrees);
            
            /*
            System.out.println("lexicon: " + lexicon.getAllTags());
            System.out.println("grammar: " + grammar);
            */
            //System.exit(-1);
        }
        
        private static String getParent(Object o) {
            if (o instanceof BinaryRule) {
                return ((BinaryRule)o).getParent();
            } else if (o instanceof UnaryRule) {
                return ((UnaryRule)o).getParent();
            } else {
                return null;
            }
        }
        
        // Print a CKY chart
        private static void printChart(List<List<Map<Object,Double>>> chart, 
                                List<List<Map<Object,Triplet<Integer,Object,Object>>>> backs, 
                                String name) {
            System.out.println("-------------------- $$$$$ --------------------");
            System.out.println(name);
            String spacer = ""; 
            for (int span = chart.size() - 1; span > 0; span--) {
                for (int begin = 0; begin < chart.size() - span; begin++) {
                    int end = begin + span;
                    System.out.println(spacer + begin + "," + end);
                    Map<Object,Double> counter = chart.get(begin).get(end);
                    Map<Object,Triplet<Integer,Object,Object>> backptr = backs.get(begin).get(end);
                    for (Object o: counter.keySet()) {
                        System.out.println(spacer + " " + o  
                            + " : " + counter.get(o) 
                            + " : " + backptr.get(o));
                    }
                }
                spacer += "\t";
            }
            System.out.println("-------------------- ***** --------------------");
        }

        private static List<Object> copyKeys(Map<Object,Double> counter) {
            List<Object> keys = new ArrayList<Object>();
            for (Object k: counter.keySet()) {
                keys.add(k);
            }
            return keys;
        }

        private Tree<String> makeTree(
                            List<List<Map<Object,Triplet<Integer,Object,Object>>>> backs, 
                            int begin, int end, Object A) {

            Triplet<Integer,Object,Object> backptr = backs.get(begin).get(end).get(A);
            String tag = getParent(A);

            //System.out.println("makeTree: begin=" + begin + ",end=" + end + ",A=" + A + " : " + "backptr=" + backptr);

            List<Tree<String>> children = new ArrayList<Tree<String>>();
            
            if (backptr == null) { 
                // No back pointer. Terminal
                Tree<String> child = new Tree<String>(((UnaryRule)A).getChild()); 
                children.add(child);
            } else  if (backptr.getFirst() < 0) {
                // Single back pointer. Unary rule 
                Object B = backptr.getSecond();
                Tree<String> child = makeTree(backs, begin, end, B); 
                children.add(child);
            } else {
                // Two back pointers. Binary rule
                int split = backptr.getFirst();
                Object B = backptr.getSecond();
                Object C = backptr.getThird();
                Tree<String> childB = makeTree(backs, begin, split, B);
                Tree<String> childC = makeTree(backs, split, end, C);
                children.add(childB);
                children.add(childC);
            }
            return new Tree<String>(tag, children);
        }  
    
        public Tree<String> getBestParse(List<String> sentence) {
            // TODO: implement this method
            int n = sentence.size();

            //System.out.println("getBestParse: n=" + n);

            List<List<Map<Object,Double>>> scores = new ArrayList<List<Map<Object,Double>>>(n+1);
            for (int i = 0; i < n+1; i++) {
                List<Map<Object,Double>> row = new ArrayList<Map<Object,Double>>(n+1);
                for (int j = 0; j < n+1; j++) {
                    row.add(new HashMap<Object,Double>());
                }
                scores.add(row);
            }
            List<List<Map<Object,Triplet<Integer,Object,Object>>>> backs = new ArrayList<List<Map<Object,Triplet<Integer,Object,Object>>>>(n+1);
            for (int i = 0; i < n+1; i++) {
                List<Map<Object,Triplet<Integer,Object,Object>>> row = new ArrayList<Map<Object,Triplet<Integer,Object,Object>>>(n+1);
                for (int j = 0; j < n+1; j++) {
                    row.add(new HashMap<Object,Triplet<Integer,Object,Object>>());
                }
                backs.add(row);
            }

            /*
            System.out.println("scores=" + scores.size() + "x" + scores.get(0).size());
            System.out.println("backs=" + backs.size() + "x" + backs.get(0).size());
            printChart(scores, backs, "scores");
            */              
            // First the Lexicon
            
            for (int i = 0; i < n; i++) {
                String word = sentence.get(i);
                for (String tag : lexicon.getAllTags()) {
                    UnaryRule A = new UnaryRule(tag, word);
                    A.setScore(Math.log(lexicon.scoreTagging(word, tag)));
                    scores.get(i).get(i+1).put(A, A.getScore()); 
                    backs.get(i).get(i+1).put(A, null);
                }

				//System.out.println("Starting unaries: i=" + i + ",n=" + n );
                // Handle unaries
                boolean added = true;
                while (added) {
                    added = false;
                    Map<Object,Double> A_scores = scores.get(i).get(i+1);
                    // Don't modify the dict we are iterating
                    List<Object> A_keys = copyKeys(A_scores);
					//for (int j = 0; j < 5 && j < A_keys.size(); j++) {
					//	System.out.print("," + j + "=" + A_scores.get(A_keys.get(j)));  
					//}
                    
                    for (Object oB : A_keys) {
                        UnaryRule B = (UnaryRule)oB;
                        for (UnaryRule A : grammar.getUnaryRulesByChild(B.getParent())) {
                            double prob = Math.log(A.getScore()) + A_scores.get(B); 
                            if (prob > -1000.0) {
								
								if (!A_scores.containsKey(A) || prob > A_scores.get(A)) {
									//System.out.print(" *A=" + A + ", B=" + B);
									//System.out.print(",  prob=" +  prob);
									//System.out.println(",  A_scores.get(A)=" +  A_scores.get(A));
									A_scores.put(A, prob);
									backs.get(i).get(i+1).put(A, new Triplet<Integer,Object,Object>(-1, B, null));
									added = true;
								}
								//System.out.println(", added=" + added);
							}
							
                        } 
                    } 
					//System.out.println(", A_scores=" + A_scores.size() + ", added=" + added);	
                }
            }

            //printChart(scores, backs, "scores with Lexicon");

            // Do higher layers  
            // Naming is based on rules: A -> B,C
        
            long startTime = new Date().getTime();
            for (int span = 2; span < n + 1; span++) {

                for (int begin = 0; begin < n + 1 - span; begin++) {
                    int end = begin + span;

                    Map<Object,Double> A_scores = scores.get(begin).get(end);
                    Map<Object,Triplet<Integer,Object,Object>> A_backs = backs.get(begin).get(end);

                    for (int split = begin + 1; split < end; split++) {

                        Map<Object,Double> B_scores = scores.get(begin).get(split);
                        Map<Object,Double> C_scores = scores.get(split).get(end);
                        
                        List<Object> B_list = new ArrayList<Object>(B_scores.keySet());
                        List<Object> C_list = new ArrayList<Object>(C_scores.keySet());

                        // This is a key optimization. !@#$
                        // It avoids a B_list.size() x C_list.size() search in the for (Object B : B_list) loop 
                        Map<String,List<Object>> C_map = new HashMap<String,List<Object>>();
                        for (Object C : C_list) {
                            String parent = getParent(C);
                            if (!C_map.containsKey(parent)) {
                                C_map.put(parent, new ArrayList<Object>());     
                            }
                            C_map.get(parent).add(C);
                        }

                        for (Object B : B_list) { 
                            for (BinaryRule A : grammar.getBinaryRulesByLeftChild(getParent(B))) {
                                if (C_map.containsKey(A.getRightChild())) {
                                    for (Object C : C_map.get(A.getRightChild())) {
                                        // We now have A which has B as left child and C as right child 
                                        double prob = Math.log(A.getScore()) + B_scores.get(B) + C_scores.get(C);
                                        if (!A_scores.containsKey(A) || prob > A_scores.get(A)) {
                                            A_scores.put(A, prob);
                                            A_backs.put(A, new Triplet<Integer,Object,Object>(split, B, C));
                                        }
                                    } 
                                }
                            }
                        }

                    }
                   
                    // Handle unaries: A -> B
                    boolean added = true;
                    while (added) {
                        added = false;
                        // Don't modify the dict we are iterating
                        List<Object> A_keys = copyKeys(A_scores);
                        for (Object oB : A_keys) {
                            for (UnaryRule A : grammar.getUnaryRulesByChild(getParent(oB))) {
                                double prob = Math.log(A.getScore()) + A_scores.get(oB); 
                                if (!A_scores.containsKey(A) || prob > A_scores.get(A)) {
                                    A_scores.put(A, prob);
                                    A_backs.put(A, new Triplet<Integer,Object,Object>(-1, oB, null));
                                    added = true;
                                }
                            }
                        }
                    }
                   
                }    
            }

            //printChart(scores, backs, "scores with Lexicon and Grammar");
            
            Map<Object,Double> topOfChart = scores.get(0).get(n);
            
            System.out.println("topOfChart: " + topOfChart.size());
            /*
            for (Object o: topOfChart.keySet()) {
                System.out.println("o=" + o + ", score=" + topOfChart.getCount(o));
            }
            */
         
            // All parses have "ROOT" at top of tree
            Object bestKey = null;
            Object secondBestKey = null;
            double bestScore = Double.NEGATIVE_INFINITY;
            double secondBestScore = Double.NEGATIVE_INFINITY;
            for (Object key: topOfChart.keySet()) {
                double score = topOfChart.get(key);
                if (score >= secondBestScore || secondBestKey == null) {
                    secondBestKey = key;
                    secondBestScore = score;
                }
                if ("ROOT".equals(getParent(key)) && (score >= bestScore || bestKey == null)) {
                    bestKey = key;
                    bestScore = score;
                }
            }
            
           if (bestKey == null) {
                bestKey = secondBestKey;
                System.out.println("secondBestKey=" + secondBestKey);
            }
            if (bestKey == null) {
                for (Object key: topOfChart.keySet()) {
                    System.out.println("val=" + topOfChart.get(key) + ", key=" + key);
                }
            }
            System.out.println("bestKey=" + bestKey + ", log(prob)=" + topOfChart.get(bestKey));
            
            Tree<String> result = makeTree(backs, 0, n, bestKey);
            if (!"ROOT".equals(result.getLabel())) {
                List<Tree<String>> children = new ArrayList<Tree<String>>();
                children.add(result);
                result = new Tree<String>("ROOT", children); // !@#$
            }
            
            /*
            System.out.println("==================================================");
            System.out.println(result);
            System.out.println("====================^^^^^^========================");
            */
            return TreeAnnotations.unAnnotateTree(result);
        }
        
    }

  // BaselineParser =============================================================

  /**
   * Baseline parser (though not a baseline I've ever seen before).  Tags the
   * sentence using the baseline tagging method, then either retrieves a known
   * parse of that tag sequence, or builds a right-branching parse for unknown
   * tag sequences.
   */
    public static class BaselineParser implements Parser {

        CounterMap<List<String>,Tree<String>> knownParses;
        CounterMap<Integer,String> spanToCategories;
        Lexicon lexicon;

        public void train(List<Tree<String>> trainTrees) {
            lexicon = new Lexicon(trainTrees);
            knownParses = new CounterMap<List<String>, Tree<String>>();
            spanToCategories = new CounterMap<Integer, String>();
            for (Tree<String> trainTree : trainTrees) {
                List<String> tags = trainTree.getPreTerminalYield();
                knownParses.incrementCount(tags, trainTree, 1.0);
                tallySpans(trainTree, 0);
            }
        }

    public Tree<String> getBestParse(List<String> sentence) {
      List<String> tags = getBaselineTagging(sentence);
      if (knownParses.keySet().contains(tags)) {
        return getBestKnownParse(tags, sentence);
      }
      return buildRightBranchParse(sentence, tags);
    }

    /* Builds a tree that branches to the right.  For pre-terminals it
     * uses the most common tag for the word in the training corpus.
     * For all other non-terminals it uses the tag that is most common
     * in training corpus of tree of the same size span as the tree
     * that is being labeled. 
     */
    private Tree<String> buildRightBranchParse(List<String> words, List<String> tags) {
      int currentPosition = words.size() - 1;
      Tree<String> rightBranchTree = buildTagTree(words, tags, currentPosition);
      while (currentPosition > 0) {
        currentPosition--;
        rightBranchTree = merge(buildTagTree(words, tags, currentPosition),
                                rightBranchTree);
      }
      rightBranchTree = addRoot(rightBranchTree);
      return rightBranchTree;
    }

    private Tree<String> merge(Tree<String> leftTree, Tree<String> rightTree) {
        int span = leftTree.getYield().size() + rightTree.getYield().size();
        String mostFrequentLabel = spanToCategories.getCounter(span).argMax();
        List<Tree<String>> children = new ArrayList<Tree<String>>();
        children.add(leftTree);
        children.add(rightTree);
        return new Tree<String>(mostFrequentLabel, children);
    }

    private Tree<String> addRoot(Tree<String> tree) {
      return new Tree<String>("ROOT", Collections.singletonList(tree));
    }

    private Tree<String> buildTagTree(List<String> words,
                                      List<String> tags,
                                      int currentPosition) {
      Tree<String> leafTree = new Tree<String>(words.get(currentPosition));
      Tree<String> tagTree = new Tree<String>(tags.get(currentPosition), 
                                              Collections.singletonList(leafTree));
      return tagTree;
    }
    
    private Tree<String> getBestKnownParse(List<String> tags, List<String> sentence) {
        Tree<String> parse = knownParses.getCounter(tags).argMax().deepCopy();
        parse.setWords(sentence);
        return parse;
    }

    private List<String> getBaselineTagging(List<String> sentence) {
      List<String> tags = new ArrayList<String>();
      for (String word : sentence) {
        String tag = getBestTag(word);
        tags.add(tag);
      }
      return tags;
    }

    private String getBestTag(String word) {
      double bestScore = Double.NEGATIVE_INFINITY;
      String bestTag = null;
      for (String tag : lexicon.getAllTags()) {
        double score = lexicon.scoreTagging(word, tag);
        if (bestTag == null || score > bestScore) {
          bestScore = score;
          bestTag = tag;
        }
      }
      return bestTag;
    }

    private int tallySpans(Tree<String> tree, int start) {
        if (tree.isLeaf() || tree.isPreTerminal()) {
            return 1;
        }
        int end = start;
        for (Tree<String> child : tree.getChildren()) {
            int childSpan = tallySpans(child, end);
            end += childSpan;
        }
        String category = tree.getLabel();
        if (! category.equals("ROOT")) {
            spanToCategories.incrementCount(end - start, category, 1.0);
        }
        return end - start;
    }

  }

  // TreeAnnotations ============================================================

  /**
   * Class which contains code for annotating and binarizing trees for
   * the parser's use, and debinarizing and unannotating them for
   * scoring.
   */
    public static class TreeAnnotations {

        public static Tree<String> annotateTree(Tree<String> unAnnotatedTree) {

            // Currently, the only annotation done is a lossless binarization

            // TODO: change the annotation from a lossless binarization to a
            // finite-order markov process (try at least 1st and 2nd order)
            // mark nodes with the label of their parent nodes, giving a second
            // order vertical markov process

            return binarizeTree(unAnnotatedTree);
        }
    
        private static Tree<String> binarizeTree(Tree<String> tree) {
            String label = tree.getLabel();
            if (tree.isLeaf()) {
                return new Tree<String>(label);
            }
            
            /*
            // [Average]    P: 48.53   R: 47.67   F1: 48.10   EX:  4.85
            if (tree.getChildren().size() == 1) {
                return new Tree<String>(label, Collections.singletonList(binarizeTree(tree.getChildren().get(0))));
            }
          */
          
          //  [Average]    P: 48.53   R: 47.67   F1: 48.10   EX:  4.85              
            if (tree.getChildren().size() <= 2) {
                List<Tree<String>> children = new ArrayList<Tree<String>>(2);
                for (Tree<String> child: tree.getChildren()) { 
                    children.add(binarizeTree(child));
                }
                return new Tree<String>(label, children);
            }
       
            // otherwise, it's a binary-or-more local tree, 
            // so decompose it into a sequence of binary and unary trees.
            String intermediateLabel = "@" + label + "->";
            Tree<String> intermediateTree = binarizeTreeHelper(tree, 0, intermediateLabel);
            return new Tree<String>(label, intermediateTree.getChildren());
        }

        private static Tree<String> binarizeTreeHelper(Tree<String> tree,
                                                   int numChildrenGenerated, 
                                                   String intermediateLabel) {
            Tree<String> leftTree = tree.getChildren().get(numChildrenGenerated);
            List<Tree<String>> children = new ArrayList<Tree<String>>();
            children.add(binarizeTree(leftTree));
            if (numChildrenGenerated < tree.getChildren().size() - 1) {
                Tree<String> rightTree = binarizeTreeHelper(tree, numChildrenGenerated + 1, 
                                                intermediateLabel + "_" + leftTree.getLabel());
                children.add(rightTree);
            }
            return new Tree<String>(intermediateLabel, children);
        } 
 
        public static Tree<String> unAnnotateTree(Tree<String> annotatedTree) {

          // Remove intermediate nodes (labels beginning with "@"
          // Remove all material on node labels which follow their base symbol 
          // (cuts at the leftmost -, ^, or : character)
          // Examples: a node with label @NP->DT_JJ will be spliced out, 
          // and a node with label NP^S will be reduced to NP

            Tree<String> debinarizedTree =
                Trees.spliceNodes(annotatedTree, new Filter<String>() {
                    public boolean accept(String s) {
                        return s.startsWith("@");
                    }
                });
            Tree<String> unAnnotatedTree = (new Trees.FunctionNodeStripper()).transformTree(debinarizedTree);
            return unAnnotatedTree;
        }
    }


  // Lexicon ====================================================================

  /**
   * Simple default implementation of a lexicon, which scores word,
   * tag pairs with a smoothed estimate of P(tag|word)/P(tag).
   */
    public static class Lexicon {

        CounterMap<String,String> wordToTagCounters = new CounterMap<String, String>();
        double totalTokens = 0.0;
        double totalWordTypes = 0.0;
        Counter<String> tagCounter = new Counter<String>();
        Counter<String> wordCounter = new Counter<String>();
        Counter<String> typeTagCounter = new Counter<String>();

        public Set<String> getAllTags() {
            return tagCounter.keySet();
        }

        public boolean isKnown(String word) {
            return wordCounter.keySet().contains(word);
        }

        /* Returns a smoothed estimate of P(word|tag) */
        public double scoreTagging(String word, String tag) {
            double p_tag = tagCounter.getCount(tag) / totalTokens;
            double c_word = wordCounter.getCount(word);
            double c_tag_and_word = wordToTagCounters.getCount(word, tag);
            if (c_word < 10) { // rare or unknown
                c_word += 1.0;
                c_tag_and_word += typeTagCounter.getCount(tag) / totalWordTypes;
            }
            double p_word = (1.0 + c_word) / (totalTokens + totalWordTypes);
            double p_tag_given_word = c_tag_and_word / c_word;
            return p_tag_given_word / p_tag * p_word;
        }

        /* Builds a lexicon from the observed tags in a list of training trees. */
        public Lexicon(List<Tree<String>> trainTrees) {
            for (Tree<String> trainTree : trainTrees) {
                List<String> words = trainTree.getYield();
                List<String> tags = trainTree.getPreTerminalYield();
                for (int position = 0; position < words.size(); position++) {
                    String word = words.get(position);
                    String tag = tags.get(position);
                    tallyTagging(word, tag);
                }
            }
        }

        private void tallyTagging(String word, String tag) {
            if (! isKnown(word)) {
                totalWordTypes += 1.0;
                typeTagCounter.incrementCount(tag, 1.0);
            }
            totalTokens += 1.0;
            tagCounter.incrementCount(tag, 1.0);
            wordCounter.incrementCount(word, 1.0);
            wordToTagCounters.incrementCount(word, tag, 1.0);
        }
    }

  // Grammar ====================================================================

  /**
   * Simple implementation of a PCFG grammar, offering the ability to
   * look up rules by their child symbols.  Rule probability estimates
   * are just relative frequency estimates off of training trees.
   */
    public static class Grammar {

        Map<String, List<BinaryRule>> binaryRulesByLeftChild = new HashMap<String, List<BinaryRule>>();
        Map<String, List<BinaryRule>> binaryRulesByRightChild = new HashMap<String, List<BinaryRule>>();
        Map<String, List<UnaryRule>> unaryRulesByChild = new HashMap<String, List<UnaryRule>>();

        /* Rules in grammar are indexed by child for easy access when
         * doing bottom up parsing. 
         */
        public List<BinaryRule> getBinaryRulesByLeftChild(String leftChild) {
            return CollectionUtils.getValueList(binaryRulesByLeftChild, leftChild);
        }

        public List<BinaryRule> getBinaryRulesByRightChild(String rightChild) {
            return CollectionUtils.getValueList(binaryRulesByRightChild, rightChild);
        }

        public List<UnaryRule> getUnaryRulesByChild(String child) {
            return CollectionUtils.getValueList(unaryRulesByChild, child);
        }

        public String toString() {
          StringBuilder sb = new StringBuilder();
          List<String> ruleStrings = new ArrayList<String>();
          for (String leftChild : binaryRulesByLeftChild.keySet()) {
            for (BinaryRule binaryRule : getBinaryRulesByLeftChild(leftChild)) {
              ruleStrings.add(binaryRule.toString());
            }
          }
          for (String child : unaryRulesByChild.keySet()) {
            for (UnaryRule unaryRule : getUnaryRulesByChild(child)) {
              ruleStrings.add(unaryRule.toString());
            }
          }
          for (String ruleString : CollectionUtils.sort(ruleStrings)) {
            sb.append(ruleString);
            sb.append("\n");
          }
          return sb.toString();
        }

        private void addBinary(BinaryRule binaryRule) {
            CollectionUtils.addToValueList(binaryRulesByLeftChild, binaryRule.getLeftChild(), binaryRule);
            CollectionUtils.addToValueList(binaryRulesByRightChild, binaryRule.getRightChild(), binaryRule);
        }

        private void addUnary(UnaryRule unaryRule) {
            CollectionUtils.addToValueList(unaryRulesByChild, unaryRule.getChild(), unaryRule);
        }

        /* A builds PCFG using the observed counts of binary and unary
         * productions in the training trees to estimate the probabilities
         * for those rules.  
         */ 
        public Grammar(List<Tree<String>> trainTrees) {
            Counter<UnaryRule> unaryRuleCounter = new Counter<UnaryRule>();
            Counter<BinaryRule> binaryRuleCounter = new Counter<BinaryRule>();
            Counter<String> symbolCounter = new Counter<String>();
            for (Tree<String> trainTree : trainTrees) {
                tallyTree(trainTree, symbolCounter, unaryRuleCounter, binaryRuleCounter);
            }
            for (UnaryRule unaryRule : unaryRuleCounter.keySet()) {
                double unaryProbability = unaryRuleCounter.getCount(unaryRule) / symbolCounter.getCount(unaryRule.getParent());
                unaryRule.setScore(unaryProbability);
                addUnary(unaryRule);
            }
            for (BinaryRule binaryRule : binaryRuleCounter.keySet()) {
                double binaryProbability = binaryRuleCounter.getCount(binaryRule) / symbolCounter.getCount(binaryRule.getParent());
                binaryRule.setScore(binaryProbability);
                addBinary(binaryRule);
            }
        }

        private void tallyTree(Tree<String> tree, Counter<String> symbolCounter,
                               Counter<UnaryRule> unaryRuleCounter, 
                               Counter<BinaryRule> binaryRuleCounter) {
            if (tree.isLeaf()) return;
            if (tree.isPreTerminal()) return;
            if (tree.getChildren().size() == 1) {
                UnaryRule unaryRule = makeUnaryRule(tree);
                symbolCounter.incrementCount(tree.getLabel(), 1.0);
                unaryRuleCounter.incrementCount(unaryRule, 1.0);
            }
            if (tree.getChildren().size() == 2) {
                BinaryRule binaryRule = makeBinaryRule(tree);
                symbolCounter.incrementCount(tree.getLabel(), 1.0);
                binaryRuleCounter.incrementCount(binaryRule, 1.0);
            }
            if (tree.getChildren().size() < 1 || tree.getChildren().size() > 2) {
                throw new RuntimeException("Attempted to construct a Grammar with an illegal tree: "+tree);
            }
            for (Tree<String> child : tree.getChildren()) {
                tallyTree(child, symbolCounter, unaryRuleCounter,  binaryRuleCounter);
            }
        }

        private UnaryRule makeUnaryRule(Tree<String> tree) {
            return new UnaryRule(tree.getLabel(), tree.getChildren().get(0).getLabel());
        }

        private BinaryRule makeBinaryRule(Tree<String> tree) {
            return new BinaryRule(tree.getLabel(), 
                                  tree.getChildren().get(0).getLabel(), 
                                  tree.getChildren().get(1).getLabel());
        }
    }


  // BinaryRule =================================================================

  /* A binary grammar rule with score representing its probability. */
  public static class BinaryRule {

    String parent;
    String leftChild;
    String rightChild;
    double score;

    public String getParent() {
      return parent;
    }

    public String getLeftChild() {
      return leftChild;
    }

    public String getRightChild() {
      return rightChild;
    }

    public double getScore() {
      return score;
    }

    public void setScore(double score) {
      this.score = score;
    }

    public boolean equals(Object o) {
      if (this == o) return true;
      if (!(o instanceof BinaryRule)) return false;

      final BinaryRule binaryRule = (BinaryRule) o;

      if (leftChild != null ? !leftChild.equals(binaryRule.leftChild) : binaryRule.leftChild != null) 
        return false;
      if (parent != null ? !parent.equals(binaryRule.parent) : binaryRule.parent != null) 
        return false;
      if (rightChild != null ? !rightChild.equals(binaryRule.rightChild) : binaryRule.rightChild != null) 
        return false;

      return true;
    }

    public int hashCode() {
      int result;
      result = (parent != null ? parent.hashCode() : 0);
      result = 29 * result + (leftChild != null ? leftChild.hashCode() : 0);
      result = 29 * result + (rightChild != null ? rightChild.hashCode() : 0);
      return result;
    }

    public String toString() {
      return parent + " -> " + leftChild + " " + rightChild + " %% "+score;
    }

    public BinaryRule(String parent, String leftChild, String rightChild) {
      this.parent = parent;
      this.leftChild = leftChild;
      this.rightChild = rightChild;
    }
  }

  // UnaryRule ==================================================================

  /** A unary grammar rule with score representing its probability. */
  public static class UnaryRule {

    String parent;
    String child;
    double score;

    public String getParent() {
      return parent;
    }

    public String getChild() {
      return child;
    }

    public double getScore() {
      return score;
    }

    public void setScore(double score) {
      this.score = score;
    }

    public boolean equals(Object o) {
      if (this == o) return true;
      if (!(o instanceof UnaryRule)) return false;

      final UnaryRule unaryRule = (UnaryRule) o;

      if (child != null ? !child.equals(unaryRule.child) : unaryRule.child != null) return false;
      if (parent != null ? !parent.equals(unaryRule.parent) : unaryRule.parent != null) return false;

      return true;
    }

    public int hashCode() {
      int result;
      result = (parent != null ? parent.hashCode() : 0);
      result = 29 * result + (child != null ? child.hashCode() : 0);
      return result;
    }

    public String toString() {
      return parent + " -> " + child + " %% "+score;
    }

    public UnaryRule(String parent, String child) {
      this.parent = parent;
      this.child = child;
    }
  }


  // PCFGParserTester ===========================================================

    // Longest sentence length that will be tested on.
    private static int MAX_LENGTH = 20;
 
    private static double testParser(Parser parser, List<Tree<String>> testTrees) {
        EnglishPennTreebankParseEvaluator.LabeledConstituentEval<String> eval = 
            new EnglishPennTreebankParseEvaluator.LabeledConstituentEval<String>(
                Collections.singleton("ROOT"), 
                new HashSet<String>(Arrays.asList(new String[] {"''", "``", ".", ":", ","})));
        for (Tree<String> testTree : testTrees) {
            List<String> testSentence = testTree.getYield();

            if (testSentence.size() > MAX_LENGTH)
                continue;
            Tree<String> guessedTree = parser.getBestParse(testSentence);
            System.out.println("Guess:\n"+Trees.PennTreeRenderer.render(guessedTree));
            System.out.println("Gold:\n"+Trees.PennTreeRenderer.render(testTree));
            eval.evaluate(guessedTree, testTree);
        }   
        System.out.println();
        return eval.display(true);
    }
  
    private static List<Tree<String>> readTrees(String basePath, int low, int high) {
        Collection<Tree<String>> trees = PennTreebankReader.readTrees(basePath, low, high);
        // normalize trees
        Trees.TreeTransformer<String> treeTransformer = new Trees.StandardTreeNormalizer();
        List<Tree<String>> normalizedTreeList = new ArrayList<Tree<String>>();
        for (Tree<String> tree : trees) {
            Tree<String> normalizedTree = treeTransformer.transformTree(tree);
            // System.out.println(Trees.PennTreeRenderer.render(normalizedTree));
            normalizedTreeList.add(normalizedTree);
        }
        return normalizedTreeList;
    }

    private static List<Tree<String>> readTrees(String basePath) {
        Collection<Tree<String>> trees = PennTreebankReader.readTrees(basePath);
        // normalize trees
        Trees.TreeTransformer<String> treeTransformer = new Trees.StandardTreeNormalizer();
        List<Tree<String>> normalizedTreeList = new ArrayList<Tree<String>>();
        for (Tree<String> tree : trees) {
          //      System.err.println(tree);
          Tree<String> normalizedTree = treeTransformer.transformTree(tree);
          // System.out.println(Trees.PennTreeRenderer.render(normalizedTree));
          normalizedTreeList.add(normalizedTree);
        }
        return normalizedTreeList;
    }


  private static List<Tree<String>> readMASCTrees(String basePath, int low, int high) {
    System.out.println("MASC basepath: " + basePath);
    Collection<Tree<String>> trees = MASCTreebankReader.readTrees(basePath, low, high);
    // normalize trees
    Trees.TreeTransformer<String> treeTransformer = new Trees.StandardTreeNormalizer();
    List<Tree<String>> normalizedTreeList = new ArrayList<Tree<String>>();
    for (Tree<String> tree : trees) {
      Tree<String> normalizedTree = treeTransformer.transformTree(tree);
      // System.out.println(Trees.PennTreeRenderer.render(normalizedTree));
      normalizedTreeList.add(normalizedTree);
    }
    return normalizedTreeList;
  }


  private static List<Tree<String>> readMASCTrees(String basePath) {
    System.out.println("MASC basepath: " + basePath);
    Collection<Tree<String>> trees = MASCTreebankReader.readTrees(basePath);
    // normalize trees
    Trees.TreeTransformer<String> treeTransformer = new Trees.StandardTreeNormalizer();
    List<Tree<String>> normalizedTreeList = new ArrayList<Tree<String>>();
    for (Tree<String> tree : trees) {
      Tree<String> normalizedTree = treeTransformer.transformTree(tree);
      // System.out.println(Trees.PennTreeRenderer.render(normalizedTree));
      normalizedTreeList.add(normalizedTree);
    }
    return normalizedTreeList;
  }
  
  
  public static void main(String[] args) {

    // set up default options ..............................................
    Map<String, String> options = new HashMap<String, String>();
    options.put("--path",      "../data/parser/");
    options.put("--data",      "masc");
    options.put("--parser",    "nlpclass.assignments.PCFGParserTester$BaselineParser");
    options.put("--maxLength", "20");

    // let command-line options supersede defaults .........................
    options.putAll(CommandLineUtils.simpleCommandLineParser(args));
    System.out.println("PCFGParserTester options:");
    for (Map.Entry<String, String> entry: options.entrySet()) {
        System.out.printf("  %-12s: %s%n", entry.getKey(), entry.getValue());
    }
    System.out.println();

    MAX_LENGTH = Integer.parseInt(options.get("--maxLength"));

    Parser parser;
    try {
        Class parserClass = Class.forName(options.get("--parser"));
        parser = (Parser) parserClass.newInstance();
    } catch (Exception e) {
        throw new RuntimeException(e);
    }
    System.out.println("Using parser: " + parser);

    String basePath = options.get("--path");
    String preBasePath = basePath;
    String dataSet = options.get("--data");
    if (!basePath.endsWith("/")) {
        basePath += "/";
    }
    //basePath += dataSet;
    System.out.println("Data will be loaded from: " + basePath + "\n");

    List<Tree<String>> trainTrees = new ArrayList<Tree<String>>();
    List<Tree<String>> validationTrees = new ArrayList<Tree<String>>();
    List<Tree<String>> testTrees = new ArrayList<Tree<String>>();

    if (dataSet.equals("miniTest")) {
        // training data: first 3 of 4 datums
        basePath += "parser/"+dataSet;
        System.out.println("Loading training trees...");
        trainTrees = readTrees(basePath, 1, 3);
        System.out.println("done.");

        // test data: last of 4 datums
        System.out.println("Loading test trees...");
        testTrees = readTrees(basePath, 4, 4);
        System.out.println("done.");
    }
    else if (dataSet.equals("masc")) {
        basePath += "parser/";
        // training data: MASC train
        System.out.println("Loading MASC training trees... from: "+basePath+"masc/train");
        trainTrees.addAll(readMASCTrees(basePath+"masc/train", 0, 38));
        System.out.println("done.");
        System.out.println("Train trees size: "+trainTrees.size());

        System.out.println("First train tree: "+Trees.PennTreeRenderer.render(trainTrees.get(0)));
        System.out.println("Last train tree: "+Trees.PennTreeRenderer.render(trainTrees.get(trainTrees.size()-1)));

        // test data: MASC devtest
        System.out.println("Loading MASC test trees...");
        testTrees.addAll(readMASCTrees(basePath+"masc/devtest", 0, 11));
        //testTrees.addAll(readMASCTrees(basePath+"masc/blindtest", 0, 8));
        System.out.println("Test trees size: "+testTrees.size());
        System.out.println("done.");

        System.out.println("First test tree: "+Trees.PennTreeRenderer.render(testTrees.get(0)));
        System.out.println("Last test tree: "+Trees.PennTreeRenderer.render(testTrees.get(testTrees.size()-1)));
    }
    else if (!dataSet.equals("miniTest") && !dataSet.equals("masc")){
      throw new RuntimeException("Bad data set: " + dataSet + ": use miniTest or masc."); 
    }

    System.out.println("\nTraining parser...");
    parser.train(trainTrees);

    System.out.println("\nTesting parser...");
    testParser(parser, testTrees);
  }
}
