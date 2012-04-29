#!/usr/bin/env python

"""
Original author: Paul Boddie <paul@boddie.org.uk>

To the extent possible under law, the person who associated CC0 with this work
has waived all copyright and related or neighboring rights to this work.

See: http://creativecommons.org/publicdomain/zero/1.0/
"""

import sgmllib

class MyParser(sgmllib.SGMLParser):
    "A simple parser class."

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."

        sgmllib.SGMLParser.__init__(self, verbose)
        self.hyperlinks = []

    def start_a(self, attributes):
        "Process a hyperlink and its 'attributes'."

        for name, value in attributes:
            if name == "href":
                self.hyperlinks.append(value)

    def get_hyperlinks(self):
        "Return the list of hyperlinks."

        return self.hyperlinks

import urllib, sgmllib
import sys

def D(msg): sys.stderr.write(msg + '\n')

def get_page_data(url):
    """Return content of page with url """
    try:
        f = urllib.urlopen(url)
        page_data = f.read()
        return page_data
    except:
        return ''
    
def get_links(page_data, url_pattern): 
    myparser = MyParser()
    myparser.parse(page_data)

    # Get the hyperlinks.
    links = myparser.get_hyperlinks()
    links = [x for x in links if x.startswith('http:') and url_pattern in x.lower()]
    return links

def add_dicts(d1, d2):
    return dict(d1.items() + d2.items())

def traverse_level(tree, depth, visited, process, url_pattern):
    """Traverse a level of the link tree""" 
    
    D('-' * 80)
    #print tree, depth, visited
    targets = tree[depth] - visited
    D(' ' * depth + '%2d: Total=%4d - Unvisited=%4d' % (depth, len(tree[depth]), len(targets)))
    
    uniques = {}    
    for url in sorted(targets):
        
        page_data = get_page_data(url)
        visited.add(url)
        
        uniques = add_dicts(uniques, process(url, page_data, depth))
        
        try:                
            links = get_links(page_data, url_pattern)
        except Exception :
            D('exception!!')
            continue 
        tree[depth+1] = tree.get(depth+1, set([])) | set(links)    
    
    #print '=' * 80
    #print tree, depth, visited
    return uniques

import pprint
_pp = pprint.PrettyPrinter(indent=4,width=160)

def print_uniques(uniques):
    if not uniques:
        return
    if False:
        _pp.pprint(uniques)
        print   # Flush stdout
    else:    
        for k in sorted(uniques.keys()):
            v = uniques[k]
        print '%s\t%s\t%s' % (v[0], v[1], k)

import SpamLord
def get_personal_info(url, data, depth):
    
    result = SpamLord.extract_personal_info(url, data)
    uniques = dict([(e[2].strip('\n'), (e[0],e[1])) for e in result])
    D(' ' * depth + ' name=%s' % url)
    print_uniques(uniques)
    return uniques

def explore(start_url, url_pattern):    
    start_depth = 0         
    url_tree = { start_depth: set([start_url]) }     
    all_uniques = {}    
    for depth in range(start_depth, 6):
        if len(url_tree[depth]) == 0:
            D('No more levels. Exiting')
            exit()
        all_uniques = add_dicts(all_uniques, traverse_level(url_tree, depth, set([]), 
            get_personal_info, url_pattern))       

    print '=' * 80
    print_uniques(all_uniques)
    
if __name__ == '__main__':
    if len(sys.argv) <= 2:
        D('Usage: ' + sys.argv[0] + ' start_url url_pattern')
        exit()
    #start_url = 'http://www.python.org'
    #start_url = 'http://www.stanford.edu/'    
    start_url = sys.argv[1]
    url_pattern = sys.argv[2]
    explore(start_url, url_pattern)
    