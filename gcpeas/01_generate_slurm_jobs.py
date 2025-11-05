#!/usr/bin/env python3
import os

# beam_list_file = "/u/isara/pipeline_runs/20241207/gcpeas/20241207_fromArchiv.txt"  
beam_list_file = "/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/data/20241207_fromArchiv.txt"
output_dir = "/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/SCRIPTS/20241207_fromArchiv"
os.makedirs(output_dir, exist_ok=True)

# SLURM job template
template = """#!/usr/bin/env bash
#SBATCH --job-name={jobname}
#SBATCH --partition=gpu.q
#SBATCH --gres=gpu:3
#SBATCH --cpus-per-task=24
#SBATCH --mem=370G
#SBATCH --output={jobname}.out
#SBATCH --error={jobname}.err

SECONDS=0

export APPTAINER_BINDPATH=$PWD,/mandap,/hercules/results/isara,/hercules/scratch/isara,/u/isara

python3 -u 0_clean.py -v {beam_path}

echo "****ELAPSED "$SECONDS" $SLURM_JOB_ID"
"""

with open(beam_list_file) as f:
    for i, beam_path in enumerate(f, start=1):
        beam_path = beam_path.strip()
        if not beam_path:
            continue

        # Create a job name based on beam name
        beam_name = os.path.basename(beam_path)
        epoch = beam_path.split('/')[-2]
        script_name = "{}_search.sh".format(beam_name)
        jobname = "{}".format(beam_name[:4] + beam_name[-3:])
        script_content = template.format(jobname=jobname, beam_path=beam_path)
        epoch_dir = os.path.join(output_dir, epoch)
        os.makedirs(epoch_dir, exist_ok=True)

        script_path = os.path.join(epoch_dir, script_name)
        print(f"sbatch {script_path}")
        
        with open(script_path, "w") as sf:
            sf.write(script_content)

