from googletrans import Translator
import pandas as pd
import itertools
import urllib2
import unicodedata
import pickle
import cPickle
import re
import warnings

warnings.filterwarnings('ignore')

# Potential bug in the Translator method. To fix see: https://github.com/ssut/py-googletrans/pull/78 
translator = Translator()

listOfEmotions = ['anger', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'normalize']
emotionD_eng={}
emotionD_ger={}

# Load all WordNetAffect emotion lists and store them in a dictionary from kylehg's github sentiment 
# analysis repo: https://github.com/kylehg/sentiment-analysis/tree/master/lexicons/wordnet
for emotion in listOfEmotions:
    if emotion not in 'normalize':
        words = []
        source = urllib2.urlopen(r"https://raw.githubusercontent.com/kylehg/sentiment-analysis/master/lexicons/wordnet/"
                                + emotion +".txt") 

        for line in source: # files are iterable
            words.append(line.split()[1:])

        # store english words in dictionary
        words = list(itertools.chain(*words))
        emotionD_eng[emotion] = words
        
        # translate and store german words
        try:
            words_ger = map(lambda x: unicodedata.normalize('NFD', translator.translate(x, dest='de').text).encode('ascii', 'ignore').lower(), words)
        except ValueError:
            pass 
        emotionD_ger[emotion] = words_ger
          
    else:
        emotionD_eng[emotion] = [[u'the']]
        emotionD_ger[emotion] = [[u'das']]


out = open('wordNetdicts.pkl', 'w')
cPickle.dump([emotionD_eng, emotionD_ger], out)
out.close() 