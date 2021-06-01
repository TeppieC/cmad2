<template>
    <div>
      <b-container>
      <b-jumbotron header="Welcome to C.M.A.D" lead="" style="text-align: left;">
        <p><strong>C</strong>lassroom <strong>M</strong>ultimedia <strong>A</strong>nalytics <strong>D</strong>ashboard is a tool that conducts automatic content analysis of classroom video/audio/scripts, with minor supervisions.</p>

        <hr class="my-4">
        <b-container style="height:200px; " align-v="end">
          <b-row align-h="center" >
                  <b-button type="button" id="cbtn" class="btn btn-success cbuttons" v-b-modal.login-modal>Continue with previous work</b-button>
                  <b-tooltip target="cbtn" triggers="hover">
                    Continue with your saved work
                  </b-tooltip>
                    <b-button type="button" class="cbuttons" id="sobtn" @click="onNewLogin" variant="danger">Start a new session</b-button>
                  <b-tooltip target="sobtn" triggers="hover">
                    To start a new session
                  </b-tooltip>

          </b-row>
          <b-row align-h="center" >
            <p><strong>Current Session ID: </strong> {{this.$globals.sessionId}} </p>
          </b-row>
          <b-row align-h="center">
            <p>(Please keep this as future reference)</p>
          </b-row>
        </b-container>
        <hr class="my-4">

        <b-container id='vid-select' style="display: none">
          
          <b-row class='my-4'>
                <b-col cols="8">
                  <p><strong>Please select a video to start</strong></p>
                </b-col>
                <b-col cols="4" style="width:600px;">
                    <b-form-select v-model="selectedVideo" @change="onVidSelectorChange($event)" :options="courses" value-field="name"
                    text-field="name" size="md"></b-form-select>
                  </b-col>
              
          </b-row>
            
          <b-row class='my-4'>
            <b-col cols="3" >
              <b-button variant='primary'>                
                <router-link to="/Page1" id="next-page-sel" @click.native="switch2Tab(1); retreiveHistoryPredictions();" style="color:#fff">
                              Annotate
                </router-link>
              </b-button>
            </b-col>
            <b-col cols="3" >
              <b-button variant='primary' @click="checkAnnotationFile();" style="color:#fff">
                              Analyze
              </b-button>                

            </b-col>
        </b-row>
        
        </b-container>
      </b-jumbotron>
    </b-container>

    <b-modal ref="loginmodal"
            id="login-modal"
            title="Continue with your previous work"
            hide-footer>
      <b-form @submit="onSubmitLogin" class="w-100">



          <b-form-group id="form-session-group"
                    label="Session ID:"
                    label-for="form-session-input">
            <b-form-input id="form-session-input"
                          v-model="sessionId"
                          placeholder="">
            </b-form-input>
          </b-form-group>

        
        
          <b-button style="float:right" type="submit" @click="onSubmitLogin" id="submitBtn" variant="success">Login</b-button>
      </b-form>



    </b-modal>
    </div>
</template>

<script>
import axios from 'axios';
import { uuid } from "vue-uuid";

