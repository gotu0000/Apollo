"""Generates list of MMSI of specific type

This script reads the csv file containing MMSI-Type 
information and returns the MMSI specific to the Types requested

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

def gen_vessel_list_based_on_type():
	"""
	Generates list of MMSIs for particular type

	Assumes MMSI-Typpe data 
	Read into dataframe
	Iterates through every row, and checks 
	whether it's type exist in the desired types or not

	TODO: can be done efficiently using pandas api
	"""

	aISDM = AISDataManager()

	numCores = multiprocessing.cpu_count()
	print(numCores)

	config = configparser.ConfigParser()
	#DefaultConfig.INI stores all the run time constants
	config.read('DefaultConfig.INI')

	mMSITypeFile = (config['GEN_VESSEL_LIST_OF_TYPE_FROM_RAW_TYPE']['MMSI_TYPE_FILE'])
	mMSITypeDestFile = (config['GEN_VESSEL_LIST_OF_TYPE_FROM_RAW_TYPE']['MMSI_SPEC_TYPE_DEST_FILE'])
	allowedType = (config['GEN_VESSEL_LIST_OF_TYPE_FROM_RAW_TYPE']['DESIRED_TYPE']).split(',')

	print(mMSITypeFile)
	print(mMSITypeDestFile)
	print(allowedType)
	mMSITypeDF,_ = aISDM.load_data_from_csv(mMSITypeFile)
	vesselTypeCounter = 0

	#empty list for desired type
	desiredType = []

	#iterate through every row
	for i in range(mMSITypeDF.shape[0]):
		#get MMSI
		currVessel = mMSITypeDF.iloc[i,0]
		currType = mMSITypeDF.iloc[i,1]
		#get type
		# print(currType)
		# print(type(currType))
		# convert in into string for comparision
		currTypeStr = str(currType)
		# print(currTypeStr)
		# print(type(currTypeStr))
		#if found match
		if(currTypeStr in allowedType):
			#append the MMSI
			desiredType.append(currVessel)
			vesselTypeCounter = vesselTypeCounter + 1
		
	print(vesselTypeCounter)
	#save to file 
	with open(mMSITypeDestFile, 'w') as f:
	    for mMSI in desiredType:
	        f.write("%s\n" % mMSI)

if __name__ == '__main__':
	gen_vessel_list_based_on_type()