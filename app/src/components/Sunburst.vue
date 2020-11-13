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
  <div style="padding-top: 10px; width: 97%">
    <div class="row">
      <div class="col-md-2">
        <div class="row">
          <div class="col-md-9">
            <b-row id="legendDiv">
              <div id="legend_text" style="margin:auto;  padding-bottom: 10px">
                <h5>Legend</h5>
                <span id="legend_text_label" style="text-align:center; "/>
                <div v-if="selectedAttribute.name =='Deviation'" class="alert alert-info">
                  <span>Color is Relative to +/- Max Abundance at a Given Rank</span>
                </div>
              </div>
              <hr>
              <div id="legend_wrapper"
                   style="position:relative; background: none; background-opacity: 0.5; width: 100%; max-height: 200px; overflow-y:auto;overflow-x:auto">
                <h5>Tax Ranks for: {{ selectedAttribute.name }}</h5>
              </div>
            </b-row>
            <div class="row" style="padding-top: 10px">
              <label class="typo__label">Classifier</label>
              <multiselect v-model="selected_classifier" :options="classifiers" :searchable="true"
                           :close-on-select="true" :show-labels="false" placeholder="Pick a value"></multiselect>
            </div>
            <div class="row" v-if="type === 1" style="padding-top: 10px">
              <label class="typo__label">Scale Slices On:</label>
              <multiselect v-model="selected_scaleMode" :options="scaleModes" :preselect-first="false" track-by="name"
                           label="label" deselect-label="Can't deselect" :searchable="true" :close-on-select="true"
                           :show-labels="false" placeholder="Pick a value"></multiselect>
            </div>
            <div class="row" style="padding-top: 10px">
              <label class="typo__label">Color Rank by</label>
              <multiselect v-model="selectedAttribute" deselect-label="Can't deselect" track-by="name" label="name"
                           placeholder="Select" @input="changeColor" :show-labels="false" :options="ranks"
                           :searchable="false" :allow-empty="false">
                <template slot="singleLabel" slot-scope="{ option }"><span>{{ option.name }}</span></template>
              </multiselect>
            </div>
            <div v-if="read_types.length > 0" class="row" style="padding-top: 10px">
              <label for="read_type_selection" class="type__label">Read Type</label>
              <multiselect v-model="read_type" :options="read_types" :allow-empty="false" :preselect-first="true"
                           :searchable="false" :close-on-select="true" id="read_type_selection" :show-labels="false"
                           placeholder="Pick a read type" @input="changeReadType"></multiselect>
            </div>
            <br>
            <br>
          </div>
        </div>
      </div>
      <div class="col-md-5">
        <div id="sunburstDiv">
        </div>
      </div>
      <div class="col-md-5">
        <div class="row">
          <button id="resetSunburst" class="btn btn-info" @click="resetSunburst">Reset Zoom</button>
        </div>
        <b-tabs v-model="tab" content-class="mt-3" style="" left align="center">
          <b-tab active title="Table">
            <div v-if="rankNames.length > 0 && height && !(calculateAbu)" class="row" style="padding-left: 20px">
              <b-col sm="12" md="12" class="my-1" v-if="type==1">
                <b-form-group>
                  <b-form-checkbox-group>
                    <b-form-checkbox
                      v-model="shown"
                      value="shown"
                      id="toggleBaselineSunburst"
                      @input="toggleTable"
                    >
                      <strong>Baseline Only</strong></b-form-checkbox>
                  </b-form-checkbox-group>
                </b-form-group>
              </b-col>
              <ComparisonTable 
                :tableData="filteredData"
                :height="height"
                :filterOn="filterOn"
                :fields="fields"
                :defaultSortBy="sortBy"
                :sortByRoot="null"
                :searchByRoot="null"
                :tableType="'sunburst'"
                :type="type"
                v-on:jumpFromTable="jumpTo($event)"
                >
              </ComparisonTable>
            </div>
          </b-tab>
          <b-tab  v-if="rankNames.length > 0 && height && !(calculateAbu) " title="Abundance Thresholding">
            <AbundanceCounts v-if="tab == '1'" width="100%"
                             id="abundanceCount"
                             :fullData="rankNames"
                             :type="'sunburst'"
                             :filteredData="rankNames"
                             v-on:stageUpdateAbuThresholdMin="writeStageUpdateThresholdMin($event)"
                             v-on:stageUpdateAbuThresholdMax="writeStageUpdateThresholdMax($event)"
                             :abuThresholdMin="abuThresholdMin"
                             :abuThresholdMax="abuThresholdMax"
                             :minAbu="minAbu"
                             :maxAbu="maxAbu"
            >

            </AbundanceCounts>
            <hr>
            <div class="col-md-12">
              <label v-b-tooltip.hover.left
                     title="This is set primarily for responsiveness by filtering out very low reported abundance taxids"
                     for="range-1">Visualized Abundance Thresholds</label>
            </div>
            <div class="row">
              <div class="col-md-4 offset-1">
                <label>Minimum</label>
                <b-form-input v-b-tooltip.hover.left
                              title="Exact Decimal or Scientific notation (e.g. 10e-5)"
                              id="abuThresholdSunburstMin"
                              :min="minAbu"
                              :max="abuThresholdMax"
                              v-model="abuThresholdMin"
                              step="any"
                              type="number"></b-form-input>
              </div>
              <div class="col-md-4 offset-1">
                <label>Maximum</label>
                <b-form-input v-b-tooltip.hover.left
                              :min="abuThresholdMin"
                              :max="maxAbu"
                              step="any"
                              title="Exact Decimal or Scientific notation (e.g. 10e-5)" id="abuThresholdSunburstMax"
                              v-model="abuThresholdMax"
                              type="number"></b-form-input>
              </div>
            </div>
            <br>
            <hr>
            <div class="row">
              <div class="col-md-4 offset-1">
                <b-button variant="light" @click="updateAbuThreshold">Update Threshold</b-button>
              </div>
              <div class="col-md-4 offset-1">
                <b-button variant="light" @click="resetAbuThreshold">Remove Threshold</b-button>
              </div>
              <div class="col-md-6 offset-3">
                <b-checkbox v-model="resetUpdateChecked" name="resetThresholdCheckbox" id="resetThresholdCheckbox"></b-checkbox>
                <label v-b-tooltip.hover.top title="When changing sunbursts, specify if you'd like to update the threshold back to the default ranges or keep the same values" for="resetThresholdCheckbox">Reset Threshold On Change</label>
              </div>
            </div>
          </b-tab>
        </b-tabs>
      </div>
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';
  import JobService from '@/services/JobService';
  import ComparisonTable from '@/components/ComparisonTable';
  import AbundanceCounts from '@/components/AbundanceCounts'

  export default {
    name: 'Sunburst',
    components: {Multiselect, ComparisonTable, AbundanceCounts},
    props: ['classifiers', 'containerHeight', 'read_types', 'classifierAbundance', "type", "baseline", "chartType", "parentTab"],
    watch: {
      firstReady() {
        this.$emit("renderSunburst", true)
      },
      filteredData(){
        this.showAllRows()
      },
      abuThresholdMax(old, newVal){
        if (newVal > old){
          this.abuThresholdMax = old
        }  
      },
      abuThresholdMin(old, newVal){
        if (newVal < old){
          this.abuThresholdMin = old
        }  
      },
      selected_classifier(val) {
        this.taxValues = null
        this.rankNames = []
        this.ranks = []
        this.taxData = null
        const $this =this
        this.root = null
        if (this.resetUpdateChecked){
          this.abuThresholdMin= this.defaultAbuThresholdMin
          this.abuThresholdMax= this.defaultAbuThresholdMax
        }
        if (this.selected_classifier) {
          !this.history[this.read_type][val] ? this.getTaxData(val) : '';
          this.history[this.read_type][val] ? this.makeSunburst(this.history[this.read_type][val]) : '';
        }
      },

      selected_scaleMode(val) {
        if (this.selected_classifier) {
          this.taxValues = null
          this.rankNames = []
          this.ranks = []
          this.taxData = null
          this.root = null
          // this.getTaxData(this.selected_classifier)
          !this.history[this.read_type][this.selected_classifier] ? this.getTaxData(this.selected_classifier) : '';
          this.history[this.read_type][this.selected_classifier] ? this.makeSunburst(this.history[this.read_type][this.selected_classifier]) : '';
        }
      },
      minAbu(val){
        if(this.abuThresholdMin < val){
          this.abuThresholdMin = val
        }
      }
    },
    data() {
      return {
        taxData: null,
        taxValues: null,
        childrenselected: 0,
        history: {},
        ranks: [],
        test: 0.5,
        maxAbu: 1,
        minAbu:10e-05,
        resetUpdateChecked: true,
        abuThresholdMin: 0,
        defaultAbuThresholdMin: 10e-5,
        // abuThresholdMin: 10e-5,
        abuThresholdMax: 1,
        defaultAbuThresholdMax: 1,
        rankAbundanceExtents: {},
        seen: {},
        originalabundanceBasis: false,
        scaleModes: [{name: 'totalabundance', label: "Total Abundance"}, {
          name: 'originalAbundance',
          label: "Original Abundance"
        }],
        selected_scaleMode: {name: 'totalabundance', label: "Total Abundance"},
        selected_classifier: null,
        rankNames: [],
        fullData: [],
        calculateAbu: true,
        zoomed: null,
        width: 1000,
        height: null,
        radius: 0,
        maxRanks: 0,
        read_type: null,
        boundsLegendDeviation: {lower: -1, upper: 1},
        boundsDeviation: {},
        firstReady: false,
        tab: 1,

        shown:false,
        fields: [
          {key: 'name', label: 'Name', sortable: true, class: 'text-center'},
          {key: 'taxid', label: 'TaxID', sortable: true, class: 'text-center'},
          {key: 'rank', label: 'Rank', sortable: true, class: 'text-center'},
          {key: 'totalabu', label: 'Reported Abu', sortable: true}
        ],
        filterOn: [],
        sortBy: 'originalAbundance',


        defaultColor: '#1f77b4',
        selectedAttribute: {name: "genus"},
        colorScalePiechart: d3.schemeCategory10.slice(1),
        colorScaleDeviationPieChart: d3.interpolateRdBu,
        x: null,
        taxes: [],
        y: null,
        arc: null,
        sortDir: {col: null, direction: null},
        middleArcLine: null,
        colorRampPieChart: null,
        colorDeviationPieChart: null,
        root: null,

      }
    },
    methods: {
      writeStageUpdateThresholdMin(val) {
        this.abuThresholdMin = val
      },
      writeStageUpdateThresholdMax(val) {
        this.abuThresholdMax = val
      },
      resetAbuThreshold() {
        this.abuThresholdMin = this.minAbu
        this.abuThresholdMax = this.defaultAbuThresholdMax
        this.updateSunburst()
      },
      validate: function(evt, number) { //https://stackoverflow.com/a/39786700/11572828
        evt = (evt) ? evt : window.event;
        var charCode = (evt.which) ? evt.which : evt.keyCode;
        if ((charCode > 31 && (charCode < 48 || charCode > 57)) && charCode !== 46) {
          evt.preventDefault();;
        } 
        else {
          return true;
        }
      },
      changeReadType(){
        if (this.selected_classifier) {
          this.taxValues = null
          this.rankNames = []
          this.ranks = []
          this.taxData = null
          this.root = null
          !this.history[this.read_type][this.selected_classifier] ? this.getTaxData(this.selected_classifier) : '';
          this.history[this.read_type][this.selected_classifier] ? this.makeSunburst(this.history[this.read_type][this.selected_classifier]) : '';
        }
      },
      updateAbuThreshold() {
        this.abuThresholdMin = (this.abuThresholdMin >= this.minAbu ? this.abuThresholdMin : this.minAbu)
        this.abuThresholdMax = (this.abuThresholdMax <= this.maxAbu ? this.abuThresholdMax : this.maxAbu)
        if (this.abuThresholdMin > this.abuThresholdMax) {
          const tmp = this.abuThresholdMin
          this.abuThresholdMin = this.abuThresholdMax
          this.abuThresholdMax = tmp
        }
        this.updateSunburst()

      },
      sort(col) {
        this.sortDir.col = col
        if (!this.sortDir.direction) {
          this.sortDir.direction = 'asc'
        } else {
          this.sortDir.direction = (this.sortDir.direction == "asc" ? 'desc' : 'asc')
        }
        this.sortDir.direction == "asc" ? this.rankNames.sort((a, b) => (a[col] > b[col]) ? 1 : -1) : this.rankNames.sort((a, b) => (a[col] < b[col]) ? 1 : -1)
      },
      toggleTable(entry, text) {
        const val = this.shown[0]
        const baseline = this.baseline
        if (val == 'shown') {
          this.filteredData = this.rankNames.filter((d) => {
            return baseline.indexOf(d.taxid) > -1
          })
        } else {
          this.filteredData = this.rankNames
        }
        this.showAllRows()
      },
      async getTaxData(classifier) {
        const read_type = (this.read_type ? this.read_type : null);
        const $this = this
        if(this.parentTab == 1){
          this.$swal.fire({
            title: "Loading Tax Data...",
            allowOutsideClick: false,
            allowEscapeKey: false,
            allowEnterKey: false,
            onBeforeOpen () {
              $this.$swal.showLoading ()
            },
            onAfterClose () {
              $this.$swal.hideLoading()
            },
          })
        }
          
        await JobService.getJobTaxResults({
          id: this.$route.params.id,
          read_type: read_type,
          classifier: classifier
        }).then((response) => {
          if(this.parentTab == 1){
            this.$swal.close()
          }
          this.taxData = response.data
          this.history[this.read_type][classifier] = this.taxData
          this.makeSunburst(this.taxData)
        })
        .catch((err)=>{
          this.$swal.fire({
              position: 'center',
              icon: 'error',
              showConfirmButton: true,
              title: "There was an error retrieving the tax data"
           })
        })

      },
      showAllRows(){
        if (this.type == 1) {
          for (const entry of this.filteredData) {
            entry._rowVariant = 'shown'
            if (entry.totalabu == 0 && entry.originalAbundance > 0) {
              entry._rowVariant = 'danger';
            } else if (this.baseline.indexOf(entry.taxid) > -1) {
              entry._rowVariant = 'primary';
            }
          }
        }
      },
      async changeColor() {
        var $this = this
        const colorSlice = this.colorSlice

        const selectedAttribute = this.selectedAttribute.name
        let colorRampPieChart;
        if (selectedAttribute != "Deviation") {
          colorRampPieChart = d3.scaleOrdinal(this.colorScalePiechart)
            .domain(this.taxValues[selectedAttribute].map((d) => {
              return d.label
            }));
        } else {
          colorRampPieChart = d3.scaleSequential(this.colorScaleDeviationPieChart).domain([this.boundsLegendDeviation.upper, this.boundsLegendDeviation.lower])
        }
        this.colorRampPieChart = colorRampPieChart;
        d3.selectAll(".main-arc")
          .style('fill', function (d) {
            return $this.colorSlice(d)
          });
        selectedAttribute != "Deviation" ? this.updateLegendTax() : this.updateLegendDeviation();
      },

      updateLegendDeviation() {
        d3.selectAll("g.legendElement").remove()
        const interpolator = this.colorScaleDeviationPieChart

        d3.selectAll(".deviationLegend").remove()
        d3.select("#legend_wrapper").style("overflow-y", "hidden").style("overflow-x", "hidden")

        const div = d3.select("#legend_text_label").text("Deviation from original abundance")
        const svg = d3.select("#sunburstSVG")
        svg.style("width", "100%")
        const legendHeight = 150 - 20
        const legendWidth = 150
        const increment = (Math.abs(this.boundsLegendDeviation.upper) + Math.abs(this.boundsLegendDeviation.lower)) / 200
        var data = [];
        for (let i = this.boundsLegendDeviation.lower; i <= this.boundsLegendDeviation.upper; i += increment) {
          data.push(i);
        }
        const rectHeights = (legendHeight / ((data[data.length - 1] - data[0]) / 0.1))
        const g = svg.append("g").attr("class", "deviationLegend")

        let legendScale = d3.scaleSequential()
          .interpolator(interpolator)
          .domain([this.boundsLegendDeviation.upper, this.boundsLegendDeviation.lower]);

        let yScale = d3.scaleLinear()
          .domain([this.boundsLegendDeviation.upper, this.boundsLegendDeviation.lower])
          .range([10, legendHeight]);

        const axisLabelsLegend = ['Over', "Equal", "Under"]
        const legendAxis = d3.axisLeft()
          .scale(yScale)
          .tickSize(10).ticks(2).tickFormat((d, i) => {
            return axisLabelsLegend[i]
          }).tickPadding(10);
        const legendAxisG = g.append("g").attr("id", "legendAxis")
          .attr("transform", "translate(" + legendWidth / 2 + "," + 0 + ")").attr("class", "legendAxisG")
          .call(legendAxis)
          .selectAll('text')
          .style('text-anchor', 'middle')
          .attr('transform', 'rotate(0)').style("font-size", "0.9em").attr("dx", '-0.9em')

        const legendG = g.selectAll("legendG")
          .data(data)

        const legendGEnter = legendG.enter().append("g")
          .attr("transform", (d) => {
            return "translate(" + 0 + "," + (Math.floor(yScale(d)) - rectHeights / 2) + ")"
          })
          .append("rect")
          .attr("class", "deviationLegendRect")
          .attr("x", (d) => {
            return 2 + legendWidth / 2
          })
          .attr("y", (d) => {
            return 0
          })
          .attr("width", 40)
          .attr("height", (d) => {
            return rectHeights
          })
          .attr("fill", (d) => {
            return legendScale(d)
          });

        legendG.merge(legendGEnter)
        d3.select("#sunburstSVG").attr("height", legendHeight + 20)
      },


      updateLegendTax() {
        let $this = this
        let emptyColor = d3.schemeCategory10[0];
        this.emptyColor = d3.schemeCategory10[0];
        const selectedAttribute = this.selectedAttribute.name
        const taxValues = this.taxValues
        const defaultColor = this.defaultColor
        const piechartLegendSVG = d3.select("#sunburstSVG")
        piechartLegendSVG.select(".deviationLegend").remove()

        d3.select("#legend_text_label").text("Rank: " + selectedAttribute)
        d3.select("#legend_wrapper").style("overflow-y", "auto").style("overflow-x", "auto")
        piechartLegendSVG.selectAll("g.legendElement").remove()
        var legendElement = piechartLegendSVG.selectAll('g.legendElement')
          .data(taxValues[selectedAttribute], function (d) {
            const abu = (!d3.select("#" + d.arc).empty() ? d3.select("#" + d.arc).data()[0].data.totalabundance : 0)
            d.abu = abu
          })
        if (legendElement && legendElement._enter.length > 0) {
          legendElement.exit().remove();
        } else {
          return
        }
        var legendEnter = legendElement.enter()
          .filter(function (d) {
            return d.abu >= $this.abuThresholdMin && d.abu <= $this.abuThresholdMax
          })
          .append('g')
        legendEnter.attr('class', 'legendElement').sort((a, b) => {
          return d3.descending(a.abu, b.abu)
        })
          .on('click', function (d) {
            $this.jumpTo(d.arc)
          })
          .attr("id", (d)=>{
            return "legendElement-"+d.arc
          });

        legendEnter.append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('width', 25)
          .attr('height', 25)
          .attr("class", "legendRect")
          .style('fill', defaultColor);

        legendEnter.append('text')
          .attr('x', 35)
          .attr('y', 18)
          .style('font-size', '14px');

        var legendUpdate = legendElement.merge(legendEnter)
          .transition().duration(0)
          .attr('transform', function (d, i) {
            return 'translate(0,' + (i * 30) + ')';
          });
        legendUpdate.selectAll('rect')
          .style('fill', function (d) {
            var ret = defaultColor;
            if (d == '') {
              ret = emptyColor;
            } else if (d) {
              ret = $this.colorRampPieChart(d.label);
            }
            return ret;
          })

        legendUpdate.selectAll('text')
          .text(function (d) {
            var val = d.label
            if (val == '') {
              val = 'No ' + selectedAttribute + ' listed';
            }
            const abu = d.abu
            return val + ' (' + $this.roundNumbers(abu, 6) + ')';
          })
        piechartLegendSVG.attr("height", legendEnter.size() * 30)
        let max_width = 0
      },
      clearSunburst() {
        return new Promise((resolve, reject) => {
          d3.select('#sunburstDiv').html("")
          resolve()
        })
      },
      resetSunburst() {
        this.jumpTo()
        this.zoomed = null
      },
      jumpTo(ele) {
        this.focusOn(d3.select("#" + ele).data()[0])
      },
      fetchArc(arcName, taxid, depth) {
        return arcName + "-" + taxid + "-" + depth
      },
      updateSunburst() {
        const root = this.root
        const $this = this
        const svg = this.svg
        const taxValues = this.taxValues
        const maxRadius = this.maxRadius
        const pieWidth = this.width;
        const pieHeight = this.height;
        const selectedAttribute = this.selectedAttribute.name
        let sortedValues = []
        const focusOn = this.focusOn
        const arc = this.arc
        const x = this.x
        const y = this.y
        this.taxValues = taxValues
        svg
          .attr('viewBox', `${-maxRadius} ${-pieHeight / 2} ${maxRadius * 2} ${pieHeight}`)

        const format = d3.format(",d")

        const width = this.width
        const radius = this.width / this.maxRanks
        this.radius = radius

        const middleArcLine = d => {
          const halfPi = Math.PI / 2;
          const angles = [x(d.x0) - halfPi, x(d.x1) - halfPi];
          const r = Math.max(0, (y(d.y0) + y(d.y1)) / 2);

          const middleAngle = (angles[1] + angles[0]) / 2;
          const invertDirection = middleAngle > 0 && middleAngle < Math.PI; // On lower quadrants write text ccw
          if (invertDirection) {
            angles.reverse();
          }

          const path = d3.path();
          path.arc(0, 0, r, angles[0], angles[1], invertDirection);
          return path.toString();
        };

        this.middleArcLine = middleArcLine

        let rankNames = [];
        const g = d3.select("#globalg")
        // d3.select("#globalg").html("")
        let minAbu = 0
        const filteredData = root.descendants().slice(1)
          .filter(function (d) {
            const id = $this.fetchArc("sliceMain", d.data.taxid, d.depth)
            rankNames.push({
              rank: d.data.rank,
              taxid: d.data.taxid,
              id: id,
              name: d.data.name,
              totalabu: d.data.totalabundance,
              originalAbundance: d.data.originalAbundance,
              label: d.data.rank + " " + d.data.name + " " + d.data.taxid
            })
            d.data.totalabu =  d.data.totalabundance
            d.data.label = d.data.rank + " " + d.data.name + " " + d.data.taxid
            d.data.id = $this.fetchArc("sliceMain", d.data.taxid, d.depth)
            
            if (d.data.totalabundance > minAbu){
              minAbu = d.data.totalabundance
            }
            return d.data.totalabundance >= $this.abuThresholdMin && d.data.totalabundance <= $this.abuThresholdMax
          })
        this.filteredData = filteredData.map((d) => {
          return d.data
        })
        const slice = g.selectAll("g.slice").data(filteredData, (d) => {
          return d.data.taxid
        })
        slice.exit().remove()
        const sliceEnter = slice.enter()
          .append('g').attr('class', 'slice')
          .on('click', function (d) {
            d3.event.stopPropagation();
            focusOn(d);
          }).attr("id", (d) => {
            return $this.fetchArc("slice", d.data.taxid, d.depth)
          });

        const yExtent = d3.extent(this.filteredData, (d) => {
          return d.abundance
        })

        // this.abuThresholdMax = yExtent[1]
        // this.abuThresholdMin = yExtent[0]

        const groupTaxes = d3.nest().key(d => d.data.rank).rollup((d) => {
          return d3.max(d, (v) => {
            return v.data.totalabundance
          })
        })
          .entries(sliceEnter.data())
        groupTaxes.forEach((d) => {
          this.boundsDeviation[d.key] = [d.value, -d.value]
        })
        sliceEnter.append("title").text(function (d) {
          let abu = (d.data.abundance ? d.data.abundance : '0')
          abu = $this.roundNumbers(abu, 6)
          return "Name: " + d.data.name + "\nTotal Abundance: " + $this.roundNumbers(d.data.totalabundance, 6) + ($this.type == 1 ? "\nOriginal Abundance: " + $this.roundNumbers(d.data.originalAbundance, 6) : '') +
            "\nRank: " + d.data.rank + "\nTaxid: " + d.data.taxid
        })
        this.deviation
        sliceEnter.append('path')
          .attr('class', 'hidden-arc')
          .attr('id', (_, i) => {
            return `hiddenArc${i}`
          })
          .attr('d', middleArcLine)
        sliceEnter.append('path')
          .attr('class', 'main-arc')
          .attr("id", (d) => {
            const id = $this.fetchArc("sliceMain", d.data.taxid, d.depth)
            return id
          })
          .style('fill', '#ccc')
          .on('mouseover', function (d) {
            var currentEl = d3.select($this.fetchArc("#sliceMain", d.data.taxid, d.depth));
            currentEl.style('fill-opacity', 0.5);
          })
          .on('mouseout', function (d) {
            var currentEl = d3.select($this.fetchArc("#sliceMain", d.data.taxid, d.depth));
            currentEl.style('fill-opacity', 1);
          });
        this.sort('depth')
        if (this.type == 1) {
          Object.keys(this.classifierAbundance[this.read_type]['BASELINE1.tsv']).forEach((d) => {
            if (!$this.seen.hasOwnProperty(d)) {
              const entry = this.classifierAbundance[this.read_type]['BASELINE1.tsv'][d]
              rankNames.push({
                rank: entry.rank,
                taxid: entry.taxid,
                name: entry.name,
                totalabu: 0,
                originalAbundance: entry.abundance,
                label: entry.rank + " " + entry.name + " " + entry.taxid
              })
            }
          })
        }


        this.rankNames = rankNames;
        const minMaxAbu = d3.extent(rankNames, (d) => {
          if (d.totalabu > 0) {
            return d.totalabu
          }
        })
        const colorSlice = this.colorSlice
        let colorRampPieChart;
        this.minAbu = minMaxAbu[0]
        if (this.abuThresholdMin < this.minAbu){
          this.abuThresholdMin = this.minAbu
        }
        this.calculateAbu = false;
        
        if (this.selectedAttribute.name != "Deviation") {
          colorRampPieChart = d3.scaleOrdinal(this.colorScalePiechart)
            .domain(taxValues[selectedAttribute].map((d) => {
              return d.label
            }));
        } else {
          colorRampPieChart = d3.scaleSequential(this.colorScaleDeviationPieChart).domain([1, -1])
        }


        this.colorRampPieChart = colorRampPieChart;
        sliceEnter.selectAll('.main-arc')
          .attr('d', arc) /* I moved this from sliceEnter to sliceUpdate in the hopes of dynamically zooming in */
          .style('fill', function (d) {
            return colorSlice(d)
          });


        const text = sliceEnter.append('text')
          .attr('display', d => this.textFits(d) ? null : 'none');

        // Add white contour
        text.append('textPath')
          .attr('startOffset', '50%')
          .attr('xlink:href', (_, i) => `#hiddenArc${i}`)
          .text(d => d.data.name)
          .style('font-size', '12px')
          .style('fill', 'none')
          .style('stroke', '#fff')
          .style('stroke-width', 4)
          .style('stroke-linejoin', 'round');

        text.append('textPath')
          .attr('startOffset', '50%')
          .attr('xlink:href', (_, i) => `#hiddenArc${i}`)
          .text(d => d.data.name)
          .style('font-size', '12px');
        slice.merge(sliceEnter)
          .transition().call(this.standardTransition);
        const piechartLegendSVG = d3.select('#legend_wrapper').append('svg')
          // .style('width', '100%')
          .attr("id", "sunburstSVG")
        selectedAttribute != "Deviation" ? this.updateLegendTax() : this.updateLegendDeviation();

        const zoom = d3.zoom()
          .scaleExtent([1, 8])
          .on("zoom", zoomed);
        function zoomed() {
          const {transform} = d3.event;
          g.attr("transform", transform);
          g.attr("stroke-width", 1 / transform.k);
        }
      },
      async makeSunburst(data) { //https://observablehq.com/@d3/zoomable-sunburst  && Tom Mehoke (JHUAPL) && Brian Merritt (JHUAPL) references for Sunburst Code
        const $this = this;
        if(this.parentTab == 1){
          $this.$swal.fire({
            title: "Building sunburst...",
            allowOutsideClick: true,
            allowEscapeKey: true,
            allowEnterKey: true,
            onBeforeOpen () {
              $this.$swal.showLoading()
            },
            onAfterClose () {
              $this.$swal.hideLoading()
            },
          })
        }
        setTimeout(()=>{ 
          $this.startSunburst(data);
          if(this.parentTab == 1){
            this.$swal.close()
          }
        }, 100)
        
        
      },
      startSunburst(data){
        const $this = this
        let dataTrue = [];
        this.childrenSelected = 0;
        const start_time= this.$moment()
        let colorScalePiechart = this.colorScalePiechart
        let defaultColor = this.defaultColor;
        d3.select("#sunburstDiv").select("svg").remove()
        d3.select("#legend_wrapper").html("")
        const pieWidth = this.width;
        const pieHeight = this.height;
        const maxRadius = Math.round(pieHeight / 2);
        this.maxRadius = maxRadius
        let svg = d3.select("#sunburstDiv").append('svg')
          .style('max-width', maxRadius * 2)
          .style('max-height', this.height)
          .attr('id', 'sunburst');
        this.svg = svg
        d3.selectAll(".slice").remove()
        d3.selectAll(".legendElement").remove()
        d3.select("#sunburstDiv").style("width", maxRadius * 2)
        const selectedAttribute = this.selectedAttribute.name
        let sortedValues = []
        const focusOn = this.focusOn
        svg.append("g").attr('id', "globalg")
        const taxValues = {}
        this.taxValues = taxValues
        const root = this.partition(data);
        this.root = root;
        this.minAbu = this.defaultAbuThresholdMin
        this.maxAbu = this.defaultAbuThresholdMax
        


        this.ranks = []
        let yt = 0
        let maxDepth = 0
        let partDepths = {}
        const classifier = this.selected_classifier
        const read_type = (this.type === 1 ? this.read_type : "real")
        root.each((d => {
          yt += d.data.abundance
          d.depth > this.maxRanks ? this.maxRanks = d.depth : '';
          if (!partDepths.hasOwnProperty(d.depth)) {
            partDepths[d.depth] = []
          }
          partDepths[d.depth].push(d)
          if (d.depth > maxDepth) {
            maxDepth = d.depth
          }
        }))
        for (let i = maxDepth; i > 0; i--) {
          partDepths[i].forEach((d) => {
            !taxValues.hasOwnProperty(d.data.rank) ? (taxValues[d.data.rank] = [], this.ranks.push({name: d.data.rank}), this.childrenSelected += 1) : '';
            taxValues[d.data.rank].map(function (e) {
              return e.label;
            }).indexOf(d.data.name) == -1 && d.data.totalabundance > 0
              ? taxValues[d.data.rank].push({
                label: d.data.name,
                arc: $this.fetchArc("sliceMain", d.data.taxid, d.depth, d.data.name)
              }) : '';
          })
        }
        const taxRanksOnly = this.ranks
        this.type == 1 ? this.ranks.push({name: "Deviation"}) : '';
        const x = d3.scaleLinear()
          .range([0, 2 * Math.PI])
          .clamp(true);
        this.x = x
        const y = d3.scaleSqrt()
          .range([maxRadius * .05, maxRadius]);
        this.y = y
        const arc = d3.arc()
          .startAngle(d => x(d.x0))
          .endAngle(d => x(d.x1))
          .innerRadius(d => Math.max(0, y(d.y0)))
          .outerRadius(d => Math.max(0, y(d.y1)));
        this.arc = arc
        // this.selectedAttribute = (this.type == 1 ? {name: "genus"} : {name: "genus"});
        this.selectedAttribute = (this.type == 1 ? {name: "Deviation"} : {name: "genus"});

        this.updateSunburst()
        data = null
        this.firstReady = true;
      },
      roundNumbers(value, to) {
        return parseFloat(value).toFixed(to)
      },
      colorSlice(d) {
        const colorRampPieChart = this.colorRampPieChart
        const selectedAttribute = this.selectedAttribute.name
        const defaultColor = this.defaultColor
        var e = d, ret = defaultColor;

        if (selectedAttribute != "Deviation") {
          if (e !== null) {
            if (e.data.taxid > 0) {
              if (e.data.rank == selectedAttribute) {
                ret = colorRampPieChart(d.data.name);
              } else {
                let end = false
                let parent = d.parent
                while (parent.depth > 0 && end == false) {
                  if (parent.data.rank == selectedAttribute) {
                    ret = colorRampPieChart(parent.data.name);
                    end = true;
                  }
                  parent = parent.parent
                }
              }
            }
          }
        } else {
          colorRampPieChart.domain(this.boundsDeviation[e.data.rank])
          ret = colorRampPieChart(e.data.totalabundance - e.data.originalAbundance)
        }
        return ret;
      },

      standardTransition(transition) {
        transition
          .duration(500)
          .ease(d3.easeLinear);
      },
      partition(data) {
        const classifierAbundance = this.classifierAbundance
        const classifier = this.selected_classifier
        const read_type = (this.type === 1 ? this.read_type : "real")
        const root = d3.hierarchy(data)
        const $this = this
        this.seen = {}
        root.sum(function (d) {
          d.taxid = parseInt(d.taxid)
          d.abundance += 0
          if ($this.taxes.findIndex(x => x.rank === d.rank) == -1) {
            $this.taxes.push({name: d.rank})
          }
          if (!d.abundance) {
            d.abundance = 0
          } else {
            d.abundance = parseFloat(d.abundance)
          }
          d.totalabundance = d.abundance
          d.originalAbundance = 0
          if (classifierAbundance.hasOwnProperty(read_type)) {
            if (classifierAbundance[read_type].hasOwnProperty('BASELINE1.tsv')) {
              if (classifierAbundance[read_type]['BASELINE1.tsv'].hasOwnProperty(d.taxid)) {
                d.originalAbundance = classifierAbundance[read_type]['BASELINE1.tsv'][d.taxid].abundance
              }
            }
            if (classifierAbundance[read_type].hasOwnProperty(classifier)) {
              if (classifierAbundance[read_type][classifier].hasOwnProperty(d.taxid)) {
                d.totalabundance = classifierAbundance[read_type][classifier][d.taxid].abundance
                d.abundance = classifierAbundance[read_type][classifier][d.taxid].abundance
              }
            }
          }
          $this.seen[d.taxid] = 1
          return !d.children || d.children.length === 0 ? ($this.selected_scaleMode.name === 'originalAbundance' ? d.originalAbundance : d.totalabundance) : 0;
        })
          .sort((a, b) => b.taxid - a.taxid);
        return d3.partition()
        (root);
      },
      textFits(d) {
        const x = this.x;
        const y = this.y;
        const CHAR_SPACE = 8;
        const deltaAngle = x(d.x1) - x(d.x0);
        const r = Math.max(0, (y(d.y0) + y(d.y1)) / 2);
        const perimeter = r * deltaAngle;
        return d.data.name.length * CHAR_SPACE < perimeter;
      },
      focusOn(d = {x0: 0, x1: 1, y0: 0, y1: 1}) {
        // Reset to top-level if no data point specified
        const x = this.x
        const y = this.y
        const svg = this.svg
        const middleArcLine = this.middleArcLine
        const transition = svg.transition()
          .duration(750)
          .tween('scale', () => {
            const xd = d3.interpolate(x.domain(), [d.x0, d.x1]),
              yd = d3.interpolate(y.domain(), [d.y0, 1]);
            return t => {
              x.domain(xd(t));
              y.domain(yd(t));
            };
          });
        transition.selectAll('path.main-arc')
          .attrTween('d', d => () => {
            return this.arc(d)
          });

        transition.selectAll('path.hidden-arc')
          .attrTween('d', d => () => middleArcLine(d));

        transition.selectAll('text')
          .attrTween('display', d => () => this.textFits(d) ? null : 'none');

        this.moveStackToFront(d);
      },
      moveStackToFront(elD) {
        const moveStackToFront = this.moveStackToFront
        this.svg.selectAll('.slice').filter(d => d === elD)
          .each(function (d) {
            this.parentNode.appendChild(this);
            if (d.parent) {
              moveStackToFront(d.parent);
            }
          })
      },
    },
    async mounted() {
      this.windowHeight = window.innerHeight
      this.windowWidth = window.innerWidth
      this.height = this.containerHeight
      this.width = this.windowWidth
      if (this.read_types.length > 0) {
        for (let i = 0; i < this.read_types.length; i++) {
          this.history[this.read_types[i]] = {}
        }
      } else {
        this.history[this.read_type] = {}
        this.read_type = null
      }
      if (this.type === 1) {
        this.fields.push({key: 'originalAbundance', label: 'Orig Abu', sortable: true, sortDirection: 'asc'})
        this.fields.push({key: 'diff', label: 'Difference', sortable: true})
      }
      this.selected_classifier = this.classifiers[0]


    },
  };
</script>
<style>
  .slice {
    cursor: pointer;
  }

  .SunburstTable {
    width: 100%;
  }

  .slice .main-arc {
    stroke: #fff;
    stroke-width: 1px;
  }

  .slice .hidden-arc {
    fill: none;
  }

  .slice text {
    pointer-events: none;
    dominant-baseline: middle;
    text-anchor: middle;
  }

  #sunburstDiv {
    vertical-align: middle;
    text-align: center;
    margin: auto;
  }
</style>


