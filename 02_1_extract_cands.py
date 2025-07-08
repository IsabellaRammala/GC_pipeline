#!/usr/bin/env python3
import xml.etree.ElementTree as ET

peasoup_cands = "/hercules/results/isara/test_peasoup/peasoup_test_output/obs_fil/overview.xml"
outfile = peasoup_cands.replace("overview.xml","candidates_for_pulsarx.cands")

import xml.etree.ElementTree as ET

tree = ET.parse(peasoup_cands)
root = tree.getroot()

candidates = []
for cand in root.findall(".//candidate"):
    # period = cand.find("period")  
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