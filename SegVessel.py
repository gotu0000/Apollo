"""Segregates vessel data based on its MMSI

This script takes the segregated data and filters data 
for the specific MMSI

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
import TimeUtils as timeUtils

from joblib import Parallel, delayed
import multiprocessing

aISDM = AISDataManager()

def segregate_vessel_data_helper(data, vesselName, dirToStore):
    """
    Takes data frame

    filters for specifc MMSI
    stores the filtered dataframe

    Parameters
    ---------
    data : pandas dataframe
        monthly DF
    vesselName : str
        name of the vessel whose data needs to be filtered
    dirToStore : str
        destination directory to store the extracted file
    """

    #filter based on MMSI
    vesselData = aISDM.filter_based_on_mmsi(data, int(vesselName))
    #get the name of file to save
    fileName = dirToStore + vesselName + '.csv'
    aISDM.save_data_to_csv(vesselData,fileName)

    #sort the data with respect to time
    aISDM.formate_time(vesselData,'DateTime',inPlace = True)
    sortedVD = vesselData.sort_values(by='DateTime')

    fileName = dirToStore + vesselName + '_Sorted.csv'
    # print(fileName)
    #save the sorted data
    aISDM.save_data_to_csv(sortedVD,fileName)

def seg_vessel_data_based_on_mmsi():
    """
    Generates segregated data of the vessel
    based on its MMSI

    Loads segregated data files
    filters for specific MMSI
    stores into specific location identified by year and month
    """

    numCores = multiprocessing.cpu_count()
    print(numCores)

    config = configparser.ConfigParser()
    #DefaultConfig.INI stores all the run time constants
    config.read('DefaultConfig.INI')

    SOURCE_DIR_NAME = (config['SEG_VESSEL']['SRC_DIR_NAME'])
    srcAffix = (config['SEG_VESSEL']['SOURCE_LOC_AFFIX'])
    mMSIFile = (config['SEG_VESSEL']['MMSI_FILE'])

    print(srcAffix+SOURCE_DIR_NAME)
    print(mMSIFile)
    #open list of MMSI file
    #and put it into list
    mMSIList = [line.rstrip('\n') for line in open(mMSIFile)]
    yearsToConsider = [int(year) for year in (config['SEG_VESSEL']['YEARS_TO_CONSIDER'].split(','))]

    monthToConsider = [ \
                        timeUtils.month['Jan']    \
                        ,timeUtils.month['Feb']   \
                        ,timeUtils.month['March'] \
                        ,timeUtils.month['April'] \
                        ,timeUtils.month['May']   \
                        ,timeUtils.month['June']  \
                        ,timeUtils.month['July']  \
                        ,timeUtils.month['Aug']   \
                        ,timeUtils.month['Sept']  \
                        ,timeUtils.month['Oct']   \
                        ,timeUtils.month['Nov']   \
                        ,timeUtils.month['Dec']   \
                        ]

    fileNameList = []
    destDirList = []

    for year in yearsToConsider:
        for monthNum in monthToConsider:
            fileName = srcAffix+SOURCE_DIR_NAME+"/"+"%02d"%(year)+"_"+"%02d"%(monthNum)+".csv"
            fileNameList.append(fileName)
            destDirName = srcAffix+SOURCE_DIR_NAME+"/"+"MMSI_"+"%02d"%(year)+"/"+"%02d"%(monthNum)+"/"
            destDirList.append(destDirName)


    # for file in fileNameList:
    #     print(file)

    # for dir in destDirList:
    #     print(dir)

    #datalist for multiprocessing
    #separate copy of dataframe for each processor
    #(data_processor_num,vessel_name,destdir)
    fileCounter = 0    
    for file in fileNameList:

        dataList = []
        gc.collect()
        for proNum in range(numCores):
            data,_ = aISDM.load_data_from_csv(file)
            dataList.append(data.copy())

        destDir = destDirList[fileCounter]

        argList = []
        procNum = 0
        for name in mMSIList:
            argList.append((procNum,name,destDir))
            procNum = procNum + 1
            if(procNum >= numCores):
                procNum = 0

        #Serial version
        for args in argList:
            segregate_vessel_data_helper(dataList[args[0]], args[1], args[2])
        # Parallel(n_jobs=numCores, backend = 'multiprocessing', verbose=10)(delayed(segregate_vessel_data_helper)(dataList[args[0]], args[1], args[2]) for args in argList)
        fileCounter = fileCounter + 1

if __name__ == '__main__':
    seg_vessel_data_based_on_mmsi()