#!/usr/bin/env python3
import os
import glob
import xml.etree.ElementTree as ET

# Speed of light in m/s
LIGHT_SPEED = 2.99792458e8  

# beam directories
beam_pattern = "/hercules/results/isara/20240321_094530/gc00/cfbf*"

def extract_peasoup_cands(xml_file, outfile, LIGHT_SPEED):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    header = root.findall("header_parameters")[0]

    tsamp = header.find("tsamp").text
    nsamples = header.find("nsamples").text

    with open(outfile, "w") as f:
        f.write("#id\tdm\tacc\tf0\tf1\tS/N\n")
        for cand_id, cand in enumerate(root.findall(".//candidate")):
            dm = cand.find("dm").text
            acc = cand.find("acc").text
            period = cand.find("period").text
            f0 = 1 / float(period)
            f1 = float(acc) * f0 / LIGHT_SPEED
            snr = cand.find("snr").text
            f.write(f"{cand_id}\t{dm}\t{acc}\t{f0}\t{f1}\t{snr}\n")

    print(f"Extracted candidates saved to {outfile}")

if __name__ == "__main__":
    # Loop over all matching beam directories
    for beam_dir in sorted(glob.glob(beam_pattern)):
        if not os.path.isdir(beam_dir):
            continue

        xml_files = glob.glob(os.path.join(beam_dir, "overview.xml"))
        if not xml_files:
            print(f"Skipping {beam_dir}: no overview.xml found")
            continue

        xml_file = xml_files[0]

        # Generate candidate file named after the beam
        beam_name = os.path.basename(beam_dir)
        cand_file = os.path.join(beam_dir, f"{beam_name}_pulsarx.cands")

        extract_peasoup_cands(xml_file, cand_file, LIGHT_SPEED)