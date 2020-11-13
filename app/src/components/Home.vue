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
  <div class="Home">
    <div>
      <About></About>
    </div>
    <div class="col-md-10 offset-1">
      <div class="row align-items-center justify-content-center">
        <div class="col-md-10 offset-0">
          <img :src="require('@/assets/AboutUs.png')" height="400px" width="750px"/>
        </div>
        <div class="col-md-10 offset-0">
          <div class="Objectives">
            <h3>Our Project</h3>
            <br/>
            <h5>

              The Metagenomics Evaluation & Testing Analysis (META) Tool is a
              software system that executes one or more third-party metagenomics
              classifiers on simulated nucleotide read sequences, and
              comparatively evaluates classification accuracy and runtime
              performance. In addition, the user can run a
              real-world read sequence (FASTQ) through any of the available
              classifiers view the aggregate results from one or more third-party metagenomics classifiers.
              In effect, there are two job modes that META can run:
              <br/>
              <br/>
              <p style="text-align:left;">
              <ul>
                <li>
                  <strong>Simulate + Classify</strong>: This feature allows you to initiate a job
                  pipeline that simulates sequencing from the <a href="https://store.nanoporetech
                                    .com/us/flowcells/spoton-flow-cell-mk-i-r9-4.html" rel="nofollow noreferrer
                                    noopener" target="_blank">Oxford Nanopore R9 flowcell</a> (r9), <a
                  href="https://nanoporetech.com/products/flongle" rel="nofollow noreferrer
                                    noopener" target="_blank">Oxford Nanopore Flongle flowcell</a> (flg), <a
                  href="https://www.illumina.com/systems/sequencing-platforms/iseq.html"
                  rel="nofollow noreferrer noopener" target="_blank">Illumina iSeq</a> (iseq), or
                  <a href="https://www.illumina.com/systems/sequencing-platforms/miseq.html"
                     rel="nofollow noreferrer noopener" target="_blank">Illumina MiSeq</a> (miseq)
                  platforms. These simulations generate a FASTQ file that approximate a given <em>abundance profile</em>.
                  For each simulated FASTQ, a set of user-selected classifiers return a predicted
                  abundance profile that is then compared to the user-specific abundance profile. The
                  list of currently available classifiers is shown in Table I.
                  <ul><br/>
                    <li>An <em>abundance profile</em> is expressed as a tab-delimited text file (TSV) where the first
                      column contains the leaf taxonomic ID, the second column contains the corresponding abundance
                      proportion (must sum to 1.000000), and the third column designates the organism as being
                      foreground (1) or background (0). There should be no headers in the abundance profile TSV. An
                      example is shown below:<br/><br/>
                      <pre class="col-md-10 offset-0" align="left" lang="plaintext"
                           v-pre="true" style="border: 1px solid black;"><code><span id="LC1" class="line"
                                                                                     lang="plaintext">400667	0.10	  1</span>
  <span id="LC2" class="line" lang="plaintext">435590	0.10	  1</span>
  <span id="LC3" class="line" lang="plaintext">367928	0.10	  1</span>
  <span id="LC4" class="line" lang="plaintext">864803	0.10	  1</span>
  <span id="LC5" class="line" lang="plaintext">1091045	0.10	  1</span>
  <span id="LC6" class="line" lang="plaintext">349101	0.10	  1</span>
  <span id="LC7" class="line" lang="plaintext">1282	0.10	  1</span>
  <span id="LC8" class="line" lang="plaintext">260799	0.10	  1</span>
  <span id="LC9" class="line" lang="plaintext">1529886	0.10	  1</span>
  <span id="LC10" class="line" lang="plaintext">198094	0.10	  1</span></code></pre>
                    </li>
                    <li>
                      To start <em>Simulate + Classify</em> jobs in bulk, you may submit a ZIP folder of abundance
                      profiles (i.e. a zipped folder of *.tsv files). You will be provided the option to
                      <strong>Upload ZIP</strong> after selecting <strong>Simulate + Classify</strong>. This will
                      create a new row in the <strong>View Jobs</strong> table for each TSV file contained in the ZIP
                      folder. It is recommended that the TSV files in the folder are uniquely named.
                    </li>
                  </ul>
                </li>
                <br/>
                <li>
                  <strong>Classify</strong>: This feature allows you to initiate a job pipeline
                  that accepts a FASTQ file and runs a set of user-selected classifiers. The list
                  of currently available classifiers is shown in Table I.
                </li>
                <ul>
                  <li>
                    To start <em>Classify</em> jobs in bulk, you may submit a ZIP folder of FASTQ (i.e. a zipped
                    folder of *.fastq files). You will be provided the option to <strong>Upload
                    ZIP</strong> after selecting <strong> Classify</strong>. This will create a new row in
                    the <strong>View Jobs</strong> table for each FASTQ file contained in the ZIP folder. It is
                    recommended that the FASTQ files in the folder are uniquely named.
                  </li>
                </ul>
              </ul>

              </p>
              <p>
                <strong>Table I.</strong> Metagenomic classifiers currently integrated in META</p>
              <table class="col-md-10 offset-1" style="border: 1px solid #a9acb1; border-collapse: collapse;">
                <thead>
                <tr style="border-bottom: 1px solid #a9acb1;">
                  <th style="border-right: 1px solid #a9acb1; padding: 15px;">Tool</th>
                  <th style="border-right: 1px solid #a9acb1; padding: 15px;">Description</th>
                  <th>Average Runtime (seconds) for 1.0 GB FASTQ File</th>
                </tr>
                </thead>
                <tbody>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="http://ccb.jhu.edu/software/kraken/MANUAL.html">Kraken</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">k-mer based, exact
                    alignment
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    4.95
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/DerrickWood/kraken2/blob/master/docs/MANUAL.markdown">
                    Kraken2</a>
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">
                    k-mer based, exact alignment, with smaller memory requirements, and translated search mode
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    0.32
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/fbreitwieser/krakenuniq">KrakenUniq</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">
                    k-mer based, exact alignment with smaller memory requirements
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    71.05
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/jenniferlu717/Bracken">Bracken</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">k-mer based abundance
                    estimation from raw reads
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    0.04
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/infphilo/centrifuge/blob/master/MANUAL.markdown"
                  >Centrifuge</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">alignment based on BWT
                    and FM-indexing schemes
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    14.38
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="http://www.diamondsearch.org/index.php">DIAMOND</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">alignment based, SW
                    against protein database
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    145.47
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://mash.readthedocs.io/en/latest/"> Mash</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">k-mer based, locality
                    sensitive hashing
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    0.64
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/soedinglab/mmseqs2">MMseqs2</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">k-mer based</td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    0.07
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/chenying2016/queries/tree/master/hs-blastn-src"
                  >BLASTN/P</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">alignment based, basic
                    local alignment
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    74.08
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://github.com/bioinformatics-centre/kaiju"
                  >Kaiju</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">alignment based on BWT
                    and FM-indexing schemes using protein sequences
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    14.63
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="https://pachterlab.github.io/kallisto/manual"
                  >Kallisto</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">alignment based,
                    pseudoalignment procedure
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    0.05
                  </td>
                </tr>
                <tr>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;"><a
                    href="http://clark.cs.ucr.edu/Overview/"
                  >CLARK</a></td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:left;">k-mer based species or
                    genus level classification
                  </td>
                  <td style="border-right: 1px solid #a9acb1; padding: 15px; text-align:right;">
                    0.04
                  </td>
                </tr>
                </tbody>
              </table>
              <br/>
              <!--                        <p>It is possible to add new classifiers to META by following the instructions in <a href="https://gitlab.jhuapl.edu/meta/meta_system/-/blob/staging/ADD_BIOCONTAINERS.md">ADD_BIOCONTAINERS.md</a>.</p>-->

            </h5>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "Home",
    data() {
      return {
        data: []
      };
    },
    mounted() {
    },
    methods: {}
  };
</script>
<!--<style>-->
/*table {*/
/*  border-collapse: collapse;*/
/*}*/
/*table, th, td {*/
/*  border: 1px solid #a9acb1;*/
/*}*/
/*th, td {*/
/*  padding: 15px;*/
/*  text-align: left;*/
/*}*/
<!--</style>-->
