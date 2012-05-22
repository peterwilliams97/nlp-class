from __future__ import division

"""
Consider the following queries and the results that follow: 

What is the capital of California? 

1. New York City 
2. Alabama 
3. Sacramento* 
4. Stanford 

What is the capital of Georgia? 

1. Altanta* 
2. Wyoming 
3. Chicago 
4. Washington DC 
5. China 
6. Steve Jobs 


What is the capital of Massachusetts? 

1. Bush 
2. Japan 
3. Massachusetts City 
4. Boston* 

What is the capital of Maryland? 

1. Facebook 
2. Africa 
3. Los Angeles 
4. Annapolis* 
5. England 

Note that answers which are followed by an asterisk are the correct answers to the query. What is the mean reciprocal rank for the set of queries over the capital of the following set of states: 

California, Georgia, Massachusetts, Maryland 
"""

x = (1/3 + 1 + 1/4 + 1/4)/4 
y = (1 + 5/6)/4
print '%.2f' % x
print '%.2f' % y    
     






