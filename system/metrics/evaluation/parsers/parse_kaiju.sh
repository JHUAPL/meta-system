#!/bin/bash
usage() {
  cat <<EOF
Output abundance profile of 'lowest classification of reads' to a 2-column tsv file, to be used for evaluation by the 'metacompare.sh' script. What is meant by 'lowest classificatino of reads' is that only taxids with reads DIRECTLY assigned to them (kraken.report column3 != 0) will have a row in the abundance profile output.

REQUIRED:
	-h	help	show this message
	-i	FILE	kaiju.report file
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

# turn line from taxdump where accession matches
acc2taxid() {
  grep -m1 "$1" "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid"
}
export tmp scriptdir
export -f acc2taxid

# only print col4 (taxids) that match a string of 1 or more numbers
#	i.e. will not print header, 'unclassified' line, or where taxid==NA (also lines like:
#		 'Warning: Taxon ID 88116243 is not contained in /db/taxonomy/nodes.dmp.')
awk -F'\t' '$4~/[0-9]+/ {print($0)}' "$INPUT" >"$tmp/kaiju.tmp1"

# calc and output predicted abundance profile
#	'total' (denominator for abundance calc) ignores unclassified reads
awk -F'\t' '{
	count[$4]+=$3;
	total+=$3;
}END{
	for(t in count){
		printf("%s\t%.9f\n",t,count[t]/total)
	}
}' "$tmp/kaiju.tmp1" >"$OUTDIR/parsed_kaiju"

rm -rf "$tmp"
