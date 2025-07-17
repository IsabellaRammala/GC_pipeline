#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import generatejobs as gen
import glob

# --------------------------------------------------------------------------------
#           READ THE CONFIG FILE & SETUP DIRECTORIES
# --------------------------------------------------------------------------------
params = gen.read_config("config.ini")
directories = gen.setup_directories(params['epoch'], 
									params['user'], 
									params['pipeline_dir'],
									params['singularity_dir']
									)
tmp_base, tmp_data_path, tmp_results_path, tmp_scripts_path, tmp_singularity_path, tmp_pipeline_path, scripts_path = directories

tmp_results_path10 = os.path.join(tmp_results_path, "search10min")
tmp_results_path10 = os.path.join(tmp_results_path, "search20min")
# for dir in directories:
# 	print (dir)
# print (f"ATTTT!!! {glob.glob(os.path.join(tmp_singularity_path, '*'))}")

# --------------------------------------------------------------------------------
#          SLURM COPY DATA TO PROCESSING NODE 
# --------------------------------------------------------------------------------
copy_commands = gen.copy_data(tmp_base, 
								tmp_data_path, 
								tmp_results_path, 
								data_path=os.path.join(params['data_dir'],params['epoch']),
								pipeline_path=params['pipeline_dir'], 
								singularity_path=params['singularity_dir']
								)
# WRITE THE SLURM SCRIPT TO COPY DATA:
gen.write_slurm_copy_data(copy_commands, params, tmp_results_path, scripts_path)
# COPY PRETTY SLOW (TIME for 2 beams real:7m37.617s, user:0m0.021s, sys:7m12.520s)
# ESTIMATING ~4 hours for the 64 beams!!!

# --------------------------------------------------------------------------------
#          SLURM COMBINE FILTERBANKS  TO 2 X 10 MIN FILES & 1 X 20 MIN FILES 
# --------------------------------------------------------------------------------
peasoup_container = os.path.join(tmp_singularity_path, os.path.basename(params['peasoup_singularity']))
dspsr_containers = os.path.join(tmp_singularity_path, os.path.basename(params['dspsr_singularity']))

beams = sorted(glob.glob(os.path.join(tmp_data_path, 'cfbf*')))
for beam in beams: # MIGHT WANT TO COMBINE20, PROCESS, COPY THE RESULTS BACK, THEN DO AGAIN FOR 10 MINUTES CHUNKS
	combine_10_cmd, combine_20_cmd = gen.digifil_commands(beam=beam, 
															singularity_image=params['dspsr_singularity'], 
															working_dir=tmp_base, 
															output_dir=None, 
															bits=8)
	# WRITE THE SLURM SCRIPT TO COMBINE THE DATA:
	# gen.write_slurm_combine10(combine_10_cmd, params, beam_dir=beam, results_dir=tmp_results_path, scripts_path=tmp_scripts_path)
	gen.write_slurm_combine20(combine_20_cmd, params, beam_dir=beam, results_dir=tmp_results_path, scripts_path=tmp_scripts_path)
# --------------------------------------------------------------------------------
#          SLURM PEASOUP SEARCH SCRIPTS 
# --------------------------------------------------------------------------------
	filterbank_files = sorted(glob.glob(os.path.join(beam, "*to*")))
	for filterbank in filterbank_files:
		print (filterbank)
		peasoup_command = gen.peasoup_command(working_dir=tmp_base, 
							singularity_path = peasoup_container, 
							results_dir=tmp_results_path, 
							params=params, 
							filterbank_file=filterbank)
		# print (peasoup_command)

		gen.write_slurm_search_beam(peasoup_command, params, beam_dir=beam, results_dir=tmp_results_path, scripts_path=tmp_scripts_path)
# ----------------------------------------------------------------------
#           WRITE THE SLURM SUBMISSION SCRIPS
# ----------------------------------------------------------------------

# generatejobs.write_batch_submission_script(data_path=params["data_dir"], slurm_scripts_dir=tmp_scripts_path)

