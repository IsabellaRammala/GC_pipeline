#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import shutil
import configparser  
import glob


def preamble():
    print('---------------------+----------------------------------------------------------')
    print('                     |')
    print('                     | ')
    print('      GC PEAS        | v0.1')
    print('                     | ')
    print('                     | ')
    print('---------------------+----------------------------------------------------------')

def read_config(config_file):
    """
    Reads the configuration file and returns the parameters as a dictionary.
    """
    if not os.path.exists(config_file):
        raise IOError("Config file {} not found.".format(config_file))
    
    config = configparser.ConfigParser()
    config.read(config_file)

    params = {
        "user": config.get("USER", "user_id"),
        "pipeline_dir": config.get("PIPELINE", "pipeline_dir"),
        "singularity_dir": config.get("PIPELINE", "singularity_dir"),
        "epoch": config.get("DATA", "epoch"),
        "data_dir": config.get("DATA", "data_dir"),
        "dspsr_singularity": config.get("DSPSR", "dspsr_singularity"),
        "readfile": config.get("PRESTO", "readfile"),
        "make_ddplan": config.get("PRESTO", "makeDDplan"),
        "make_birdies": config.get("PRESTO", "makebirdies"), 
        "make_zaplist": config.get("PRESTO", "makezaplist"),
        "presto_singularity": config.get("PRESTO", "presto_singularity"),
        "peasoup_singularity": config.get("PEASOUP", "peasoup_singularity"),
        "filterbank_dir": config.get("PEASOUP", "filterbank_dir"),
        "results_dir": config.get("PEASOUP", "results_dir"),
        "scratch_dir": config.get("PEASOUP", "scratch_dir"),
        "output_prefix": config.get("PEASOUP", "output_prefix"),
        "dm_start": config.getfloat("PEASOUP", "dm_start"),
        "dm_end": config.getfloat("PEASOUP", "dm_end"),
        "acc_start": config.getfloat("PEASOUP", "acc_start"),
        "acc_end": config.getfloat("PEASOUP", "acc_end"),
        "nharmonics": config.getint("PEASOUP", "nharmonics"),
        "min_snr": config.getfloat("PEASOUP", "min_snr"),
        "parallel": config.getboolean("PEASOUP", "parallel"),
        "output_dir": config.get("PEASOUP", "output_dir"),
        "job_name": config.get("PEASOUP", "job_name"),
        "partition": config.get("PEASOUP", "partition"),
        "time": config.get("PEASOUP", "time"),
        "cpus": config.getint("PEASOUP", "cpus"),
        "partition": config.get("SLURM", "partition"),
        "nodes": config.getint("SLURM", "nodes"),
        "ntasks": config.getint("SLURM", "ntasks"),
        "gres": config.get("SLURM", "gres"),
        "cpus-per-task": config.getint("SLURM", "cpus-per-task"),
        "mem": config.get("SLURM", "mem"),
        "time": config.get("SLURM", "time")
    }
    return params

# def combined_fil_file(fil1, fil2):
#     """
#     Given two filterbank file paths, generate a new name for the combined filterbank for be 
#     generated from dspr
#     """
#     parts1 = fil1.split('/')[-1].split('_')
#     parts2 = fil2.split('/')[-1].split('_')
#     prefix = '_'.join(parts1[:2])
#     start = parts1[2].replace('.fil', '')
#     end = parts2[2].replace('.fil', '')
#     combined_name = f"{prefix}_{start}_to_{end}.fil"
#     return combined_name


# def digifil_commands(beam, singularity_image, working_dir, output_dir=None, bits=8):
#     """
#     Given a directory containing 5-min filterbank files, generate digifil commands
#     to create 10-min and 20-min versions.
#     """
#     # beam_path = Path(beam)
#     output_path = output_dir if output_dir else beam

#     # Sort files by name (assumes time ordering is encoded in filename)
#     fil_files = sorted(glob.glob(os.path.join(beam, "*.fil")))

#     if len(fil_files) < 2:
#         raise ValueError("Need at least 2 .fil files to combine")

