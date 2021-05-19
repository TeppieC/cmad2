import os
import sidekit
import numpy as np
import warnings
warnings.filterwarnings("ignore")
import logging
# log = logging.getLogger(__name__)
# logging.getLogger().setLevel(logging.WARNING)
import shutil
from model_interface import SidekitModel
from sidekit import Mixture


class UBM(SidekitModel):
    """Universal Background Model"""
    
    def __init__(self, conf_filepath, retrain=True):
        super().__init__(conf_filepath)
        self.retrain = retrain
        # Number of Guassian Distributions
        self.NUM_GAUSSIANS = self.conf['num_gaussians']
        # print("BASE_DIR", self.BASE_DIR)
        self.enrol_audio_dir = os.path.join(self.BASE_DIR, "audio", "enroll")
        self.train_audio_dir = os.path.join(self.BASE_DIR, "audio", "train")
        self.model_loc = os.path.join(self.BASE_DIR, "ubm", "ubm_{}.h5".format(self.NUM_GAUSSIANS))
        self.stat_loc = os.path.join(self.BASE_DIR, "stat", "enroll_stat_{}.h5".format(self.NUM_GAUSSIANS))
        self.enrol_idmap_loc = os.path.join(self.BASE_DIR, "task", "enroll_idmap.h5")
        self.test_ndx_loc = os.path.join(self.BASE_DIR, "task", "test_ndx.h5")
        self.scores_loc = os.path.join(self.BASE_DIR, "result", "ubm_scores_{}.h5".format(self.NUM_GAUSSIANS))
        self.test_trials_loc = os.path.join(self.BASE_DIR, "task", "test_trials.txt")
        
        # Init or Read the UBM model
        self.ubm = sidekit.Mixture()
        if os.path.exists(self.model_loc):
            if self.retrain:
                os.remove(self.model_loc)
            else:
                self.ubm.read(self.model_loc)
                logging.info("Read the model {} at {}".format(self.ubm.name, self.model_loc))

        self.enrol_stat = None
        self.enroll_sv = None
        self.scores = None

    def createFeatureServer(self, group=None):
        """
        This methos is used to crate FeatureServer object which is an object for
        features management. It loads datasets from a HDF5 files ( produced by
        a FeaturesExtractor object)
        Args:
            group (string): the group of features to manage. If None, then it 
            will create a generic FeatureServer over the feat directory.
        Returns:
            server: which is the FeatureServer object
        """
        if group:
            feat_dir = os.path.join(self.BASE_DIR, "feat", group)
        else:
            feat_dir = os.path.join(self.BASE_DIR, "feat")
        # feature_filename_structure: structure of the filename to use to load HDF5 files
        # dataset_list: string of the form ["cep", "fb", vad", energy", "bnf"]
        # feat_norm: type of normalization to apply as post-processing
        # delta: if True, append the first order derivative
        # double_delta: if True, append the second order derivative
        # rasta: if True, perform RASTA filtering
        # keep_all_features: boolean, if True, keep all features; if False,
        #       keep frames according to the vad labels
        server = sidekit.FeaturesServer(
                feature_filename_structure=os.path.join(feat_dir, "{}.h5"),
                dataset_list=self.conf['features'],
                feat_norm="cmvn", #cepstral mean-variance normalization
                delta=True,
                double_delta=True,
                rasta=True,
                keep_all_features=True)
        return server
    
    def train(self, SAVE=True):
        """
        This method is used to train our UBM model by doing the following:
        - Create FeatureServe for the enroll features
        - create use EM algorithm to train our UBM over the enroll features
        - create StatServer to save trained parameters
        - if Save arugment is True (which is by default), then it saves that
          StatServer.
        Args:
            SAVE (boolean): if True, then it will save the StatServer. If False,
               then the StatServer will be discarded.
        """
        #SEE: https://projets-lium.univ-lemans.fr/sidekit/tutorial/ubmTraining.html
        
        train_list = os.listdir(self.train_audio_dir)
        for i in range(len(train_list)):
            train_list[i] = train_list[i].split(".h5")[0]
        train_server = self.createFeatureServer("train") # at /output/feat/train
        print('************** [UBM Training] Training in process ...')

        # print(self.ubm)
        # print(self.ubm.w)
        # print('train server', train_server)
        # print('train list', train_list)
        # print(self.NUM_GAUSSIANS)
        # print(self.NUM_THREADS)
        # print('what wrong')

        # Expectation-Maximization estimation of the Mixture parameters.
        self.ubm.EM_split(features_server=train_server, feature_list=train_list, distrib_nb=self.NUM_GAUSSIANS, num_thread=1, save_partial=False, iterations=(2, 2, 4, 4, 4))
        #     # -> 2 iterations of EM with 2    distributions
        #     # -> 2 iterations of EM with 4    distributions
        #     # -> 4 iterations of EM with 8    distributions
        #     # -> 4 iterations of EM with 16   distributions
        #     # -> 4 iterations of EM with 32   distributions
        #     # -> 4 iterations of EM with 64   distributions
        #     # -> 8 iterations of EM with 128  distributions
        #     # -> 8 iterations of EM with 256  distributions
        #     # -> 8 iterations of EM with 512  distributions
        #     # -> 8 iterations of EM with 1024 distributions 
        # print('Done EM-SPLITING')
        self.ubm.write(self.model_loc)
        logging.info("Saving the model {} at {}".format(self.ubm.name, self.model_loc))   


    def enroll(self):

        ############################# Compute sufficient stats ############################
        # Read idmap for the enrolling data
        enroll_idmap = sidekit.IdMap.read(self.enrol_idmap_loc)
        # Create Statistic Server to store/process the enrollment data
        self.enroll_stat = sidekit.StatServer(statserver_file_name=enroll_idmap,
                                         ubm=self.ubm)
        #logging.debug(enroll_stat)

        server = self.createFeatureServer("enroll") # at /output/feat/enrol
        server.feature_filename_structure = os.path.join(self.BASE_DIR, "feat", "{}.h5") 
        # Compute the sufficient statistics for a list of sessions whose indices are segIndices.
        #BUG: don't use self.NUM_THREADS when assgining num_thread as it's prune to race-conditioning
        self.enroll_stat.accumulate_stat(ubm=self.ubm,
                                    feature_server=server,
                                    seg_indices=range(self.enroll_stat.segset.shape[0])
                                   ) 

        # MAP adaptation of enrollment speaker models
        self.enroll_sv = self.enroll_stat.adapt_mean_map_multisession(ubm=self.ubm, r=3)

    def evaluate(self, save=True, explain=True):
        """
        This method is used to evaluate the test set. It does so by"
        - read the test_ndx file that contains the test set
        - read the trained UBM model, and trained parameters (enroll_stat file)
        - evaluate the test set using gmm_scoring and write the scores
        - if explain=True, write the scores in a more readible way
        Args:
            explain (boolean): If True, write another text file that contain
            the same information as the one within ubm_scores file but in a 
            readible way.
        """
        
        ############################# Read previously-trained UBM ############################


        # Create Feature server
        server = self.createFeatureServer()
        # Read the index for the test datas
        test_ndx = sidekit.Ndx.read(self.test_ndx_loc)

        ############################ Evaluating ###########################
        # Compute scores
        scores_gmm_ubm = sidekit.gmm_scoring(ubm=self.ubm, # universal model
                                             feature_server=server,
                                             enroll=self.enroll_sv, # stats for the gmms (2 gaussian components)
                                             ndx=test_ndx,
                                             num_thread=self.NUM_THREADS
                                            )
        self.scores = scores_gmm_ubm

        # Get Accuracy
        modelset = list(scores_gmm_ubm.modelset)
        segset = list(scores_gmm_ubm.segset)
        scoremat = np.array(scores_gmm_ubm.scoremat)
        # accuracy = super().getAccuracy( modelset, segset, scoremat, threshold=0)
        # print( "Accuracy: {}%".format(accuracy))

        if save:
            # Save the model's Score object
            scores_gmm_ubm.write(self.scores_loc)
            
        # # Explain the Analysis by writing more readible text file
        # if explain:
        #     filename = "ubm_scores_{}_explained.txt".format(self.NUM_GAUSSIANS)
        #     fout = open(os.path.join(self.BASE_DIR, "result", filename), "a")
        #     fout.truncate(0) #clear content
        #     modelset = list(scores_gmm_ubm.modelset)
        #     segset = list(scores_gmm_ubm.segset)
        #     scores = np.array(scores_gmm_ubm.scoremat)
        #     for seg_idx, seg in enumerate(segset):
        #         fout.write("Wav: {}\n".format(seg))
        #         for speaker_idx, speaker in enumerate(modelset):
        #             fout.write("\tSpeaker {}:\t{}\n"\
        #                 .format(speaker, scores[speaker_idx, seg_idx]))
        #         fout.write("\n")
        #     fout.close()

        return segset, scoremat, modelset


# if __name__ == "__main__":
#     conf_filename = "conf.yaml"
#     retrain = True

#     ubm = UBM(conf_filename, retrain=retrain)
#     if retrain:
#         ubm.train()

#     ubm.evaluate()
#     ubm.plotDETcurve()
#     print( "Accuracy: {}%".format(ubm.getAccuracy()) )