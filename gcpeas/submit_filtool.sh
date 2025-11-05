#!/usr/bin/env bash
#SBATCH --job-name=FLTcfbf02
#SBATCH --partition=short.q
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=12
#SBATCH --mem=125G
#SBATCH --output=filtool_cfbf00000_GC%j.out
#SBATCH --error=filtool_cfbf00000_GC%j.err

# export APPTAINER_BINDPATH=$PWD,/mandap/incoming/meertrans,/hercules/results/isara/,/u/isara/
# time singularity exec /u/isara/CONTAINERS/pulsarx_latest.sif filtool -v -f /mandap/incoming/meertrans/tapeStaging/29568/TRAPUM/SCI-20200703-MK-05/gc00/20240321_094530/cfbf00021/*

# # ---- User Config ----
# INPUT_LIST="20240321_094530_data.txt"
# TEST_BEAM="/mandap/incoming/meertrans/tapeStaging/29508/TRAPUM/SCI-20200703-MK-05/gc00/20240321_061310/cfbf00021"
TEST_BEAM=" /hercules/scratch/isara/20250919_test/cfbf00000/"

OUTPUT_BASE="/hercules/results/isara"
PULSARX_IMG="/u/isara/CONTAINERS/pulsarx_latest.sif"
PYTHON_SCRIPT="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/01_runfiltool.py"
FILPLAN="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/filplan.json"

export APPTAINER_BINDPATH=$PWD,/mandap,/hercules/results/isara,/u/isara

python3 "$PYTHON_SCRIPT" "$TEST_BEAM" "$OUTPUT_BASE" "$PULSARX_IMG" "$FILPLAN"




# # while IFS= read -r input_dir; do
# #     if [[ -z "$input_dir" ]]; then
# #         continue  
# #     fi
# #     echo "[INFO] Processing: $input_dir"
# #     python3 "$PYTHON_SCRIPT" "$input_dir" "$OUTPUT_BASE" "$PULSARX_IMG"
# # done < "$INPUT_LIST"
