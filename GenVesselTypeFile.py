"""Generates type file for vessels of different type

This script takes the combined vessel data and checks the
type column and generates txt and csv file for MMSI-type

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


def gen_vessel_type_file():
	"""
	Generates type file for all the vessel

	Assumes combined vessel data to be present in SOURCE_DIR
	and takes list of MMSI
	opens file corresponding to MMSI
	reads the type column
	appens to the list
	the list gets stored as csv and txt file
	"""

	aISDM = AISDataManager()

	numCores = multiprocessing.cpu_count()
	print(numCores)

	config = configparser.ConfigParser()
	#DefaultConfig.INI stores all the run time constants
	config.read('DefaultConfig.INI')

	srcDir = (config['GEN_VESSEL_TYPE']['SOURCE_DIR'])
	mMSIFile = (config['GEN_VESSEL_TYPE']['MMSI_FILE'])
	destFile = (config['GEN_VESSEL_TYPE']['DEST_FILE'])
	typeListDestFile = (config['GEN_VESSEL_TYPE']['TYPE_LIST_DEST_FILE'])

	print(srcDir)
	print(mMSIFile)
	print(destFile)
	print(typeListDestFile)
	#open list of MMSI file
	#and put it into list
	mMSIList = [line.rstrip('\n') for line in open(mMSIFile)]

	#targeted dataframe to be stored as the output
	vesselTypeDF = pd.DataFrame(columns=['MMSI','VesselType'])

	for vesselName in mMSIList:
		#get the file name
		fileName = srcDir + vesselName + "_Sorted.csv"
		#load the data of one particular vessel
		mMSIDF,_ = aISDM.load_data_from_csv(fileName)
		#get the index of type
		typeIDX = mMSIDF.columns.get_loc("VesselType")
		#now append the MMSI and type in data farme
		vesselType = mMSIDF.iloc[0,typeIDX]
		# print(vesselType)

		#https://thispointer.com/pandas-how-to-create-an-empty-dataframe-and-append-rows-columns-to-it-in-python/
		vesselTypeDF = vesselTypeDF.append({'MMSI':vesselName \
										,'VesselType':vesselType}
										, ignore_index= True)


	#sort according to type
	vesselTypeDF = vesselTypeDF.sort_values(by='VesselType')
	# sortedType = aISDM.get_list_of_unique_enries(vesselTypeDF,'VesselType')
	sortedType = vesselTypeDF['VesselType'].unique()

	#save to file 
	with open(typeListDestFile, 'w') as f:
	    for item in sortedType:
	        f.write("%s\n" % item)

	#save the information
	#further can be edited manuall
	aISDM.save_data_to_csv(vesselTypeDF, destFile)

if __name__ == '__main__':
	gen_vessel_type_file()