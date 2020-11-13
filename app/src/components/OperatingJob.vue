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
  <div class="jobs">
    <div class="row" center-align-items>
      <div class="col-md-12 col-centered">
        <h1>Operating Jobs</h1>
      </div>
    </div>
    <div class="row center" center-align-items>
      <div class="col-md-12 col-centered">
        <div class="table-wrap">
          <div>
            <router-link v-bind:to="{ name: 'addJob' }" class="">Add New Job</router-link>
          </div>
          <b-container fluid>
            <b-row class="justify-content-center center-align-items">
              <b-col md="2" class="my-1">
                <b-pagination
                  v-model="currentPage"
                  :total-rows="totalRows"
                  :per-page="perPage"
                  align="fill"
                  size="sm"
                  class="my-0"
                ></b-pagination>
              </b-col>
              <b-col sm="3" md="2" class="my-1">
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
              <b-col md="4" class="my-1">
                <b-form-group
                  label="Filter"
                  label-cols-sm="1"
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
              <b-col md="1" class="my-1">
                <b-dropdown
                  id="dropdown-dropup"
                  dropdown
                  size="sm"
                  label-size="sm"
                  class="mb-0"
                >
                  <template v-slot:button-content>
                    Show {{showing}}
                  </template>
                  <b-dropdown-item @click="hidden = false; showing='Jobs'; getJobs(hidden)">Jobs</b-dropdown-item>
                  <b-dropdown-item @click="hidden = true; showing='Hidden Jobs'; getJobs(hidden)">Hidden Jobs
                  </b-dropdown-item>
                </b-dropdown>
              </b-col>
            </b-row>
          </b-container>

          <b-table
            show-empty
            small
            stacked="md"
            :items="jobs"
            :fields="fields"
            :current-page="currentPage"
            :per-page="perPage"
            :filter="filter"
            :filterIncludedFields="filterOn"
            :sort-by.sync="sortBy"
            :sort-desc.sync="sortDesc"
            :sort-direction="sortDirection"
            :sort-compare="mySortCompare"
            @filtered="onFiltered"
          >

            <template v-slot:cell(created_datetime)="row">
                <span>{{row.item.created_datetime | moment('MMMM Do YYYY, h:mm a' )}} UTC</span>
            </template>

            <template v-slot:cell(read_types)="row">
              <span>{{[row.item.read_types].join(', ')}} </span>
            </template>

            <template v-slot:cell(abundance_tsv)="row">
              <div v-if="row.item.fastq">
                <span>{{row.item.fastq}} </span>
              </div>
              <div v-else>
                <span>{{row.item.abundance_tsv}} </span>
              </div>
            </template>

            <template v-slot:cell(process_time)="row">
              <div v-if="!row.item.completed_datetime || !row.item.started_datetime ">
              </div>
              <div v-else="(row.item.child_jobs_completed)== row.item.total_child_jobs">
                <span>{{ processTime(row.item.completed_datetime, row.item.started_datetime) }}  </span>
              </div>
            </template>

            <template v-slot:cell(progress)="row">
              {{ [row.item.child_jobs_completed, row.item.total_child_jobs].join(" of ") }}
            </template>
            <template v-slot:cell(progress)="row">
              {{ [row.item.child_jobs_completed, row.item.total_child_jobs].join(" of ") }}
            </template>

            <template v-slot:cell(status)="row">
              <div v-if="(row.item.status)=='JobStatus.COMPLETED'">
                <span variant="outline-dark"
                      size="md"
                      id="status"
                >Finished</span>
              </div>
              <div v-else-if="(row.item.status)=='JobStatus.PROCESSING'">
                <span variant="outline-dark"
                      size="md"
                      id="status"
                >Processing</span>
              </div>
              <div v-else-if="(row.item.status)=='JobStatus.CANCELLED'">
                <span variant="outline-dark"
                      size="md"
                      id="status"
                >Cancelled</span>
              </div>
              <div v-else-if="(row.item.status)=='JobStatus.QUEUED'">
                <span variant="outline-dark"
                      size="md"
                      id="status"
                >Queued</span>
              </div>
              <div v-else-if="(row.item.status)=='JobStatus.FAILED'">
                <span variant="outline-dark"
                      size="md"
                      id="status"
                >Failed</span>
              </div>
              <div v-else>
                <span variant="outline-dark"
                      size="md"
                      id="status"
                >Unknown</span>
              </div>
            </template>

            <!-- Job table actions -->
            <template v-slot:cell(actions)="row">
              <div class="action-buttons">
                <!-- Results button -->
                <b-button :id="'popover-target-results'+row.item._id"
                          variant="outline-dark"
                          size="sm"
                          :disabled="row.item.child_jobs_completed != row.item.total_child_jobs"
                          @click="setJobState(row.item)"
                >
                  <font-awesome-icon icon="chart-bar" size="lg"/>
                </b-button>
                <!-- Download button -->
                <b-button :id="'popover-target-download'+row.item._id"
                          variant="outline-dark"
                          size="sm"
                          :disabled="!( (row.item.status)=='JobStatus.COMPLETED' ||  // can't download if queued or failed
                      (row.item.status)=='JobStatus.CANCELLED' || (row.item.status)=='JobStatus.PROCESSING')"
                          @click="downloadJob(row.item._id, row.item.status)"
                >
                  <font-awesome-icon icon="download" size="lg"/>
                </b-button>
                <!-- Cancel button -->
                <b-button :id="'popover-target-cancel'+row.item._id"
                          variant="outline-dark"
                          size="sm"
                          :disabled="(row.item.status)=='JobStatus.CANCELLED' || (row.item.status)=='JobStatus.COMPLETED'"
                          @click="cancelJob(row.item._id)"
                >
                  <font-awesome-icon icon="ban" size="lg"/>
                </b-button>
                <!-- Delete button -->
                <b-button :id="'popover-target-delete'+row.item._id"
                          variant="outline-dark"
                          size="sm"
                          :disabled="(row.item.status)=='JobStatus.PROCESSING' || (row.item.status)=='JobStatus.QUEUED' || (row.item.status)=='JobStatus.FAILED ' "
                          @click="deleteJob(row.item._id)"
                >
                  <font-awesome-icon icon="trash-alt" size="lg"/>
                </b-button>
                <!-- Hide button -->
                <b-button :id="'popover-target-hide'+row.item._id"
                          variant="outline-dark"
                          size="sm"
                          v-show="(row.item.hide)==false"
                          @click="hide(row.item._id)"
                >
                  <font-awesome-icon icon="eye-slash" size="lg"/>
                </b-button>
                <b-button :id="'popover-target-unhide'+row.item._id"
                          variant="outline-dark"
                          size="sm"
                          v-show="(row.item.hide)==true"
                          @click="unhide(row.item._id)"
                >
                  <font-awesome-icon icon="eye" size="lg"/>
                </b-button>
              </div>
              <b-popover :target="'popover-target-results'+row.item._id" triggers="hover" placement="top">
                <template v-slot:title>Visualize Results</template>
                View the job results and performance metrics.
              </b-popover>
              <b-popover :target="'popover-target-download'+row.item._id" triggers="hover" placement="top">
                <template v-slot:title>Download Results</template>
                Includes: <br/> - .results and .report files <br/> - abundance.tsv <br/> - inclusion.tsv <br/> - parsed
                results files
              </b-popover>
              <b-popover :target="'popover-target-cancel'+row.item._id" triggers="hover" placement="top">
                <template v-slot:title>Cancel Job</template>
                Stop the running job, or cancel a queued job. <br/><br/>Partial results may be available for download.
              </b-popover>
              <b-popover :target="'popover-target-delete'+row.item._id" triggers="hover" placement="top">
                <template v-slot:title>Delete Job</template>
                Delete canceled or completed job.
              </b-popover>
              <b-popover :target="'popover-target-hide'+row.item._id" triggers="hover" placement="top">
                <template v-slot:title>Hide Job</template>
                Hides job from main job table. <br/><br/>You can recover hidden jobs by toggling the “Show Jobs”
                dropdown and selecting “Hidden Jobs”.
              </b-popover>
              <b-popover :target="'popover-target-unhide'+row.item._id" triggers="hover" placement="top">
                <template v-slot:title>Unhide Job</template>
                Job will return to main “Jobs” table view.
              </b-popover>
            </template>
            <!-- End of job table actions -->

          </b-table>
        </div>
      </div>

    </div>
  </div>
