#!/usr/bin/env bash
#SBATCH --job-name=TESTPS
#SBATCH --partition=gpu.q
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=12
#SBATCH --mem=125G
#SBATCH --output=/hercules/results/isara/peasoup_test_%j.out
#SBATCH --error=/hercules/results/isara/peasoup_test_%j.err

SECONDS=0

export APPTAINER_BINDPATH=$PWD,/mandap,/hercules/scratch/isara,/u/isara

# FILFILE="/hercules/scratch/isara/DATA/SCI-20200703-MK-05/gc00/20240321_061310/cfbf00022/31122620_01.fil"
# RESULTS_BASE="/hercules/results/isara"
# PULSARX_IMG="/u/isara/CONTAINERS/pulsarx_latest.sif"
# PEASOUP_IMG="/u/isara/CONTAINERS/peasoup_latest.sif"
# PYTHON_SCRIPT="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/00_runfiltool.py"
# FILPLAN="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/filplan.json"

# TMPDIR=/tmp/${SLURM_JOB_ID}
# # filtlfil_name="${TMPDIR}/20minfil.fil"
# # # Make WD in the local scratch
# # mkdir -p "$TMPDIR"
# # # run filtool (read data from mandap and save output to TMPDIR)
# # python3 "$PYTHON_SCRIPT" "$FILFILE" "$TMPDIR" "$PULSARX_IMG"
# # # Run filtool for the 10 min files

# # run peasoup on the cleaned 20 minutes filterbank file 
# echo "Copying ${FILFILE} to ${TMPDIR}"
# cp -r ${FILFILE} ${TMPDIR}
# cp -r ${PEASOUP_IMG} ${TMPDIR}
# echo "Printing what is in the directory"
# ls $TMPDIR

# cleaned_file="${TMPDIR}/31122620_01.fil"
# search_file="${TMPDIR}/20240321_061310_cfbf00022_20min"
# peasoup_sif="${TMPDIR}/peasoup_latest.sif"
# echo "Now running PEASOUP on ${cleaned_file}"
# # singularity exec --nv -B $TMPDIR,/hercules,/u/isara $PEASOUP_IMG peasoup -i $cleaned_file -o $TMPDIR --dm_start 0 --dm_end 6000 --acc_start 100 --acc_end 100 --nharmonics 8 --min_snr 7 --ram_limit_gb 90 --limit 100000 --fft_size 4194304
# # run also the 10 minute search

# # Moving the data back to results
# result_dir=${RESULTS_BASE}/${SLURM_JOB_ID}
# mkdir -p $result_dir
# echo "Copying the data from ${TMPDIR} to ${result_dir}"
# cp $TMPDIR $result_dir



# # singularity exec --nv -B $PWD,/hercules /u/isara/CONTAINERS/peasoup_latest.sif  peasoup -i /hercules/scratch/isara/DATA/SCI-20200703-MK-05/gc00/20240321_061310/cfbf00022/2024-03-21-02:32:42_cfbf00000_0000000000000000.fil_01.fil  -o /hercules/results/isara/test_peasoup/OBS_1_peasoup_test --dm_start 0 --dm_end 10 --acc_start 0 --acc_end 1 --nharmonics 1 --min_snr 8 --ram_limit_gb 10 --limit 100 --fft_size 4194304


echo "== Environment Setup =="

# Bind paths
export APPTAINER_BINDPATH=$PWD,/mandap,/hercules/scratch/isara,/u/isara

# Input and config paths
FILFILE="/hercules/scratch/isara/DATA/SCI-20200703-MK-05/gc00/20240321_061310/cfbf00022/31122620_01.fil"
RESULTS_BASE="/hercules/results/isara"
PULSARX_IMG="/u/isara/CONTAINERS/pulsarx_latest.sif"
PEASOUP_IMG="/u/isara/CONTAINERS/peasoup_latest.sif"
PYTHON_SCRIPT="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/00_runfiltool.py"
FILPLAN="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/filplan.json"

# Create a working directory in local tmp
TMPDIR="/tmp/${SLURM_JOB_ID}_500"
mkdir -p "$TMPDIR"

echo "== Copying Input Files to TMPDIR =="
cp "$FILFILE" "$TMPDIR"
cp "$PEASOUP_IMG" "$TMPDIR"

echo "== TMPDIR Contents =="
ls -lh "$TMPDIR"

# Define working filenames inside TMPDIR
cleaned_file="${TMPDIR}/$(basename "$FILFILE")"
peasoup_sif="${TMPDIR}/$(basename "$PEASOUP_IMG")"

echo "== Running PEASOUP on: $cleaned_file =="

singularity exec --nv "$peasoup_sif" peasoup -i "$cleaned_file" -o "$TMPDIR" --dm_start 0 --dm_end 6000 --acc_start -2500 --acc_end 2500 --nharmonics 8 --min_snr 7 --ram_limit_gb 100 --fft_size 4194304 --limit 1000


# Prepare result directory and move data
result_dir="${RESULTS_BASE}/${SLURM_JOB_ID}"
mkdir -p "$result_dir"
echo "== Moving results to: $result_dir =="
cp -r "$TMPDIR"/* "$result_dir/"

# Cleanup local scratch
echo "== Cleaning up TMPDIR: $TMPDIR =="
rm -rf "$TMPDIR"

echo "== Job Done =="

echo "****ELAPSED "$SECONDS" $SLURM_JOB_ID"
