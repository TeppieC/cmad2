import yake

import os
import numpy as np
from scipy.io import wavfile
import pandas as pd
import seaborn as sns
from bs4 import BeautifulSoup
import pickle
from pprint import pprint
from nltk.stem.porter import PorterStemmer
from datetime import datetime
import nltk
import collections
import math
import spacy
import string

class Proc1(object):
    """docstring for Proc1"""
    def __init__(self, rq, infolder):
        self.infolder = infolder
        # self.outfolder = outfolder
        self.filename, self.sessionId, self.stopwords, self.numOfKeywords, self.interval, self.no_bins = self.get_request(rq)
        
    
    def get_request(self, rq):
        rq_dict = rq

        sessionId = rq_dict['sessionId']

        filename = rq_dict['filename']
        stopwords = rq_dict['stopwords']
        numOfKeywords = rq_dict['numOfKeywords']
        interval = rq_dict['interval']
        no_bins = rq_dict['no_bins']
        # max_ngram_size = 3

        print('****** [Proc1] received post data', rq_dict)

        return filename, sessionId, stopwords, numOfKeywords, interval, no_bins

    def parse_annos(self, infolder, filename):
        with open(infolder+filename+'_annos.pickle','rb') as f: # TO CHANGE: absolute path when in production
            anno = pickle.load(f)  

        t_segs = []
        s_segs = []
        o_segs = []
        for i, segs in enumerate([anno['preds'], anno['adjustedAnnos']]):
            if i==0:
                for k,v in segs.items():
                    if v['Pred']=='T':
                        t_segs.append(float(v['File']))
                    elif v['Pred']=='S':
                        s_segs.append(float(v['File']))
                    else:
                        o_segs.append(float(v['File']))
            else:
                
                for k,v in segs.items():
                    if v=='S':
                        s_segs.append(float(k))
                    elif v=='T':
                        t_segs.append(float(k))
                    elif v=='O':
                        o_segs.append(float(k))

        # print(t_segs)
        with open(infolder+filename+'_subs.txt','r') as f: # convert from subs file (TODO:everytime we should keep a copy of this file) # TO CHANGE: absolute path when in production
            subs = f.readlines()
        
        subs_dict = {}
        for sub in subs[1:]: # TO CHANGE to include first line if necessary
            tp,txt = sub.strip().split('\t')
            tp_hr = float(datetime.strptime(tp,'%H:%M:%S').hour)    
            tp_min = float(datetime.strptime(tp,'%H:%M:%S').minute)    
            tp_sec = float(datetime.strptime(tp,'%H:%M:%S').second)   
            tp_s = tp_hr*3600+tp_min*60+tp_sec 
            # print(tp_s, txt)
            subs_dict[tp_s] = txt
        # print(subs_dict)

        dtas = []
        for tp, txt in subs_dict.items():
            if tp in t_segs:
                dtas.append([tp,'T', txt])
            elif tp in s_segs:
                dtas.append([tp, 'S', txt])
            elif tp in o_segs:
                dtas.append([tp, 'O', txt])

        df = pd.DataFrame(dtas, columns=['Start','Who','Text']).sort_values('Start').reset_index(drop=True)
        df['End'] = df['Start'].shift(-1)
        df['Start'] = df['Start']+0.001 # TODO: address the last row

        return df


    def crop_on_interval(self, annos, no_bins, interval):
        count = 0
        bins = list(range(0, no_bins*interval, interval))
        annos['bin'] = pd.cut(annos['End'], bins)
        # bins = list(df.bin.unique())
        dfs = dict(tuple(annos.groupby('bin')))

        return dfs


    def extract(self, dfs, num_keywords, stopwords):
        keywords = {'S':{},'T':{}}

        max_ngram_size = 3
        deduplication_thresold = 0.9
        deduplication_algo = 'seqm'
        window_size = 1
        num_periods = 0

        for interval, df in dfs.items():
            # print(interval)
            if len(df):
                stu_texts = '. '.join(df.loc[df['Who']=='S','Text'].values.tolist())
                tea_texts = '. '.join(df.loc[df['Who']=='T','Text'].values.tolist())
                ids = dfs[interval].index.values.tolist() # find all posts of this week
                kw_extractor = yake.KeywordExtractor(lan="en", n=max_ngram_size, \
                                                     dedupLim=deduplication_thresold, \
                                                     dedupFunc=deduplication_algo, \
                                                     windowsSize=window_size, \
                                                     top=num_keywords, \
                                                     features=None,\
                                                     stopwords=stopwords)
                stu_keywords = kw_extractor.extract_keywords(stu_texts)
                
                kw_extractor = yake.KeywordExtractor(lan="en", n=max_ngram_size, \
                                                     dedupLim=deduplication_thresold, \
                                                     dedupFunc=deduplication_algo, \
                                                     windowsSize=window_size, \
                                                     top=num_keywords, \
                                                     features=None,\
                                                     stopwords=stopwords)
                tea_keywords = kw_extractor.extract_keywords(tea_texts)
                # print(stu_keywords)
                # print(tea_keywords)

                # keywords['S'][(interval.left,interval.right)] = stu_keywords # not used
                # keywords['T'][(interval.left,interval.right)] = tea_keywords # not used     
                # keywords['S'][float(interval.left)] = stu_keywords
                # keywords['T'][float(interval.left)] = tea_keywords
                keywords['S'][float(interval.left)] = [[k for k,v in stu_keywords][::-1], [v.round(3) for k,v in stu_keywords][::-1]]
                keywords['T'][float(interval.left)] = [[k for k,v in tea_keywords][::-1], [v.round(3) for k,v in tea_keywords][::-1]]

                num_periods +=1
        keywords['config'] = {'num_keywords':num_keywords, 'num_periods':num_periods}


        return keywords
        # with open(self.filename+'/'+str(interval)+'_proc1'+'.txt','w') as f: # TO CHANGE: absolute path when in production, use JSON to output
        #     f.write('Time interval %s\n'%interval)
        #     f.write('In total %d posts\n'%len(ids))
        #     f.write('=====================\n')
        #     f.write('Student keywords: \n')
        #     f.write('---------------------\n')
        #     for kw in stu_keywords:
        #         f.write('%s: %.3f\n'%(kw[0],kw[1]))
        #     f.write('---------------------\n')
        #     f.write('Teacher keywords: \n')
        #     f.write('---------------------\n')
        #     for kw in tea_keywords:
        #         f.write('%s: %.3f\n'%(kw[0],kw[1]))

    def main(self):
        self.annos = self.parse_annos(self.infolder, self.filename)
        binned_df = self.crop_on_interval(self.annos, self.no_bins, self.interval)
        # print(binned_df.keys())
        return self.extract(binned_df, self.numOfKeywords, self.stopwords)


