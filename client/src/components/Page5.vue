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
          <strong>Video:</strong> {{ this.selectedVideo }} <br>
        </p>
      </b-row>
      <hr class="my-4">

      <div>
        <b-card no-body>
          <b-tabs card>
            <b-tab title="Procedure 1" active>
              <b-form v-on:submit.prevent="onSubmitP1" v-if="show">
<!--                 <b-form-group id="input-group-0" label="Analysis procedure:" label-for="input-0">
                  <b-form-radio-group
                    id="input-0"
                    v-model="selectedmode"
                    :options="modes"
                    class="mb-3"
                    value-field="item"
                    text-field="name"
                    disabled-field="notEnabled"
                  ></b-form-radio-group>
                </b-form-group>
 -->

                <b-form-group id="input-group-1" label="Stopwords (words that should not be considered):" label-for="input-1">
                  <b-form-textarea
                    id="input-1"
                    v-model="stopwords"
                    rows="3"
                    max-rows="100"
                  ></b-form-textarea>
                </b-form-group>

                <b-form-group id="input-group-2" label="Desired time interval (s):" label-for="input-2">
                  <b-form-input
                    id="input-2"
                    v-model="timeinterval"
                  ></b-form-input>
                </b-form-group>


                <b-form-group id="input-group-3" label="Number of keywords:" label-for="input-3">
                  <b-form-spinbutton 
                    id="input-3" 
                    v-model="numkeyword" 
                    min="1" 
                    max="100">
                  </b-form-spinbutton>
                </b-form-group>



                <b-button type="submit"  variant="success">Submit</b-button>
              </b-form>
            </b-tab>


            <b-tab title="Procedure 2">
              <b-form v-on:submit.prevent="onSubmitP2" v-if="show">
<!--                 <b-form-group id="input-group-0" label="Analysis procedure:" label-for="input-0">
                  <b-form-radio-group
                    id="input-0"
                    v-model="selectedmode"
                    :options="modes"
                    class="mb-3"
                    value-field="item"
                    text-field="name"
                    disabled-field="notEnabled"
                  ></b-form-radio-group>
                </b-form-group>
 -->

                <b-form-group id="input-group-1" label="Stopwords (words that should not be considered):" label-for="input-1">
                  <b-form-textarea
                    id="input-1"
                    v-model="stopwords"
                    rows="3"
                    max-rows="100"
                  ></b-form-textarea>
                </b-form-group>

                <b-form-group id="input-group-2" label="Desired time interval (s):" label-for="input-2">
                  <b-form-input
                    id="input-2"
                    v-model="timeinterval"
                    placeholder="Time interval"
                  ></b-form-input>
                </b-form-group>


                <b-form-group id="input-group-3" label="Number of keywords:" label-for="input-3">
                  <b-form-spinbutton 
                    id="input-3" 
                    v-model="numkeyword" 
                    min="1" 
                    max="100">
                  </b-form-spinbutton>
                </b-form-group>

                <b-form-group
                  label="Accepted POS tags"
                  v-slot="{ ariaDescribedby }"
                >
                <b-form-checkbox-group
                    v-model="selectedpostags"
                    :options="postags"
                    :aria-describedby="ariaDescribedby"
                    name="flavour-1a"
                  ></b-form-checkbox-group>
                </b-form-group>

                <b-button type="submit"  variant="success">Submit</b-button>
              </b-form>
            </b-tab>

            <b-tab title="Procedure 3">
              <b-form v-on:submit.prevent="onSubmitP3" v-if="show">
