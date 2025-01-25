import math ,time ,os #line:2
import numpy as np #line:3
import numpy .random as nr #line:4
from copy import deepcopy #line:5
import matplotlib .pyplot as plt #line:6
from joblib import Parallel ,delayed #line:7
import hashlib #line:8
md5_s =['6c11f117a84c860c4044f8a1a45a0e67','cb51d4bbfdf4cc67e8bec57bc57e21c8','28f9afcaa52714aa964e215b7247a691','57f92316a9e611dd97c1528694ff6f9f','fd3dbb083970d4ba54ff6d067ab0c320','57c3d88ebf6777016c1429d25f283052','5f12a9899da112ee22a9a3ca7286b75b','9c84d4d198be8a5ef0dd96a8df934a80','df9c3ded3fe362c4c513a2bb3b28383f','12536e9b1dad1aabd97139327a115cc4','2a282b5b4649959c8a37c38e333789ad','0946a6c2e833058ced3d4798ba7ed903','432b8b1a39018c5b423f618c825a170c','46332f4160a17a9cb13fe5a559a66004','53630aba1c1685f49a216d70eb6bb7e0','acd9e269de3dcf51a4090cc907ae6ca9','affe60d5c024c79e77e7723bbca9608d','985b95f3aa925b05f3ac50561bab5dc2','2b7b9589e306a4419a7b259a1a7f1127','f9ac39e0da75c423a92003125f573429','0a988276a12594b79f9d79457371a1ad','ff4808135d6784b9a849f650cf579a46','91f88b573ccf4e2cc31da287baaff287','660440c7e709d6d3cd86293bd8ef1368','d552702c3e333e8c8e0d766c9b2c2b1c','31cd4b4c4b6964a1d4b1f78e8d2b213e','03a6a04c30c6d5b2041671c39eeec57e','503b8c8889c87da762be47d452d9fe12','146aec80f4ccdd435a2aaf7339e598e8','a02c5ad1046ed530f5e96c317300f312']#line:44
class vcopt :#line:63
    def __init__ (O0O0000O0O0OO0OO0 ):#line:64
        pass #line:65
    def __del__ (O000000000O0O0O0O ):#line:66
        pass #line:67
    def setting_1 (OO00OO0OO00OOO000 ,OO00O0OO0OO0OOO0O ,O0000OO0O0OOOOOO0 ,OO00O000O00OOOOOO ,OO0O00OO0O00O00OO ,OOOOO0O0000OOOO0O ,OO000OOO0OOOO00O0 ,OOO000OOOOO00O00O ,OO00O0000O0OOO000 ):#line:71
        OO00OO0OO00OOO000 .para_range =OO00O0OO0OO0OOO0O #line:72
        OO00OO0OO00OOO000 .para_num =len (OO00O0OO0OO0OOO0O )#line:73
        OO00OO0OO00OOO000 .score_func =O0000OO0O0OOOOOO0 #line:74
        if type (OO00O000O00OOOOOO )==str and OO00O000O00OOOOOO [0 :2 ]=='==':#line:76
                OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO [2 :])#line:77
                OO00OO0OO00OOO000 .aim_operator ='=='#line:78
        elif type (OO00O000O00OOOOOO )==str and (OO00O000O00OOOOOO [0 :2 ]=='>='or OO00O000O00OOOOOO [0 :2 ]=='=>'):#line:79
                OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO [2 :])#line:80
                OO00OO0OO00OOO000 .aim_operator ='>='#line:81
        elif type (OO00O000O00OOOOOO )==str and (OO00O000O00OOOOOO [0 :2 ]=='<='or OO00O000O00OOOOOO [0 :2 ]=='=<'):#line:82
                OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO [2 :])#line:83
                OO00OO0OO00OOO000 .aim_operator ='<='#line:84
        elif type (OO00O000O00OOOOOO )==str and OO00O000O00OOOOOO [0 :1 ]=='>':#line:85
                OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO [1 :])#line:86
                OO00OO0OO00OOO000 .aim_operator ='>'#line:87
        elif type (OO00O000O00OOOOOO )==str and OO00O000O00OOOOOO [0 :1 ]=='<':#line:88
                OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO [1 :])#line:89
                OO00OO0OO00OOO000 .aim_operator ='<'#line:90
        elif type (OO00O000O00OOOOOO )==str and OO00O000O00OOOOOO [0 :1 ]=='=':#line:91
                OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO [1 :])#line:92
                OO00OO0OO00OOO000 .aim_operator ='=='#line:93
        else :#line:94
            OO00OO0OO00OOO000 .aim =float (OO00O000O00OOOOOO )#line:95
            OO00OO0OO00OOO000 .aim_operator ='=='#line:96
        OO00OO0OO00OOO000 .show_pool_func =OO0O00OO0O00O00OO #line:98
        if OO00OO0OO00OOO000 .show_pool_func ==None :pass #line:100
        elif OO00OO0OO00OOO000 .show_pool_func in ['bar','print','plot']:pass #line:101
        elif callable (OO00OO0OO00OOO000 .show_pool_func ):pass #line:102
        elif type (OO0O00OO0O00O00OO )==str :#line:103
            if len (OO0O00OO0O00O00OO )==0 or OO0O00OO0O00O00OO [-1 ]!='/':#line:104
                OO00OO0OO00OOO000 .show_pool_func ='bar'#line:105
        if type (OOOOO0O0000OOOO0O )in [int ,float ]:#line:107
            OO00OO0OO00OOO000 .seed =int (OOOOO0O0000OOOO0O )#line:108
        else :#line:109
            OO00OO0OO00OOO000 .seed =None #line:110
        nr .seed (OO00OO0OO00OOO000 .seed )#line:111
        OO0OOO0O0O0OOO00O =2051190000.0 #line:112
        if type (OO000OOO0OOOO00O0 )in [int ,float ]:#line:114
            OO00OO0OO00OOO000 .pool_num =int (OO000OOO0OOOO00O0 )#line:115
            if OO00OO0OO00OOO000 .pool_num %2 !=0 :#line:117
                OO00OO0OO00OOO000 .pool_num +=1 #line:118
        else :#line:119
            OO00OO0OO00OOO000 .pool_num =None #line:120
        if type (OOO000OOOOO00O00O )in [int ,float ]:#line:122
            OO00OO0OO00OOO000 .max_gen =int (OOO000OOOOO00O00O )#line:123
        else :#line:124
            OO00OO0OO00OOO000 .max_gen =None #line:125
        OO00OO0OO00OOO000 .core_num =1 #line:128
        if type (OO00O0000O0OOO000 )in [int ,float ]:#line:129
            O00O00O0000O0OOOO =hashlib .md5 (str (OOOOO0O0000OOOO0O ).encode ()).hexdigest ()#line:131
            if O00O00O0000O0OOOO in md5_s and time .time ()<OO0OOO0O0O0OOO00O :#line:132
                OO00OO0OO00OOO000 .core_num =int (OO00O0000O0OOO000 )#line:133
        OO00OO0OO00OOO000 .start =time .time ()#line:134
    def setting_2 (O00OOO000OOOO0000 ,OO0OO000O0O0O00O0 ,OOO0OOO0OO0O00000 ,OOO0OOOO0OO0O000O ):#line:138
        if O00OOO000OOOO0000 .pool_num is None :#line:140
            O00OOO000OOOO0000 .pool_num =OO0OO000O0O0O00O0 #line:141
        O00OOO000OOOO0000 .parent_num =OOO0OOO0OO0O00000 #line:142
        O00OOO000OOOO0000 .child_num =OOO0OOOO0OO0O000O #line:143
        O00OOO000OOOO0000 .family_num =OOO0OOO0OO0O00000 +OOO0OOOO0OO0O000O #line:144
        if O00OOO000OOOO0000 .max_gen is None :#line:146
            O00OOO000OOOO0000 .max_n =1000000 #line:147
        else :#line:148
            O00OOO000OOOO0000 .max_n =O00OOO000OOOO0000 .max_gen //O00OOO000OOOO0000 .pool_num +1 #line:149
    def setting_3 (OO00OOOOO00OOOO0O ,O0O0O0O0O0O0O000O ):#line:153
        OO00OOOOO00OOOO0O .pool ,OO00OOOOO00OOOO0O .pool_score =np .zeros ((OO00OOOOO00OOOO0O .pool_num ,OO00OOOOO00OOOO0O .para_num ),dtype =O0O0O0O0O0O0O000O ),np .zeros (OO00OOOOO00OOOO0O .pool_num )#line:154
        OO00OOOOO00OOOO0O .parent ,OO00OOOOO00OOOO0O .parent_score =np .zeros ((OO00OOOOO00OOOO0O .parent_num ,OO00OOOOO00OOOO0O .para_num ),dtype =O0O0O0O0O0O0O000O ),np .zeros (OO00OOOOO00OOOO0O .parent_num )#line:155
        OO00OOOOO00OOOO0O .child ,OO00OOOOO00OOOO0O .child_score =np .zeros ((OO00OOOOO00OOOO0O .child_num ,OO00OOOOO00OOOO0O .para_num ),dtype =O0O0O0O0O0O0O000O ),np .zeros (OO00OOOOO00OOOO0O .child_num )#line:156
        OO00OOOOO00OOOO0O .family ,OO00OOOOO00OOOO0O .family_score =np .zeros ((OO00OOOOO00OOOO0O .family_num ,OO00OOOOO00OOOO0O .para_num ),dtype =O0O0O0O0O0O0O000O ),np .zeros (OO00OOOOO00OOOO0O .family_num )#line:157
    def print_info (O0O0000OO00OO00O0 ):#line:161
        if O0O0000OO00OO00O0 .show_pool_func is not None :#line:162
            print ('{:_^86}'.format (' info '))#line:163
            print ('para_range     : n={}'.format (O0O0000OO00OO00O0 .para_num ))#line:164
            print ('score_func     : {}'.format (type (O0O0000OO00OO00O0 .score_func )))#line:165
            print ('aim            : {}{}'.format (O0O0000OO00OO00O0 .aim_operator ,O0O0000OO00OO00O0 .aim ))#line:166
            print ('show_pool_func : \'{}\''.format (O0O0000OO00OO00O0 .show_pool_func ))#line:168
            print ('seed           : {}'.format (O0O0000OO00OO00O0 .seed ))#line:169
            print ('pool_num       : {}'.format (O0O0000OO00OO00O0 .pool_num ))#line:170
            print ('max_gen        : {}'.format (O0O0000OO00OO00O0 .max_gen ))#line:171
            if O0O0000OO00OO00O0 .core_num ==1 :#line:172
                print ('core_num       : {} (*vcopt, vc-grendel)'.format (O0O0000OO00OO00O0 .core_num ))#line:173
            else :#line:174
                print ('core_num       : {} (vcopt, *vc-grendel)'.format (O0O0000OO00OO00O0 .core_num ))#line:175
            print ('{:_^86}'.format (' start '))#line:176
    def print_result (OOO00O0000000OOO0 ,O0O00OOOO00O0OO0O ):#line:180
        if OOO00O0000000OOO0 .show_pool_func !=None :#line:182
            print ('{:_^86}'.format (' result '))#line:183
            O000O0O0OO000OO0O ='para = np.array([{}'.format (O0O00OOOO00O0OO0O [0 ])#line:186
            for O0000O000OO0OOOO0 in O0O00OOOO00O0OO0O [1 :]:#line:187
                O000O0O0OO000OO0O +=', {}'.format (O0000O000OO0OOOO0 )#line:188
            O000O0O0OO000OO0O +='])'#line:189
            print (O000O0O0OO000OO0O )#line:190
            print ('score = {}'.format (OOO00O0000000OOO0 .score_best ))#line:191
            print ('{:_^86}'.format (' end '))#line:192
    def score_pool_multi (OO0OOO0OOO000O0OO ,OO0OOO0OOO00O0OOO ):#line:196
        O00OO0000O0OOO0OO =OO0OOO0OOO000O0OO .para_range [OO0OOO0OOO000O0OO .pool [OO0OOO0OOO00O0OOO ]]#line:197
        OO0OOO0OOO000O0OO .pool_score [OO0OOO0OOO00O0OOO ]=OO0OOO0OOO000O0OO .score_func (O00OO0000O0OOO0OO )#line:198
        OO0OOO0OOO000O0OO .aaa +=1 #line:199
        if OO0OOO0OOO000O0OO .show_pool_func !=None :#line:200
            O00O000O0000000OO ='\rScoring first gen {}/{}        '.format (OO0OOO0OOO00O0OOO +1 ,OO0OOO0OOO000O0OO .pool_num )#line:201
            print (O00O000O0000000OO ,end ='')#line:202
    def score_pool (OOO0O0OO0OOOO0OOO ):#line:203
        OOO0O0OO0OOOO0OOO .aaa =0 #line:204
        Parallel (n_jobs =OOO0O0OO0OOOO0OOO .core_num ,require ='sharedmem')([delayed (OOO0O0OO0OOOO0OOO .score_pool_multi )(OO000OOO0OO0O0O0O )for OO000OOO0OO0O0O0O in range (OOO0O0OO0OOOO0OOO .pool_num )])#line:205
        if OOO0O0OO0OOOO0OOO .show_pool_func !=None :#line:206
            O0000O000O0OOOO00 ='\rScoring first gen {}/{}        '.format (OOO0O0OO0OOOO0OOO .pool_num ,OOO0O0OO0OOOO0OOO .pool_num )#line:207
            print (O0000O000O0OOOO00 )#line:208
    def score_pool_dc_multi (OOO00O0O00O0O00OO ,OOO00OO0000OO00OO ):#line:219
        O0OOOO0O00O0OO00O =[]#line:220
        for OO0O00OOO00OO00O0 in range (OOO00O0O00O0O00OO .para_num ):#line:221
            O0OOOO0O00O0OO00O .append (OOO00O0O00O0O00OO .para_range [OO0O00OOO00OO00O0 ][OOO00O0O00O0O00OO .pool [OOO00OO0000OO00OO ,OO0O00OOO00OO00O0 ]])#line:222
        O0OOOO0O00O0OO00O =np .array (O0OOOO0O00O0OO00O )#line:223
        OOO00O0O00O0O00OO .pool_score [OOO00OO0000OO00OO ]=OOO00O0O00O0O00OO .score_func (O0OOOO0O00O0OO00O )#line:224
        OOO00O0O00O0O00OO .aaa +=1 #line:225
        if OOO00O0O00O0O00OO .show_pool_func !=None :#line:226
            OOOOO0O0OOOOO0O0O ='\rScoring first gen {}/{}        '.format (OOO00OO0000OO00OO +1 ,OOO00O0O00O0O00OO .pool_num )#line:227
            print (OOOOO0O0OOOOO0O0O ,end ='')#line:228
    def score_pool_dc (O0O0OOOOO000OO0O0 ):#line:229
        O0O0OOOOO000OO0O0 .aaa =0 #line:230
        Parallel (n_jobs =O0O0OOOOO000OO0O0 .core_num ,require ='sharedmem')([delayed (O0O0OOOOO000OO0O0 .score_pool_dc_multi )(O0OO0000O0O000OO0 )for O0OO0000O0O000OO0 in range (O0O0OOOOO000OO0O0 .pool_num )])#line:231
        if O0O0OOOOO000OO0O0 .show_pool_func !=None :#line:232
            O0O00000O00O0000O ='\rScoring first gen {}/{}        '.format (O0O0OOOOO000OO0O0 .pool_num ,O0O0OOOOO000OO0O0 .pool_num )#line:233
            print (O0O00000O00O0000O )#line:234
    def score_pool_rc_multi (OOO0O00O00O0OOOOO ,OOOOO0OO0OO00O0O0 ):#line:248
        OOOOOO0000000OO00 =OOO0O00O00O0OOOOO .pool [OOOOO0OO0OO00O0O0 ]*(OOO0O00O00O0OOOOO .para_range [:,1 ]-OOO0O00O00O0OOOOO .para_range [:,0 ])+OOO0O00O00O0OOOOO .para_range [:,0 ]#line:249
        OOO0O00O00O0OOOOO .pool_score [OOOOO0OO0OO00O0O0 ]=OOO0O00O00O0OOOOO .score_func (OOOOOO0000000OO00 )#line:250
        OOO0O00O00O0OOOOO .aaa +=1 #line:251
        if OOO0O00O00O0OOOOO .show_pool_func !=None :#line:252
            O0000O000OOO0O0O0 ='\rScoring first gen {}/{}        '.format (OOOOO0OO0OO00O0O0 +1 ,OOO0O00O00O0OOOOO .pool_num )#line:253
            print (O0000O000OOO0O0O0 ,end ='')#line:254
    def score_pool_rc (OO000000OO0OOOOO0 ):#line:255
        OO000000OO0OOOOO0 .aaa =0 #line:256
        Parallel (n_jobs =OO000000OO0OOOOO0 .core_num ,require ='sharedmem')([delayed (OO000000OO0OOOOO0 .score_pool_rc_multi )(O000O0OO0O0OOO0O0 )for O000O0OO0O0OOO0O0 in range (OO000000OO0OOOOO0 .pool_num )])#line:257
        if OO000000OO0OOOOO0 .show_pool_func !=None :#line:258
            O0O0OO00O00OO0O0O ='\rScoring first gen {}/{}        '.format (OO000000OO0OOOOO0 .pool_num ,OO000000OO0OOOOO0 .pool_num )#line:259
            print (O0O0OO00O00OO0O0O )#line:260
    def save_best_mean (O00O000O0O0OO00O0 ):#line:294
        O00O000O0O0OO00O0 .best_index =np .argmin (np .abs (O00O000O0O0OO00O0 .aim -O00O000O0O0OO00O0 .pool_score ))#line:296
        O00O000O0O0OO00O0 .pool_best =deepcopy (O00O000O0O0OO00O0 .pool [O00O000O0O0OO00O0 .best_index ])#line:298
        O00O000O0O0OO00O0 .score_best =deepcopy (O00O000O0O0OO00O0 .pool_score [O00O000O0O0OO00O0 .best_index ])#line:299
        O00O000O0O0OO00O0 .score_mean =np .mean (O00O000O0O0OO00O0 .pool_score )#line:302
        O00O000O0O0OO00O0 .gap_mean =np .mean (np .abs (O00O000O0O0OO00O0 .aim -O00O000O0O0OO00O0 .pool_score ))#line:303
        O00O000O0O0OO00O0 .score_mean_save =deepcopy (O00O000O0O0OO00O0 .score_mean )#line:305
        O00O000O0O0OO00O0 .gap_mean_save =deepcopy (O00O000O0O0OO00O0 .gap_mean )#line:306
    def make_parent (O0O0000OO0O00O0OO ,OOO0OOO00000O0O0O ):#line:310
        O0O0000OO0O00O0OO .pool_select =OOO0OOO00000O0O0O #line:311
        O0O0000OO0O00O0OO .parent =O0O0000OO0O00O0OO .pool [O0O0000OO0O00O0OO .pool_select ]#line:312
        O0O0000OO0O00O0OO .parent_score =O0O0000OO0O00O0OO .pool_score [O0O0000OO0O00O0OO .pool_select ]#line:313
    def make_family (O0OOOO000OOOOOO0O ):#line:317
        O0OOOO000OOOOOO0O .family =np .vstack ((O0OOOO000OOOOOO0O .child ,O0OOOO000OOOOOO0O .parent ))#line:318
        O0OOOO000OOOOOO0O .family_score =np .hstack ((O0OOOO000OOOOOO0O .child_score ,O0OOOO000OOOOOO0O .parent_score ))#line:319
    def JGG (O0000OO0000O00000 ):#line:323
        O0000OO0000O00000 .family_select =np .argpartition (np .abs (O0000OO0000O00000 .aim -O0000OO0000O00000 .family_score ),O0000OO0000O00000 .parent_num )[:O0000OO0000O00000 .parent_num ]#line:326
        O0000OO0000O00000 .pool [O0000OO0000O00000 .pool_select ]=O0000OO0000O00000 .family [O0000OO0000O00000 .family_select ]#line:328
        O0000OO0000O00000 .pool_score [O0000OO0000O00000 .pool_select ]=O0000OO0000O00000 .family_score [O0000OO0000O00000 .family_select ]#line:329
    def end_check (OOOOO00OOO0OO00OO ):#line:333
        OOOOO00OOO0OO00OO .best_index =np .argmin (np .abs (OOOOO00OOO0OO00OO .aim -OOOOO00OOO0OO00OO .pool_score ))#line:335
        OOOOO00OOO0OO00OO .score_best =deepcopy (OOOOO00OOO0OO00OO .pool_score [OOOOO00OOO0OO00OO .best_index ])#line:336
        OOOOO00OOO0OO00OO .gap_mean =np .mean (np .abs (OOOOO00OOO0OO00OO .aim -OOOOO00OOO0OO00OO .pool_score ))#line:338
        if eval (str (OOOOO00OOO0OO00OO .score_best )+OOOOO00OOO0OO00OO .aim_operator +str (OOOOO00OOO0OO00OO .aim )):#line:342
            return 10 #line:343
        if OOOOO00OOO0OO00OO .gap_mean >=OOOOO00OOO0OO00OO .gap_mean_save :#line:345
            return 1 #line:346
        return 0 #line:347
    def make_info (OO00OO0O00O0OOO00 ,O00OOOO000000O00O ):#line:365
        OO0O0O00000O00O00 ={'gen':O00OOOO000000O00O ,'best_index':OO00OO0O00O0OOO00 .best_index ,'best_score':OO00OO0O00O0OOO00 .score_best ,'mean_score':OO00OO0O00O0OOO00 .score_mean ,'mean_gap':OO00OO0O00O0OOO00 .gap_mean ,'time':time .time ()-OO00OO0O00O0OOO00 .start }#line:370
        return OO0O0O00000O00O00 #line:371
    def show_pool (OOO00000O0OO00O00 ,OOOO0OO0O000000O0 ):#line:375
        OO0O0000000OOOO00 =OOO00000O0OO00O00 .make_info (OOOO0OO0O000000O0 )#line:376
        OOO00000O0OO00O00 .show_pool_func (OOO00000O0OO00O00 .para_range [OOO00000O0OO00O00 .pool ],**OO0O0000000OOOO00 )#line:377
    def show_pool_dc (O0OO0O00O000OOOOO ,O00OO0OO00OO00000 ):#line:378
        O0OO0OO0O0O0O0OOO =O0OO0O00O000OOOOO .make_info (O00OO0OO00OO00000 )#line:379
        O0O00OO0OO0OOOOO0 =[]#line:380
        for O0OO00000OOOOOOO0 in range (O0OO0O00O000OOOOO .pool_num ):#line:381
            O0OOOOO0O0O0OO0O0 =[]#line:382
            for OOO0O00OO0OOOO000 in range (O0OO0O00O000OOOOO .para_num ):#line:383
                O0OOOOO0O0O0OO0O0 .append (O0OO0O00O000OOOOO .para_range [OOO0O00OO0OOOO000 ][O0OO0O00O000OOOOO .pool [O0OO00000OOOOOOO0 ,OOO0O00OO0OOOO000 ]])#line:384
            O0O00OO0OO0OOOOO0 .append (O0OOOOO0O0O0OO0O0 )#line:385
        O0O00OO0OO0OOOOO0 =np .array (O0O00OO0OO0OOOOO0 )#line:386
        O0OO0O00O000OOOOO .show_pool_func (O0O00OO0OO0OOOOO0 ,**O0OO0OO0O0O0O0OOO )#line:387
    def show_pool_rc (OO000OO0000O00O0O ,OOOOOOO0O000000O0 ):#line:388
        O00000O0OOOOOOO0O =OO000OO0000O00O0O .make_info (OOOOOOO0O000000O0 )#line:389
        OOO00O0O00O0O0OOO =np .array (list (map (lambda O000OOO0O0OO0OOO0 :OO000OO0000O00O0O .pool [O000OOO0O0OO0OOO0 ]*(OO000OO0000O00O0O .para_range [:,1 ]-OO000OO0000O00O0O .para_range [:,0 ])+OO000OO0000O00O0O .para_range [:,0 ],range (OO000OO0000O00O0O .pool_num ))))#line:392
        OO000OO0000O00O0O .show_pool_func (OOO00O0O00O0O0OOO ,**O00000O0OOOOOOO0O )#line:393
    def make_fill (OO00000O000OO0OOO ,OOO0O000O0O0OOO00 ):#line:397
        OOO0O000O0O0OOO00 ='{:>8}'.format (OOO0O000O0O0OOO00 )#line:398
        O0OOO0O0O00O0OO00 ='{:8.3f}'.format (OO00000O000OO0OOO .score_best )#line:399
        OOO0OO00OO0000O00 ='{:8.3f}'.format (OO00000O000OO0OOO .score_mean )#line:400
        OO0O00OOOO00O0O00 ='{:8.3f}'.format (OO00000O000OO0OOO .gap_mean )#line:401
        O0O000O0O000OOOO0 ='{:6.1f}'.format (time .time ()-OO00000O000OO0OOO .start )#line:402
        return OOO0O000O0O0OOO00 ,O0OOO0O0O00O0OO00 ,OOO0OO00OO0000O00 ,OO0O00OOOO00O0O00 ,O0O000O0O000OOOO0 #line:403
    def show_pool_bar (OO000OOO0OOOO0OO0 ,OOOOO0O00O00OOOO0 ):#line:408
        OO00OO00OO000O0O0 =round (OO000OOO0OOOO0OO0 .score_best ,4 )#line:410
        OO0OO0OO000OOO00O =min (abs (OO000OOO0OOOO0OO0 .aim -OO000OOO0OOOO0OO0 .init_score_range [0 ]),abs (OO000OOO0OOOO0OO0 .aim -OO000OOO0OOOO0OO0 .init_score_range [1 ]))#line:412
        OO0O0O0OO0O00000O =abs (OO000OOO0OOOO0OO0 .aim -OO000OOO0OOOO0OO0 .score_best )#line:413
        O00O00O0O0O00O0O0 =min (abs (OO000OOO0OOOO0OO0 .aim -OO000OOO0OOOO0OO0 .gap_mean ),OO0OO0OO000OOO00O )#line:414
        if OO0OO0OO000OOO00O ==0 :#line:416
            OO0OO0OO000OOO00O =0.001 #line:417
        O0OOOOO0O00OOOO00 =int (OO0O0O0OO0O00000O /OO0OO0OO000OOO00O *40 )#line:418
        OO0O00OOOO0OOO000 =int ((O00O00O0O0O00O0O0 -OO0O0O0OO0O00000O )/OO0OO0OO000OOO00O *40 )#line:419
        O0OO00OO00OO00OO0 =40 -O0OOOOO0O00OOOO00 -OO0O00OOOO0OOO000 #line:420
        OO000O0O0000OO0OO ='\r|{}+{}<{}| gen={}, best_score={}'.format (' '*O0OOOOO0O00OOOO00 ,' '*OO0O00OOOO0OOO000 ,' '*O0OO00OO00OO00OO0 ,OOOOO0O00O00OOOO0 ,OO00OO00OO000O0O0 )#line:422
        print (OO000O0O0000OO0OO ,end ='')#line:423
        if OOOOO0O00O00OOOO0 ==0 :#line:425
            time .sleep (0.2 )#line:426
    def show_pool_print (O000OOOO0O00000O0 ,O0O0O0O0O0O000O0O ):#line:428
        O0O0O0O0O0O000O0O ,O0OO000OO0OOO0O00 ,O0OO0OOOOO0O0OO00 ,OOO0OOO0OO0OO0OOO ,O00OO00OOOOOOOO00 =O000OOOO0O00000O0 .make_fill (O0O0O0O0O0O000O0O )#line:429
        print ('gen={}, best_score={}, mean_score={}, mean_gap={}, time={}'.format (O0O0O0O0O0O000O0O ,O0OO000OO0OOO0O00 ,O0OO0OOOOO0O0OO00 ,OOO0OOO0OO0OO0OOO ,O00OO00OOOOOOOO00 ))#line:430
    def show_pool_plot (O0O0O0OOO00O0OO0O ,O00O0OOO000000O0O ):#line:433
        O00O0OOO000000O0O ,O0OOO0OOO00OOOOO0 ,O0OOO0000O0OO000O ,OO0OO00OO0OOO0000 ,O000OO00OO000OOOO =O0O0O0OOO00O0OO0O .make_fill (O00O0OOO000000O0O )#line:434
        plt .bar (range (len (O0O0O0OOO00O0OO0O .pool_score [:100 ])),O0O0O0OOO00O0OO0O .pool_score [:100 ])#line:436
        plt .ylim ([min (O0O0O0OOO00O0OO0O .aim ,O0O0O0OOO00O0OO0O .init_score_range [0 ]),max (O0O0O0OOO00O0OO0O .aim ,O0O0O0OOO00O0OO0O .init_score_range [1 ])])#line:437
        plt .title ('gen        = {}{}best_score = {}{}mean_score = {}{}mean_gap   = {}{}time       =   {}'.format (O00O0OOO000000O0O ,'\n',O0OOO0OOO00OOOOO0 ,'\n',O0OOO0000O0OO000O ,'\n',OO0OO00OO0OOO0000 ,'\n',O000OO00OO000OOOO ),loc ='left',fontname ='monospace')#line:438
        plt .show ();plt .close ();print ()#line:439
    def show_pool_save (OO0O0O0OOOOOO000O ,OO0O000O00OOO0O0O ):#line:442
        OO0O0O0OOOOOO000O .show_pool_bar (OO0O000O00OOO0O0O )#line:444
        OOOOO0OO0O000OOOO ,OOO0OOOOO00O0O000 ,OO00OO0OO0OO0OO00 ,OO000OO0OOO0O0O00 ,OO000O0OOO0OO00OO =OO0O0O0OOOOOO000O .make_fill (OO0O000O00OOO0O0O )#line:446
        plt .bar (range (len (OO0O0O0OOOOOO000O .pool_score [:100 ])),OO0O0O0OOOOOO000O .pool_score [:100 ])#line:448
        plt .ylim ([min (OO0O0O0OOOOOO000O .aim ,OO0O0O0OOOOOO000O .init_score_range [0 ]),max (OO0O0O0OOOOOO000O .aim ,OO0O0O0OOOOOO000O .init_score_range [1 ])])#line:449
        plt .title ('gen        = {}{}best_score = {}{}mean_score = {}{}mean_gap   = {}{}time       =   {}'.format (OOOOO0OO0O000OOOO ,'\n',OOO0OOOOO00O0O000 ,'\n',OO00OO0OO0OO0OO00 ,'\n',OO000OO0OOO0O0O00 ,'\n',OO000O0OOO0OO00OO ),loc ='left',fontname ='monospace')#line:450
        plt .subplots_adjust (left =0.1 ,right =0.95 ,bottom =0.1 ,top =0.70 )#line:451
        plt .savefig (OO0O0O0OOOOOO000O .show_pool_func +'gen_{}.png'.format (str (OO0O000O00OOO0O0O ).zfill (8 )));plt .close ()#line:452
    def opt2 (O0OOO00O00OO0OOOO ,O0OOOOOOOO00O0000 ,OOOOO0O00OOOO0O00 ,O0OOOOO0O0O0OOOO0 ,show_para_func =None ,seed =None ,step_max =float ('inf')):#line:458
        O0OOOOOOOO00O0000 ,OOO00OO000O0OO0O0 =np .array (O0OOOOOOOO00O0000 ),OOOOO0O00OOOO0O00 (O0OOOOOOOO00O0000 )#line:460
        OO0OOO0O0O00O0O00 ={}#line:461
        if seed !='pass':nr .seed (seed )#line:462
        O00OOOO000O000000 =0 #line:463
        if show_para_func !=None :#line:465
            OO0OOO0O0O00O0O00 .update ({'step_num':O00OOOO000O000000 ,'score':round (OOO00OO000O0OO0O0 ,3 )})#line:466
            show_para_func (O0OOOOOOOO00O0000 ,**OO0OOO0O0O00O0O00 )#line:467
        while 1 :#line:469
            OOO00O0O0O0OOOO00 =False #line:470
            if O00OOOO000O000000 >=step_max :#line:471
                break #line:473
            O00OOO0O000O0OO00 =np .arange (0 ,len (O0OOOOOOOO00O0000 )-1 )#line:475
            nr .shuffle (O00OOO0O000O0OO00 )#line:476
            for OO000O0O00OO00O0O in O00OOO0O000O0OO00 :#line:477
                if OOO00O0O0O0OOOO00 ==True :break #line:479
                O0O00OO0O000O00O0 =np .arange (OO000O0O00OO00O0O +1 ,len (O0OOOOOOOO00O0000 ))#line:481
                nr .shuffle (O0O00OO0O000O00O0 )#line:482
                for OO0O0O0OO0000OO0O in O0O00OO0O000O00O0 :#line:483
                    if OOO00O0O0O0OOOO00 ==True :break #line:485
                    OOO00OOOO0OOOO0OO =np .hstack ((O0OOOOOOOO00O0000 [:OO000O0O00OO00O0O ],O0OOOOOOOO00O0000 [OO000O0O00OO00O0O :OO0O0O0OO0000OO0O +1 ][::-1 ],O0OOOOOOOO00O0000 [OO0O0O0OO0000OO0O +1 :]))#line:488
                    OOO000O0000000O00 =OOOOO0O00OOOO0O00 (OOO00OOOO0OOOO0OO )#line:489
                    if np .abs (O0OOOOO0O0O0OOOO0 -OOO000O0000000O00 )<np .abs (O0OOOOO0O0O0OOOO0 -OOO00OO000O0OO0O0 ):#line:492
                        O0OOOOOOOO00O0000 ,OOO00OO000O0OO0O0 =OOO00OOOO0OOOO0OO ,OOO000O0000000O00 #line:493
                        O00OOOO000O000000 +=1 #line:494
                        if show_para_func !=None :#line:495
                            OO0OOO0O0O00O0O00 .update ({'step_num':O00OOOO000O000000 ,'score':round (OOO00OO000O0OO0O0 ,3 )})#line:496
                            show_para_func (O0OOOOOOOO00O0000 ,**OO0OOO0O0O00O0O00 )#line:497
                        OOO00O0O0O0OOOO00 =True #line:498
            if OOO00O0O0O0OOOO00 ==False :#line:499
                break #line:501
        return O0OOOOOOOO00O0000 ,OOO00OO000O0OO0O0 #line:502
    def opt2_tspGA (OO0O0000O00O0000O ,OO0OO0OO00O0O0OOO ,O0OOOO000O000O000 ,step_max =float ('inf')):#line:506
        OO0OO0OO00O0O0OOO ,O0OOOO000O000O000 =OO0OO0OO00O0O0OOO ,O0OOOO000O000O000 #line:508
        O0OO00000000OO00O =0 #line:509
        while 1 :#line:511
            OOO000OOO000O0OOO =False #line:512
            if O0OO00000000OO00O >=step_max :#line:513
                break #line:514
            OOOO0OO00OOO0O00O =np .arange (0 ,OO0O0000O00O0000O .para_num -1 )#line:516
            nr .shuffle (OOOO0OO00OOO0O00O )#line:518
            for OO00000OO00OOO000 in OOOO0OO00OOO0O00O :#line:519
                if OOO000OOO000O0OOO ==True :break #line:521
                OO000OOO00OO0O000 =np .arange (OO00000OO00OOO000 +1 ,OO0O0000O00O0000O .para_num )#line:523
                nr .shuffle (OO000OOO00OO0O000 )#line:524
                for OO0O0O00O0O0000O0 in OO000OOO00OO0O000 :#line:525
                    if OOO000OOO000O0OOO ==True :break #line:527
                    OOOOOOOOOOOOOO0O0 =np .hstack ((OO0OO0OO00O0O0OOO [:OO00000OO00OOO000 ],OO0OO0OO00O0O0OOO [OO00000OO00OOO000 :OO0O0O00O0O0000O0 +1 ][::-1 ],OO0OO0OO00O0O0OOO [OO0O0O00O0O0000O0 +1 :]))#line:530
                    O0OOO00O00000OO00 =OO0O0000O00O0000O .score_func (OO0O0000O00O0000O .para_range [OOOOOOOOOOOOOO0O0 ])#line:531
                    if np .abs (OO0O0000O00O0000O .aim -O0OOO00O00000OO00 )<np .abs (OO0O0000O00O0000O .aim -O0OOOO000O000O000 ):#line:534
                        OO0OO0OO00O0O0OOO ,O0OOOO000O000O000 =OOOOOOOOOOOOOO0O0 ,O0OOO00O00000OO00 #line:535
                        O0OO00000000OO00O +=1 #line:536
                        OOO000OOO000O0OOO =True #line:537
            if OOO000OOO000O0OOO ==False :#line:538
                break #line:540
        return OO0OO0OO00O0O0OOO ,O0OOOO000O000O000 #line:541
    def tspGA_multi (OO00O00O00OOO0000 ,OOOOOO000O0OO00O0 ):#line:570
        OOOOO0O00000OOOOO =OO00O00O00OOO0000 .pool [OOOOOO000O0OO00O0 ]#line:572
        OO0OO0000O0O0OOO0 =OO00O00O00OOO0000 .pool_score [OOOOOO000O0OO00O0 ]#line:573
        O0OO0O0OOOO0OO0O0 =np .ones ((OO00O00O00OOO0000 .child_num ,OO00O00O00OOO0000 .para_num ),dtype =int )#line:574
        OOOOO00O000000OO0 =np .zeros (OO00O00O00OOO0000 .child_num )#line:575
        OOOOOO00000O0OOO0 =np .hstack ((OOOOO0O00000OOOOO [:,-2 :].reshape (OO00O00O00OOO0000 .parent_num ,2 ),OOOOO0O00000OOOOO ,OOOOO0O00000OOOOO [:,:2 ].reshape (OO00O00O00OOO0000 .parent_num ,2 )))#line:580
        for O0OOOO0OOO0000O00 in range (OO00O00O00OOO0000 .child_num ):#line:583
            O0000O000OO000O00 =OOOOO0O00000OOOOO [nr .randint (OO00O00O00OOO0000 .parent_num ),0 ]#line:585
            if nr .rand ()<(1.0 /OO00O00O00OOO0000 .para_num ):#line:586
                O0000O000OO000O00 =nr .choice (OO00O00O00OOO0000 .para_index )#line:587
            O0OO0O0OOOO0OO0O0 [O0OOOO0OOO0000O00 ,0 ]=O0000O000OO000O00 #line:588
            for O00O0000OO00OOO00 in range (1 ,OO00O00O00OOO0000 .para_num ):#line:590
                OO0OO0OOO0O00OOOO =np .zeros ((OO00O00O00OOO0000 .parent_num ,OO00O00O00OOO0000 .para_num +4 ),dtype =bool )#line:592
                OO0OO0OO0OOO00000 =np .zeros ((OO00O00O00OOO0000 .parent_num ,OO00O00O00OOO0000 .para_num +4 ),dtype =bool )#line:593
                OO0OO0OOO0O00OOOO [:,1 :-3 ]+=(OO00O00O00OOO0000 .parent ==O0000O000OO000O00 )#line:595
                OO0OO0OOO0O00OOOO [:,3 :-1 ]+=(OO00O00O00OOO0000 .parent ==O0000O000OO000O00 )#line:596
                OO0OO0OO0OOO00000 [:,0 :-4 ]+=(OO00O00O00OOO0000 .parent ==O0000O000OO000O00 )#line:597
                OO0OO0OO0OOO00000 [:,4 :]+=(OO00O00O00OOO0000 .parent ==O0000O000OO000O00 )#line:598
                OOO00O0OO00O0OOO0 =np .ones (OO00O00O00OOO0000 .para_num )*(1.0 /OO00O00O00OOO0000 .para_num )#line:601
                for O00OOO0OOOO0O0OO0 in OOOOOO00000O0OOO0 [OO0OO0OOO0O00OOOO ]:#line:602
                    OOO00O0OO00O0OOO0 [np .where (OO00O00O00OOO0000 .para_index ==O00OOO0OOOO0O0OO0 )[0 ]]+=1.0 /OO00O00O00OOO0000 .parent_num #line:603
                for O00OOO0OOOO0O0OO0 in OOOOOO00000O0OOO0 [OO0OO0OO0OOO00000 ]:#line:604
                    OOO00O0OO00O0OOO0 [np .where (OO00O00O00OOO0000 .para_index ==O00OOO0OOOO0O0OO0 )[0 ]]+=0.1 /OO00O00O00OOO0000 .parent_num #line:605
                for O00OOO0OOOO0O0OO0 in O0OO0O0OOOO0OO0O0 [O0OOOO0OOO0000O00 ,0 :O00O0000OO00OOO00 ]:#line:608
                    OOO00O0OO00O0OOO0 [np .where (OO00O00O00OOO0000 .para_index ==O00OOO0OOOO0O0OO0 )[0 ]]=0.0 #line:609
                OOO00O0OO00O0OOO0 *=1.0 /np .sum (OOO00O0OO00O0OOO0 )#line:612
                O0000O000OO000O00 =nr .choice (OO00O00O00OOO0000 .para_index ,p =OOO00O0OO00O0OOO0 )#line:613
                O0OO0O0OOOO0OO0O0 [O0OOOO0OOO0000O00 ,O00O0000OO00OOO00 ]=O0000O000OO000O00 #line:615
        for O0OOOO0OOO0000O00 in range (OO00O00O00OOO0000 .child_num ):#line:619
            OOO0OO0OO0O0O0000 =OO00O00O00OOO0000 .para_range [O0OO0O0OOOO0OO0O0 [O0OOOO0OOO0000O00 ]]#line:620
            OOOOO00O000000OO0 [O0OOOO0OOO0000O00 ]=OO00O00O00OOO0000 .score_func (OOO0OO0OO0O0O0000 )#line:621
        OOOOO0OOOO00O0OOO =np .vstack ((O0OO0O0OOOO0OO0O0 ,OOOOO0O00000OOOOO ))#line:623
        O0O0OOOO00OOO0OOO =np .hstack ((OOOOO00O000000OO0 ,OO0OO0000O0O0OOO0 ))#line:624
        for O0OOOO0OOO0000O00 in range (OO00O00O00OOO0000 .family_num ):#line:626
            OOOOO0OOOO00O0OOO [O0OOOO0OOO0000O00 ],O0O0OOOO00OOO0OOO [O0OOOO0OOO0000O00 ]=OO00O00O00OOO0000 .opt2_tspGA (OOOOO0OOOO00O0OOO [O0OOOO0OOO0000O00 ],O0O0OOOO00OOO0OOO [O0OOOO0OOO0000O00 ],step_max =OO00O00O00OOO0000 .opt2_num )#line:627
        O0OOOOOOOOO00OOOO =np .argpartition (np .abs (OO00O00O00OOO0000 .aim -O0O0OOOO00OOO0OOO ),OO00O00O00OOO0000 .parent_num )[:OO00O00O00OOO0000 .parent_num ]#line:629
        OO00O00O00OOO0000 .pool [OOOOOO000O0OO00O0 ]=OOOOO0OOOO00O0OOO [O0OOOOOOOOO00OOOO ]#line:630
        OO00O00O00OOO0000 .pool_score [OOOOOO000O0OO00O0 ]=O0O0OOOO00OOO0OOO [O0OOOOOOOOO00OOOO ]#line:631
    def tspGA (O0O000O0OOO00OO00 ,O0OOO0O00OO0O00O0 ,OO000O0O0OO00O0OO ,OOOOOOOO00000O0O0 ,show_pool_func ='bar',seed =None ,pool_num =None ,max_gen =None ,core_num =1 ):#line:633
        O0OOO0O00OO0O00O0 =np .array (O0OOO0O00OO0O00O0 )#line:638
        O0O000O0OOO00OO00 .setting_1 (O0OOO0O00OO0O00O0 ,OO000O0O0OO00O0OO ,OOOOOOOO00000O0O0 ,show_pool_func ,seed ,pool_num ,max_gen ,core_num )#line:641
        O0O000O0OOO00OO00 .setting_2 (O0O000O0OOO00OO00 .para_num *10 ,2 ,4 )#line:642
        O0O000O0OOO00OO00 .setting_3 (int )#line:643
        O0O000O0OOO00OO00 .print_info ()#line:644
        O0O000O0OOO00OO00 .para_index =np .arange (O0O000O0OOO00OO00 .para_num )#line:647
        O0O000O0OOO00OO00 .opt2_num =1 #line:648
        for OOO00OO0000OOOOO0 in range (O0O000O0OOO00OO00 .pool_num ):#line:651
            O0O000O0OOO00OO00 .pool [OOO00OO0000OOOOO0 ]=deepcopy (O0O000O0OOO00OO00 .para_index )#line:652
            nr .shuffle (O0O000O0OOO00OO00 .pool [OOO00OO0000OOOOO0 ])#line:653
        O0O000O0OOO00OO00 .score_pool ()#line:656
        for OOO00OO0000OOOOO0 in range (O0O000O0OOO00OO00 .pool_num ):#line:659
            O0O000O0OOO00OO00 .pool [OOO00OO0000OOOOO0 ],O0O000O0OOO00OO00 .pool_score [OOO00OO0000OOOOO0 ]=O0O000O0OOO00OO00 .opt2_tspGA (O0O000O0OOO00OO00 .pool [OOO00OO0000OOOOO0 ],O0O000O0OOO00OO00 .pool_score [OOO00OO0000OOOOO0 ],step_max =O0O000O0OOO00OO00 .opt2_num )#line:660
            if O0O000O0OOO00OO00 .show_pool_func !=None :#line:661
                O0O00OOOOO0O0000O ='\rMini 2-opting first gen {}/{}        '.format (OOO00OO0000OOOOO0 +1 ,O0O000O0OOO00OO00 .pool_num )#line:662
                print (O0O00OOOOO0O0000O ,end ='')#line:663
        if O0O000O0OOO00OO00 .show_pool_func !=None :print ()#line:664
        O0O000O0OOO00OO00 .save_best_mean ()#line:667
        O0O000O0OOO00OO00 .init_score_range =(np .min (O0O000O0OOO00OO00 .pool_score ),np .max (O0O000O0OOO00OO00 .pool_score ))#line:669
        O0O000O0OOO00OO00 .init_gap_mean =deepcopy (O0O000O0OOO00OO00 .gap_mean )#line:670
        if O0O000O0OOO00OO00 .show_pool_func ==None :pass #line:673
        elif O0O000O0OOO00OO00 .show_pool_func =='bar':O0O000O0OOO00OO00 .show_pool_bar (0 )#line:674
        elif O0O000O0OOO00OO00 .show_pool_func =='print':O0O000O0OOO00OO00 .show_pool_print (0 )#line:675
        elif O0O000O0OOO00OO00 .show_pool_func =='plot':O0O000O0OOO00OO00 .show_pool_plot (0 )#line:676
        elif callable (O0O000O0OOO00OO00 .show_pool_func ):O0O000O0OOO00OO00 .show_pool (0 )#line:677
        elif type (show_pool_func )==str :#line:678
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:679
                if not os .path .exists (show_pool_func ):os .mkdir (show_pool_func )#line:680
                O0O000O0OOO00OO00 .show_pool_save (0 )#line:681
        OO000O000O00OOO00 =0 #line:684
        for O00000000000OOO00 in range (1 ,O0O000O0OOO00OO00 .max_n +1 ):#line:685
            OO0O0O0OOOO000000 =np .arange (O0O000O0OOO00OO00 .pool_num )#line:690
            nr .shuffle (OO0O0O0OOOO000000 )#line:691
            OO0O0O0OOOO000000 =OO0O0O0OOOO000000 .reshape ((O0O000O0OOO00OO00 .pool_num //O0O000O0OOO00OO00 .parent_num ),O0O000O0OOO00OO00 .parent_num )#line:692
            Parallel (n_jobs =O0O000O0OOO00OO00 .core_num ,require ='sharedmem')([delayed (O0O000O0OOO00OO00 .tspGA_multi )(OOO0OOOO00O000000 )for OOO0OOOO00O000000 in OO0O0O0OOOO000000 ])#line:695
            OO000O000O00OOO00 +=O0O000O0OOO00OO00 .end_check ()#line:752
            O0O000O0OOO00OO00 .save_best_mean ()#line:755
            if O0O000O0OOO00OO00 .show_pool_func ==None :pass #line:758
            elif O0O000O0OOO00OO00 .show_pool_func =='bar':O0O000O0OOO00OO00 .show_pool_bar (O00000000000OOO00 *O0O000O0OOO00OO00 .pool_num )#line:759
            elif O0O000O0OOO00OO00 .show_pool_func =='print':O0O000O0OOO00OO00 .show_pool_print (O00000000000OOO00 *O0O000O0OOO00OO00 .pool_num )#line:760
            elif O0O000O0OOO00OO00 .show_pool_func =='plot':O0O000O0OOO00OO00 .show_pool_plot (O00000000000OOO00 *O0O000O0OOO00OO00 .pool_num )#line:761
            elif callable (O0O000O0OOO00OO00 .show_pool_func ):O0O000O0OOO00OO00 .show_pool (O00000000000OOO00 *O0O000O0OOO00OO00 .pool_num )#line:762
            elif type (show_pool_func )==str :#line:763
                if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:764
                    O0O000O0OOO00OO00 .show_pool_save (O00000000000OOO00 )#line:765
            if OO000O000O00OOO00 >=1 :#line:768
                break #line:769
        O0000OO0OO0OOO0OO =O0O000O0OOO00OO00 .para_range [O0O000O0OOO00OO00 .pool_best ]#line:772
        if O0O000O0OOO00OO00 .show_pool_func =='bar':print ()#line:775
        elif type (show_pool_func )==str :#line:776
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:777
                print ()#line:778
        O0O000O0OOO00OO00 .print_result (O0000OO0OO0OOO0OO )#line:781
        return O0000OO0OO0OOO0OO ,O0O000O0OOO00OO00 .score_best #line:783
    def dcGA_multi (O00O0O00OO00OO00O ,O00O00O000O000OO0 ):#line:811
        OOOOO0O0OOO0O0OO0 =O00O0O00OO00OO00O .pool [O00O00O000O000OO0 ]#line:813
        OO0OOO0O0O0000O00 =O00O0O00OO00OO00O .pool_score [O00O00O000O000OO0 ]#line:814
        OO0000O00000OO000 =np .zeros ((O00O0O00OO00OO00O .child_num ,O00O0O00OO00OO00O .para_num ),dtype =int )#line:815
        O00OO0OO00OO000OO =np .zeros (O00O0O00OO00OO00O .child_num )#line:816
        if O00O0O00OO00OO00O .para_num >=3 :#line:819
            O0O000OO0O000O0OO =nr .choice (range (1 ,O00O0O00OO00OO00O .para_num ),2 ,replace =False )#line:823
            if O0O000OO0O000O0OO [0 ]>O0O000OO0O000O0OO [1 ]:#line:824
                O0O000OO0O000O0OO [0 ],O0O000OO0O000O0OO [1 ]=O0O000OO0O000O0OO [1 ],O0O000OO0O000O0OO [0 ]#line:825
            for OO0OO000OOO000O00 in range (len (O00O0O00OO00OO00O .choice )):#line:827
                OO0000O00000OO000 [OO0OO000OOO000O00 ]=np .hstack ((OOOOO0O0OOO0O0OO0 [O00O0O00OO00OO00O .choice [OO0OO000OOO000O00 ,0 ],:O0O000OO0O000O0OO [0 ]],OOOOO0O0OOO0O0OO0 [O00O0O00OO00OO00O .choice [OO0OO000OOO000O00 ,1 ],O0O000OO0O000O0OO [0 ]:O0O000OO0O000O0OO [1 ]],OOOOO0O0OOO0O0OO0 [O00O0O00OO00OO00O .choice [OO0OO000OOO000O00 ,2 ],O0O000OO0O000O0OO [1 ]:]))#line:830
            for OO0OO000OOO000O00 in [2 ,3 ]:#line:835
                O0000OO00OOOO0O00 =nr .randint (0 ,2 ,O00O0O00OO00OO00O .para_num )#line:836
                OO0000O00000OO000 [OO0OO000OOO000O00 ][O0000OO00OOOO0O00 ==0 ]=OOOOO0O0OOO0O0OO0 [0 ][O0000OO00OOOO0O00 ==0 ]#line:837
                OO0000O00000OO000 [OO0OO000OOO000O00 ][O0000OO00OOOO0O00 ==1 ]=OOOOO0O0OOO0O0OO0 [1 ][O0000OO00OOOO0O00 ==1 ]#line:838
            for O00OOO000000OOOO0 in OO0000O00000OO000 :#line:842
                for O00O00000OO0O00O0 in range (O00O0O00OO00OO00O .para_num ):#line:843
                    if nr .rand ()<(1.0 /O00O0O00OO00OO00O .para_num ):#line:844
                        O00OOO000000OOOO0 [O00O00000OO0O00O0 ]=nr .choice (O00O0O00OO00OO00O .para_index [O00O00000OO0O00O0 ])#line:845
        elif O00O0O00OO00OO00O .para_num ==2 :#line:849
            OO0000O00000OO000 [:2 ]=np .array ([[OOOOO0O0OOO0O0OO0 [0 ,0 ],OOOOO0O0OOO0O0OO0 [1 ,1 ]],[OOOOO0O0OOO0O0OO0 [0 ,1 ],OOOOO0O0OOO0O0OO0 [1 ,0 ]]])#line:851
            for OO0OO000OOO000O00 in range (2 ,O00O0O00OO00OO00O .child_num ):#line:853
                for O00O00000OO0O00O0 in range (2 ):#line:854
                    OO0000O00000OO000 [OO0OO000OOO000O00 ,O00O00000OO0O00O0 ]=nr .choice (O00O0O00OO00OO00O .para_index [O00O00000OO0O00O0 ])#line:855
        elif O00O0O00OO00OO00O .para_num ==1 :#line:857
            for OO0OO000OOO000O00 in range (O00O0O00OO00OO00O .child_num ):#line:859
                OO0000O00000OO000 [OO0OO000OOO000O00 ]=nr .choice (O00O0O00OO00OO00O .para_index [0 ])#line:860
        for OO0OO000OOO000O00 in range (O00O0O00OO00OO00O .child_num ):#line:864
            O00O0OO0OOO00O0O0 =[]#line:865
            for O00O00000OO0O00O0 in range (O00O0O00OO00OO00O .para_num ):#line:866
                O00O0OO0OOO00O0O0 .append (O00O0O00OO00OO00O .para_range [O00O00000OO0O00O0 ][OO0000O00000OO000 [OO0OO000OOO000O00 ,O00O00000OO0O00O0 ]])#line:867
            O00O0OO0OOO00O0O0 =np .array (O00O0OO0OOO00O0O0 )#line:868
            O00OO0OO00OO000OO [OO0OO000OOO000O00 ]=O00O0O00OO00OO00O .score_func (O00O0OO0OOO00O0O0 )#line:869
        OOO000OOOOO0O0OO0 =np .vstack ((OO0000O00000OO000 ,OOOOO0O0OOO0O0OO0 ))#line:871
        O00OO0OO000OO00O0 =np .hstack ((O00OO0OO00OO000OO ,OO0OOO0O0O0000O00 ))#line:872
        OOOOO00OOO0O0000O =np .argpartition (np .abs (O00O0O00OO00OO00O .aim -O00OO0OO000OO00O0 ),O00O0O00OO00OO00O .parent_num )[:O00O0O00OO00OO00O .parent_num ]#line:874
        O00O0O00OO00OO00O .pool [O00O00O000O000OO0 ]=OOO000OOOOO0O0OO0 [OOOOO00OOO0O0000O ]#line:875
        O00O0O00OO00OO00O .pool_score [O00O00O000O000OO0 ]=O00OO0OO000OO00O0 [OOOOO00OOO0O0000O ]#line:876
    def dcGA (O0OO00O0OO0O000OO ,O0OOO0O0OO000O0OO ,O00O0OO00OOO0O00O ,OO000O000OO0OOO0O ,show_pool_func ='bar',seed =None ,pool_num =None ,max_gen =None ,core_num =1 ):#line:879
        if type (O0OOO0O0OO000O0OO )==list :#line:884
            if isinstance (O0OOO0O0OO000O0OO [0 ],list )==False :#line:885
                O0OOO0O0OO000O0OO =[O0OOO0O0OO000O0OO ]#line:886
        if type (O0OOO0O0OO000O0OO )==np .ndarray :#line:887
            if O0OOO0O0OO000O0OO .ndim ==1 :#line:888
                O0OOO0O0OO000O0OO =O0OOO0O0OO000O0OO .reshape (1 ,len (O0OOO0O0OO000O0OO ))#line:889
        O0OO00O0OO0O000OO .setting_1 (O0OOO0O0OO000O0OO ,O00O0OO00OOO0O00O ,OO000O000OO0OOO0O ,show_pool_func ,seed ,pool_num ,max_gen ,core_num )#line:892
        O0OO00O0OO0O000OO .setting_2 (O0OO00O0OO0O000OO .para_num *10 ,2 ,4 )#line:893
        O0OO00O0OO0O000OO .setting_3 (int )#line:894
        O0OO00O0OO0O000OO .print_info ()#line:895
        O0OO00O0OO0O000OO .para_index =[]#line:898
        for OOO0O0000O0O0O000 in range (O0OO00O0OO0O000OO .para_num ):#line:899
            O0OO00O0OO0O000OO .para_index .append (np .arange (len (O0OO00O0OO0O000OO .para_range [OOO0O0000O0O0O000 ])))#line:900
        O0OO00O0OO0O000OO .choice =np .array ([[0 ,1 ,0 ],[1 ,0 ,1 ]],dtype =int )#line:901
        for OOO0O0000O0O0O000 in range (O0OO00O0OO0O000OO .pool_num ):#line:904
            for OOOO000OO0O0OOO0O in range (O0OO00O0OO0O000OO .para_num ):#line:905
                O0OO00O0OO0O000OO .pool [OOO0O0000O0O0O000 ,OOOO000OO0O0OOO0O ]=nr .choice (O0OO00O0OO0O000OO .para_index [OOOO000OO0O0OOO0O ])#line:906
        O0OO00O0OO0O000OO .score_pool_dc ()#line:909
        O0OO00O0OO0O000OO .save_best_mean ()#line:910
        O0OO00O0OO0O000OO .init_score_range =(np .min (O0OO00O0OO0O000OO .pool_score ),np .max (O0OO00O0OO0O000OO .pool_score ))#line:912
        O0OO00O0OO0O000OO .init_gap_mean =deepcopy (O0OO00O0OO0O000OO .gap_mean )#line:913
        if O0OO00O0OO0O000OO .show_pool_func ==None :pass #line:916
        elif O0OO00O0OO0O000OO .show_pool_func =='bar':O0OO00O0OO0O000OO .show_pool_bar (0 )#line:917
        elif O0OO00O0OO0O000OO .show_pool_func =='print':O0OO00O0OO0O000OO .show_pool_print (0 )#line:918
        elif O0OO00O0OO0O000OO .show_pool_func =='plot':O0OO00O0OO0O000OO .show_pool_plot (0 )#line:919
        elif callable (O0OO00O0OO0O000OO .show_pool_func ):O0OO00O0OO0O000OO .show_pool_dc (0 )#line:920
        elif type (show_pool_func )==str :#line:921
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:922
                if not os .path .exists (show_pool_func ):os .mkdir (show_pool_func )#line:923
                O0OO00O0OO0O000OO .show_pool_save (0 )#line:924
        OO00OOO0O00OOO0O0 =0 #line:927
        for OO0OO0OO00O0OO00O in range (1 ,O0OO00O0OO0O000OO .max_n +1 ):#line:928
            O00O00000OOOO0OO0 =np .arange (O0OO00O0OO0O000OO .pool_num )#line:931
            nr .shuffle (O00O00000OOOO0OO0 )#line:932
            O00O00000OOOO0OO0 =O00O00000OOOO0OO0 .reshape ((O0OO00O0OO0O000OO .pool_num //O0OO00O0OO0O000OO .parent_num ),O0OO00O0OO0O000OO .parent_num )#line:933
            Parallel (n_jobs =O0OO00O0OO0O000OO .core_num ,require ='sharedmem')([delayed (O0OO00O0OO0O000OO .dcGA_multi )(O00OOO00O00O0O00O )for O00OOO00O00O0O00O in O00O00000OOOO0OO0 ])#line:936
            OO00OOO0O00OOO0O0 +=O0OO00O0OO0O000OO .end_check ()#line:992
            O0OO00O0OO0O000OO .save_best_mean ()#line:995
            if O0OO00O0OO0O000OO .show_pool_func ==None :pass #line:998
            elif O0OO00O0OO0O000OO .show_pool_func =='bar':O0OO00O0OO0O000OO .show_pool_bar (OO0OO0OO00O0OO00O *O0OO00O0OO0O000OO .pool_num )#line:999
            elif O0OO00O0OO0O000OO .show_pool_func =='print':O0OO00O0OO0O000OO .show_pool_print (OO0OO0OO00O0OO00O *O0OO00O0OO0O000OO .pool_num )#line:1000
            elif O0OO00O0OO0O000OO .show_pool_func =='plot':O0OO00O0OO0O000OO .show_pool_plot (OO0OO0OO00O0OO00O *O0OO00O0OO0O000OO .pool_num )#line:1001
            elif callable (O0OO00O0OO0O000OO .show_pool_func ):O0OO00O0OO0O000OO .show_pool_dc (OO0OO0OO00O0OO00O *O0OO00O0OO0O000OO .pool_num )#line:1002
            elif type (show_pool_func )==str :#line:1003
                if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1004
                    O0OO00O0OO0O000OO .show_pool_save (OO0OO0OO00O0OO00O )#line:1005
            if OO00OOO0O00OOO0O0 >=1 :#line:1008
                break #line:1009
        OO0000OOO0OO0O00O =[]#line:1012
        for OOOO000OO0O0OOO0O in range (O0OO00O0OO0O000OO .para_num ):#line:1013
            OO0000OOO0OO0O00O .append (O0OO00O0OO0O000OO .para_range [OOOO000OO0O0OOO0O ][O0OO00O0OO0O000OO .pool [O0OO00O0OO0O000OO .best_index ,OOOO000OO0O0OOO0O ]])#line:1014
        OO0000OOO0OO0O00O =np .array (OO0000OOO0OO0O00O )#line:1015
        if O0OO00O0OO0O000OO .show_pool_func =='bar':print ()#line:1018
        elif type (show_pool_func )==str :#line:1019
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1020
                print ()#line:1021
        O0OO00O0OO0O000OO .print_result (OO0000OOO0OO0O00O )#line:1024
        return OO0000OOO0OO0O00O ,O0OO00O0OO0O000OO .score_best #line:1026
    def setGA_multi (O0OO0O00OO00OO0OO ,OO00OOOO00O0O00OO ):#line:1056
        O00OOOOO0000000O0 =O0OO0O00OO00OO0OO .pool [OO00OOOO00O0O00OO ]#line:1058
        OOO0OOOOOO00OOOO0 =O0OO0O00OO00OO0OO .pool_score [OO00OOOO00O0O00OO ]#line:1059
        OO0O00O0O0000O0OO =np .zeros ((O0OO0O00OO00OO0OO .child_num ,O0OO0O00OO00OO0OO .para_num ),dtype =int )#line:1060
        O0000OOOOOO00O0OO =np .zeros (O0OO0O00OO00OO0OO .child_num )#line:1061
        O0000O00OOOOOO0OO =set (O00OOOOO0000000O0 [0 ])&set (O00OOOOO0000000O0 [1 ])#line:1066
        OOO000O00OOO00O0O =set (O0OO0O00OO00OO0OO .para_index )-O0000O00OOOOOO0OO #line:1068
        for O00OOOOOO00000OO0 in range (len (OO0O00O0O0000O0OO )):#line:1070
            O00O00OOO0OO0OOOO =nr .choice (np .array (list (OOO000O00OOO00O0O )),O0OO0O00OO00OO0OO .set_num -len (O0000O00OOOOOO0OO ),replace =False )#line:1071
            OO0O00O0O0000O0OO [O00OOOOOO00000OO0 ]=np .hstack ((np .array (list (O0000O00OOOOOO0OO )),O00O00OOO0OO0OOOO ))#line:1073
        for O00O0O0OO0O00O000 in OO0O00O0O0000O0OO [2 :]:#line:1080
            for O0O0O0OOO00OOOOOO in range (O0OO0O00OO00OO0OO .set_num ):#line:1081
                if nr .rand ()<(1.0 /O0OO0O00OO00OO0OO .set_num ):#line:1082
                    O0O00OO0O0OOOOOO0 =nr .choice (O0OO0O00OO00OO0OO .para_index )#line:1083
                    if O0O00OO0O0OOOOOO0 not in O00O0O0OO0O00O000 :#line:1084
                        O00O0O0OO0O00O000 [O0O0O0OOO00OOOOOO ]=O0O00OO0O0OOOOOO0 #line:1085
        for O00OOOOOO00000OO0 in range (O0OO0O00OO00OO0OO .child_num ):#line:1090
            O0000O00OOOO000O0 =O0OO0O00OO00OO0OO .para_range [OO0O00O0O0000O0OO [O00OOOOOO00000OO0 ]]#line:1091
            O0000OOOOOO00O0OO [O00OOOOOO00000OO0 ]=O0OO0O00OO00OO0OO .score_func (O0000O00OOOO000O0 )#line:1092
        OO0O0OOOO0OO00OOO =np .vstack ((OO0O00O0O0000O0OO ,O00OOOOO0000000O0 ))#line:1094
        OOO00OO000O0OO000 =np .hstack ((O0000OOOOOO00O0OO ,OOO0OOOOOO00OOOO0 ))#line:1095
        OO0O0OO000OO0000O =np .argpartition (np .abs (O0OO0O00OO00OO0OO .aim -OOO00OO000O0OO000 ),O0OO0O00OO00OO0OO .parent_num )[:O0OO0O00OO00OO0OO .parent_num ]#line:1097
        O0OO0O00OO00OO0OO .pool [OO00OOOO00O0O00OO ]=OO0O0OOOO0OO00OOO [OO0O0OO000OO0000O ]#line:1098
        O0OO0O00OO00OO0OO .pool_score [OO00OOOO00O0O00OO ]=OOO00OO000O0OO000 [OO0O0OO000OO0000O ]#line:1099
    def setGA (O0O00OOO0O0000O00 ,OO00O0O0OOOOOO000 ,OOOO0OO0000O0O00O ,O00O000O00OOOO000 ,O0000O0OO0O00OOOO ,show_pool_func ='bar',seed =None ,pool_num =None ,max_gen =None ,core_num =1 ):#line:1101
        OO00O0O0OOOOOO000 =np .array (OO00O0O0OOOOOO000 )#line:1106
        O0O00OOO0O0000O00 .setting_1 (OO00O0O0OOOOOO000 ,O00O000O00OOOO000 ,O0000O0OO0O00OOOO ,show_pool_func ,seed ,pool_num ,max_gen ,core_num )#line:1109
        O0O00OOO0O0000O00 .set_num =OOOO0OO0000O0O00O #line:1110
        O0O00OOO0O0000O00 .para_num =O0O00OOO0O0000O00 .set_num #line:1111
        O0O00OOO0O0000O00 .setting_2 (O0O00OOO0O0000O00 .para_num *10 ,2 ,4 )#line:1112
        O0O00OOO0O0000O00 .setting_3 (int )#line:1113
        O0O00OOO0O0000O00 .print_info ()#line:1114
        O0O00OOO0O0000O00 .para_index =np .arange (len (O0O00OOO0O0000O00 .para_range ))#line:1117
        for OOOO0O000O0000O0O in range (O0O00OOO0O0000O00 .pool_num ):#line:1120
            O0O00OOO0O0000O00 .pool [OOOO0O000O0000O0O ]=nr .choice (O0O00OOO0O0000O00 .para_index ,O0O00OOO0O0000O00 .set_num ,replace =False )#line:1121
        O0O00OOO0O0000O00 .score_pool ()#line:1125
        O0O00OOO0O0000O00 .save_best_mean ()#line:1126
        O0O00OOO0O0000O00 .init_score_range =(np .min (O0O00OOO0O0000O00 .pool_score ),np .max (O0O00OOO0O0000O00 .pool_score ))#line:1128
        O0O00OOO0O0000O00 .init_gap_mean =deepcopy (O0O00OOO0O0000O00 .gap_mean )#line:1129
        if O0O00OOO0O0000O00 .show_pool_func ==None :pass #line:1132
        elif O0O00OOO0O0000O00 .show_pool_func =='bar':O0O00OOO0O0000O00 .show_pool_bar (0 )#line:1133
        elif O0O00OOO0O0000O00 .show_pool_func =='print':O0O00OOO0O0000O00 .show_pool_print (0 )#line:1134
        elif O0O00OOO0O0000O00 .show_pool_func =='plot':O0O00OOO0O0000O00 .show_pool_plot (0 )#line:1135
        elif callable (O0O00OOO0O0000O00 .show_pool_func ):O0O00OOO0O0000O00 .show_pool (0 )#line:1136
        elif type (show_pool_func )==str :#line:1137
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1138
                if not os .path .exists (show_pool_func ):os .mkdir (show_pool_func )#line:1139
                O0O00OOO0O0000O00 .show_pool_save (0 )#line:1140
        OO0OOO00O0O0O00O0 =0 #line:1143
        for O000OOO00O0OOO0O0 in range (1 ,O0O00OOO0O0000O00 .max_n +1 ):#line:1144
            O000OOOOOO00O00OO =np .arange (O0O00OOO0O0000O00 .pool_num )#line:1147
            nr .shuffle (O000OOOOOO00O00OO )#line:1148
            O000OOOOOO00O00OO =O000OOOOOO00O00OO .reshape ((O0O00OOO0O0000O00 .pool_num //O0O00OOO0O0000O00 .parent_num ),O0O00OOO0O0000O00 .parent_num )#line:1149
            Parallel (n_jobs =O0O00OOO0O0000O00 .core_num ,require ='sharedmem')([delayed (O0O00OOO0O0000O00 .setGA_multi )(OOO00O00000OO0000 )for OOO00O00000OO0000 in O000OOOOOO00O00OO ])#line:1152
            OO0OOO00O0O0O00O0 +=O0O00OOO0O0000O00 .end_check ()#line:1188
            O0O00OOO0O0000O00 .save_best_mean ()#line:1191
            if O0O00OOO0O0000O00 .show_pool_func ==None :pass #line:1194
            elif O0O00OOO0O0000O00 .show_pool_func =='bar':O0O00OOO0O0000O00 .show_pool_bar (O000OOO00O0OOO0O0 *O0O00OOO0O0000O00 .pool_num )#line:1195
            elif O0O00OOO0O0000O00 .show_pool_func =='print':O0O00OOO0O0000O00 .show_pool_print (O000OOO00O0OOO0O0 *O0O00OOO0O0000O00 .pool_num )#line:1196
            elif O0O00OOO0O0000O00 .show_pool_func =='plot':O0O00OOO0O0000O00 .show_pool_plot (O000OOO00O0OOO0O0 *O0O00OOO0O0000O00 .pool_num )#line:1197
            elif callable (O0O00OOO0O0000O00 .show_pool_func ):O0O00OOO0O0000O00 .show_pool (O000OOO00O0OOO0O0 *O0O00OOO0O0000O00 .pool_num )#line:1198
            elif type (show_pool_func )==str :#line:1199
                if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1200
                    O0O00OOO0O0000O00 .show_pool_save (O000OOO00O0OOO0O0 )#line:1201
            if OO0OOO00O0O0O00O0 >=1 :#line:1204
                break #line:1205
        OO0O0OO000OO0O0O0 =O0O00OOO0O0000O00 .para_range [O0O00OOO0O0000O00 .pool_best ]#line:1208
        if O0O00OOO0O0000O00 .show_pool_func =='bar':print ()#line:1211
        elif type (show_pool_func )==str :#line:1212
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1213
                print ()#line:1214
        O0O00OOO0O0000O00 .print_result (OO0O0OO000OO0O0O0 )#line:1217
        return OO0O0OO000OO0O0O0 ,O0O00OOO0O0000O00 .score_best #line:1219
    def rcGA_multi (OOOOOO0OOO0O00OO0 ,OO0O0OOOO0O0OOO00 ):#line:1247
        O00OOOO0O0OOOO0OO =OOOOOO0OOO0O00OO0 .pool [OO0O0OOOO0O0OOO00 ]#line:1249
        OOOO0OO0O00OO000O =OOOOOO0OOO0O00OO0 .pool_score [OO0O0OOOO0O0OOO00 ]#line:1250
        O000O000OOO000O00 =np .ones ((OOOOOO0OOO0O00OO0 .child_num ,OOOOOO0OOO0O00OO0 .para_num ),dtype =float )*2.0 #line:1251
        O00OO0OO0OOOO000O =np .zeros (OOOOOO0OOO0O00OO0 .child_num )#line:1252
        O0000OO0O00OOO0OO =np .mean (O00OOOO0O0OOOO0OO ,axis =0 )#line:1257
        for OO0OO0000OOOOO0OO in range (OOOOOO0OOO0O00OO0 .child_num ):#line:1260
            for OOO00000O0000O00O in range (OOOOOO0OOO0O00OO0 .para_num ):#line:1261
                O000O000OOO000O00 [OO0OO0000OOOOO0OO ,OOO00000O0000O00O ]=O0000OO0O00OOO0OO [OOO00000O0000O00O ]#line:1263
                for O0OOO0O000O0OO0O0 in range (OOOOOO0OOO0O00OO0 .parent_num ):#line:1265
                    O000O000OOO000O00 [OO0OO0000OOOOO0OO ,OOO00000O0000O00O ]+=nr .normal (0 ,OOOOOO0OOO0O00OO0 .sd )*(O00OOOO0O0OOOO0OO [O0OOO0O000O0OO0O0 ][OOO00000O0000O00O ]-O0000OO0O00OOO0OO [OOO00000O0000O00O ])#line:1266
        O000O000OOO000O00 =np .clip (O000O000OOO000O00 ,0.0 ,1.0 )#line:1268
        for OO0OO0000OOOOO0OO in range (OOOOOO0OOO0O00OO0 .child_num ):#line:1272
            O00OOOOO0OO0OOO00 =O000O000OOO000O00 [OO0OO0000OOOOO0OO ]*(OOOOOO0OOO0O00OO0 .para_range [:,1 ]-OOOOOO0OOO0O00OO0 .para_range [:,0 ])+OOOOOO0OOO0O00OO0 .para_range [:,0 ]#line:1273
            O00OO0OO0OOOO000O [OO0OO0000OOOOO0OO ]=OOOOOO0OOO0O00OO0 .score_func (O00OOOOO0OO0OOO00 )#line:1274
        OOO0000O0O0O0OO0O =np .vstack ((O000O000OOO000O00 ,O00OOOO0O0OOOO0OO ))#line:1276
        OOO0OOOOO000O0OO0 =np .hstack ((O00OO0OO0OOOO000O ,OOOO0OO0O00OO000O ))#line:1277
        OO0000OOOO0OO0O00 =np .argpartition (np .abs (OOOOOO0OOO0O00OO0 .aim -OOO0OOOOO000O0OO0 ),OOOOOO0OOO0O00OO0 .parent_num )[:OOOOOO0OOO0O00OO0 .parent_num ]#line:1279
        OOOOOO0OOO0O00OO0 .pool [OO0O0OOOO0O0OOO00 ]=OOO0000O0O0O0OO0O [OO0000OOOO0OO0O00 ]#line:1280
        OOOOOO0OOO0O00OO0 .pool_score [OO0O0OOOO0O0OOO00 ]=OOO0OOOOO000O0OO0 [OO0000OOOO0OO0O00 ]#line:1281
    def rcGA (OO0OO0000O00OO0OO ,O000OO00O00O0O00O ,O00OO00OOO00O0O00 ,OO000O00O00O0O00O ,show_pool_func ='bar',seed =None ,pool_num =None ,max_gen =None ,core_num =1 ):#line:1284
        O000OO00O00O0O00O =np .array (O000OO00O00O0O00O )#line:1289
        if O000OO00O00O0O00O .ndim ==1 :#line:1290
            O000OO00O00O0O00O =O000OO00O00O0O00O .reshape (1 ,2 )#line:1291
        OO0OO0000O00OO0OO .setting_1 (O000OO00O00O0O00O ,O00OO00OOO00O0O00 ,OO000O00O00O0O00O ,show_pool_func ,seed ,pool_num ,max_gen ,core_num )#line:1294
        OO0OO0000O00OO0OO .setting_2 (OO0OO0000O00OO0OO .para_num *10 ,2 ,4 )#line:1295
        OO0OO0000O00OO0OO .setting_3 (float )#line:1296
        OO0OO0000O00OO0OO .print_info ()#line:1297
        OO0OO0000O00OO0OO .sd =1.2 /math .sqrt (OO0OO0000O00OO0OO .parent_num )#line:1300
        if OO0OO0000O00OO0OO .para_num ==1 :#line:1305
            O0O0OO0OO0O00O000 =np .tile (np .array ([0.5 ]),(OO0OO0000O00OO0OO .pool_num //OO0OO0000O00OO0OO .para_num )+1 )#line:1306
        else :#line:1307
            O0O0OO0OO0O00O000 =np .tile (np .arange (0.0 ,1.000001 ,1.0 /(OO0OO0000O00OO0OO .para_num -1 )),(OO0OO0000O00OO0OO .pool_num //OO0OO0000O00OO0OO .para_num )+1 )#line:1308
        for O0O0OOOO0000O0O0O in range (OO0OO0000O00OO0OO .para_num ):#line:1311
            OO0OO0000O00OO0OO .pool [:,O0O0OOOO0000O0O0O ]=nr .permutation (O0O0OO0OO0O00O000 [:OO0OO0000O00OO0OO .pool_num ])#line:1312
        if OO0OO0000O00OO0OO .para_num ==1 :#line:1315
            OO0OO0000O00OO0OO .pool +=nr .rand (OO0OO0000O00OO0OO .pool_num ,OO0OO0000O00OO0OO .para_num )*1.0 -0.5 #line:1316
        else :#line:1317
            OO0OO0000O00OO0OO .pool +=nr .rand (OO0OO0000O00OO0OO .pool_num ,OO0OO0000O00OO0OO .para_num )*(2.0 /(3 *OO0OO0000O00OO0OO .para_num -3 ))-(1.0 /(3 *OO0OO0000O00OO0OO .para_num -3 ))#line:1318
        OO0OO0000O00OO0OO .pool =np .clip (OO0OO0000O00OO0OO .pool ,0.0 ,1.0 )#line:1321
        def OO00OOOO000000OO0 (O0OOOOO0OOOOOO0OO ):#line:1324
            O00OOOOO0O000O0OO =np .expand_dims (OO0OO0000O00OO0OO .pool ,axis =1 )-np .expand_dims (OO0OO0000O00OO0OO .pool ,axis =0 )#line:1325
            O00OOOOO0O000O0OO =np .sqrt (np .sum (O00OOOOO0O000O0OO **2 ,axis =-1 ))#line:1326
            O00OOOOO0O000O0OO =np .sum (O00OOOOO0O000O0OO ,axis =-1 )/OO0OO0000O00OO0OO .pool_num #line:1327
            return O00OOOOO0O000O0OO #line:1328
        if OO0OO0000O00OO0OO .pool_num <=5 *10 :#line:1331
            O00O0O00OOO000O0O =200 #line:1332
        elif OO0OO0000O00OO0OO .pool_num <=10 *10 :#line:1333
            O00O0O00OOO000O0O =150 #line:1334
        elif OO0OO0000O00OO0OO .pool_num <=15 *10 :#line:1335
            O00O0O00OOO000O0O =70 #line:1336
        elif OO0OO0000O00OO0OO .pool_num <=20 *10 :#line:1337
            O00O0O00OOO000O0O =30 #line:1338
        elif OO0OO0000O00OO0OO .pool_num <=30 *10 :#line:1339
            O00O0O00OOO000O0O =12 #line:1340
        else :#line:1341
            O00O0O00OOO000O0O =0 #line:1342
        O0OOOO0O0OO0OOOOO =False #line:1343
        for O0OO0O00O0OO00O00 in range (O00O0O00OOO000O0O ):#line:1344
            O0O00O000OO0000O0 =OO00OOOO000000OO0 (OO0OO0000O00OO0OO .pool )#line:1345
            O0OO000OO000O00OO =np .argmin (O0O00O000OO0000O0 )#line:1346
            OO0OO0000O00OO0OO .pool [O0OO000OO000O00OO ]=nr .rand (OO0OO0000O00OO0OO .para_num )#line:1348
            OOO0O0OOO000000O0 =OO00OOOO000000OO0 (OO0OO0000O00OO0OO .pool )#line:1349
            O00OOOOO000OO0OOO =0 #line:1351
            while np .sum (OOO0O0OOO000000O0 )<np .sum (O0O00O000OO0000O0 ):#line:1352
                OO0OO0000O00OO0OO .pool [O0OO000OO000O00OO ]=nr .rand (OO0OO0000O00OO0OO .para_num )#line:1354
                OOO0O0OOO000000O0 =OO00OOOO000000OO0 (OO0OO0000O00OO0OO .pool )#line:1355
                O00OOOOO000OO0OOO +=1 #line:1356
                if O00OOOOO000OO0OOO ==O00O0O00OOO000O0O :#line:1357
                    O0OOOO0O0OO0OOOOO =True #line:1359
                    break #line:1360
            if O0OOOO0O0OO0OOOOO ==True :#line:1361
                break #line:1362
        OO0OO0000O00OO0OO .score_pool_rc ()#line:1367
        OO0OO0000O00OO0OO .save_best_mean ()#line:1368
        OO0OO0000O00OO0OO .init_score_range =(np .min (OO0OO0000O00OO0OO .pool_score ),np .max (OO0OO0000O00OO0OO .pool_score ))#line:1370
        OO0OO0000O00OO0OO .init_gap_mean =deepcopy (OO0OO0000O00OO0OO .gap_mean )#line:1371
        if OO0OO0000O00OO0OO .show_pool_func ==None :pass #line:1374
        elif OO0OO0000O00OO0OO .show_pool_func =='bar':OO0OO0000O00OO0OO .show_pool_bar (0 )#line:1375
        elif OO0OO0000O00OO0OO .show_pool_func =='print':OO0OO0000O00OO0OO .show_pool_print (0 )#line:1376
        elif OO0OO0000O00OO0OO .show_pool_func =='plot':OO0OO0000O00OO0OO .show_pool_plot (0 )#line:1377
        elif callable (OO0OO0000O00OO0OO .show_pool_func ):OO0OO0000O00OO0OO .show_pool_rc (0 )#line:1378
        elif type (show_pool_func )==str :#line:1379
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1380
                if not os .path .exists (show_pool_func ):os .mkdir (show_pool_func )#line:1381
                OO0OO0000O00OO0OO .show_pool_save (0 )#line:1382
        O00OOOOO000OO0OOO =0 #line:1385
        for OOO0O0OOO0O000OOO in range (1 ,OO0OO0000O00OO0OO .max_n +1 ):#line:1386
            O0O0OOOOO00O00000 =np .arange (OO0OO0000O00OO0OO .pool_num )#line:1389
            nr .shuffle (O0O0OOOOO00O00000 )#line:1390
            O0O0OOOOO00O00000 =O0O0OOOOO00O00000 .reshape ((OO0OO0000O00OO0OO .pool_num //OO0OO0000O00OO0OO .parent_num ),OO0OO0000O00OO0OO .parent_num )#line:1391
            Parallel (n_jobs =OO0OO0000O00OO0OO .core_num ,require ='sharedmem')([delayed (OO0OO0000O00OO0OO .rcGA_multi )(O0O000O0OOOOO0000 )for O0O000O0OOOOO0000 in O0O0OOOOO00O00000 ])#line:1394
            OO0OO0000O00OO0OO .sd =max (OO0OO0000O00OO0OO .sd *0.995 ,0.9 /math .sqrt (OO0OO0000O00OO0OO .parent_num ))#line:1424
            O00OOOOO000OO0OOO +=OO0OO0000O00OO0OO .end_check ()#line:1427
            if np .max (np .std (OO0OO0000O00OO0OO .pool ,axis =0 ))<0.03 :#line:1430
                O00OOOOO000OO0OOO +=1 #line:1431
            OO0OO0000O00OO0OO .save_best_mean ()#line:1434
            if OO0OO0000O00OO0OO .show_pool_func ==None :pass #line:1437
            elif OO0OO0000O00OO0OO .show_pool_func =='bar':OO0OO0000O00OO0OO .show_pool_bar (OOO0O0OOO0O000OOO *OO0OO0000O00OO0OO .pool_num )#line:1438
            elif OO0OO0000O00OO0OO .show_pool_func =='print':OO0OO0000O00OO0OO .show_pool_print (OOO0O0OOO0O000OOO *OO0OO0000O00OO0OO .pool_num )#line:1439
            elif OO0OO0000O00OO0OO .show_pool_func =='plot':OO0OO0000O00OO0OO .show_pool_plot (OOO0O0OOO0O000OOO *OO0OO0000O00OO0OO .pool_num )#line:1440
            elif callable (OO0OO0000O00OO0OO .show_pool_func ):OO0OO0000O00OO0OO .show_pool_rc (OOO0O0OOO0O000OOO *OO0OO0000O00OO0OO .pool_num )#line:1441
            elif type (show_pool_func )==str :#line:1442
                if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1443
                    OO0OO0000O00OO0OO .show_pool_save (OOO0O0OOO0O000OOO )#line:1444
            if O00OOOOO000OO0OOO >=1 :#line:1447
                break #line:1448
        OO00OOOOO0O000O0O =OO0OO0000O00OO0OO .pool_best *(OO0OO0000O00OO0OO .para_range [:,1 ]-OO0OO0000O00OO0OO .para_range [:,0 ])+OO0OO0000O00OO0OO .para_range [:,0 ]#line:1451
        if OO0OO0000O00OO0OO .show_pool_func =='bar':print ()#line:1454
        elif type (show_pool_func )==str :#line:1455
            if len (show_pool_func )>0 and show_pool_func [-1 ]=='/':#line:1456
                print ()#line:1457
        OO0OO0000O00OO0OO .print_result (OO00OOOOO0O000O0O )#line:1460
        return OO00OOOOO0O000O0O ,OO0OO0000O00OO0OO .score_best #line:1462
if __name__ =='__main__':#line:1472
    pass #line:1473
