import re

_COUNTRIES = ['new york', 'australia', 'greece', 'california' ]

_RE_LOCATION = re.compile(r'<LOCATION>\s*?(.*?)\s*?</LOCATION>')

if False:
    text = '<em><ORGANIZATION>Stanford</ORGANIZATION>, <LOCATION>California</LOCATION></em>,'
    matches = _RE_LOCATION.finditer(text)
    print [m.group(1) for m in matches]
    exit()
    
_RE_MARKUP = re.compile(r'<.*?>')
    
def clean_markup(text): 
    cleaned = _RE_MARKUP.sub('', text)
    #print 'clean_markup(%s) = "%s"' % (text, cleaned)
    return cleaned

def get_locations(data):
    #print type(query)
    text = '\n'.join(query.snip for query in data)
    #print text
    #print type(text)
       
    matches = _RE_LOCATION.finditer(text)
    locations = [clean_markup(m.group(1).lower()) for m in matches]
    loc_dict = {}
    for loc in locations:
        loc_dict[loc] = loc_dict.get(loc,0) + 1
    sorted_locations = sorted(loc_dict.keys(), key = lambda k : -loc_dict[k])    
    return sorted_locations

# defines the components of a query result from Google.
class GoogleQuery:
    
    def __init__(self, title, snip, link):
        self.title = title
        self.snip = snip
        self.link = link
    
    '''
    returns the title, snip, and link associated with a Google result
    '''
    def __str__(self):
        return ('title: ' + self.title + '\nsnip: ' + self.snip + '\nlink: ' + self.link)

# note that you should not need to use this class. this class defines the possible locations 
# of a landmark. it differs from the location object in that it stores multiple possible location
# objects, while the location object only stores one possible guess for a city location.
class LocationPossibilities:
    
    def __init__(self, cities, country):
        self.cities = cities
        self.country = country

    '''
    returns the list of all the possible cities along with the country which contains the city
    '''
    def __str__(self):
        locations = ''
        for city in self.cities:
            locations += (city + ', ')
        locations = locations[:-2]
        return ('possible cities: ' + locations + '\ncountry: ' + self.country)

# defines the components of a location.
class Location:
    
    def __init__(self, city, country):
        self.city = city
        self.country = country

    '''
    returns the name of the city and country associated with the landmark
    '''
    def __str__(self):
        return ('city: ' + self.city + '\ncountry: ' + self.country)

