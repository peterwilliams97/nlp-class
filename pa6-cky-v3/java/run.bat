
REM You may find this shell script helpful.

SET DATA=miniTest
REM SET DATA=masc


REM --parser nlpclass.assignments.PCFGParserTester\$PCFGParser \

java -server -mx500m -cp classes nlpclass.assignments.PCFGParserTester --parser nlpclass.assignments.PCFGParserTester$BaselineParser --path ../data --data %DATA% 
 
