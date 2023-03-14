# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Mon Jan 23 13:22:30 2023

# @author: htomio
# """

import re
import sys
import numpy as np
import matplotlib.pyplot as plt

from dataclasses import dataclass, field

@dataclass
class MODTRAN_entry:
    H1ALT: float = field(default_factory=float)
    H2ALT: float = field(default_factory=float)
    OBSZEN: float = field(default_factory=float)
    HRANGE: float = field(default_factory=float)
    ECA: float = field(default_factory=float)
    EARTH_RAD: float = field(default_factory=float)
    LENN: int = field(default_factory=int)
    BCKZEN: float = field(default_factory=float)
    HMIN: float = field(default_factory=float)
    
    FREQ: list[float] = field(default_factory=list)
    COMBIN_TRANS: list[float] = field(default_factory=list)


def loadMODOUT2(filename):
    infile = open(filename, 'r')
    lines = infile.readlines()#.strip()
    infile.close()
    
    file_entries = []
    
    if len(lines) < 10:
        print(f'Error reading file {filename}: too few lines!')
        return None


    for i in range(len(lines)):
        
        #get the row of the header that contains the parameters describing the geometry
        #and find the parameters describing the geometry
        floats_ints = re.findall(r'(\d+(?:\.\d+)?)', lines[i])
        if len(floats_ints) == 9:
            md = MODTRAN_entry()
            md.H1ALT = floats_ints[0]
            md.H2ALT = floats_ints[1]
            md.OBSZEN = floats_ints[2]
            md.HRANGE = floats_ints[3]
            md.ECA = floats_ints[4]
            md.EARTH_RAD = floats_ints[5]
            md.LENN = floats_ints[6]
            md.BCKZEN = floats_ints[7]
            md.HMIN = floats_ints[8] #not actually sure on this last one 
            #TODO - rerun MODTRAN with a nonzero HMIN
            #TODO - figure out what to do for the following case
            #   0.00000 100.00000  90.000001184.30554  10.53352  6378.10000  0       99.99173   0.00000
            
            trans_start = i + 7
            trans_vals = re.findall(r'(\d+(?:\.\d+)?)', lines[trans_start])
            if len(trans_vals) != 40:
                print(f'Error reading file {filename}: expected at least 1 frequency')
                return None
            
            while(len(trans_vals) == 40):
                md.FREQ.append(trans_vals[0])
                md.COMBIN_TRANS.append(trans_vals[1])
                #TODO: add the rest of the transmissivities if desired
                
                trans_start = trans_start + 1
                trans_vals = re.findall(r'(\d+(?:\.\d+)?)', lines[trans_start])
            
            file_entries.append(md)
            
    return file_entries
   

if __name__ == "__main__":
    modtran_data = loadMODOUT2('/Users/htomio/workspace/CLICK/Optical-Link-Budget/MODTRAN_outputs/MODOUT2')

    dist = []
    trans = []

    for i in modtran_data:
        dist.append(float(i.HRANGE))
        trans.append(float(i.COMBIN_TRANS[3]))
    
    plt.figure()
    plt.plot(dist[:88], trans[:88])
    plt.xlabel('Range through atmosphere (km)')
    plt.ylabel('Transmissivity')