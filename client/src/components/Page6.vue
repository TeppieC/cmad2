<template>
    <div>




      <b-container class="my-2">
        <!-- {{ this.preds }} -->
        <!-- {{ this.deltas }} -->
        
        <b-row align-h='center'>
          <p>
            <strong>Session ID:</strong> {{ this.$globals.sessionId }} <br>
            <strong>Video:</strong> {{ this.selectedVideo }} <br>
          </p>
        </b-row>
        <hr class="my-4">

        <div align-h='center'>
          <b-card no-body >
            <b-container class="my-2">
              <b-row>
              <b-col cols="6"> Select a period</b-col>
              <b-col cols="4"><b-form-select v-model="view_period" @change="onPeriodSelectorChange($event)" :options="periods" value-field="name"
                text-field="name" size="md"></b-form-select></b-col>
              <b-col cols="2"></b-col>
              </b-row>
                
              
            </b-container>
              <b-tabs card>
                <b-tab title="Keywords" active>
                    <apexchart 
                        id="chart_v1_s" 
                        ref="realtimeChart"
                        type="bar" 
                        height="440" 
                        :options="chartOptions_v1_s" 
                        :series="series_v1_s"></apexchart>

                    <apexchart 
                        id="chart_v1_t" 
                        ref="realtimeChart"
                        type="bar" 
                        height="440" 
                        :options="chartOptions_v1_t" 
                        :series="series_v1_t"></apexchart>
                </b-tab>
                              <!-- <b-tab title="# occurence" active>
                    <apexchart type="bar" height="440" :options="chartOptions" :series="series"></apexchart>
                </b-tab>
                              <b-tab title="# occurence" active>
                    <apexchart type="bar" height="440" :options="chartOptions" :series="series"></apexchart>
                </b-tab> -->
              </b-tabs>

          <b-container id='kw_detail' style="display: none">
            <hr class="my-4">
            <b-row align-h="center">
              <b-col cols="6">
                  <p><strong id="selected_kw">{{ this.selected_kw }}</strong></p>
                  <b-row style="width:600px; " align-v="end">
                    <b-col cols="8" >
                      
                      
                    </b-col>
                    
                  </b-row>
              </b-col>
            </b-row>
          </b-container>
          </b-card>


        </div>
        

        <!-- <b-table hover :items="table_items" ></b-table> -->
        <b-row align-h="center" class="my-4">
                <!-- <b-button type="button" class="btn cbuttons" variant="danger">Back</b-button> -->
                <!-- <b-button type="button" class="cbuttons" @click="onSubmit()" variant="success">Finish</b-button> -->
        </b-row>


      </b-container>

    </div>
</template>

<script src="http://d3js.org/d3.v3.min.js"></script>
<!-- <script type='text/javascript' src='../barchart.js'></script> -->
<!-- <script>
document.write('<script src="http://' + (location.host || 'localhost').split(':')[0] + ':35729/livereload.js?snipver=1"></' + 'script>')
</script>
 -->
<!-- <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js"></script> -->
<!-- <script>
window.jQuery || document.write('<script src="js/vendor/jquery-1.10.2.min.js"><\/script>')
</script> -->
<!-- <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script> -->
<!-- <script src="https://cdn.jsdelivr.net/npm/vue-apexcharts"></script> -->

<script>
import axios from 'axios';
import Vue from 'vue'
import * as d3 from 'd3'
import VueApexCharts from 'vue-apexcharts'

Vue.use(VueApexCharts)
Vue.component('apexchart', VueApexCharts)

