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
  <div class="ComparisonTable">
    <!-- <h4>Comparison Table</h4> -->
    <b-container fluid>
      <b-row class="">
        <b-col sm="7" class="">
          <b-col sm="12" style="text-align:center">
            <b-form-group
              label=""
              label-align-sm="center"
              label-size="sm"
              label-for="filterAdd"
              class="mb-0"
            >
              <b-input-group size="lg">
                <b-input-group-append>
                  <label style="text-align:center; margin:auto; padding-right: 20px">Filter search by: </label>
                </b-input-group-append>
                <b-input-group-append>
                  <multiselect v-model="tableFilterTypes_selected" name='filterSelectedType' :allow-empty="false" 
                   tag-placeholder="Add this as new tag" :preselect-first="true" placeholder="Select 1" :show-labels="false"
                   :options="tableFilterTypes"  track-by="name" label="name"  :taggable="false"></multiselect>
                </b-input-group-append>
              </b-input-group>
            </b-form-group>
          </b-col>
        </b-col>
        <b-col sm="5" >
          <b-form-group
            label-cols-sm="12"
            label-align-sm="right"
            label-size="sm"
            label-for="filterInput"
            class="mb-0"
            v-for="n in filterCount"
          >
            <b-input-group size="sm">
              <b-input-group-append>
                <b-button v-if="n == 1 && tableType =='inclusion'" :disabled="!filter" @click="updateFilters()">Search</b-button>
              </b-input-group-append>
              

              <b-form-input v-if="tableType !='inclusion'"
                v-model="filter[n-1]"
                type="search"
                id="filterInput"
                placeholder="Type to Search"
              ></b-form-input>
              <b-form-input v-else
                v-model="filter_submitted[n-1]"
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
    <b-row>
      <div class="comparison_table_div">
        <b-table
          show-empty
          small
          id="comparison_table"
          stacked="md"
          :items="tableData"
          :fields="fields"
          :current-page="currentPage"
          :per-page="perPage"
          :filter="filter"
          :class="[tableType =='sunburst' ? 'cursor' : '']"
          @filtered="updateRows"
          :filter-function="filterEntries"
          :filterIncludedFields="filterOn"
          :sort-by.sync="sortBy"
          :sort-desc.sync="sortDesc"
          :sort-direction="sortDirection"
          :sort-compare="mySortCompare"
          @row-hovered="hoverRowHighlight"
          @row-unhovered="leaveRowHighlight"
          @row-clicked="clickRowHandler"
        >
          <template v-if="tableType == 'grouped'" v-slot:cell(L2)="row">
            {{row.item.L2.toFixed(5)}}
          </template>
          <template v-if="tableType == 'grouped'" v-slot:cell(AUPRC)="row">
            {{row.item.AUPRC.toFixed(5)}}
          </template>
          <template v-if="tableType == 'grouped'" v-slot:cell(METAVal)="row">
            {{row.item.METAVal.toFixed(5)}}
          </template>
          <template v-if="tableType == 'grouped'" v-slot:cell(classifier_inclusion)="row">
            {{row.item.classifier_inclusion.join(",")}}
          </template>

          <template  v-if="tableType == 'inclusion'" v-slot:cell(abundance)="row">
            {{parseFloat(row.item.abundance ==0 ? 0 : row.item.abundance.toFixed(5))}}
          </template>
          <template  v-if="tableType == 'inclusion'" v-slot:cell(ratio)="row">
            <div style="opacity: 1; will-change: unset !important;" :id="row.index + 'inclusion' + row.item.taxid">
              <b-tooltip placement="left" style="color:white;" triggers="hover" custom-class="yess"
                         :target="row.index + 'inclusion' + row.item.taxid">{{row.item.classifier_inclusion.join("; ")}}
              </b-tooltip>
              <span>{{ row.item.ratio.toFixed(3)}}</span>
            </div>

          </template>
          <template v-if="tableType=='sunburst'"v-slot:cell(totalabu)="row">
            {{parseFloat(row.item.totalabu ==0 ? 0 : row.item.totalabu.toFixed(5))}}
          </template>
          <template v-if="type ===1 && tableType=='sunburst'" v-slot:cell(originalAbundance)="row">
            {{parseFloat(row.item.originalAbundance ==0 ? 0 : row.item.originalAbundance.toFixed(5))}}
          </template>
          <template v-if="type ===1 && tableType=='sunburst'" v-slot:cell(diff)="row">
            {{(parseFloat(row.item.totalabu - row.item.originalAbundance).toFixed(6)) }}
          </template>


        </b-table>
      </div>
    </b-row>
    <b-container fluid>
      <b-row class="">
        <b-col sm="6" class="my-1">
          <b-pagination
            v-model="currentPage"
            :total-rows="totalRows"
            :per-page="perPage"
            align="fill"
            size="sm"
            class="my-0"
          ></b-pagination>
        </b-col>
        <b-col sm="6"  class="my-1">
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
        <b-col sm="12" class="my-1">
          <b-form-group
            label="Sort"
            label-align-sm="center"
            label-cols-sm="4"
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

      </b-row>
    </b-container>
  </div>
