<template>
    <div>
    <b-overlay :show="show" rounded="lg">
    <b-container fluid="md" >
        <b-row>
        <b-col cols="8">
            <b-container>

                <div id="video-wrapper" class="with-margin">
                    <video controls ref="videoPlayer" class="video-js vjs-fluid">     
                        <source :src="'http://localhost:5000/api/uploads/vid/' + this.$globals.file + '.mp4'" type="video/mp4">  
                        <track id="entrack" kind="captions"  mode='showing'
                            :src="'http://localhost:5000/api/uploads/sub/' + $globals.file + '.vtt'" 
                            srclang="en" label="English" default>
                    </video>
                </div>
<!--                 <b-row align-v="center" class="text-left">
                    <b-col cols=6>
                        <h2>{{ $globals.file }}</h2></b-col>
                    
                    <b-col cols=6> -->
<div class="with-margin">
                        
                    <b-form-checkbox
                      id="loopCheck"
                      v-model="checkedLoop"
                      name="loopCheck"
                      value="Yes"
                      unchecked-value="No"
                    >
                      Enable utterance by utterance loop
                  </b-form-checkbox>
              <!-- </b-col>
                </b-row>
 -->
                    <!-- <div>State: <strong>{{ status }}</strong></div> -->
                    <b-button-group class="mx-1">
                    <b-button id="prevBtn" class="cue-button" @click="rewind2PrevLoop()"><b-icon icon="skip-backward-fill" aria-hidden="true"></b-icon> Previous cue</b-button>
                    <b-button id="nextBtn" class="cue-button" @click="forward2NextLoop()">Next cue <b-icon icon="skip-forward-fill" aria-hidden="true"></b-icon></b-button>
                    </b-button-group>
                
</div>
            </b-container>
        </b-col>
        <b-col cols="4" class="container"> 
            <b-container class="h-100 position-absolute">
                    <div class="with-margin top-inside-abs" >
                        <h2>Who's speaking?</h2>
                        <b-button-group class="with-margin">
                            <b-button id="marker-teacher" @click="annotateT()" 
                            variant="outline-primary">Teacher</b-button>
                            <b-button id="marker-student" @click="annotateS()"
                            variant="outline-success">Student</b-button>
                            <b-button id="marker-other" @click="annotateO()"
                            variant="outline-secondary">Others</b-button></b-button-group>
                    </div>
                    <!-- <b-container class="bv-example-row"> -->
                    <div class="with-margin end-inside-abs">
                          <b-button variant="danger" class="save-button" @click="onSave(); saveToast(true)">Save for later</b-button>
                          <b-button variant="success" class="save-button" @click="onSubmit(); safeSubmitToast(true);">Submit now</b-button>
                    </div>
                </b-container>
                <!-- </b-container> -->
        </b-col>
        </b-row>
    </b-container>
        
    <template #overlay>
        <div class="text-center">
          <b-icon icon="stopwatch" font-scale="3" animation="cylon"></b-icon>
          <p> Training in process...</p>
          <!-- <p> Please keep your session ID for future references: {{ this.sessionId }}</p> -->
          <p>This could take upto 20 minutes.</p>
        </div>
    </template>

    </b-overlay>
    </div>
</template>

