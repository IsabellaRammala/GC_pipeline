#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import shutil
import configparser  


def preamble():
    print('---------------------+----------------------------------------------------------')
    print('                     |')
    print('                     | ')
    print('      GC PEAS        | v0.0')
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
        "epoch": config.get("DATA", "epoch"),
        "data_dir": config.get("DATA", "data_dir"),
        "readfile": config.get("PRESTO", "readfile"),
        "make_ddplan": config.get("PRESTO", "makeDDplan"),
        "make_birdies": config.get("PRESTO", "makebirdies"), 
        "make_zaplist": config.get("PRESTO", "makezaplist"),
        "presto_singularity": config.get("PRESTO", "presto_singularity"),
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
        "peasoup_singularity": config.get("PEASOUP", "peasoup_singularity"),
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

def generate_copy_data(origin_dir, results_dir, epoch, user_id, pipeline_path, singularity_path, direction="to_node"):
    """
    Copy the data, pipeline, and containmer to (direction="to_node") / from (direction="from_node") processing node )

    returns: tmp_data_path, tmp_pipeline_path, tmp_singularity_path
    """
    tmp_base = os.path.join("/tmp", user_id)
    destination_dir_name = "DATA"
    tmp_data_path = os.path.join(tmp_base, destination_dir_name, epoch)
    tmp_pipeline_path = os.path.join(tmp_base, os.path.basename(pipeline_path))
    tmp_singularity_path = os.path.join(tmp_base, os.path.basename(singularity_path))
    tmp_results_path = os.path.join(tmp_base, ("RESULTS"))
    
    data_path = os.path.join(origin_dir, epoch)
    if direction == "to_node":
        if not os.path.exists(origin_dir):
            raise FileNotFoundError(f"Data directory not found: {origin_dir}")
        
        make_base_dir_command = f"mkdir {tmp_base}"
        if os.path.exists(tmp_data_path):
            print(f"[INFO] Data already exists in /tmp: {tmp_data_path}")
        else:
            print(f"[INFO] Copying data from {data_path} to {tmp_data_path} ...")
            copy_data_command = f"cp -r {data_path} {tmp_data_path}"
            copy_pipeline_command = f"cp -r {pipeline_path} {tmp_pipeline_path}"
            copy_singularity_command = f"cp {singularity_path} {tmp_singularity_path}"
            make_results_dir_command = f"mkdir {tmp_results_path}"
            print(f"[INFO] Copy complete.")
            print(f"{make_base_dir_command}, {make_results_dir_command}, {copy_data_command}, {copy_pipeline_command}, {copy_singularity_command}")
            return make_base_dir_command, copy_data_command, copy_pipeline_command, copy_singularity_command, make_results_dir_command, tmp_base, tmp_data_path, tmp_pipeline_path, tmp_singularity_path

    elif direction == "from_node":
        if not os.path.exists(tmp_data_path):
            raise FileNotFoundError(f"Temporary data directory not found: {tmp_data_path}")

        print(f"[INFO] Restoring data from {tmp_data_path} to {results_dir} ...")
        shutil.copytree(tmp_data_path, results_dir)

        print(f"[INFO] Copy from node complete.")

    else:
        raise ValueError(f"Invalid direction: {direction}. Must be 'to_node' or 'from_node'.")

    # return tmp_base, tmp_data_path, tmp_pipeline_path, tmp_singularity_path, tmp_results_path

def find_filterbank_files(directory):
    """
    Finds all filterbank (.fil) files in the specified directory and returns their paths as a list.
    """
    if not os.path.isdir(directory):
        raise IOError("Directory {} not found.".format(directory))
    
    filterbank_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".fil")]
    
    if not filterbank_files:
        raise IOError("No filterbank files found in directory {}.".format(directory))
    
    return filterbank_files

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

def generate_peasoup_command(working_dir, data_path, pipeline_path, singularity_path, results_dir, params, filterbank_file):
    """
    Generates the PEASOUP command string based on the provided parameters,
    with added Singularity binding for the /tmp working directory.
    """
    command = (
        "singularity exec -B {working_dir} {singularity_path} peasoup "
        "-i {filterbank_file} "
        "-o {output_prefix} "
        "--dm_start {dm_start} --dm_end {dm_end} "
        "--acc_start {acc_start} --acc_end {acc_end} "
        "--nharmonics {nharmonics} --min_snr {min_snr} "
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
    
    return command

def write_slurm_search_script(beam, peasoup_command, copy_commands, params, results_dir, scripts_path):
    """
    Writes the SLURM job script for submitting the PEASOUP jobs.
    """

    script_name = "peasoup_search_{}.sh".format(beam)
    job_name = script_name.split('.')[0]
    tmp_script_path = os.path.join(scripts_path, script_name)
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
        for command in peasoup_command:
            f.write(command + "\n")
            filterbank = os.path.basename(command.split("-i")[1].split()[0])
            # f.write('\necho "PEASOUP job on {filterbank} completed"\n')
            f.write('\nend=$(date +%s)')
            f.write('\nruntime=$((end - start))')
            f.write('\necho "Total runtime: ${runtime} seconds"')
            os.chmod(tmp_script_path, 0o755)
    print("SLURM script written to {}".format(tmp_script_path))

def write_batch_submission_script(data_path, slurm_scripts_dir):
    """
    Generates a bash script to submit all SLURM job scripts in a directory using sbatch.
    """
    #slurm_dir = params["filterbank_dir"]
    #if not os.path.isdir(slurm_dir):
    #    raise IOError("The directory {} does not exist.".format(slurm_dir))
    
    # Find all SLURM scripts (*.sh) in the directory
    slurm_scripts = [f for f in os.listdir(slurm_scripts_dir) if f.endswith(".sh")]
    
    if not slurm_scripts:
       raise IOError("No SLURM job scripts (*.sh) found in the directory {}.".format(slurm_dir))
    
    # Write the sbatch submission script
    for slurm_script in slurm_scripts:
        output_script_name = 'submit_{}_jobs.sh'.format(slurm_script.split('.')[0])
        output_script_path = os.path.join(slurm_scripts_dir, output_script_name)
        with open(output_script_path, "w") as batch_file:
            batch_file.write("#!/usr/bin/env bash\n\n")
            batch_file.write("export SINGULARITY_BINDPATH={},{}\n\n".format(data_path, slurm_scripts_dir))
            batch_file.write("echo 'Submitting all SLURM job scripts in {}'\n\n".format(slurm_scripts_dir))
            batch_file.write("sbatch {}\n\n".format(slurm_script))
            batch_file.write("\necho 'All jobs submitted.'\n")
    
    	# Make the script executable
        os.chmod(output_script_path, 0o755)
        print("Batch submission script written to {}".format(output_script_path))


    
