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
            
if __name__ == '__main__':
    aDMTest = AISDataManager()