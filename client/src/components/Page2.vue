<template>
    <div>

      <!-- Create a div where the graph will take place -->
        <!-- <TrendPlot/> -->
<!--         <trend
          :data="deltas"
          :gradient="['#6fa8dc', '#42b983', '#2c3e50']"
          auto-draw
          smooth
        >
        </trend> -->

      <b-container>
      <b-row align-h='center'>
      <p>
        <strong>Session ID:</strong> {{ this.$globals.sessionId }} <br>
      </p>
    </b-row>
            <hr class="my-4">
      <b-row>

          <h2>Summary</h2>
          </b-row>
          <b-row>
            <b-col cols="8">
            <p style="text-align: left;">
              The video clip consists of {{ this.n_total_segs }} utterances. Given the {{ this.n_annos }} annotations provided by the user in the last step, we generated the predictions for the remaining part of the video. 
            </p>
            <p style="text-align: left;">
              Out of the {{ this.n_preds }} predictions, <strong>{{ this.n_t_segs }}</strong> are classified as <strong>Teacher</strong>'s, and <strong>{{ this.n_s_segs }}</strong> are classified as <strong>Students</strong>'.
            </p>
            <p style="text-align: left;">
              Regarding the confidential scores, the average score differences between the two classes is {{ this.preds.mean.toFixed(3) }}, with a standard deviation of {{ this.preds.std.toFixed(3) }}.
            </p>
          </b-col>
          <b-col>
            
        <b-table hover :items="stat_table_items"></b-table>
          </b-col>
          </b-row>
        </b-container>

      <b-container class="my-2">
        <!-- {{ this.preds }} -->
        <!-- {{ this.deltas }} -->


        <h2>Prediction results</h2>
        <b-table hover :items="table_items" ></b-table>



      </b-container>
      <b-container class="my-2">
            <hr class="my-4">
          <div>
            <h2>Pick a range to adjust</h2>
            <vue-range-slider style="margin-top: 50px" ref="slider" :min="min_score" :step="0.001" :max="max_score" v-model="slider_value"></vue-range-slider>
          </div>
          <b-row align-h="center" class="my-4">
                  <!-- <b-button type="button" class="btn cbuttons" variant="danger">Back</b-button> -->
                  <b-button type="button" class="cbuttons" @click="onSubmit()" variant="success">Next</b-button>
                              </b-row>
      </b-container>
    </div>
</template>

<script>
import axios from 'axios';
import Vue from 'vue'
import 'vue-range-component/dist/vue-range-slider.css'
import VueRangeSlider from 'vue-range-component'
//import * as d3 from 'd3'
// import Trend from "vuetrend"
// Vue.use(Trend)


