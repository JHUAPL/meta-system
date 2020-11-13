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
  <div class="row centered" style=" padding-top: 30px">
    <div class="col-md-12">
      <div class="row">
        <div class="col-md-10">
          <div style="max-width: 100000px; border: 0px solid black; " ref="inclusionDIV" id="inclusionDIV">
            <div class="inclusion_tooltip" id="pt" style="opacity:0"></div>
          </div>
          <b-tabs v-model="tabIndex" content-class="mt-3" style="" left align="center">
            <b-tab v-if="filteredInclusionData.length > 0 && groupedData.length > 0 && displayTable" title="Table">
              <div class="col-md-12">
                <b-col sm="12" md="12" class="my-1" v-if="type==1">
                    <b-form-group>
                      <b-form-checkbox-group>
                        <b-form-checkbox
                          v-model="shown"
                          value="shown"
                          id="toggleBaseline"
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
                    :sortByRoot="inclusionSortByRoot"
                    :searchByRoot="inclusionSearchByRoot"
                    :tableType="chartType.key"
                    :type="type"
                    >
                  </ComparisonTable>
              </div>
            </b-tab>
            <b-tab title="Abundance Thresholding">
              <div v-if="filteredInclusionData.length > 0 && tabIndex=='1'" class="col-md-12">
                <AbundanceCounts width="100%"
                                 id="abundanceCount"
                                 :type="'inclusion'"
                                 :fullData="inclusionData"
                                 :filteredData="filteredInclusionData"
                                 v-on:stageUpdateAbuThresholdMin="writeStageUpdateThresholdMin($event)"
                                 v-on:stageUpdateAbuThresholdMax="writeStageUpdateThresholdMax($event)"
                                 :abuThresholdMin="abuThresholdMin"
                                 :abuThresholdMax="abuThresholdMax"
                                 :minAbu="minAbu"
                                 :maxAbu="maxAbu"
                >
                </AbundanceCounts>
              </div>
            </b-tab>
          </b-tabs>

        </div>
        <div class="col-md-2">
          <div style="max-height: 150px; overflow:auto" class="alert alert-info">
            <span>Brush an area to zoom. Double click anywhere to reset zoom.</span>
          </div>
          <label class="typo__label">Color Scale</label>
          <multiselect v-model="colorScale_selected" :allow-empty="false" :preselect-first="false"
                       tag-placeholder="Add this as new tag" placeholder="Select 0 or more" :show-labels="false"
                       :options="colorScale" @input="reset_color()" :multiple="false" :taggable="true"></multiselect>
          <br>
          <div v-if="classifiers.length > 0">
            <label class="typo__label">Filter Classifier(s)</label>
            <multiselect v-model="classifiers_selected" :preselect-first="false" tag-placeholder="Add this as new tag"
                         placeholder="Select 0 or more" :show-labels="false" :options="classifiers" @input="reset()"
                         :multiple="true" :taggable="true" @tag="addClassifiersTag"></multiselect>
          </div>
          <br>
          <div v-if="ranks.length > 0">
            <label class="typo__label">Filter Rank(s)</label>
            <multiselect v-model="ranks_selected" :preselect-first="true" tag-placeholder="Add this as new tag"
                         placeholder="Select 0 or more" :show-labels="false" :options="ranks" :multiple="true"
                         :taggable="true" @input="reset()" @tag="addRanksTag"></multiselect>
          </div>
          <br>
          <hr>
          <div class="row">
            <div class="col-md-12">
              <label v-b-tooltip.hover.left
                     title="This is set primarily for responsiveness by filtering out very low reported abundance taxids"
                     for="range-1">Visualized Abundance Thresholds</label>
              <label>Minimum</label>
              <b-form-input v-b-tooltip.hover.left title="Exact Decimal or Scientific notation (e.g. 10e-5)"
                            :min="minAbu"
                            :max="abuThresholdMax"
                            id="abuThresholdinclusionMin"
                            v-model="abuThresholdMin"
                            ref="abuThresholdinclusionMin"
                            step="any"
                            type="number"></b-form-input>
            </div>
            <br>
            <br>
            <div class="col-md-12">
              <label>Maximum</label>
              <b-form-input v-b-tooltip.hover.left title="Exact Decimal or Scientific notation (e.g. 10e-5)"
                            id="abuThresholdinclusionMax"
                            v-model="abuThresholdMax"
                            :min="abuThresholdMin"
                            :max="maxAbu"
                            ref="abuThresholdinclusionMax"
                            step="any"
                            type="number"></b-form-input>
            </div>
            <br>
            <br>
            <div class="d-flex jfustify-content-center;" style="margin:auto">
              <b-button class="" variant="light" @click="updateAbuThreshold">Update Threshold</b-button>
            </div>
            <div class="d-flex justify-content-center;" style="margin:auto;">
              <b-button class="" variant="light" @click="resetAbuThreshold">Remove Threshold</b-button>
            </div>
          </div>
          <div v-if="(svg)" :style="{ display: colorScale_selected !=='abundance' ? '' : 'none'  }"
               id="legend_wrapper_inclusion"
               style="position:relative; background: none; background-opacity: 0.5; width: 100%; max-height: 200px; overflow:auto;">
            <h5>Tax Ranks</h5>
            <svg id="inclusionSVGLegend"></svg>
          </div>
          <br>
        </div>
      </div>

    </div>

  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';
  import AbundanceCounts from '@/components/AbundanceCounts'
  import ComparisonTable from '@/components/ComparisonTable'

  export default {
    name: 'Inclusion',
    props: ['inclusionData', "chartType", 'containerHeight', 'type', 'inclusionSearchByRoot', 'inclusionSortByRoot', 'baseline', 'tabInclusion'],
    components: {Multiselect, ComparisonTable, AbundanceCounts},
    data() {
      return {
        chart: null,
        classifiers_selected: [],
        filteredInclusionData: [],
        groups_track: {},
        groupedData: [],
        classifiers: [],
        ranks: [],
        abuThresholdMin: 10e-5,
        defaultAbuThresholdMin: 10e-10,
        defaultAbuThresholdMax: 1,
        abuThresholdMax: 1,
        ranks_selected: [],
        ySelected: null,
        xSelected: null,
        yOptions: ['abundance', 'count'],
        xOptions: ['classifier', 'rank'],
        displayTable: false,
        dimensions: {},
        jitterWidth: 40,
        svg: null,
        aspect: null,
        chart_width: null,
        chart_height: null,
        histograms: {},
        maxAbu: 1,
        minAbu: 0,
        margin: null,
        scaleY: {ABUNDANCE: null, COUNT: null},
        yAxis: {ABUNDANCE: null, COUNT: null},
        scaleX: {CLASSIFIER: null, RANK: null},
        xAxis: {CLASSIFIER: null, RANK: null},
        data: null,
        color: null,
        filteredData: null,
        colorScale: ['abundance', 'rank'],
        colorScale_selected: null,
        tabIndex: this.tabInclusion,
        filterOn: ['name', 'taxid', 'rank', 'classifier'], //Everything downards is for table generation
        filteredData:[],
        shown: false,
        sortBy: 'classifier',
        fields: [
          {key: 'name', label: 'Name', sortable: true, class: 'text-center'},
          {key: 'taxid', label: 'TaxID', sortable: true, class: 'text-center'},
          {key: 'rank', label: 'Rank', sortable: true, class: 'text-center'},
          {key: 'abundance', label: 'Abu', sortable: true},
          {key: 'classifier', label: 'Classifier(s)', sortable: true, class: 'text-center'},
          {key: 'classifier_count', label: 'Taxid Calls', sortable: true},
          {key: 'ratio', label: 'Total Calls Ratio', sortable: true}
        ],
      }
    },
    watch: {
      inclusionSearchByRoot(val) {
        this.ranks_selected = [val]
        this.updateViolin(this.inclusionData, this.ySelected, this.xSelected, false)
      },
      tabInclusion(val) {
        this.tabIndex = val
      },
      tabIndex(val) {
        this.$emit("updateChildTab", val)
      },
      abuThresholdMin(val) {
        if (!val) {
          this.abuThresholdMin = this.minAbu
        }
      },
      abuThresholdMax(val) {
        if (!val) {
          this.abuThresholdMax = this.maxAbu
        }
      }
    },
    async mounted() {
      this.windowHeight = window.innerHeight
      this.windowWidth = window.innerWidth
      this.height = this.containerHeight
      const groupedInclusionData = [];
      this.filteredData = this.inclusionData
      this.inclusionData.forEach((d) => {
        if (!this.groups_track.hasOwnProperty(d.taxid)) {
          this.groups_track[d.taxid] = d
          this.groups_track[d.taxid].abundance_grouped = [d.abundance]
        } else {
          this.groups_track[d.taxid].abundance_grouped.push(d.abundance)
        }
      })
      Object.keys(this.groups_track).forEach((d) => {
        this.groupedData.push(this.groups_track[d])
      })

      if (this.type == 1) {
        this.fields.push({key: 'read_type', label: 'Read Type', sortable: true})
      }

      const $this  = this

      this.displayTable = true
      this.$swal.fire({
        title: "Making Inclusion Plot...",
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
      setTimeout(()=>{this.makeViolin(this.inclusionData); this.$swal.close()}, 1)
      

    },
    methods: {
      writeStageUpdateThresholdMin(val) {
        this.abuThresholdMin = val
      },
      writeStageUpdateThresholdMax(val) {
        this.abuThresholdMax = val
      },
      toggleTable(entry, text) {
        const val = this.shown
        const baseline = this.baseline
        if (val == 'shown') {
          this.filteredData = this.inclusionData.filter((d) => {
            return baseline.indexOf(d.taxid) > -1
          })
        } else {
          this.filteredData = this.inclusionData
        }
      },
      resetAbuThreshold() {
        this.abuThresholdMin = this.minAbu
        this.abuThresholdMax = this.defaultAbuThresholdMax
        this.updateViolin(this.inclusionData, this.ySelected, this.xSelected, false)
      },
      updateAbuThreshold() {
        this.abuThresholdMin = (this.abuThresholdMin >= this.minAbu ? this.abuThresholdMin : this.minAbu)
        this.abuThresholdMax = (this.abuThresholdMin <= this.maxAbu ? this.abuThresholdMax : this.maxAbu)
        if (this.abuThresholdMin > this.abuThresholdMax) {
          const tmp = this.abuThresholdMin
          this.abuThresholdMin = this.abuThresholdMax
          this.abuThresholdMax = tmp
        }
        this.updateViolin(this.inclusionData, this.ySelected, this.xSelected, false)
      },

      makeHistogram(scaleX, scaleY, chartData) {
        // Features of the histogram
        const margin = this.margin
        let svg = this.svg
        let histogram = d3.histogram()
          .domain(scaleY.domain())
          .thresholds(scaleY.ticks(10))    // Important: how many bins approx are going to be made? It is the 'resolution' of the violin plot
          .value(d => d)      // Compute the binning for each group of the dataset
        let sumstat = d3.nest()  // nest function allows to group the calculation per level of a factor
          .key(function (d) {
            return d.classifier;
          })
          .rollup(function (d) {   // For each key..
            let input = d.map(function (g) {
              return g.abundance;
            })    // Keep the variable called: abundance
            let bins = histogram(input)   // And compute the binning on it.
            return (bins)
          })
          .entries(chartData)
        // What is the biggest number of value in a bin? We need it cause this value will have a width of 100% of the bandwidth.
        let maxNum = 0
        let longuest;
        for (let i in sumstat) {
          const allBins = sumstat[i].value
          const lengths = allBins.map(function (a) {
            return a.length;
          })
          longuest = d3.max(lengths)
          if (longuest > maxNum) {
            maxNum = longuest
          }
        }

        // The maximum width of a violin must be x.bandwidth = the width dedicated to a group
        let xNum = d3.scaleLinear()
          .range([0, scaleX.bandwidth()])
          .domain([-maxNum, maxNum])

        // Add the shape to this svg!
        d3.selectAll(".inclusionPlot").remove()
        const g = svg
          .selectAll(".inclusionPlot")
          .data(sumstat, (d) => {
            return d.key
          })
          .join(
            function (enter) {
              return enter.append("g")
                .attr("class", "inclusionPlot")
                .attr("id", (d) => {
                  return d.key
                })
                .attr("transform", function (d, i) {
                  return ("translate(" + scaleX(d.key) + " ,0)")
                }) // Translation on the right to be at the group position
                .append("path")
                .datum(function (d, i) {
                  return (d.value)
                }, (d) => {
                  return d.key
                })     // So now we are working bin per bin
                .style("stroke", "none")
                .style("fill", "grey")
                .attr("d", d3.area()
                  .x1(function (d, i) {
                    return (xNum(d.length))
                  })
                  .x0(xNum(0))
                  .y(function (d) {
                    return (scaleY(d.x0))
                  })
                  .curve(d3.curveCatmullRom)    // This makes the line smoother to give the violin appearance. Try d3.curveStep to see the difference
                )
            },
            function (update) {
              return update.transition().duration(700).attr("transform", function (d) {
                return ("translate(" + scaleX(d.key) + " ,0)")
              }) // Translation on the right to be at the group position
            },
            function (exit) {
              return exit.remove()
            }
          )

      },
      updateColorScale(yElement) {
        let ranks = (this.ranks_selected.length > 0 ? this.ranks_selected : this.ranks);
        const scaleY = this.scaleY[yElement]
        let myColor;
        if (this.colorScale_selected === "abundance") {
          myColor = d3.scaleSequential()
            .interpolator(d3.interpolateYlGnBu)
            .domain((scaleY.domain()))
        } else {
          myColor = d3.scaleOrdinal(d3.schemeCategory10.slice(1))
            .domain(ranks);
        }
        this.myColor = myColor
        return myColor
      },
      async updateViolin(data, yElement, xElement, initial) {
        let svg = this.svg
        const $this = this
        const scaleY = this.scaleY[yElement]
        const classifiers = (this.classifiers_selected.length > 0 ? this.classifiers_selected : this.classifiers);
        let ranks = (this.ranks_selected.length > 0 ? this.ranks_selected : this.ranks);
        this.scaleX[xElement].domain(classifiers)
        const margin = this.margin
        const scaleX = this.scaleX[xElement]
        let tooltip = d3.select("#pt")

        let chartData = data.filter((d) => {
          return classifiers.indexOf(d.classifier) > -1 && ranks.indexOf(d.rank) > -1
        })
        const yExtentFull = this.defineExtents(chartData)
        this.maxAbu = yExtentFull[1]
        this.minAbu = yExtentFull[0]
        if (this.abuThresholdMin < this.minAbu){
          this.abuThresholdMin = this.minAbu
        }
        this.filteredInclusionData = chartData
        chartData = chartData.filter((d) => {
          if (d.abundance >= $this.abuThresholdMin && d.abundance <= $this.abuThresholdMax) {
            return true
          } else {
            return false
          }
        })
        const yExtent = d3.extent(chartData, (d) => {
          return d.abundance
        })
        this.abuThresholdMax = yExtent[1]
        // this.abuThresholdMin = yExtent[0]
        yExtent[1] = yExtent[1]
        this.yExtent = yExtent
        scaleY.domain(d3.extent(chartData, (d) => {
          return d.abundance
        }))

        scaleX.domain(classifiers)
        this.makeHistogram(scaleX, scaleY, chartData)
        // Color scale for dots
        let myColor = this.updateColorScale(yElement)

        this.xAxis[xElement].scale(scaleX)
        this.yAxis[yElement].scale(scaleY)
        const xAxis = this.xAxis[xElement]
        const yAxis = this.yAxis[yElement]
        // Add individual points with jitter
        let jitterWidth = this.jitterWidth;
        svg.select(".x-axis").transition().duration(1000).call(xAxis)
        svg.select(".y-axis").transition().duration(1000).call(yAxis)
        const circles = svg.selectAll(".indPoints").data(chartData, function (d) {
          return d.taxid + "-" + d.classifier + '-' + d.read_type
        })
          .join(
            function (enter) {
              return enter
                .append("circle").attr("class", (d) => {
                  return "indPoints  " + "indPoints-" + d.taxid
                })
                .attr("id", (d, i) => {
                  return "indPoint-" + d.taxid + "-" + d.classifier + "-" + ($this.type == 1 ? d.read_type : '')
                })
                .attr("cx", function (d) {
                  return (scaleX(d.classifier) + scaleX.bandwidth() / 2 - Math.random() * jitterWidth)
                })
                .attr("cy", function (d) {
                  return (scaleY(d.abundance))
                })
                .attr("r", 4)
                .style("fill", function (d) {
                  return (myColor(d[$this.colorScale_selected]))
                })
                .on("mousemove", (d, i, n) => {
                  d3.select(n[i]).transition().duration(500).attr("r", 12)

                })
                .on('mouseout', (d, i, n) => {
                  d3.select(n[i]).transition().duration(500).attr("r", 4)
                })
                .append("title").text(d => 'Classifier: ' + d.classifier + "\nRank: " + d.rank + "\nAbu: " + d.abundance + "\nTaxid: " + d.taxid + "\nName: " + d.name + ($this.type == 1 ? "\nRead Type: " + d.read_type : ''))

            },
            function (update) {
              return update.transition().duration(700).attr("cx", function (d) {
                return (scaleX(d.classifier) + scaleX.bandwidth() / 2 - Math.random() * jitterWidth)
              })
                .attr("cy", function (d) {
                  return (scaleY(d.abundance))
                }).style("fill", function (d) {
                  return (myColor(d[$this.colorScale_selected]))
                })
            },
            function (exit) {
              return exit.remove()
            }
          )

        this.updateLegend(ranks)


      },
      addClassifiersTag(newTag) {
        const tag = newTag
        this.classifiers_selected.push(tag)
      },
      addRanksTag(newTag) {
        const tag = newTag
        this.ranks_selected.push(tag)
      },
      updateLegend(ranks) {
        const $this = this
        d3.select("#legend_wrapper_inclusion").style("overflow-y", "auto")
        const svg = d3.select("#inclusionSVGLegend")
        svg.attr("height", ranks.length * 30).attr("width", "100%")
        var legendElement = svg.selectAll('g.legendElementInclusion')
          .data(ranks, (d) => {
            return d
          })
        legendElement.exit().remove();
        var legendEnter = legendElement.enter()
          .append('g')
          .attr('class', 'legendElementInclusion')
          .attr("id", (d) => {
            return d
          })

        legendEnter.append('rect')
          .attr('x', 0)
          .attr('y', 0)
          .attr('width', 25)
          .attr('height', 25)
          .attr("class", "legendRect")
          .style('fill', (d) => {
            return $this.myColor(d)
          });

        legendEnter.append('text')
          .attr('x', 35)
          .attr('y', 18)
          .style('font-size', '14px')
          .text((d) => {
            return d
          });
        var legendUpdate = legendElement.merge(legendEnter)
          .transition().duration(0)
          .attr('transform', function (d, i) {
            return 'translate(0,' + (i * 30) + ')';
          });
        legendUpdate.selectAll('rect')
          .style('fill', function (d) {
            var ret = 'black';
            if (d == '') {
              ret = emptyColor;
            } else if (d) {
              ret = $this.myColor(d);
            }
            return ret;
          })


        legendUpdate.selectAll('text')
          .text(function (d) {
            var val = d
            return val
          });
      },
      async reset() {
        d3.selectAll(".indPoints").style("opacity", 1)
        if (this.ranks) {
          this.updateViolin(this.inclusionData, this.ySelected, this.xSelected, false)
        }
      },
      defineExtents(data) {
        return d3.extent(data, (d) => {
          if (d.abundance > 0) {
            return d.abundance
          }
        })
      },
      async reset_color() {
        let myColor = this.updateColorScale(this.ySelected)
        const $this = this
        const svg = d3.select('#svgInclusion')
        let t = svg.transition().duration(750);
        svg.selectAll("circle").transition(t)
          .style("fill", function (d) {
            return (myColor(d[$this.colorScale_selected]))
          })
        if (this.colorScale_selected === "rank") {
          this.updateLegend((this.ranks_selected.length == 0 ? this.ranks : this.ranks_selected))
        } else {
          this.updateLegend([])
        }
      },
      zoom() {
        const svg = d3.select('#svgInclusion')
        const scaleX = this.scaleX[this.xSelected]
        const scaleY = this.scaleY[this.ySelected]
        const scaleYdomain = scaleY.domain();
        let t = svg.transition().duration(750);
        const xAxis = this.xAxis[this.xSelected]
        const yAxis = this.yAxis[this.ySelected]
        const jitterWidth = this.jitterWidth
        svg.select(".x-axis").transition(t).call(xAxis);
        svg.select(".y-axis").transition(t).call(yAxis);
        const eles = d3.selectAll("circle").data()
        this.makeHistogram(scaleX, scaleY, eles)
        const myColor = this.updateColorScale(this.ySelected)
        const $this = this
        svg.selectAll("circle").transition(t)
          .attr("cx", function (d) {
            return scaleX(d.classifier) + scaleX.bandwidth() / 2 - Math.random() * jitterWidth;
          })
          .attr("cy", function (d) {
            return scaleY(d.abundance);
          })
          .style("fill", function (d) {
            return (myColor(d[$this.colorScale_selected]))
          })
          .style("opacity", (d) => {
            if (d.abundance > scaleYdomain[1] || d.abundance < scaleYdomain[0]) {
              return 0
            } else {
              return 1
            }
          })
        ;
      },
      brushended() {
        var s = d3.event.selection;
        const classifiers = this.classifiers
        const yExtent = this.yExtent
        const scaleY = this.scaleY[this.ySelected]
        const scaleX = this.scaleX[this.xSelected]
        if (!s) {
          if (!this.idleTimeout) return this.idleTimeout = setTimeout(this.idled, this.idleDelay);
          this.scaleY[this.ySelected].domain(yExtent);
          // this.scaleX[this.xSelected].domain(xExtent);
        } else {
          // x.domain([s[0][0], s[1][0]].map(x.invert, x));
          this.scaleY[this.ySelected].domain([s[1][1], s[0][1]].map(scaleY.invert, scaleY));

          d3.select('#svgInclusion').select(".brush").call(this.brush.move, null);
        }
        this.zoom();
      },
      idled() {
        this.idleTimeout = null;
      },
      async makeViolin(data) {
        this.height = (this.containerHeight * 0.95)
        this.width = this.$refs.inclusionDIV.clientWidth
        const jitterWidth = this.jitterwidth

        this.margin = {
          top: 0.1 * this.height,
          bottom: 0.1 * this.height,
          left: 0.1 * this.width,
          right: this.width * 0.1
        }
        const margin = this.margin
        const height = this.height
        const width = this.width
        // append the svg object to the body of the page
        let svg = d3.select("#inclusionDIV")
          .append("svg")
          .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
          // .style("background", "aliceblue")
          .attr("id", "svgInclusion")
          .append("g")
          .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");
        this.svg = svg
        let ranks = d3.map(data, function (d) {
          return d.rank;
        }).keys()
        if (ranks.indexOf('species') > -1) {
          ranks.splice(ranks.indexOf('species'), 1)
          ranks.unshift('species')
        }

        const classifiers = d3.map(data, function (d) {
          return d.classifier;
        }).keys()
        const yExtent = this.defineExtents(data)
        this.abuThresholdMin = this.defaultAbuThresholdMin

        this.classifiers = classifiers
        this.ranks = ranks
        // this.ranks_selected = ["phylum"]
        let scaleY = d3.scaleLinear()
          .range([height, 0])
        this.scaleY.count = scaleY
        scaleY = d3.scaleLinear()
          .range([height, 0])
        this.scaleY.abundance = scaleY


        const yAxis = d3.axisLeft(scaleY)
        this.yAxis.abundance = yAxis
        svg.append("g").attr("class", "y-axis").call(yAxis)


        // Build and Show the X scale. It is a band scale like for a boxplot: each group has an dedicated RANGE on the axis. This range has a length of x.bandwidth
        // Classifier x Abundance
        let scaleX = d3.scaleBand()
          .range([0, width])
          .padding(0.0)     // This is important: it is the space between 2 groups. 0 means no padding. 1 is the maximum.
        this.scaleX.rank = scaleX


        scaleX = d3.scaleBand()
          .range([0, width])
          .padding(0.00)     // This is important: it is the space between 2 groups. 0 means no padding. 1 is the maximum.
        this.scaleX.classifier = scaleX


        this.xOptions = Object.keys(this.scaleX)
        this.yOptions = Object.keys(this.scaleY)

        this.ySelected = "abundance"
        this.xSelected = "classifier"

        const xAxis = d3.axisBottom(scaleX)
        this.xAxis.classifier = xAxis
        // Rank x Count TaxIDs
        svg.append("g").attr("class", "x-axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis)


        let brush = d3.brush().on("end", this.brushended);
        this.idleTimeout;
        this.idleDelay = 350;
        this.brush = brush
        svg.append("g")
          .attr("class", "brush")
          .call(brush);
        this.updateViolin(data, 'abundance', 'classifier', true)
        this.colorScale_selected = this.colorScale[0]
        //Make y axis title for abundance
        d3.select(".y-axis").append("text")
          // .attr("transform", "translate("  + "-0.5em," + "0.5em" + ")")
          .attr("x", (8))
          .attr("y", (-this.margin.top / 2))
          .text("Abundance (relative)")
          .style("color", "grey")
          .style("text-anchor", "middle")
          .style("stroke", "black")
          .style("stroke-width", 1)
          .style("opacity", 0.9)
          .attr("transform", "rotate(0)")


      }

    }

  };
</script>
<style>
  .inclusion_tooltip {
    position: absolute;
    text-align: center;
    max-width: 300px;
    padding: 10px;
    background: #efefef;
    border: 0px;
    border-radius: 4px;
    pointer-events: none;
    display: flex;
    justify-content: center;
    align-content: center;
    align-items: center;
    color: #fff;
    background: #232B2B;
    box-shadow: 0px 3px 1px rgba(39, 39, 40, 0.6);
  }

  .y-axis, .x-axis {
    font-size: 1em;
  }

  .indPoints {
    stroke: black;
    stroke-width: 0.4;
  }
</style>


