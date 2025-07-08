#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import ConfigParser  

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
    
    config = ConfigParser.ConfigParser()
    config.read(config_file)

    params = {
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

def presto_readfile(params, filterbank_file):
    """
    Use presto to read the filterbank file and save the header info into a file
    """
    current_dir = os.getcwd()

    command = (
        "singularity exec -B {current_dir},{results_dir},{scratch_dir},{filterbank_dir} {singularity_image} readfile {filterbank_file}"        
    ).format(
        current_dir=current_dir,
        results_dir=params[""]
    )

def generate_peasoup_command(params, filterbank_file):
    """
    Generates the PEASOUP command string based on the provided parameters,
    with added Singularity binding for the working directory.
    """
    current_dir = os.getcwd()

    command = (
        "singularity exec -B {current_dir},{results_dir},{scratch_dir},{filterbank_dir} {singularity_image} peasoup "
        "-i {filterbank_file} "
        "-o {output_prefix} "
        "--dm_start {dm_start} --dm_end {dm_end} "
        "--acc_start {acc_start} --acc_end {acc_end} "
        "--nharmonics {nharmonics} --min_snr {min_snr} "
    ).format(
        current_dir=current_dir,
        filterbank_dir=params["filterbank_dir"],
        results_dir=params["results_dir"], 
        scratch_dir=params["scratch_dir"],
        singularity_image=params["singularity_image"],
        filterbank_file=filterbank_file,
        output_prefix=params["output_prefix"],
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

def write_slurm_script(params, peasoup_command, filterbank_file):
    """
    Writes the SLURM job script for submitting the PEASOUP job.
    """
    job_name = "{}_{}".format(params["job_name"], os.path.basename(filterbank_file).split(".")[0])
    slurm_script = """#!/usr/bin/env bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --time={time}
#SBATCH --cpus-per-task={cpus}
#SBATCH --output={output_dir}{job_name}_%j.out
#SBATCH --error={output_dir}{job_name}_%j.err

echo "Running PEASOUP on {filterbank_file}"
{command}
echo "PEASOUP job completed"
""".format(
        job_name=job_name,
        partition=params["partition"],
        time=params["time"],
        cpus=params["cpus"],
        output_dir=params["output_dir"],
        filterbank_file=filterbank_file,
        command=peasoup_command
    )

    script_name = "{}.sh".format(job_name)
    with open(script_name, "w") as f:
        f.write(slurm_script)
    os.system("chmod 777 {}".format(script_name))
    print("SLURM script written to {}".format(script_name))

def write_batch_submission_script(params, output_script_name="submit_jobs.sh"):
    """
    Generates a bash script to submit all SLURM job scripts in a directory using sbatch.

    Args:
        slurm_dir (str): Path to the directory containing SLURM scripts.
        out_dir (str): Path to the results output dir
        output_script_name (str): Name of the batch submission script to be created.
    """
    slurm_dir = params["filterbank_dir"]
    if not os.path.isdir(slurm_dir):
        raise IOError("The directory {} does not exist.".format(slurm_dir))
    
    # Find all SLURM scripts (*.sh) in the directory
    slurm_scripts = [f for f in os.listdir(slurm_dir) if f.endswith(".sh")]
    
    if not slurm_scripts:
        raise IOError("No SLURM job scripts (*.sh) found in the directory {}.".format(slurm_dir))
    
    # Write the sbatch submission script
    output_script_path = os.path.join(slurm_dir, output_script_name)
    with open(output_script_path, "w") as batch_file:
        batch_file.write("#!/usr/bin/env bash\n\n")
        batch_file.write("export SINGULARITY_BINDPATH=$PWD,{}\n\n".format(slurm_dir))
        batch_file.write("echo 'Submitting all SLURM job scripts in {}'\n\n".format(slurm_dir))
        
        for script in slurm_scripts:
            batch_file.write("sbatch {}/{}\n".format(slurm_dir, script))
        
        batch_file.write("\necho 'All jobs submitted.'\n")
    
    # Make the script executable
    os.chmod(output_script_path, 0o755)
    print("Batch submission script written to {}".format(output_script_path))

# Example Usage
if __name__ == "__main__":
    preamble()
    config_file = "config.ini"
    params = read_config(config_file)
    
    # Find all filterbank files in the specified directory
    filterbank_files = find_filterbank_files(params["filterbank_dir"])
    
    # Generate a SLURM script for each filterbank file
    for filterbank_file in filterbank_files:
        peasoup_command = generate_peasoup_command(params, filterbank_file)
        write_slurm_script(params, peasoup_command, filterbank_file)

    # Generate a batch submission script
    write_batch_submission_script(params)

    