#!/usr/bin/env python3
import os
import glob

# Directory to the beams
beam_pattern = "/hercules/results/isara/20240321_094530/gc00/cfbf*"


pulsarx_img = "/u/isara/CONTAINERS/pulsarx_latest.sif"
meerkat_fold_template = "/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/meerkat_fold_S4.template"
results_base = "/hercules/scratch/isara"

# SLURM job template
slurm_template = """#!/usr/bin/env bash
#SBATCH --job-name={jobname}
#SBATCH --partition=long.q
#SBATCH --time=08:00:00
#SBATCH --cpus-per-task=12
#SBATCH --mem=125G
#SBATCH --output={beam_dir}/{jobname}_%j.out
#SBATCH --error={beam_dir}/{jobname}_%j.err

SECONDS=0

echo "== Environment Setup =="
export APPTAINER_BINDPATH=$PWD,/mandap,/hercules/scratch/isara,/u/isara

FILFILE="{filfile}"
OUTFILE="{outfile}"
TESTXML="{xmlfile}"
CANDS="{candfile}"
MKAT_FOLD_TEMP="{fold_template}"
RESULTS_BASE="{results_base}"
PULSARX_IMG="{pulsarx_img}"

# Temporary working directory on node
TMPDIR="/tmp/${{SLURM_JOB_ID}}_2500"
mkdir -p "$TMPDIR"

echo "== Copying input files to TMPDIR =="
cp "$CANDS" "$TMPDIR"
cp "$PULSARX_IMG" "$TMPDIR"
cp "$MKAT_FOLD_TEMP" "$TMPDIR"
cp "$FILFILE" "$TMPDIR"
cp "$TESTXML" "$TMPDIR"

echo "== TMPDIR Contents =="
ls -lh "$TMPDIR"

# Define working filenames inside TMPDIR
cands_file="${{TMPDIR}}/$(basename "$CANDS")"
pulsarx_sif="${{TMPDIR}}/$(basename "$PULSARX_IMG")"
fold_temp="${{TMPDIR}}/$(basename "$MKAT_FOLD_TEMP")"
fil_file="${{TMPDIR}}/$(basename "$FILFILE")"
outfile="${{TMPDIR}}/$(basename "$OUTFILE")"

echo "== Running PSRFOLD_FIL on: $cands_file =="
singularity exec --nv "$pulsarx_sif" psrfold_fil -v -t 12 --candfile "$cands_file" -n 64 -b 64 --template "$fold_temp" -f "$fil_file" -o "$outfile"

# Determine results directory on scratch, maintaining beam structure
beam_subpath = "{beam_subpath}"
result_dir="${{RESULTS_BASE}}/{beam_subpath}"
mkdir -p "$result_dir"
echo "== Moving folded output to: $result_dir =="
cp "$outfile"* "$result_dir/"

# Cleanup
echo "== Cleaning up TMPDIR: $TMPDIR =="
rm -rf "$TMPDIR"

echo "== Job Done =="
echo "****ELAPSED "$SECONDS" $SLURM_JOB_ID"
"""

# Loop over all beam directories
for beam_dir in sorted(glob.glob(beam_pattern)):
    if not os.path.isdir(beam_dir):
        continue
    fil_files = glob.glob(os.path.join(beam_dir, "*.fil"))
    cand_files = glob.glob(os.path.join(beam_dir, "*_pulsarx.cands"))
    xml_files = glob.glob(os.path.join(beam_dir, "overview.xml"))

    if not fil_files:
        print(f"Skipping {beam_dir}: no .fil file found")
        continue

    if not cand_files:
        print(f"Skipping {beam_dir}: no _pulsarx.cands file found")
        continue

    if not xml_files:
        print(f"Skipping {beam_dir}: no overview.xml found")
        continue
        
    filfile = fil_files[0]
    candfile = cand_files[0]
    xmlfile = xml_files[0]

    beam_name = os.path.basename(filfile).split(".")[0]
    outfile = os.path.join(beam_dir, f"{beam_name}_PSRFOLD")

    jobname = f"{beam_name}_FOLD"
    script_name = f"{beam_name}_psrfold.sh"
    script_path = os.path.join(beam_dir, script_name)

    # Preserve subpath after /hercules/results/isara/ to maintain structure
    beam_subpath = os.path.relpath(beam_dir, "/hercules/results/isara")

    # Fill template
    script_content = slurm_template.format(
        jobname=jobname,
        filfile=filfile,
        candfile=candfile,
        xmlfile=xmlfile,
        fold_template=meerkat_fold_template,
        pulsarx_img=pulsarx_img,
        results_base=results_base,
        beam_dir=beam_dir,
        outfile=outfile,
        beam_subpath=beam_subpath
    )
    # Write SLURM script
    with open(script_path, "w") as f:
        f.write(script_content)

    print(f"Generated SLURM script: sbatch {script_path}")