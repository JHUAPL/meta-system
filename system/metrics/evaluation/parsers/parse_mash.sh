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
	-i	FILE	mash.report file
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

# setup for accession to taxid
if [[ ! -f "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid" ]]; then
  echo >&2 "getting ncbi taxonomy files"
  mkdir -p "$scriptdir/taxdump/accession2taxid"
  wget ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz -O "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid.gz"
  gunzip "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid.gz"
fi

acc2taxid() {
  grep -m1 "$1" "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid"
}
export tmp scriptdir
export -f acc2taxid

# make 2col tsv of 'read count' and 'accession'
sed -e 's/.*\t\[//' -e 's/ seqs] /\t/' -e 's/ .*//' "$INPUT" >"$tmp/reads.acc"
# make list of accessions for finding taxid from nucl_gb...
cut -f2 "$tmp/reads.acc" >"$tmp/acc.list"
parallel --arg-file "$tmp/acc.list" --jobs=$(nproc) acc2taxid >"$tmp/a.av.taxid.gi"

# map read counts to taxids with accessions
awk -F'\t' '{if(NR==FNR){taxid[$2]=$3}else{printf("%s\t%s\n",$1,taxid[$2])}}' "$tmp/a.av.taxid.gi" "$tmp/reads.acc" >"$tmp/reads.taxid"

# calc and output predicted abundance profile
awk -F'\t' '{
	count[$2]+=$1;
	total+=$1;
}END{
	for(t in count){
		printf("%s\t%.9f\n",t,count[t]/total)
	}
}' "$tmp/reads.taxid" >"$OUTDIR/parsed_mash"

#rm -rf "$tmp"
