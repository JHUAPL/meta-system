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
  <div class="About">
    <div class="col-md-10 offset-1">
      <div class="row align-items-center justify-content-center">
        <div class="col-md-12"><h4>The Metagenomic Evaluation & Testing Analysis (META) Tool</h4></div>
        <div
          class="col-md-12"><h1>A tool that evaluates runtime performance and classification accuracy of a variety
          metagenomic classifiers</h1></div>
        <div class="col-md-10 offset-0">
          <div class="Requirements">
            <br/>
            <br/>
            <h3>System Requirements</h3>
            <ul class="list-unstyled" align="center">
              <li>>512 GB RAM</li>
              <li>50-900 GB storage per classifier database</li>
              <li>32 CPU Cores</li>
              <li>Docker, Python 3.7, Node 10, NPM 6</li>
            </ul>
          </div>
        </div>
        <div class="col-md-10 offset-0">
          <div class="Workflow">
            <br/>
            <br/>
            <h3>Workflow and Architecture</h3>
            <img :src="require('@/assets/Workflow.png')" height="400px" width="750px"/>
          </div>
        </div>
        <div class="col-md-10 offset-0">
          <div class="Metrics">
            <br/>
            <br/>
            <h3> Comparison Metrics</h3>
            <h5>
              <p style="text-align:left;">
                The primary metrics used in META for comparing classifier performance are
                the <i>area under precision recall curve (AUPRC)</i> and the <i>L2 distance</i>. These metrics highlight
                complementary phenomena that occur in genomic classification. In effect, AUPRC is more sensitive to low
                abundance quantification, while L2 is more sensitive to high abundance taxa. <br/><br/>

                These metrics are detailed in, and Figures <strong>A</strong> and <strong>B</strong> have been pulled
                from, the following <i>Cell</i> publication:
                <i>
                  Ye SH, Siddle KJ, Park DJ, Sabeti PC. Benchmarking Metagenomics Tools for Taxonomic Classification.
                  Cell. 2019;178(4):779‐794. <a href="https://pubmed.ncbi.nlm.nih.gov/31398336/">doi:10.1016/j.cell.2019.07.010</a>
                </i>
                <br/><br/>
              </p>
            </h5>
            <h2>Example</h2>
            <h5>
              <p style="text-align:left;">
                For a simple example, AUPRC is not significantly effected if a particular taxa is 80% or 20% of the
                sample, however the L2 distance of the resulting taxonomic abundance profile will increase notably.
                <br/><br/>

                For AUPRC, each point represents the precision and recall scores at a increasing abundance
                thresholds. The resultant curve is illustrated in (Figure <strong>A-A</strong>).
                For each abundance threshold, you determine which of your ground truth
                taxa are above (positive) and which are below (negative).
                <br/><br/>

                Next, you check each taxa of the classifier output. If a taxa is positive in ground truth (above the
                abundance threshold), but negative in the classifier output (below the abundance threshold), the FN
                (false negative) count is increased by one. This is done for each unique taxa among the ground truth set
                and classifier output set, to obtain total TP (true positive), FN, FP (false positive), and TN (true
                negative) counts from which precision and recall may be calculated. <br/> <br/>

                The L2 metric is based on the Euclidean distance between the ground truth and classifier output
                taxa abundance vectors (Figure <strong>A-B</strong>). For example, let <i>gt</i> be the ground truth
                abundance vector, and <i>co</i> be the classifier output abundance vector below:
              </p>
            </h5>
            <div class="col-md-10 offset-1">
              <img :src="require('@/assets/Calculations.png')" height="172px" width="683px"/>
            </div>
            <div class="col-md-10 offset-1">
              <img :src="require('@/assets/Graphs.png')" height="522px" width="1053px"/>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
  export default {
    name: "about",
    data() {
      return {
        data: []
      };
    }
  };
</script>
<style lang="scss">
</style>
