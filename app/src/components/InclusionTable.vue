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
  <div class="InclusionTable">
    <b-container fluid>
      <b-row>
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
      </b-row>
      <b-row class="">
        <b-col sm="3" md="6" class="my-1">
          <b-form-group
            label="Sort"
            label-cols-sm="2"
            label-align-sm="right"
            label-size="sm"
            label-for="sortBySelect"
            class="mb-0"
          >
            <b-input-group size="sm">
              <b-form-select v-model="sortBy" id="sortBySelect" :options="sortOptions" class="w-75">
                <template v-slot:first>
                  <option value="">-- none --</option>
                </template>
              </b-form-select>
              <b-form-select v-model="sortDesc" size="sm" :disabled="!sortBy" class="w-25">
                <option :value="false">Asc</option>
                <option :value="true">Desc</option>
              </b-form-select>
            </b-input-group>
          </b-form-group>
        </b-col>
        <b-col md="6" class="my-1">
          <b-form-group
            label="Filter"
            label-cols-sm="2"
            label-align-sm="right"
            label-size="sm"
            label-for="filterInput"
            class="mb-0"
          >
            <b-input-group size="sm">
              <b-input-group-append>
                <b-button :disabled="!filter" @click="filter_submitted = filter">Search</b-button>
              </b-input-group-append>
              <b-form-input
                v-model="filter"
                type="search"
                id="filterInput"
                placeholder="Type to Search"
              ></b-form-input>
              <b-input-group-append>
                <b-button :disabled="!filter" @click="filter_submitted = ''; filter = ''">Clear</b-button>
              </b-input-group-append>
            </b-input-group>
          </b-form-group>
        </b-col>
      </b-row>
    </b-container>
    <b-row>
      <div class="abu_table_div">
        <b-table
          show-empty
          small
          id="inclusion_table"
          stacked="md"
          :items="filteredData"
          :fields="fields"
          :current-page="currentPage"
          :per-page="perPage"
          :filter="filter_submitted"
          :filterIncludedFields="filterOn"
          @filtered="updateRows"
          :sort-by.sync="sortBy"
          :sort-desc.sync="sortDesc"
          :sort-direction="sortDirection"
          :sort-compare="mySortCompare"
          @row-hovered="hoverRowHighlight"
          @row-unhovered="leaveRowHighlight"
        >
          <template v-slot:cell(abundance)="row">
            {{parseFloat(row.item.abundance ==0 ? 0 : row.item.abundance.toFixed(5))}}
          </template>
          <template v-slot:cell(ratio)="row">
            <div style="opacity: 1; will-change: unset !important;" :id="row.index + 'inclusion' + row.item.taxid">
              <b-tooltip placement="left" style="color:white;" triggers="hover" custom-class="yess"
                         :target="row.index + 'inclusion' + row.item.taxid">{{row.item.classifier_inclusion.join("; ")}}
              </b-tooltip>
              <span>{{ row.item.ratio.toFixed(3)}}</span>
            </div>

          </template>


        </b-table>
      </div>
    </b-row>
    <b-container fluid>
      <b-row class="">
        <b-col md="5" class="my-1">
          <b-pagination
            v-model="currentPage"
            :total-rows="totalRows"
            :per-page="perPage"
            align="fill"
            size="sm"
            class="my-0"
          ></b-pagination>
        </b-col>
        <b-col sm="6" md="4" class="my-1">
          <b-form-group
            label="Per page"
            label-cols-sm="4"
            label-cols-md="5"
            label-cols-lg="6"
            label-align-sm="right"
            label-size="sm"
            label-for="perPageSelect"
            class="mb-0"
          >
            <b-form-select
              v-model="perPage"
              id="perPageSelect"
              size="sm"
              :options="pageOptions"
            ></b-form-select>
          </b-form-group>
        </b-col>

      </b-row>
    </b-container>
  </div>
</template>

