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

function getDefaultState() {
  return {
    jobID: null,
    read_types: [],
    classifiers: [],
    type: null,
    created_datetime: null,
    updated_datetime: null,
    jobTitle: null,

  }
}

const state = getDefaultState()

const actions = {
  SAVE_JOB({commit}, job) {
    return new Promise((resolve, reject) => {
      commit('SAVE_JOB', job);
      resolve()
    })
  },
  clearAll({commit}) {
    return new Promise((resolve, reject) => {
      commit("clearAll")
      resolve()
    })
  }
};

const mutations = {
  SAVE_JOB(state, job) {
    state.jobID = job._id
    state.read_types = (job.read_types ? job.read_types : []);
    state.type = job.type
    state.classifiers = job.classifiers
    state.jobTitle = job.title
    state.created_datetime = job.started_datetime
    state.updated_datetime = job.updated_datetime
  },
  clearAll(state, name) { //https://github.com/vuejs/vuex/issues/1118#issuecomment-356286218
    const s = getDefaultState()
    Object.keys(s).forEach(key => {
      // delete state[key]
      state[key] = s[key]
    })
  }
};

export default {
  state,
  actions,
  mutations
};
