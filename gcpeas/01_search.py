#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import generatejobs
import glob

# ----------------------------------------------------------------------
#           READ THE CONFIG FILE 
# ----------------------------------------------------------------------
params = generatejobs.read_config("config.ini")

# ----------------------------------------------------------------------
#           READ THE DDPLAN FILE
# ----------------------------------------------------------------------
# ddplan_file = "ddplan.txt"
# dm_ranges = []

# with open(ddplan_file, "r") as f:
#     next(f)
#     for line in f:
#         parts = line.split()
#         if len(parts) >= 2:
#             dm_start = float(parts[0])
#             dm_end = float(parts[1])
#             dm_ranges.append((dm_start, dm_end))

# ----------------------------------------------------------------------
#           COPY DATA TO PROCESSING NODE (HEAVY JOB>> NEEDS TO BE A SLURM JOB >> HOW TO GET THE OUTPUTS BACK HERE?? A SETUP SCRIPT WITH PROJECT INFO THAT CAN BE READ HERE?)
# ----------------------------------------------------------------------
make_base_dir_command, copy_data_command, copy_pipeline_command, copy_singularity_command, make_results_dir_command, tmp_base_path, tmp_data_path, tmp_pipeline_path, tmp_singularity_path = generatejobs.generate_copy_data(origin_dir=params["data_dir"],
																					results_dir=params["results_dir"],
																					epoch=params["epoch"], 
																					user_id=params["user"], 
																					pipeline_path=params["pipeline_dir"], 
																					singularity_path=params["peasoup_singularity"], 
																					direction="to_node")

# # --------------------------------------------------------------------
#           GET THE BEAMS & WRITE SEARCH COMMAND
# ----------------------------------------------------------------------
tmp_scripts_path = os.path.join(tmp_base_path, "SCRIPTS")
os.makedirs(tmp_scripts_path)

beam_dirs = sorted(glob.glob(os.path.join(tmp_data_path, "cfbf*")))
for beam_dir in beam_dirs:
	syscall = []
	beam = os.path.basename(beam_dir)
	filterbanks = sorted(glob.glob(os.path.join(beam_dir, "*.fil")))
	for fil_file in filterbanks:
		# for dm_start, dm_end in dm_ranges:
		# 	params["dm_start"] = dm_start
		# 	params["dm_end"] = dm_end
		peasoup_command = generatejobs.generate_peasoup_command(tmp_base_path, tmp_data_path, tmp_pipeline_path, tmp_singularity_path, tmp_results_path, params, fil_file)
		syscall.append(peasoup_command)
	# generatejobs.write_slurm_search_script(beam, syscall, params, tmp_results_path, tmp_scripts_path)
# ----------------------------------------------------------------------
#           WRITE THE SLURM SUBMISSION SCRIPS
# ----------------------------------------------------------------------

# generatejobs.write_batch_submission_script(data_path=params["data_dir"], slurm_scripts_dir=tmp_scripts_path)