</template>

<script>
  import * as d3 from 'd3'
  import Multiselect from 'vue-multiselect';
  import {filterEntriesTable} from '@/controller/index'
  
  export default {
    name: "ComparisonTable",
    components: {Multiselect},
    props: ['tableData', 'ranks', 'height', 'read_types', 'sortByRoot', 'searchByRoot',
    'filterOn', 'fields', 'defaultSortBy', 'tableType', 'type'],
    data() {
      return {
        totalRows: 1,
        currentPage: 1,
        perPage: 15,
        pageOptions: [5, 10, 15, 25, 100],
        sortDesc: true,
        sortDirection: 'asc',
        filter: [],
        filter_submitted: [],
        sortBy:null,
        sorted_ranks: ['strain', 'species', 'genus', 'family', 'order', 'class', 'phylum', 'superkingdom'],
        tableFilterTypes_selected: {name: 'Match one or more terms', key: 'or'},
        tableFilterTypes: [{name: 'Must include all terms', key: 'and'}, {name: 'Match one or more terms', key: 'or'}],
        filterCount: 1
      };
    },
    watch: {
      tableData(val) {
        this.totalRows = val.length
      },
      // sortByRoot(val) {
      //   this.sortBy = val
      // },
      // searchByRoot(val) {
      //   this.filter = val
      // }
    },
    mounted() {
      d3.select(".comparison_table_div").style("max-height", this.height * 1.5 + "px")
      this.totalRows = this.tableData.length
      this.sortBy  = this.defaultSortBy //due to prop mutation limitations, need to define a brand new sort column as default
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
      hoverRowHighlight(element, index) {
        if (this.tableType =='comparison'){
          d3.selectAll(".rectGrouped").style("opacity", (d) => {
            if (d.classifier_name == element.classifier_name && element.index == d.index && element.read_type === d.read_type) {
              return 1
            } else {
              return 0.3
            }
          })
          d3.selectAll(".blockRect").style("opacity", (d) => {
            if (d.classifier_name == element.classifier_name && element.index == d.index && element.read_type === d.read_type) {
              return 1
            } else {
              return 0.1
            }
          })
        }
        else if (this.tableType =='inclusion'){
          d3.selectAll(".indPoints")
          .style("opacity", (d) => {
            return (element.taxid == d.taxid ? 1 : 0)
          })
          this.hoverRow = d3.selectAll(".indPoints-" + element.taxid)

          this.hoverRow
            .transition().duration(400)
            .attr("r", 10)

          d3.select("#indPoint-" + element.taxid + "-" + element.classifier.replace("\.", "\\.") + "-" + (this.type == 1 ? element.read_type : ''))
            .transition().duration(400)
            .attr("r", 30)
        } 
      },
      clearFilter(n){
        this.$set(this.filter, n, '') 
        this.$set(this.filter_submitted, n, '') 
      },
      removeField(n){
        if (this.filterCount > 1) {
          this.filter.splice(n, 1);
          this.filterCount -=1
        }
      },
      clickRowHandler(record, index) {
        if(this.tableType=='sunburst'){
          this.$emit('jumpFromTable', record.id)
        }
      },
      updateFilters(){
        for (let i =0; i < this.filter_submitted.length; i++){
          this.$set(this.filter, i, this.filter_submitted[i])
        }
      },
      updateRows(filteredItems) {
        this.totalRows = filteredItems.length
      },
      filterEntries(row, filter){
        return filterEntriesTable(row, filter, this.tableFilterTypes_selected.key, this.filterOn)
      },
      leaveRowHighlight(element, index) {
        if(this.tableType == 'inclusion'){
          this.hoverRow.interrupt()
          this.hoverRow
          .transition().duration(400)
          .attr("r", 4)
          d3.selectAll(".indPoints")
          .style("opacity", 1)
        } else if (this.tableType =='comparison'){
          d3.selectAll(".rectGrouped").style("opacity", 0.8)
          d3.selectAll(".blockRect").style("opacity", 0.8)
        }
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
  .ComparisonTable {
    padding-top: 10px;
    padding-right: 20px;
    padding-left: 50px;
    width:100%;
  }
</style>
