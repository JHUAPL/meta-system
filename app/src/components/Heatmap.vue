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
  <div style="overflow-y:auto; overflow-x:hidden">
    <div class="row">
      <div class="col-md-12" style="width: 100%; border: 0px solid black; " ref="heatmapDIVAUPRC" id="heatmapDIVAUPRC">
      </div>
      <div class="col-md-12" style="width: 100%; border: 0px solid black; " ref="heatmapDIVL2" id="heatmapDIVL2">
      </div>
      <div class="alert alert-info col-md-12">
        <span>Higher AUPRC and lower L2 are preferred</span>
      </div>
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';

  export default {
    name: 'Heatmap',
    props: ['chartData', 'chartType', 'taxes', 'classifiers', 'containerHeight', 'read_types'],
    components: {Multiselect},
    data() {
      return {
        height: 900,
        width: 900,
        boxSpacing: 0,
        boxWidth: 0,
        border: 0,
        svgs: {L2: null, AUPRC: null},

        scaleXInner: {L2: null, AUPRC: null},
        scaleXGroup: null,
        xAxisInner: {L2: null, AUPRC: null},
        xAxisGroup: {L2: null, AUPRC: null},


        divisionYScale: {L2: null, AUPRC: null},
        yAxisDivision: {L2: null, AUPRC: null},

        scaleY: null,
        yAxis: {L2: null, AUPRC: null},

        colors: {"start": "#fff", "end": '#666699'},
        ranks: []
      }
    },
    mounted() {
      this.chartHeight = (this.containerHeight * 0.55)
      this.height = Math.min(this.chartHeight)
      this.width = this.$refs.heatmapDIVAUPRC.clientWidth
      const $this = this
      this.margin = {
        top: 0.1 * this.chartHeight,
        bottom: 0.25 * this.chartHeight,
        left: 0.15 * this.width,
        right: 0.2 * this.width
      }
      const border = this.border
      const taxes = $this.taxes.map((d) => {
        return d.name
      })
      this.ranks = taxes
      const margin = this.margin
      const boxSpacingX = (this.width - margin.left - margin.right) / this.taxes.length
      const boxSpacingY = (this.height - margin.bottom - margin.top) / this.classifiers.length
      const boxWidth = ((this.width - margin.left - margin.right) / this.taxes.length) - border
      this.boxWidth = boxWidth
      // const bottomPosition = Math.min((this.height - margin.top-margin.bottom), this.classifiers.length * 70)
      const boxHeight = (((this.height - margin.top - margin.bottom) / this.classifiers.length) - border)
      this.boxHeight = boxHeight
      this.scaleY = d3.scaleOrdinal().domain($this.classifiers)
        .range($this.classifiers.map((d, i) => {
          const spacing = boxHeight / 2;
          return (i * boxHeight) + spacing + margin.top
        }))

      this.scaleXGroup = d3.scaleBand().domain(taxes)
        .range([this.margin.left, this.width - this.margin.right])
      // .rangeRound($this.taxes.map((d,i)=>{return i*boxSpacingX + margin.left}))


      const elements = ['AUPRC', 'L2']
      for (let i = 0; i < elements.length; i++) {
        const element = elements[i]
        const scaleXInner = d3.scaleBand()
        this.scaleXInner[element] = scaleXInner

        const divisionYScale = d3.scaleBand()
          .domain(taxes)
          .range([this.margin.left, this.width - this.margin.right])

        const yAxisDivision = d3.axisLeft()
          .scale(divisionYScale).tickSizeOuter(0)
          .ticks(0);

        this.yAxisDivision[element] = yAxisDivision
        this.startHeatmap(this.chartData, elements[i], i)

      }
    },


    methods: {

      startHeatmap(data, element, inc) {
        const $this = this
        const classifiers = this.classifiers
        const read_types = this.read_types
        const taxes = this.ranks
        const margin = this.margin
        d3.select("#heatmapDIV" + element).style("height", this.chartHeight + "px")
        const svg = d3.select("#heatmapDIV" + element).append("svg").attr("id", "heatmapSVG-" + element)
          .attr('viewBox', `0 0 ${this.width} ${this.chartHeight}`)
        this.svgs[element] = svg
        this.g = svg.append("g").attr("class", "svgG")
        const scaleXInner = this.scaleXInner[element]
        const scaleY = this.scaleY
        const scaleXGroup = this.scaleXGroup
        scaleXInner.domain(read_types).range([0, scaleXGroup.bandwidth()])
        this.scaleColor = d3.scaleLinear().range([$this.colors.start, $this.colors.end]).domain(element == 'AUPRC' ? [0, d3.max($this.chartData, (d) => {
          return d[element]
        })] : [d3.max($this.chartData, (d) => {
          return d[element]
        }), 0])
        const g = this.g
        const block = g.selectAll(".block").data(data, function (d) {
          return d
        })
        const blockEnter = block.enter().append("g")
          .attr("transform", (d) => {
            return "translate(" + $this.scaleXGroup(d.rank) + "," + ($this.scaleY(d.classifier_name) - $this.boxHeight / 2) + ")"
          }).attr("class", function (d) {
            return "block"
          }).attr("id", function (d) {
            return "g-" + element + "-" + d.rank + "-" + d.classifier_name
          })

          .attr('class', "blockRect")
          .style("rx", "2px")
          .style("stroke", "black")
          .style("stroke-width", "0.5")
          .append("g")
          .attr("transform", (d, i) => {
            return `translate(${scaleXInner(d.read_type)}, ${0})`
          })
          .attr("class", "innerBlock")
          .append("rect")
          .attr("fill", (d) => {
            return $this.scaleColor(d[element])
          })
          .attr("width", this.boxWidth).attr("height", this.boxHeight)
          .attr("id", (d) => {
            return d.classifier_name + "-" + d.rank + "-" + d.read_type
          })
          .attr("width", this.boxWidth / read_types.length)
          .attr("height", this.boxHeight)

          .on("mouseover", function (d) {
            d3.select(this).style("fill-opacity", 0.3)
          }).on("mouseout", function (d) {
            d3.select(this).style("fill-opacity", 1)
          })
          .append("title").text(function (d) {
            return "Classifier: " + d.classifier_name + "\nRank: " + d.rank + "\nRead Type: " + d.read_type +
              "\n" + element + ": " + d[element]
          })

        const legendScale = d3.scaleLinear()
          .domain(element == 'AUPRC' ? [0, d3.max($this.chartData, (d) => {
            return d[element]
          })] : [d3.max($this.chartData, (d) => {
            return d[element]
          }), 0])
          .range([0, this.height * 0.5]);
        const legendAxis = d3.axisRight()
          .scale(legendScale)
          .ticks(4);

        const legendAxisG = g.append("g").attr("id", "legendAxis")
          .attr("transform", "translate(" + (this.width - this.margin.right + 5 + this.margin.right / 4) + "," + (this.margin.top + 10) + ")").attr("class", "legendAxis")
          .call(legendAxis)
          .selectAll('text')
          .style('text-anchor', 'start')
          .attr('transform', 'rotate(0)').style("font-size", "1em");

        const legend = d3.select("#heatmapSVG-" + element).append("defs").append("linearGradient")
          .attr("id", "linear-gradient")
          .attr("x1", "0%")
          .attr("y1", "0%")
          .attr("x2", "0%")
          .attr("y2", "100%");
        legend.append("stop")
          .attr("offset", "0")
          .attr("stop-color", $this.colors.start)

        legend.append("stop")
          .attr("offset", "100")
          .attr("stop-color", $this.colors.end)

        g.append("rect")
          .attr("width", this.margin.right / 4)
          .attr("height", this.height * 0.5)
          .attr("x", this.width - this.margin.right + 5)
          .attr("y", this.margin.top + 10)
          .style("fill", "url(#linear-gradient)");

        g.append("text")
          .style("font-size", "1em")
          .style("text-anchor", "middle")
          .text(element).attr("x", this.width - this.margin.right / 2)
          .attr("y", this.margin.top)

        const xAxis = d3.axisTop()
          .scale($this.scaleXGroup).tickSizeOuter(0).ticks(read_types.length)
        const xAxisInner = d3.axisBottom()
          .scale($this.scaleXInner[element]).tickSizeOuter(0).ticks(classifiers.length).tickPadding(10);

        const yAxis = d3.axisLeft()
          .scale($this.scaleY)
          .ticks(classifiers.length);
        const xAxisG = g.append("g").attr("class", "xAxis")
          .attr("transform", "translate(" + 0 + "," + (this.margin.top) + ")")
          .call(xAxis)
          .selectAll('text')
          .style('text-anchor', 'middle')
          .attr('transform', 'rotate(0)').style("font-size", "0.9em");
        if (inc + 1 == 2) {
          g.selectAll('.xAxisInner').remove()
          const xAxisGInner = g.selectAll('.xAxisInner')
            .data(taxes, (d) => {
              return d
            }).enter().append("g").attr("class", "xAxisInner")
            .attr("transform", (d, i) => {
              return `translate(${this.margin.left + (i * scaleXGroup.bandwidth())},${this.height - ($this.margin.bottom)})`
            })
            .call(xAxisInner)
            .selectAll('text')
            .style('text-anchor', 'end')
            .attr("dx", "-1.0em")
            .attr("dy", "-1.0em")
            .attr('transform', 'rotate(-70)').style("font-size", "1em");

        }

        const yAxisG = g.append("g").attr("class", "yAxis")
          .attr("transform", "translate(" + this.margin.left + "," + 0 + ")")
          .style("stroke-width", 0)
          .call(yAxis)
          .call(g => g.select(".domain").remove())
          .selectAll('text')
          .style('text-anchor', 'end')
          .attr('transform', 'rotate(0)').style("font-size", "1.2em")

        const yAxisDivision = this.yAxisDivision[element]
        g.selectAll(".divisionAxisLine").remove()
        d3.select("#heatmapSVG-" + element).selectAll(".divisionAxisLine").data(taxes, (d) => {
          return d
        }).enter().append("g")
          .attr("class", "divisionAxisLine").call(yAxisDivision)
          .call((g) => {
            g.selectAll(".tick").remove()
          })
          .attr("transform", (d, i) => {
            return `translate(${this.margin.left + ((i + 1) * scaleXGroup.bandwidth())}, ${-this.height})`
          })

      }

    }

  };
</script>
<style>
  .innerBlock rect {
    border-radius: 10px;
  }

  .divisionAxisLine line, .divisionAxisLine path {
    stroke: lightgrey;
    /*stroke-width: 15px;*/
    /*stroke-dasharray: 5;*/
    /*fill: black;*/
    /*z-index: 99999;*/
    /*shape-rendering: crispEdges;*/
  }
</style>


