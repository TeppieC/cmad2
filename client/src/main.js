import Vue from 'vue'
import App from './App.vue'
import VueCoreVideoPlayer from 'vue-core-video-player'
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import router from './router';
import UUID from "vue-uuid";
import HistogramSlider from 'vue-histogram-slider';
import 'vue-histogram-slider/dist/histogram-slider.css';
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import { uuid } from "vue-uuid";

Vue.use(UUID);
Vue.use(BootstrapVue)
Vue.use(IconsPlugin)
Vue.use(VueCoreVideoPlayer)
Vue.prototype.$globals = Vue.observable({
  file: null ,
  // ASSET_URL: 'http://127.0.0.1:5000/uploads/',
  // API_URL: 'http://127.0.0.1:5000',
  // sessionId: uuid.v1(),
  // userId: uuid.v4()
  sessionId: null,

  annos: null, // 1st-time annotaions
  preds:null, //// 1st-time prediction results, contain preds, annos, and stats
  pred_id:null,

  to_adjust:null, // list of indices/timestamps (str) which the user chose to adjust
  annos_and_preds:null, // an annotation file combined with the previous annotations and 1st-time predictions, for display uses in page 3

  adjustments:null, // 2nd-time annotations
  adjusted_preds:null, // 2nd-time prediction results, contain preds, annos, and stats
  adjusted_pred_id:null,
  // domain:"/uploads/"
  // analyses_res:null
});


new Vue({    
  router,
  render: h => h(App),
}).$mount('#app')