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
  <div>
    <b-tabs v-model="tab" content-class="mt-3" style="" left align="center">
      <b-tab title="Table">
        <div class="row" id="inclusionTable" v-if="height">
          <div class="col-md-12">
            <ComparisonTable
              :tableData="chartData"
              :height="height"
              :filterOn="filterOn"
              :fields="fields"
              :defaultSortBy="sortBy"
              :sortByRoot="sortByRoot"
              :searchByRoot="searchByRoot"
              :tableType="chartType.key"
              :type="type"
              >
            </ComparisonTable>
          </div>
        </div>
      </b-tab>
      <b-tab active title="Chart" >
        <div class="row">
          <div class="col-md-8">
            <div class="row">
              <div class="col-md-12">
                <h3 style="padding-left: 10%">AUPRC</h3>
                <div style="max-width: 100000px; border: 0px solid black; " ref="groupedDIVAUPRC" id="groupedDIVAUPRC">
                  <div class="tooltip" id="pt_AUPRC" style="opacity:0"></div>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-md-12">
                <h3 style="padding-left: 10%">L2</h3>
                <div style="max-width: 100000px; border: 0px solid black; " ref="groupedDIVL2" id="groupedDIVL2">
                  <div class="tooltip" id="pt_L2" style="opacity:0"></div>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="col-md-12">
                <div style="max-width: 100000px; height: 100px; border: 0px solid black; " ref="groupedLegend"
                     id="groupedLegend">
                </div>
              </div>
            </div>

          </div>
          <div class="col-md-4">
            <br>
            <div class="alert alert-info">
              <span>Filter Parameters</span>

            </div>
            <br>
            <label class="typo__label">Select classifier(s)</label>
            <multiselect v-model="classifiers_selected" tag-placeholder="Add this as new tag"
                         placeholder="Select 0 or more" :show-labels="false" :options="classifiers" :multiple="true"
                         :taggable="true" @input="reset()" @tag="addClassifiersTag"></multiselect>
            <div id="xAxisLegendMaxed" style="max-height: 190px; padding-top: 20px; overflow:auto">
              <label v-if="mapMaxXAxis" class="typo__label">Classifiers Map</label>
              <ul id="xAxisLegendList"></ul>
            </div>
            <br>
            <label class="typo__label">Filter Rank</label>
            <multiselect v-model="taxes_selected" tag-placeholder="Add this as new tag" placeholder="Select 0 or more"
                         :show-labels="false" :options="taxes" label="name" track-by="name" :multiple="true"
                         :taggable="true" @input="reset()" @tag="addTaxesTag"></multiselect>
            <br>
            <label class="typo__label">Filter Read Type</label>
            <multiselect v-model="read_types_selected" tag-placeholder="Add this as new tag"
                         placeholder="Select 0 or more" :show-labels="false" :options="read_types" :multiple="true"
                         :taggable="true" @input="reset()" @tag="addTaxesTag"></multiselect>
          </div>
        </div>
      </b-tab>
    </b-tabs>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';
  import ComparisonTable from '@/components/ComparisonTable'

  export default {
    name: 'Chart',
    components: {Multiselect, ComparisonTable},
    props: ['chartData', 'chartType', 'taxes', 'classifiers', 'containerHeight', 'read_types', 'sortByRoot', 'searchByRoot', 'tabRoot', 'type'],
    data() {
      return {
        chart: null,
        classifiers_selected: [],
        taxes_selected: [],
        read_types_selected: [],
        container: {AUPRC: null, L2: null},
        dimensions: {},
        svg: {L2: null, AUPRC: null},
        aspect: null,
        chart_width: null,
        chart_height: null,
        height: null,
        margin: null,
        scaleY: {L2: null, AUPRC: null},
        divisionYScale: {L2: null, AUPRC: null},
        scaleXCore: {L2: null, AUPRC: null},
        scaleXInner: {L2: null, AUPRC: null},
        scaleXGroup: {L2: null, AUPRC: null},
        xAxisInner: {L2: null, AUPRC: null},
        xAxisGroup: {L2: null, AUPRC: null},
        xAxis: {L2: null, AUPRC: null},
        xAxisCore: {L2: null, AUPRC: null},
        yAxis: {L2: null, AUPRC: null},
        yAxisDivision: {L2: null, AUPRC: null},
        cat: "combined",
        data: null,
        color: null,
        maxXAxisAmount: 12,
        mapMaxXAxis: false,
        tab: 0,
        thisSort: {
          L2: {sortAscending: false, sortTaxAscending: false},
          AUPRC: {sortAscending: false, sortTaxAscending: false}
        },
        sortBy: 'classifier', //Here downwards are props for the table component
        filterOn: ['rank', 'L2', 'AUPRC', 'METAVal', 'read_type', 'classifier_name'],
        fields: [
          {key: 'rank', label: 'Rank', sortable: true, class: 'text-center'},
          {key: 'classifier_name', label: 'Classifier(s)', sortable: true, class: 'text-center'},
          {key: 'L2', label: 'L2', sortable: true},
          {key: 'AUPRC', label: 'AUPRC', sortable: true},
          {key: 'METAVal', label: 'Ratio (AUPRC / L2)', sortable: true},
          {key: 'read_type', label: 'Read Type', sortable: true}
        ],      }
    },
    watch: {
      searchByRoot(val) {
        this.taxes_selected = [{name: val}]
        this.reset()
      },
      tabRoot(val) {
        this.tab = val
      },
      tab(val) {
        this.$emit("updateChildTab", val)
      }
    },
    mounted() {
      const $this = this
      const elements = Object.keys(this.container)
      this.height = this.containerHeight * 0.6
      d3.select("#groupedDIVAUPRC").style("height", this.height)
      d3.select("#groupedDIVL2").style("height", this.height)
      this.width = d3.select("#groupedDIVAUPRC").style("width").replace("px", "")
      this.margin = {
        top: 0.15 * this.height,
        bottom: 0.1 * this.height,
        left: 0.1 * this.width,
        right: this.width * 0.1
      }
      const margin = this.margin
      const width = this.width

      const keys = this.taxes.map((d) => {
        return d.name
      })
      for (var i = 0; i < elements.length; i++) {
        const element = elements[i]

        const svg = d3.select('#groupedDIV' + element).append("svg").attr('id', "groupedSVG-" + element)
          .attr('viewBox', `0 0 ${this.width} ${this.height}`)
        this.svg[element] = svg
        const g = svg.append("g").attr("id", "svgG-" + element)
        this.g = g
        const classifiers = (this.classifiers_selected.length == 0 ? this.classifiers : this.classifiers_selected)
        const read_types = (this.read_types_selected.length == 0 ? read_types : this.read_types_selected)


        const scaleXCore = d3.scaleBand()
          .rangeRound([this.margin.left, this.width])
        // .paddingInner(0.05)

        const scaleXGroup = d3.scaleBand()
        // .padding(0.1)

        const scaleXInner = d3.scaleBand()
        // .padding(0.05)

        const scaleY = d3.scaleLinear()
          .domain([0, element == "L2" ? d3.max(this.chartData, (d) => {
            return d[element]
          }) : 1]).nice()
          .rangeRound([this.height - this.margin.bottom - this.margin.top, this.margin.top])
        const divisionYScale = d3.scaleLinear()
          .domain([0, element == "L2" ? d3.max(this.chartData, (d) => {
            return d[element]
          }) : 1]).nice()
          .rangeRound([this.height - this.margin.bottom, 0])

        const color = d3.scaleOrdinal().range(d3.schemeAccent.slice(1))
          .domain(this.taxes.map((d) => {
            return d.name
          }))
        this.color = color

        this.scaleY[element] = scaleY
        this.scaleXInner[element] = scaleXInner
        this.scaleXGroup[element] = scaleXGroup
        this.scaleXCore[element] = scaleXCore
        this.divisionYScale[element] = divisionYScale

        const xAxis = d3.axisBottom()
          .scale(scaleXGroup)
        const xAxisCore = d3.axisTop()
          .scale(scaleXCore).tickSizeOuter(0)

        const yAxis = d3.axisLeft()
          .scale(scaleY).tickSizeOuter(0)
          .ticks(10);
        const yAxisDivision = d3.axisLeft()
          .scale(divisionYScale).tickSizeOuter(0)
          .ticks(0);

        this.yAxis[element] = yAxis
        this.xAxis[element] = xAxis
        this.xAxisCore[element] = xAxisCore
        this.yAxisDivision[element] = yAxisDivision

        const xAxisGCore = g.append("g")
          .attr("transform", `translate(0,${this.margin.top / 1})`)
          .attr("id", "x-axisGCore-" + element)
          .attr("class", "x-AxisGCore")
          .call(xAxis)
          .call(g => g.select(".domain").remove())
          .selectAll('text')
          .style('text-anchor', 'middle')
          .attr('transform', 'rotate(0)')


        const yAxisG = g.append("g").attr("class", "yAxis")
          .attr("id", "y-axisG-" + element)
          .attr("class", "y-axisG")
          .attr("transform", "translate(" + this.margin.left + "," + 0 + ")")

        yAxisG.call(yAxis.tickSize(-this.width + this.margin.right))
          .selectAll('text')
          .style('text-anchor', 'end')
          .attr('transform', 'rotate(0)').style("font-size", "0.8em")
        g.select("#y-axisG-" + element + " ").selectAll(".tick").filter(":last-child").select("line").style("display", "none")
        this.updatePlot(element)
      }
      ;
      const color = this.color

      const gLegendDIV = d3.select("#groupedLegend").style("height", this.height * 0.1)
      const gLegendWidth = gLegendDIV.style("width").replace("px", "")
      const gLegendHeight = gLegendDIV.style("height").replace("px", "")
      const gLegend = gLegendDIV.append("svg").attr('id', "groupedLegendSVG")
        .attr('viewBox', `0 0 ${gLegendWidth} ${gLegendHeight}`)
      const legendPosY = (gLegendHeight / 2)
      const legendWidth = (gLegendWidth - margin.right - margin.left) / this.taxes.length
      const legendScale = d3.scaleOrdinal()
        .domain(this.taxes.map((d) => {
          return d.name
        }))
        .range(this.taxes.map((d, i) => {
          return margin.right + margin.left + i * legendWidth
        }))
      const legendAxis = d3.axisBottom()
        .scale(legendScale)
        .tickSize(0)
      const legendAxisG = gLegend.append("g").attr("id", "legendAxis")
        .attr("transform", "translate(" + 0 + "," + legendPosY + ")").attr("class", "legendAxisG")
        .call(legendAxis)

        .call(g => gLegend.select(".domain").remove())
        .selectAll('text')
        .style('text-anchor', 'middle')
        .attr('transform', 'rotate(0)').style("font-size", "0.95em")

      const legendG = gLegend.selectAll("legendG")
        .data(this.taxes.map((d) => {
          return d.name
        }))

      const legendGEnter = legendG.enter().append("g")
        .attr("transform", (d) => {
          return "translate(" + legendScale(d) + "," + 0 + ")"
        })
        .attr("class", "legendG")

      legendGEnter.append("rect")
        .attr("width", legendWidth)
        .attr("height", 15)
        .attr("x", (d, i) => {
          return -legendWidth / 2
        })
        .attr("y", legendPosY - 15)
        .attr("class", "rectLegend")
        .style("fill", (d) => {
          return color(d)
        })
        .style("opacity", 0.9)
      legendG.merge(legendGEnter)

    },
    methods: {
      updatePlot(element) {
        const $this = this
        let keys = (this.taxes_selected.length == 0 ? this.taxes.map((d) => {
          return d.name
        }) : this.taxes_selected.map((d) => {
          return d.name
        }))
        const svg = this.svg[element]
        const classifiers = (this.classifiers_selected.length == 0 ? this.classifiers : this.classifiers_selected)
        const read_types = (this.read_types_selected.length == 0 ? this.read_types : this.read_types_selected)
        const color = this.color
        const order_taxes = ['strain', 'species', 'genus', 'family', 'order', 'class', 'phylum', 'superkingdom']
        keys = keys.sort(function (a, b) {
          return order_taxes.indexOf(b) - order_taxes.indexOf(a);
        });
        this.scaleXCore[element].domain(read_types)
        let scaleXCore = this.scaleXCore[element]
        const axisLegendDivList = d3.select("#xAxisLegendMaxed").select("ul")
        axisLegendDivList.html("")
        if (classifiers.length * read_types.length > this.maxXAxisAmount) {
          this.scaleXGroup[element].domain(d3.range(0, classifiers.length))
          this.mapMaxXAxis = true
          classifiers.forEach((d, i) => {
            axisLegendDivList.append("li").text(i + ". " + d)
          })

        } else {
          this.scaleXGroup[element].domain(classifiers)
          this.mapMaxXAxis = false
        }
        this.scaleXGroup[element].rangeRound([0, scaleXCore.bandwidth()])
        const scaleXGroup = this.scaleXGroup[element]
        this.scaleXInner[element].domain(keys)
        this.scaleXInner[element].rangeRound([0, scaleXGroup.bandwidth()])
        const scaleXInner = this.scaleXInner[element]
        const scaleY = this.scaleY[element]
        const g = d3.select("#svgG-" + element)


        const xAxis = this.xAxis[element]
        const xAxisCore = this.xAxisCore[element]
        const yAxis = this.yAxis[element]
        const yAxisDivision = this.yAxisDivision[element]

        g.selectAll(".x-axisG-" + element).remove()
        const xAxisG = g.selectAll(".x-axisG-" + element).data(read_types, (d) => {
          return d
        }).enter().append("g")
          .attr("transform", (d, i) => {
            return `translate(${this.margin.left + (i * scaleXCore.bandwidth())},${this.height - (this.margin.bottom) - this.margin.top})`
          })
          .attr("class", "x-axisG-" + element)
          .attr("id", "x-axisG-" + element)
          .call(xAxis)
          .call(g => g.select(".domain").remove())
          .selectAll('text')
          .style('text-anchor', 'middle')
          .attr('transform', 'rotate(0)').style("font-size", "0.85em");


        g.selectAll(".divisionAxisLine").remove()
        g.selectAll(".divisionAxisLine").data(read_types, (d) => {
          return d
        }).enter().append("g")
          .attr("class", "divisionAxisLine").call(yAxisDivision)
          .call((g) => {
            g.selectAll(".tick").remove()
          })

          .attr("transform", (d, i) => {
            return `translate(${this.margin.left + ((i + 1) * scaleXCore.bandwidth())}, ${-this.margin.top})`
          })


        g.select("#x-axisGCore-" + element).style("font-size", "0.6em").transition().duration(1000).call(xAxisCore)
        g.select("#y-axisG-" + element).transition().duration(1000).call(yAxis)
        let tooltip = d3.select("#pt_" + element)
        const chartData = this.chartData.filter((d) => {
          return classifiers.indexOf(d.classifier_name) > -1 && keys.indexOf(d.rank) > -1 && read_types.indexOf(d.read_type) > -1
        })
        const barG = g.selectAll(".bar-" + element).data(chartData, function (d) {
          return d.index + "-" + element + d.classifier + "-" + d.read_type
        })
          .join(
            function (enter) {
              return enter.append("g").attr("class", "bar-" + element)
                .attr("id", (d, i) => {
                  return ("bar-" + element + "-" + d.index + "-" + d.classifier_name)
                })
                .attr("transform", function (d) {
                  return "translate(" + scaleXCore(d.read_type) + "," + 0 + ")"
                })
                .append("g").attr("class", "bar-Grouped-" + element)
                .attr("transform", function (d) {
                  return "translate(" + scaleXGroup(($this.mapMaxXAxis ? classifiers.indexOf(d.classifier_name) : d.classifier_name)) + "," + scaleY(d[element]) + ")"
                })
                .on("mousemove", (d, i, n) => {

                  tooltip.html('<span> Classifier: ' + d.classifier_name + "<br> Rank: " + d.rank + "<br> " + element + ": " + d[element] + "<br> METAVal (AUPRC/L2): " + d.METAVal.toFixed(5) + '</span>')
                  // const side = (i <= read_types.length/2 ? 20 : -tooltip.style("width").replace("px", ""))
                  let tooltipWidth = parseFloat(tooltip.style("width").replace("px", ""))
                  let x = d3.mouse(n[i])[0] + scaleXGroup(($this.mapMaxXAxis ? classifiers.indexOf(d.classifier_name) : d.classifier_name)) + scaleXCore(d.read_type)
                  if (x + tooltipWidth + 1 <= $this.width) {
                    x += 20
                  } else {
                    x -= tooltipWidth
                  }
                  tooltip.style('top', () => {
                    return d3.mouse(n[i])[1] + scaleY(d[element]) + "px"
                  })
                    .style('left', () => {
                      return x + "px"
                    })
                    .style('opacity', 1)
                    .style("stroke-width", 5)
                    .transition()
                    .delay(200)
                  d3.selectAll(".blockRect").style("opacity", (v) => {
                    if (v.classifier_name == d.classifier_name && v.index == d.index && v.read_type === d.read_type) {
                      return 0.9
                    } else {
                      return 0.1
                    }
                  })
                  d3.selectAll(".bar-" + (element === "AUPRC" ? "L2" : "AUPRC")).select(".rectGrouped").style("fill-opacity", (v) => {
                    if (v.classifier_name == d.classifier_name && v.index == d.index && v.read_type === d.read_type) {
                      return 0.9
                    } else {
                      return 0.05
                    }
                  })
                })
                .on("mouseout", (d, i, n) => {
                  d3.selectAll(".rectGrouped").style("fill-opacity", 0.9)
                  d3.selectAll(".blockRect").interrupt()
                  d3.selectAll(".blockRect").style("opacity", 1)
                  tooltip.style('opacity', 0)
                }).append("rect")
                .attr("class", "rectGrouped")
                .attr("x", d => scaleXInner(d.rank))
                .attr("width", scaleXInner.bandwidth())
                .attr("height", (d) => {
                  return scaleY(0) - scaleY(d[element])
                })
                .attr("fill", (d) => {
                  return color(d.rank)
                })
                .style("opacity", 0.9)
            },
            function (update) {
              return update.transition().duration(700).attr('transform', (d, i) => {
                return "translate(" + scaleXCore(d.read_type) + "," + 0 + ")"
              })
                .selectAll(".bar-Grouped-" + element).attr("transform", function (d) {
                  return "translate(" + scaleXGroup(($this.mapMaxXAxis ? classifiers.indexOf(d.classifier_name) : d.classifier_name)) + "," + scaleY(d[element]) + ")"
                })
                .selectAll(".rectGrouped").attr("width", scaleXInner.bandwidth()).attr("x", d => scaleXInner(d.rank))
            },
            function (exit) {
              return exit.remove()
            }
          )
      },
      addTaxesTag(newTag) {
        const tag = {
          name: newTag,
        }
        this.taxes_selected.push(tag)
      },
      addClassifiersTag(newTag) {
        const tag = {
          name: newTag,
        }
        this.classifiers_selected.push(tag)
      },
      reset() {
        this.updatePlot("AUPRC")
        this.updatePlot("L2")
      },
    }

  };
</script>
<style>
  .btn-info {
    float: left !important;
    margin-bottom: 10px;
  }

  path {
    stroke-width: 0.4;
  }

  #logistics {
    display: block;
    width: 100%;
  }

  #logistics div {
    display: block;
    width: 100%;
  }

  .sortBar {
    width: 100% !important;
  }

  .divisionAxisLine line, .divisionAxisLine path {
    stroke: lightgrey;
    stroke-width: 1px;
    stroke-dasharray: 5;
    /*shape-rendering: crispEdges;*/
  }

  .y-axisG line, .y-axisG.domain {
    stroke: lightgrey;
    stroke-width: 2px;
    stroke-opacity: 0.3;
  }

  #xAxisLegendList {
    list-style: none;
    counter-reset: li 0;
    padding-left: 1.4em;
    text-align: left;
  }

  .x-axisGCore {
    font-size: 2000px;
  }

  #xAxisLegendList li {
    counter-increment: li
  }
</style>


