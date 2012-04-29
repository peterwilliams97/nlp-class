
def get_data(path):
    return [tuple(line.strip().split('\t')) for line in open(path, 'rt')]
    
def print_dict(name, d):    
    print '%s : %s' % ('-' * 40, name)
    for k in sorted(d.keys()):
        print '%30s : %s' % (k, d[k])

def main(path):
    """Print the unique emails and telephone numbers in the results"""
    data = get_data(path)
    emails = dict([(d[2], d[0]) for d in data if d[1] == 'e']) 
    phones = dict([(d[2], d[0]) for d in data if d[1] == 'p']) 

    print_dict('emails', emails)
    print_dict('phones', phones)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print 'usage: ' + sys.argv[0] + ' <results>'
        sys.exit(0)
    main(sys.argv[1])
