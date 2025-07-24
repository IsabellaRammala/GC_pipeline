#!/usr/bin/env python3
import os
import sys
import glob
import subprocess

def run_filtool(input_dir, output_dir, pulsarx_path):
    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    fil_files = sorted(glob.glob(os.path.join(input_dir, "*.fil")))
    if not fil_files:
        print(f"[ERROR] No .fil files found in {input_dir}")
        return

    out_base = os.path.basename(fil_files[0])
    output_file = os.path.join(output_dir, out_base)

    cmd = [
        "singularity", "exec", 
        "-B", f"{os.getcwd()},/mandap,/hercules/results/isara,/u/isara",
        pulsarx_path,
        "filtool", "-v",
        "-o", output_file,
        "-f"
    ] + fil_files  

    print(f"[INFO] Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] filtool failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: runfiltool.py <input_dir> <output_dir> <pulsarx.sif>")
        sys.exit(1)

    run_filtool(sys.argv[1], sys.argv[2], sys.argv[3])
