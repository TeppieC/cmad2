import os
import yaml
import shutil
import sidekit
import numpy as np
from tqdm import tqdm
from utils import safe_makedir, parse_yaml
import logging
from flask import current_app
import subprocess
import h5py


class Initializer():
    """
    To build speaker verification model, one needs speech data from each speaker
    that is to be known by the system. The set of known speakers are in speaker
    recognition known as the (enrollment speakers), and a speaker is enrolled
    into the system when enrollment data from the speaker is processed to build
    its model.
    After the enrollment process, the performance of the speaker verification
    system can be evaluated using test data, which in an open set scenario, will
    consist of data from speakers in and outside the enrollment set.
    The set of all speakers involved in testing the system will be referred to
    as the test speakers.

    This class if for preprocessing and structure the preprocessed data
    into h5 files that will be used later for training and evaluating our models
    NOTE:All outputs of this script can be found in the directory self.task_dir
    """

    def __init__(self, conf_path, annos):
        """
        This method parses the YAML configuration file which can be used for
        initializing the member varaibles!!
        Args:
            conf_path (String): path of the YAML configuration file
        """
        
        #location of output files
        self.conf = parse_yaml(conf_path)
        self.annos = annos
        self.task_dir = os.path.join(self.conf['outpath'], "task")
        #location of audio files
        self.audio_dir = os.path.join(self.conf['outpath'], "audio")
        #location of all the audio data
        self.data_dir = os.path.join(self.audio_dir, "data")
        # location of training data
        self.train_dir = os.path.join(self.audio_dir, "train")
        #location of just the enrollment audio data
        self.enroll_dir = os.path.join(self.audio_dir, "enroll")
        #location of just the test audio data
        self.test_dir = os.path.join(self.audio_dir, "test")
        self.speakers = self.conf['speakers']
    
    def convert_wav(self, inpath, outpath, no_channels, sampling_rate, bit_precision,
                showWarning=False):
        """
        Convert the waves to a pre-defined sampling rate, number of channels and
        bit-precision using SoX tool. So, it should be installed!!
        """
        parent, _ = os.path.split(outpath)
        if not os.path.exists(parent):
            os.makedirs(parent)

        command = "sox {} -r {} -c {} -b {} {}".format( inpath,
                                                        sampling_rate,
                                                        no_channels,
                                                        bit_precision,
                                                        outpath) # TO CHANGE into /usr/bin/sox

        current_app.logger.debug('CMD'+str(command))
        # if showWarning:
        #     subprocess.call(command, shell=True) 
        # else:
        # subprocess.call(command.split(), shell=True, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)
        #subprocess.call(command, shell=True, stdout=subprocess.STDOUT, stderr=subprocess.STDOUT)
        # p = os.popen(command)
        # current_app.logger.debug(p.read())
        os.system(command)

    def preprocess_audio(self):        
        #remove the data directory if exists
        # if os.path.exists(self.data_dir):
        #     current_app.logger.debug(self.data_dir)
        #     current_app.logger.debug('data eixjoitajkdfhsjdvbnxc,.zn;vika;w;ofbu;nw')
        #     shutil.rmtree(self.data_dir)

        # Process enrol and test wavs
        inpath = self.conf['inpath']
        wav_filenames = os.listdir(inpath)
        for wav in wav_filenames:
            current_app.logger.debug('Processing file'+str(wav))
            inwav = os.path.join(inpath, wav)
            outwav = os.path.join(self.data_dir, wav) 
            current_app.logger.debug('inpath'+str(inwav))
            current_app.logger.debug('outpath'+str(outwav))
            self.convert_wav(inwav, outwav,
                        no_channels = self.conf['no_channels'],
                        sampling_rate = self.conf['sampling_rate'],
                        bit_precision = self.conf['bit_precision'])

            current_app.logger.debug('Done')

        #remove the train directory if exists
        if os.path.exists(self.train_dir):
            shutil.rmtree(self.train_dir)        
        #remove the enroll directory if exists
        if os.path.exists(self.enroll_dir):
            shutil.rmtree(self.enroll_dir)
        #remove the test directory if exists
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        if not os.path.exists(self.train_dir):
            os.makedirs(self.train_dir)
        #create audio/enroll directory
        if not os.path.exists(self.enroll_dir):
            os.makedirs(self.enroll_dir)
        #create audio/test directory
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        #parse num of sessions from configuration
        n_train_sessions = self.conf['n_train_sessions']
        n_test_sessions = self.conf['n_test_sessions']
        if n_train_sessions<0:
            current_app.logger.debug('************** [Data Init] Train using all sessions (unlabeled)')
        if n_test_sessions<0:
            current_app.logger.debug('************** [Data Init] Test all remaining sessions')

        #iterate over all preprocessed waves
        n_unlbl_samples = 0
        wav_filenames = os.listdir(self.data_dir)
        current_app.logger.debug('****** [Data Init] wav files available'+str(wav_filenames))
        current_app.logger.debug('****** [Data Init] already-labeled annotations'+str(self.annos))
        for wav in tqdm(sorted(wav_filenames), desc="Copying enroll/test waves"): # loop over all files TQDM can be removed
            inwav = os.path.join(self.data_dir, wav)
            tm = wav[:-4] 
            if tm in self.annos:
                current_app.logger.debug('************** [Data Init] parsing training timepoint: '+str(tm))
                lbl = self.annos[tm]
                if lbl in ['S','T']:
                    current_app.logger.debug('************** [Data Init] logging enroll file '+str(tm))
                    outwav = os.path.join(self.enroll_dir, lbl+'-'+wav) # move annotated samples (only S and T classes) to enroll folder
                    shutil.copyfile(inwav, outwav)
            else:
                if n_train_sessions < 0 or n_unlbl_samples < n_train_sessions: # move designated number of train samples to train folder
                    outwav = os.path.join(self.train_dir, wav) 
                    shutil.copyfile(inwav, outwav)
                if n_test_sessions < 0 or n_unlbl_samples < n_test_sessions: # move designated number of train samples to test folder
                    outwav = os.path.join(self.test_dir, wav) 
                    shutil.copyfile(inwav, outwav)

                n_unlbl_samples+=1
 
    def create_idMap(self, group):
        """
        IdMap are used to store two lists of strings and to map between them.
        Most of the time, IdMap are used to associate segments names (sessions)
        stored in leftids; with the ID of their class (that could be the speaker
        ID) stored in rightids.
        Additionally, and in order to allow more flexibility, IdMap includes two
        other vectors: 'start'and 'stop' which are float vectors used to store
        boudaries of audio segments.
        Args:
            group (string): name of the group that we want to create idmap for
        NOTE: Duplicated entries are allowed in each list.
        """
        # Make enrollment (IdMap) file list
        group_dir = os.path.join(self.audio_dir, group)
        group_files = sorted(os.listdir(group_dir))
        # print('group_dir',group_dir)
        # print('group_files',group_files)

        # list of model IDs
        group_models = [files.split('-')[0] for files in group_files]
        # print('group_models',group_models)
        '''
        'S01', 'S01', 'S01', 'S01', 'S01', 'S01',  6个label
        '''

        # list of audio segments IDs
        group_segments = [group+"/"+f for f in group_files]
        # print('group_segments',group_segments)
        '''
        'enroll/S01.01.digits.wav', 'enroll/S01.01.words.wav', 'enroll/S01.02.digits.wav', 
        'enroll/S01.02.words.wav', 'enroll/S01.03.digits.wav', 'enroll/S01.03.words.wav',
        '''


        # print('task dir', self.task_dir)

        # Generate IdMap
        group_idmap = sidekit.IdMap()
        group_idmap.leftids = np.asarray(group_models)
        group_idmap.rightids = np.asarray(group_segments)
        group_idmap.start = np.empty(group_idmap.rightids.shape, '|O')
        group_idmap.stop = np.empty(group_idmap.rightids.shape, '|O')
        if group_idmap.validate():
            group_idmap.write(os.path.join(self.task_dir, group+'_idmap.h5'))
            #generate tv_idmap and plda_idmap as well
            if group == "enroll":
                group_idmap.write(os.path.join(self.task_dir, 'tv_idmap.h5'))
                group_idmap.write(os.path.join(self.task_dir, 'plda_idmap.h5'))
        else:
            raise RuntimeError('Problems with creating idMap file')


    def create_test_trials(self):
        """
        Ndx objects store trials index information, i.e., combination of 
        model and segment IDs that should be evaluated by the system which 
        will produce a score for those trials.

        The trialmask is a m-by-n matrix of boolean where m is the number of
        unique models 讲话人 and n is the number of unique segments 语音片段. If trialmask(i,j)
        is true 就是target/nontarget then the score between model i and segment j will be computed.
        """
        # Make list of test segments
        test_data_dir = os.path.join(self.audio_dir, "test") #test data directory
        test_files = sorted(os.listdir(test_data_dir))
        test_files = ["test/"+f for f in test_files]
        # print('test_data_dir',test_data_dir)
        # print('test_files',test_files)

        # Make lists for trial definition, and write to file
        test_models = []
        test_segments = []
        test_labels = []
        # Get enroll speakers
        enrolled_speakers = ['S','T']
        enrolled_speakers = sorted(enrolled_speakers)
        current_app.logger.debug('************** [Data Init] enrolled_speakers'+str(enrolled_speakers))

        for model in tqdm(enrolled_speakers, desc="Creating Test Cases"):
            for segment in sorted(test_files):
                test_model = 'NA'
                test_models.append(model)
                test_segments.append(segment)
                # Compare gender and speaker ID for each test file
                if test_model == model:
                    test_labels.append('target')
                else:
                    test_labels.append('nontarget')
            
        with open(os.path.join(self.task_dir, "test_trials.txt"), "w") as fh:
            for i in range(len(test_models)):
                fh.write(test_models[i]+' '+test_segments[i]+' '+test_labels[i]+'\n')


    def create_Ndx(self):
        """
        Key are used to store information about which trial is a target trial
        and which one is a non-target (or impostor) trial. tar(i,j) is true
        if the test between model i and segment j is target. non(i,j) is true
        if the test between model i and segment j is non-target.
        """
        #Define Key and Ndx from text file
        #SEE: https://projets-lium.univ-lemans.fr/sidekit/_modules/sidekit/bosaris/key.html
        key = sidekit.Key.read_txt(os.path.join(self.task_dir, "test_trials.txt"))
        ndx = key.to_ndx()
        if ndx.validate():
            ndx.write(os.path.join(self.task_dir, 'test_ndx.h5'))
        else:
            raise RuntimeError('Problems with creating idMap file')


    def structure(self):
        """
        This is the main method for this class, it calls all previous
        methods... that's basically what it does :)
        """
        self.preprocess_audio()
        self.create_idMap("enroll")
        self.create_idMap("test")
        self.create_test_trials()
        self.create_Ndx()




if __name__ == "__main__":
    conf_filename = "conf2.yaml"
    init = Initializer(conf_filename)
    init.structure()