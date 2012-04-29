
# You may find this shell script helpful.

SET DATA=masc
SET DATA=miniTest

REM --parser PCFGParser \

python PCFGParserTester.py --path ../data --parser BaselineParser  --data %DATA%
  
