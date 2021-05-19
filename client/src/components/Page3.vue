<template>
    <div>
    <b-overlay :show="show" rounded="lg">
    <b-container fluid="md" >
        <b-row>
        <b-col cols="8">
            <b-container>

                <div id="video-wrapper" class="with-margin">
                    <video controls ref="videoPlayer" class="video-js vjs-fluid">     
                        <source :src="'http://127.0.0.1:5000/api/uploads/vid/' + this.$globals.file + '.mp4'" type="video/mp4">  
                        <track id="entrack" kind="captions"  mode='showing'
                            :src="'http://127.0.0.1:5000/api/uploads/sub/' + $globals.file + '.vtt'" 
                            srclang="en" label="English" default>
                    </video>
                </div>
<!--                 <b-row align-v="center" class="text-left">
                    <b-col cols=6>
                        <h2>{{ $globals.file }}</h2></b-col>
                    
                    <b-col cols=6> -->
<div class="with-margin">
                        
<!--                     <b-form-checkbox
                      id="loopCheck"
                      v-model="checkedLoop"
                      name="loopCheck"
                      value="Yes"
                      unchecked-value="No"
                    >
                      Enable utterance by utterance loop
                  </b-form-checkbox> -->
              <!-- </b-col>
                </b-row>
 -->
                    <!-- <div>State: <strong>{{ status }}</strong></div> -->
<!--                     <b-button-group class="mx-1">
                    <b-button id="prevBtn" class="cue-button" @click="rewind2PrevLoop()"><b-icon icon="skip-backward-fill" aria-hidden="true"></b-icon> Previous cue</b-button>
                    <b-button id="nextBtn" class="cue-button" @click="forward2NextLoop()">Next cue <b-icon icon="skip-forward-fill" aria-hidden="true"></b-icon></b-button>
                    </b-button-group> -->
                
