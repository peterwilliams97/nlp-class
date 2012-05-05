
REM You may find this shell script helpful.

SET DATA=masc
REM SET DATA=miniTest

REM --parser PCFGParser \

REM python PCFGParserTester.py --path ../data --parser BaselineParser  --data %DATA%
python PCFGParserTester.py --path ../data --parser  PCFGParser  --data %DATA%

