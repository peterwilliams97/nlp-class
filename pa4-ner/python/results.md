NER RESULTS
===========
BASE
----
precision = 0.801673640167364
recall = 0.5229257641921398
F1 = 0.6329699372315825

_title()
--------
precision = 0.9535256410256411
recall = 0.6495633187772926
F1 = 0.7727272727272728

_title() -1,0,+1
----------------
precision = 0.9612263300270514
recall = 0.5818777292576419
F1 = 0.7249234954097247

_numeric()
----------
precision = 0.9542536115569823
recall = 0.6490174672489083
F1 = 0.7725795971410007

_title() + _numeric()
---------------------
precision = 0.9542536115569823
recall = 0.6490174672489083
F1 = 0.7725795971410007

_title() + _numeric() + (_title(), _numeric())
----------------------------------------------
precision = 0.9543634907926342
recall = 0.6506550218340611
F1 = 0.7737747484582929

precision = 0.9468531468531468
recall = 0.7390829694323144
F1 = 0.8301655426118947


        f_title = _KV('title=', _title(currentWord))
        f_numeric = _KV('numeric=', _numeric(currentWord))
        f_letterFirst = _KV('letterFirst', currentWord[0].lower())
        f_letterLast = _KV('letterLast', currentWord[-1].lower())
        
        features.append(f_title)
        
        features.append(f_numeric)
        features.append(_COMBINE([f_title, f_numeric]))
        features.append(_COMBINE([f_title, f_prevLabel]))
        
        features.append(f_letterFirst)
        features.append(f_letterLast)
        
length
------
precision = 0.9475890985324947
recall = 0.740174672489083
F1 = 0.8311369904995404     


latest
------   
precision = 0.9479166666666666
recall = 0.7450873362445415
F1 = 0.8343520782396088

latest + f_not_title
--------------------   
precision = 0.9504189944134078
recall = 0.7429039301310044
F1 = 0.8339460784313725

+ f_title2
----------
precision = 0.9483471074380165
recall = 0.7516375545851528
F1 = 0.8386114494518879

last with f_word
---------------- 
precision = 0.9483960948396095
recall = 0.74235807860262
F1 = 0.8328230251071647       

no f_word
---------
precision = 0.7220843672456576
recall = 0.31768558951965065
F1 = 0.44124336618650495

f_title_run
-----------
precision = 0.723458904109589
recall = 0.46124454148471616
F1 = 0.5633333333333332

features.append(f_title_run)
features.append(_COMBINE([f_title, f_title_run]))
features.append(_COMBINE([f_title2, f_title_run]))

next test
---------
precision = 0.7619047619047619
recall = 0.48034934497816595
F1 = 0.5892199531302309

improved _title_run()
---------------------
precision = 0.7459677419354839
recall = 0.5049126637554585
F1 = 0.6022135416666666

added prevLabel combo
---------------------
precision = 0.7396078431372549
recall = 0.5147379912663755
F1 = 0.6070164145477953

removed first + last letter
---------------------------
precision = 0.6966452533904354
recall = 0.5327510917030568
F1 = 0.6037735849056604

vowell shape
------------
precision = 0.6967435549525102
recall = 0.5605895196506551
F1 = 0.6212946158499698