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
    <div class="row centered" style=" padding-top: 30px">
      <div class="col-md-10">
        <div class="row" style="">
          <div class="col-md-6" style="overflow-x:auto; overflow-y: hidden;">
            <div id="bar_chart_container-L2" style="max-width:100000px">
              <div class="tooltipL2"></div>
            </div>
          </div>
          <div class="col-md-6" style="overflow-x:auto; overflow-y: hidden;">
            <div id="bar_chart_container-AUPRC" style="max-width: 100000px">
              <div class="tooltipAUPRC"></div>
            </div>
          </div>
        </div>
      </div>
      <div id='logistics' class="col-md-2" style="">
        <div class="sortBar" style="width:1000px;float:left">
          <button type="button" class="btn btn-info">Sort Bars on Y-axis</button>
        </div>
        <br><br>
        <div class="sortTax">
          <button type="button" class="btn btn-info">Sort Bars on Taxonomy Level</button>
        </div>
        <br><br>
        <hr>
        <div style="max-height: 150px; overflow:auto" class="alert alert-info">
          <span> Filter on taxonomy. Leave empty to use all taxonomy in the list</span>
        </div>
        <multiselect v-model="taxes_selected" tag-placeholder="Add this as new tag" placeholder="Select 0 or more"
                     :show-labels="false" label="name" track-by="name" :options="taxes" :multiple="true"
                     :taggable="true" @tag="addTaxesTag" @input="reset()"></multiselect>
        <br><br>
        <div class="reset">
          <button type="button" @click="resetFull()" class="btn btn-info">Reset</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';

  export default {
    name: 'Chart',
    props: ['chartData', 'chartType', 'taxes', 'classifiers', 'containerHeight'],
    components: {Multiselect},
    data() {
      return {
        chart: null,
        taxes_selected: [{name: "species"}],
        container: {AUPRC: null, L2: null},
        dimensions: {},
        svg: {L2: null, AUPRC: null},
        viewBox_width: null,
        viewBox_height: null,
        svg_width: null,
        svg_height: null,
        aspect: null,
        chart_width: null,
        chart_height: null,
        margin: null,
        scaleY: {L2: null, AUPRC: null},
        scaleX: {L2: null, AUPRC: null},
        xAxis: {L2: null, AUPRC: null},
        yAxis: {L2: null, AUPRC: null},
        cat: "combined",
        data: null,
        color: null,
        thisSort: {
          L2: {sortAscending: false, sortTaxAscending: false},
          AUPRC: {sortAscending: false, sortTaxAscending: false}
        }
      }
    },
    watch: {
      chartData(val) {
        if (!this.data && val) { //This is too hacky
          this.startPlot(val)
        }
      }
    },
    mounted() {
      this.windowHeight = window.innerHeight
      this.windowWidth = window.innerWidth

      this.height = this.containerHeight
      this.startPlot(this.chartData)

    },
    methods: {

      startPlot(val) {
        if (this.chart != null) this.chart.remove();
        this.data = val
        this.color = d3.scaleOrdinal()
          .range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00", 'black'])
        this.makePlot(val, 'L2');
        this.makePlot(val, 'AUPRC');
      },
      addTaxesTag(newTag) {
        const tag = {
          name: newTag,
        }
        this.taxes_selected.push(tag)
      },
      reset() { //Deprectated, potentially explore later
        this.cat = "combined"
        this.updatePlot(this.data, "L2")
        this.updatePlot(this.data, "AUPRC")
      },
      resetFull() {
        this.taxes_selected = []
        this.reset()
      },
      resize() {
        var targetWidth = parseInt(this.container.L2.style("width"))
        if (this.svg.AUPRC) {
          this.svg.AUPRC.attr("width", targetWidth)
          this.svg.AUPRC.attr("height", Math.round(targetWidth / this.aspect))
        }
        if (this.svg.L2) {
          this.svg.L2.attr("width", targetWidth)
          this.svg.L2.attr("height", Math.round(targetWidth / this.aspect))
        }
        if (this.svg.L2) {
          this.tooltip_pos('L2')
        }
      },
      get_dimensions(chart_id) {
        let svg = d3.select("#bar_chart-" + chart_id)
        this.svg[chart_id] = svg
        this.viewBox_width = parseInt(svg.style("width"))
        this.viewBox_height = this.containerHeight
        this.aspect = this.viewBox_width / this.viewBox_height;
        this.svg_width = this.viewBox_width
        this.svg_height = this.viewBox_height
        this.margin = {
          top: 0.02 * this.svg_height,
          bottom: 0.25 * this.svg_height,
          left: 0.12 * this.svg_width,
          right: 0
        }
        this.chart_width = this.svg_width - this.margin.left - this.margin.right;
        this.chart_height = this.svg_height - this.margin.top - this.margin.bottom;
      },
      tooltip_pos(chart_id) {
        const scaleX = this.scaleX[chart_id]
        const scaleY = this.scaleY[chart_id]
        this.get_dimensions(chart_id)
        scaleX.range([this.margin.left, this.chart_width])
        d3.selectAll(".gRect-" + chart_id).on('mousemove', (d, i, n) => {
          d3.select('#' + chart_id + '-rect' + d.index).attr('fill', 'steelblue')
          d3.select('.tooltip' + chart_id).html('<span> Rank: ' + d.rank + '<br>' + 'L2: ' + d.L2 + '<br>Classifier: ' + d.classifier_name + '<br>AUPRC: ' + d.AUPRC + '<br>Read Type: ' + d.read_type + '</span>')
            .style('top', () => {
              return d3.mouse(n[i])[1] + scaleY(d[chart_id]) - 10 + "px"
            })
            .style('left', () => {
              return d3.mouse(n[i])[0] + scaleX(d.combined) + "px"
            })
            .style('opacity', 1)
            .transition()
            .delay(200)
        })
          .on('mouseout', (d, i) => {
            d3.select('#' + chart_id + '-rect' + d.index).attr('fill', 'goldenrod')
            d3.select('.tooltip' + chart_id).style('opacity', 0)
          })
      },
      updatePlot(chartData, chart_id) {
        this.get_dimensions(chart_id)
        this.data = chartData
        const chart_width = this.chart_width
        const chart_height = this.chart_height
        const svg_width = this.svg_width
        const svg_height = this.svg_height
        const margin = this.margin
        const svg = this.svg[chart_id]
        this.scaleX[chart_id].range([margin.left, chart_width])
        this.scaleY[chart_id].range([chart_height, 0])
        const taxes_selected = this.taxes_selected.map((d) => {
          return d.name
        })
        const scaleX = this.scaleX[chart_id]
        const scaleY = this.scaleY[chart_id]
        let cat = this.cat
        const $this = this
        //Update X and Y Axis
        scaleX.domain(this.filtering())
        this.scaleX[chart_id] = scaleX
        const xAxis = d3.axisBottom()
          .scale(scaleX)

        const yAxis = d3.axisLeft()
          .scale(scaleY)
          .ticks(10);
        d3.select("#x-axis-" + chart_id).transition().duration(1000).call(xAxis)

        const svg_bottom_axis = d3.select("#x-axis-" + chart_id)
        const text = svg_bottom_axis.selectAll("text")
          .attr("id", (d, i) => {
            return "xaxis-text-" + d.replace(/ /g, "-") + "-" + chart_id
          })
          .style('text-anchor', 'end')
          .attr("transform", "rotate(-50)");


        setTimeout(function (d) {
          text.style("font-size", (d, i) => {
            // return Math.min(($this.svg_height - $this.chart_height), ($this.svg_height - $this.chart_height)/d3.select("#xaxis-text-"+d.replace(/ /g,"-")+"-"+chart_id).node().getComputedTextLength()*12)+"px"
            return "0.8em"
          })
        }, 30)


        const taxes = (this.taxes_selected.length == 0 ? this.taxes.map((d) => {
          return d.name
        }) : taxes_selected)
        chartData = this.chartData.filter((d) => {
          return taxes.indexOf(d.rank) > -1
        })
        // d3.selectAll(".gRect-"+chart_id).remove()
        let g = svg.selectAll('.gRect-' + chart_id).data(chartData, function (d) {
          return d.index + "-" + chart_id
        })
          .join(
            function (enter) {
              return enter.filter(function (d) {
                if (taxes_selected.length == 0) {
                  return d
                } else {
                  return taxes_selected.indexOf(d.rank) != -1
                }
              }).append('g')
                .attr('transform', (d, i) => {
                  let xPos = scaleX(d.combined)
                  return 'translate(' + xPos + ',' + scaleY(d[chart_id]) + ')'
                })
                .attr('id', (d, i) => {
                  return 'g' + i
                })
                .attr('class', 'gRect-' + chart_id)
                .append('rect').attr('width', scaleX.bandwidth())
                .attr('class', 'gRectrect-' + chart_id)

                .attr('id', (d, i) => {
                  return chart_id + '-rect' + d.index
                })
                .attr('height', (d) => {
                  return chart_height - scaleY(d[chart_id])
                })
                .attr('fill', 'goldenrod')
                .style('stroke-width', 0.5)
                .style('stroke', 'black')
            },
            function (update) {
              return update.transition().duration(1000).attr('transform', (d, i) => {
                return 'translate(' + scaleX(d.combined) + ',' + scaleY(d[chart_id]) + ')'
              })
                .selectAll('.gRectrect-' + chart_id).attr('width', scaleX.bandwidth())
            },
            function (exit) {
              return exit.remove()
            }
          )

        this.tooltip_pos(chart_id)

        //////////////////////////////////////////////////////////////////////////
        // Update the graphs with sorting feature
        d3.select('.sortBar button').on('click', () => {
          this.thisSort.sortAscending = !this.thisSort.sortAscending
          this.sorted("standard", this.data)
        })
        d3.select('.sortTax button').on('click', () => {
          this.thisSort.sortTaxAscending = !this.thisSort.sortTaxAscending
          this.sorted("tax", this.data)
        })


      },
      filtering() {
        const data = this.data
        const taxes_selected = this.taxes_selected.map((d) => {
          return d.name
        })
        let domX = data.filter((d) => {
          return taxes_selected.indexOf(d.rank) != -1 || taxes_selected.length == 0
        })
          .map(function (d) {
            return d.combined
          })
        return domX
      },
      sorted(type, data, chart_id) {
        const taxes = ['strain', 'species', 'genus', 'family', 'order', 'class', 'phylum', 'superkingdom']
        let sorted = ''
        const chart_ids = ['L2', 'AUPRC']
        for (var i = 0; i < chart_ids.length; i++) {
          const chart_id = chart_ids[i]
          if (type == "tax") {
            if (this.thisSort.sortTaxAscending) {
              this.cat = "sortedTax"
              data.sort((a, b) => d3.ascending(taxes.indexOf(a.rank), taxes.indexOf(b.rank)))
            } else {
              this.cat = "combined"
              data.sort((a, b) => d3.ascending(a.index, b.index))
            }
          } else {
            if (this.thisSort.sortAscending) {
              this.cat = "sortedY"
              data.sort((a, b) => d3.ascending(a[chart_id], b[chart_id]))
            } else {
              this.cat = "combined"
              data.sort((a, b) => d3.ascending(a.index, b.index))
            }
          }
          this.updatePlot(this.data, chart_id)
        }
        d3.select('.tooltipL2').style('opacity', 0)
        d3.select('.tooltipAUPRC').style('opacity', 0)
      },
      makePlot(chartData, chart_id) {
        this.container[chart_id] = null
        this.svg[chart_id] = null
        var container = d3.select('#bar_chart_container-' + chart_id).style("height", this.height + "px")
        this.container[chart_id] = container
        let container_width = container.style("width").replace("px", "")
        let container_height = container.style("height").replace("px", "")
        var svg = d3.select("#bar_chart_container-" + chart_id).append("svg").attr("height", container_height).attr("width", container_width).attr("id", "bar_chart-" + chart_id)


        this.dimensions = {}
        this.viewBox_width = null,
          this.viewBox_height = null
        this.svg_width = null
        this.svg_height = null
        this.aspect = null
        this.chart_width = null
        this.chart_height = null
        this.margin = null
        this.scaleY[chart_id] = null
        this.scaleX[chart_id] = null
        this.xAxis[chart_id] = null
        this.yAxis[chart_id] = null
        this.thisSort = {sortAscending: false, sortTaxAscending: false}
        //Rdefine the dimensions in case of resizing of window
        this.get_dimensions(chart_id)
        const $this = this
        //Redefine all state variables to local constants
        const aspect = this.aspect
        const viewBox_width = this.viewBox_width
        const viewBox_height = this.viewBox_height
        const svg_width = this.svg_width
        const svg_height = this.svg_height
        const margin = this.margin
        const chart_width = this.chart_width
        const chart_height = this.chart_height
        let cat = this.cat


        //create an array of all available taxa
        let domX = chartData.map(function (d) {
          return d[cat]
        })

        //Define the scales for x and y axis. Set domain to available taxa
        const scaleX = d3.scaleBand().domain(domX).range([margin.left, chart_width]).padding(0.2)
        const scaleY = d3.scaleLinear().range([chart_height, 0 + this.margin.top])
        if (chart_id == "L2") {
          scaleY.domain([0, 1])
        } else {
          scaleY.domain([0, d3.extent(chartData, (d) => {
            return d[chart_id]
          })[1]])
        }

        const xAxis = d3.axisBottom()
          .scale(scaleX)

        const yAxis = d3.axisLeft()
          .scale(scaleY)
          .ticks(10);

        //assign globally to state
        this.scaleY[chart_id] = scaleY
        this.scaleX[chart_id] = scaleX
        this.xAxis[chart_id] = xAxis
        this.yAxis[chart_id] = yAxis

        const y_axis_label = svg.append("text")
          .text(chart_id).style("text-anchor", "middle")
          .attr("transform", function (d) {
            return "translate(" + (margin.left / 3) + "," + (chart_height / 2) + ") rotate(-90)"
          })
          .style("font-size", '0.8em')
        //Define the x and y axis for left and bottom positions
        let svg_bottom_x_axis = svg.append('g')
          .attr('class', 'x-axis').attr("id", "x-axis-" + chart_id).attr('transform', 'translate( ' + '0' + ',' + chart_height + ')')
        // .call(xAxis)

        let bottom_x_axis_text = svg_bottom_x_axis.selectAll('text')
          .attr("id", (d, i) => {
            return "xaxis-text-" + d.replace(/ /g, "-") + "-" + chart_id
          })
        // .call(xAxis)

        const svg_left_y_axis = svg.append('g').attr("class", "y-axis").attr("id", "y-axis-" + chart_id).attr('transform', 'translate( ' + margin.left + ',' + '0' + ')')
          .call(yAxis).style("font-size", "0.9em");


        this.svg_left_y_axis = svg_left_y_axis
        this.svg_bottom_x_axis = svg_bottom_x_axis

        //Update the Plot, populating rectangles and axis ticks
        this.updatePlot(chartData, chart_id)

        //If there is any change in the window size, scale the svg based on viewbox dimensions
        svg.attr("viewBox", "0 0 " + viewBox_width + " " + viewBox_height)
          .attr("perserveAspectRatio", "xMinYMid")
          .call(this.resize);
        d3.select(window).on("resize." + container.attr("id"), this.resize);
        return ''
      }
    }

  };
</script>
<style>
  div.tooltipL2, div.tooltipAUPRC {
    position: absolute;
    text-align: left;
    padding: 2px;
    font: 14px sans-serif;
    border-radius: 8px;
    pointer-events: none;
    background: white;
    text-transform: none;
  }

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
</style>