</div>
            </b-container>
        </b-col>
        <b-col cols="4" class="container"> 
            <b-container class="h-100 position-absolute">
                    <div class="with-margin top-inside-abs" >
                        <h2>Correct any wrong labels</h2>
                

                    <b-button-group class="mx-1">
                    <b-button id="prevCorBtn" class="cue-button" @click="rewind2PrevCorrection()"><b-icon icon="skip-backward-fill" aria-hidden="false"></b-icon> Previous correction</b-button>
                    <b-button id="nexCortBtn" class="cue-button" @click="forward2NextCorrection()">Next correction <b-icon icon="skip-forward-fill" aria-hidden="false"></b-icon></b-button>
                    </b-button-group>
                                        <b-form-checkbox
                      id="loopCheck"
                      v-model="checkedLoop"
                      name="loopCheck"
                      value="Yes"
                      unchecked-value="No"
                    >
                      Enable utterance by utterance loop
                    </b-form-checkbox>

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
                          <b-button variant="danger" class="save-button" @click="onSave(); saveToast(true);">Save for later</b-button>
                          <b-button variant="success" class="save-button" @click="onSubmit()">Submit now</b-button>
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
          <!-- <p> Please keep your session ID for future references: {{ this.$globals.sessionId }}</p> -->
          <p>This could take up to 20 minutes.</p>
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
    name: 'Page3',
    components: {
        // VideoJS
    },

    props:{
    },

    watch: {

    },

    methods: {
        swtich2Tab(selected){
            console.log('[Page 3] Directed to [Page '+selected+']');
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
            var prev = document.getElementById("prevCorBtn");
            var next = document.getElementById("nextCorBtn");
            if (checkBox.checked == true) {           

                this.player.pause();
                // this.player.currentTime(0); // rewind to start
                console.log("[Page 3] Cue loop enabled");
                // var range = this.ranges[0];                

                var rangeIndex = this.checkRange(this.player.currentTime(), this.ranges);
                if(rangeIndex==-1){
                    //go to next cue
                    rangeIndex = this.getSurrRangeIdx(this.player.currentTime(), this.ranges, 'prev');
                    console.log('No subtitles found for currentTime, forward to next');
                }
                var range = this.ranges[rangeIndex];
                var startTp = (parseFloat(range[0])+parseFloat('0.001')).toFixed(3);// to avoid double-line subtitles, in the case that subtitles does not have spacings TODO
                this.player.abLoopPlugin.setStart(startTp).setEnd(range[1]).enable();
            }else{
                this.player.pause();
                // this.player.currentTime(0); // rewind to start   
                console.log("[Page 3] Cue loop disabled");             
                this.player.abLoopPlugin.disable();

            }
        },

        // forward2NextLoop(){
        //     this.player.pause();
        //     var curTime = this.player.currentTime();
        //     var rangeIndex = this.checkRange(curTime, this.ranges);
        //     console.log("Forward cue loop pressed");
        //     if(rangeIndex+1 < this.ranges.length){
        //         var range = this.ranges[rangeIndex+1];
        //         this.player.currentTime(range[0]);
        //         this.player.abLoopPlugin.setStart(range[0]).setEnd(range[1]).enable();
        //         console.log("Loop time forward to cue index "+ (rangeIndex+1) +" - ("+range[0]+", "+range[1]+").");
        //     }

        // },

        // rewind2PrevLoop(){
        //     this.player.pause();
        //     var curTime = this.player.currentTime();
        //     var rangeIndex = this.checkRange(curTime, this.ranges);
        //     console.log("Rewind cue loop pressed");
        //     if(rangeIndex-1 >= 0){
        //         var range = this.ranges[rangeIndex-1];
        //         this.player.currentTime(range[0]);
        //         this.player.abLoopPlugin.setStart(range[0]).setEnd(range[1]).enable();
        //         console.log("Loop time rewind to cue index "+ (rangeIndex-1) +" - ("+range[0]+", "+range[1]+").");
        //     }

        // },

        forward2NextCorrection(){
            this.player.pause();
            var curTime = this.player.currentTime();
            console.log("[Page 3] Current time: "+ curTime);

            var go_to_range = null;
            var comp_adjusted_range = [];
            for (var i = 0; i < this.adjusted_range.length; ++i) {
                if (i==0) {
                    comp_adjusted_range.push([0, this.adjusted_range[0][0]]);
                }else if(i==this.adjusted_range.length-1){
                    comp_adjusted_range.push([this.adjusted_range[i-1][1], this.player.duration]);
                }else{
                    comp_adjusted_range.push([this.adjusted_range[i-1][1], this.adjusted_range[i][0]]);
                }
            }
            // console.log('[Page 3] comp_adjusted_range',comp_adjusted_range);

            for (var i = 0; i < this.adjusted_range.length; ++i) {
                if (curTime >= this.adjusted_range[i][0] && curTime < this.adjusted_range[i][1]) {
                        // console.log("1 Current cue index is ", i);
                        go_to_range = i+1; // if exactly falls in one of the to-be-corrected ranges

                }
            }
            if(go_to_range==null){
                for (var i = 0; i < comp_adjusted_range.length; ++i) {
                    if (curTime >= comp_adjusted_range[i][0] && curTime < comp_adjusted_range[i][1]) {
                        // console.log("2 Current cue index is ", i);
                        go_to_range = i; // if exactly falls in one of the to-be-corrected ranges

                    }
                }
            }


            console.log("[Page 3] Forward pressed");
            if(go_to_range < this.adjusted_range.length){
                var range = this.adjusted_range[go_to_range];
                var startTp = (parseFloat(range[0])+parseFloat('0.001')).toFixed(3);// to avoid double-line subtitles, in the case that subtitles does not have spacings TODO
                this.player.currentTime(startTp);
                this.player.abLoopPlugin.setStart(startTp).setEnd(range[1]).enable();
                console.log("[Page 3] Loop time forward to cue index "+ go_to_range +" - ("+startTp+", "+range[1]+").");
            }

        },

        rewind2PrevCorrection(){
            this.player.pause();
            var curTime = this.player.currentTime();
            console.log("[Page 3] Current time: "+ curTime);

            var go_to_range = null;
            var comp_adjusted_range = [];
            for (var i = 0; i < this.adjusted_range.length; ++i) {
                if (i==0) {
                    comp_adjusted_range.push([0, this.adjusted_range[0][0]]);
                }else if(i==this.adjusted_range.length-1){
                    comp_adjusted_range.push([this.adjusted_range[i-1][1], this.player.duration]);
                }else{
                    comp_adjusted_range.push([this.adjusted_range[i-1][1], this.adjusted_range[0][0]]);
                }
            }
            // console.log('comp_adjusted_range',comp_adjusted_range);

            for (var i = 0; i < this.adjusted_range.length; ++i) {
                if (curTime >= this.adjusted_range[i][0] && curTime < this.adjusted_range[i][1]) {
                        // console.log("1 Current cue index is ", i);
                        go_to_range = i; // if exactly falls in one of the to-be-corrected ranges

                }
            }
            if(go_to_range==null){
                for (var i = 0; i < comp_adjusted_range.length; ++i) {
                    if (curTime >= comp_adjusted_range[i][0] && curTime < comp_adjusted_range[i][1]) {
                        // console.log("2 Current cue index is ", i);
                        go_to_range = i-1; // if exactly falls in one of the to-be-corrected ranges

                    }
                }
            }


            console.log("[Page 3] Rewind pressed");
            if(go_to_range-1 >= 0){
                var range = this.adjusted_range[go_to_range-1];                
                var startTp = (parseFloat(range[0])+parseFloat('0.001')).toFixed(3);// to avoid double-line subtitles, in the case that subtitles does not have spacings TODO

                this.player.currentTime(startTp);
                this.player.abLoopPlugin.setStart(startTp).setEnd(range[1]).enable();
                console.log("[Page 3] Loop time Rewind to cue index "+ go_to_range +" - ("+startTp+", "+range[1]+").");
            }

        },

        checkCorrectionRange(cur, ranges){
            // console.log(ranges);
            console.log("[Page 3] Current time: "+ cur);
            for (var i = 0; i < ranges.length; ++i) {
                if ((cur >= ranges[i][0])&&(cur < ranges[i][1])) {
                    // console.log("Current cue index is "+i);
                    return i // if exactly falls in one of the to-be-corrected ranges
                }
            }
            // if is out of the to-be-corrected range
            return -1
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
                        console.log("[Page 3] Annotate interval ("+key+", "+range[1]+") as Teacher");
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
                // console.log(this.savedAnnos);
                if (!(key in this.savedAnnos)) { //if did not annotate before
                    this.setBtnStyle(btnS, 'S', 'on');  
                    this.setVideoWrapperStyle(vw, 'S', 'on');
                    this.savedAnnos[key] = "S";
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
                        this.savedAnnos[key] = "S";
                        console.log("[Page 3] Annotate interval ("+key+", "+range[1]+") as Student");
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
                        this.savedAnnos[key] = "O";
                        console.log("[Page 3] Annotate interval ("+key+", "+range[1]+") as Others");
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
            const res = await fetch('http://127.0.0.1:5000/api/uploads/txt/' + this.$globals.file + ".txt");

            const data = await res.text();
            var lines = data.split("\n");
            var ranges = [];
            for (var i = 0; i < lines.length; i++) {
                var aa = lines[i].split(" ");
                ranges.push([parseFloat(aa[0]).toFixed(3), parseFloat(aa[1]).toFixed(3)]);
            }
            this.ranges = ranges;
            console.log("[Page 3] Fetched ranges",this.ranges);

            console.log('[Page 3] To-be-adjusted timestamps',this.to_adjusted); // ["103.000", "106.000", "117.000", "152.000", "35.000", "37.000", "48.000", "60.000", "8.000", "87.000"]

            // var temp_adj = [];
            // for (var i = 0; i < this.to_adjusted.length; i++) {
            //     temp_adj.push(parseInt(this.to_adjusted[i].slice(0,-4)));
            // }
            // console.log('temp adj',temp_adj);

            for (i = 0; i < this.ranges.length; i++) {
                var range = this.ranges[i];
                // console.log('range',range);
                // console.log('range0',range[0]);
                if (this.to_adjusted.includes(range[0])){
                    // console.log(range[0]);
                    this.adjusted_range.push(range);
                }    
            } 
            console.log('[Page 3] To-be-adjusted range', this.adjusted_range);
        },

        checkRange(cur, ranges) {
            // console.log(ranges);
            console.log("[Page 3] Current time: "+ cur);
            for (var i = 0; i < ranges.length; ++i) {
                if ((cur >= ranges[i][0])&&(cur < ranges[i][1])) {
                    console.log("[Page 3] Current cue index is "+i);
                    return i
                }
            }
            console.log('No subtitle/cue found for this timestamp');
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

            console.log("[Page 3] Prev index is ", prevRange);
            console.log("[Page 3] Next index is ", nextRange);
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

        saveToast(append = false) {
               this.toastCount++
                this.$bvToast.toast('Your annotations have been saved!', {
                    title: 'Saved successfully',
                    autoHideDelay: 5000,
                    appendToast: append,
                    variant: 'success',
                });
            
        },

        onSave() {
            // evt.preventDefault();
            const annotation = {
                sessionId: this.$globals.sessionId,
                filename: this.$globals.file ,
                annos: this.savedAnnos,
                typ: "adjusted"
            };
            console.log('[Page 3] Annotations to be saved: ', annotation);
            this.saveAdjustment(annotation);
        },

        saveAdjustment(annotation) { // to save a set of annotaion
          const path = 'http://127.0.0.1:5000/api/adjustments';
          // console.log(annotation);
          axios.post(path, annotation)
            .then(() => {
              this.getSavedAdjustments(); // to receive the updated list of annotations
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.log(error);
              // this.getBooks();
            });
        },

        getSavedAdjustments() { // to get annotations (previously saved)
          const path = 'http://127.0.0.1:5000/api/adjustments';
          console.log("[Page 3] Fetching the most updated annotations");
          axios.get(path)
            .then((res) => {
                this.savedAnnos = res.data.savedAnnos;
                console.log('[Page 3] The most updated annotations: ', this.savedAnnos);
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error);
            });
        },

        onSubmit() {
            // evt.preventDefault();
            const annotation = {
                sessionId: this.$globals.sessionId,
                filename: this.$globals.file ,
                annos: this.savedAnnos, // To display / the as-is annotations/predictions for all utterances / can be wrong
                prevAnnos: this.$globals.annos, // last-time annotations (Annos made in P1)
                prevPreds: this.$globals.preds, // complex structured / the most useful thing is a list of previous prediction results
                adjustedPreds: this.to_adjusted, // sub-list of last-time predictions that was reviewed in this round (some preds decided in P2)
                typ: "adjusted"
            };
            this.show = true;
            this.saveAdjustment(annotation);
            this.$globals.adjustments = this.savedAnnos;
            console.log('[Page 3] to-be-submitted annotations: ', annotation);
            this.submitAdjustment(annotation);
            // console.log('Submitted');
        },

        submitAdjustment(annotation) { // to submit a set of annotaion
          const path = 'http://127.0.0.1:5000/api/predictions';
          axios.post(path, annotation)
            .then((res) => { 
                this.pred_id = res.data.pred_id;
                console.log("[Page 3] Prediction done, ID is: ",this.pred_id);
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
          const path = 'http://127.0.0.1:5000/api/predictions';
          // console.log("Prediction ID is: ",pred_id);
          axios.get(path, {params:{pid: pred_id}})
            .then((res) => {
                this.preds = res.data.preds;
                console.log('[Page 3] Fetching prediction results ...')
                console.log("[Page 3] 2nd-time prediction results: ", this.preds);   
                this.$globals.adjusted_preds = this.preds;
                this.$globals.adjusted_pred_id = this.pred_id;
                this.swtich2Tab(4);
                this.$router.push('/Page4');
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.error(error);
            });
        }


    },
    data () {
        return {
            player:null,
            checkedLoop: 'Yes',
            ranges:null,
            curRangeIdx:null,
            savedAnnos: null,
            preds: null,
            pred_id:null,
            show: false,
            to_adjusted: null,
            adjusted_range:null
        };
    },

    beforeMount(){
        this.getRange();
        console.log('[Page 3] Session ID: ',this.$globals.sessionId);
    },

    mounted() {
        // this.savedAnnos = new Object();
        // this.getSavedAnnotations();
        this.to_adjusted = this.$globals.to_adjusted;
        this.adjusted_range = [];
        this.savedAnnos = this.$globals.annos_and_preds;
        console.log("[Page 3] The saved annotations to be displayed is", this.savedAnnos);
        this.curRangeIdx = 0;

        if (!videojs.getPlugins().abLoopPlugin) {
          abLoopPlugin(window, videojs)
        }

        let options = {plugins: {
                            abLoopPlugin: {
                                enabled:false,
                                loopIfBeforeStart:false,
                                loopIfAfterEnd:false,
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