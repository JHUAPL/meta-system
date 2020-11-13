#!/bin/bash
# **********************************************************************
# Copyright (C) 2019 Johns Hopkins University Applied Physics Laboratory
#
# All Rights Reserved.
# For any other permission, please contact the Legal Office at JHU/APL.
# **********************************************************************

usage() {
  cat <<EOF

REQUIRED:
	-h	help	show this message
	-i	FILE	diamond.report file
	-o	DIR*	directory that 'metacompare.sh -i' should be set to
				*this should be the same for all other classifier output parse scripts
					- dir will be made if it does not already exist
					- should probably be named for Evaluation_Job ID (refer to wiki db schema)

FORMAT:
	-102
		Taxonomic classification.
		This format will not print alignments but only a taxonomic classification for each query using the LCA algorithm. The output lines consist of 3 tab-delimited fields:

	1.	Query ID
	2.	NCBI taxonomy ID (0 if unclassified)
	3.	E-value of the best alignment with a known taxonomic ID found for the query (0 if unclassified)

EOF
}

# parse args
while getopts "hi:o:" OPTION; do
  case $OPTION in
  h)
    usage
    exit 1
    ;;
  i) INPUT=$OPTARG ;;
  o) OUTDIR=$OPTARG ;;
  ?)
    usage
    exit
    ;;
  esac
done
# check args
if [[ -z "$INPUT" ]]; then
  printf "%s\n" "Please specify an input tsv file (-i)."
  exit
fi
if [[ -z "$OUTDIR" ]]; then
  printf "%s\n" "Please specify an output directory (-o)."
  exit
fi
if [[ ! -f "$INPUT" ]]; then
  printf "%s\n" "The input (-i) $INPUT file does not exist."
  exit
fi
if [[ ! -d "$OUTDIR" ]]; then mkdir -p "$OUTDIR"; fi

# absolute path to script dir
absolute_path_x="$(
  readlink -fn -- "$0"
  echo x
)"
absolute_path_of_script="${absolute_path_x%x}"
scriptdir=$(dirname "$absolute_path_of_script")
bin="$scriptdir/bin"
runtime=$(date +"%Y%m%d%H%M%S%N")
tmp="$scriptdir/tmp-$runtime"
mkdir "$tmp"

# calculate abundance of lowest OR species (if no lower classification) taxids from report file
#	'total reads' (denominator for abundance calc) ignores unclassified reads
get_taxid_abundance() {
  # return list of unique taxids from report
  cut -f2 "$1" | sort | uniq >"$tmp/taxid.list.tmp"
  # discard taxid 0 (unclassifed)
  grep -v "^0$" "$tmp/taxid.list.tmp" >"$tmp/taxid.list"

  # aggregate counts (ignore taxid 0), calc abundance
  awk -F'\t' '{
		if(FNR==NR){
			count[$2]++;
			total++;
		}else{
			printf("%s\t%s\n",$0,count[$0]/total);
		}
	}' <(grep -vP "\t0\t" "$1") "$tmp/taxid.list" >"$tmp/parse.tmp"
  # roll up abundances if any taxids are repeated
  awk -F'\t' '{abu[$1]+=$2}END{for(taxid in abu){printf("%s\t%.9f\n",taxid,abu[taxid])}}' "$tmp/parse.tmp"
}
export tmp
export -f get_taxid_abundance

# print abundances for 'leaf' identified tax IDs (species and below, ie. strain)
get_taxid_abundance "$INPUT" >"$OUTDIR/parsed_diamond"

rm -rf "$tmp"
