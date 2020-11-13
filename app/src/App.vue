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
  <div id="app">
    <div>
      <Navigation></Navigation>
    </div>
    <router-view></router-view>
  </div>

</template>

<script>
  import Navigation from './components/Navigation';

  export default {
    name: 'app',
    components: {
      Navigation,
    },
  };
</script>

<style lang="scss">

  @import '~bootstrap/dist/css/bootstrap.css';
  @import '~bootstrap-vue/dist/bootstrap-vue.css';

  #app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;
    text-align: center;
    margin-top: 60px;
  }

  .error {
    font-size: 0.75rem;
    color: #f57f6c;
  }

  .toolbar {
    /*color:aliceblue;*/
    background: blue;
    width: 100%;
  }

  .spacer {
    flex: 1 1 auto;
  }

  .activeRoute {
    color: black;
    fill: black;
  }
</style>
<style lang="scss">
  @import './assets/css/style.css';
</style>