if __name__ == '__main__':
    ENGLISH_STOP_WORDS = frozenset([
        "thank", "use","need", 'll', # this is 'll
        "does","doesn","one","say","try","didn","said", 'bit', 'inaudible',
        "thanks", "use","need", "don","wouldn","won","able","just",
        "a", "about", "above", "across", "after", "afterwards", "again", "against",
        "all", "almost", "alone", "along", "already", "also", "although", "always",
        "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are", 
        "use","look","a", "about", "above", "across", "after", "afterwards", "again", "against",
        "all", "almost", "alone", "along", "already", "also", "although", "always",
        "am", "among", "amongst", "amoungst", "amount", "an", "another",
        "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
        "around", "as", "at", "back", "be", "became", "because", "become",
        "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
        "below", "beside", "besides", "between", "beyond", "both",
        "but", "by", "call", "can", "cannot", "cant", "co", "con",
        "could", "couldnt", "cry", "de", "do", "done", "don't","didn't","don","did",
        "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
        "elsewhere", "enough", "etc", "ever", "every", "everyone",
        "everything", "everywhere", "except", "few", "fill",
        "find", "for", "former", "formerly", "forty","just",
        "found", "from", "front", "get", "give", "go",
        "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
        "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
        "how", "however", "i", "ie", "if", "in", "inc", "indeed",
        "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
        "latterly", "least", "less", "ltd", "made", "many", "may", "me",
        "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
        "move", "much", "must", "my", "myself", "name", "namely", "neither",
        "never", "nevertheless", "next", "no", "nobody", "none", "noone",
        "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on","ok","okay",
        "once", "only", "onto", "other", "others", "otherwise", "our", 'or','and',
        "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
        "please", "put", "rather", "re", "same", "see", "seem", "seemed",
        "seeming", "seems", "serious", "several", "she", "should",
        "since", "sincere", "so", "some", "somehow", "someone",
        "something", "sometime", "sometimes", "somewhere", "still", "such",
        "take", "than", "that", "the", "their", "them", "first","second",
        "themselves", "then", "thence", "there", "thereafter", "thereby",
        "therefore", "therein", "thereupon", "these", "they", 
        "third", "this", "those", "though", "through", "throughout",
        "thru", "thus", "to", "together", "too", "top", "toward", "towards",
        "un", "under", "until", "up", "upon", "us", "um","uh","eh",
        "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
        "whence", "whenever", "where", "whereafter", "whereas", "whereby",
        "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
        "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
        "within", "without", "would", "yet", "you", "your", "yours", "yourself",
        "yourselves","yes","yeah",'ya',"yep"])
    ENGLISH_STOP_WORDS = list(ENGLISH_STOP_WORDS)
    ENGLISH_STOP_WORDS = ENGLISH_STOP_WORDS+list(string.ascii_lowercase)
    stoplist = ENGLISH_STOP_WORDS+list('1234567890')
    sessionId = 1111
    numOfKeywords = 20
    interval = 300
    no_bins = 30
    filename = 'JP4'

    rq_dict = {'filename':filename, 'sessionId':sessionId, 'stopwords':stoplist, 'numOfKeywords':numOfKeywords, 'interval':interval, 'no_bins':no_bins}

    infolder = '/Users/zhaorui/work/cmad/processed_data/annotations/'
    proc1 = Proc1(rq_dict, infolder)
    
    res = proc1.main()
    print(res)

