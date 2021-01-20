import pandas as pd
import numpy as np 
import Constants as c

class AISDataManager():
    """
    A wrapper class for pandas api to process the AIS data

    Attributes
    ---------

    Methods
    ---------
    load_data_from_csv(fileName)
        loads data from csv file to pandas dataframe
    save_data_to_csv(dFObj, fileName)
        saves data from pandas dataframe to csv file
    filter_based_on_lon_lat(self, dFObj, lonMin, lonMax, latMin, latMax)
        crops the data to given ROI
    get_list_of_unique_mmsi(self, dFObj)
        get list of unique MMSI in a given data frame
    filter_based_on_mmsi(self, dFObj, mMSINum)
        filter MMSI specific data
    def formate_time(self, dFObj, colName, inPlace = False)
        add date time column which has time64 formate
    """

    def __init__(self):
        pass

    def load_data_from_csv(self, fileName):
        """
        loads data from the csv file into pandas dataframe

        Parameters
        ---------
        fileName : str
            relative or exact location of the csv file
            

        Raises
        ---------
        FileNotFoundError
            if file is not present
        """

        try:
            data = pd.read_csv(f'{fileName}')
            return data, c.errNO['SUCCESS']
        except FileNotFoundError:
            print("File : '%s' Not found"%fileName)
            return None, c.errNO['FILE_NOT_FOUND']
    
    def save_data_to_csv(self, dFObj, fileName):
        """
        saves pandas dataframe to csv file

        Parameters
        ---------
        dFObj : pandas dataframe
            dataframe object to be saved
        fileName : str
            relative or exact location of the csv file to be stored
        
        Raises
        ---------
        FileNotFoundError
            if destination directory is not present
        """

        try:
            dFObj.to_csv(fileName,index=False)
            return c.errNO['SUCCESS']
        except FileNotFoundError:
            print("File : '%s' Not found"%fileName)
            return c.errNO['FILE_NOT_FOUND']

    def filter_based_on_lon_lat(self, dFObj, lonMin, lonMax, latMin, latMax):
        """
        To extract data limited to Region of Interest

        Parameters
        ---------
        dFObj : pandas dataframe
            dataframe object to be cropped
        lonMin : float
            bottom left longitude coordinate 
        lonMax : float
            top right longitude coordinate 
        latMin : float
            bottom left lattitude coordinate 
        latMax : float
            top right lattitude coordinate 
        """
        filteredDF = dFObj[(dFObj[c.LON_COL_NAME] >= lonMin) \
                            & (dFObj[c.LON_COL_NAME] < lonMax) \
                            & (dFObj[c.LAT_COL_NAME] >= latMin) \
                            & (dFObj[c.LAT_COL_NAME] < latMax) \
                            ]
        return filteredDF

    def get_list_of_unique_mmsi(self, dFObj):
        """
        To get unique entries of MMSI

        Parameters
        ---------
        dFObj : pandas dataframe
            dataframe object from which we need unique MMSI

        TODO:
            does not check for the presence of MMSI column
            add a check if needed
        """
        ret = dFObj[c.MMSI_COL_NAME].unique()
        return ret

    def filter_based_on_mmsi(self, dFObj, mMSINum):
        """
        Get dataframe consisting of MMSI specified by mMSINum

        Parameters
        ---------
        dFObj : pandas dataframe
            dataframe object from which we need MMSI specific data
        mMSINum : str or int
            specif MMSI whose data we need
        """

        #filtered data frame
        #based on MMSI number
        filteredDF = dFObj[dFObj[c.MMSI_COL_NAME] == mMSINum]
        return filteredDF

    def formate_time(self, dFObj, colName, inPlace = False):
        """
        Makes type of Basetime column of the dataset ob Time64 formate

        Parameters
        ---------
        dFObj : pandas dataframe
            dataframe object whose basetime needs to be converted
        colName : str
            name of the BaseTime column
        inPlace : bool 
            in place or not, pass true to save memory
        """
        #will return same DF with extra column
        #this will change the original DF if we change the return value
        if(inPlace == False):
            retDF = dFObj.copy()
        else:
            retDF = dFObj
        #check for whether date time column is already there or not
        if(colName in retDF.columns):
            if(retDF.loc[:, colName].dtypes == np.dtype('object')):
                retDF.loc[:, colName] = pd.to_datetime(retDF[colName])
        else:
            with pd.option_context('mode.chained_assignment', None):
                retDF.loc[:, colName] = pd.to_datetime(retDF[c.BASE_TIME_COL_NAME], format='%Y-%m-%dT%H:%M:%S')
        return retDF
            
if __name__ == '__main__':
    aDMTest = AISDataManager()