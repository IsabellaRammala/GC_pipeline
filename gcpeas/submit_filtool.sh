#!/usr/bin/env bash
#SBATCH --job-name=20240321FLT
#SBATCH --partition=short.q
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=32G
#SBATCH --output=filtool_all_%j.out
#SBATCH --error=filtool_all_%j.err

#export APPTAINER_BINDPATH=$PWD,/mandap/incoming/meertrans/tapeStaging/29437/TRAPUM/SCI-20200703-MK-05/gc00/20240321_023307/cfbf00000/,/hercules/results/isara/,/u/isara/
#time singularity exec /u/isara/CONTAINERS/pulsarx_latest.sif filtool -v -f /mandap/incoming/meertrans/tapeStaging/29437/TRAPUM/SCI-20200703-MK-05/gc00/20240321_023307/cfbf00000/*

# ---- User Config ----
INPUT_LIST="20240321_094530_data.txt"
OUTPUT_BASE="/hercules/results/isara"
PULSARX_IMG="/u/isara/CONTAINERS/pulsarx_latest.sif"
PYTHON_SCRIPT="$PWD/runfiltool.py"

export APPTAINER_BINDPATH=$PWD,/mandap,/hercules/results/isara,/u/isara

while IFS= read -r input_dir; do
    if [[ -z "$input_dir" ]]; then
        continue  # skip empty lines
    fi
    echo "[INFO] Processing: $input_dir"
    python3 "$PYTHON_SCRIPT" "$input_dir" "$OUTPUT_BASE" "$PULSARX_IMG"
done < "$INPUT_LIST"