#     half_cmd = []
#     combined_file_names10 = []
#     # Create 10-min file (2 combinations)
#     for i in range(0, len(fil_files) - 1, 2):
#         f1 = fil_files[i]
#         f2 = fil_files[i + 1]
#         combined_name_10 = combined_fil_file(f1, f2)
#         combined_file_names10.append(combined_name_10)
#         out_file = os.path.join(output_path, combined_name_10)
#         cmd = f'singularity exec -B {working_dir} {singularity_image} digifil -cont -b {bits} -o {out_file} {f1} {f2}'
#         half_cmd.append(cmd)
    
#     # Create a 20-min file (all combined)
#     first_fil = fil_files[0]
#     last_fil= fil_files[-1]
#     combined_name_20 = combined_fil_file(first_fil, last_fil)
#     out_file = os.path.join(output_path, combined_name_20)
#     full_cmd = f'singularity exec -B {working_dir} {singularity_image} digifil -cont -b {bits} -o {out_file} {" ".join(fil_files)}'
    

#     return half_cmd, full_cmd


# def setup_directories(epoch, user_id, pipeline_path, singularity_path):
#     """
#     Sets up the input and output directories
#     """
#     # EVENTUALLY NEED TO GET THE USER AND TMP ENV DIRECTLY FROM BASH!!!
#     scripts_path = os.path.join(pipeline_path, "SCRIPTS")
#     tmp_base = os.path.join("/tmp", user_id)
#     destination_dir_name = "DATA"
#     tmp_data_path = os.path.join(tmp_base, destination_dir_name, epoch)
#     tmp_pipeline_path = os.path.join(tmp_base, os.path.basename(pipeline_path))
#     tmp_singularity_path = os.path.join(tmp_base, os.path.basename(singularity_path))
#     tmp_scripts_path = os.path.join(tmp_pipeline_path, os.path.basename(scripts_path))
#     tmp_results_path = os.path.join(tmp_base, ("RESULTS"))
#     # data_path = os.path.join(origin_dir, epoch)
#     return tmp_base, tmp_data_path, tmp_results_path, tmp_scripts_path, tmp_singularity_path, tmp_pipeline_path, scripts_path
    
    import os

def setup_directories(epoch, user_id, pipeline_path, singularity_path):
    """
    Sets up and creates the input and output directories.
    """
    scripts_path = os.path.join(pipeline_path, "SCRIPTS")
    tmp_base = os.path.join("/tmp", user_id)
    destination_dir_name = "DATA"
    
    tmp_data_path = os.path.join(tmp_base, destination_dir_name, epoch)
    tmp_pipeline_path = os.path.join(tmp_base, os.path.basename(pipeline_path))
    tmp_singularity_path = os.path.join(tmp_base, os.path.basename(singularity_path))
    tmp_scripts_path = os.path.join(tmp_pipeline_path, os.path.basename(scripts_path))
    tmp_results_path = os.path.join(tmp_base, "RESULTS")

    os.makedirs(tmp_data_path, exist_ok=True)
    os.makedirs(tmp_pipeline_path, exist_ok=True)
    os.makedirs(tmp_singularity_path, exist_ok=True)
    os.makedirs(tmp_scripts_path, exist_ok=True)
    os.makedirs(tmp_results_path, exist_ok=True)

    return tmp_base, tmp_data_path, tmp_results_path, tmp_scripts_path, tmp_singularity_path, tmp_pipeline_path, scripts_path

# def find_filterbank_files(directory):
#     """
#     Finds all filterbank (.fil) files in the specified directory and returns their paths as a list.
#     """
#     if not os.path.isdir(directory):
#         raise IOError("Directory {} not found.".format(directory))
    
#     filterbank_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".fil")]
#     # print (filterbank_files)
    
#     if not filterbank_files:
#         raise IOError("No filterbank files found in directory {}.".format(directory))
#     return filterbank_files

def peasoup_command(working_dir, singularity_path, results_dir, params, filterbank_file):
    """
    Generates the PEASOUP command string based on the provided parameters,
    """
    command = (
        "singularity exec -B {working_dir} {singularity_path} peasoup "
        "-i {filterbank_file} "
        "-o {output_prefix} "
        "--dm_start {dm_start} --dm_end {dm_end} "
        "--acc_start {acc_start} --acc_end {acc_end} "
        "--nharmonics {nharmonics} --min_snr {min_snr} "
        "--sta"
    ).format(
        working_dir=working_dir,
        filterbank_dir=params["epoch"],
        singularity_path=singularity_path,
        filterbank_file=filterbank_file,
        output_prefix=results_dir,
        dm_start=params["dm_start"],
        dm_end=params["dm_end"],
        acc_start=params["acc_start"],
        acc_end=params["acc_end"],
        nharmonics=params["nharmonics"],
        min_snr=params["min_snr"]
    )

    if params["parallel"]:
        command += "-p"
    # print(command)
    return command