export default {
    name: 'Page0',
    
    components: {
    },
    
    props:{
    },

    methods: {
    loginMsg() {
        this.boxTwo = ''
        var message = null;
        var ty = null;
        var va = null;
        if (this.verified==1){
          message = "Logged in!";
          ty = "Confirmation";
          va = "success";
        }else{
          message = "Please try again";
          ty = "Wrong tokens";
          va = "danger";
        }
        this.$bvModal.msgBoxOk(message, {
          title: ty,
          size: 'md',
          buttonSize: 'md',
          okVariant: va,
          headerClass: 'p-2 border-bottom-0',
          footerClass: 'p-2 border-top-0',
          centered: true
        })
          .then(value => {
            this.boxTwo = value
          })
          .catch(err => {
            // An error occurred
          })
      },

      annoNotFoundToast(append = false) {
        this.toastCount++
        this.$bvToast.toast('No annotation file found for this video', {
            title: 'Annotations Not Found',
            autoHideDelay: 5000,
            appendToast: append,
            variant: 'danger',
        });    
      },

      checkAnnotationFile(){
        const info = {
            filename: this.$globals.file
        };
        console.log(info);
        const path = 'http://localhost:5000/api/historyAnnotation';
                  axios.post(path, info)
                    .then((res) => { 
                        var found = res.data.found;
                        console.log('Found: '+res.data.found);
                        if (found==1) {
                          this.switch2Tab(5);
                          this.$router.push('/Page5');
                        }else{
                          this.annoNotFoundToast(true);
                        }
                    })
                    .catch((error) => {
                      // eslint-disable-next-line
                      console.log(error);
                    });
      },

      onVidSelectorChange:function(value){
         this.$globals.file = value;
         console.log('[Page 0] Video file',this.$globals.file); // set the videofile

          // evt.preventDefault();
          // to save current auto-generated ids to the server
          const file = {
            filename: value                        
          }; 

          const path = 'http://localhost:5000/api/file';
          axios.post(path, file)
            .then(() => {
              this.showMessage = true;
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.log(error);
            });

          // this.initForm();
          console.log('[Page 0] File switched to ', value); 
      },

      switch2Tab(selected){
        console.log('[Page 0] Directed to [Page '+selected+']');
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


      initServerGlobals(){
        const path = 'http://localhost:5000/api/init';

        axios.get(path)
          .then(() => {
            console.log('[Page 0] Init globals... Done');
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
        },
        
      // importAll(r) {
      //   r.keys().forEach(key => (this.files.push({ value: key.slice(2, -4),  text: key.slice(2, -4)})));
      // },

      getCourses(){
        // todo: apply warning if missing any files, or just missing certain types of files
        // this.importAll(require.context('../../public/uploads/vid/', true, /^.*\.mp4$/));
        const path = 'http://localhost:5000/api/courses';
        axios.get(path)
          .then((res) => {
            this.courses = res.data.courses;
            console.log(this.courses);
          })
          .catch((error) => {
            // eslint-disable-next-line
            console.error(error);
          });
        },

        initGlobals(){
          for (let key in this.$globals) {
            if (key!='domain'){
              this.$globals[key] = null;
            }
          }
          console.log('[Page 0] refreshed globals',this.$globals);
        },

        retreiveHistoryPredictions(evt){
            const data = {
              sessionId: this.$globals.sessionId,
              filename: this.$globals.file
            }; 
            console.log('[Page 0] input session id to retreive logged predictions', data.sessionId);
            console.log('[Page 0] input filename to retreive logged predictions', data.filename);
            var that = this;
            const path = 'http://localhost:5000/api/'+'loggedpredictions';
            axios.post(path, data)
              .then((res) => {
                if (res.data.found==1){
                  console.log('[Page 0] Found logged predictions');
                  var typs = res.data.typs;
                  var ps = res.data.ps;
                  var pids = res.data.pred_ids;
                  for (var i = 0; i < typs.length; i++) {
                    if (typs[i]=='first-time'){
                      that.$globals.pred_id = pids[i];
                      that.$globals.preds = ps[i];
                      console.log('[Page 0] Prediction ID: ', that.$globals.pred_id);
                    }else{
                      that.$globals.adjusted_pred_id = pids[i];
                      that.$globals.adjusted_preds = ps[i];
                      console.log('[Page 0] Prediction ID: ', that.$globals.pred_id);                    
                    }
                  }
                }

              })
              .catch((error) => {
                // eslint-disable-next-line
                console.log(error);
            });
        },

        onSubmitLogin(evt) {
          evt.preventDefault();
          if(this.sessionId!="" && this.sessionId!=null){

            const authIds = {
              sessionId: this.sessionId,
              typ: 'verify'
            }; 
            console.log('[Page 0] input session id to verify', authIds.sessionId);
            var that = this;
            const path = 'http://localhost:5000/api/auth';
            axios.post(path, authIds)
              .then((res) => {
                this.getCourses();
                that.verified = res.data.found;
                console.log('[Page 0] Verifying auth');
                if(that.verified==1){
                  this.initGlobals();// Clear everything in the global variables/give a fresh start for the app
                  this.$globals.sessionId = this.sessionId;
                  this.$refs.loginmodal.hide();

                  var vs = document.getElementById("vid-select");
                  if (this.$globals.sessionId==null){
                    vs.style.display = 'none';
                  }else{
                    vs.style.display = 'block';
                  }
                }else{
                  console.log('[Page 0] ID Not found');
                }
                this.loginMsg();

              })
              .catch((error) => {
                // eslint-disable-next-line
                console.log(error);
            });
          }
          // this.initForm();
        },

        onNewLogin(evt){

          this.initGlobals();// Clear everything in the global variables/give a fresh start for the app

          evt.preventDefault();
          // to save current auto-generated ids to the server
          this.sessionId = uuid.v4();
          const authIds = {
            sessionId: this.sessionId,
            // sessionId: "9998",
            typ:'save'
          }; 
          this.$globals.sessionId = this.sessionId;

          const path = 'http://localhost:5000/api/auth';
          axios.post(path, authIds)
            .then(() => {
              this.getCourses();
              this.showMessage = true;
              console.log("[Page 0] New Session ID: "+this.$globals.sessionId);
              this.box3 = ''
              var message = "Your session ID is " + this.$globals.sessionId;
              this.$bvModal.msgBoxOk(message, {
                title: "Your new tokens",
                size: 'md',
                buttonSize: 'md',
                okVariant: "success",
                headerClass: 'p-2 border-bottom-0',
                footerClass: 'p-2 border-top-0',
                centered: true
              })
                .then(value => {
                  this.box3 = value
                })
                .catch(err => {
                  // An error occurred
                })
            })
            .catch((error) => {
              // eslint-disable-next-line
              console.log(error);
            });

          var vs = document.getElementById("vid-select");
          if (this.$globals.sessionId==null){
            vs.style.display = 'none';
          }else{
            vs.style.display = 'block';
          }

          // this.initForm();
          console.log('[Page 0] Continue with new session ID');
        }
    },

    created(){
      console.log("Session ID: "+this.$globals.sessionId);
      if(this.$globals.sessionId==null){
        this.initServerGlobals();
      }
    },

    mounted(){

      var vs = document.getElementById("vid-select");
      if (this.$globals.sessionId==null){
        vs.style.display = 'none';
      }else{
        vs.style.display = 'block';
      }

    },
    
    data () {
        return {
            selectedVideo: this.$globals.file,

            boxTwo: null,
            box3:null,
            toastCount: 0,

            courses: null,

            verified: null,

              sessionId: null,

            videoOptions: {
              autoplay: false,
              controls: true,
              sources: [
                {
                    type: "video/mp4"
                }
              ]
        }
      };
    }
}
</script>
<style type="text/css">
  
    .cbuttons{
        width: 250px;
        height: 60px;
        margin:30px;
    }
</style>