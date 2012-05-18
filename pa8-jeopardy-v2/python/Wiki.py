import sys, traceback, re

_RE_START_INFO_BOX = re.compile(r'\{\{Infobox')
_RE_END_INFO_BOX = re.compile(r'\}\}')
_RE_INFO_BOX_NAME = re.compile(r'\|name\s*=\s*(\S.+\S)\s*$')
_RE_INFO_BOX_WIFE = re.compile(r'\|spouse\s*=.*\[\[(.+)\]\]')

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

def parse_infobox(f):
    """Generator for extractiong info box fields from f which is a text file, hence
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

        
        # TODO:
        # Process the wiki file and fill the husbands Array
        # +1 for correct Answer, 0 for no answer, -1 for wrong answers
        # add 'No Answer' string as the answer when you dont want to answer
        
        for wife in wives:
            if useInfoBox: 
                wife = wife.strip()
                if wife in wife_husband_map:
                    husband = 'Who is %s?' % wife_husband_map[wife] 
                else:
                    husband = 'No Answer'
                husbands.append(husband) 
            else:
                husbands.append('No Answer')
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
    useInfoBox = True;
    wiki = Wiki()
    wives = wiki.addWives(wivesFile)
    husbands = wiki.processFile(open(wikiFile), wives, useInfoBox)
    wiki.evaluateAnswers(useInfoBox, husbands, goldFile)
    