# def copy_data(tmp_base, tmp_data_path, tmp_results_path, data_path, epoch, pipeline_path, singularity_path):
#     """
#     Copy the data, pipeline, and containmer to  processing node)
#     """    
#     if not os.path.exists(data_path):
#         raise FileNotFoundError(f"Data directory not found: {data_path}")
    
#     if os.path.exists(tmp_data_path):
#         print(f"[INFO] Data already exists in /tmp: {tmp_data_path}")
#         copy_commands = []
#     else:
#         tmp_dir = os.path.join(tmp_base, 'DATA')
#         tmp_epoch = os.path.join(tmp_dir, f'{epoch}')
#         copy_commands = [
#         f'mkdir -p "{tmp_base}"',
#         f'mkdir -p "{tmp_dir}"',
#         f'mkdir -p "{tmp_epoch}"',
#         f'mkdir -p "{tmp_results_path}"',
#         f'cp -r "{data_path}"/* "{tmp_data_path}"',
#         f'cp -r "{pipeline_path}" "{tmp_base}"',
#         f'cp -r "{singularity_path}" "{tmp_base}"'
#         ]

#     return copy_commands 

import os
import shutil

def copy_data(tmp_base, tmp_data_path, tmp_results_path, data_path, epoch, pipeline_path, singularity_path):
    """
    Copy the data, pipeline, and container to the processing node using shutil.
    Assumes necessary directories except tmp_data_path are already created.
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data directory not found: {data_path}")
    
    if os.path.exists(tmp_data_path):
        print(f"[INFO] Data already exists in /tmp: {tmp_data_path}")
        return []  

    # COPY DATA
    shutil.copytree(data_path, tmp_data_path)

    # COPY PIPELINE
    pipeline_dest = os.path.join(tmp_base, os.path.basename(pipeline_path))
    if not os.path.exists(pipeline_dest):
        shutil.copytree(pipeline_path, pipeline_dest)

    # COPY CONTAINERS
    singularity_dest = os.path.join(tmp_base, os.path.basename(singularity_path))
    if os.path.isdir(singularity_path):
        if not os.path.exists(singularity_dest):
            shutil.copytree(singularity_path, singularity_dest)
    else:
        if not os.path.exists(singularity_dest):
            shutil.copy2(singularity_path, singularity_dest)


# def copy_results(tmp_results_dir, results_dir):
#     """
#     Copy the results back to /scratch
#     """
#     # if not os.path.exists(tmp_results_dir):
#     #     raise FileNotFoundError(f"Temporary data directory not found: {tmp_results_dir}")
#     print(f"[INFO] Restoring data from {tmp_results_dir} to {results_dir} ...")
#     command = [f"cp -r {tmp_results_dir} {results_dir}"]
#     print(f"[INFO] Copy of results from node complete.")
#     return command


