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

import Vue from 'vue';

import {BootstrapVue} from 'bootstrap-vue';
import Vuelidate from 'vuelidate';
import Vue2TouchEvents from 'vue2-touch-events';
import VueSweetalert2 from 'vue-sweetalert2';
import * as mdbvue from 'mdbvue';
import VueNumerals from 'vue-numerals';
import App from './App.vue'
import router from './router'
import store from './store'
import { convert_seconds } from './controller/index'
import {library} from '@fortawesome/fontawesome-svg-core'
import {faBan, faChartBar, faDownload, faEye, faEyeSlash, faMinusCircle, faTrashAlt} from '@fortawesome/free-solid-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'

library.add(faChartBar, faDownload, faBan, faEyeSlash, faEye, faMinusCircle, faTrashAlt)
Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.use(BootstrapVue);
Vue.use(Vuelidate);
Vue.use(Vue2TouchEvents);
Vue.use(VueSweetalert2);
Vue.use(require('vue-moment'));
Vue.use(convert_seconds)
Vue.use(VueNumerals); // default locale is 'en'

Object.values(mdbvue).forEach((component) => {
  Vue.component(component, mdbvue[component])
});

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app');
