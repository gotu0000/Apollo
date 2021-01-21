"""Combine vessel data based on its MMSI

This script takes the vessel data segregated by month 
and combines them into one file for a year or entire duration
of the data

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

def combine_vessel_data(name, segSourceDirList, destDir):
    """
    Helper function to combine the data of the vessel

    Based on name of the vessel
    It willl read individual files from each sub folder
    Combine it and store it into final directory

    Parametert:
    name: str
        name of the vessel
    segSourceDirList : List of str
        List of source directories from which data needs to
        be loaded
    destDir : str
        Destination directory where combined data would be stored
    """

    #empty dataframe initialization
    yearTrajDF = pd.DataFrame()
    for dirEn in segSourceDirList:
        monTrajFile = dirEn + name +'.csv'
        #load and append monthly based data
        monTrajDF,_ = aISDM.load_data_from_csv(monTrajFile)
        yearTrajDF = yearTrajDF.append(monTrajDF, ignore_index = True, sort = True)
    #write it into file
    yearTrajFile = destDir + name +'.csv'
    aISDM.save_data_to_csv(yearTrajDF,yearTrajFile)
    
    #sort it with time
    aISDM.formate_time(yearTrajDF,'DateTime',inPlace = True)
    sortedYearTrajDF = yearTrajDF.sort_values(by='DateTime')
    
    yearTrajSortedFile = destDir + name +'_Sorted.csv'
    aISDM.save_data_to_csv(sortedYearTrajDF,yearTrajSortedFile)

def combine_vessel_data_main():
    """
    Combines vessel monthly data to form yearly data

    Assumes segregated data to be presented in specific formate
    and in specific directory of SOURCE_DIR_NAME folder
    i.e. MMSI_15 will have folders naming from
    01 
    02 
    03 
    04
    -
    -
    -
    12
    Reads MMSI file which has all the names of the vessel whose
    data neeeds to be combined in file either for a year or more
    than one year 
    """

    numCores = multiprocessing.cpu_count()
    print(numCores)

    config = configparser.ConfigParser()
    #DefaultConfig.INI stores all the run time constants
    config.read('DefaultConfig.INI')

    SOURCE_DIR_NAME = (config['COMBINE_VESSEL']['SOURCE_DIR_NAME'])
    mMSIFile = (config['COMBINE_VESSEL']['MMSI_FILE'])
    destDir = (config['COMBINE_VESSEL']['DEST_DIR'])
    yearsToConsider = [int(year) for year in (config['COMBINE_VESSEL']['YEARS_TO_CONSIDER'].split(','))]

    print(SOURCE_DIR_NAME)
    print(mMSIFile)
    print(destDir)

    #open list of MMSI file
    #and put it into list
    mMSIList = [line.rstrip('\n') for line in open(mMSIFile)]


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

    #Source directory list
    #assumes one specif folder 
    segSourceDirList = []

    for year in yearsToConsider:
        for monthNum in monthToConsider:
            segSrcDirName = SOURCE_DIR_NAME+"MMSI_"+"%02d"%(year)+"/"+"%02d"%(monthNum)+"/"
            segSourceDirList.append(segSrcDirName)

    for dirEn in segSourceDirList:
        print(dirEn)
        
    for name in mMSIList:
        combine_vessel_data(name, segSourceDirList, destDir)

if __name__ == '__main__':
    combine_vessel_data_main()