<script>
import videojs from 'video.js';
import 'video.js/dist/video-js.min.css';
import 'video.js/dist/video.min.js';
import 'videojs-seek-buttons/dist/videojs-seek-buttons.css';
import 'videojs-seek-buttons/dist/videojs-seek-buttons.min.js';
import axios from 'axios';
import { uuid } from 'vue-uuid'; 
// eslint-disable-next-line no-unused-vars
import abLoopPlugin from 'videojs-abloop';
// import txtdata from ${this.$globals.ASSET_URL} + 'txt/' + ${this.$globals.file} + '.txt';
export default {
    name: 'Page1',
    methods: {
        swtich2Tab(selected){
            console.log('[Page 1] Directed to [Page '+selected+']');
            var tabs = document.getElementById("header").getElementsByTagName("span");
            for (var i = 0; i < tabs.length; i++) {
                var tab = tabs[i];
            if (i==selected) {
                tab.classList.add('tab-selected');
            }else{
                tab.classList.remove('tab-selected');
            }
          }
        },

        debug (event) {
            console.log(event.target.name)
        },

        log(item) {
            console.log(item)
        },

        toggleCueLoop(){
            var checkBox = document.getElementById("loopCheck");
            var prev = document.getElementById("prevBtn");
            var next = document.getElementById("nextBtn");
            if (checkBox.checked == true) {           
                this.player.pause();
                // this.player.currentTime(0); // rewind to start
                console.log("[Page 1] Cue loop enabled");
                next.removeAttribute("disabled");
                prev.removeAttribute("disabled");

                var rangeIndex = this.checkRange(this.player.currentTime(), this.ranges);
                if(rangeIndex==-1){
                    //go to next cue
                    rangeIndex = this.getSurrRangeIdx(this.player.currentTime(), this.ranges, 'prev');
                    console.log('No subtitles found for currentTime, forward to next');
                }
                var range = this.ranges[rangeIndex];
                var startTp = (parseFloat(range[0])+parseFloat('0.001')).toFixed(3);
                this.player.abLoopPlugin.setStart(startTp).setEnd(range[1]).enable();
            }else{
                this.player.pause();
                next.setAttribute("disabled", "true");
                prev.setAttribute("disabled", "true");
                // this.player.currentTime(0); // rewind to start   
                console.log("[Page 1] Cue loop disabled");             
                this.player.abLoopPlugin.disable();

            }
        },

        forward2NextLoop(){
            this.player.pause();
            var curTime = this.player.currentTime();
            var rangeIndex = this.checkRange(curTime, this.ranges);
            // console.log("Forward cue loop pressed");
            if(rangeIndex+1 < this.ranges.length){
                var range = this.ranges[rangeIndex+1];
                var startTp = (parseFloat(range[0])+parseFloat('0.001')).toFixed(3);// to avoid double-line subtitles, in the case that subtitles does not have spacings TODO
                this.player.currentTime(startTp);
                this.player.abLoopPlugin.setStart(startTp).setEnd(range[1]).enable();
                console.log("[Page 1] Loop time forward to cue index "+ (rangeIndex+1) +" - ("+startTp+", "+range[1]+").");
            }

        },

        rewind2PrevLoop(){
            this.player.pause();
            var curTime = this.player.currentTime();
            var rangeIndex = this.checkRange(curTime, this.ranges);
            // console.log("[Page 1] Rewind cue loop pressed");
            if(rangeIndex-1 >= 0){
                var range = this.ranges[rangeIndex-1];
                var startTp = (parseFloat(range[0])+parseFloat('0.001')).toFixed(3);// to avoid double-line subtitles, in the case that subtitles does not have spacings TODO
                this.player.currentTime(startTp);
                this.player.abLoopPlugin.setStart(startTp).setEnd(range[1]).enable();
                console.log("[Page 1] Loop time rewind to cue index "+ (rangeIndex-1) +" - ("+startTp+", "+range[1]+").");
            }

        },

        setVideoWrapperStyle(vw, typ, act){
            if (typ=='T'){
                if (act=='off'){                                            
                    vw.classList.remove("shadow-t");
                }else{
                    vw.classList.remove("shadow-o");
                    vw.classList.remove("shadow-s");
                    vw.classList.add("shadow-t");
                }

            }else if(typ=='S'){
                if (act=='off'){                                  
                    vw.classList.remove("shadow-s");
                }else{
                    vw.classList.remove("shadow-o");
                    vw.classList.remove("shadow-t");
                    vw.classList.add("shadow-s");
                }
            }else{
               if (act=='off'){                               
                    vw.classList.remove("shadow-o");

                }else{
                    vw.classList.remove("shadow-s");
                    vw.classList.remove("shadow-t");
                    vw.classList.add("shadow-o");
                } 
            }
        },

annotateT(){
            var btnT = document.getElementById("marker-teacher");
            var btnS = document.getElementById("marker-student");
            var btnO = document.getElementById("marker-other");
            var vw = document.getElementById("video-wrapper");
            var rangeIndex = this.checkRange(this.player.currentTime(), this.ranges);
            if (rangeIndex!=-1){
                var range = this.ranges[rangeIndex];
                var key = String(range[0]); // use the starting timestamp as key
                if (!(key in this.savedAnnos)) { //if did not annotate before
                    this.setBtnStyle(btnT, 'T', 'on');  
                    this.setVideoWrapperStyle(vw, 'T', 'on');
                    this.savedAnnos[key] = "T";
                    console.log("[Page 1] Annotate interval ("+key+", "+range[1]+") as Teacher");
                }else{
                    if (this.savedAnnos[key] == "T"){                       
                            this.setBtnStyle(btnT, 'T', 'off');
                            this.setVideoWrapperStyle(vw, 'T', 'off');
                            delete this.savedAnnos[key];   
                            console.log("De-select");
                        }
                    else{
                        this.setBtnStyle(btnO, 'O', 'off');
                        this.setBtnStyle(btnS, 'S', 'off');
                        this.setBtnStyle(btnT, 'T', 'on');
                        this.setVideoWrapperStyle(vw, 'T', 'on');
                        this.savedAnnos[key] = "T";
                        console.log("[Page 1] Annotate interval ("+key+", "+range[1]+") as Teacher");
                    }
                }
            } 
        },

        annotateS(){
            var btnT = document.getElementById("marker-teacher");
            var btnS = document.getElementById("marker-student");
            var btnO = document.getElementById("marker-other");
            var vw = document.getElementById("video-wrapper");
            var rangeIndex = this.checkRange(this.player.currentTime(), this.ranges);
            if (rangeIndex!=-1){
                var range = this.ranges[rangeIndex];
                var key = String(range[0]); // use the starting timestamp as key
                if (!(key in this.savedAnnos)) { //if did not annotate before
                    this.setBtnStyle(btnS, 'S', 'on');  
                    this.setVideoWrapperStyle(vw, 'S', 'on');
                    this.savedAnnos[key] = "S";
                    console.log("[Page 1] Annotate interval ("+key+", "+range[1]+") as Student");
                }else{
                    if (this.savedAnnos[key] == "S"){                       
                            this.setBtnStyle(btnS, 'S', 'off');
                            this.setVideoWrapperStyle(vw, 'S', 'off');
                            delete this.savedAnnos[key];  
                            console.log("De-select");
                        }
                    else{
                        // deselect the previous selection 
                        this.setBtnStyle(btnO, 'O', 'off');
                        this.setBtnStyle(btnT, 'T', 'off');
                        this.setBtnStyle(btnS, 'S', 'on');
                        this.setVideoWrapperStyle(vw, 'S', 'on');
                        console.log("[Page 1] Annotate interval ("+key+", "+range[1]+") as Student");
                        this.savedAnnos[key] = "S";
                    }
                }
            }
        },

        annotateO(){
            var btnT = document.getElementById("marker-teacher");
            var btnS = document.getElementById("marker-student");
            var btnO = document.getElementById("marker-other");
            var vw = document.getElementById("video-wrapper");
            var rangeIndex = this.checkRange(this.player.currentTime(), this.ranges);
            if (rangeIndex!=-1){
                var range = this.ranges[rangeIndex];
                var key = String(range[0]); // use the starting timestamp as key
                // console.log(this.savedAnnos);
                if (!(key in this.savedAnnos)) { //if did not annotate before
                    this.setBtnStyle(btnO, 'O', 'on'); 
                    this.setVideoWrapperStyle(vw, 'O', 'on'); 
                    this.savedAnnos[key] = "O";
                    console.log("[Page 1] Annotate interval ("+key+", "+range[1]+") as Others");
                }else{
                    if (this.savedAnnos[key] == "O"){                       
                            this.setBtnStyle(btnO, 'O', 'off');
                            this.setVideoWrapperStyle(vw, 'O', 'of');
                            delete this.savedAnnos[key]; 
                            console.log("De-select"); 
                        }
                    else{
                        // deselect the previous selection 
                        this.setBtnStyle(btnS, 'S', 'off');
                        this.setBtnStyle(btnT, 'T', 'off');
                        this.setBtnStyle(btnO, 'O', 'on');
                        this.setVideoWrapperStyle(vw, 'O', 'on');
                        console.log("[Page 1] Annotate interval ("+key+", "+range[1]+") as Others");
                        this.savedAnnos[key] = "O";
                    }
                }
            }
        },
        loadSavedBtn(rangeIndex){
            var btnT = document.getElementById("marker-teacher");
            var btnS = document.getElementById("marker-student");
            var btnO = document.getElementById("marker-other");
            var vw = document.getElementById("video-wrapper");
            // To render button styles on already saved annotations
            if (rangeIndex == -1) { // if this portion does not belong to any cue ranges/intervals
                this.setBtnStyle(btnS, 'S', 'off');
                this.setBtnStyle(btnT, 'T', 'off');
                this.setBtnStyle(btnO, 'O', 'off');
                vw.classList.remove("shadow-o");
                vw.classList.remove("shadow-s");
                vw.classList.remove("shadow-t");
            }else {
                var key = String(this.ranges[rangeIndex][0]);
                if (!(key in this.savedAnnos)){
                    this.setBtnStyle(btnS, 'S', 'off');
                    this.setBtnStyle(btnT, 'T', 'off');
                    this.setBtnStyle(btnO, 'O', 'off');
                    vw.classList.remove("shadow-o");
                    vw.classList.remove("shadow-s");
                    vw.classList.remove("shadow-t");
                }else{
                    var lbl = this.savedAnnos[key];
                    if (lbl=='O'){
                        this.setBtnStyle(btnS, 'S', 'off');
                        this.setBtnStyle(btnT, 'T', 'off');
                        this.setBtnStyle(btnO, 'O', 'on');
                        vw.classList.remove("shadow-s");
                        vw.classList.remove("shadow-t");
                        vw.classList.add("shadow-o");

                    } else if (lbl=='S'){
                        this.setBtnStyle(btnO, 'O', 'off');
                        this.setBtnStyle(btnT, 'T', 'off');
                        this.setBtnStyle(btnS, 'S', 'on');
                        vw.classList.remove("shadow-o");
                        vw.classList.remove("shadow-t");
                        vw.classList.add("shadow-s");
                    } else{

                        this.setBtnStyle(btnO, 'O', 'off');
                        this.setBtnStyle(btnS, 'S', 'off');
                        this.setBtnStyle(btnT, 'T', 'on');
                        vw.classList.remove("shadow-s");
                        vw.classList.remove("shadow-o");
                        vw.classList.add("shadow-t");
                    }
                }
            }
        },

        async getRange(){
            const res = await fetch('http://localhost:5000/api/uploads/txt/' + this.$globals.file + ".txt");

            const data = await res.text();
            var lines = data.split("\n");
            var ranges = [];
            for (var i = 0; i < lines.length; i++) {
                var aa = lines[i].split(" ");
                ranges.push([parseFloat(aa[0]).toFixed(3), parseFloat(aa[1]).toFixed(3)]);
            }
            this.ranges = ranges;
            console.log("[Page 1] Fetched ranges",this.ranges);
        },

        checkRange(cur, ranges) {
            // console.log(ranges);
            console.log("[Page 1] Current time: "+ cur);
            for (var i = 0; i < ranges.length; ++i) {
                if ((cur >= ranges[i][0])&&(cur < ranges[i][1])) {
                    console.log("[Page 1] Current cue index is ", i);
                    return i
                }
            }
            return -1
        },

        getSurrRangeIdx(cur, ranges, typ){
            // for timepoints  
            var prevRange = -1;
            var nextRange = -1;
            for (var i = 0; i < ranges.length; ++i) {
                if ((cur > ranges[i][1])) {
                    prevRange = i;
                } else{
                    nextRange = i;
                    break;
                }
            }

            console.log("[Page 1] Prev index is ", prevRange);
            console.log("[Page 1] Next index is ", nextRange);
            if(typ=='prev'){
                return prevRange;
            }else{
                return nextRange;
            }
        },

        setBtnStyle(btn, typ, act){
            if (typ=='T'){
                if (act=='off'){                                            
                    btn.classList.remove("btn-primary");
                    btn.classList.add("btn-outline-primary");
                }else{
                    btn.classList.remove("btn-outline-primary");
                    btn.classList.add("btn-primary");
                }

            }else if(typ=='S'){
                if (act=='off'){                                            
                    btn.classList.remove("btn-success");
                    btn.classList.add("btn-outline-success");
                }else{
                    btn.classList.remove("btn-outline-success");
                    btn.classList.add("btn-success");
                }
            }else{
               if (act=='off'){                                            
                    btn.classList.remove("btn-secondary");
                    btn.classList.add("btn-outline-secondary");
                }else{
                    btn.classList.remove("btn-outline-secondary");
                    btn.classList.add("btn-secondary");
                } 
            }
        },    

        onSave() {
            // evt.preventDefault();
            const annotation = {
                sessionId: this.$globals.sessionId,
                filename: this.$globals.file ,
                annos: this.savedAnnos,
                typ: "first-time"
            };
            console.log('[Page 1] to-be-saved annotations: ', annotation);
            this.saveAnnotation(annotation);
        },

        saveAnnotation(annotation) { // to save a set of annotaion
          const path = 'http://localhost:5000/api/annotations';
          axios.post(path, annotation)
            .then(() => {
              this.getSavedAnnotations(); // to receive the updated list of annotations
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.log(error);
              // this.getBooks();
            });
        },

        getSavedAnnotations() { // to get annotations (previously saved)
          const path = 'http://localhost:5000/api/annotations';
          console.log("[Page 1] Fetching the most updated annotations");
          axios.get(path)
            .then((res) => {
              this.savedAnnos = res.data.savedAnnos;
                console.log('[Page 1] Updated annotations: ',this.savedAnnos);
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error);
            });
        },

        safeSubmitToast(append = false) {
            if(Object.keys(this.savedAnnos).length==0){
               this.toastCount++
                this.$bvToast.toast('Need at least one annotation to proceed!', {
                  title: 'Unable to submit',
                  autoHideDelay: 5000,
                  variant: 'warning',
                  appendToast: append
                })
            }
        },

        saveToast(append = false) {
               this.toastCount++
                this.$bvToast.toast('Your annotations have been saved!', {
                    title: 'Saved successfully',
                    autoHideDelay: 5000,
                    appendToast: append,
                    variant: 'success',
                });
            
        },


        onSubmit() {
            console.log('[Page 1] submit button pressed, annotation length', Object.keys(this.savedAnnos).length);
            if(Object.keys(this.savedAnnos).length!=0){            
                // evt.preventDefault();
                const annotation = {
                    sessionId: this.$globals.sessionId,
                    filename: this.$globals.file ,
                    annos: this.savedAnnos,
                    typ: "first-time"
                };
                this.show = true;
                this.saveAnnotation(annotation);
                console.log('[Page 1] the to-be-submitted annotations: ', annotation);
                this.submitAnnotation(annotation);
                this.$globals.annos  = this.savedAnnos;
            }
        },

        submitAnnotation(annotation) { // to submit a set of annotaion
          const path = 'http://localhost:5000/api/predictions';
          axios.post(path, annotation)
            .then((res) => { 
                this.pred_id = res.data.pred_id;
                console.log("[Page 1] Prediction done, ID is: ", this.pred_id);
                // console.log(res);
                this.getPredictions(this.pred_id); // to receive the predictions
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.log(error);
              // this.getBooks();
            });
        },

        getPredictions(pred_id){
          const path = 'http://localhost:5000/api/predictions';
          // console.log("Prediction ID is: ",pred_id);
          axios.get(path, {params:{pid: pred_id}})
            .then((res) => {
              this.preds = res.data.preds;
              console.log('[Page 1] Fetching prediction results ...')
              console.log("[Page 1] 1st-time prediction results: ", this.preds);       

              this.$globals.preds = this.preds;
              this.$globals.pred_id = this.pred_id;
              this.swtich2Tab(2);
              this.$router.push('/Page2');     
              console.log('[Page 1] Directed to [Page 2]');
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error);
            });
        }


    },
    data () {
        return {
            vid_file:null,
            sub_file:null,
            player:null,
            checkedLoop: 'No',
            ranges:null,
            curRangeIdx:null,
            savedAnnos: null,
            preds: null,
            pred_id:null,
            show: false,
            toastCount: 0,
            sessionId: null// since overlay does not recognize global variables
        };
    },

    beforeMount(){
        this.vid_file = this.$globals.file + '.mp4';
        this.sub_file = this.$globals.file + '.vtt';
        this.getRange();
        console.log('[Page 1] session ID',this.$globals.sessionId);
    },

    mounted() {

        var prev = document.getElementById("prevBtn");
        var next = document.getElementById("nextBtn");
        next.setAttribute("disabled", "true");
        prev.setAttribute("disabled", "true");

        // this.savedAnnos = new Object();
        this.getSavedAnnotations();
        if (this.savedAnnos==null){
            this.savedAnnos = new Object();
        }
        console.log("[Page 1] Onload, Fetched last-login annotations: ", this.savedAnnos);
        this.curRangeIdx = 0;

        if (!videojs.getPlugins().abLoopPlugin) {
          abLoopPlugin(window, videojs)
        }
        this.sessionId = this.$globals.sessionId;

        let options = {plugins: {
                            abLoopPlugin: {
                                enabled:false,
                                loopIfBeforeStart:false,
                                loopIfAfterEnd:true,
                                pauseAfterLooping: true,
                                pauseBeforeLooping: false,
                                createButtons: true
                        }}};
        this.player = videojs(this.$refs.videoPlayer, 
                                options,
                            function onPlayerReady() {
                                console.log('onPlayerReady', this);
                                
        });

        
        let that = this; 
        this.player.on("timeupdate", // to render button styles 
            function(){
                var curTime = that.player.currentTime();
                // console.log(that.curRangeIdx);
                var rangeIndex = -1;
                for (var i = 0; i < that.ranges.length; ++i) {
                    var range = that.ranges[i];
                    if ((curTime >= range[0])&&(curTime < range[1])) {
                        rangeIndex = i;
                    }
                } 
                // console.log("rangeIndex="+rangeIndex);
                if (that.curRangeIdx!=rangeIndex){ //if cue has changed
                    that.loadSavedBtn(rangeIndex); // render saved 
                    that.curRangeIdx = rangeIndex;
            }
            }
        );
        this.player.abLoopPlugin.onLoopCallBack = function(api,player){
            var opts = api.getOptions();
            api.setOptions({'pauseAfterLooping': true}); 
        };

        this.player.seekButtons({
            forward: 5,
            back: 5
        });
    },


    beforeUpdate(){
        this.toggleCueLoop()
    },

    beforeDestroy() {
        if (this.player) {
            this.player.dispose()
        }
    }
}
</script>

