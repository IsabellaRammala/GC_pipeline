#!/usr/bin/env python3
import glob
import subprocess

# find all generated PSRFOLD SLURM scripts
slurm_scripts = "/hercules/results/isara/20240321_094530/gc00/cfbf0*/*_psrfold.sh"

for script_path in sorted(glob.glob(slurm_scripts)):
    try:
        subprocess.run(["sbatch", script_path], check=True)
        print(f"Submitted: {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to submit {script_path}: {e}")