"""Extracts continueous trajectories for the vessels

This script reads txt file of list of vessels for a particular 
type and opens a file containing the data specifc to particular vessel
and extracts continuous trajectories of that vessels
continuous trajectories can be defined as difference between consecutive AIS
messages is less than an hour or time specified default 60 Minutes

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
import datetime

aISDM = AISDataManager()
#T Minutes * 60(seconds)
#to identify continuous trajectories
MAX_TIME_INTERVAL_DIFF = (10*timeUtils.NUM_SEC_IN_MIN)
#assumption is 1 Minute so atleast message of 90 minutes
MINIMUM_SHAPE = 90
minimumShapeDropped = 0

SOG_THRESHOLD = 2.0

def convert_to_seconds(timeDel):
	return datetime.timedelta.total_seconds(timeDel)

def seg_traj_data(sourceDir, vesselName, destDir):
	"""
	segregates the trajectory data into multiple files

	Reads the file of one vessel
	Computes the time difference between consecutive AIS messages
	And breaks the trajectory into separate dataframe
	which at the end gets written into a file

	Parametert:
    sourceDir: str
        source directory of the vessel data 
        like MMSI_15_16_17_18_19_COMBINED
    vesselName : str
        name of the vessel whose data needs  to be segrgated
    destDir : str
        Destination directory where combined data would be stored
	where each file can be used to simulate the vessels trajectory 
	"""

	#read the data sorted data
	sourceFile = sourceDir + vesselName + '_Sorted.csv'
	sourceDF, retVal = aISDM.load_data_from_csv(sourceFile)
	# print(sourceDF)
	# print(sourceDF.dtypes)
	#formate the date time
	sourceDFFT = aISDM.formate_time(sourceDF,'DateTime')
	print("Before SOG >= %1.1f"%(SOG_THRESHOLD), sourceDFFT.shape)

	#get rid of all the trajectories 
	#where it is not moving at all
	sourceDFFT = sourceDFFT[sourceDFFT['SOG'] >= SOG_THRESHOLD]
	print("After SOG >= %1.1f"%(SOG_THRESHOLD), sourceDFFT.shape)

	sourceDFFT = sourceDFFT.reset_index(drop=True)
	#Not too many instances
	if(sourceDFFT.shape[0] < 3):
		return -1, -1
	#make copy of DateTime column
	#get the series of date time
	#remove first element
	#and append the time diff of time stamp
	#make it new column
	#compute diff
	dateTimeSeries = sourceDFFT['DateTime']
	# print(type(dateTimeSeries))
	# print(dateTimeSeries.dtypes)
	dateTimeSeriesNext = dateTimeSeries[1:].copy()
	dateTimeSeriesNext = dateTimeSeriesNext.reset_index(drop=True)
	dateTimeSeriesCurrent = dateTimeSeries[0:-1].copy()
	dateTimeSeriesCurrent = dateTimeSeriesCurrent.reset_index(drop=True)
	#last element of series
	dataeTimeDiff = (dateTimeSeriesNext - dateTimeSeriesCurrent)
	dataeTimeDiffSec = dataeTimeDiff.apply(convert_to_seconds) 
	# print(dataeTimeDiffSec.shape)
	slicIdx = dataeTimeDiffSec[(dataeTimeDiffSec > MAX_TIME_INTERVAL_DIFF)].index.tolist()
	# print(slicIdx)


	vesselTrajCounter = 0
	vesselDroppedCounter = 0
	atleastOneFile = 0
	if(len(slicIdx) > 0):
		firstIndex = 0
		for i in range(0,len(slicIdx)):

			ret = sourceDFFT.iloc[firstIndex:slicIdx[i]+1,:].copy()
			ret = ret.reset_index(drop=True)
			print(ret.shape)
			if(ret.shape[0] > MINIMUM_SHAPE):
				opFile = destDir + vesselName + '_' + str(vesselTrajCounter) + '.csv'
				# trajInitT = ret['DateTime'][0]
				# trajEndT = ret['DateTime'][ret['DateTime'].shape[0]-1]
				# print(trajInitT, trajEndT)
				# trajLen = convert_to_seconds(trajEndT - trajInitT)/timeUtils.NUM_SEC_IN_MIN
				# print("Track Length %f"%trajLen)
				# print("Average SOG = %f, Median SOG = %f"%(ret[c.SOG_COL_NAME].mean(),ret[c.SOG_COL_NAME].median()))
				aISDM.save_data_to_csv(ret,opFile)
				vesselTrajCounter = vesselTrajCounter + 1
				atleastOneFile = 1
			else:
				vesselDroppedCounter = vesselDroppedCounter + 1

			firstIndex = slicIdx[i]+1

		firstIndex = slicIdx[-1]+1

		ret = sourceDFFT.iloc[firstIndex:,:].copy()
		ret = ret.reset_index(drop=True)
		print(ret.shape)
		if(ret.shape[0] > MINIMUM_SHAPE):
			opFile = destDir + vesselName + '_' + str(vesselTrajCounter) + '.csv'
			# trajInitT = ret['DateTime'][0]
			# trajEndT = ret['DateTime'][ret['DateTime'].shape[0]-1]
			# print(trajInitT, trajEndT)
			# trajLen = convert_to_seconds(trajEndT - trajInitT)/timeUtils.NUM_SEC_IN_MIN
			# print("Track Length %f"%trajLen)
			# print("Average SOG = %f, Median SOG = %f"%(ret[c.SOG_COL_NAME].mean(),ret[c.SOG_COL_NAME].median()))
			aISDM.save_data_to_csv(ret,opFile)
			vesselTrajCounter = vesselTrajCounter + 1
			atleastOneFile = 1
		else:
			vesselDroppedCounter = vesselDroppedCounter + 1

	#its all part of one sequence
	else:
		ret = sourceDFFT.copy()
		ret = ret.reset_index(drop=True)
		print(ret.shape)
		if(ret.shape[0] > MINIMUM_SHAPE):
			opFile = destDir + vesselName + '_' + str(vesselTrajCounter) + '.csv'
			# trajInitT = ret['DateTime'][0]
			# trajEndT = ret['DateTime'][ret['DateTime'].shape[0]-1]
			# print(trajInitT, trajEndT)
			# trajLen = convert_to_seconds(trajEndT - trajInitT)/timeUtils.NUM_SEC_IN_MIN
			# print("Track Length %f"%trajLen)
			# print("Average SOG = %f, Median SOG = %f"%(ret[c.SOG_COL_NAME].mean(),ret[c.SOG_COL_NAME].median()))
			aISDM.save_data_to_csv(ret,opFile)
			vesselTrajCounter = vesselTrajCounter + 1
			atleastOneFile = 1
		else:
			vesselDroppedCounter = vesselDroppedCounter + 1

	if(atleastOneFile == 1):
		return vesselTrajCounter, vesselDroppedCounter
	else:
		return -1, -1

        

def main():
	config = configparser.ConfigParser()
	config.read('DefaultConfig.INI')

	print("Generating Vessel Trajectory")

	srcDir = (config['GEN_VESSEL_TRAJ']['SRC_DIR'])
	mMSIListFile = (config['GEN_VESSEL_TRAJ']['MMSI_FILE'])
	destDir = (config['GEN_VESSEL_TRAJ']['DEST_DIR'])
	print(srcDir)
	print(mMSIListFile)
	print(destDir)

	
	#Generate List from MMSI
	mMSIList = [line.rstrip('\n') for line in open(mMSIListFile)]
	#For testing purpose uncomment
	# mMSIList = [mMSIList[1]]
	vesselTrajCountList = []
	for mMSI in mMSIList:
		print(mMSI)
		trajCount, trajDroppedCount = seg_traj_data(srcDir, mMSI, destDir)
		print(trajCount)
		if(trajCount > 0):
			vesselTrajCountStr = mMSI + '-' + str(trajCount) + '-' + str(trajDroppedCount)
			vesselTrajCountList.append(vesselTrajCountStr)

	#save to file 
	destFileName = destDir + 'VesselTrajCount.txt'
	with open(destFileName, 'w') as f:
	    for item in vesselTrajCountList:
	        f.write("%s\n" % item)
	

if __name__ == '__main__':
	main()