<!--
  - # **********************************************************************
  - # Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
  - #
  - # All Rights Reserved.
  - # For any other permission, please contact the Legal Office at JHU/APL.
  -
  - # Licensed under the Apache License, Version 2.0 (the "License");
  - # you may not use this file except in compliance with the License.
  - # You may obtain a copy of the License at
  -
  - #    http://www.apache.org/licenses/LICENSE-2.0
  -
  - # Unless required by applicable law or agreed to in writing, software
  - # distributed under the License is distributed on an "AS IS" BASIS,
  - # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - # See the License for the specific language governing permissions and
  - # limitations under the License.
  - # **********************************************************************
  -->

<template>
  <div class="Results">
    <div class="row">
      <div class="col-md-12 " style="padding:10px !important">
        <div v-if="jobData && type" class="row">
          <div class="col-md-12">
            <h2>Title: {{jobData.jobTitle}}</h2>
          </div>
          <div class="col-md-6">
            <h2>Created Datetime: {{jobData.started_datetime}}</h2>
          </div>
          <div class="col-md-6">
            <h2>Updated Datetime: {{jobData.updated_datetime}}</h2>
          </div>
          <div :class="(type == '1') ? 'col-md-4' : 'col-md-6'">
            <h2 style="text-decoration: underline">Type</h2>
            <h2>{{jobData.type == 1 ? 'Simulated' : 'Real Read'}}</h2>
          </div>
          <div :class="(type == '1') ? 'col-md-4' : 'col-md-6'">
            <h2 style="text-decoration: underline">Classifier(s)</h2>
            <h2>{{jobData.classifiers}}</h2>
          </div>
          <div v-if="type == 1" :class="(type == '1') ? 'col-md-4' : 'col-md-6'">
            <h2 style="text-decoration: underline">Read Type(s)</h2>
            <h2>{{jobData.read_types.join(",")}}</h2>
          </div>
        </div>
        <br>

        <div>
          <b-tabs v-model="tab" content-class="mt-3" style="" align="center">

            <b-tab title="Metrics">
              <div class="row" style="padding-bottom: 50px">
                <div class="col-md-6 offset-4"
                     style="display:flex; padding-right: 50px; vertical-align:center; text-align:right">
                  <multiselect :class="{hiddenField: hideFAQ }" v-model="faqQuestion" :options="faqQuestions"
                               style="padding:0px; margin-right:20px;"
                               :searchable="false" id="faqDropdown" :close-on-select="true" label="desc" track-by="key"
                               :show-labels="false" placeholder="Quick Answers">
                  </multiselect>
                  <b-button variant="outline-dark" @click="hideFAQ = !hideFAQ">
                    <font-awesome-icon v-if="hideFAQ" style="line-height: inherit" icon="minus-circle" size="sm"/>
                    <font-awesome-icon v-if="!hideFAQ" style="line-height: inherit" icon="eye-slash" size="sm"/>
                  </b-button>

                </div>
                <div class="col-md-2" style="padding-right: 50px">
                  <multiselect v-model="chartType" :options="chartTypes" style="padding:0px; margin:0px;"
                               :searchable="true" :close-on-select="true" label="name" track-by="key"
                               :show-labels="false" placeholder="Pick a value">
                  </multiselect>
                </div>
              </div>
              <div class="row" id="metricsContainer">
                <div v-bind:class="[ type == 1 ? 'col-md-12' : 'col-md-12' ]"
                     style="padding-right: 20px; padding-left: 20px" v-if="chartType">
                  <b-row>
                    <div
                      v-if="type === 1 && taxes.length > 0 && chartData.length > 0 &&  read_types.length > 0  && !(compareQuery) && chartType.key === 'grouped'"
                      class="chartArea col-md-12">
                      <div class="row">
                        <div class="col-md-5">
                          <Heatmap
                            :chartData="chartData"
                            :containerHeight="0.65 * height"
                            :taxes="taxes"
                            :classifiers="classifiers"
                            :read_types="read_types"
                            :type="type"
                          >
                          </Heatmap>
                        </div>
                        <div class="col-md-7">
                          <GroupedChart
                            :chartData="chartData"
                            :taxes="taxes"
                            :containerHeight="0.5 * height"
                            :classifiers="classifiers"
                            :read_types="read_types"
                            :sortByRoot="sortByRoot"
                            :searchByRoot="searchByRoot"
                            :tabRoot="tabRoot"
                            :chartType="chartType"
                            v-on:updateChildTab="updateChildTab($event, 'grouped')"
                          >
                          </GroupedChart>
                        </div>
                      </div>
                    </div>
                    <div v-if="!(inclusionQuery) &&  chartType.key === 'inclusion'" class="chartArea">
                      <Inclusion
                        :inclusionData="inclusionData"
                        :chartType="chartType"
                        :containerHeight="0.6 * height"
                        :type="type"
                        :inclusionSearchByRoot="inclusionSearchByRoot"
                        :inclusionSortByRoot="inclusionSortByRoot"
                        :baseline="baselineTaxids"
                        :tabInclusion='tabInclusion'
                        v-on:updateChildTab="updateChildTab($event, 'inclusion')"
                      >
                      </Inclusion>
                    </div>
                    <div v-if="!(resourcesQuery) &&  chartType.key === 'resources'" class="chartArea">
                      <Resources
                        :resourcesData="resourcesData"
                        :chartType="chartType"
                        :containerHeight="0.6 * height"
                        :metrics="metrics"
                        :type="type"
                        :pipelines="pipelines"
                        :resourcesSortByRoot="resourcesSortByRoot"
                      >
                      </Resources>
                    </div>
                  </b-row>
                </div>
              </div>
            </b-tab>
            <b-tab :disabled="!readySunburst" :title="readySunburst ? 'Abundance' : 'Calculating Abundance...' "
                   id="sunburstTab"
                   v-if="(!(classifierAbuQuery))">

              <!-- <b-tab active title="Abundance"> -->

              <div class="row" id="sunburstContainer" style="padding-top: 30px;">
                <div class="col-md-12">
                  <div v-if="classifiers.length > 0 && !(inclusionQuery)">
                    <div class="chartArea" style="margin-left:20px;">
                      <Sunburst
                        :containerHeight="0.96 * height"
                        :classifiers="classifiers"
                        :classifierAbundance="classifierAbundance"
                        :read_types="read_types"
                        :type="type"
                        :parentTab="tab"
                        v-on:renderSunburst="renderSunburst"
                        :baseline="baselineTaxids"
                        :chartType="chartType"
                      >
                      </Sunburst>
                    </div>
                  </div>
                </div>
              </div>
            </b-tab>
          </b-tabs>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<script>
  import JobService from '@/services/JobService'
  import Chart from '@/components/Chart'
  import Heatmap from '@/components/Heatmap'
  import GroupedChart from '@/components/GroupedChart';
  import Resources from '@/components/Resources';
  import Sunburst from '@/components/Sunburst'
  import Inclusion from '@/components/Inclusion';
  import Multiselect from 'vue-multiselect';
  import * as d3 from 'd3'

  export default {
    name: 'Results',
    components: {
      Chart,
      Sunburst,
      Heatmap,
      GroupedChart,
      Inclusion,
      Resources,
      Multiselect,
    },
    data() {
      return {
        chartData: [],
        baselineTaxids: [],
        compareQuery: true,

        resourcesData: [],
        resourcesQuery: true,

        inclusionData: [],
        inclusionQuery: true,

        classifierAbundance: {},
        classifierAbuQuery: true,

        pipelines: ['classification'],
        metrics: ['cpu_time', 'wall_clock_time', 'max_memory_MBs'],
        resources: {
          cpu_time: {classification: [], simulation: []},
          max_memory_MBs: {classification: [], simulation: []},
          wall_clock_time: {classification: [], simulation: []}
        },
        classifiers: [],
        user_id: '',
        chartType: null,
        chartTypes: [],
        jobID: '',
        jobTitle: '',
        job_created_date: '',
        userEmail: '',
        taxes: [],
        read_type: null,
        read_types: [],
        type: null,
        fetchJobErrors: [],
        classifiers_read_types: [],
        readySunburst: false,
        jobData: null,
        sortByRoot: '',
        searchByRoot: '',
        inclusionSortByRoot: '',
        inclusionSearchByRoot: '',
        resourcesSortByRoot: '',
        faqQuestions: [],
        faqQuestion: null,
        tabInclusion: 0,
        tabGrouped: 0,
        tab: 0, //Metrics tab, index of 1 is sunburst abundance
        tabRoot: 1, // Set tab selected for the comparison metrics if available
        hideFAQ: false,
        faqParams: {
          grouped: [
            {
              key: 'maxAUPRC',
              desc: 'Which classifier has the max AUPRC?',
              params: {
                type: 'sort',
                sortDesc: true,
                tab: 0,
                field: 'AUPRC',
                chartType: 'grouped',
                tab: 0
              }
            },
            {
              key: 'maxAUPRC_L2',
              desc: 'Which classifier has the largest ratio of AUPRC/L2?',
              params: {
                type: 'sort',
                sortDesc: true,
                tab: 0,
                field: 'METAVal',
                chartType: 'grouped',
                tab: 0
              }
            },
            {
              key: 'maxL2',
              desc: "Which classifier has the largest L2?",
              params: {
                type: 'sort',
                sortDesc: true,
                tab: 0,
                field: 'L2',
                chartType: 'grouped',
                tab: 0
              }
            },
            {
              key: 'maxSearchAUPRC',
              desc: "Which species and classifier combination has the largest AUPRC?",
              plot: 'Comparison',
              params: {
                type: 'search_and_sort',
                search: 'species',
                sortDesc: true,
                tab: 0,
                field: 'AUPRC',
                chartType: 'grouped',
                tab: 1
              }
            },
            {
              key: 'maxSearchAUPRC_L2',
              desc: "Which superkingdom has the greatest AUPRC/L2?",
              params: {
                type: 'search_and_sort',
                search: 'superkingdom',
                sortDesc: true,
                tab: 0,
                field: 'METAVal',
                chartType: 'grouped',
                tab: 1
              }
            },
            {
              key: 'maxSearchL2',
              desc: "Which species has the highest L2?",
              params: {
                type: 'search_and_sort',
                search: 'species',
                sortDesc: true,
                tab: 0,
                field: 'L2',
                chartType: 'grouped',
                tab: 1
              }
            },
          ],
          inclusion: [
            {
              key: 'inclusionMaxSearchAbu',
              desc: "Which abundance is the greatest for all strains present?",
              params: {
                type: 'search_and_sort_inclusion',
                search: 'strain',
                sortDesc: true,
                tab: 0,
                field: 'abundance',
                chartType: 'inclusion'
              }
            },
            {
              key: 'inclusionMaxSearchClassifier',
              desc: "Which genus has the greatest abundance?",
              params: {
                type: 'search_and_sort_inclusion',
                search: 'genus',
                sortDesc: true,
                tab: 0,
                field: 'classifier',
                chartType: 'inclusion'
              }
            },
          ],
          resources: [
            {
              key: 'resourcesMaxCpu_Time',
              desc: "What classifier took the longest CPU time?",
              params: {
                type: 'sort_resources',
                sortDesc: false,
                tab: 0,
                field: 'cpu_time',
                chartType: 'resources'
              }
            },
            {
              key: 'resourcesMaxWall_Time',
              desc: "Which classifier has the longest wall clock time",
              params: {
                type: 'sort_resources',
                sortDesc: true,
                tab: 0,
                field: 'wall_clock_time',
                chartType: 'resources'
              }
            },
            {
              key: 'resourcesMinMemory',
              desc: "Which classifier uses the least memory?",
              params: {
                type: 'sort_resources',
                sortDesc: false,
                tab: 0,
                field: 'max_memory_MBs',
                chartType: 'resources'
              }
            }
          ]
        }
      }
    },
    watch: {
      chartType(val) {
        if (val){
          this.faqQuestions = this.faqParams[val.key]
          this.faqQuestion = null

        }
      },
      faqQuestion(val) {
        if (val) {
          this.updatePlotsFAQ(val)
        }
      }
    },
    methods: {
      renderSunburst(value) {
        this.readySunburst = value
      },
      updateChartType(val) {
        //Get the index of the chart Types where the chart Type is equal to the param chart Type
        const idx = this.chartTypes.map(function (e) {
          return e.key;
        }).indexOf(val);
        this.chartType = this.chartTypes[idx]
      },
      updateChildTab(val, child) {
        if (child == 'inclusion') {
          this.tabInclusion = val
        } else {
          this.tabRoot = val
        }
      },

      updatePlotsFAQ(faqParams) {
        //Get the index of the chart Types where the chart Type is equal to the param chart Type
        const idx = this.chartTypes.map(function (e) {
          return e.key;
        }).indexOf(faqParams.params.chartType);
        this.chartType = this.chartTypes[idx]
        if (faqParams.params.type == 'sort') {
          this.sortByRoot = faqParams.params.field
          this.tabRoot = faqParams.params.tab
        } else if (faqParams.params.type == 'search') {
          this.searchByRoot = faqParams.params.search
          this.tabRoot = faqParams.params.tab
        } else if (faqParams.params.type == 'search_and_sort') {
          this.sortByRoot = faqParams.params.field
          this.searchByRoot = faqParams.params.search
          this.tabRoot = faqParams.params.tab
        } else if (faqParams.params.type == 'search_and_sort_inclusion') {
          this.inclusionSortByRoot = faqParams.params.field
          this.inclusionSearchByRoot = faqParams.params.search
          this.tabInclusion = 0
        } else if (faqParams.params.type == 'sort_resources') {
          this.resourcesSortByRoot = {text: faqParams.params.field, sortDirection: faqParams.params.sortDesc}
        }
      },
      calculateMetaVal(AUPRC, L2){
        return (((AUPRC+1)/((L2/Math.pow(2, 1/2))+1))-0.5)/1.5
      },
      async fetchCompare(read_type) {
        const $this = this
        return new Promise(function (resolve, reject) {
          try {
            JobService.getJobResults({
              id: $this.$route.params.id,
              read_type: read_type
            }).then((response) => {
              const data = response.data
              for (var i = 0; i < data.length; i++) {
                data[i].classifier_name = data[i].classifier_name.replace("_dir", "")
                $this.classifiers_read_types.indexOf(response.data[i].classifier_name + " - " + read_type) == -1 ? $this.classifiers_read_types.push(response.data[i].classifier_name.replace("_dir", "") + " - " + read_type) : '';
                data[i].combined = data[i].rank + " - " + data[i].classifier_name + " - " + read_type
                data[i].read_type = read_type
                data[i].index = i
                data[i].METAVal = $this.calculateMetaVal(data[i].AUPRC, data[i].L2)
                $this.chartData.push(data[i])
              }
              resolve()
            }).catch((err) => {
              console.error(err.message, "error at gathering compare metrics results for read type: " + read_type)
              resolve()
              $this.fetchJobErrors.push(($this.type == 1 ? read_type : 'Real'))
            })
          } catch (error) {
            $this.fetchJobErrors.push(($this.type == 1 ? read_type : 'Real'))
            console.error(error)
          }
        });
      },
      async fetchInclusion(params) {
        const $this = this
        return new Promise(function (resolve, reject) {
          try {
            let read_type = (params.read_type ? params.read_type : null);
            JobService.fetchInclusion({
              id: params.id,
              read_type: read_type
            }).then((response) => {
              const data = response.data
              for (var i = 0; i < data.length; i++) {
                params.read_type ? data[i].read_type = read_type : null;
                data[i].ratio = 0
                $this.inclusionData.push(data[i])
                const classifier = data[i].classifier
                const taxid = data[i].taxid
                read_type = (read_type ? read_type : "real");
                if (!$this.classifierAbundance.hasOwnProperty(read_type)) {
                  $this.classifierAbundance[read_type] = {}
                }
                if (!$this.classifierAbundance[read_type].hasOwnProperty(classifier)) {
                  $this.classifierAbundance[read_type][classifier] = {}
                }
                $this.classifierAbundance[read_type][classifier][data[i].taxid] = data[i]
              }
              resolve()
            }).catch((err) => {
              console.error(err.message, "error at gathering inclusion metrics results for read type: " + params.read_type)
              resolve()
              $this.fetchJobErrors.push(($this.type == 1 ? params.read_type : 'Real'))
            })
          } catch (error) {
            $this.fetchJobErrors.push(($this.type == 1 ? params.read_type : 'Real'))
            console.error(error)
          }
        });
      },
      async fetchOriginalAbu() {
        if (this.type == 1) {
          try {
            await JobService.fetchAbuTSV({
              id: this.$route.params.id
            })
              .then((response) => {
                this.baselineTaxids = response.data.map((d) => {
                  return d.taxid
                })
              })
          } catch (err) {
            console.error(err.message, "error in gaining original baseline abu file")
            this.$swal.fire({
              position: 'center',
              icon: 'error',
              showConfirmButton: true,
              title: "There was an error gathering the original baseline abu tax file"
            })
          }
        }
      },
      async fetchMetric(param, metrics) {
        const $this = this
        const obj = this.resourcesData
        const params = param
        const pipeline = params.pipeline
        const read_type = params.read_type
        const metric = params.metric
        const id = params.id
        const classifier = params.classifier
        let cpu_time, max_memory_MBs, wall_clock_time;
        return new Promise(function (resolve, reject) {
          try {
            (async () => {
              await JobService.fetchMetrics({
                pipeline: pipeline,
                read_type: read_type,
                metric: 'cpu_time',
                id: id,
                classifier: classifier
              }).then((response) => {
                cpu_time = parseFloat(response.data.cpu_time)
              }).catch((error) => {
                console.error(error)
              })
              await JobService.fetchMetrics({
                pipeline: pipeline,
                read_type: read_type,
                metric: 'wall_clock_time',
                id: id,
                classifier: classifier
              }).then((response) => {
                wall_clock_time = parseFloat(response.data.wall_clock_time)
              }).catch((error) => {
                console.error(error)
              })
              await JobService.fetchMetrics({
                pipeline: pipeline,
                read_type: read_type,
                metric: 'max_memory_MBs',
                id: id,
                classifier: classifier
              }).then((response) => {
                max_memory_MBs = parseFloat(response.data.max_memory_MBs)
              }).catch((error) => {
                console.error(error)
              })
              $this.resourcesData.push({
                cpu_time: cpu_time,
                wall_clock_time: wall_clock_time,
                max_memory_MBs: max_memory_MBs,
                read_type: read_type,
                classifier: classifier
              })
              resolve()
            })()
          } catch (err) {
            console.error(err)
            reject(err)
          }

        })
      },

      async getJobResults() {
        const read_types = this.read_types
        let promises = [];
        let errorPromises = [];
        const length = (this.type == 1 ? this.read_types.length : 1);


        await this.fetchOriginalAbu()

        for (let k = 0; k < length; k++) {
          try {
            const id = this.$route.params.id;
            const params = {
              id: id,
              read_type: (this.type == 1 ? this.read_types[k] : null),
            }
            promises.push(this.fetchInclusion(params))
          } catch (err) {
            console.error(err.message, "error in gaining inclusion information")
            this.$swal.fire({
              position: 'center',
              icon: 'error',
              showConfirmButton: true,
              title: "There was an error gathering the inclusion metrics for your job"
            })
          }
        }
        this.fetchJobErrors = [];
        Promise.all(promises)
          .then((response) => {
            if (this.fetchJobErrors.length > 0) {
              this.$swal.fire({
                position: 'center',
                icon: 'warning',
                showConfirmButton: true,
                title: "There was an error gathering the inclusion metrics for jobs: " + this.fetchJobErrors.join("; ")
              })
            }
            this.inclusionQuery = false;
            const classifiers = d3.map(this.inclusionData, (d) => {
              return d.classifier
            }).keys()
            this.inclusionData.forEach((d) => {
              const classifiers_without = d.classifier_inclusion.filter((d)=>{return d !== 'BASELINE1.tsv'})
              d.ratio = (classifiers_without.length) / this.classifiers.length
            })
            this.classifierAbuQuery = false;

          })
          .catch((e) => {
            console.error("error", e)
            this.inclusionQuery = false;
            this.classifierAbuQuery = false;
          });

        promises = []
        this.fetchJobErrors = [];
        if (this.type === 1) {
          for (let i = 0; i < length; i++) {
            promises.push(this.fetchCompare(read_types[i]));
          }
          Promise.all(promises)
            .then(() => {
              const taxes = this.chartData.map(function (d) {
                return d.rank
              })
              let dist_taxes = [...new Set(taxes.map(x => x))];
              dist_taxes = dist_taxes.map(function (d) {
                return {"name": d}
              })
              this.taxes = dist_taxes
              this.compareQuery = false;

              if (this.fetchJobErrors.length > 0) {
                this.$swal.fire({
                  position: 'center',
                  icon: 'warning',
                  showConfirmButton: true,
                  title: "There was an error gathering the comparison metrics for jobs: " + this.fetchJobErrors.join("; ")
                })
              }
            })
            .catch((e) => {
              console.error("error", e)
            });
        }


        this.jobID = this.$route.params.id
        // this.user_id = this.$route.params.user_id;
        promises = [];
        for (let k = 0; k < length; k++) {
          try {

            const id = this.$route.params.id;
            const metrics = this.metrics
            const pipelines = this.pipelines
            const params = {
              id: id,
              read_type: (this.type == 1 ? this.read_types[k] : null),
              metric: null,
              classifier: null,
              pipeline: null
            }
            for (let i = 0; i < this.classifiers.length; i++) {
              for (let k = 0; k < pipelines.length; k++) {
                pipelines[k] == 'classification' ? params.classifier = this.classifiers[i] : params.classifier = null;
                params.pipeline = pipelines[k]
                promises.push(this.fetchMetric(params, metrics))
              }
            }
          } catch (err) {
            console.error(err.message, "error in gaining metrics information")
            this.$swal.fire({
              position: 'center',
              icon: 'error',
              showConfirmButton: true,
              title: "There was an error gathering the resources metrics for your job"
            })
          }
        }
        Promise.all(promises)
          .then((response) => {
            this.resourcesQuery = false;
            if (this.fetchJobErrors.length > 0) {
              this.$swal.fire({
                position: 'center',
                icon: 'warning',
                showConfirmButton: true,
                title: "There was an error gathering the resources metrics for jobs: " + this.fetchJobErrors.join("; ")
              })
            }

          })
          .catch((e) => {
            console.error("error", e)
            this.resourcesQuery = false;
          });


      },
      async displayResults() {
        this.chartData = []
        this.getJobResults()
      },
    },
    mounted() {
      this.jobData = this.$store.state.jobData
      this.height = window.innerHeight
      this.width = window.innerWidth
      this.read_types = this.$store.state.jobData.read_types
      if (this.read_types.length > 0 && this.read_types) {
        this.read_type = this.read_types[0]
      }
      this.classifiers = this.$store.state.jobData.classifiers.split(", ")
      this.type = this.$store.state.jobData.type

      this.chartTypes = (this.type === 1 ? [{name: 'Comparison Metrics', key: 'grouped'}, {
        name: 'Inclusion Metrics',
        key: 'inclusion'
      }, {name: 'Resource Metrics', key: 'resources'}] : [{
        name: 'Inclusion Metrics',
        key: 'inclusion'
      }, {name: 'Resource Metrics', key: 'resources'}])
      this.chartType = this.chartTypes[0]
      this.jobID = this.$route.params.id

      this.getJobResults()
    },
  };
</script>
<style>
  .chartArea {
    width: 100%;
  }

  hr {
    border-top: 2px dashed #232B2B;
  }

  h1, h2 {
    font-size: 20px;
  }

  .Results {
    padding-right: 40px;
    padding-left: 40px;
  }

  .tabAccordion {
    background: #0c5460;
  }

  .faqButton {
    background: #333333;
    color: #fff;
    width: 100%;
  }

  .fa-minus-circle, .fa-eye-slash {
    margin: auto;
    vertical-align: middle
  }

  .hiddenField {
    opacity: 0;
  }
</style>
