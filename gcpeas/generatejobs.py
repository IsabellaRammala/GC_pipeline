#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import shutil
import configparser  
import glob
import subprocess



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
        "pulsarx_singularity": config.get("PULSARX", "pulsarx_singularity"),
        "filterbank_dir": config.get("PEASOUP", "filterbank_dir"),
        "results_dir": config.get("PEASOUP", "results_dir"),
        "scratch_dir": config.get("PEASOUP", "scratch_dir"),
        "output_prefix": config.get("PEASOUP", "output_prefix"),
        "dm_start": config.getfloat("PEASOUP", "dm_start"),
        "dm_end": config.getfloat("PEASOUP", "dm_end"),
        "acc_start": config.getfloat("PEASOUP", "acc_start"),
        "acc_end": config.getfloat("PEASOUP", "acc_end"),
        "nharmonics": config.getint("PEASOUP", "nharmonics"),
        "fft_size": config.getfloat("PEASOUP", "fft_size"),
        "limit": config.getfloat("PEASOUP", "limit"),
        "min_snr": config.getfloat("PEASOUP", "min_snr"),
        "ram_limit_gb": config.getfloat("PEASOUP", "ram_limit_gb"),
        "parallel": config.getboolean("PEASOUP", "parallel"),
        "output_dir": config.get("PEASOUP", "output_dir"),
        "job_name": config.get("PEASOUP", "job_name"),
        "partition": config.get("PEASOUP", "partition"),
        "time": config.get("PEASOUP", "time"),
        "cpus": config.getint("PEASOUP", "cpus"),
        "threads":config.get("PEASOUP", "threads"),
        "partition": config.get("SLURM", "partition"),
        "nodes": config.getint("SLURM", "nodes"),
        "ntasks": config.getint("SLURM", "ntasks"),
        "gres": config.get("SLURM", "gres"),
        "cpus-per-task": config.getint("SLURM", "cpus-per-task"),
        "mem": config.get("SLURM", "mem"),
        "time": config.get("SLURM", "time")
        }
    return params



def setup_directories(input_dir, output_dir, verbose=True):
    """
    Sets up and creates working directories on local and processing nodes.
    """
    # scripts_path = os.path.join(pipeline_path, "SCRIPTS")
    # tmp_base = os.path.join("/tmp", user_id)
    # destination_dir_name = "DATA"
    
    # tmp_data_path = os.path.join(tmp_base, destination_dir_name, epoch)
    # tmp_pipeline_path = os.path.join(tmp_base, os.path.basename(pipeline_path))
    # tmp_singularity_path = os.path.join(tmp_base, os.path.basename(singularity_path))
    # tmp_scripts_path = os.path.join(tmp_pipeline_path, os.path.basename(scripts_path))
    # tmp_results_path = os.path.join(tmp_base, "RESULTS")

    # os.makedirs(tmp_data_path, exist_ok=True)
    # os.makedirs(tmp_pipeline_path, exist_ok=True)
    # os.makedirs(tmp_singularity_path, exist_ok=True)
    # os.makedirs(tmp_scripts_path, exist_ok=True)
    # os.makedirs(tmp_results_path, exist_ok=True)

    # return tmp_base, tmp_data_path, tmp_results_path, tmp_scripts_path, tmp_singularity_path, tmp_pipeline_path, scripts_path
    
    # SETUP LOCAL DIRECTORIES
    if verbose:
        print ("------------------------------------------------------------")
        print ("                SETTING  UP DIRECTORIES                     ")
        print ("------------------------------------------------------------")

    INPUT_DIR = os.path.abspath(input_dir)
    OUTPUT_DIR = os.path.abspath(output_dir)

    BEAM = os.path.basename(INPUT_DIR)
    EPOCH = os.path.basename(os.path.dirname(INPUT_DIR))  
    POINTING = os.path.basename(os.path.dirname(os.path.dirname(INPUT_DIR)))

    RESULTS_DIR = os.path.join(OUTPUT_DIR, EPOCH, POINTING, BEAM)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # MIRROR THE PATHS ONTO THE PROCESSING NODE
    BASE_TMPDIR = os.environ.get("TMPDIR", "/tmp")
    TMP_DIR = os.path.join(BASE_TMPDIR, EPOCH)
    os.makedirs(TMP_DIR, exist_ok=True)

    # # CREATE CONTAINERS AND PIPELINE DIRECTORIES ONTO THE NODE
    # PIPELINE_DIR = os.path.join(BASE_TMPDIR, "PIPELINES")
    # CONTAINERS_DIR = os.path.join(BASE_TMPDIR, "CONTAINERS")
    # os.makedirs(PIPELINE_DIR, exist_ok=True)
    # os.makedirs(CONTAINERS_DIR, exist_ok=True)

    if verbose:
        print (f"Input directory: {INPUT_DIR}")
        print (f"Data will be processed on {TMP_DIR}")
        print (f"Results will be moved to {OUTPUT_DIR}")
        # print (f"Pipeline on NODE: {PIPELINE_DIR}")
        # print (f"Containers on NODE: {CONTAINERS_DIR}")

    return INPUT_DIR, RESULTS_DIR, OUTPUT_DIR, TMP_DIR, POINTING, BEAM, 