</template>

<script>

  import _ from "lodash";
  import JobsService from "@/services/JobService";
  import Multiselect from "vue-multiselect";
  import numeralFormat from "vue-numerals";
  import {convert_seconds} from '@/controller/index'
  import "vue-moment";
  import moment from 'moment'

  export default {
    components: {
      Multiselect,
      numeralFormat
    },
    name: "jobs",
    data() {
      return {
        // All table-related code based on source code provided at: https://bootstrap-vue.org/docs/components/table. Used in both template and renderer
        fields: [
          {key: 'title', label: 'Job Title', sortable: true},
          {key: 'abundance_tsv', label: 'Input Filename', sortable: true, class: 'text-center'},
          // { key: 'abundance_tsv', label: 'TSV Filename', sortable: true, class: 'text-center' },
          // { key: 'fastq', label: 'FASTQ Filename', sortable: true, class: 'text-center' },
          {key: 'classifiers', label: 'Classifiers', sortable: true, class: 'text-center'},
          // { key: 'number_of_reads', label: 'Read Count', sortable: true, class: 'text-center' },
          {key: 'read_types', label: 'Read Types', sortable: false, class: 'text-center'},
          {key: 'created_datetime', label: 'Created Time', sortable: true, sortDirection: 'asc'},
          {key: 'process_time', label: 'Process Time', sortable: true, class: 'text-center'},
          {key: 'progress', label: 'Progress', sortable: false, class: 'text-center'},
          {key: 'status', label: 'Status', sortable: false},
          {key: 'actions', label: 'Actions', sortable: false},
        ],
        jobs: [],
        checked: false,

        totalRows: 1,
        currentPage: 1,
        perPage: 25,
        pageOptions: [5, 10, 15, 25, 100],
        sortBy: 'created_datetime',
        sortDesc: false,
        sortDirection: 'desc',
        filter: null,
        filterOn: [],

        fetchingJobs: false,
        countJobsComplete: 0,
        tableInterval: null,

        hidden: false,
        showing: "Jobs"
      }
    },
    mounted() {
      this.getJobs(this.hidden)
      this.setWatchInterval()
      this.$store.dispatch('clearAll')
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
      flipChecked() {
        return !this.checked;
      },
      setWatchInterval() {
        this.$nextTick(function () {
          this.tableInterval = setInterval(() => {
            !this.fetchingJobs ? (async () => {
              this.getJobs(this.hidden);
            })() : '';
          }, 8000);
        })
      },
      info(item, index, button) {
        this.infoModal.title = `Row index: ${index}`
        this.infoModal.content = JSON.stringify(item, null, 2)
        this.$root.$emit('bv::show::modal', this.infoModal.id, button)
      },
      processTime(completed_datetime, started_datetime) {
        var process_time = convert_seconds(moment.utc(moment(completed_datetime).diff(moment(started_datetime))).format("HH:mm:ss"))
        var d = moment.duration(process_time)
        var formatted_time = d.hours() + ' hours ' + d.minutes() +' mins ' + d.seconds() +' sec ';
        return formatted_time

      },

      resetInfoModal() {
        this.infoModal.title = ''
        this.infoModal.content = ''
      },
      onFiltered(filteredItems) {
        // Trigger pagination to update the number of buttons/pages due to filtering
        this.totalRows = filteredItems.length
        this.currentPage = 1
      },
      mySortCompare(a, b, key) {
        if (key === 'created_datetime' || key === "updated_datetime") {
          return this.$moment(b[key]) - this.$moment(a[key])
        } else {
          return false
        }
      },
      async getJobs(choice) {
        let jobs_shown = (choice ? JobsService.fetchHiddenJobs() : JobsService.fetchUnhiddenJobs())
        const vm = this;
        vm.jobs.length = 0;
        this.fetchingJobs = true;
        jobs_shown.then(res => {
          let countJobsCompleteLocal = 0;
          vm.jobs = [];
          _.forEach(res.data, function (job) {
            let parsed_job = JSON.parse(job);
            parsed_job.classifiers = parsed_job.classifiers.join(", ")
            vm.jobs.push(parsed_job);
          });
          this.totalRows = this.jobs.length
          this.fetchingJobs = false
        });
      },
      async setJobState(obj) {
        obj.type = (obj.abundance_tsv ? 1 : 2)
        await this.$store.dispatch("SAVE_JOB", obj)
        this.$router.push({name: 'viewJobResult', params: {id: obj._id}})
      },
      async downloadJob(id, status) {
          const $this = this;
          const $is_partial = (status=='JobStatus.CANCELLED' || status=='JobStatus.PROCESSING')
          const $out_file = $is_partial ? "meta_results_" + id + "_partial.zip" : "meta_results_" + id + ".zip"  // if partial, put in fname download
          JobsService.downloadJob(id, $out_file);
          window.open("/api/results/download/" + id + "/" + $out_file, '_blank');
      },
      async cancelJob(id) {
        const $this = this;
        $this
          .$swal({
            title: "Are you sure?",
            text: "You won't be able to revert this!",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Yes, cancel it!"
          })
          .then(res => {
            if (res.value) {
              JobsService.cancelJob(id);
              $this.$router.go({
                path: "/operating_jobs"
              });
            }
          });
      },
      async deleteJob(id) {
        const $this = this;
        $this
          .$swal({
            title: "Are you sure?",
            text: "You won't be able to revert this!",
            type: "warning",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Yes, delete it!"
          })
          .then(res => {
            if (res.value) {
              JobsService.deleteJob(id);
              $this.$router.go({
                path: "/operating_jobs"
              });
            }
          });
      },
      async hide(id) {
        try {
          await JobsService.hideJob(id);
          clearInterval($this.tableInterval)
          await $this.getJobs($this.hidden)
          $this.setWatchInterval()
        } catch (err) {
          console.error(err)
          $this.$swal.fire({
            position: 'center',
            icon: 'error',
            showConfirmButton: true,
            title: "There was an error hiding your job"
          })
        }
      },
      async unhide(id) {
        try {
          await JobsService.unhideJob(id);
          await this.getJobs(this.hidden)
          clearInterval(this.tableInterval)
          this.setWatchInterval()
        } catch (err) {
          console.error(err)
          $this.$swal.fire({
            position: 'center',
            icon: 'error',
            showConfirmButton: true,
            title: "There was an error unhiding your job"
          })
        }
      }
    },
    beforeDestroy: function () {
      clearInterval(this.tableInterval)
    },
  };
