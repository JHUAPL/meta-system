#!/bin/bash
# **********************************************************************
# Copyright (C) 2019 Johns Hopkins University Applied Physics Laboratory
#
# All Rights Reserved.
# For any other permission, please contact the Legal Office at JHU/APL.
# **********************************************************************

usage() {
  cat <<EOF
Output abundance profile of 'lowest classification of reads' to a 2-column tsv file, to be used for evaluation by the 'metacompare.sh' script. What is meant by 'lowest classificatino of reads' is that only taxids with reads DIRECTLY assigned to them (kraken.report column3 != 0) will have a row in the abundance profile output.

REQUIRED:
	-h	help	show this message
	-i	FILE	centrifuge.report file (formatted as kraken.report)
	-o	DIR*	directory that 'metacompare.sh -i' should be set to
				*this should be the same for all other classifier output parse scripts
					- dir will be made if it does not already exist
					- should probably be named for Evaluation_Job ID (refer to wiki db schema)

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

absolute_path_x="$(
  readlink -fn -- "$0"
  echo x
)"
absolute_path_of_script="${absolute_path_x%x}"
scriptdir=$(dirname "$absolute_path_of_script")
runtime=$(date +"%Y%m%d%H%M%S%N")
tmp="$scriptdir/tmp-$runtime"
mkdir "$tmp"

# return abundances only for taxids with reads DIRECTLY assigned to them
#	'total reads' (denominator for abundance calc) ignores unclassified reads
get_taxid_abundance() {
  # get taxid and counts for reads directly assigned to taxids
  awk -F'\t' '{if($3!=0){print($0)}}' "$1" >"$tmp/kr.tmp"
  # discard taxid 0 (unclassifed) assigned reads
  grep -vP "\tU\t0\t" "$tmp/kr.tmp" >"$tmp/kraken.tmp"

  # calc and output predicted abundance profile
  cut -f3,5 "$tmp/kraken.tmp" | awk -F'\t' '{
		count[$2]+=$1;
		total+=$1;
	}END{
		for(t in count){
			printf("%s\t%.9f\n",t,count[t]/total)
		}
	}'
}
export tmp
export -f get_taxid_abundance

get_taxid_abundance "$INPUT" >"$OUTDIR/parsed_centrifuge"

rm -rf "$tmp"
