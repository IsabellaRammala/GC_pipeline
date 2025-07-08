#!/usr/bin/env bash
#SBATCH --job-name=GCPEASMKT
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu.q
#SBATCH --time=24:00:00
#SBATCH --cpus-per-task=8
#SBATCH --output=/hercules/results/isara/test_peasoup/01_peasoup_job_MKAT_%j.out
#SBATCH --error=/hercules/results/isara/test_peasoup/01_peasoup_job_MKAT_%j.err

echo "Running PEASOUP on /hercules/scratch/isara/gc/gcpeas_nongit/2025-02-06_cfbf00000_0000032812498944_filtool_01.fil"
singularity exec -B /hercules/scratch/isara/gc/gcpeas_nongit,/hercules/results/isara/,/hercules/scratch/isara/ /hercules/scratch/isara/containers/peasoup_latest.sif peasoup -p --dm_start 0 --dm_end 977.5 --acc_start -50.0 --acc_end 50.0 --nharmonics 8 --min_snr 7.0 -o /hercules/results/isara/test_peasoup/peasoup_test_output -i /hercules/scratch/isara/gc/gcpeas_nongit/2025-02-06_cfbf00000_0000032812498944_filtool_01.fil
singularity exec -B /hercules/scratch/isara/gc/gcpeas_nongit,/hercules/results/isara/,/hercules/scratch/isara/ /hercules/scratch/isara/containers/peasoup_latest.sif peasoup -p --dm_start 977.5 --dm_end 1668.5 --acc_start -50.0 --acc_end 50.0 --nharmonics 8 --min_snr 7.0 -o /hercules/results/isara/test_peasoup/peasoup_test_output -i /hercules/scratch/isara/gc/gcpeas_nongit/2025-02-06_cfbf00000_0000032812498944_filtool_01.fil
singularity exec -B /hercules/scratch/isara/gc/gcpeas_nongit,/hercules/results/isara/,/hercules/scratch/isara/ /hercules/scratch/isara/containers/peasoup_latest.sif peasoup -p --dm_start 1668.5 --dm_end 3000.5 --acc_start -50.0 --acc_end 50.0 --nharmonics 8 --min_snr 7.0 -o /hercules/results/isara/test_peasoup/peasoup_test_output -i /hercules/scratch/isara/gc/gcpeas_nongit/2025-02-06_cfbf00000_0000032812498944_filtool_01.fil

echo "PEASOUP job completed"
