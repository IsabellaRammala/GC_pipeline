#!/usr/bin/env python
#irammala@mpif-bonn.mpg.de
import os
import generatejobs as gen
import argparse
import shutil



def parse_user_options():
    """
    Parse command-line arguments and return them as a Namespace object.
    """
    parser = argparse.ArgumentParser(description="Cleans the Filterbank file using filtool, runs peasoup to search for candidates, and fold the candidates")
    parser.add_argument("beam_path", help="Path to the beam with filterbank files")
    
    # Optional arguments
    parser.add_argument("-o", "--output_path", default="/hercules/results/isara/RESULTS", help="Path to the results directory (default: /hercules/results/isara/RESULTS")
    parser.add_argument("-c", "--config", default="/u/isara/SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/config.ini", help="Path to the config file (default: SOFTWARES/gcpeas/gcpeas_nongit/gcpeas/config.ini)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    # parser.add_argument("-n", "--num_iterations", type=int, default=10, help="Number of iterations (default: 10)")
    
    args = parser.parse_args()
    return args


def main(beam_path, results_path, config_path, verbose):
    gen.preamble()
    # --------------------------------------------------------------------------------
    #           READ CONFIG FILE
    # --------------------------------------------------------------------------------
    params = gen.read_config(config_path)

    # --------------------------------------------------------------------------------
    #           SETUP DIRECTORIES
    # --------------------------------------------------------------------------------
    INPUT_DIR, RESULTS_DIR, OUTPUT_DIR, TMP_DIR, POINTING, BEAM = gen.setup_directories(input_dir=beam_path, output_dir=results_path, verbose=verbose)

    # --------------------------------------------------------------------------------
    #           COPY DATA TO THE PROCESSING NODE
    # --------------------------------------------------------------------------------
    PULSARX = params["pulsarx_singularity"]
    PEASOUP = params["peasoup_singularity"]
    CONTAINERS_ORIGIN = list([PULSARX, PEASOUP])
    PIPELINE_ORIGIN = params["pipeline_dir"]
    TMP_BEAM_DIR, TMP_CONTAINER_DIR, TMP_PIPELINE_DIR, TMP_RESULTS_DIR = gen.copy_data_to_node(INPUT_DIR, TMP_DIR, BEAM, PIPELINE_ORIGIN, CONTAINERS_ORIGIN, verbose=verbose)
    
    # --------------------------------------------------------------------------------
    #           CLEAN AND COMBINE THE FILTERBANKS
    # --------------------------------------------------------------------------------
    print (TMP_BEAM_DIR, TMP_CONTAINER_DIR, TMP_PIPELINE_DIR, TMP_RESULTS_DIR, RESULTS_DIR)
    filplan = os.path.join(TMP_PIPELINE_DIR, "filplan.json")
    pulsarx_path, peasoup_path = [os.path.join(TMP_CONTAINER_DIR, os.path.basename(sif)) for sif in CONTAINERS_ORIGIN]
    
    beam_id = os.path.basename(TMP_BEAM_DIR)
    cleaned_beam_prefix = os.path.join(TMP_RESULTS_DIR, beam_id)
    gen.run_filtool(TMP_BEAM_DIR, cleaned_beam_prefix, pulsarx_path, filplan)

    # --------------------------------------------------------------------------------
    #           SEARCH THE CLEANED FILTERBANK FILE 
    # --------------------------------------------------------------------------------
    # xml_prefix = f"{beam_id}_20min_search"
    xml_path = os.path.join(TMP_RESULTS_DIR)#, xml_prefix)
    cleaned_beam = f"{cleaned_beam_prefix}_01.fil"
    gen.run_peasoup(peasoup_path, xml_path, params, cleaned_beam)

    print("--------------------------------------------------------------------------------")
    print("           MOVE THE RESULTS TO LOCAL SCRATCH                                    ")
    print("--------------------------------------------------------------------------------")
    # Deleting the cleaned beam to save space
    print(f"Deleting temporary beam directory: {cleaned_beam}")
    shutil.rmtree(cleaned_beam)

    print(f"Moving {TMP_RESULTS_DIR} to {RESULTS_DIR}") 
    if os.path.exists(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR) 
    shutil.copytree(TMP_RESULTS_DIR, RESULTS_DIR)  

    print("--------------------------------------------------------------------------------")
    print("                 CLEAR UP THE PROCESSING NODE                                   ")
    print("--------------------------------------------------------------------------------")
    shutil.rmtree(TMP_DIR)



if __name__ == "__main__":
    opts = parse_user_options()
    if opts.verbose:
        verbose=True
    else:
        verbose=False

    main(beam_path=opts.beam_path, 
        results_path=opts.output_path, 
        config_path=opts.config,
        verbose=verbose)    