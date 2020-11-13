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
  <div style="">
    <div class="row">
      <div class="col-md-12" style="width: 100%; border: 0px solid black; " ref="histogramAbu"
           :id="'histogramAbu-'+type">
      </div>
    </div>
    <div class="row">
      <div class="col-md-4 offset-1">
        <span>xScale</span>
        <multiselect deselect-label="Can't de-select" :allow-empty="false" v-model="xScaleType" :options="scaleTypes"
                     style="padding:0px; margin:0px;"
                     :searchable="false"
        >
        </multiselect>
      </div>
      <div class="col-md-4 offset-1">
        <span>yScale</span>
        <multiselect deselect-label="Can't de-select" :allow-empty="false" v-model="yScaleType" :options="scaleTypes"
                     style="padding:0px; margin:0px;"
                     :searchable="false"
        >
        </multiselect>
      </div>
    </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';

  export default {
    name: 'AbundanceCounts',
    props: ['fullData', 'filteredData', 'abuThresholdMin', 'abuThresholdMax', 'type', 'minAbu', 'maxAbu'],
    components: {Multiselect},
    data() {
      return {
        height: 900,
        width: 900,
        boxSpacing: 0,
        boxWidth: 0,
        border: 0,
        xAxis: null,
        minMaxAbu: null,
        scaleX: null,
        scaleY: null,
        yAxis: null,
        yScaleType: 'linear',
        xScaleType: 'log',
        scaleTypes: ['log', 'linear'],
        abundanceThresholdSlider: 0

      }
    },
    mounted() {
      this.chartHeight = 400
      this.height = Math.min(this.chartHeight)
      this.width = this.$refs.histogramAbu.clientWidth
      const $this = this
      this.margin = {
        top: 0.1 * this.chartHeight,
        bottom: 0.1 * this.chartHeight,
        left: 0.1 * this.width,
        right: 0.05 * this.width
      }
      const border = this.border
      const margin = this.margin
      this.svg = d3.select("#histogramAbu-" + this.type).append("svg")
        .attr('viewBox', `0 0 ${this.width + this.margin.left + this.margin.right} ${this.height + this.margin.top + this.margin.bottom}`)
      const data = this.fullData
      this.makeHistogram(data, this.filteredData, this.abuThresholdMin, this.abuThresholdMax)
    },
    watch: {
      filteredData(val) {
        this.updateHistogram(this.fullData, val, this.abuThresholdMin, this.abuThresholdMax)
      },
      fullData(val) {
        this.makeHistogram(val, this.filteredData, this.abuThresholdMin, this.abuThresholdMax)
      },
      yScaleType(val) {
        this.updateHistogram(this.fullData, this.filteredData, this.abuThresholdMin, this.abuThresholdMax)
      },
      xScaleType(val) {
        this.updateHistogram(this.fullData, this.filteredData, this.abuThresholdMin, this.abuThresholdMax)
      },
      minAbu(val) {
        this.minMaxAbu[0] = val
        this.updateHistogram(this.fullData, this.filteredData, this.abuThresholdMin, this.abuThresholdMax)
      },
      maxAbu(val) {
        this.minMaxAbu[1] = val
        this.updateHistogram(this.fullData, this.filteredData, this.abuThresholdMin, this.abuThresholdMax)
      },
    },


    methods: {

      updateHistogram(chartData, filteredData, abuThresholdMin, abuThresholdMax) {
        const $this = this
        const minMaxAbu = this.minMaxAbu
        if (this.xScaleType == "log") {
          this.scaleX = d3.scaleLog()
            .range([this.margin.left, this.width - this.margin.right])
            .domain(minMaxAbu)
        } else {
          this.scaleX = d3.scaleLinear()
            .range([this.margin.left, this.width - this.margin.right])
            .domain(minMaxAbu)
        }
        const minmaxx = d3.extent(filteredData, (d) => {
          return ($this.type != 'sunburst' ? d.abundance : d.totalabu)
        })

        const scaleX = this.scaleX
        const thresholds = scaleX.ticks(40)
        const bandwidth = 100
        const bins = d3.histogram()
          .domain(scaleX.domain())
          .thresholds(thresholds)
          .value((d) => {
            return ($this.type != 'sunburst' ? d.abundance : d.totalabu)
          })
          (filteredData)
          .filter(d => d.length !== 0)
        let i = 0;
        bins.forEach((d) => {
          i += d.length
        })

        if (this.yScaleType == "log") {
          this.scaleY = d3.scaleLog().range([this.height - this.margin.bottom, this.margin.top]).domain([this.minAbu, d3.max(bins, d => d.length) / filteredData.length])
        } else {
          this.scaleY = d3.scaleLinear().range([this.height - this.margin.bottom, this.margin.top]).domain([this.minAbu, d3.max(bins, d => d.length) / filteredData.length])
        }
        let scaleY = this.scaleY
        const svg = this.svg

        this.yAxis.call(d3.axisLeft(scaleY))
        this.xAxis.call(d3.axisBottom(scaleX))
        svg.selectAll(".abundanceLine")
          .datum(bins)
          .attr("d", d3.area()
            .x(function (d) {
              return scaleX(d.x0) + 1
            })
            .y0(function (d) {
              return scaleY(minMaxAbu[0])
            })
            .y1(function (d) {
              return scaleY(d.length / filteredData.length)
            })
          )
        d3.select("#abuThresholdBar-" + $this.type)
          .attr("x", function (d) {
            return scaleX($this.abuThresholdMin)
          })
          .attr("width", scaleX((minMaxAbu[1] < this.abuThresholdMax ? minMaxAbu[1] : this.abuThresholdMax)) - scaleX(this.abuThresholdMin))
        d3.select("#abuThresholdBarRight-" + $this.type)
          .attr("x", function (d) {
            return scaleX((minMaxAbu[1] < $this.abuThresholdMax ? minMaxAbu[1] : $this.abuThresholdMax)) - 2.5
          })
        d3.select("#abuThresholdBarLeft-" + $this.type)
          .attr("x", function (d) {
            return scaleX($this.abuThresholdMin) - 2.5
          })


      },

      makeHistogram(chartData, filteredData, abuThresholdMin, abuThresholdMax) {
        // Features of the histogram
        const margin = this.margin
        const $this = this
        let svg = this.svg
        svg.html("")

        const minMaxAbu = [this.minAbu, this.maxAbu]
        this.minMaxAbu = minMaxAbu
        let scaleX = d3.scaleLinear()
          .range([this.margin.left, this.width - this.margin.right])
          .domain(minMaxAbu)
        const xAxis = svg.append("g")
          .style("font-size", "1em")
          .attr("transform", "translate(0," + (this.height - this.margin.bottom) + ")")
        this.xAxis = xAxis


        const yAxis = svg.append("g")
          .style("font-size", "1em")
          .attr("transform", "translate(" + this.margin.left + "," + 0 + ")")
        this.yAxis = yAxis

        svg.append("path")
          .attr("fill", "#666699")
          .attr("class", "abundanceLine")
          // .attr("stroke", "#119164")
          .attr("fill-opacity", 0.6)
          .attr("stroke-width", 2.5)


        const dragMax = d3.drag()
          .on("drag", draggedMax)
        const dragMin = d3.drag()
          .on("drag", draggedMin)
        const dragAll = d3.drag()
          .on("drag", dragged)

        const top = this.margin.top
        svg.append("rect")
          .attr("y", this.margin.top)
          .style("stroke", "grey")
          .style("opacity", 0.2)
          .attr("height", (this.height - this.margin.top - this.margin.bottom))
          .attr("id", "abuThresholdBar-" + $this.type)
          .attr("cursor", "move")
          .call(dragAll)

        const svgDragRight = svg.append("rect")
          .attr("y", top)
          .style("stroke", "grey")
          .style("opacity", 0.0)
          .attr("width", 5)
          .attr("height", (this.height - this.margin.top - this.margin.bottom))
          .attr("id", "abuThresholdBarRight-" + $this.type)
          .attr("cursor", "ew-resize")
          .call(dragMax)
        ;

        const svgDragLeft = svg.append("rect")
          .attr("y", top)
          .style("stroke", "grey")
          .style("opacity", 0.0)
          .attr("width", 5)
          .attr("height", (this.height - this.margin.top - this.margin.bottom))
          .attr("id", "abuThresholdBarLeft-" + $this.type)
          .attr("cursor", "ew-resize")
          .call(dragMin)
        ;
        this.updateHistogram(chartData, filteredData, abuThresholdMin, abuThresholdMax)
        svg.append("text").text("Abundance")
          .attr("text-anchor", "middle")
          .style("font-size", 15)
          .attr("transform", "translate(" + (this.width / 2) + "," + (this.height + this.margin.top - this.margin.bottom / 2) + ")")

        svg.append("text").text("Frequency")
          .style("font-size", 15)
          .attr("transform", "translate(" + (this.margin.left / 3) + "," + (this.margin.top / 2) + ") rotate(0)")

        function dragstarted(d) {
          d3.select(this).raise().attr("stroke", "black");
        }

        function draggedMax(d) {
          const scaleX = $this.scaleX
          const xcoord = Math.min($this.width - $this.margin.right, Math.max(scaleX($this.abuThresholdMin), d3.event.x));
          d3.select("#abuThresholdBarRight-" + $this.type)
            .attr("x", xcoord)
          d3.select('#abuThresholdBar-' + $this.type)
            .attr("width", xcoord - scaleX($this.abuThresholdMin))
          if (xcoord > $this.margin.left & xcoord < $this.width - $this.margin.right) {
            $this.$emit('stageUpdateAbuThresholdMax', $this.scaleX.invert(xcoord))
          } else if (xcoord == $this.margin.left) {
            $this.$emit('stageUpdateAbuThresholdMax', $this.scaleX.invert($this.margin.left))
          } else {
            $this.$emit('stageUpdateAbuThresholdMax', $this.scaleX.invert($this.width - $this.margin.right))
          }
        }

        function draggedMin(d) {
          const scaleX = $this.scaleX
          const xcoord = Math.max($this.margin.left, Math.min(scaleX($this.abuThresholdMax), d3.event.x));
          d3.select("#abuThresholdBarLeft-" + $this.type)
            .attr("x", xcoord)
          d3.select('#abuThresholdBar-' + $this.type)
            .attr("x", xcoord)
            .attr("width", scaleX($this.abuThresholdMax) - xcoord)
          if (xcoord > $this.margin.left & xcoord < $this.width - $this.margin.right) {
            $this.$emit('stageUpdateAbuThresholdMin', $this.scaleX.invert(xcoord))
          } else if (xcoord == $this.margin.left) {
            $this.$emit('stageUpdateAbuThresholdMin', $this.scaleX.invert($this.margin.left))
          } else {
            $this.$emit('stageUpdateAbuThresholdMin', $this.scaleX.invert($this.width - $this.margin.right))
          }
        }

        function dragged(d) {
          const scaleX = $this.scaleX
          if ($this.abuThresholdMin && $this.abuThresholdMax){
            const width = scaleX($this.abuThresholdMax) - scaleX($this.abuThresholdMin)
            let xcoord
            if (!Math.min($this.width - $this.margin.right - width, d3.event.x)){
              xcoord = $this.margin.left
            } else {
              xcoord = Math.max($this.margin.left, Math.min($this.width - $this.margin.right - width, d3.event.x))
            }
            d3.select(this)
              .attr("x", xcoord)
            const xcoordLeft = d3.select(this).attr("x")
            const xcoordRight = parseFloat(d3.select(this).attr("x")) + parseFloat(d3.select(this).attr("width"))
            d3.select("#abuThresholdBarLeft-" + $this.type)
              .attr("x", xcoordLeft)
            d3.select("#abuThresholdBarRight-" + $this.type)
              .attr("x", xcoordRight)

            $this.$emit('stageUpdateAbuThresholdMin', $this.scaleX.invert(xcoordLeft))
            $this.$emit('stageUpdateAbuThresholdMax', $this.scaleX.invert(xcoordRight))
          }
        }

        function dragended(d) {
          d3.select(this).attr("stroke", 10);
        }


      },
    }
  };
</script>
<style>
  .innerBlock rect {
    border-radius: 10px;
  }

  .divisionAxisLine line, .divisionAxisLine path {
    stroke: lightgrey;
  }
</style>