def copy_data_to_node(input_dir, tmp_dir, beam, pipeline, containers, verbose):
    # COPY THE DATA, pipelines, and containers TO THE PROCESSING NODE
    if verbose:
        print ("------------------------------------------------------------")
        print ("                  COPY DATA TO PCROCESSING NODE             ")
        print ("------------------------------------------------------------")
    tmp_beam_dir = os.path.join(tmp_dir, beam)
    tmp_containers_dir = os.path.join(tmp_dir, "CONTAINERS")
    tmp_pipelines_dir = os.path.join(tmp_dir, "PIPELINES")
    tmp_results_dir = os.path.join(tmp_dir, "RESULTS")

    os.makedirs(tmp_containers_dir, exist_ok=True)
    os.makedirs(tmp_results_dir, exist_ok=True)
    # os.makedirs(tmp_pipelines_dir, exist_ok=True)
    
    if verbose:
        print (f"Copying Singularity containers {containers} to {tmp_containers_dir}...")
    for container in containers:
        shutil.copy2(container, tmp_containers_dir)

    if verbose:
        print (f"Copying Pipeline {pipeline} to {tmp_pipelines_dir}...")
    shutil.copytree(pipeline, tmp_pipelines_dir)
    if verbose:
        print (f"Copying beam from {input_dir} to {tmp_beam_dir}...")

    if not os.path.exists(tmp_beam_dir):
        shutil.copytree(input_dir, tmp_beam_dir)
    else:
        print(f"{tmp_beam_dir} already exists, skipping copy")

    if os.path.isdir(tmp_beam_dir) and os.listdir(tmp_beam_dir):
        print(f"Files successfully copied to {tmp_beam_dir}:")
        for f in os.listdir(tmp_beam_dir):
            print("  ", f)
    return tmp_beam_dir, tmp_containers_dir, tmp_pipelines_dir, tmp_results_dir

def run_filtool(input_dir, output_dir, pulsarx_sif, filplan):
    fil_files = sorted(glob.glob(os.path.join(input_dir, "*.fil")))
    print ("------------------------------------------------------------")
    print ("                   RUNNING FILTOOL                          ")
    print ("------------------------------------------------------------")
    cmd = [
        "singularity", "exec", 
        #"-B", f"{os.getcwd()},/mandap,/hercules/results/isara,/u/isara",
        pulsarx_sif,
        "filtool", "-v",
        "--filplan", filplan,
        "-o", output_dir,
        "-f"
    ] + fil_files  
    print(f"[INFO] Command: {' '.join(cmd)}")
    try:
        print (fil_files)
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] filtool failed: {e}")


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

def run_peasoup(peasoup_sif, results_dir, params, filterbank_file):
    """
    Generates the PEASOUP command string based on the provided parameters,
    """
    command = [
        "singularity", "exec", "--nv",
        peasoup_sif,
        "peasoup",
        "-i", filterbank_file,
        "-o", results_dir,
        "--dm_start", str(params["dm_start"]),
        "--dm_end", str(params["dm_end"]),
        "--acc_start", str(params["acc_start"]),
        "--acc_end", str(params["acc_end"]),
        "--nharmonics", str(params["nharmonics"]),
        "--min_snr", str(params["min_snr"]),
        "--ram_limit_gb", str(params["ram_limit_gb"]),
        "--fft_size", str(int(params["fft_size"])),
        "--limit", str(int(params["limit"])),
        "-t", str(int(params["threads"])), 
        "-v"
    ]

    try:
        print(f"[INFO] Command: {' '.join(command)}")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Peasoup failed: {e}")
    

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

# def copy_data(tmp_base, tmp_data_path, tmp_results_path, data_path, epoch, pipeline_path, singularity_path):
#     """
#     Copy the data, pipeline, and container to the processing node using shutil.
#     Assumes necessary directories except tmp_data_path are already created.
#     """
#     if not os.path.exists(data_path):
#         raise FileNotFoundError(f"Data directory not found: {data_path}")
    
#     if os.path.exists(tmp_data_path):
#         print(f"[INFO] Data already exists in /tmp: {tmp_data_path}")
#         return []  

#     # COPY DATA
#     shutil.copytree(data_path, tmp_data_path)

    # # COPY PIPELINE
    # pipeline_dest = os.path.join(tmp_base, os.path.basename(pipeline_path))
    # if not os.path.exists(pipeline_dest):
    #     shutil.copytree(pipeline_path, pipeline_dest)

    # # COPY CONTAINERS
    # singularity_dest = os.path.join(tmp_base, os.path.basename(singularity_path))
    # if os.path.isdir(singularity_path):
    #     if not os.path.exists(singularity_dest):
    #         shutil.copytree(singularity_path, singularity_dest)
    # else:
    #     if not os.path.exists(singularity_dest):
    #         shutil.copy2(singularity_path, singularity_dest)


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
    
