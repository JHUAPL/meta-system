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
  <div class="Jobs">
    <div class="col-md-10 offset-1">
      <div class="row align-items-center justify-content-center">
        <h1>Create a New Job</h1>
      </div>
      <div class="row align-items-center justify-content-center">
        <h4>
          Submit a job to discover the computational performance and accuracy of
          your selected metagenomic classifiers on your abundance profile.
          <br/>
          <br/>
        </h4>
      </div>
      <!--           <div>Available Read Types: {{read_types}}</div>-->
      <!--            <div>Available Classifiers: {{classifiers}}</div>-->
      <form class="vertical" @submit.prevent="addJob">
        <div class="form-horizontal">
          <div class="form-group required">
            <label class="col-md-3 offset-0 control-label">
              <b>1. Add Job Title:</b>
            </label>

            <div :class="{ 'form-control--error': $v.title.$error }">
              <input
                class="form-control"
                v-model="title"
                name="title"
                placeholder="Must be at least 2 characters"
                required="required"
                type="text"
                maxlength="30"
              />
            </div>
          </div>
          <div class="vertical">
            <div class="form-group required">
              <b
              >2. Would you like to submit a simulation or classification job?</b
              >
            </div>

            <b-button
              title="Click to Upload TSV"
              variant="outline-primary"
              v-on:click="
                () => {
                  simulate = !simulate;
                  classify = false;
                }
              "
              type="button"
              class="btn btn-outline-primary"
              :pressed="simulate"
            > 
              Simulate + Classify
            </b-button>
            &nbsp;

            <b-button
              title="Click to Upload FASTQ"
              variant="outline-primary"
              v-on:click="
                () => {
                  classify = !classify;
                  simulate = false;
                }
              "
              type="button"
              class="btn btn-outline-primary"
              :pressed="classify"
            >
              Classify
            </b-button>
          </div>
          <br/>
          <div class="vertical" v-if="simulate">
            <b-button
              squared
              title="Yes"
              variant="outline-dark"
              v-on:click="
                () => {
                  isMultipleFiles = !isMultipleFiles;
                  notMultipleFiles = false;
                }
              "
              type="button"
              class="btn-sm btn-outline-dark"
              :pressed="isMultipleFiles"
            >
              Upload ZIP
            </b-button>
            &nbsp;

            <b-button
              squared
              title="No"
              variant="outline-dark"
              v-on:click="
                () => {
                  notMultipleFiles = !notMultipleFiles;
                  isMultipleFiles = false;
                }
              "
              type="button"
              class="btn-sm btn-outline-dark"
              :pressed="notMultipleFiles"
            >
              Upload TSV
            </b-button>
          </div>

          <div class="vertical" v-if="classify">
            <b-button
              squared
              title="Yes"
              variant="outline-dark"
              v-on:click="
                  () => {
                    isMultipleFiles = !isMultipleFiles;
                    notMultipleFiles = false;
                  }
                "
              type="button"
              class="btn-sm btn-outline-dark mr-1"
              :pressed="isMultipleFiles"
            >
              Upload ZIP
            </b-button>

            <b-button
              squared
              title="No"
              variant="outline-dark"
              v-on:click="
                  () => {
                    notMultipleFiles = !notMultipleFiles;
                    isMultipleFiles = false;
                  }
                "
              type="button"
              class="btn-sm btn-outline-dark"
              :pressed="notMultipleFiles"
            >
              Upload FASTQ
            </b-button>
          </div>
        </div>

        <div v-if="notMultipleFiles">
          <div v-if="simulate" class="vertical">
            <br/>
            <div class="form-group required">
              <label class="col-md-8 offset-0 control-label">
                Upload Abundance TSV File.
              </label>
            </div>
          </div>
        </div>

        <div v-if="isMultipleFiles">
          <div v-if="simulate" class="vertical">
            <br/>
            <div class="form-group required">
              <label class="col-md-8 offset-0 control-label">
                Upload Zip folder of Abundance TSV files. <i>It is recommended that all files are uniquely named.</i>
              </label>
            </div>
          </div>
        </div>

        <div v-if="notMultipleFiles">
          <div v-if="classify" class="vertical">
            <br/>
            <div class="form-group required">
              <label class="col-md-8 offset-0 control-label">
                Upload FASTQ File.
              </label>
            </div>
          </div>
        </div>

        <div v-if="isMultipleFiles">
          <div v-if="classify" class="vertical">
            <br/>
            <div class="form-group required">
              <label class="col-md-8 offset-0 control-label">
                Upload Zip folder of FASTQ files. <i>It is recommended that all files are uniquely named.</i>
              </label>
            </div>
          </div>
        </div>

        <div v-if="isMultipleFiles || notMultipleFiles">
          <vue-dropzone
            ref="myVueDropzone"
            id="abu_file"
            @vdropzone-file-added="vfileAdded"
            @vdropzone-success="vsuccess"
            @vdropzone-error="verror"
            @vdropzone-removed-file="vremoved"
            @vdropzone-sending="vsending"
            @vdropzone-queue-complete="vqueueComplete"
            @vdropzone-total-upload-progress="vprogress"
            @vdropzone-mounted="vmounted"
            @vdropzone-drop="vddrop"
            @vdropzone-drag-start="vdstart"
            @vdropzone-drag-end="vdend"
            @vdropzone-drag-enter="vdenter"
            @vdropzone-drag-over="vdover"
            @vdropzone-drag-leave="vdleave"
            @vdropzone-duplicate-file="vdduplicate"
            :options="dropzoneOption"
            :duplicateCheck="true"
          >
          </vue-dropzone>
        </div>

        <div v-if="validate">
          Uploading and validating file, please wait...
        </div>

        <div v-if="filePath">
          <div v-for="message in filePath.messages">
            <div v-if="message[message.length-1] == 'd'">
              <b-alert show dismissible variant="success">
                <strong> ALL/OTHER FILE(S) IN PROPER FORMAT </strong>
              </b-alert>
            </div>
            <div v-else>
              <b-alert show dismissible variant="danger">
                <strong> {{message}}</strong> </br>
                Your file is not in proper format.
                <strong>{{toggle_validations()}}</strong>
              </b-alert>
            </div>
          </div>
        </div>

        <br>
        <div class="vertical form-group required">
          <label class="vertical control-label">
            <b>3. Select classifier(s):</b>
          </label>
          <div class="center">
            <b-form-checkbox
              v-model="allSelected['classifier']"
              :indeterminate="indeterminate.classifier"
              @change="toggleAllClassifier"
            >Select All
            </b-form-checkbox>
            <br/>
          </div>
          <b-form-checkbox-group
            v-model="classifiers_selected"
            v-bind:style="{
              'column-count': classifiers.length >= 6 ? 6 : classifiers.length
            }"
            stacked
          >
            <div v-for="classifier in classifiersOnly">
              <span>
                <div style="display:inline-block;" :id="`${classifier}`">
                  <b-form-checkbox v-bind:value="classifier"
                  >{{ classifier }}
                  </b-form-checkbox>
                </div>
                <div v-for="c in classifiers">
                  <b-popover
                    :target="`${c.name}`"
                    triggers="hover"
                    placement="top"
                  >
                    <template v-slot:title>Classifier Info</template>
                    <a target="_blank" v-bind:href="c.link">{{ c.link }}</a>
                  </b-popover>
                </div>
              </span>
            </div>
          </b-form-checkbox-group>
          <div class="error" v-if="!$v.classifiers_selected.minLength">
            Classifier set must be one or more. Total selected:
            {{ classifiers_selected.length }}.
          </div>
        </div>
        <div v-if="!classify" class="form-group required">
          <label class="col-md-5 offset-0 control-label">
            <b>4. Select read type(s):</b>
          </label>
          <div class="center">
            <b-form-checkbox
              v-model="allSelected['read_types']"
              :indeterminate="indeterminate.read_types"
              @change="toggleAllReads"
            >Select All
            </b-form-checkbox>
            <br/>
          </div>
          <div style="text-align:center; justify-content:center;">
            <b-form-checkbox-group
              v-model="read_types_selected"
              v-bind:style="{
                'column-count': read_types.length >= 6 ? 6 : read_types.length
              }"
              stacked
            >
              <div
                v-if="read_types.length > 0"
                v-for="read_type in read_types_only"
              >
                <span>
                  <div :id="`${read_type}`" style="display: inline-block">
                    <b-form-checkbox v-bind:value="read_type"
                    >{{ read_type }}
                    </b-form-checkbox>
                  </div>
                  <div v-for="read in read_types">
                    <b-popover
                      :target="`${read.name}`"
                      triggers="hover"
                      placement="top"
                    >
                      <template v-slot:title>Read Type Info</template>
                      <h6>Simulator Ref</h6>
                      <a target="_blank" v-bind:href="read.simlink"
                      >Simulator: {{ read.simlink }}</a
                      >
                      <br/><br/>
                      <h6>Product Ref</h6>
                      <a target="_blank" :href="read.prodlink">{{
                        read.prodlink
                      }}</a>
                    </b-popover>
                  </div>
                </span>
              </div>
            </b-form-checkbox-group>
          </div>
          <div class="error" v-if="!$v.read_types_selected.minLength">
            Read types set must be one or more. Total selected:
            {{ read_types_selected.length }}.
          </div>
        </div>
        <button
          v-on:click="
              () => {
                submitStatus = null;
                loading = true;
              }
            "
          :disabled="!this.success || this.removedFile|| this.upload || this.validations"
          class="btn btn-lg btn-primary btn-block"
        >
          Submit Job
        </button>

        <div
          v-if="loading && submitStatus !== 'ERROR' && this.success == false"
          align="center"
        >
          <br/>
          Submitting Job...
        </div>
        <p class="typo__p" v-if="submitStatus === 'OK' && this.success == true">
          Thanks for your submission!
        </p>
        <p
          class="typo__p"
          v-if="submitStatus === 'ERROR' && this.success == false"
        >
          Please fill the form correctly.
        </p>
      </form>
    </div>
  </div>
