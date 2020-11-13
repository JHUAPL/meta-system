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

import Vue from 'vue'
import VueRouter from 'vue-router'
import OperatingJobs from '@/components/OperatingJob';
import addJob from '@/components/AddJob';
import Home from '@/components/Home';
import Results from '@/components/Results';
import About from '@/components/About';


Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    meta: {
      title: 'META - Home',
    },
    name: 'Home',
    component: Home,
  },
  {
    path: '/operating_jobs',
    component: OperatingJobs,
    name: 'operating_jobs',
    meta: {
      requiresAuth: false,
      title: 'META - View Jobs',
    }
  },
  {
    path: '/addJob',
    component: addJob,
    name: 'addJob',
    meta: {
      requiresAuth: false,
      title: 'META - Add Job',
    }
  },
  {
    path: '/viewJobResult/:id/compare',
    component: Results,
    props: {default: true, sidebar: false},
    name: 'viewJobResult',
    meta: {
      requiresAuth: false,
      title: 'META - Results',
    }
  },
  {
    path: '/about',
    name: 'about',
    component: About,
    meta: {
      requiresAuth: false,
      title: 'META - About',
    }
  }
];

const router = new VueRouter({
  base: process.env.BASE_URL,
  // mode:'history',
  routes
});

router.beforeEach((to, from, next) => {
  try{
    document.title = to.meta.title;
  } catch(err){

  }
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (localStorage.getItem('user') == null) {
      next({
        path: '/'
      })
    } else {
      next()
    }
  } else {
    next()
  }
});

export default router
