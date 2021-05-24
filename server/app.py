import uuid
import os
from flask import Flask, jsonify, request
# from flask_session import Session
from redis import StrictRedis
from redis.exceptions import ConnectionError
from flask_cors import CORS, cross_origin

from flask import send_file, send_from_directory, safe_join, abort
import sys
import json
sys.path.append('../model_T1/src')
sys.path.append('../model_T1/src/sidekit')
sys.path.append('../model_T2/src')
from pipeline import Pipeline
from Proc1 import Proc1
import pickle
from flask import current_app
from markupsafe import escape
import shutil
import logging



######################################################################################################
#######################################  Globals Variables  ##########################################
######################################################################################################

DEBUG = True
# instantiate the app
sr = StrictRedis(host='localhost', port=6379, db=0)
app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = app.root_path + '/uploads/'
app.config['LOG_FOLDER'] = app.root_path + '/logs/'
app.config['PRED_FOLDER'] = app.root_path + '/preds/'
app.config['AUTH_FOLDER'] = app.root_path + '/auth/'
# enable CORS
# CORS(app, resources={r'/api/*': {'origins':  "http://localhost:port"}})
# app.config['CORS_HEADERS'] = 'Content-Type'

# CORS(app, resources={r'/api/*': {'origins': '*'}})
CORS(app)

######################################################################################################
################################   Globals Functions  ################################################
######################################################################################################

# Dynamically populate the database according to the static folder
def access_uploaded_courses():
    courses = []
    for file in os.listdir('./uploads/vid/'):
        if file[0]!='.':
            courses.append(file.split('.')[0])

    print('Courses availbale:',courses)
    # app.logger.info("Courses on server:"+str(courses))
    return courses

def access_saved_annotations():
    annos = {}
    try:
        with open('./logs/anno/annotations.pickle','rb') as f:
            annos = pickle.load(f)
            print('History annotations found', annos)
            #app.logger.info('Annotation file found'+str(annos))
    except FileNotFoundError:
        print('File not exist or is empty')
        #app.logger.error('Annotation file not exist or is empty')
        with open('./logs/anno/annotations.pickle','wb') as f:
            pickle.dump(annos, f, protocol=pickle.HIGHEST_PROTOCOL)    
        
    return annos

def access_existing_preds():
    preds = []
    for file in os.listdir('../model_T1/results/'):
        if file[0]!='.':
            pred_dict = None
            with open('../model_T1/results/'+file,'r') as f:
                pred_dict = json.loads(f.read()) 
                pred_dict.append({'sessionId': pred_dict['sessionId'], 
                            'filename': pred_dict['filename'],
                            'annos': pred_dict['annos'],
                            'typ': pred_dict['typ'],
                            'preds': pred_dict['preds']})
    return preds


def remove_course(course_id):
    for course in COURSES:
        if course['id'] == course_id:
            COURSES.remove(course)
            return True
    return False


def filter_annos(sessionId, typ, file, all_annos):
    # print('ANNOS',all_annos)
    # print('sid', sessionId)
    # print('typ', typ)
    # print('filename',file)
    for key in all_annos.keys():
        if key[0] == sessionId and key[1]==typ and key[2]==file: # and anno['filename'] == filename:
            
            return all_annos[key]['annos']

def get_redis_nested(key, sr):
    val =  json.loads(sr.get(key))
    #app.logger.debug('[Redis - GET]' + key + ': '+str(val))
    print('[Redis - GET]' + key + ': '+str(val))
    return val

def set_redis_nested(dic, key, sr):
    #app.logger.debug('[Redis - SET]' + key + ': '+str(dic))
    print('[Redis - SET]' + key + ': '+str(dic))
    sr.set(key, json.dumps(dic))

if __name__ != '__main__':

    # for gunicorn or uwsgi
    gunicorn_logger = logging.getLogger('gunicorn.error') # TO REMOVE IN PRODUCTION
    app.logger.handlers = gunicorn_logger.handlers # TO REMOVE IN PRODUCTION
    app.logger.setLevel(gunicorn_logger.level) # TO REMOVE IN PRODUCTION

######################################################################################################
########################################  APIs  ######################################################
######################################################################################################
@app.route('/api/init')
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def default():
    crs = access_uploaded_courses()
    anns = access_saved_annotations()
    json_anns = {str(key):val for key, val in anns.items()}
    preds = {}
    cur_sess = {'sessionId':None, 'filename':None}
    sr.set('COURSES', json.dumps(crs))
    sr.set('ANNOS', json.dumps(json_anns))
    sr.set('PREDS', json.dumps(preds))
    sr.set('CURRENT_SESSION', json.dumps(cur_sess))

    return jsonify('Init done')

