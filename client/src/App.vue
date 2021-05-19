<template>
  <div id="app">

     <div class="top" id="header">
        <div class="title">
<!--             <div class="primary-title">
                <a href="index.html"></a>
                <img src="img/n.png">
                <img src="img/u.png">
                <img class="l" src="img/l1.png">
                <img src="img/l2.png">
            </div> -->
            <div class="sub-title"><h1>C.M.A.D v0.1</h1></div>

            <div class="top-buttons">
                <router-link to="/Page0" @click.native="swtich2Tab(0)">
                  <span class="btn btn-default" style="color:#fff;">
                  1. Get started
                  </span>
                </router-link>

                <router-link to="/Page1" @click.native="swtich2Tab(1)">
                  <span class="btn btn-default" style="color:#fff;">
                  2. Annotate</span>
                </router-link>

                <router-link to="/Page2" @click.native="swtich2Tab(2)">
                  <span class="btn btn-default" style="color:#fff;">
                  3. Preview</span>
                </router-link>

                <router-link to="/Page3" @click.native="swtich2Tab(3)">
                  <span class="btn btn-default" style="color:#fff;">
                  4. Adjustment</span>
                </router-link>

                <router-link to="/Page4" @click.native="swtich2Tab(4)">
                  <span class="btn btn-default" style="color:#fff;">
                  5. Review</span>
                </router-link>
                <router-link to="/Page5" @click.native="swtich2Tab(5)">
                  <span class="btn btn-default" style="color:#fff;">
                  6. Mode select</span>
                </router-link>
                <router-link to="/Page6" @click.native="swtich2Tab(6)">
                  <span class="btn btn-default" style="color:#fff;">
                  7. Dashboard</span>
                </router-link>
            </div>
          </div>
      </div>

      <router-view/>

  </div>
</template>

<script>
  import axios from 'axios';
  import 'bootstrap/dist/css/bootstrap.css';
  import 'bootstrap-vue/dist/bootstrap-vue.css';
  import './style.css'
  export default {
    name: "App",
    methods:{
      swtich2Tab(selected){
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
      }
    }
  }

</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  /*margin-top: 60px;*/
}
</style>
