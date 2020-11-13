/*
 * # **********************************************************************
 * # Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
 * #
 * # All Rights Reserved.
 * # For any other permission, please contact the Legal Office at JHU/APL.
 *
 * # Licensed under the Apache License, Version 2.0 (the "License");
 * # you may not use this file except in compliance with the License.
 * # You may obtain a copy of the License at
 *
 * #    http://www.apache.org/licenses/LICENSE-2.0
 *
 * # Unless required by applicable law or agreed to in writing, software
 * # distributed under the License is distributed on an "AS IS" BASIS,
 * # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * # See the License for the specific language governing permissions and
 * # limitations under the License.
 * # **********************************************************************
 */

import Api from '@/services/Api'

export default {
  fetchAllJobs() {
    return Api().get('/api/jobs/all')
  },
  fetchUnhiddenJobs() {
    return Api().get('api/jobs/unhidden')
  },
  fetchHiddenJobs() {
    return Api().get('api/jobs/hidden')
  },
  fetchAbuTSV(params) {
    return Api().get('api/results/orig_abundance_profile/' + params.id)
  },
  addJob(params) {
    return Api().post('/api/jobs/submit_simulation', params)
  },
  addJobClassify(params) {
    return Api().post('/api/jobs/submit_classification', params)
  },
  getJobResults(params) {
    return Api().get('/api/results/' + params.id + '/' + params.read_type + '/compare')
  },
  getJobTaxResults(params) {
    if (params.read_type) {
      return Api().get('/api/results/taxid_abu_org/' + params.id + '/' + params.read_type + '/' + params.classifier)
    } else {
      return Api().get('/api/results/taxid_abu_org/' + params.id + '/' + params.classifier)
    }
  },
  getJobResultsDummy() {
    return Api().get('/api/results/test')
  },
  hideJob(id) {
    return Api().post('/api/jobs/hide/' + id)
  },
  unhideJob(id) {
    return Api().post('/api/jobs/unhide/' + id)
  },
  fetchMetrics(params) {
    if (params.classifier) {
      if (params.read_type) {
        return Api().get('/api/results/computation/' + params.pipeline + '/' + params.metric + "/" + params.id + "/" + params.read_type + "/" + params.classifier)
      } else {
        return Api().get('/api/results/computation/' + params.pipeline + '/' + params.metric + "/" + params.id + "/" + params.classifier)
      }
    } else {
      return Api().get('/api/results/computation/' + params.pipeline + '/' + params.metric + "/" + params.id + "/" + params.read_type)
    }
  },
  fetchInclusion(params) {
    if (!params.read_type) {
      return Api().get('/api/results/' + params.id + '/inclusion')
    } else {
      return Api().get('/api/results/' + params.id + '/' + params.read_type + '/inclusion')
    }
  },
  cancelJob(id) {
    return Api().post('/api/jobs/cancel/' + id)
  },
  deleteJob(id) {
    return Api().post('/api/jobs/delete/' + id)
  },
  downloadJob(id, fname) {
    return Api().get('/api/results/download/' + id + '/' + fname)
  }
}
