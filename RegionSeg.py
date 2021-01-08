"""Crop data for the Region of Interest(ROI)

This script takes the raw data from the source directory 
and crops the region specific data specified by min and max 
coordinates specified in the configuration file

This script uses files present in Utils directory 
and assumes pandas and numpy are installed in the system

This file 
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


def seg_reg_data():
    """
    Crops the raw data for the desired ROI

    Reads the configuration file for all the variables
    Loads file for zone 10 and 11
    Crops the data specific to the desired ROI
    Stores to the destination location

    Issue
    ---------
        may run out of memory due to large size of the raw data
    """

    aISDM = AISDataManager()
    config = configparser.ConfigParser()
    #DefaultConfig.INI stores all the run time constants
    config.read('DefaultConfig.INI')

    lonMin = (float)(config['REGION']['LON_MIN'])
    lonMax = (float)(config['REGION']['LON_MAX'])

    latMin = (float)(config['REGION']['LAT_MIN'])
    latMax = (float)(config['REGION']['LAT_MAX'])

    print("(lonMin , latMin) = (%f,%f)"%(lonMin,latMin))
    print("(lonMax , latMax) = (%f,%f)"%(lonMax,latMax))

    srcAffix = (config['REGION_SEG']['SOURCE_LOC_AFFIX'])
    destAffix = (config['REGION_SEG']['DEST_LOC_AFFIX'])
    fileSuffix = (config['REGION_SEG']['FILE_SUFFIX'])
    print(srcAffix)
    print(destAffix)
    print(fileSuffix)

    #data is available on yearly bases
    #year to consider for the data pre-processing
    yearsToConsider = [int(year) for year in (config['REGION_SEG']['YEARS_TO_CONSIDER'].split(','))]

    print("Starting Cropping...")
    DEST_DIR = destAffix + sU.convert_boundary_to_string(lonMin \
                                        , lonMax \
                                        , latMin \
                                        , latMax \
                                        )

    #generate list of filenames touple
    #(ZONE11,ZONE10,DEST)
    fileNameList = []
    for year in yearsToConsider:
        for monthNum in range(1,13):
            fileNames = (srcAffix+"20"+"%02d"%(year)+"/AIS_20"+"%02d"%(year)+"_"+"%02d"%(monthNum)+"_11.csv", \
                    srcAffix+"20"+"%02d"%(year)+"/AIS_20"+"%02d"%(year)+"_"+"%02d"%(monthNum)+"_10.csv", \
                    DEST_DIR+"/"+"%02d"%(year)+"_"+"%02d"%(monthNum)+fileSuffix+".csv")
            
            fileNameList.append(fileNames)
    # for fileName in fileNameList:
    #     print(fileName)

    SRC_1_INDEX = 0
    SRC_2_INDEX = 1
    DEST_INDEX = 2

    for file in fileNameList:
        #load from source 1 i.e. zone 11 raw data
        src1, _ = aISDM.load_data_from_csv(file[SRC_1_INDEX])
        filteredDF1 = aISDM.filter_based_on_lon_lat(src1,lonMin, lonMax, latMin, latMax)
        print(src1.shape)
        print(filteredDF1.shape)

        #clear memory for the next file
        src1 = pd.DataFrame()
        gc.collect()

        #load from source 2 i.e. zone 10 raw data
        src2, _ = aISDM.load_data_from_csv(file[SRC_2_INDEX])
        filteredDF2 = aISDM.filter_based_on_lon_lat(src2,lonMin, lonMax, latMin, latMax)
        print(src2.shape)
        print(filteredDF2.shape)

        #clear memory for the next file
        src2 = pd.DataFrame()
        gc.collect()

        #combine cropped files
        #filter for the desired region
        combinedDF = filteredDF1.append(filteredDF2, ignore_index = True)
        print(combinedDF.shape)
        #save data to destination
        aISDM.save_data_to_csv(combinedDF,file[DEST_INDEX])
        print("%s generated"%(file[DEST_INDEX]))

        #clear memory for the next run
        filteredDF1 = pd.DataFrame()
        filteredDF2 = pd.DataFrame()
        combinedDF = pd.DataFrame()
        gc.collect()

if __name__ == '__main__':
    seg_reg_data()