</template>

<script>
  import JobService from "@/services/JobService";
  import ClassifierService from "@/services/ClassifierService";
  import {minLength, required} from "vuelidate/lib/validators";
  import swal from "sweetalert";
  import {Circle} from "vue-loading-spinner";
  import vue2Dropzone from "vue2-dropzone";
  import {BAlert} from "bootstrap-vue";
  import "vue2-dropzone/dist/vue2Dropzone.min.css";

  export default {
    name: "addJob",
    components: {
      Circle,
      vueDropzone: vue2Dropzone,
      BAlert
    },
    data() {
      return {
        title: null,
        classifiers_selected: [],
        classifiers: [],
        classifiersOnly: [],
        created_time: "",
        updated_time: "",
        read_types: [],
        read_types_only: [],
        read_types_selected: [],
        total_jobs: [],
        submitStatus: "",
        filePath: false,
        message: false,
        simulate: false,
        classify: false,
        isMultipleFiles: false,
        notMultipleFiles: false,
        loading: false,
        all: false,
        validations: false,
        upload: false,
        allSelected: {
          classifier: false,
          read_types: false
        },
        indeterminate: {
          classifier: false,
          read_types: false
        },
        dropzoneOption: {
          url: "/api/jobs/file_upload/files",
          success: (file, response) => {
            this.filePath = JSON.parse(file.xhr.response);
          },
          addRemoveLinks: true,
          uploadMultiple: false,
          chunking: false,
          maxFiles: 1,
          maxFilesize: 10000, // MB https://www.dropzonejs.com/#config-maxFilesize
          parallelChunkUploads: false,
          acceptedFiles: ".fastq, .tsv, .zip",
          timeout: 3.6e6, //thirty minutes
          dictDefaultMessage:
            "<i class='fa fa-cloud-upload'></i> Drop File Here to Upload"
        },
        counter: 0,
        fileAdded: false,
        success: false,
        error: false,
        removedFile: false,
        sending: false,
        queueComplete: false,
        uploadProgress: false,
        progress: false,
        myProgress: 0,
        isMounted: false,
        dDrop: false,
        dStarted: false,
        dEnded: false,
        dEntered: false,
        dOver: false,
        dLeave: false,
        dDuplicate: false,
        switch: false,
        validate: false
      };
    },
    validations: {
      title: {
        required,
        minLength: minLength(2)
      },
      classifiers_selected: {
        required,
        minLength: minLength(1)
      },
      read_types_selected: {
        minLength: minLength(1)
      }
    },
    mounted() {
      this.fetchClassifiers();
      this.fetchReadTypes();
      this.fetchReadTypesOnly();
      this.fetchClassifiersOnly();
    },
    methods: {
      async addJob() {
        if (this.$v.$invalid) {
          this.submitStatus = "ERROR";
        } else {
          let formData = new FormData();
          formData.append("title", this.title);
          formData.append("filePath", this.filePath.paths);
          formData.append("multiple_files", this.isMultipleFiles)
          formData.append(
            "classifiers",
            JSON.stringify(this.classifiers_selected)
          );
          if (this.simulate) {
            formData.append(
              "read_types",
              JSON.stringify(this.read_types_selected)
            );
          }
          // let mode = (this.simulate ? JobService.addJob(formData) :  JobService.addJobClassify(formData))
          if (this.simulate) {
            await JobService.addJob(formData)
              .then(res => {
                this.$swal("Your job has been submitted!");
                this.submitStatus = "OK";
                this.loading = false;
                // router.push({ name: 'operating_jobs' }) //commenting out for now until an operating_jobs collection is created via pymodm
              })
              .catch(err => {
                if (err.response.status === 409) {
                  swal("Error", err.response.status, "error");
                } else if (err.response.status === 410) {
                  swal("Error: ", err.response.data.message, "error");
                } else {
                  swal(
                    "Error",
                    "Error in adding the job. Please contact an admin to resolve this issue.",
                    "error"
                  );
                }
              });
          } else {
            await JobService.addJobClassify(formData)
              .then(res => {
                this.$swal("Your job has been submitted!");
                this.submitStatus = "OK";
                this.loading = false;
                // router.push({ name: 'operating_jobs' }) //commenting out for now until an operating_jobs collection is created via pymodm
              })
              .catch(err => {
                if (err.response.status === 409) {
                  swal("Error", err.response.status, "error");
                } else if (err.response.status === 410) {
                  swal("Error: ", err.response.data.message, "error");
                } else {
                  swal(
                    "Error",
                    "Error in adding the job. Please contact an admin to resolve this issue.",
                    "error"
                  );
                }
              });
          }

          // this.$router.push({ name: "operating_jobs" });
        }
      },
      async fetchClassifiers() {
        const response = await ClassifierService.fetchClassifiers().catch(err => {
          console.error(err);
        });
        this.classifiers = response.data.data;
      },
      async fetchReadTypes() {
        const response = await ClassifierService.fetchReadTypes();
        this.read_types = response.data.data;
      },
      async fetchClassifiersOnly() {
        const response = await ClassifierService.fetchClassifiersOnly();
        this.classifiersOnly = response.data.data;
      },
      async fetchReadTypesOnly() {
        const response = await ClassifierService.fetchReadTypesOnly();
        this.read_types_only = response.data.data;
      },
      addClassifierTag(newTag) {
        const tag = {
          name: newTag
        };
        this.classifiers.push(tag);
      },
      addReadTypeTag(newTag) {
        const tag = {
          name: newTag
        };
        this.read_types.push(tag);
      },
      toggleAllClassifier(checked) {
        this.classifiers_selected = checked ? this.classifiersOnly.slice() : [];
      },
      toggleAllReads(checked) {
        this.read_types_selected = checked ? this.read_types_only.slice() : [];
      },
      toggle_validations() {
        this.validations = true;
      },
      vfileAdded(file) {
        this.fileAdded = true;
        this.removedFile = false;
        this.sending = false;
      },
      vsuccess(file, response) {
        this.success = true;
        this.upload = false;
        this.removedFile = false;
        this.validate = false;
      },
      verror(file) {
        this.error = true;
      },
      vremoved(file, xhr, error) {
        this.removedFile = true;
        this.upload = false;
        this.filePath = ""
        this.validate = false;
        this.validations = false;
      },
      vsending(file, xhr, formData) {
        this.sending = true;
        if (this.isMultipleFiles == true) {
          formData.append("zip", file)
        }
        if (this.simulate == true) {
          formData.append("tsv", file);
        } else {
          formData.append("fastq", file);
        }
        formData.append("upload", this.upload);
        formData.append("multiple", this.isMultipleFiles);
        formData.append("simulate", this.simulate)
        formData.append("classify", this.classify)
      },
      vqueueComplete(file, xhr, formData) {
        this.queueComplete = true;
      },
      vprogress(totalProgress, totalBytes, totalBytesSent) {
        this.progress = true;
        this.myProgress = Math.floor(totalProgress);
        this.removedFile = false;
        this.upload = true
        this.validate = true;
      },
      vmounted() {
        this.isMounted = true;
      },
      vddrop() {
        this.dDrop = true;
      },
      vdstart() {
        this.dStarted = true;
      },
      vdend() {
        this.dEnded = true;
      },
      vdenter() {
        this.dEntered = true;
      },
      vdover() {
        this.dOver = true;
      },
      vdleave() {
        this.dLeave = true;
      },
      vdduplicate() {
        this.dDuplicate = true;
      }
    },
    watch: {
      read_types_selected(newVal) {
        if (newVal.length == 0) {
          this.indeterminate.read_types = false;
          this.all = false;
        } else if (newVal.length == this.read_types.length) {
          this.indeterminate.read_types = false;
          this.allSelected.read_types = true;
        } else {
          this.indeterminate.read_types = true;
          this.allSelected.read_types = false;
        }
      },
      classifiers_selected(classVal) {
        if (classVal.length == 0) {
          this.indeterminate.classifier = false;
          this.allSelected.classifier = false;
        } else if (classVal.length == this.classifiers.length) {
          this.indeterminate.classifier = false;
          this.allSelected.classifier = true;
        } else {
          this.indeterminate.classifier = true;
          this.allSelected.classifier = false;
        }
      },
      fileAdded() {
        let that = this;
        setTimeout(function () {
        }, 2000);
      },
      success() {
        let that = this;
        setTimeout(function () {
          that.success = true;
        }, 2000);
      },
      error() {
        let that = this;
        setTimeout(function () {
          that.error = false;
        }, 2000);
      },
      removedFile() {
        let that = this;
        setTimeout(function () {
        }, 2000);
      },
      sending() {
        let that = this;
        setTimeout(function () {
          that.sending = false;
        }, 2000);
      },
      queueComplete() {
        let that = this;
        setTimeout(function () {
          that.queueComplete = false;
        }, 2000);
      },
      progress() {
        let that = this;
        setTimeout(function () {
          that.progress = false;
        }, 2000);
      },
      isMounted() {
        let that = this;
        setTimeout(function () {
          that.isMounted = false;
        }, 2000);
      },
      dDrop() {
        let that = this;
        setTimeout(function () {
          that.dDrop = false;
        }, 2000);
      },
      dStarted() {
        let that = this;
        setTimeout(function () {
          that.dStarted = false;
        }, 2000);
      },
      dEnded() {
        let that = this;
        setTimeout(function () {
          that.dEnded = false;
        }, 2000);
      },
      dEntered() {
        let that = this;
        setTimeout(function () {
          that.dEntered = false;
        }, 2000);
      },
      dOver() {
        let that = this;
        setTimeout(function () {
          that.dOver = false;
        }, 2000);
      },
      dLeave() {
        let that = this;
        setTimeout(function () {
          that.dLeave = false;
        }, 2000);
      },
      dDuplicate() {
        let that = this;
        setTimeout(function () {
          that.dDuplicate = false;
        }, 2000);
      }
    }
  };
</script>

<style>
  @import "../assets/css/style.css";
  @import url("https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css");

  .checks label {
    text-anchor: left;
    flex-direction: row;
    align-items: baseline;
  }
</style>
