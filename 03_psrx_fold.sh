#!/usr/bin/env bash
#SBATCH --job-name=PSRXFLD
#SBATCH --partition=long.q
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --output=/hercules/results/isara/test_peasoup/03_psrx_fold_job_OBS_1_%j.out
#SBATCH --error=/hercules/results/isara/test_peasoup/03_psrx_fold_job_OBS_1_%j.err

singularity exec -B /hercules/scratch/isara/gc/gcpeas_nongit,/hercules/results/isara/,/hercules/scratch/isara/ /hercules/scratch/isara/containers/pulsarx_latest.sif psrfold_fil -v --candfile /hercules/results/isara/test_peasoup/peasoup_test_output/obs_fil/candidates_for_pulsarx.cands  --template /hercules/scratch/isara/gc/gcpeas_nongit/meerkat_fold.template --plotx -n 64 -b 64 --clfd 2 -f /hercules/scratch/isara/gc/gcpeas_nongit/OBS_1.fil
