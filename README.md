# About this project
This is a dashboard built to study the differences in teachers'/students' word uses in (Math) classrooms. The painpoint of conducting such analyses lies in the tedious work in annotating course recordings and the lack of useful automatic visualization tools. This interactive dashboard tool is targeted at facilitating the annotation process(specifically the identification of who speaks what) following a semi-supervised approach. As downstream tasks, it features in extracting keywords from both parties and contrast them with some visualizations to help analysis.

# Features
The annotation feature: For unannotated classroom recordings, CMAD will identify the speaker of each speech. To do this, it asks for a minimum number of mannual annotations and will generate predictions for the rest. 

The keyword extraction feature: 3 types of keyword extraction methods are provided. Visualizations of the output are also provided for language use analysis.

# Workflow
1. On homepage, user select an video to start analysis; If already annotated, jump to step x; else, step 2.
2. The initial annotation page will display a video player to play the classroom recording with subtitles/captions. It asked user to manually annotate/identify if the line is spoken by the teacher or a student. They can click on save progress and return to this page later on, or proceed to next page when they've done with a certain number of annotations(a minimum of 1 line annotation from each side has to be provided before proceeding to the next page, otherwise the UBM speaker recognition engine won't start)
3. The initial prediction page displays our UBM speaker recognition engine's predictions to the rest of unannotated lines. Each prediction is associated with a confidence score. Users can use the slider to the bottom of this page to select a subset of predicted annotations (usually those low confidence ones) to review and correct in the next page
4. The re-annotation page display similar content as the initial annotation page, but only focus on review and correct the selected lines from last page. The idea is to use those corrections to improve the prediction engine.
5. The final result page display the final predictions of all lines in the captions. 
6. The analysis page allow user to select one of the 3 keyword extraction approaches and display results in different kinds of visualizations.

# Current status
- UBM speaker recognition engine works. 
- keyword extraction approaches have been experimented in notebooks, all work individually, but not yet integrated into the dashboard.
- Website can be fire up with VueJS frontend and flask backend on localhost
- Homepage, intial annotation, intial prediction, re-annotation, final result page work with minor issues around edge cases
- Analysis page unfinished (need to integrate all 3 keyword extraction approaches, skeleton code is done, one of the approach(yake?) is done, bar chart visualizations is done in apexcharts, need to enable downloading annotation results in csv/xlsx)
- Need to setup in remote server
- May need to add support to load video and read captions directly from Youtube instead of uploading to server


# Stack
Backend: flask
Frontend: VueJS
Visualiations: apexcharts
Speaker recognition engine: sidekit's ubm model from https://github.com/Anwarvic/Speaker-Recognition
Keyword extraction methods: yake, babelfy WSD api, customized AWL list

# References
- https://github.com/Anwarvic/Speaker-Recognition

# Get started
Prepare data
- Register in babelfy to get your babelfy api key
- Download video and script files from the shared google drive, and put them in place TODO

Prepare project for dev
- Make a .env file in the root folder based on .env.example and source it using ```. .env```  or ```source .env```
- (Optional but recommended) Create a virtual environment for python3, python 3.9 preferred. Switch to this environment.
- From the root folder of this project, run ```pip install -r requirements.txt`
- Install libsvm by either `sudo apt-get install libsvm-dev` or `brew install libsvm`
- Install a spacy vocab using `python -m spacy download en_core_web_sm`
- From client/src run ```npm run serve```
- From server/ run ```python app.py```