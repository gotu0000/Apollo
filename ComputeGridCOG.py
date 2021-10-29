"""Computes Grid SOG/COG using training list 

This script reads csv file containing list of training trajectories
Script would drop unnecessary columns and append the entire trajectory data 
into one big dataframe. This dataframe is used to compute the COGGrid matrix

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
import HMUtils as hMUtil

aISDM = AISDataManager()

def compute_mean_matrix(cogDF, boundaryArray, horizontalAxis, verticalAxis, opFile, opFileMedian):
	"""
	computes the grid mean matrix by iterating through individual cells
	and getting trajectory points corresponding to those cells then computes
	the mean value of COG for that cell, fianally stores it into the output file
	"""
	npCOG = np.zeros((horizontalAxis.shape[0]*verticalAxis.shape[0]))
	npCOGMed = np.zeros((horizontalAxis.shape[0]*verticalAxis.shape[0]))
	for i in range(len(boundaryArray)):
		boundedDF = aISDM.filter_based_on_lon_lat(cogDF,boundaryArray[i][0]\
													,boundaryArray[i][1]\
													,boundaryArray[i][2]\
													,boundaryArray[i][3]\
													)
		if(boundedDF.shape[0] > 0):
			npCOG[i] = boundedDF['COG'].mean()
			npCOGMed[i] = boundedDF['COG'].median()
			print(npCOG[i])
		print("Done Computing %d"%(i))
	np.save(opFile, npCOG)
	np.save(opFileMedian, npCOGMed)

def main():
	config = configparser.ConfigParser()
	config.read('DefaultConfig.INI')

	print("Computing mean COG")

	lonMin = (float)(config['REGION']['LON_MIN'])
	lonMax = (float)(config['REGION']['LON_MAX'])

	latMin = (float)(config['REGION']['LAT_MIN'])
	latMax = (float)(config['REGION']['LAT_MAX'])

	increStep = (float)(config['COMPUTE_AVG_COG']['INCR_STEP'])
	incrRes = (int)(config['COMPUTE_AVG_COG']['INCR_RES'])
	opFile = (config['COMPUTE_AVG_COG']['OUTPUT_FILE'])
	opFileMedian = (config['COMPUTE_AVG_COG']['OUTPUT_MED_FILE'])

	srcDir = (config['COMPUTE_AVG_COG']['SRC_DIR'])
	srcTrainFile = (config['COMPUTE_AVG_COG']['SRC_TRAIN_LIST'])

	print(srcDir)
	print(srcTrainFile)
	print(opFile)

	heatMapGrid = hMUtil.generate_grid(lonMin, lonMax, latMin, latMax, increStep, incrRes)
	boundaryArray = heatMapGrid[2]
	horizontalAxis = heatMapGrid[0]
	verticalAxis = heatMapGrid[1]

	trainDataList, _ = aISDM.load_data_from_csv(srcTrainFile)
	print(trainDataList.shape)
	vesselTrajCountList = []
	cOGDF = pd.DataFrame()
	# for i in range(trainDataList.shape[0]):
	for i in range(0,1):
		tempTrajInfo = trainDataList.iloc[i]
		tempMMSI = tempTrajInfo['MMSI']
		tempTrajNum = tempTrajInfo['TRAJ_NUM']
		tempTrajLoc = srcDir + str(int(tempMMSI)) + "_" + str(int(tempTrajNum)) + ".csv"
		ret, _ = aISDM.load_data_from_csv(tempTrajLoc)
		ret = ret.drop(columns = ['BaseDateTime', 'DateTime' \
									, 'SOG', 'CallSign', 'Cargo', 'Draft' \
									, 'Heading', 'IMO', 'Length', 'MMSI' \
									, 'Status', 'TranscieverClass', 'VesselName'
									, 'VesselType', 'Width' \
									])
		cOGDF = cOGDF.append(ret, ignore_index = True)
	compute_mean_matrix(cOGDF, boundaryArray, horizontalAxis, verticalAxis, opFile, opFileMedian)

if __name__ == '__main__':
	main()