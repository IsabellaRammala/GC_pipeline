#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import sys

peasoup_cands = "/hercules/results/isara/test_peasoup/peasoup_test_output/obs_fil/overview.xml"
outfile = peasoup_cands.replace("overview.xml","candidates_for_pulsarx.cands")

def extract_cands(xml, outfile):
    tree = ET.parse(xml)
    root = tree.getroot()

    candidates = []
    for cand in root.findall(".//candidate"):
        # period = cand.find("period")  
        cand_id = cand.find("candidate id")
        dm = cand.find("dm")          
        acc = cand.find("acc")  
        # f0 = cand.find("F0")
        # f1 = cand.find("F1")
        snr = cand.find("snr")

    
        if period is not None and dm is not None and acc is not None:
            candidates.append((dm.text, acc.text, snr.text))

    with open(outfile, "w") as f:
        f.write("#id  dm  acc  S/N\n")
        for i, cand in enumerate(candidates):
            f.write(f"{i} {' '.join(map(str, cand))}\n")
    print("Extracted candidates saved to candidates_for_pulsarx.txt")

if __name__ == "__main__":
    extract_cands(sys.argv[1], sys.argv[2])
