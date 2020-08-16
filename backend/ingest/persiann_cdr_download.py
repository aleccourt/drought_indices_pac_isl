# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 18:09:34 2019

@author: alec.courtright
"""

import os
import urllib.request as urlreq
import pandas as pd
import netCDF4 as nc
import datetime
from bs4 import BeautifulSoup
import re
import argparse

#-----------------------------------------------------------------------------------------------------------------------
# Define function to download the file
def get_file(out_dir, data_url, saveAs):
    urlSave = out_dir + saveAs

    try:
        open_url = urlreq.urlopen(data_url)
        read_file = open_url.read()
        open_url.close()
        if (len(read_file) < 100):
            return false

        file = open(urlSave, 'wb')
        file.write(read_file)
        file.close()
        print("---> Downloading file from: " + data_url)
    except:
        return False
    return True

#-----------------------------------------------------------------------------------------------------------------------
# PERSIANN Data
def get_persiann(temp_location, save_location, start_date, end_date):
    base_url = 'https://www.ncei.noaa.gov/data/precipitation-persiann/access/'
    
    # Create date loop for each day of the year specified by 'year' arg
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    print("Start date: ", start)
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    print("End date: ", end)
    step = datetime.timedelta(days=1)
    # Set data url including year directory
    year = start.strftime("%Y")
    data_url = base_url + year + '/'
    ## NEED TO COLLECT LIST OF LINKS WITH ".nc" AT END
    # Get list of links on https by year
    links = list(getLinks(data_url))
    # Get list of day dates
    date_list = []
    while start <= end:
        date = start.strftime("%Y%m%d")
        date_list.append(date)
        start += step
        
    # Check that date list and number of links match up
    print("Number of dates and links matches?: ", len(date_list) == len(links))
    ## MAY NEED TO BE WITHIN A LOOP AND UTILIZE LIST OF LINKS FROM BEAUTIFUL SOUPS
    # Loop to download data file for each day within the date list
    for i in range(len(date_list)):
        # create name for new file to download
        saveAs = 'PERSIANN_CDR_v01r01_' + date_list[i] + '.nc'
        # set url for file to download
        file_url = data_url + links[i]
        get_file(save_location, file_url, saveAs)
        print("---> Downloaded: " + str(saveAs))
    
#    if (not (os.path.exists(temp_location + saveAs))):
#        get_file(temp_location, data_url, saveAs)

    #get_file(temp_location, data_url, saveAs)

    #unzip_data(temp_location + saveAs, save_location)
    print("---> Downloaded: " + str(saveAs))
    
#-----------------------------------------------------------------------------------------------------------------------
def getLinks(url):
    html_page = urlreq.urlopen(url)
    soup = BeautifulSoup(html_page)
    links = []

    for link in soup.findAll('a', attrs={'href': re.compile(".nc")}): #$.nc?
        links.append(link.get('href'))

    return links    
    
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    """
    This module is used to perform ingest of PERSIANN CDR data for the United States.

    Example command line usage from the EIA Map Data access:
    
    $ python -u persiann_cdr_download.py --temp_location /data/cmorph/raw/ \
                                 --save_location C:/home/data/cmorph_file.nc \
                                 --start_date 2018-01-01 \ 
                                 --end_date 2018-12-31
                                                         
    """

    try:
        # log some timing info, used later for elapsed time
        start_datetime = datetime.datetime.now()
        print("Start time:     " + str(start_datetime))

        # parse the command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--temp_location",
                             help="Temporary directory location to save zipped files",
                             required=True)
        parser.add_argument("--save_location",
                             help="Output directory for saved files",
                             required=True)
        parser.add_argument("--start_date",
                            help="Start date for download - format: YYYY-MM-DD I.e., 2018-01-01 for Jan 1st, 2018",
                            required=True)
        parser.add_argument("--end_date",
                            help="End date for download (must be within same year as start date - format: YYYY-MM-DD I.e., 2018-01-01 for Jan 1st, 2018",
                            required=True)
        args = parser.parse_args()

        # perform the ingest of EIA Power Plant
        get_persiann(args.temp_location, 
                          args.save_location,
                          args.start_date,
                          args.end_date)

        # End time
        end_datetime = datetime.datetime.now()
        print("End time:     " + str(end_datetime))
        elapsed = end_datetime - start_datetime
        print("Time elapsed:     " + str(elapsed))

    except Exception as ex:
        print('Failed to complete')
        raise