export default {
    name: 'Page6',
    
    components: {
      apexchart: VueApexCharts,
    },
    
    props:{
    },

    methods: {
      switch2Tab(selected){
            console.log('Directed to page'+selected);
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
      onSubmit(){

      },
      onPeriodSelectorChange:function(value){
        this.view_period = value;
        console.log('[Page 6] selected period',this.view_period); 
        this.updateViz();
        // this.updateChart();

          // evt.preventDefault();
          // to save current auto-generated ids to the server
          // const file = {
          //   filename: value                        
          // }; 

          // const path = 'http://localhost:5000/api/file';
          // axios.post(path, file)
          //   .then(() => {
          //     this.showMessage = true;
          //   })
          //   .catch((error) => {
          //     // eslint-disable-next-line
          //     console.log(error);
          //   });

          // // this.initForm();
          // console.log('[Page 0] File switched to ', value); 
      },
      updateViz(){

        this.series_v1_s = [
                            {
                              name: 'Students',
                              data: this.students_segs[this.view_period][1],
                              // labels: this.students_segs[this.view_period][0]
                            }
                          ]
        this.series_v1_t = [
                            {
                              name: 'Teacher',
                              data: this.teacher_segs[this.view_period][1],
                              // labels: this.teacher_segs[this.view_period][0]
                            }]
        this.chartOptions_v1_s = {
         labels: [this.students_segs[this.view_period][0]]
        }
        this.chartOptions_v1_t = {
         labels: [this.teacher_segs[this.view_period][0]]
        }

        // this.$refs.realtimeChart.updateSeries(this.series_v1, false, true);
        // this.series_v1[0].data = this.students_segs[this.view_period][1];
        // this.series_v1[0].labels = this.students_segs[this.view_period][0];
        // this.series_v1[1].data = this.teacher_segs[this.view_period][1];
        // this.series_v1[1].labels = this.teacher_segs[this.view_period][0];
        console.log(this.series_v1_s);//
        console.log(this.series_v1_t);//

        // var chart = new ApexCharts(document.querySelector("#chart_v1"), this.chartOptions_v1);
        // chart.render();

      }
      // updateChart() {
      //   const max = 90;
      //   const min = 20;
      //   const newData = this.series_v1[0].data.map(() => {
      //     return Math.floor(Math.random() * (max - min + 1)) + min
      //   })
      //   // In the same way, update the series option
      //   this.series_v1 = [{
      //     data: newData
      //   }];

      // }
    },
    beforeCreate(){


      // var categories = [];
      // for(var i = 0, len = num_keywords; i < len; i++){
      //   var j = i+1;
      //   categories.push("Keyword #"+j);
      // }
      // this.chartOptions_v1 = {
      //  xaxis: {
      //    categories: categories
      //  }
      // }
      // console.log(this.chartOptions_v1.xaxis.categories);
    },

    created(){
      // console.log("Session ID: "+this.$globals.sessionId);
      // this.analyses_res = this.$globals.analyses_res;


      this.analyses_res = this.$route.params.analyses_res;

      this.students_segs = this.analyses_res.S;
      this.teacher_segs = this.analyses_res.T;
      var num_periods = this.analyses_res.config.num_periods;
      var num_keywords =  this.analyses_res.config.num_keywords;
      this.periods = Object.keys(this.students_segs); // TODO: assuming both sides have the same number of periods, even with empty keyword data
      this.view_period = this.periods[0]; // use timestamp in seconds as index
      this.updateViz();
      // console.log(this.periods);      
      // console.log(this.students_segs[this.view_period]);
      // console.log(num_periods);
      // console.log(this.series_v1_s);
      // var cell_color = {'T':'primary','S':'success'};
      // if (this.preds.hasOwnProperty('preds')) {
      //   let pp = this.preds.preds;
      //   this.n_preds = Object.keys(this.preds.preds).length;
      //   this.n_total_segs = this.n_total_segs + this.n_preds;
      //   for (var idx in pp) {
      //     if (pp[idx]['Pred']=='T') {
      //       this.n_t_segs+=1;
      //     }else{
      //       this.n_s_segs+=1;
      //     }

      //     this.deltas.push(pp[idx]['Delta']);
      //     this.table_items.push({
      //       start_timestamp: pp[idx]['File'],
      //       type: 'Prediction',
      //       delta: pp[idx]['Delta'].toFixed(3),
      //       speaker: pp[idx]['Pred'],
      //       _cellVariants: { speaker: cell_color[pp[idx]['Pred']] }
      //     });
      //   }
      // }
      // console.log(this.table_items);
      // console.log(this.deltas);
      // console.log(this.n_total_segs);

    },

    mounted(){


    },

    data () {
        return {
          analyses_res:null,
          students_segs:[],
          teacher_segs:[],
          selectedVideo:null,
          // table_items:null,
          periods:[], // available periods
          view_period:null, // the period that is currently displayed
          selected_kw: null, // the keyword selected to display details
          // teacher_keywords:[],
          // students_keywords: [],
          series_v1_s: [{
            name: 'Students',
            data: [], // scores
            // data: [0.7756799031784363, 0.7756799031784363, 0.7687249135190602, 0.7601013610898208, 0.7585123736110231, 0.7371205633923014, 0.7355330622565307, 0.659436505067051, 0.3424107600809398, 0.31138173371255223, 0.3044788300614989, 0.30056451594067535, 0.26323272356511407, 0.26323272356511407, 0.16905133555086116, 0.12806557992766787, 0.11449109755714651, 0.10832898960079078, 0.0892841109343624, 0.04314630378298711],
          }],
          series_v1_t:[
          {
            name: 'Teacher',
            data: [], // scores
            // data: [0.7756799031784363, 0.7756799031784363, 0.7687249135190602, 0.7601013610898208, 0.7585123736110231, 0.7371205633923014, 0.7355330622565307, 0.659436505067051, 0.3424107600809398, 0.31138173371255223, 0.3044788300614989, 0.30056451594067535, 0.26323272356511407, 0.26323272356511407, 0.16905133555086116, 0.12806557992766787, 0.11449109755714651, 0.10832898960079078, 0.0892841109343624, 0.04314630378298711],
          }
          ],
          chartOptions_v1_s: {
            labels: [], // add for keywords
            chart: {
              type: 'bar',
              height: 440,
              stacked: true,
              events: {
                // click: function(event, chartContext, config) {
                //   // The last parameter config contains additional information like `seriesIndex` and `dataPointIndex` for cartesian charts
                //   console.log(config.config.series[config.dataPointIndex]);
                //   var kd = document.getElementById("kw_detail");
                //     if (this.selected_kw==null){
                //       kd.style.display = 'none';
                //     }else{
                //       kd.style.display = 'block';
                //   }
                // },
                dataPointSelection: function(event, chartContext, config) {
                  console.log(config.dataPointIndex);
                  console.log(config.w.config.labels[0][config.dataPointIndex]);
                  var kd = document.getElementById("kw_detail");
                  var kw = document.getElementById("selected_kw");
                  kw.innerHTML = config.w.config.labels[0][config.dataPointIndex]; // assign the keyword
                  if (kw.innerHTML==null){
                      kd.style.display = 'none';
                    }else{
                      kd.style.display = 'block';
                  }
                  // other things follows
                }
              }
            },
            colors: [ '#FF4560'],
            plotOptions: {
              bar: {
                horizontal: true,
                barHeight: '80%',
              },
            },
            dataLabels: {
              enabled: true,
              textAnchor: 'start',
              style: {
                  colors: ['#fff']
              },
              offsetX: 0,
              formatter: function (val, opt) {
                // console.log(opt.w.config.series[opt.seriesIndex]);
                return opt.w.config.labels[opt.seriesIndex][opt.dataPointIndex] + ":  " + Math.abs(Math.round(val* 100) / 100)
              },
            },
            stroke: {
              width: 1,
              colors: ["#fff"]
            },
            
            grid: {
              xaxis: {
                lines: {
                  show: false
                }
              }
            },
            yaxis: {
              title: {
                text: 'Keywords',
              },

              labels: {
                show: false
              }
            },
            tooltip: {
              theme: "dark",
              x: {
                  formatter: function (val, opt) {
                    return opt.w.config.labels[opt.seriesIndex][opt.dataPointIndex]
                }
              },
              y: {
                title: {
                  formatter: function (val) {
                  return Math.abs(Math.round(val* 100) / 100)
                  }
                }
              }
            },
            title: {
              text: 'Extracted keywords, ranked by the keyword scores (students)',
        align: "center",
        floating: true
            },
            xaxis: {
              categories: ['Keywords'],
              title: {
                text: 'Keyword Score'
              },

              min: 0,
              max: 1,
              labels: {
                formatter: function (val) {
                  return Math.abs(Math.round(val* 100) / 100)//round to 2 decimal
                }
              }
            },
          },
          chartOptions_v1_t: {
            labels: [], // add for keywords
            chart: {
              type: 'bar',
              height: 440,
              stacked: true,
              events: {
              click: function(event, chartContext, config) {
                // The last parameter config contains additional information like `seriesIndex` and `dataPointIndex` for cartesian charts
                console.log('hw');
              }
            }
            },
            colors: ['#008FFB'],
            plotOptions: {
              bar: {
                horizontal: true,
                barHeight: '80%',
              },
            },
            dataLabels: {
              enabled: true,
              textAnchor: 'start',
              style: {
                  colors: ['#fff']
              },
              offsetX: 0,
              formatter: function (val, opt) {
                // console.log(opt.w.config.series[opt.seriesIndex]);
                return opt.w.config.labels[opt.seriesIndex][opt.dataPointIndex] + ":  " + Math.abs(Math.round(val* 100) / 100)
              },
            },
            
            grid: {
              xaxis: {
                lines: {
                  show: false
                }
              }
            },
            yaxis: {
              title: {
                text: 'Keywords',
              },
              labels: {
                show: false
              }
            },
            tooltip: {
              theme: "dark",
              x: {
                  formatter: function (val, opt) {
                    return opt.w.config.labels[opt.seriesIndex][opt.dataPointIndex]
                }
              },
              y: {
                title: {
                  formatter: function (val) {
                  return Math.abs(Math.round(val* 100) / 100)
                  }
                }
              }
              
              // shared: false,
              // x: {
              //   formatter: function (val, opt) {
              //     return opt.w.config.labels[opt.seriesIndex][opt.dataPointIndex]
              //   }
              // },
              // y: {
              //   formatter: function (val) {
              //     return "Keyword score: " + Math.abs(Math.round(val* 100) / 100)
              //   }
              // }
            },
            title: {
              text: 'Extracted keywords, ranked by the keyword scores (teacher)',
        align: "center",
        floating: true
            },
            xaxis: {
              categories: ['Keywords'],
              title: {
                text: 'Keyword Score'
              },

              min: 0,
              max: 1,
              labels: {
                formatter: function (val) {
                  return Math.abs(Math.round(val* 100) / 100)//round to 2 decimal
                }
              }
            },
          },

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