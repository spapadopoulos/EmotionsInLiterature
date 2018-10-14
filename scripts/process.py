import pandas as pd
import numpy as np
import requests
import os
import zipfile
import urllib2
import glob
import re
import itertools
import csv
import pickle
import cPickle
import unicodedata


# Create directories to store the .csv files
os.mkdir('eng')
os.mkdir('ger')

# Create directories to store the processed .pkl files
os.mkdir('pickledEmotions')
os.mkdir('pickledEmotions/eng')
os.mkdir('pickledEmotions/ger')

# Download Google 1-grams
for num in range(10):
    
    # English 1-grams
    url = "http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-1gram-20090715-"+str(num)+".csv.zip"
    filename = url.split("/")[-1]
    with open(filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)
        
    # German 1-grams
    url = "http://storage.googleapis.com/books/ngrams/books/googlebooks-ger-all-1gram-20090715-"+str(num)+".csv.zip"
    filename = url.split("/")[-1]
    with open(filename, "wb") as f:
        r = requests.get(url)
        f.write(r.content)



# Unzip data and move to directory
for fileName in  os.listdir('.'):
    if '.zip' in fileName:
        zip_ref = zipfile.ZipFile(fileName, 'r')
        zip_ref.extractall()
        zip_ref.close()
        
        for csvFile in glob.glob('*.csv'):
            if '-eng-' in csvFile:
                shutil.move(csvFile, "eng/"+csvFile)
            else:
                shutil.move(csvFile, "ger/"+csvFile)




# 'the' is the normalization factor
listOfEmotions = ['anger', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'the']

# load pickled emotion words dictionaries
emotionD_eng, emotionD_ger = cPickle.load(open('wordNetdicts.pkl', 'r'))

# Aggregate emotional words by year
def mapper(row):
    return unicodedata.normalize('NFD', row['word'].decode('utf-8')), int(row['year']), int(row['counts'])

def mapper2(row):
    return (row[1], row[2])

aggrEmotDic={}




# Process
for lang in ['eng', 'ger']:

    if lang == 'eng':
    	# Due to change in encoding in compute environment
        emotionD_eng['the'] = [[u'the']]
        emotionDic = emotionD_eng
    else:
        emotionD_ger['the'] = [[u'das']]
        emotionDic = emotionD_ger
        

    for emotion in listOfEmotions:
        def filterer(filt):
            # select 20th centrury emotional words
            if (filt[1]<=2000)&(filt[1]>=1900)&(filt[0] in emotionDic[emotion]):
                return filt

        counts = []
        counter = 1

        os.chdir(os.getcwd() + '/' + lang)

        for csvFile in glob.glob('*.csv'):
            with open(csvFile, 'rb') as csvfile:
                reader = csv.DictReader(csvfile, fieldnames=['word', 'year', 'counts', 'page', 'volume'],
                                        delimiter='\t', quoting=csv.QUOTE_NONE)
                output = map(mapper2, filter(filterer,map(mapper, reader)))

            counts = counts+output

            print "Emotion:" + emotion + " -- Processed " + str(counter) + "/" + str(len(glob.glob('*.csv'))) + " files"
            counter+=1

        dictionary = dict()
        for (year, val) in counts: 
            dictionary[year] = dictionary.get(year, 0) + val  # return the value for that key or return default 0 (and create key)

        data_aggregated = [(key, val) for (key, val) in dictionary.iteritems()]


        with open('pickledEmotions/'+ lang + '/' + emotion + '_'+ str.upper(lang) +'.pkl', 'w') as f:  
            pickle.dump([data_aggregated], f)

        aggrEmotDic[emotion] = data_aggregated

        os.chdir('..')
        



