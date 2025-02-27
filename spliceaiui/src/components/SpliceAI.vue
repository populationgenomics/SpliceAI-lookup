<template>
  <b-container>

      <section class="mt-3">

          <b-card
            title="SpliceAI scores lookup"
            class="mb-2"
          >
          <b-form @submit="onSubmit">

            <b-row>
              <b-col cols="10">

                <b-form-group
                  label-cols-sm="2"
                  label-size="sm"
                  label="HGVSc Input"
                  label-for="hgvsc"
                >
                  <b-form-input required v-model="input" id="hgvsc"></b-form-input>
                </b-form-group>

                <b-form-group
                  label-cols-sm="2"
                  label-size="sm"
                  label="Distance to scan"
                  label-for="scan_distance"
                >
                  <b-form-select required v-model="selected_scan_distance" id="scan_distance" :options="scan_distance_options"></b-form-select>
                </b-form-group>

              </b-col>

              <b-col>
                <b-button type="submit" variant="primary"><b-spinner small v-bind:type="spinner_state"></b-spinner> Submit</b-button>
              </b-col>
            
            </b-row>

          </b-form>
        </b-card>
      </section>

      <div>
         <b-alert :show="errored" variant="danger">{{ error_message }}</b-alert>
      </div>

      <section id="results" v-if="loaded">

        <b-row>
          <b-col>

            <b-card no-body>
              <b-tabs card>
                <span v-for="(spliceai, index) in spliceai" :key="index">
                  <b-tab :title="tabformatter(spliceai.gene, spliceai.strand, spliceai.chr, spliceai.pos, spliceai.ref, spliceai.alt)" class="mx-0 px-0">
                    <results
                      :results="spliceai.stats"
                      :pos="spliceai.pos"
                      :strand="spliceai.strand">
                    </results>
                </b-tab>
                </span>
              </b-tabs>
            </b-card>

          </b-col>
        </b-row>

      </section>
  </b-container>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
import VueAxios from 'vue-axios'
import Results from './ResultsTable'

const FormData = require('form-data'); 

Vue.use(VueAxios, axios)
Vue.component("results", Results)

export default {
  name: 'SpliceAI',
  data() {
    return {
      input: null,
      loading: false,
      loaded: false,
      spliceai: null,
      errored: false,
      error_message: null,
      pos: null,
      selected_scan_distance: null,
      scan_distance_options: [
        { value: 50, text: "+/-50" },
        { value: 100, text: "+/-100" },
        { value: 250, text: "+/-250" },
        { value: 500, text: "+/-500" },
        { value: 1000, text: "+/-1000" },
      ]
    }
  },
  props: {
    msg: String
  },
  computed: {
    spinner_state() {
      if (this.loading) {
        return 'grow'
      } else {
        return ''
      }
    }
  },
  methods: {
    tabformatter(gene, strand, chr, pos, ref, alt) {
      return(gene + " (" + strand + ") " + chr + "-" + pos + "-" + ref + "-" + alt)
    },
    onSubmit(evt) {
      evt.preventDefault()
      console.log("Getting predictions for: " + this.input)

      let currentObj = this;
      currentObj.loaded = false
      currentObj.loading = true
      currentObj.errored = false

      this.axios.get(
        "https://rest.ensembl.org/variant_recoder/human/" + this.input + "?content-type=application/json&fields=vcf_string",
        { crossdomain: true }
      ).catch(function(error) {
        if (error.response) {
          currentObj.errored = true
          currentObj.error_message = "Encountered error while calling Ensembl API [" + error.response.data.error + "]"
          currentObj.loading = false
          currentObj.loaded = false
        } else if (error.request) {
          currentObj.errored = true
          currentObj.error_message = "Encountered error while calling Ensembl API [" + error.request + "]"
          currentObj.loading = false
          currentObj.loaded = false
        } else {
          currentObj.errored = true
          currentObj.error_message = "Encountered error while calling Ensembl API [" + error.message + "]"
          currentObj.loading = false
          currentObj.loaded = false
        }
      }).then(function(response) {
        console.log(response.data)

        const form = new FormData()

        let response_data = response.data[0]
        form.append('chrom', response_data[Object.keys(response_data)]['vcf_string'][0].split('-')[0])
        form.append('pos', response_data[Object.keys(response_data)]['vcf_string'][0].split('-')[1])
        form.append('ref', response_data[Object.keys(response_data)]['vcf_string'][0].split('-')[2])
        form.append('alt', response_data[Object.keys(response_data)]['vcf_string'][0].split('-')[3])
        form.append('assembly','grch38')
        form.append('distance', currentObj.selected_scan_distance)
        form.append('mask','0')

        currentObj.pos = response_data[Object.keys(response_data)]['vcf_string'][0].split('-')[1]
      
        currentObj.axios.post('/api/get_variant_assessment',
          form
        ).catch(function(error) {
          console.log("Encountered error while calling SpliceAI API [" + error.message + "]")
          currentObj.errored = true
          currentObj.error_message = "Encountered error while calling SpliceAI API [" + error.message + "]"
          currentObj.loading = false
          currentObj.loaded = false
        }).then(function(response) {
          console.log(response.data)
          currentObj.loading = false
          currentObj.loaded = true
          currentObj.errored = false
          currentObj.spliceai = response.data

        })
      })
    }
  }
}
</script>
