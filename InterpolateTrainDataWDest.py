"""Interpolates continueous trajectories of the vessel for an interval 
of 5 minute (for 1 minute there are lot of approximations)

This script reads csv file containing list of training trajectories
Now for a particular trajectory, the script generates trajectory
at an interval of 5 minute by interpolating the neighbouring values
1st location 2:18:57 
2nd location 2:19:03
Script would give location at 2:18:57
Interpolated location at 2:23:57
Interpolated locations are computed using nearest negihbours

Any additional comments
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
import Interpolation as iP
import Constants as c
import TimeUtils as timeUtils

from joblib import Parallel, delayed
import multiprocessing
import datetime

aISDM = AISDataManager()
CONSECUTIVE_DP_TIME_DIFF = 5#TODO use this to get rid of other constants
CONSECUTIVE_DP_TIME_DIFF_THRES = 2.5

def convert_to_seconds(timeDel):
	return datetime.timedelta.total_seconds(timeDel)

def gen_interpolated_traj(trajDF, infoAffx):
	"""
	generates interpolated trajectory

	Dataframe corresponding to trajectory
	Gets first trajectory instance
	Generates next 5 minute time point
	Finds nearest neighbour in the data frame
	Computes interpolated value

	Parameter:
    trajDF: pandas dataframe
    	name of a file, which contains trajectory of a vessel
    infoAffx: string
    	name of affix file to identify individual trajectory
	"""
	
	#First time stamp
	firstDPTS = trajDF['DateTime'].iloc[0]
	firstDPTS = pd.to_datetime(firstDPTS)
	# print(firstDPTS)
	#Next would be at 5 minute interval
	nextDPTS = firstDPTS + datetime.timedelta(minutes = CONSECUTIVE_DP_TIME_DIFF)
	destLat, destLon = trajDF['LAT'].iloc[-1], trajDF['LON'].iloc[-1]
	rowsDF = []
	rowDF = [trajDF['DateTime'].iloc[0] \
			, trajDF['LAT'].iloc[0] \
			, trajDF['LON'].iloc[0] \
			, trajDF['SOG'].iloc[0] \
			, trajDF['COG'].iloc[0] \
			, destLat \
			, destLon \
			]
	rowsDF.append(rowDF)
	trajCounter = 0
	for i in range(1,trajDF.shape[0]):
		prevTempTime = pd.to_datetime(trajDF['DateTime'].iloc[i-1])
		tempTime = pd.to_datetime(trajDF['DateTime'].iloc[i])
		if(tempTime > nextDPTS):
			# print(tempTime)

			timeDiff = tempTime - nextDPTS
			#Check here for difference of time 
			#Should be between 0 minutes to 3 minutes
			#If more than that then new dataframe append
			if(convert_to_seconds(timeDiff) > ((CONSECUTIVE_DP_TIME_DIFF-CONSECUTIVE_DP_TIME_DIFF_THRES)*timeUtils.NUM_SEC_IN_MIN)):
				#Check for row count
				#put it into dataframe
				if(len(rowsDF) >= 18):
					opFile = (infoAffx+"_"+str(trajCounter)+".csv")
					rowsPDDF = pd.DataFrame(rowsDF, columns =['DateTime', 'LAT', 'LON', 'SOG', 'COG', 'DEST_LAT', 'DEST_LON'])
					aISDM.save_data_to_csv(rowsPDDF, opFile)
					trajCounter = trajCounter + 1
				else:
					pass
					#dropped counter increment if needed

				#make new dataframe
				rowsDF = []
				rowDF = [trajDF['DateTime'].iloc[i] \
						, trajDF['LAT'].iloc[i] \
						, trajDF['LON'].iloc[i] \
						, trajDF['SOG'].iloc[i] \
						, trajDF['COG'].iloc[i] \
						, destLat \
						, destLon \
						]
				rowsDF.append(rowDF)
				nextDPTS = pd.to_datetime(trajDF['DateTime'].iloc[i]) + datetime.timedelta(minutes = CONSECUTIVE_DP_TIME_DIFF)
				continue

			lon1 = trajDF['LON'].iloc[i-1]
			lat1 = trajDF['LAT'].iloc[i-1]
			sOG1 = trajDF['SOG'].iloc[i-1]
			cOG1 = trajDF['COG'].iloc[i-1]

			lon2 = trajDF['LON'].iloc[i]
			lat2 = trajDF['LAT'].iloc[i]
			sOG2 = trajDF['SOG'].iloc[i]
			cOG2 = trajDF['COG'].iloc[i]

			t2 = pd.to_datetime(trajDF['DateTime'].iloc[i])
			t1 = pd.to_datetime(trajDF['DateTime'].iloc[i-1])

			t2Del = convert_to_seconds((t2 - t1))
			t1Del = convert_to_seconds((t1 - t1))
			tIP = convert_to_seconds((nextDPTS - t1))

			#Compute the interpolated locations
			lonIP = iP.apply_linear_interpolation(t1Del, lon1, t2Del, lon2, tIP)
			latIP = iP.apply_linear_interpolation(t1Del, lat1, t2Del, lat2, tIP)
			sOGIP = iP.apply_linear_interpolation(t1Del, sOG1, t2Del, sOG2, tIP)
			cOGIP = iP.apply_linear_interpolation(t1Del, cOG1, t2Del, cOG2, tIP)

			rowDF = [ nextDPTS\
						, latIP \
						, lonIP \
						, sOGIP \
						, cOGIP \
						, destLat \
						, destLon \
						]
			rowsDF.append(rowDF)
			nextDPTS = nextDPTS + datetime.timedelta(minutes = CONSECUTIVE_DP_TIME_DIFF)
	#TODO replace 18 with the constant
	if(len(rowsDF) >= 18):
		opFile = (infoAffx+"_"+str(trajCounter)+".csv")
		rowsPDDF = pd.DataFrame(rowsDF, columns =['DateTime', 'LAT', 'LON', 'SOG', 'COG', 'DEST_LAT', 'DEST_LON'])
		aISDM.save_data_to_csv(rowsPDDF, opFile)
		trajCounter = trajCounter + 1
	else:
		pass
		#dropped counter increment if needed
	fileCountStr = (infoAffx+"_"+str(trajCounter))
	return fileCountStr
        

def main():
	config = configparser.ConfigParser()
	config.read('DefaultConfig.INI')

	print("Interpolating vessel trajectories")

	srcDir = (config['INTERP_TRAJ_DEST']['SRC_DIR'])
	srcTrainFile = (config['INTERP_TRAJ_DEST']['SRC_TRAIN_LIST'])
	destDir = (config['INTERP_TRAJ_DEST']['DEST_DIR'])

	print(srcDir)
	print(srcTrainFile)
	print(destDir)

	trainDataList, _ = aISDM.load_data_from_csv(srcTrainFile)
	print(trainDataList.shape)
	vesselTrajCountList = []
	for i in range(trainDataList.shape[0]):
	# for i in range(0,1):
		tempTrajInfo = trainDataList.iloc[i]
		tempMMSI = tempTrajInfo['MMSI']
		tempTrajNum = tempTrajInfo['TRAJ_NUM']
		tempTrajLoc = srcDir + str(int(tempMMSI)) + "_" + str(int(tempTrajNum)) + ".csv"
		ret, _ = aISDM.load_data_from_csv(tempTrajLoc)
		trajInfoAffix = destDir + str(int(tempMMSI)) + "_" + str(int(tempTrajNum)) + "_" + str(int(0))
		print(trajInfoAffix)
		vesselTrajCountStr = gen_interpolated_traj(ret, trajInfoAffix)
		vesselTrajCountList.append(vesselTrajCountStr)

		#First time stamp
		delayedTS = pd.to_datetime(ret['DateTime'].iloc[0]) + datetime.timedelta(minutes = 2)
		print(delayedTS)
		#get the delayed index
		for delayedIDX in range(1,ret.shape[0]):
			prevTempTime = pd.to_datetime(ret['DateTime'].iloc[delayedIDX-1])
			tempTime = pd.to_datetime(ret['DateTime'].iloc[delayedIDX])
			if(tempTime > delayedTS):
				#routine for delayed version of trajectory
				retDelayed = ret.iloc[delayedIDX:,:]
				trajInfoAffix = destDir + str(int(tempMMSI)) + "_" + str(int(tempTrajNum)) + "_" + str(int(1))
				print(trajInfoAffix)
				vesselTrajCountStr = gen_interpolated_traj(retDelayed, trajInfoAffix)
				vesselTrajCountList.append(vesselTrajCountStr)
				break

	#save to file 
	destFileName = destDir + 'TrainTrajCount.txt'
	with open(destFileName, 'w') as f:
	    for item in vesselTrajCountList:
	        f.write("%s\n" % item)


if __name__ == '__main__':
	main()