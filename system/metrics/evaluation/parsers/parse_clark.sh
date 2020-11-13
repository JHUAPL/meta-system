#!/bin/bash
usage() {
  cat <<EOF
Output abundance profile of 'lowest classification of reads' to a 2-column tsv file, to be used for evaluation by the 'metacompare.sh' script. What is meant by 'lowest classificatino of reads' is that only taxids with reads DIRECTLY assigned to them (i.e. all rows in a kraken.report column3 != 0) will have a row in the abundance profile output.

REQUIRED:
	-h	help	show this message
	-i	FILE	clark.report file
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
#	IF NEEDED
#THREADS=$(printf $(nproc) | awk '{printf("%.0f",$0/2)}')
# single threades systems will return 0, change to 1 if 0
#if [[ "$THREADS" == "0" ]]; then THREADS=1; fi

# setup for accession to taxid
if [[ ! -f "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid_a2t" ]]; then
  echo >&2 "getting ncbi taxonomy files"
  mkdir -p "$scriptdir/taxdump/accession2taxid"
  wget ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz -O "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid.gz"
  gunzip "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid.gz"
  cut -f2,3 "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid" >"$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid_a2t"
fi

# CLARK output format: first line is column header
#	1	Object_ID, read header
#	2	Length, read length
#	3	Assignment, predicted taxid

# remove header, only keep rows where last column matches a string of 1 or more numbers
tail -n+2 "$INPUT" | grep ",[0-9]\+$" >"$tmp/k.tmp"

#	'total reads' (denominator for abundance calc) ignores unclassified reads
awk -F',' '{
		count[$3]++;
		total++
}END{
	for(t in count){
		printf("%s\t%.9f\n",t,count[t]/total);
	}
}' "$tmp/k.tmp" >"$tmp/parsed_clark"

cp "$tmp/parsed_clark" "$OUTDIR/parsed_clark"

rm -rf "$tmp"