</script>
<style type="text/css">

  .table-wrap {
    width: 95%;
    margin: 0 auto;
    text-align: center;
  }

  table th,
  table tr,
  table td,
  table li,
  table ul {
    text-align: center;
  }

  .action-buttons {
    width: 230px;
    display: flex;
    justify-content: space-between;
    margin: 0 auto;
  }

  /* .ulDiv {
    text-align: center;
  }

  .ulDiv ul {
    /*margin:auto;*/
  /* list-style: none;
  display: inline;
  padding: 0px;
}

.ulDiv ul::after {
  content: " ";
}

.ulDiv :last-child::after {
  content: "";
} */

  table thead {
    background: #f2f2f2;
    align-items: center;
  }

  table tr td {
    padding: 10px;
  }

  table tr:nth-child(odd) {
    background: #f2f2f2;
  }

  .paginateButton {
    background-color: white !important;
    border: 1px solid steelblue !important;
    color: #007bff !important;
    border-radius: 0 !important;
  }

  .activeButton, .paginateButton:hover {
    color: #fff !important;
    background-color: #007bff !important;
    border-color: #007bff !important;;
  }

  .flex-centered {
    display: flex;
    justify-content: center;
    vertical-align: middle !important;
  }

  .link {
    cursor: pointer;
  }
</style>