export default {
    name: 'Page2',
    
    components: {
      VueRangeSlider
    },
    
    props:{
    },

    methods: {
      swtich2Tab(selected){
            console.log('[Page 2] Directed to [Page '+selected+']');
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

      initValues(){
        // console.log(this.to_adjusted);
        // console.log(this.slider_value);
        // console.log(this.to_adjusted);
        var pp = this.preds.preds;
        // console.log('preds',pp);
        for (var idx in pp) {
          if (parseFloat(pp[idx]['Delta'].toFixed(3))>=this.slider_value[0] 
            && parseFloat(pp[idx]['Delta'].toFixed(3))<=this.slider_value[1]) 
          {
            this.to_adjusted.push(pp[idx]['File']);
          }
        }

        console.log('[Page 2] Timestamps to b adjusted'+ this.to_adjusted);
        this.$globals.to_adjusted = this.to_adjusted;

        // console.log('previous annos ', this.$globals.annos);
        var savedAnnos = {};

        for (var idx in this.$globals.annos) {
          // var it = {};
          // it[key] = 
          //   savedAnnos.push(it);
            savedAnnos[idx] = this.$globals.annos[idx];
        }

        // console.log('annos_and_preds unfinished ', savedAnnos);
        for (var idx in pp) {
          var key = pp[idx]['File'];
            savedAnnos[key] = pp[idx]['Pred'];
        }
        // console.log('annos_and_preds ', savedAnnos);
        this.$globals.annos_and_preds = savedAnnos;
        console.log('[Page 2] 1st-time annotations + predictions (annos_and_preds): ', this.$globals.annos_and_preds);
        console.log('[Page 2] 1st-time annotations ', this.$globals.annos); 
      },

      onSubmit(){


        this.swtich2Tab(3);
        this.$router.push('/Page3');
      }
    },

    created(){
      console.log("[Page 2] Session ID: "+this.$globals.sessionId);
      this.preds = this.$globals.preds;
      this.pred_id = this.$globals.pred_id;
      // console.log(this.preds);
      console.log('[Page 2] 1st-time prediction results (preds.preds): ',this.preds.preds);

      this.n_total_segs = 0;
      this.n_annos = 0;
      this.n_preds = 0;
      this.n_t_segs = 0;
      this.n_s_segs = 0;
      this.table_items = [];
      this.max_score = parseFloat(this.preds['max'].toFixed(3));
      this.min_score = parseFloat(this.preds['min'].toFixed(3));
      this.slider_value = [parseFloat(this.preds['min'].toFixed(3)), 
                          parseFloat(this.preds['max'].toFixed(3))];
      // this.to_adjusted = [];

      this.stat_table_items = [];
      this.stat_table_items.push({attribute: "Min", value: this.preds['min'].toFixed(3)});
      this.stat_table_items.push({attribute: "25%", value: this.preds['25%'].toFixed(3)});
      this.stat_table_items.push({attribute: "50%", value: this.preds['50%'].toFixed(3)});
      this.stat_table_items.push({attribute: "75%", value: this.preds['75%'].toFixed(3)});
      this.stat_table_items.push({attribute: "Max", value: this.preds['max'].toFixed(3)});
      this.stat_table_items.push({attribute: "Mean", value: this.preds['mean'].toFixed(3)});
      this.stat_table_items.push({attribute: "S.D", value: this.preds['std'].toFixed(3)});

      if (this.preds.hasOwnProperty('annos')) {
        let pp = this.preds.annos;
        this.n_annos = Object.keys(this.preds.annos).length;
        this.n_total_segs = this.n_annos;

        for (var idx in pp) {
          this.table_items.push({
            start_timestamp: idx,
            type: 'Annotation',
            delta: 'N/A',
            speaker: pp[idx],
            _rowVariant: 'danger'
          });
        }
      }

      var cell_color = {'T':'primary','S':'success'};
      if (this.preds.hasOwnProperty('preds')) {
        let pp = this.preds.preds;
        this.n_preds = Object.keys(this.preds.preds).length;
        this.n_total_segs = this.n_total_segs + this.n_preds;
        for (var idx in pp) {
          if (pp[idx]['Pred']=='T') {
            this.n_t_segs+=1;
          }else{
            this.n_s_segs+=1;
          }

          this.deltas.push(pp[idx]['Delta']);
          this.table_items.push({
            start_timestamp: pp[idx]['File'],
            type: 'Prediction',
            delta: pp[idx]['Delta'].toFixed(3),
            speaker: pp[idx]['Pred'],
            _cellVariants: { speaker: cell_color[pp[idx]['Pred']] }
          });
        }
      }
      this.initValues();
      // console.log(this.table_items);
      // console.log(this.deltas);
      // console.log(this.n_total_segs);

    },

    data () {
        return {
            selectedVideo: this.$globals.file,
            sessionId: null,
            preds: null,
            pred_id:null,
            deltas: [],
            table_items: null,
            max_score: null,
            min_score: null,
            avg_score: null,
            n_t_segs: null,
            n_s_segs: null,
            n_annos: null,
            n_preds: null,
            n_total_segs: null,
            slider_value: null,
            to_adjusted: []

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