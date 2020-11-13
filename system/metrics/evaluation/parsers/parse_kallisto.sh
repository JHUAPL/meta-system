#!/bin/bash
usage() {
  cat <<EOF
Output abundance profile of 'lowest classification of reads' to a 2-column tsv file, to be used for evaluation by the 'metacompare.sh' script. What is meant by 'lowest classificatino of reads' is that only taxids with reads DIRECTLY assigned to them (i.e. all rows in a kraken.report column3 != 0) will have a row in the abundance profile output.

REQUIRED:
	-h	help	show this message
	-i	FILE	kallisto.report file
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

# kallisto output format:
#	1	target_id	<-	accession
#	2	length
#	3	eff_length
#	4	est_counts	<- raw read count
#	5	tpm			<- normalized per million reads... not useful here

# remove header, only keep rows where est_counts!=0, then target_id and est_counts columns
tail -n+2 "$INPUT" | awk -F'\t' '{if($4!=0){printf("%s\t%s\n",$1,$4)}}' >"$tmp/k.tmp"

# get unique accessions, find taxid for each
cut -f1 "$tmp/k.tmp" | sort | uniq >"$tmp/k.cut1"
# return line from taxdump where accession ($2) matches, taxid is col $3
awk -F'\t' '{
	if(NR==FNR){
		acc[$0]=FNR;
	}else{
		if($1 in acc){
			print($0);
		}
	}
}' "$tmp/k.cut1" "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid_a2t" >"$tmp/k.a2t"

# match acc to taxids, then calc and output predicted abundance profile
#	'total reads' (denominator for abundance calc) ignores unclassified reads
awk -F'\t' '{if(NR==FNR){
		taxid[$1]=$2;
	}else{
		count[$1]+=$2;
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
}' "$tmp/k.a2t" "$tmp/k.tmp" >"$tmp/parsed_kallisto"

cp "$tmp/parsed_kallisto" "$OUTDIR/parsed_kallisto"

rm -rf "$tmp"
