import os
import numpy as np
from scipy.io import wavfile
import pandas as pd

from bs4 import BeautifulSoup
import pickle
from pprint import pprint
from nltk.stem.porter import PorterStemmer
from datetime import datetime
import nltk
import collections
import math
import spacy
import requests
import string
import json


class Proc3(object):
    """docstring for Proc1"""
    def __init__(self, rq, infolder, vocab):
        self.infolder = infolder
        self.rq = rq
        self.vocab = vocab
    
    def get_request(self, rq):
        rq_dict = rq

        sessionId = rq_dict['sessionId']

        filename = rq_dict['filename']
        num_keywords = rq_dict['numkeyword']
        interval = rq_dict['interval']

        # pos_tags = rq_dict['allowedPos']
        pos_tags = ['NOUN','VERB']
        # max_ngram_size = 3

        print('****** [Proc3] received post data', rq_dict)

        return filename, sessionId, num_keywords, interval, pos_tags

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
        last_tp = 0.0
        for sub in subs[1:]: # TO CHANGE to include first line if necessary
            tp,txt = sub.strip().split('\t')
            tp_hr = float(datetime.strptime(tp,'%H:%M:%S').hour)    
            tp_min = float(datetime.strptime(tp,'%H:%M:%S').minute)    
            tp_sec = float(datetime.strptime(tp,'%H:%M:%S').second)   
            tp_s = tp_hr*3600+tp_min*60+tp_sec 
            # print(tp_s, txt)
            subs_dict[tp_s] = txt
            last_tp = tp_s

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

        return df, last_tp


    def crop_on_interval(self, annos, last_tp, interval):
        no_bins = int(last_tp // interval + 1)
        # print(range(0, 30*interval, interval))
        # print(no_bins)
        bins = list(range(0, no_bins*interval, interval))
        annos['bin'] = pd.cut(annos['End'], bins)
        # bins = list(df.bin.unique())
        dfs = dict(tuple(annos.groupby('bin')))

        return dfs
                
    
    def extract_keywords_from_list(self, doc, wordlist, allowed_pos):
        kws = {}
        
        lemma_text = {} # where we keep the original word
        for token in doc:
            if token.pos_ in allowed_pos:
                if token.lemma_ in lemma_text:
                    lemma_text[token.lemma_].append(token.text)
                else:
                    lemma_text[token.lemma_] = [token.text]
                    
        lemmas = [token.lemma_ for token in doc if token.pos_ in allowed_pos]
        for word in wordlist: # wordlist contain all tier 2 and tier 3 words, can have multiple forms (plural etc)
            ct = lemmas.count(word) 
            if ct: #if this tier word is spotted in text
                kws[word] = {'count':ct, 'text':lemma_text[word]}

        return kws # extracted kws are in the form of lemmas
                
    def tf(self, tokens):
        tfdict = {}
        for t in tokens.keys():
            if t not in tfdict:
                tfdict[t] = tokens[t]['count']
        return tfdict # term frequency of a token

    def idf(self, all_tokens):
        num_intervals = len(all_tokens)
        print("Number of intervals/documents",num_intervals)
        bow = set()
        for tokens in all_tokens.values():
            for word in tokens.keys():
                bow.add(word) # the set of all extracted entities
                
        idfdict = {}
        token_lookup = {t:[] for t in bow} # the lookup dictionary to find where the entity was
        for tk in bow:
            interval = 0
            for tokens in all_tokens.values():
                if tk in tokens.keys():
                    token_lookup[tk].append(interval)
                interval+=1
            idfdict[tk] = math.log10(num_intervals/float(len(token_lookup[tk])))
            
        return (idfdict, token_lookup)

    def extract(self, dfs, num_keywords, pos_allowed):
        with open(self.vocab,'rb') as f:
            tier_vocab = pickle.load(f)
        # Entity linking and parsing
        nlp = spacy.load("en_core_web_sm")

        all_entities = {}
        num_periods = 0
        for interval in sorted(dfs.keys()):
            df = dfs[interval]
            if len(df):
                stu_texts = '. '.join(df.loc[df['Who']!='T','Text'].values.tolist())
                doc = nlp(stu_texts)
                stu_kws_w = self.extract_keywords_from_list(doc, tier_vocab, pos_allowed)
                tea_texts = '. '.join(df.loc[df['Who']=='T','Text'].values.tolist())
                doc = nlp(tea_texts)
                tea_kws_w = self.extract_keywords_from_list(doc, tier_vocab, pos_allowed)
                
                all_entities[(interval, 'T')] = tea_kws_w
                all_entities[(interval, 'S')] = stu_kws_w
                num_periods +=1

        # For raw count
        # occurences = {'S':{},'T':{}}
        
        # for interval, kws in all_entities.items():
        #     sp = interval[1]
        #     time = (interval[0].left, interval[0].right)
        #     extracted = []
        #     for kw, kw_info in kws.items():
        #         row = []
        #         row.append(kw)
        #         row.append(kw_info['count'])
        #         extracted.append(row)
        #     df = pd.DataFrame(extracted, columns=['word','count'])
        #     order = list(df.sort_values(by=['count'],axis=0,ascending=False)['word'].values)
        #     figsize=(15,8)
        #     fig, ax = plt.subplots(figsize=figsize)
        #     plot = sns.barplot(ax=ax, data=df, y='word',x='count',
        #                 orient='h',order=order, color='red')
        #     plot.set_title('Raw counts from %ds to %ds, %s'%(time[0],
        #                                                      time[1],
        #                                                      sp))
        #     ax.figure.savefig("results/"+course+"/Tier_rc_%d_%d_%s.png"%(time[0],time[1],sp))

        # For TF-IDF
        # calculate the tf-idf score for each extracted entity
        outputs = {}
        idfdict, ent_interval_lookup = self.idf(all_entities)
        tfdicts = {}
        for interval, tokens in all_entities.items():
            scores = {}
            tfdict = self.tf(tokens)
            for word, tf_val in tfdict.items():
                scores[word] = tf_val*idfdict[word]
            tfdicts[interval] = tfdict
            outputs[interval] = scores


        keywords = {'S':{},'T':{}}
        for interval, kws in outputs.items():
            extracted = [(txt, score) for txt, score in kws.items()]
            # rank and truncate
            extracted_truncated = sorted(extracted, key=lambda e: e[1])[::-1][:num_keywords]
            kw_txts = [kw[0] for kw in extracted_truncated]
            kw_scores = [kw[1] for kw in extracted_truncated]
            if interval[1]=='S':
                keywords['S'][float(interval[0].left)] = [kw_txts, kw_scores]
            elif interval[1]=='T':
                keywords['T'][float(interval[0].left)] = [kw_txts, kw_scores]

        keywords['config'] = {'num_keywords':num_keywords, 'num_periods':num_periods}

        return keywords



    def main(self):
        self.filename, self.sessionId, self.num_keywords, self.interval, self.pos_tags = self.get_request(self.rq)
        self.annos, last_tp = self.parse_annos(self.infolder, self.filename)
        binned_df = self.crop_on_interval(self.annos, last_tp, self.interval)
        # print(binned_df.keys())
        return self.extract(binned_df, self.num_keywords, self.pos_tags)


if __name__ == '__main__':
    pass

