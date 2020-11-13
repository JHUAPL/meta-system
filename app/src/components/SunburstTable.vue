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
  <div class="SunburstTable">
    <b-container fluid>
      <b-row>
        <b-col sm="6" md="6" class="my-1">
          <span>Total Rows: <strong>{{data.length}}</strong></span>
        </b-col>
        <b-col sm="6" md="6" class="my-1" v-if="type==1">
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
              <b-form-input
                v-model="filter"
                type="search"
                id="filterInput"
                placeholder="Type to Search"
              ></b-form-input>
              <b-input-group-append>
                <b-button :disabled="!filter" @click="filter = ''">Clear</b-button>
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
          id="abu_table"
          stacked="md"
          :items="filteredData"
          :fields="fields"
          :current-page="currentPage"
          :per-page="perPage"
          :filter="filter"
          @filtered="updateRows"
          :filterIncludedFields="filterOn"
          :sort-by.sync="sortBy"
          :sort-desc.sync="sortDesc"
          :sort-direction="sortDirection"
          :sort-compare="mySortCompare"
          @row-clicked="clickRowHandler"
        >
          <template v-slot:cell(totalabu)="row">
            {{parseFloat(row.item.totalabu ==0 ? 0 : row.item.totalabu.toFixed(5))}}
          </template>
          <template v-if="type ===1" v-slot:cell(originalAbundance)="row">
            {{parseFloat(row.item.originalAbundance ==0 ? 0 : row.item.originalAbundance.toFixed(5))}}
          </template>
          <template v-if="type ===1" v-slot:cell(diff)="row">
            {{(parseFloat(row.item.totalabu - row.item.originalAbundance).toFixed(6)) }}
          </template>

        </b-table>
      </div>
    </b-row>
    <b-container fluid>
      <b-row class="">
        <b-col md="6" class="my-1">
          <b-pagination
            v-model="currentPage"
            :total-rows="totalRows"
            :per-page="perPage"
            align="fill"
            size="sm"
            class="my-0"
          ></b-pagination>
        </b-col>
        <b-col sm="5" md="6" class="my-1">
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
    name: "SunburstTable",
    props: ['data', 'taxes', 'height', 'type', 'baseline'],
    data() {
      return {
        totalRows: 1,
        currentPage: 1,
        perPage: 15,
        pageOptions: [5, 10, 15, 25, 100],
        sortBy: 'originalAbundance',
        sortDesc: true,
        sortDirection: 'asc',
        filter: null,
        filterOn: [],
        shown: false,
        filteredData: [],

        fields: [
          {key: 'name', label: 'Name', sortable: true, class: 'text-center'},
          {key: 'taxid', label: 'TaxID', sortable: true, class: 'text-center'},
          {key: 'rank', label: 'Rank', sortable: true, class: 'text-center'},
          {key: 'totalabu', label: 'Reported Abu', sortable: true}
        ],

      };
    },
    mounted() {
      if (this.type === 1) {
        this.fields.push({key: 'originalAbundance', label: 'Orig Abu', sortable: true, sortDirection: 'asc'})
        this.fields.push({key: 'diff', label: 'Difference', sortable: true})
      }
      this.totalRows = this.data.length
      d3.select(".abu_table_div").style("max-height", this.height * 0.8 + "px")
      this.filteredData = this.data
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
    watch: {
      filteredData(val) {
        this.totalRows = val.length
        this.showAllRows()
      }
    },

    methods: {
      clickRowHandler(record, index) {
        this.$emit('jumpFromTable', record.id)
      },
      updateRows(filteredItems) {
        this.totalRows = filteredItems.length
      },
      toggleTable(entry, text) {
        const val = this.shown[0]
        const baseline = this.baseline
        if (val == 'shown') {
          this.filteredData = this.data.filter((d) => {
            return baseline.indexOf(d.taxid) > -1
          })
        } else {
          this.filteredData = this.data
        }
      },
      showAllRows() {
        if (this.type == 1) {
          this.totalrows = this.data.length
          for (const entry of this.data) {
            entry._rowVariant = 'shown'
            if (entry.totalabu == 0 && entry.originalAbundance > 0) {
              entry._rowVariant = 'danger';
            } else if (this.baseline.indexOf(entry.taxid) > -1) {
              entry._rowVariant = 'primary';
            }
          }
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

        const taxes = this.taxes
        if (key === 'rank') {
          return taxes.findIndex(item => item.name === a.rank) - taxes.findIndex(item => item.name === b.rank);
        } else if (key == "diff") {
          const keyA = parseFloat(a['totalabu'] - a['originalAbundance'])
          const keyB = parseFloat(b['totalabu'] - b['originalAbundance'])
          return keyA < keyB ? -1 : keyA > keyB ? 1 : 0
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
  .table-hide {
    visibility: hidden;
  }

  .table-show {
    visibility: visible;
  }
</style>