def copy_results(tmp_results_dir, results_dir):
    """
    Copy the results back to /scratch.
    """
    if not os.path.exists(tmp_results_dir):
        raise FileNotFoundError(f"Temporary results directory not found: {tmp_results_dir}")

    print(f"[INFO] Restoring data from {tmp_results_dir} to {results_dir} ...")

    os.makedirs(results_dir, exist_ok=True)

    for item in os.listdir(tmp_results_dir):
        src = os.path.join(tmp_results_dir, item)
        dst = os.path.join(results_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    print(f"[INFO] Copy of results from node complete.")
    return [f"Copied results from {tmp_results_dir} to {results_dir}"]

# def presto_readfile(params, filterbank_file):
#     """
#     Use presto to read the filterbank file and save the header info into a file
#     """
#     current_dir = os.getcwd()

#     command = (
#         "singularity exec -B {current_dir},{results_dir},{scratch_dir},{filterbank_dir} {singularity_image} readfile {filterbank_file}"        
#     ).format(
#         current_dir=current_dir,
#         results_dir=params[""]
#     )
# def write_slurm_copy_data(script_name, copy_commands, params, beam_dir, results_dir, scripts_path, working_dir):
#     """
#     Writes the slurm sript to copy data to /tmp
#     """
#     beam = beam_dir.split('/')[-1]
#     job_name = f"CP{beam}"

#     tmp_script_path = os.path.join(working_dir, script_name)
    
#     slurm_header = """#!/usr/bin/env bash
# #SBATCH --job-name={job_name}
# #SBATCH --partition=short.q
# #SBATCH --time=00:20:00
# #SBATCH --cpus-per-task=2
# #SBATCH --output={results_dir}/{job_name}_%j.out
# #SBATCH --error={results_dir}/{job_name}_%j.err
#     """.format(job_name=job_name,
#             results_dir=results_dir,
#             partition=params['partition'],
#             cpu_time=params['time'],
#             cpus=params['cpus'], 
#             )
#     with open(tmp_script_path, "w") as f:
#         f.write(slurm_header)
#         f.write("\n")
#         f.write("set -euo pipefail\n\n")

#         for command in copy_commands:
#             f.write(command + "\n")
#         f.write("\n")
#     os.chmod(tmp_script_path, 0o755)
#     print("SLURM copy-data script written to {}".format(tmp_script_path))

def write_slurm_combine10(script_name, commands, params, beam_dir, results_dir, scripts_path, working_dir):
    """
    Writes the slurm sript to combine filterbank files to 10 & 20 min time chuncks
    """
    beam = beam_dir.split('/')[-1]
    # script_name = f"02_combine10_{beam}.sh"
    job_name = f"CBN10{beam}"
    tmp_script_path = os.path.join(working_dir, script_name)
    # tmp_script_path = os.path.join(scripts_path, script_name)

    slurm_header = """#!/usr/bin/env bash
#SBATCH --job-name={job_name}
#SBATCH --partition=short.q
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --output={results_dir}/{job_name}_%j.out
#SBATCH --error={results_dir}/{job_name}_%j.err
    """.format(job_name=job_name,
                results_dir=results_dir,
                partition=params['partition'],
                cpu_time=params['time'],
                cpus=params['cpus'], 
                )          

    with open(tmp_script_path, "w") as f:
        f.write(slurm_header)
        f.write("\n")

        for command in commands:
            f.write(command + "\n")
            # print (command)
        f.write("\n")
    os.chmod(tmp_script_path, 0o755)
    print("SLURM combine filterbanks to 10 min chunks script written to {}".format(tmp_script_path))

def write_slurm_combine20(script_name, commands, params, beam_dir, results_dir, scripts_path, working_dir):
    """
    Writes the slurm sript to combine filterbank files to 10 & 20 min time chuncks
    """
    beam = beam_dir.split('/')[-1]
    job_name = f"CBN20{beam}"

    tmp_script_path = os.path.join(working_dir, script_name)
    # tmp_script_path = os.path.join(scripts_path, script_name)

    slurm_header = """#!/usr/bin/env bash
#SBATCH --job-name={job_name}
#SBATCH --partition=short.q
#SBATCH --time=00:20:00
#SBATCH --cpus-per-task=2
#SBATCH --output={results_dir}/{job_name}_%j.out
#SBATCH --error={results_dir}/{job_name}_%j.err
    """.format(job_name=job_name,
                results_dir=results_dir,
                partition=params['partition'],
                cpu_time=params['time'],
                cpus=params['cpus'], 
                )        
    with open(tmp_script_path, "w") as f:
        f.write(slurm_header)
        f.write("\n")
        f.write(commands)
        # print (commands)
    os.chmod(tmp_script_path, 0o755)
    print("SLURM combine filterbanks to 20 min chunk script written to {}".format(tmp_script_path))


def write_slurm_search_beam(script_name, peasoup_command, params, beam_dir, results_dir, scripts_path, working_dir):
    """
    Writes the SLURM job script for submitting the PEASOUP jobs.
    """
    # output_script_name = f'submit__search_{beam_name}_jobs.sh'
    tmp_script_path = os.path.join(working_dir, script_name)
    
    beam = beam_dir.split('/')[-1]
    job_name = f"SCH20{beam}"
    # tmp_script_path = os.path.join(scripts_path, script_name)

    slurm_header = """#!/usr/bin/env bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --time={cpu_time}
#SBATCH --cpus-per-task={cpus}
#SBATCH --output={results_dir}/{job_name}_%j.out
#SBATCH --error={results_dir}/{job_name}_%j.err

echo "Running PEASOUP on {beam}"

start=$(date +%s)
    """.format(
        job_name=job_name,
        results_dir=results_dir,
        partition=params['partition'],
        cpu_time=params['time'],
        cpus=params['cpus'], 
        beam=beam
    )

    with open(tmp_script_path, "w") as f:
        f.write(slurm_header)
        f.write("\n")
        f.write(peasoup_command + "\n")
        f.write('\nend=$(date +%s)')
        f.write('\nruntime=$((end - start))')
        f.write('\necho "Total runtime: ${runtime} seconds"')
        # for command in peasoup_command:
        #     f.write(command + "\n")
        #     f.write('\nend=$(date +%s)')
        #     f.write('\nruntime=$((end - start))')
        f.write('\necho "Total runtime: ${runtime} seconds"')
    os.chmod(tmp_script_path, 0o755)
    print("SLURM search script written to {}".format(tmp_script_path))

def write_slurm_copy_results(script_name, copy_commands, params, beam_dir, results_dir, working_dir):
    """
    Writes the slurm sript to copy data to /tmp
    """
    beam = beam_dir.split('/')[-1]
    job_name = f"CPR{beam}"

    tmp_script_path = os.path.join(working_dir, script_name)
    
    slurm_header = """#!/usr/bin/env bash
#SBATCH --job-name={job_name}
#SBATCH --partition=short.q
#SBATCH --time={cpu_time}
#SBATCH --cpus-per-task={cpus}
#SBATCH --output={results_dir}/{job_name}_%j.out
#SBATCH --error={results_dir}/{job_name}_%j.err
    """.format(job_name=job_name,
            results_dir=results_dir,
            partition=params['partition'],
            cpu_time=params['time'],
            cpus=params['cpus'], 
            )
    with open(tmp_script_path, "w") as f:
        f.write(slurm_header)
        f.write("\n")
        for command in copy_commands:
            f.write(command + "\n")
        f.write("\n")
    os.chmod(tmp_script_path, 0o755)
    print("SLURM copy-data script written to {}".format(tmp_script_path))


def write_submission_script(copydata_script, combine_script, search_script, copyresults_script, data_path, tmp_base, beam_name, slurm_scripts_dir, working_dir):
    """
    Generates a bash script to submit all SLURM job scripts in a directory.
    """
    output_script_name = f'submit_search_{beam_name}_jobs.sh'
    output_script_path = os.path.join(working_dir, output_script_name)
    job_id = "$(awk '{print $4})'" 
    copy_id = f"CP{beam_name}"
    combine_id = "CBN20"
    search_id = "SCH20"
    copyr_id = f"CPR{beam_name}"

    with open(output_script_path, "w") as batch_file:
        batch_file.write("#!/usr/bin/env bash\n\n")
        batch_file.write(f"export SINGULARITY_BINDPATH={tmp_base},{data_path},{slurm_scripts_dir}\n\n")
        batch_file.write(f"echo 'Submitting SLURM search jobs on beam {beam_name}'\n\n")

        batch_file.write(f"{copy_id}=$(sbatch {copydata_script} | awk '{{print $4}}')\n")
        batch_file.write(f"{combine_id}=$(sbatch -d afterok:${{{copy_id}}} {combine_script} | awk '{{print $4}}')\n")
        batch_file.write(f"{search_id}=$(sbatch -d afterok:${{{combine_id}}} {search_script} | awk '{{print $4}}')\n")
        batch_file.write(f"{copyr_id}=$(sbatch -d afterok:${{{search_id}}} {copyresults_script} | awk '{{print $4}}')\n\n")

        batch_file.write("echo 'All jobs submitted.'\n")
        batch_file.write(f'echo "scancel ${{{copy_id}}} ${{{combine_id}}} ${{{search_id}}} ${{{copyr_id}}}" > {os.path.join(working_dir, "scancel_jobs.sh")}\n')

    os.chmod(output_script_path, 0o755)
    print(f"Batch submission script written to {output_script_path}")
    