<!--                 <b-form-group id="input-group-0" label="Analysis procedure:" label-for="input-0">
                  <b-form-radio-group
                    id="input-0"
                    v-model="selectedmode"
                    :options="modes"
                    class="mb-3"
                    value-field="item"
                    text-field="name"
                    disabled-field="notEnabled"
                  ></b-form-radio-group>
                </b-form-group>
 -->

                <b-form-group id="input-group-1" label="Stopwords (words that should not be considered):" label-for="input-1">
                  <b-form-textarea
                    id="input-1"
                    v-model="stopwords"
                    placeholder="sometimes, much, other, whereas, don, also, name, a, mill, find, now, it, see, get, many, without, seeming, against, again, several, am, their, couldnt, doesn, an, ltd, nobody, look, behind, uh, amongst, enough, everywhere, must, us, keep, interest, than, was, co, will, has, me, where, above, down, any, eleven, hers, don't, below, please, at, you, does, very, out, by, would, his, yep, un, were, both, ever, part, back, yourself, beyond, made, however, since, these, serious, together, either, around, every, along, somewhere, ours, moreover, while, wouldn, therein, first, cannot, which, all, didn, whose, whoever, well, anyhow, becomes, them, sincere, through, indeed, anywhere, formerly, before, use, last, our, after, because, then, is, what, until, during, go, afterwards, elsewhere, been, had, if, de, she, within, as, whom, cry, and, some, how, thus, already, ok, nowhere, so, seem, him, um, thanks, he, put, one, of, didn't, anything, won, the, each, re, themselves, that, etc, too, no, who, least, under, call, being, few, yours, hereafter, into, second, they, have, eh, move, to, can, thereby, beside, among, alone, could, whence, might, front, upon, herself, your, namely, whereupon, everything, only, whereby, rather, never, her, yourselves, more, another, hasnt, always, take, may, third, mine, with, found, top, former, meanwhile, but, neither, whether, said, here, such, con, seemed, do, give, becoming, inc, whenever, ourselves, although, everyone, whole, my, anyway, throughout, same, others, beforehand, on, hereby, wherein, onto, someone, for, next, myself, yet, per, are, be, okay, yes, this, due, whereafter, over, say, latterly, inaudible, almost, noone, able, need, nothing, not, when, thence, we, seems, besides, amoungst, its, whither, became, none, across, ll, though, ya, did, or, nevertheless, once, herein, bit, thank, perhaps, ie, up, towards, mostly, thereafter, eg, wherever, off, therefore, except, still, hereupon, often, there, yeah, i, latter, between, own, hence, try, toward, just, himself, should, thereupon, forty, amount, somehow, sometime, from, else, done, thru, most, about, less, otherwise, whatever, nor, eight, in, something, those, why, via, itself, become, anyone, fill, cant, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0"
                    rows="3"
                    max-rows="100"
                  ></b-form-textarea>
                </b-form-group>

                <b-form-group id="input-group-2" label="Desired time interval (s):" label-for="input-2">
                  <b-form-input
                    id="input-2"
                    v-model="timeinterval"
                    placeholder="Time interval"
                  ></b-form-input>
                </b-form-group>


                <b-form-group id="input-group-3" label="Number of keywords:" label-for="input-3">
                  <b-form-spinbutton 
                    id="input-3" 
                    v-model="numkeyword" 
                    min="1" 
                    max="100">
                  </b-form-spinbutton>
                </b-form-group>

                <b-form-group
                  label="Accepted POS tags"
                  v-slot="{ ariaDescribedby }"
                >
                <b-form-checkbox-group
                    v-model="selectedpostags"
                    :options="postags"
                    :aria-describedby="ariaDescribedby"
                    name="flavour-1a"
                  ></b-form-checkbox-group>
                </b-form-group>

                <b-button type="submit"  variant="success">Submit</b-button>
              </b-form>
            </b-tab>


          </b-tabs>
        </b-card>
      </div>
        
<!--       <b-row align-h="center" class="my-4">
          <b-button type="button" class="cbuttons" @click="onSubmit()" variant="success">Go</b-button>
      </b-row> -->
    </b-container>


    </div>
</template>

<script>
import axios from 'axios';
import Vue from 'vue'
//import * as d3 from 'd3'
// import Trend from "vuetrend"
// Vue.use(Trend)