@app.route('/api/uploads/<path:filename>')
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def download_file(filename):
    print('[Filename] Accessing file:'+str(filename))
    app.logger.info('[Filename] Accessing file:'+str(filename))
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename, as_attachment=True)

@app.route('/api/auth', methods=['GET','POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def auth():
    ids = set()
    try:
        with open('./auth/ids.pickle', 'rb') as f: # save locally on server
            ids = pickle.load(f)
        print('[/auth] Auth log found: ', ids)
        # app.logger.info('[/auth] Auth log found: '+str(ids))
    except FileNotFoundError as e:
        print('[/auth] Authenciation log not found, new one is created')
        # app.logger.error('[/auth] Authenciation log not found, new one is created')

    # sessionId  = request.args.get('sessionId', None)
    post_data = request.get_json()
    print('[/auth] auth request', post_data)
    sessionId = post_data.get('sessionId')
    typ = post_data.get('typ')
    response_object = {'status': 'success'}

    if request.method == 'POST':
        if typ=='save':
            ids.add(sessionId)
            with open('./auth/ids.pickle', 'wb') as handle:
                pickle.dump(ids, handle, protocol=pickle.HIGHEST_PROTOCOL)

            response_object['message'] = 'Auth keys added!'

            # To keep the current user
            cur_sess = get_redis_nested('CURRENT_SESSION', sr)
            cur_sess['sessionId'] = sessionId
            set_redis_nested(cur_sess, 'CURRENT_SESSION', sr)

        elif typ=='verify':
            print('[/auth] All available authenciation IDs',ids)
            if sessionId in ids:
                response_object['found'] = 1
            else:
                response_object['found'] = 0 # if not found the combination in logged data

            cur_sess = get_redis_nested('CURRENT_SESSION', sr)
            cur_sess['sessionId'] = sessionId
            set_redis_nested(cur_sess, 'CURRENT_SESSION', sr)

    return jsonify(response_object)

@app.route('/api/courses', methods=['GET', 'POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def all_courses():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        
        crs = get_redis_dict('COURSES', sr)
        crs.append(post_data.get('name'))
        set_redis_dict(crs, 'COURSES', sr)

        response_object['message'] = 'Course added!'
    else:
        response_object['courses'] = get_redis_nested('COURSES', sr)
    return jsonify(response_object)

@app.route('/api/file', methods=['POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def set_course():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        cur_sess = get_redis_nested('CURRENT_SESSION', sr)
        cur_sess['filename'] = post_data.get('filename')
        set_redis_nested(cur_sess, 'CURRENT_SESSION', sr)
        response_object['message'] = 'Course switched!'
    return jsonify(response_object)

@app.route('/api/annotations', methods=['GET','POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def saved_annos():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        # print(post_data)
        sid = post_data.get('sessionId')
        filename = post_data.get('filename')
        new_anno = {
            'annos':post_data.get('annos'),
            'typ':post_data.get('typ')
        }
        print('[/annotations] received updated annotations,', new_anno)        
        # app.logger.info('[/annotations, POST] received updated annotations,'+str(new_anno))

        anns = get_redis_nested('ANNOS', sr)
        anns[str((sid,'FIRST-TIME', filename))] = new_anno
        set_redis_nested(anns, 'ANNOS', sr)
        # with open('./logs/anno/%s_%s_%s_%s.pickle'%(sid, uid, \
        #             new_anno['filename'],new_anno['typ']), 'wb') as f: # save locally on server
        #     pickle.dump(new_anno, f, protocol=pickle.HIGHEST_PROTOCOL)        

        # To resolve concurrency
        updated_annos = {}
        with open('./logs/anno/annotations.pickle', 'rb') as f: # Read the most updated file
            updated_annos = pickle.load(f)
        updated_annos[(sid,'FIRST-TIME', filename)] = new_anno
        with open('./logs/anno/annotations.pickle', 'wb') as f: # save locally on server
            pickle.dump(updated_annos, f, protocol=pickle.HIGHEST_PROTOCOL)

        # app.logger.info('[/annotations, POST] the global annotations repository now contains,'+str(get_redis_nested('ANNOS', sr)))
        print('[/annotations, POST] the global annotations repository now contains,'+str(get_redis_nested('ANNOS', sr)))
        response_object['message'] = 'Annotations added!'

    else:
        cur_sess = get_redis_nested('CURRENT_SESSION', sr)
        json_anns = get_redis_nested('ANNOS', sr)
        anns = {eval(key):val for key, val in json_anns.items()}
        curr_anno = filter_annos(cur_sess['sessionId'], 'FIRST-TIME', cur_sess['filename'], anns)
        print('[/annotations, GET] the global annotations repository now contains,'+str(json_anns))
        # app.logger.info('[/annotations, GET] the global annotations repository now contains,'+str(json_anns))
        if curr_anno:

            print("[/annotations, GET] The current session's saved annotations: "+str(curr_anno))
            response_object['savedAnnos'] = curr_anno

        else:

            print('[/annotations, GET]  Cannot find any previous annotations')
            response_object['savedAnnos'] = {}

    return jsonify(response_object)


@app.route('/api/adjustments', methods=['GET','POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def saved_adjustments():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        sid = post_data.get('sessionId')
        filename = post_data.get('filename')
        new_anno = {
            'annos':post_data.get('annos'), # To display
            'prevAnnos':post_data.get('prevAnnos'), # 1st-time annotations
            'adjustedPreds':post_data.get('adjustedPreds'), # selected 1st-time predictions 
            'typ':post_data.get('typ')
        }
        print('[/adjustments] received updated annotations,', new_anno)

        anns = get_redis_nested('ANNOS', sr)
        anns[str((sid,'ADJUSTED', filename))] = new_anno
        set_redis_nested(anns, 'ANNOS', sr)

        # To resolve concurrency
        updated_annos = {}
        with open('./logs/anno/annotations.pickle', 'rb') as f: # Read the most updated file
            updated_annos = pickle.load(f)
        updated_annos[(sid,'ADJUSTED', filename)] = new_anno
        with open('./logs/anno/annotations.pickle', 'wb') as f: # save locally on server
            pickle.dump(updated_annos, f, protocol=pickle.HIGHEST_PROTOCOL)

        # app.logger.info('[/adjustments, POST] the global annotations repository now contains,'+str(get_redis_nested('ANNOS', sr)))
        print('[/adjustments, POST] the global annotations repository now contains,'+str(get_redis_nested('ANNOS', sr)))
        response_object['message'] = 'Annotations added!'

    else:
        cur_sess = get_redis_nested('CURRENT_SESSION', sr)
        json_anns = get_redis_nested('ANNOS', sr)
        anns = {eval(key):val for key, val in json_anns.items()}
        curr_anno = filter_annos(cur_sess['sessionId'], 'ADJUSTED', cur_sess['filename'], anns)
        print('[/adjustments, GET] the global annotations repository now contains,'+str(json_anns))
        # app.logger.info('[/adjustments, GET] the global annotations repository now contains,'+str(json_anns))
        if curr_anno:
            print("[/adjustments] The current session's saved annotations: ", curr_anno)
            # app.logger.info("[/adjustments] The current session's saved annotations: ", curr_anno)
            response_object['savedAnnos'] = curr_anno

        else:
            print('[/adjustments]  Cannot find any previous adjusted annotations')
            # app.logger.info('[/adjustments]  Cannot find any previous adjusted annotations')
            response_object['savedAnnos'] = {}


    return jsonify(response_object)

@app.route('/api/predictions', methods=['POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
# @crossdomain(origin='*')
def predict():
    response_object = {'status': 'success'}


    data = request.get_json()
    print("[/predictions] prediction request received: ", data)
    if request.method =='POST':
        p = Pipeline(data, '/Users/zhaorui/work/cmad2.0/raw_data/','/Users/zhaorui/work/cmad2.0/processed_data/') ### TO CHANGE in production: absolute path
        p.train(True)
        p.enroll()
        df_res = p.predict(eval=False, gtp=[])
        print('[/predictions] df_res: ',df_res)
        prediction_results = p.post_result(df_res)  
        
        pred_id = uuid.uuid4().hex
        pres = get_redis_nested('PREDS', sr)
        pres[pred_id] = prediction_results
        set_redis_nested(pres, 'PREDS', sr)

        response_object['pred_id'] = pred_id  # save to the response to JS
        print('[/predictions] the prediction results to be returned',prediction_results)

        with open('./preds/%s_%s_%s_%s.pickle'%(data.get('sessionId'), pred_id,data.get('filename'),data.get('typ')), 'wb') as f: # save locally on server
            pickle.dump(prediction_results, f, protocol=pickle.HIGHEST_PROTOCOL)

    # data = request.get_json()
    # pred_id = '81f482a7a0a54ff6b5f72187b8f31baa'
    # with open('./preds/%s_%s_%s_%s_first-time.pickle'%(pred_id, data.get('userId'),data.get('sessionId'),data.get('filename')), 'rb') as f: # save locally on server
    #     PREDS[pred_id] = pickle.load(f)
    # response_object['pred_id'] = pred_id 

    return jsonify(response_object)

@app.route('/api/p1analyses', methods=['POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
# @crossdomain(origin='*')
def compute_p1():
    response_object = {'status': 'success'}


    rq = request.get_json()
    print("[/predictions] prediction request received: ", rq)
    if request.method =='POST':
        # rq_dict = {'filename':filename, 'sessionId':sessionId, 'stopwords':stoplist, 'numOfKeywords':numOfKeywords, 'interval':interval, 'no_bins':no_bins}

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
        import string

        ENGLISH_STOP_WORDS = ENGLISH_STOP_WORDS+list(string.ascii_lowercase)
        stoplist = ENGLISH_STOP_WORDS+list('1234567890')
        sessionId = 1111
        numOfKeywords = 20
        interval = 300
        no_bins = 30
        filename = 'JP4'

        rq = {'filename':filename, 'sessionId':sessionId, 'stopwords':stoplist, 'numOfKeywords':numOfKeywords, 'interval':interval, 'no_bins':no_bins}


        infolder = '/Users/zhaorui/work/cmad2.0/processed_data/annotations/'
        proc1 = Proc1(rq, infolder)
        res = proc1.main()
        print(res)

        response_object['result'] = res
        # {'S': {(2400, 2700): [('write number two', 0.03967149495968096), ('number two', 0.11188876046331633), ...], other_intervals:[], other_intervals:[]}}

    return jsonify(response_object)

@app.route('/api/predictions', methods=['GET'])
# @crossdomain(origin='*')
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def retrieve_prediction():
    pred_id = request.args.get('pid')
    response_object = {'status': 'success'}
    if request.method == 'GET':
        response_object['preds'] = get_redis_nested('PREDS', sr)[pred_id]

    return jsonify(response_object)

@app.route('/api/loggedpredictions', methods=['POST'])
# @cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
# @crossdomain(origin='*')
def loggedpredictions():
    # To return logged predictions upon loggin
    response_object = {'status': 'success'}

    data = request.get_json()
    sessionId = data.get('sessionId')
    filename = data.get('filename')
    print("[/loggedpredictions] prediction request received: ", data)
    response_object['found'] = 0
    if request.method =='POST':
        pids = []
        ps = []
        typs = []

        for f in os.listdir('./preds/'):
            print('pred file',f)
            if f.split('.')[-1] =='pickle':
                pid, sid, fname, ftyp = f.split('.')[0].split('_')
                if sid==sessionId and fname==filename:
                    print("[/loggedpredictions] found logged predictions: ", f)
                    with open('./preds/'+f, 'rb') as fi: # save locally on server
                        prediction_results = pickle.load(fi)
                        pres = get_redis_nested('PREDS', sr)
                        pres[pid] = prediction_results
                        set_redis_nested(pres, 'PREDS', sr)
                        pids.append(pid)
                        ps.append(prediction_results)
                        typs.append(ftyp)
                        response_object['found'] = 1
                        print('[/loggedpredictions] the prediction results to be returned',prediction_results)


        response_object['pred_ids'] = pids  # save to the response to JS
        response_object['typs'] = typs  # save to the response to JS         
        response_object['ps'] = ps  # save to the response to JS 

    return jsonify(response_object)   

@app.route('/api/submit', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def end_session():
    # To return logged predictions upon loggin
    response_object = {'status': 'success'}

    data = request.get_json()
    sessionId = data.get('sessionId')
    filename = data.get('filename')

    audio_locs = ['../processed_data/%s_out_%s_%s/'%(filename, sessionId, typ) for typ in \
                                                    ['first-time','adjusted','adjusted2','adjusted3','adjusted4']]
    ### TO CHANGE in production: absolute path

    print("[/submit] session end request received: "+str(data))
    # app.logger.info("[/submit] session end request received: "+str(data))

    # remove audio files
    for dire in audio_locs:
        print('[/submit] removing from'+str(dire))
        # app.logger.debug('[/submit] removing from'+str(dire))
        try:
            shutil.rmtree(dire+'audio')
            shutil.rmtree(dire+'feat')
        except FileNotFoundError as e:
            print(e)
        
    return jsonify(response_object)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

if __name__ == '__main__':
    app.run(host='localhost', port=5000)   ### TO CHANGE in production: 0.0.0.0