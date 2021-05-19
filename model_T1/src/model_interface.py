import os
import sidekit
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)
from multiprocessing import cpu_count
from utils import parse_yaml



class SidekitModel():
    """This class is just an interface for my models to inherit"""

    def __init__(self, conf_filepath):
        self.conf = parse_yaml(conf_filepath)
        # use 0 to disable multi-processing
        self.NUM_THREADS = cpu_count()
        # The parent directory of the project
        self.BASE_DIR = self.conf['outpath']
    
    def getAccuracy(self, speakers, test_files, scores, threshold=0):
        """
        This method is used to get the accuracy of a model over a bunch of data
        files. The accuracy is returned in percentage. 
        NOTE: The file is considered to be correct if the correct speaker has the
        max score (that's in case the speaker is in the training set). And also
        if the max score is below threshold (that's in case the speaker is not
        in the training set).
        Args
            speakers: list of speakers
            test_files: list of filenames that used to evaluate model
            scores: the score numpy matrix obtained by the model
            threshold: the value above which we will consider the verification
                is done correctly. In other words, if the score>threshold, then
                the answer is considered; otherwise, the answer is not considered
        Returns
            accuracy (float): accuracy of the model in percentage
        """
        assert scores.shape == (len(speakers), len(test_files)),\
            "The dimensions of the input don't match"
        accuracy = 0.
        speakers = [sp for sp in speakers]
        max_indices = np.argmax(scores, axis=0)
        max_scores = np.max(scores, axis=0)
        for idx, test_filename in enumerate(test_files):
            test_filename = test_filename #convert from byte to string
            actual_speaker = test_filename.split("/")[-1].split(".")[0]
            predicted_speaker = speakers[max_indices[idx]]
            #evaluate the test data file
            if max_scores[idx] < threshold:
                if actual_speaker not in speakers:
                    accuracy += 1
            else:
                if predicted_speaker == actual_speaker:
                    accuracy += 1.
        return accuracy*100./len(test_files)
