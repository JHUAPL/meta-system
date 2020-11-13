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
  <div class="Resources">
    <div class="row">
      <div class="col-md-12">
        <div style="max-width: 10000000; border: 0px solid black; " ref="pcMetrics" id="pcMetrics"></div>
      </div>
      <div class="col-md-9" >
        <div class="resources_table_div" v-if="renderTable">
          <b-table
            show-empty
            small
            ref="resources_table"
            id="resources_table"
            stacked="md"
            :items="resourcesData"
            :fields="fields"
            :filter="filter"
            :filter-function="filterEntries"
            :filterIncludedFields="filterOn"
            :sort-by.sync="sortBy"
            :sort-desc.sync="sortDesc"
            :sort-direction="sortDirection"
            :sort-compare="mySortCompare"
            @row-hovered="hoverRowHighlight"
            @row-unhovered="leaveRowHighlight"
          >
            <template v-slot:cell(show)="row">
              <b-form-checkbox-group v-model="entries_selected">
                <b-form-checkbox
                  v-bind:value="row.item"
                  :id="'row-'+row.item.classifier + '-' + row.item.read_type"
                  @change="displayData(row.item.classifier + '-' + row.item.read_type)"
                >
                </b-form-checkbox>
              </b-form-checkbox-group>

            </template>
            <template v-slot:cell(wall_clock_time)="row">
              <span v-if="timeViews_selected.key=='s'">{{ (row.item.wall_clock_time) }}</span>
              <span v-else>{{ durationHMS(row.item.wall_clock_time) }}</span>
            </template>
            <template v-slot:cell(cpu_time)="row">
              <span v-if="timeViews_selected.key=='s'">{{ (row.item.cpu_time) }}</span>
              <span v-else="">{{ durationHMS(row.item.cpu_time) }}</span>
            </template>
            <template v-slot:cell(max_memory_MBs)="row">
              <span >{{ parseMemory(row.item.max_memory_MBs) }}</span>
            </template>
            <template  v-slot:cell(legend)="row">
              <svg :id="'rowLegend-'+row.item.classifier + '-' + row.item.read_type"
                   :style="{width: '15px', height: '15px', background: color(row.item.classifier)}"></svg>
            </template>
          </b-table>

        </div>
      </div>
      <div class="col-md-3" id="pcMetricsLegend" ref="pcMetricsLegend">
        <b-container fluid>
            <b-row class="">
              <b-form-checkbox
                v-model="allSelected"
                :indeterminate="indeterminate"
                @change="toggleAllEntries"
              >Toggle Showing All Entries
              </b-form-checkbox>
            </b-row>
            <b-row style="padding-top: 20px">
              <label for="timeView">Time format</label>
              <multiselect v-model="timeViews_selected" name='timeView' :allow-empty="false" 
             tag-placeholder="Add this as new tag" :preselect-first="true" placeholder="Select 1" :show-labels="false"
             :options="timeViews"  track-by="name" label="name"  :taggable="false"></multiselect>
            </b-row>
            <b-row style="padding-top: 20px">
              <b-col sm="12" style="text-align:center">
                <b-form-group
                  label=""
                  label-cols-sm="12"
                  label-align-sm="right"
                  label-size="sm"
                  label-for="filterAdd"
                  class="mb-0"
                >
                  <b-input-group size="sm">
                    <b-input-group-append>
                      <label for="filterSelectedType" style="padding-right: 20px; text-align:center; margin:auto">Filter: </label>
                    </b-input-group-append>
                    <b-input-group-append>
                      <multiselect v-model="tableFilterInclusionTypes_selected" name='filterSelectedType' :allow-empty="false" 
                       tag-placeholder="Add this as new tag" :preselect-first="true" placeholder="Select 1" :show-labels="false"
                       :options="tableFilterInclusionTypes"  track-by="name" label="name"  :taggable="false"></multiselect>
                    </b-input-group-append>
                  </b-input-group>
                </b-form-group>
              </b-col>
              <b-col sm="12" v-for="n in filterCount">
                <b-form-group
                  label=""
                  label-cols-sm="12"
                  label-align-sm="right"
                  label-size="sm"
                  label-for="filterInput"
                  class="mb-0"
                >
                  <b-input-group size="sm">
                    <b-form-input
                      v-model="filter[n-1]"
                      type="search"
                      id="filterInput"
                      placeholder="Type to Search"
                    ></b-form-input>
                    <b-input-group-append>
                      <b-button  @click="clearFilter(n-1)">Clear</b-button>
                    </b-input-group-append>
                    <b-input-group-append v-if="n > 1">
                      <b-button :id="'removeButtonFilter-'+(n-1)"
                              variant="outline-dark"
                              size="md"
                              v-b-tooltip.hover.top
                              title="Remove Search Field"
                              @click="removeField(n-1)"
                      >
                        <font-awesome-icon icon="minus-circle" size="sm"/>
                      </b-button>
                    </b-input-group-append>
                    <b-input-group-append v-else>
                      <b-button  :id="'addButtonFilter'"
                              variant="outline-dark"
                              size="md"
                              v-b-tooltip.hover.top
                              title="Add an additional filter term"
                              @click="filterCount+=1"
                      >
                        <font-awesome-icon icon="plus" size="sm"/>
                      </b-button>
                    </b-input-group-append>
                  </b-input-group>
                </b-form-group>
              </b-col>
            </b-row>
        </b-container>
        <br/>
      </div>
      <div class="parallel_tooltip" id="pt" style="opacity:0"></div>
    </div>
  </div>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';
  import {convert_seconds, filterEntriesTable} from '@/controller/index'
