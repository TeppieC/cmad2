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


class Proc2(object):
    """
        Procedure 2: Knowledge base keyword extractor using babelfy
    """
    def __init__(self, rq, infolder, api_key):
        self.infolder = infolder
        self.rq = rq
        self.api_key = api_key
    
    def get_request(self, rq):
        rq_dict = rq

        sessionId = rq_dict['sessionId']

        filename = rq_dict['filename']
        stopwords = rq_dict['stopwords']
        num_keywords = rq_dict['numkeyword']
        interval = rq_dict['interval']

        pos_tags = ['v', 'n']
        # max_ngram_size = 3

        print('****** [Proc2] received post data', rq_dict)

        return filename, sessionId, stopwords, num_keywords, interval, pos_tags

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

    def extract_entities_paragraph(self, paragraph, ann_type='ALL', ann_res='BN'):
        url = "https://babelfy.io/v1/disambiguate?text=%s&lang=%s&key=%s&annType=%s&annRes=%s"%(paragraph,'EN', self.api_key, ann_type, ann_res)
        #params = {'text':text, 'lang':'en', 'key':key}
        res = requests.get(url)
        extracted_ents = {}
        for ent in json.loads(res.text):
            ent_loc = (ent['charFragment']['start'], ent['charFragment']['end']+1)
            ent_txt = paragraph[ent['charFragment']['start']:ent['charFragment']['end']+1]
            ent_id = ent['babelSynsetID']
            ent_score = ent['score']
            ent_coh_score = ent['coherenceScore']
            ent_glb_score = ent['globalScore']
            print(ent_id, ent_txt, ent_loc,ent_score,ent_coh_score,ent_glb_score)
            if ent_id in extracted_ents:
                extracted_ents[ent_id]['count'] += 1 
                extracted_ents[ent_id]['text'].append(ent_txt) 
                extracted_ents[ent_id]['pos'].append(ent_loc)  
                extracted_ents[ent_id]['score'].append(ent_score) 
                extracted_ents[ent_id]['coh_score'].append(ent_coh_score) 
                extracted_ents[ent_id]['glob_score'].append(ent_glb_score) 
            else:
                extracted_ents[ent_id] = {'count':1, 'text':[ent_txt], 
                                          'pos':[ent_loc],'type':'ent', 
                                          'coh_score':[ent_coh_score], 
                                          'score':[ent_score],
                                          'glob_score':[ent_glb_score]}
        return json.loads(res.text), extracted_ents

    def extract_keywords_from_list(self, text, wordlist):
        kws = {}
        for word in wordlist:
            ct = text.count(word) 
            if ct:
                if word in kws:
                    kws[word]['count'] += ct
                else:
                    kws[word] = {'count':ct, 'type':'tier','text':[word]}

        return kws

    def extract(self, dfs, num_keywords, pos_allowed, stopwords):
        # Entity linking and parsing
        raws = {}
        all_entities = {}
        num_periods = 0
        for interval in sorted(dfs.keys()):
            df = dfs[interval]
            if len(df):
                stu_texts = '. '.join(df.loc[df['Who']!='T','text'].values.tolist())
                tea_texts = '. '.join(df.loc[df['Who']=='T','text'].values.tolist())
                stu_raw, stu_kws = self.extract_entities_paragraph(stu_texts,ann_res='BN')
                tea_raw, tea_kws = self.extract_entities_paragraph(tea_texts,ann_res='BN')
                
                all_entities[(interval, 'T')] = tea_kws
                all_entities[(interval, 'S')] = stu_kws
                raws[(interval, 'T')] = tea_raw
                raws[(interval, 'S')] = stu_raw 
                num_periods +=1

        # POS tag inference
        lm = WordNetLemmatizer()
        ent_text_lookup_nonstem = {}
        for k, value in all_entities.items():
            for bid, kw in value.items():
                kw_cpy = kw.copy()
                if bid not in ent_text_lookup_nonstem:
                    ent_text_lookup_nonstem[bid] = kw_cpy['text']
                else:
                    ent_text_lookup_nonstem[bid] = ent_text_lookup_nonstem[bid]  + kw_cpy['text']

        ent_text_lookup = {}
        for k,v in ent_text_lookup_nonstem.items():
            ent_text_lookup[k] = set()
            for word in v:
                ent_text_lookup[k].add(lm.lemmatize(word.lower()))# remove duplicates
                # remove duplicated same-stemming words
            ent_text_lookup_nonstem[k] = list(set(v))


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

        # rank and display
        # extracted_words = {} # output without stop words
        keywords = {'S':{},'T':{}}
        occurences = {'S':{},'T':{}}
        for k,v in outputs.items():

            print('Interval:',k[0])
            print('Category:',k[1])

            s_kw_count = 0
            t_kw_count = 0
            
            for score in sorted(v.items(), reverse=True, key=lambda item: item[1]): # sorted
                if score[0][-1] in pos_allowed:
                    texts = ent_text_lookup[score[0]]
                    stop = False # to remove from the stop word list
                    for text in texts:
                        if text in stopwords:
                            stop = True
                            break
                    if not stop:        
                        kw_txt = ent_text_lookup[score[0]]
                        kw_score = score[1]

                        # try:
                        #     # print(all_entities[k][score[0]]['score'])
                        #     # print(all_entities[k][score[0]]['coh_score'])
                        #     # print(all_entities[k][score[0]]['glob_score'])
                        #     # extracted_words[score[0]] = score[1]
                        #     # output_row.append(score[0]) #bn_id
                        #     kw_txt = ent_text_lookup[score[0]]
                        #     kw_score = score[1]
                        #     # output_row.append([round(n, 3) for n in all_entities[k][score[0]]['score']])
                        #     # output_row.append([round(n, 3) for n in all_entities[k][score[0]]['coh_score']])
                        #     # output_row.append([round(n, 3) for n in all_entities[k][score[0]]['glob_score']])
                        # except KeyError:


                        if k[1] == 'S' and s_kw_count < num_keywords:
                            if float(k[0].left) not in keywords['S']:
                                keywords['S'][float(k[0].left)] = [[kw_txt], [kw_score]]
                            else:
                                keywords['S'][float(k[0].left)][0].append(kw_txt)
                                keywords['S'][float(k[0].left)][1].append(kw_score)
                            s_kw_count +=1
                        elif k[1] == 'T' and t_kw_count < num_keywords:                            
                            if float(k[0].left) not in keywords['S']:
                                keywords['S'][float(k[0].left)] = [[kw_txt], [kw_score]]
                            else:
                                keywords['S'][float(k[0].left)][0].append(kw_txt)
                                keywords['S'][float(k[0].left)][1].append(kw_score)
                            t_kw_count +=1

        keywords['config'] = {'num_keywords':num_keywords, 'num_periods':num_periods}
        return keywords



    def main(self):
        self.filename, self.sessionId, self.stopwords, self.num_keywords, self.interval, self.pos_tags = self.get_request(self.rq)
        self.annos, last_tp = self.parse_annos(self.infolder, self.filename)
        binned_df = self.crop_on_interval(self.annos, last_tp, self.interval)
        # print(binned_df.keys())
        return self.extract(binned_df, self.num_keywords, self.pos_tags, self.stopwords)


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
    num_keywords = 20
    interval = 300
    no_bins = 30
    filename = 'JP4'

    rq_dict = {'filename':filename, 'sessionId':sessionId, 'stopwords':stoplist, 'num_keywords':num_keywords, 'interval':interval, 'no_bins':no_bins}

    proc2 = Proc2(rq_dict, os.environ['INFOLDER'], os.environ['BABELFY_API_KEY'])
    
    res = proc2.main()
    print(res)

