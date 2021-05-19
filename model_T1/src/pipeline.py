import os
import yaml
import shutil
import sidekit
import numpy as np
import pandas as pd
from tqdm import tqdm
from data_init import Initializer
from model_interface import SidekitModel
from data_init import Initializer
from extract_features import FeaturesExtractor
from ubm import UBM
import shutil
import pandas as pd
import json
import logging
from flask import current_app

class Pipeline:
    def __init__(self, rq, infolder, outfolder):
        self.infolder = infolder
        self.outfolder = outfolder
        params = self.get_request(rq)
        if params[1]=='first-time':
            self.filename, self.typ, self.annos, self.sessionId = params
        else:
            self.filename, self.typ, self.annos_preds, self.sessionId, self.prevAnnos, prevPreds, self.adjustedPreds = params
            print('****** [Pipeline]  1st-time annotations+predictions',self.annos_preds) #'2'
            print('****** [Pipeline]  timepoints to be adjusted',self.adjustedPreds) #'103.000'
            print('****** [Pipeline]  1st-time annos', self.prevAnnos)
            self.prevPreds = {}
            for i, pred in prevPreds.get('preds').items():
                self.prevPreds[pred['File']] = pred['Pred'] #'103.000'
            print('****** [Pipeline]  1st-time predictions', self.prevPreds)

            self.annos = self.prevAnnos.copy() # first, we include everything from all available manual annotations
            print('****** [Pipeline] the length of annos_preds: '+str(len(self.annos_preds)))
            print('****** [Pipeline] the length of prevAnnos: '+str(len(self.prevAnnos)))
            print('****** [Pipeline] the length of prevPreds: '+str(len(self.prevPreds)))
            print('annos_preds',self.annos_preds)
            print('prevAnnos',self.prevAnnos)
            print('prevPreds',self.prevPreds)
            for k,v in self.annos_preds.items(): # NOTE: annos_preds is not accurate, it is as is, for disply use only
                if k in self.prevPreds: # if it is not one of the already-annotated utterances
                    if k in self.adjustedPreds: # if it is reviewed this time (that were selected from the slider, or within this 25%)
                        self.annos[k] = v # add newly adjusted annotations 
                        print('****** [Pipeline] LOG to enroll set: Selected prediction at time', k, 'was adjusted from', self.prevPreds[k],'to', v)
                    elif v != self.prevPreds[k]: # or its value has been manually changed from last-time's prediction 
                        self.annos[k] = v # add any predictions that've changed since last time
                        print('****** [Pipeline] CHANGE to enroll set: 1-st time prediction at time', k, 'was adjusted from', self.prevPreds[k],'to', v)

                # CHANGE: MAR 10
                elif v != self.prevAnnos[k]: # if it was one of the already-annotated utterances, but has its value changed
                    self.annos[k] = v # update any previous annotations that've changed 
                    print('****** [Pipeline] 1st-time annotation at time', k, 'was adjusted from', self.annos[k],'to', v)
        
        print('****** [Pipeline] training samples (self.annos)', self.annos)
        # print('*********************** prev preds', self.prevPreds)
        # self.cur_page_annos = self.annos
        # true_annos = {}
        # for k,v in self.annos.items():
        #     print('*********************',k,v)
        #     if k in self.prevAnnos:
        #         print('in prev annos')
        #         true_annos[k] = self.annos[k]
        #     if k in self.prevPreds:
        #         if self.prevPreds[k]!=self.annos[k]:
        #             true_annos[k] = self.annos[k]
        #             print("in this times' annos")
        # self.annos = true_annos

        self.data_init(self.config, self.annos)
        print('****** [Pipeline] Data copied.')
        self.extract_features(self.config)
        print('****** [Pipeline] Features extracted.')

    def get_request(self, rq):
        '''
        To create a YAML configuration file
        
        rq: JSON filename from the front-end requesting for verfication task
        '''     
        rq_dict = rq
        # with open('./JP1_rq.json','r') as f:
        #   rq_dict = json.loads(f.read()) # may have to move this line to flask, instead of here

        filename = rq_dict['filename']
        typ = rq_dict['typ']
        annos = rq_dict['annos']
        sessionId = rq_dict['sessionId']
        print('****** [Pipeline] received post data', rq_dict)

        if typ == 'first-time':
            self.create_yaml(sessionId, typ, filename, annos)
        elif typ == 'adjusted':
            # received new annotations
            # added_annos = rq_dict['added_annos']
            # annos.update(added_annos)
            self.create_yaml(sessionId, typ, filename, annos)


        if typ=='adjusted':
            prevAnnos = rq_dict['prevAnnos']
            adjustedPreds = rq_dict['adjustedPreds']   
            prevPreds = rq_dict['prevPreds']   
            return filename, typ, annos, sessionId, prevAnnos, prevPreds, adjustedPreds
        elif typ=='first-time':
            return filename, typ, annos, sessionId

    def create_yaml(self, sessionId, typ, filename, annos):
        n_t_segs = 0 
        n_s_segs = 0
        n_o_segs = 0
        for tm, sp in annos.items():
            if sp=='T':
                n_t_segs+=1
            elif sp=='S':
                n_s_segs+=1
            else:
                n_o_segs+=1
        print('****** [Pipeline] We received %d, %d, %d annotated audios for Teacher, Student, Others'
            %(n_t_segs,n_s_segs,n_o_segs)) # can be removed

        d_yml = {'inpath': self.infolder+filename+'/unsorted',
             'outpath': self.outfolder+'%s_out_%s_%s'%(filename, sessionId, typ),
             'n_test_sessions': -1,
             'n_train_sessions': -1,
             'speakers': ['S', 'T'],
             'sampling_rate': 16000,
             'bit_precision': 16,
             'no_channels': 1,
             'features': ['vad', 'energy', 'cep', 'fb'],
             'cepstral_coefficients': 19,
             'filter_bank': 'log',
             'filter_bank_size': 24,
             'lower_frequency': 300,
             'higher_frequency': 3400,
             'vad': 'snr',
             'snr_ratio': 40,
             'window_size': 0.025,
             'window_shift': 0.01,
             'num_gaussians': 32,
             'batch_size': 30,
             'tv_rank': 25,
             'tv_iterations': 50,
             'scoring': 'cosine',
             'DET_curve': 'rocch'}

        if os.path.exists(d_yml['outpath']):
            shutil.rmtree(d_yml['outpath'])

        self.config = self.outfolder+'%s_%s_%s.yaml'%(filename, sessionId, typ)      
        print("****** [Pipeline] Config file location",self.config)   
        with open(self.config, 'w') as f:
            yaml.dump(d_yml, f)

    
    def data_init(self, config, annos):

        init = Initializer(config, annos)
        init.structure()

    def extract_features(self, config):
        ex = FeaturesExtractor(config)
        ex.extract_features("enroll")
        ex.extract_features("test")
        ex.extract_features("train")
        return ex

    def train(self, retrain):
        if retrain:
            self.ubm = UBM(self.config, retrain=retrain)
            current_app.logger.debug('****** [Pipeline] UBM built')
            self.ubm.train()
            current_app.logger.debug('****** [Pipeline] UBM Training done')

    def enroll(self):
        self.ubm.enroll()

    def predict(self, eval=False, gtp=None):
        fs, scores, classes = self.ubm.evaluate(save=True, explain=True)
        df_res = pd.DataFrame(scores).T
        df_res.columns = classes
        filenames = [name[:-4].split('/')[1] for name in fs]
        tp = pd.DataFrame(filenames)
        df_res['Pred'] = df_res.idxmax(axis=1)
        df_res = pd.concat([tp, df_res], axis = 1)
        df_res.columns = ['File']+list(df_res.columns)[1:]
        df_res['Delta']=(df_res['S']-df_res['T']).abs()
        
        if eval:
            df_res = self.evaluate(df_res, gtp)

        print(df_res)
        self.df_res =df_res

        return df_res

    def evaluate(self, df_res, gtp):
        gtp_dict = None
        with open(gtp,'r') as f:
            gtp_dict = json.loads(f.read())
        gtp = pd.DataFrame.from_dict(gtp_dict,orient='index').reset_index()
        gtp.columns=['File','Truth']
        df_res = pd.merge(df_res, gtp, on=['File'], how='inner')
        df_res['Correct'] = df_res['Pred']==df_res['Truth']

        return df_res

    def post_result(self, df_res):
        output = df_res['Delta'].describe()[['mean','std','max','min','25%','50%','75%']].to_dict()
        output['file'] = self.filename
        output['type'] = self.typ
        output['sessionId'] = self.sessionId
        output['preds'] = df_res.to_dict(orient='index')
        if self.typ=='adjusted':
            output['lastAnnos'] = self.prevAnnos
            output['adjustedAnnos'] = self.annos
            output['lastPreds'] = self.prevPreds
        else:
            output['annos'] = self.annos

        return output