<style type="text/css">
    .test-bg1{background-color: coral}
    .test-bg2{background-color: red}
    .top-inside-abs{
        position: absolute; 
        left: 0;
        right: 0;
        margin: auto;/* horizontally centering 2*/
        top:0;
    }
    .end-inside-abs{
        position: absolute; 
        left: 0;
        right: 0;
        margin: auto;/* horizontally centering 2*/
        bottom:0;
    }
    .cue-button{
        margin:5px;
        width:150px;
    }
    .save-button{
        width: 125px;
        margin:15px;
    }
    .with-margin{
        margin-top: 30px;
        margin-bottom: 30px
    }
    .shadow-t {
      -moz-box-shadow:    0px 0px 20px 20px rgba(2,117,216,0.6);
      -webkit-box-shadow: 0px 0px 20px 20px rgba(2,117,216,0.6);
      box-shadow:         0px 0px 20px 20px rgba(2,117,216,0.6);
    }    
    .shadow-s {
      -moz-box-shadow:    0px 0px 20px 20px rgba(92, 184, 92, 0.6);
      -webkit-box-shadow: 0px 0px 20px 20px rgba(92, 184, 92, 0.6);
      box-shadow:         0px 0px 20px 20px rgba(92, 184, 92, 0.6);
    }    
    .shadow-o {
      -moz-box-shadow:    0px 0px 20px 20px rgba(119,119,119,0.7);
      -webkit-box-shadow: 0px 0px 20px 20px rgba(119,119,119,0.7);
      box-shadow:         0px 0px 20px 20px rgba(119,119,119,0.7);
    }
</style>