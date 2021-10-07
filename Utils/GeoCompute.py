import numpy as np
import math
#to compute haversine distance
from haversine import haversine, Unit


##
## @brief      Calculates the distance in KM between two GPS formate.
##
## @param      lon1  The lon 1
## @param      lat1  The lat 1
## @param      lon2  The lon 2
## @param      lat2  The lat 2
##
## @return     The distance in KM.
##
def compute_distance(lon1,lat1,lon2,lat2):
	#(LAT,LON) formate
	startPoint = (lat1, lon1)
	endPoint = (lat2, lon2)
	distanceKM = haversine(startPoint, endPoint)
	return distanceKM


##
## @brief      Calculates the heading in degrees.
##
## @param      lon1  The lon 1
## @param      lat1  The lat 1
## @param      lon2  The lon 2
## @param      lat2  The lat 2
##
## @return     The heading.
##
def compute_heading(lon1,lat1,lon2,lat2):
	diffLong = math.radians(lon2 - lon1)

	lat1Rad = math.radians(lat1)
	lat2Rad = math.radians(lat2)

	y = math.sin(diffLong) * math.cos(lat2Rad)
	x = math.cos(lat1Rad) * math.sin(lat2Rad)\
		- (math.sin(lat1Rad) * math.cos(lat2Rad) * math.cos(diffLong))

	compassBearing = 0

	compassBearing = math.atan2(x, y)

	retVal = (-1*math.degrees(compassBearing))+90
	if(retVal > 180):
		return (-360 + retVal)
	else:
		return retVal

if __name__ == '__main__':
	####################################
	#Test to compute distance between two points
	# distVal = compute_distance(-119.20,32.0,-119.21,32.01)
	# print(distVal)
	####################################
	#Test to compute heading angle between two points
	angle = compute_heading(-118.25061, 33.71417, -118.24766, 33.71412)
	print(angle)