export default {
    name: 'Resources',
    components: {Multiselect},
    props: ['resourcesData', 'chartType', 'containerHeight', 'pipelines', 'metrics', 'resourcesSortByRoot', 'type'],
    data() {
      return {
        svg: {},
        aspect: null,
        entries_selected: [],
        entriesOnly: [],
        chart_width: null,
        chart_height: null,
        indeterminate: true,
        margin: null,
        start: false,
        scaleY: {},
        scaleX: {},
        xAxis: {},
        yAxis: {},
        allSelected: true,
        labelPadding: 40,
        dragging: {},
        sortDirection: 'desc',
        filter: [],
        filterOn: [],
        sortBy: 'classifier',
        sortDesc: false,
        currentPage: 1,
        perPage: 5,
        filterCount: 1,
        timeViews_selected: {name: 'Hours:Minutes:Seconds', key: 'h:m:s'},
        timeViews: [{name: 'Hours:Minutes:Seconds', key: 'h:m:s'}, {name: 'Seconds Only', key: 's'}],
        tableFilterInclusionTypes_selected: {name: 'One or more terms must match', key: 'or'},
        tableFilterInclusionTypes: [{name: 'Must include all terms', key: 'and'}, {name: 'One or more terms must match', key: 'or'}],
        renderTable: false,
        pageOptions: [5, 10, 15, 25, 100],
        selectedEntries: {},
        fields: [
          {key: 'cpu_time', label: 'CPU Time (h:m:s)', sortable: true, class: 'text-center'},
          {key: 'wall_clock_time', label: 'Wall Clock Time (h:m:s)', sortable: true, class: 'text-center'},
          {key: 'max_memory_MBs', label: 'Max Memory (GB)', sortable: true, class: 'text-center'},
          {key: 'classifier', label: 'Classifier', sortable: true, sortDirection: 'asc'},
          // {key: 'read_type', label: 'Read Type', sortable: true, sortDirection: 'asc'},
          {key: 'show', label: 'Show', sortable: false},
          {key: 'legend', label: 'Legend', sortable: false},
        ] 
      }
    },
    watch: {
      resourcesSortByRoot(val) {
        this.sortBy = val.text
        this.sortDesc = val.direction
      },
      entries_selected(newVal) {
        const selectedEntries = {}
        for (let i = 0; i < newVal.length; i++) {
            selectedEntries[newVal[i].classifier + "-" + newVal[i].read_type] = true         
        }
        d3.selectAll(".pc_lines").classed("hidden", (d,i)=>{
          if (d.classifier +"-"+d.read_type in selectedEntries){
            return false
          } else{
            return true
          }
        })
        if (newVal.length == 0) {
          this.indeterminate = false;
          this.all = false;
        } else if (newVal.length == this.resourcesData.length) {
          this.indeterminate = false;
          this.allSelected = true;
        } else {
          this.indeterminate = true;
          this.allSelected = false;
        }
      },
    },
    mounted() {
      const $this = this
      const arr = this.resourcesData
      this.entries_selected = this.resourcesData
      this.height = this.containerHeight * 0.7
      d3.select(".resources_table_div").style("height", this.height * 0.7 + "px")
      this.width = parseFloat(d3.select("#pcMetrics").style("width").replace("px", ""))
      this.margin = {
        top: 0.05 * this.height,
        bottom: 0.1 * this.height,
        left: 0.1 * this.width,
        right: this.width * 0.02
      }
      const margin = this.margin
      this.start = true
      d3.select("#pcMetrics").style("height", this.height + "px")
      this.type == 1 ? this.fields.splice(3,0, {key: 'read_type', label: 'Read Type', sortable: true}) : '';

      this.renderTable = true
      const width = this.width
      const height = this.height
      const rightside = this.width
      const bottomside = this.height
      let svg = d3.select("#pcMetrics").append("svg").attr("id", "pcSVG").attr('viewBox', `${this.margin.right} ${this.margin.top} ${rightside} ${bottomside}`);

      const color = d3.scaleOrdinal().range(d3.schemeCategory10.slice(1))
        .domain([...new Set(this.resourcesData.map((d) => {
          return d.classifier
        }))])
      this.color = color
      let scaleX = d3.scaleBand().rangeRound([this.margin.left, width + this.margin.left + this.margin.right])
      let scaleY = {}
      let dragging = {}
      let labelPadding = this.labelPadding
      const read_types = [...new Set(this.resourcesData.map((d) => {
        return d.read_type
      }))]
      this.read_types = read_types

      let line = d3.line(),
        axis = d3.axisLeft(),
        background, foreground,
        dimensions
      this.line = line
      // Extract the list of dimensions and create a scale for each.
      scaleX.domain(dimensions = d3.keys(arr[0]).filter(function (d) {
        return d !== "classifier" && (d !== "read_type" ? scaleY[d] = d3.scaleLinear()
          .domain([0, 1.1 * d3.max(arr, function (p) {
            return +p[d];
          })])
          .range([height - margin.bottom, margin.top + labelPadding]) : scaleY[d] = d3.scaleBand()
          .domain(read_types)
          .rangeRound([height - margin.bottom, margin.top + labelPadding]));
      }));
      this.scaleX = scaleX
      this.scaleY = scaleY
      this.dimensions = dimensions
      // Add grey background lines for context.
      background = svg.append("g")
        .attr("class", "background")
        .selectAll("path")
        .data(arr)
        .enter().append("path")
        .attr("d", this.path);
      var parallel_tooltip = d3.select("#pt")
      // Add blue foreground lines for focus.
      foreground = svg.append("g")
        .attr("class", "foreground")
        .selectAll("path")
        .data(arr)
        .enter().append("path").attr("class", "pc_lines").attr("id", function (d) {
          return d["classifier"] + "-" + d['read_type'];
        })
        .attr("d", this.path)
        .style("stroke", function (d) {
          return color(d.classifier)
        })
        .on("mousemove", (d, i, n) => {
          d3.select("#" + d.classifier + "-" + d.read_type).style("stroke-width", 8)
          d3.select('.parallel_tooltip').html('<span> Classifier: ' + d.classifier + ($this.type == 1 ? "<br> Read Type: " + d.read_type : '') + "<br> Max Memory (GB): " + $this.parseMemory(d.max_memory_MBs)  + " (GB)<br> Wall Clock Time (h:m:s): " + $this.durationHMS(d.wall_clock_time)+ "<br> CPU Time (h:m:s): " + d.cpu_time + '</span>')
            .style('top', () => {
              return d3.mouse(n[i])[1] + "px"
            })
            .style('left', () => {
              return d3.mouse(n[i])[0] + "px"
            })
            .style('opacity', 1)
            .style("stroke-width", 5)
            .transition()
            .delay(200)
        })
        .on('mouseout', (d, i) => {
          d3.select("#" + d.classifier + "-" + d.read_type).style("stroke-width", 2)
          d3.select('.parallel_tooltip').style('opacity', 0)
        })
      this.foreground = foreground
      this.background = background
      this.svg = svg
      this.dragging = dragging
      // Add a group element for each dimension.
      var g = svg.selectAll(".dimension")
        .data(dimensions)
        .enter().append("g")
        .attr("class", "dimension")
        .attr("transform", function (d) {
          return "translate(" + scaleX(d) + ")";
        })
        .call(d3.drag()
          .on("start", function (d) {
            dragging[d] = scaleX(d);
            background.attr("visibility", "hidden");
          })
          .on("drag", function (d) {
            dragging[d] = Math.min(width, Math.max(0, d3.event.x));
            foreground.attr("d", $this.path);
            dimensions.sort(function (a, b) {
              return $this.position(a) - $this.position(b);
            });
            scaleX.domain(dimensions);
            g.attr("transform", function (d) {
              return "translate(" + $this.position(d) + ")";
            })
          })
          .on("end", function (d) {
            delete dragging[d];
            $this.transition(d3.select(this)).attr("transform", "translate(" + scaleX(d) + ")");
            $this.transition(foreground).attr("d", $this.path);
            background
              .attr("d", $this.path)
              .transition()
              .delay(50)
              .duration(0)
              .attr("visibility", null);
          }));
      // Add an axis and title.
      g.append("g")
        .attr("class", "pc_axis")
        .each(function (d) {
          d3.select(this).call(axis.scale(scaleY[d]).ticks(6));
        })
        .append("rect").attr("x", 20).attr("y", 0).attr("width", 100).attr("height", 300)
      g.append("text")
        .style("text-anchor", "middle")
        .attr("y", labelPadding)
        .attr("x", 9)
        .style('font-size', 14 + 'px')
        .text(function (d) {
          return d;
        });
      // Add and store a brush for each axis.
      g.append("g")
        .attr("class", "brush")
        .each(function (d) {
          d3.select(this).call(scaleY[d].brush = d3.brushY().extent([[-10, margin.top + labelPadding], [10, height - margin.bottom]])
            .on("start", $this.brushstart)
            .on("brush", $this.brush)
            .on("end", $this.brush))
        })
        .selectAll("rect")
        .attr("x", -8)
        .attr("width", 16);

      foreground.each((d) => {
        d3.select("#rowLegend-" + d.classifier + "-" + d.read_type).style("background", () => {
          return color(d.classifier)
        })
      })
    },
    methods: {
      toggleAllEntries(checked) {
        this.entries_selected = checked ? this.resourcesData.slice() : [];
      },
      durationHMS(secs){
          return convert_seconds(secs)
      },
      parseMemory(memory){
          const gb = (memory && memory > 0  ? (memory / 1000 ).toFixed(3) : 0)
          return gb
      },
      removeField(n){
        if (this.filterCount > 1) {
          this.filter.splice(n, 1);
          this.filterCount -=1
        }
      },
      filterEntries(row, filter){
        return filterEntriesTable(row, filter, this.tableFilterInclusionTypes_selected.key, this.filterOn)
      },
      clearFilter(n){
        this.$set(this.filter, n, '')        
      },
      displayData(element) {
        d3.select("#" + element).style("opacity", (d) => {
          if (!d3.select("#" + element).classed("fade") && d3.select("#" + element).classed("hidden")) {
            d3.select("#" + element).classed("hidden", false)
          } else {
            d3.select("#" + element).classed("hidden", true)
          }
        })
      },
      hoverRowHighlight(element, index) {
        this.hoverRow = d3.select("#" + element.classifier + "-" + element.read_type)
        this.hoverRow.style("stroke-width", 8)
      },
      leaveRowHighlight(element, index) {
        this.hoverRow.style("stroke-width", 2)
      },
      sortOptions() {
        // Create an options list from our fields
        return this.fields
          .filter(f => f.sortable)
          .map(f => {
            return {text: f.label, value: f.key}
          })
      },
      // Returns the path for a given data point.
      path(d) {
        const $this = this
        return this.line(this.dimensions.map(function (p) {
          let yPos;
          if (p == 'read_type') {
            yPos = $this.scaleY[p](d[p]) + $this.scaleY[p].bandwidth() / 2
          } else {
            yPos = $this.scaleY[p](d[p])
          }
          return [$this.position(p), yPos];
        }));
      },
      position(d) {
        let v = this.dragging[d];
        return v == null ? this.scaleX(d) : v;
      },
      transition(g) {
        return g.transition().duration(50);
      },
      brushstart() {
        d3.event.sourceEvent.stopPropagation();
      },

      // Handles a brush event, toggling the display of foreground lines.
      brush() {
        let actives = [];
        //filter brushed extents
        this.svg.selectAll(".brush")
          .filter(function (d) {
            return d3.brushSelection(this);
          })
          .each(function (d) {
            actives.push({
              dimension: d,
              extent: d3.brushSelection(this)
            });
          });
        const $this = this
        //set un-brushed foreground line disappear
        this.foreground.classed("fade", function (d, i) {
          return !actives.every(function (active) {
            let dim = active.dimension;
            if (dim !== "read_type") {
              if (active.extent[0] <= $this.scaleY[dim](d[dim]) && $this.scaleY[dim](d[dim]) <= active.extent[1]){
                // d3.select("#"+d.classifier +"-"+d.read_type).classed('hidden', false)
                return true
              } else{
                return false
              };
            } 
            else {
              if(active.extent[0] <= ($this.scaleY[dim](d[dim]) + $this.scaleY[dim].bandwidth() / 2) && ($this.scaleY[dim](d[dim]) + $this.scaleY[dim].bandwidth() / 2) <= (active.extent[1])){
                // d3.select("#"+d.classifier +"-"+d.read_type).classed('hidden', false)                
                return true
              } else{                
                return false
              }
            }
          });
        });
      },
      mySortCompare(a, b, key) {
        return false
      },

    }

  };
</script>
<style>
  .foreground path.fade {
    /*stroke: grey;*/
    stroke-opacity: .00;
    stroke-width: 10px;
    display:block;
  }

  .parallel_tooltip {
    position: absolute;
    text-align: center;
    max-width: 400px;
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

  #pcMetrics path {
    fill: none;
  }

.foreground path.hidden {
    stroke: #000;
    stroke-opacity: .00;
    display:none;
  }

  .background {
    /*stroke: grey;*/
    opacity: 0.01;
    fill: none;
  }

  #pcMetrics path {
    stroke-width: 2px;
    fill: none;
  }

  #pcMetricsLegend {
    /*  margin-top: auto;
      margin-bottom: auto;
    */ /*vertical-align: middle;*/
  }

  .pc_lines {
    stroke-width: 30px;
    fill: none;
  }

  .pc_axis {
    font-size: 13px;
  }

  .resources_table_div {
    overflow: auto;
    padding-left: 40px;
  }

</style>