<script>
  import * as d3 from 'd3'

  export default {
    name: "InclusionTable",
    props: ['tableData', 'type', 'ranks', 'height', 'inclusionSearchByRoot', 'inclusionSortByRoot', 'baseline'],
    data() {
      return {
        totalRows: 1,
        filteredData: [],
        currentPage: 1,
        perPage: 15,
        pageOptions: [5, 10, 15, 25, 100],
        sortBy: 'classifier',
        sortDesc: true,
        sortDirection: 'asc',
        filter: null,
        filter_submitted: null,
        filterOn: ['name', 'taxid', 'rank', 'classifier'],
        classifiers: [],
        read_types: [],
        shown: false,
        sorted_ranks: ['strain', 'species', 'genus', 'family', 'order', 'class', 'phylum', 'superkingdom'],
        fields: [
          {key: 'name', label: 'Name', sortable: true, class: 'text-center'},
          {key: 'taxid', label: 'TaxID', sortable: true, class: 'text-center'},
          {key: 'rank', label: 'Rank', sortable: true, class: 'text-center'},
          {key: 'abundance', label: 'Abu', sortable: true},
          {key: 'classifier', label: 'Classifier(s)', sortable: true, class: 'text-center'},
          {key: 'classifier_count', label: 'Taxid Calls', sortable: true},
          {key: 'ratio', label: 'Total Calls Ratio', sortable: true}
        ],

      };
    },
    watch: {
      tableData(val) {
        this.shown = false
        this.filteredData = val
        this.totalRows = val.length
      },
      inclusionSearchByRoot(val) {
        this.filter = val
        this.filter_submitted = val
      },
      inclusionSortByRoot(val) {
        this.sortBy = val
      }
    },
    mounted() {
      d3.select(".abu_table_div").style("max-height", this.height * 0.5 + "px")
      this.totalRows = this.tableData.length
      this.filteredData = this.tableData
      if (this.type == 1) {
        this.fields.push({key: 'read_type', label: 'Read Type', sortable: true})
        this.read_types = d3.map(this.filteredData, (d) => {
          return d.read_type
        }).keys()
      } else {
        this.read_types = ['real']
      }

    },
    computed: {
      filteredJobs() {
        return this.jobs.filter((j) => {
          return j.created_by.includes(this.user.email)
        })
      },
      sortOptions() {
        // Create an options list from our fields
        return this.fields
          .filter(f => f.sortable)
          .map(f => {
            return {text: f.label, value: f.key}
          })
      }
    },

    methods: {
      updateRows(filteredItems) {
        this.totalRows = filteredItems.length
      },
      toggleTable(entry, text) {
        const val = this.shown
        const baseline = this.baseline
        if (val == 'shown') {
          this.filteredData = this.tableData.filter((d) => {
            return baseline.indexOf(d.taxid) > -1
          })
        } else {
          this.filteredData = this.tableData
        }
      },
      hoverRowHighlight(element, index) {
        d3.selectAll(".indPoints")
          .style("opacity", (d) => {
            return (element.taxid == d.taxid ? 1 : 0)
          })
        // .sort(function (a, b) { // select the parent and sort the path's
        //     if (a.taxid != element.taxid){return -1}          // a is not the hovered element, send "a" to the back
        //     else {return 1};                             // a is the hovered element, bring "a" to the front
        // });
        this.hoverRow = d3.selectAll(".indPoints-" + element.taxid)

        this.hoverRow
          .transition().duration(400)
          .attr("r", 10)

        d3.select("#indPoint-" + element.taxid + "-" + element.classifier.replace("\.", "\\.") + "-" + (this.type == 1 ? element.read_type : ''))
          .transition().duration(400)
          .attr("r", 30)
      },
      leaveRowHighlight(element, index) {
        this.hoverRow.interrupt()
        this.hoverRow
          .transition().duration(400)
          .attr("r", 4)
        d3.selectAll(".indPoints")
          .style("opacity", 1)
      },
      mySortCompare(a, b, key, sortDesc, formatter, compareOptions, compareLocale) {
        // https://bootstrap-vue.org/docs/components/table
        function toString(value) {
          if (value === null || typeof value === 'undefined') {
            return ''
          } else if (value instanceof Object) {
            return Object.keys(value)
              .sort()
              .map(key => toString(value[key]))
              .join(' ')
          } else {
            return (String(value))
          }
        }

        const taxes = this.sorted_ranks
        if (key === 'rank') {
          return taxes.findIndex(item => item === a.rank) - taxes.findIndex(item => item === b.rank);
        } else {
          return a[key] < b[key] ? -1 : a[key] > b[key] ? 1 : 0
        }

      },

    }
  };
</script>

<style lang="scss">
  @import "~vue-multiselect/dist/vue-multiselect.min.css";
</style>
<style>
  .InclusionTable {
    padding-top: 10px;
    padding-right: 20px;
    padding-left: 20px;
  }

</style>
