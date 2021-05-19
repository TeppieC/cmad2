import Vue from 'vue';
import Router from 'vue-router';
import Page1 from "@/components/Page1.vue";
import Page0 from "@/components/Page0.vue";
import Page2 from "@/components/Page2.vue";
import Page3 from "@/components/Page3.vue";
import Page4 from "@/components/Page4.vue";
import Page5 from "@/components/Page5.vue";
import Page6 from "@/components/Page6.vue";

Vue.use(Router);

export default new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
  {
   path: '/',
   name: 'Welcome',
   component: Page0
  },
  { path: '/page0', name:'Welcome', component: Page0 },
  { path: '/page1', name:'Annotation', component: Page1 },
  { path: '/page2', name:'Preview', component: Page2 },
  { path: '/page3', name:'Adjustment', component: Page3 },
  { path: '/page4', name:'Review', component: Page4 },
  { path: '/page5', name:'Analysis configuration', component: Page5 },
  { path: '/page6', name:'Analysis dashboard', component: Page6 }
],
});
