#!/bin/bash
usage() {
  cat <<EOF
Output abundance profile of 'lowest classification of reads' to a 2-column tsv file, to be used for evaluation by the 'metacompare.sh' script. What is meant by 'lowest classificatino of reads' is that only taxids with reads DIRECTLY assigned to them (i.e. all rows in a kraken.report column3 != 0) will have a row in the abundance profile output.

REQUIRED:
	-h	help	show this message
	-i	FILE	blastn.report file (blastn format 6)
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

# no header to deal with for b6 format
# there ARE multiple hits per read id, so find the best hit per read based on E-value
awk -F'\t' '{
	if($1 in b){if($12>b[$1]){b[$1]=$12;best[$1]=$0;}}else{b[$1]=$12;best[$1]=$0;}
}END{
	for(r in best){print(best[r]);}
}' "$INPUT" >"$tmp/b.tmp"

# get unique accessions, find taxid for each
cut -f2 "$tmp/b.tmp" | sort | uniq >"$tmp/b.cut2"
# return line from taxdump where accession ($2) matches, taxid is col $3
awk -F'\t' '{
	if(NR==FNR){
		acc[$0]=FNR;
	}else{
		if($1 in acc){
			print($0);
		}
	}
}' "$tmp/b.cut2" "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid_a2t" >"$tmp/b.a2t"

# match acc to taxids, then calc and output predicted abundance profile
#	'total reads' (denominator for abundance calc) ignores unclassified reads
awk -F'\t' '{
	if(NR==FNR){
		taxid[$1]=$2;
	}else{
		count[$2]++;
	}
}END{
	for(a in count){
		if(a in taxid){
			tcount[taxid[a]]+=count[a];
			total+=count[a];
		}
	}
	for(t in tcount){
		printf("%s\t%.9f\n",t,tcount[t]/total);
	}
}' "$tmp/b.a2t" "$tmp/b.tmp" >"$tmp/parsed_blastn"

cp "$tmp/parsed_blastn" "$OUTDIR/parsed_blastn"

rm -rf "$tmp"
