#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de

import os
import generatejobs as gen
import glob

gen.preamble()
# --------------------------------------------------------------------------------
#           READ THE CONFIG FILE & SETUP DIRECTORIES
# --------------------------------------------------------------------------------
params = gen.read_config("config.ini")
data_path = os.path.join(params['data_dir'],params['epoch'])
CWD = os.getcwd()
slurm_dir = os.path.join(CWD, "SCRIPTS")

directories = gen.setup_directories(params['epoch'], 
									params['user'], 
									params['pipeline_dir'],
									params['singularity_dir']
									)
tmp_base, tmp_data_path, tmp_results_path, tmp_scripts_path, tmp_singularity_path, tmp_pipeline_path, scripts_path = directories
tmp_results_path10 = os.path.join(tmp_results_path, "search10min")
tmp_results_path10 = os.path.join(tmp_results_path, "search20min")
peasoup_container = os.path.join(tmp_singularity_path, os.path.basename(params['peasoup_singularity']))
dspsr_containers = os.path.join(tmp_singularity_path, os.path.basename(params['dspsr_singularity']))

# --------------------------------------------------------------------------------
#           RUNNING THE SEARCH PER BEAM
# --------------------------------------------------------------------------------

# beams = sorted(glob.glob(os.path.join(tmp_data_path, 'cfbf*')))
beams = sorted(glob.glob(os.path.join(data_path, 'cfbf*')))
for beam in beams: # MIGHT WANT TO COMBINE20, PROCESS, COPY THE RESULTS BACK, THEN DO AGAIN FOR 10 MINUTES CHUNKS
	beam_id = os.path.basename(beam)
# --------------------------------------------------------------------------------
#          SLURM COPY DATA TO PROCESSING NODE 
# --------------------------------------------------------------------------------
	cp_script_name = f"01_copy_{beam_id}.sh"
	copy_commands = gen.copy_data(tmp_base, 
								tmp_data_path, 
								tmp_results_path, 
								data_path=os.path.join(params['data_dir'],params['epoch']),
								epoch=params['epoch'],
								pipeline_path=params['pipeline_dir'], 
								singularity_path=params['singularity_dir']
								)
	gen.write_slurm_copy_data(cp_script_name, copy_commands, params, beam, tmp_results_path, tmp_scripts_path, slurm_dir)
# --------------------------------------------------------------------------------
#          SLURM COMBINE FILTERBANKS  TO 2 X 10 MIN FILES & 1 X 20 MIN FILES 
# --------------------------------------------------------------------------------
	digifil_script_name = f"02_combine20_{beam_id}.sh"
	combine_10_cmd, combine_20_cmd = gen.digifil_commands(beam=beam, 
															singularity_image=params['dspsr_singularity'], 
															working_dir=tmp_base, 
															output_dir=None, 
															bits=8)
	# WRITE THE SLURM SCRIPT TO COMBINE THE DATA:
	# gen.write_slurm_combine10(combine_10_cmd, params, beam_dir=beam, results_dir=tmp_results_path, scripts_path=tmp_scripts_path)
	gen.write_slurm_combine20(digifil_script_name, combine_20_cmd, params, beam_dir=beam, results_dir=tmp_results_path, scripts_path=tmp_scripts_path, working_dir=slurm_dir)

# --------------------------------------------------------------------------------
#          SLURM PEASOUP SEARCH SCRIPTS 
# --------------------------------------------------------------------------------
	peasoup_script_name = f"03_peasoup_search_{beam_id}.sh"
	filterbank = combine_20_cmd.split(' ')[10] # NEED A BETTER WAY TO DO THIS 

	peasoup_command = gen.peasoup_command(working_dir=tmp_base, 
						singularity_path = peasoup_container, 
						results_dir=os.path.join(tmp_results_path, beam),
						params=params, 
						filterbank_file=filterbank)
	gen.write_slurm_search_beam(peasoup_script_name, peasoup_command, params, beam_dir=beam, results_dir=tmp_results_path, scripts_path=tmp_scripts_path, working_dir=slurm_dir)


# ----------------------------------------------------------------------
#           COPY THE RESULTS BACK TO /hercules/results
# ----------------------------------------------------------------------
	cpr_script_name = f"04_copy_results_{beam_id}.sh"
	copy_results_command = gen.copy_results(tmp_results_dir=os.path.join(tmp_results_path, beam),
											 results_dir=os.path.join(params['results_dir'], params['epoch']))
	gen.write_slurm_copy_results(cpr_script_name, 
								copy_results_command, 
								params, 
								beam, 
								tmp_results_path, 
								slurm_dir)

# ----------------------------------------------------------------------
#           WRITE THE SLURM SUBMISSION SCRIPS
# ----------------------------------------------------------------------
	combine_slurm_script = os.path.join(scripts_path, digifil_script_name)
	search_slurm_script = os.path.join(scripts_path, peasoup_script_name)
	copydata_slurm_script = os.path.join(scripts_path, cp_script_name)
	copyresults_script = os.path.join(scripts_path, cpr_script_name)
	gen.write_submission_script(copydata_script=copydata_slurm_script,
								combine_script=combine_slurm_script, 
								search_script=search_slurm_script,
								copyresults_script=copyresults_script,
								data_path=data_path,
								tmp_base=tmp_base, 
								beam_name=beam_id, 
								slurm_scripts_dir=tmp_scripts_path, 
								working_dir=slurm_dir)

# FROM THE MMGPS Meeting on 18 July 2025
# PULSARX is currently doing better on RFI excercision on birdies and/or channel masklist 
# GC DATA on Hercules is on a staging area (slow network - only 10 jobs max)
# Recommendation - copy data from mandap to hercules/scratch
# filtool jobs (only 10 jobs at a time) - that saves the data to /hercules/scratch
# then copy those to tmp ()