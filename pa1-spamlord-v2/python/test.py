import sys
import SpamLord

def get_personal_info(path):
    data = file(path, 'rt').read()
    result = SpamLord.extract_personal_info(path, data)
    print result
    uniques = dict([(e[2].strip('\n'), (e[0],e[1])) for e in result])
    print '\n'.join(['%30s : %s' % (k,v) for (k,v) in uniques.items()])

    
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        D('Usage: ' + sys.argv[0] + ' path')
        exit()
 
    get_personal_info(sys.argv[1])
    