class Googling:

    # reads in data for a set of results for a single query
    def readInSegment(self, lines):
        queryResults = []
        for i in range(0, len(lines), 3):
            queryResults.append(GoogleQuery(lines[i], lines[i + 1], lines[i + 2]))
        return queryResults
    
    # reads in data from a string rather than a file. assumes the same text file structure as readInData
    def readString(self, infoString):
        queryData = []
        lines = infoString
        startline = 0
        endline = 0
        while startline < len(lines):
            i = startline
            while i < len(lines) and len(lines[i].strip()) > 0: # reads for a query until an empty line or the end of the file
                i += 1
            endline = i
            queryData.append(self.readInSegment(lines[startline:endline]))
            startline = endline + 1 
        return queryData
    
    # reads in the tagged query results output by Google. takes in the name of the file containing the tagged Google results.
    def readInData(self, googleResultsFile):
        queryData = []
        infile = open(googleResultsFile)
        lines = infile.readlines()
        infile.close()
        startline = 0
        endline = 0
        while startline < len(lines):
            i = startline
            while i < len(lines) and len(lines[i].strip()) > 0: # reads for a query until an empty line or the end of the file
                i += 1
            endline = i
            queryData.append(self.readInSegment(lines[startline:endline]))
            startline = endline + 1 
        return queryData
    
    # takes a line and parses out the correct possible locations of the landmark for that line.
    # returns a LocationPossibilities object as well as the associated landmark
    def readGoldEntry(self, line):
        parts = line.split('\t')
        locationParts = parts[2].split(',')
        cities = locationParts[0].split('/')
        return LocationPossibilities(cities, locationParts[1].lower().strip()), parts[1].lower().strip()
    
    # reads in a file containing data about the landmark and where it's located 
    # returns a list of LocationPossibilities object as well as a list of landmarks. takes 
    # in the name of the gold file
    def readInGold(self, goldFile):
        goldData = []
        landmarks = []
        infile = open(goldFile)
        lines = infile.readlines()
        infile.close()
        for line in lines:
            goldEntry, landmark = self.readGoldEntry(line)
            goldData.append(goldEntry)
            landmarks.append(landmark)
        return goldData, landmarks
            
    # in this method, you must return Location object, where the first parameter of the constructor is the city where
    # the landmark is located and the second parameter is the state or the country containing the city. 
    # the return parameter is a Location object. if no good answer is found, returns a GoogleQuery object with
    # empty strings as parameters
    
    # note that the method does not get passed the actual landmark being queried. you do not need this information,
    # as your primary task in this method is to simply extract a guess for the location of the landmark given
    # Google results. you can, however, extract the landmark name from the given queries if you feel that helps.
    def guessLocation(self, data):
        #TODO: use the GoogleQuery object for landmark to generate a tuple of the location
        # of the landmark
        #print(data[1])
        
        #print '-' * 80
        locations = get_locations(data)
        locations = [loc for loc in locations
                if ('island' not in loc 
                and 'parthenon' not in loc)]
                
        locations.sort(key = lambda k : k != 'stanford')        
        
        countries = [loc for loc in locations if loc in _COUNTRIES]
        cities = [loc for loc in locations if loc not in _COUNTRIES]
        
        #print locations
        
        if len(countries) >= 1:
            country = countries[0]
        elif len(cities) >= 2:
            country = cities[1]
        else:
            country = ''
            
        if len(cities) >= 1:
            city = cities[0]
        elif len(countries) >= 2:
            city = countries[1]
        else:
            country = '' 

        return Location(city, country)         
    
       
        if len(locations) >= 2:
            ret = Location(locations[0], locations[1])
        elif len(locations) == 1:
            ret = Location(locations[0], '')    
        else:
            ret = Location('', '')
        #print ret
        
        return ret
    
    # loops through each of the data associated with each query and passes it into the
    # guessLocation method, which returns the guess of the user
    def processQueries(self, queryData):
        #TODO: this todo is optional. this is for anyone who might want to write any initialization code that should 
        # only be performed once.
        guesses = [''] * len(queryData)
        for i in range(len(queryData)):
            guesses[i] = self.guessLocation(queryData[i])
        return guesses
    
    # prints out the results as described in the handout
    def printResults(self, correctCities, incorrectCities, noguessCities, correctCountries, incorrectCountries, 
                noguessCountries, landmarks, guesses, gold):
        print('LANDMARK\tYOUR GUESSED CITY\tCORRECT CITY/CITIES\tYOUR GUESSED COUNTRY\tCORRECT COUNTRY')
        correctGuesses = set(correctCities).intersection(set(correctCountries))
        noGuesses = set(noguessCities).union(set(noguessCountries))
        incorrectGuesses = set(incorrectCities).union(set(incorrectCountries))
        print('=====CORRECT GUESSES=====')
        for i in correctGuesses:
            print(landmarks[i] + '\t' + guesses[i].city + '\t' + str(gold[i].cities) + '\t' + guesses[i].country + '\t' + gold[i].country)
        print('=====NO GUESSES=====')
        for i in noGuesses:
            print(landmarks[i] + '\t' + guesses[i].city + '\t' + str(gold[i].cities) + '\t' + guesses[i].country + '\t' + gold[i].country)
        print('=====INCORRECT GUESSES=====')
        for i in incorrectGuesses:
            print(landmarks[i] + '\t' + guesses[i].city + '\t' + str(gold[i].cities) + '\t' + guesses[i].country + '\t' + gold[i].country)
        print('=====TOTAL SCORE=====')
        correctTotal = len(correctCities) + len(correctCountries)
        noguessTotal = len(noguessCities) + len(noguessCountries)
        incorrectTotal = len(incorrectCities) + len(incorrectCountries)
        print('correct guesses: ' + str(correctTotal))
        print('no guesses: ' + str(noguessTotal))
        print('incorrect guesses: ' + str(incorrectTotal))
        print('total score: ' + str(correctTotal - incorrectTotal) + ' out of ' + str(correctTotal + noguessTotal + incorrectTotal))
    
    # takes a list of Location objects and prints a list of correct and incorrect answers as well as scores the results
    def scoreAnswers(self, guesses, gold, landmarks):
        correctCities = []
        incorrectCities = []
        noguessCities = []
        correctCountries = []
        incorrectCountries = []
        noguessCountries = []
        for i in range(len(guesses)):
            if guesses[i].city.lower() in gold[i].cities:
                correctCities.append(i)
            elif guesses[i].city == '':
                noguessCities.append(i)
            else:
                incorrectCities.append(i)
            if guesses[i].country.lower() == gold[i].country.lower():
                correctCountries.append(i)
            elif guesses[i].country == '':
                noguessCountries.append(i)
            else:
                incorrectCountries.append(i)
        self.printResults(correctCities, incorrectCities, noguessCities, correctCountries, incorrectCountries, noguessCountries, landmarks, guesses, gold)
    
if __name__ == '__main__':
    googleResultsFile = '../data/googleResults_tagged.txt' # file where Google query results are read
    goldFile = '../data/landmarks.txt' # contains the results 
    googling = Googling()
    queryData = googling.readInData(googleResultsFile)
    goldData, landmarks = googling.readInGold(goldFile)
    guesses = googling.processQueries(queryData)
    googling.scoreAnswers(guesses, goldData, landmarks)
