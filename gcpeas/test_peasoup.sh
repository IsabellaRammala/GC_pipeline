#!/usr/bin/env bash
#SBATCH --job-name=TESTPS
#SBATCH --partition=gpu.q
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=2
#SBATCH --time=02:00:00
#SBATCH --mem=64G
#SBATCH --output=peasoup_test_%j.out
#SBATCH --error=peasoup_test_%j.err

singularity exec -B $PWD,/hercules /u/isara/CONTAINERS/peasoup_latest.sif  peasoup -i /hercules/scratch/isara/DATA/TEST_DATA/test_epoch/OBS_1.fil  -o /hercules/results/isara/test_peasoup/OBS_1_peasoup_test --dm_start 0 --dm_end 10 --acc_start 0 --acc_end 1 --nharmonics 1 --min_snr 8 --ram_limit_gb 64 --limit 100 --fft_size 4194304