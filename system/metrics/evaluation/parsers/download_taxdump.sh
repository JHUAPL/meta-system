#!/usr/bin/env bash

absolute_path_x="$(
  readlink -fn -- "$0"
  echo x
)"
absolute_path_of_script="${absolute_path_x%x}"
scriptdir=$(dirname "$absolute_path_of_script")

# setup for accession to taxid
if [[ ! -f "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid" ]]; then
  echo >&2 "getting ncbi taxonomy files"
  mkdir -p "$scriptdir/taxdump/accession2taxid"
  # Quiet, since we might run this w/o a tty... and --progress=dot (default when no TTY) prints too many lines...
  wget --quiet ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz -O "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid.gz"
  gunzip "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid.gz"
fi

echo >&2 "Finished download"
echo >&2 "Running optimizations..."

# adjustments for clark, blastn, kallisto
if [[ ! -f "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid_a2t" ]]; then
  cut -f2,3 "$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid" >"$scriptdir/taxdump/accession2taxid/nucl_gb.accession2taxid_a2t"
fi

echo >&2 "Done"

exit 0
