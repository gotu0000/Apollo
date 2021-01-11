"""Generates list of vessels for the Region of Interest(ROI)

This script takes the segregated data and gets unique entries
of MMSI to make the final list of vessels for a given region

This script uses files present in Utils directory 
and assumes pandas and numpy are installed in the system
"""
import sys
import os
import numpy as np
import pandas as pd
import gc

import configparser
sys.path.insert(0, 'Utils/')

from AISDataManager import AISDataManager
import SimpleUtils as sU
import Constants as c

def gen_vessel_list():
    """
    Generates list of vessel names for the years specified

    Loads segrgated data files
    Checks for unique MMSI 
    Stores them into the file specified by DEST_FILE_NAME
    """
    aISDM = AISDataManager()
    config = configparser.ConfigParser()
    #DefaultConfig.INI stores all the run time constants
    config.read('DefaultConfig.INI')

    SOURCE_DIR_NAME = (config['GEN_VESSEL_LIST_TXT']['SRC_DIR_NAME'])
    srcAffix = (config['GEN_VESSEL_LIST_TXT']['SOURCE_LOC_AFFIX'])
    fileSuffix = (config['GEN_VESSEL_LIST_TXT']['FILE_SUFFIX'])
    destFileName = (config['GEN_VESSEL_LIST_TXT']['DEST_FILE_NAME'])
    print(srcAffix + SOURCE_DIR_NAME + fileSuffix)
    print(destFileName)

    yearsToConsider = [int(year) for year in (config['GEN_VESSEL_LIST_TXT']['YEARS_TO_CONSIDER'].split(','))]

    #List of file names to load the data from
    fileNameList = []
    for year in yearsToConsider:
        for monthNum in range(1,13):
            fileName = srcAffix + SOURCE_DIR_NAME + "/" + "%02d"%(year)+"_"+"%02d"%(monthNum)+fileSuffix+".csv"
            fileNameList.append(fileName)

    # print(fileNameList)
    #generate list of unique entries for entire regeion
    vesselListSets = []
    for i in fileNameList:
        lAPData,retVal = aISDM.load_data_from_csv(i)
        if(retVal == c.errNO['SUCCESS']):
            vesselListSets.append(aISDM.get_list_of_unique_mmsi(lAPData))
        else:
            print("Unable to load")
            break;

    #make empty set
    unionOfVesselList = set()
    #get unioun of all the sets
    for i in vesselListSets:
        unionOfVesselList = unionOfVesselList.union(set(i))

    #convert set to list
    unionOfVesselList = list(unionOfVesselList)

    #sort them
    sortedMMSI = unionOfVesselList.copy()
    sortedMMSI.sort()

    #save to file 
    with open(destFileName, 'w') as f:
        for item in sortedMMSI:
            f.write("%s\n" % item)

if __name__ == '__main__':
    gen_vessel_list()