export default {
    name: 'Page5',
    
    components: {
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
      onSubmitP1(){
        const info = {
            sessionId: this.$globals.sessionId,
            filename: this.$globals.file,
            stopwords: this.stopwords,
            interval: this.timeinterval,
            numOfKeywords: this.numkeyword
        };
        console.log(info);
        const path = 'http://localhost:5000/api/p1analyses';
                  axios.post(path, info)
                    .then((res) => { 
                        console.log("[Page 5] Analyses done");
                        // this.$globals.analyses_res = res.data.result; 
                        // console.log(res.data.result);

                        this.switch2Tab(6);
                        this.$router.push({name:'Analysis dashboard',params:{ analyses_res: res.data.result }});
                    })
                    .catch((error) => {
                      // eslint-disable-next-line
                      console.log(error);
                      // this.getBooks();
                    });
      },
      onSubmitP2(){
        const info = {
            sessionId: this.$globals.sessionId,
            filename: this.$globals.file
        };
        const path = 'http://localhost:5000/api/p1analyses';
                  axios.post(path, info)
                    .then((res) => { 
                        console.log("[Page 5] Analyses done");
                        this.$globals.analyses_res = res.data.result;
                        // console.log(res.data.result);

                        this.switch2Tab(6);
                        this.$router.push('/Page6');
                    })
                    .catch((error) => {
                      // eslint-disable-next-line
                      console.log(error);
                      // this.getBooks();
                    });
      },
      onSubmitP3(){
        const info = {
            sessionId: this.$globals.sessionId,
            filename: this.$globals.file
        };
        const path = 'http://localhost:5000/api/p1analyses';
                  axios.post(path, info)
                    .then((res) => { 
                        console.log("[Page 5] Analyses done");
                        this.$globals.analyses_res = res.data.result;
                        // console.log(res.data.result);

                        this.switch2Tab(6);
                        this.$router.push('/Page6');
                    })
                    .catch((error) => {
                      // eslint-disable-next-line
                      console.log(error);
                      // this.getBooks();
                    });
      }

    },

    created(){
      console.log("Session ID: "+this.$globals.sessionId);

      
    },

    mounted(){


    },

    data () {
        return {
            selectedVideo: this.$globals.file,
            sessionId: null,
            show: true,
            timeinterval:300,
            numkeyword:20,

            stopwords:"sometimes, much, other, whereas, don, also, name, a, mill, find, now, it, see, get, many, without, seeming, against, again, several, am, their, couldnt, doesn, an, ltd, nobody, look, behind, uh, amongst, enough, everywhere, must, us, keep, interest, than, was, co, will, has, me, where, above, down, any, eleven, hers, don't, below, please, at, you, does, very, out, by, would, his, yep, un, were, both, ever, part, back, yourself, beyond, made, however, since, these, serious, together, either, around, every, along, somewhere, ours, moreover, while, wouldn, therein, first, cannot, which, all, didn, whose, whoever, well, anyhow, becomes, them, sincere, through, indeed, anywhere, formerly, before, use, last, our, after, because, then, is, what, until, during, go, afterwards, elsewhere, been, had, if, de, she, within, as, whom, cry, and, some, how, thus, already, ok, nowhere, so, seem, him, um, thanks, he, put, one, of, didn't, anything, won, the, each, re, themselves, that, etc, too, no, who, least, under, call, being, few, yours, hereafter, into, second, they, have, eh, move, to, can, thereby, beside, among, alone, could, whence, might, front, upon, herself, your, namely, whereupon, everything, only, whereby, rather, never, her, yourselves, more, another, hasnt, always, take, may, third, mine, with, found, top, former, meanwhile, but, neither, whether, said, here, such, con, seemed, do, give, becoming, inc, whenever, ourselves, although, everyone, whole, my, anyway, throughout, same, others, beforehand, on, hereby, wherein, onto, someone, for, next, myself, yet, per, are, be, okay, yes, this, due, whereafter, over, say, latterly, inaudible, almost, noone, able, need, nothing, not, when, thence, we, seems, besides, amoungst, its, whither, became, none, across, ll, though, ya, did, or, nevertheless, once, herein, bit, thank, perhaps, ie, up, towards, mostly, thereafter, eg, wherever, off, therefore, except, still, hereupon, often, there, yeah, i, latter, between, own, hence, try, toward, just, himself, should, thereupon, forty, amount, somehow, sometime, from, else, done, thru, most, about, less, otherwise, whatever, nor, eight, in, something, those, why, via, itself, become, anyone, fill, cant, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0",
            selectedmode:'',/// not in use
            modes: [
              { item: 'A', name: 'Proc A' },
              { item: 'B', name: 'Proc B' },
              { item: 'D', name: 'Proc C'}
            ],
            selectedpostags:[],
            postags: [
              { text: 'Verb', value: 'verb' },
              { text: 'Noun', value: 'noun' },
              { text: 'Adjective', value: 'adj' },
              { text: 'Adverb', value: 'adv' },
              { text: 'All words', value: 'all' }
            ]

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