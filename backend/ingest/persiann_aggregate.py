# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import argparse
import logging
from datetime import datetime, date
import netCDF4
import numpy as np
import os
from pandas import date_range

#-----------------------------------------------------------------------------------------------------------------------
# set up a basic, global _logger which will write to the console as standard error
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d  %H:%M:%S')
_logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------------------------------
def _compute_days_full_years(year_initial,
                             year_final,
                             year_since=1979,
                             month_initial=1,
                             day_initial=1,
                             month_final=12,
                             day_final=31):
    '''
    Computes the "number of days" equivalent for regular, incremental daily time steps given an initial year. 
    Useful when using "days since <year_since>" as the time units within a NetCDF dataset. The resulting list
    of days will represent the range of full years, i.e. from January 1st of the initial year through December 31st 
    of the final year.
     
    :param year_initial: the initial year from which the day values should start, i.e. the first value in the output
                        array will correspond to the number of days between January 1st of this initial year and January 
                        1st of the units since year
    :param year_final: the final year through which the result values are computed
    :param year_since: the start year from which the day values are incremented, with result time steps measured
                        in days since January 1st of this year 
    :return: an array of time step increments, measured in days since midnight of January 1st of the units' "since year"
    :rtype: ndarray of ints 
    '''
    
    # arguments validation
    if year_initial < year_since:
        raise ValueError('Invalid year arguments, initial data year is before the units since year')
    elif year_final < year_initial:
        raise ValueError('Invalid year arguments, final data year is before the initial data year')

    # datetime objects from the years
    date_initial = datetime(year_initial, month_initial, day_initial) # assumes start at beginning of year (issue with partial records like Real-time ICDR)
    date_final = datetime(year_final, month_final, day_final) # assumes end of year, issue with partial records like real-time ICDR
    date_since = datetime(year_since, 1, 1)
        
    # starting day value, i.e. first number of days since the time units' "since year"
    days_initial = (date_initial - date_since).days
        
    # total number of days between Jan 1st of the initial year and Dec 31st of the final year 
    total_days = (date_final - date_initial).days + 1
    
    # list of day values starting at the initial number of days since the time units' "since year"
    days_since = range(days_initial, days_initial + total_days)
                
    return np.array(days_since)

#-----------------------------------------------------------------------------------------------------------------------

def _get_months(start_date,
                 end_date):

    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')

    return date_range(start_date_obj, end_date_obj, freq='D').tolist()

#-----------------------------------------------------------------------------------------------------------------------

def aggregate_persiann(persiann_dir,
                       netcdf_file,
                       start_date,
                       end_date):

    # Change directory to where netCDF output file will be
    os.chdir(persiann_dir) # Necessary?
    _logger.info('\nChanging directory to: ', persiann_dir)
    # Get list of netCDF files in this directory (only works if entire dir...
    # is filled with only netCDF files)
    daily_files = os.listdir(path='.')
    _logger.info('\nFile List length: %s' % str(len(daily_files)))
    # Get values from first file in list
    _logger.info('\nGetting dimension values')

    test_data = netCDF4.Dataset(daily_files[0], 'r')
    # Get dimension values from test data file
    lat_values = list(test_data.variables['lat'])
    lon_values = list(test_data.variables['lon'])
    # Get length of dimension variables
    lat_len = len(lat_values)
    lon_len = len(lon_values)

    # get range of dates to cover
    _logger.info('\nGetting list of dates')
    dates = _get_months(start_date, end_date)
    # DEBUGGING
    
    # for debugging on October 2018 date errors
    _logger.info('\nDates length: %s' % str(len(dates)))
    with netCDF4.Dataset(netcdf_file, 'w') as output_dataset:
        _logger.info('\nCreating netCDF file: %s' % str(netcdf_file))
        # create the time, x, and y dimensions
        output_dataset.createDimension('time', None)
        output_dataset.createDimension('lat', len(lat_values))
        output_dataset.createDimension('lon', len(lon_values))
        
        # global attributes
        output_dataset.title = 'Precipitation Amount'
            
        # create the coordinate variables
        time_variable = output_dataset.createVariable('time', 'i4', ('time',))
        lat_variable = output_dataset.createVariable('lat', 'f4', ('lat',))
        lon_variable = output_dataset.createVariable('lon', 'f4', ('lon',))
          
        # set the coordinate variables' attributes
        #time_variable.units = 'days since {0}-01-01'.format(units_since_year)
        time_variable.units = 'days since 1979-01-01'
        lat_variable.units = 'degrees_north'
        lon_variable.units = 'degrees_east'
        time_variable.long_name = 'Time'
        lat_variable.long_name = 'Latitude'
        lon_variable.long_name = 'Longitude'
        time_variable.calendar = 'gregorian'
            
        # set the coordinate variable values
        time_variable[:] = _compute_days_full_years(dates[0].year,
                                                    dates[len(dates)-1].year,
                                                    1979,
                                                    dates[0].month,
                                                    dates[0].day,
                                                    dates[len(dates)-1].month,
                                                    dates[len(dates)-1].day)

        lat_variable[:] = np.array(lat_values, 'f4')
        lon_variable[:] = np.array(lon_values, 'f4')
        
        # read the variable data from the PERSIANN file, mask and reshape accordingly, and then assign into the variable
        data_variable = output_dataset.createVariable('prcp', 
                                                      'f4', 
                                                      ('time', 'lon', 'lat',),
                                                      fill_value=np.NaN)
        data_variable.units = 'mm'
        data_variable.standard_name = 'precipitation'
        data_variable.long_name = 'NOAA Climate Data Record of PERSIANN-CDR daily precipitation'
        data_variable.description = 'Precipitation amount'
    
        # Add data from files into output netCDF created above
        # Change directory to where netCDF output file will be
        os.chdir(persiann_dir) # Check format
        # loop over each year/month, reading binary data from PERSIANN files and adding into the NetCDF variable
        # NEED TO MAKE THIS IF AND ONLY UPDATE WITH MANUAL_DATES OPTION
        days_index = 0
        
        # Get list of netCDF files in this directory (only works if entire dir...
        # is filled with only netCDF files)
        daily_files = os.listdir(path='.')
    
        # Added for manual dates
        _logger.info('\nLooping through files and adding data')
        
        for datee in dates:
            # find correct file from list by date
            doi = datee.strftime("%Y%m%d")
            sub = "v01r01_{}".format(doi)
            fname = str([thisfile for thisfile in daily_files if sub in thisfile])
            fname = fname[2:len(fname)-2] # Removes brackets from selected file name
            # read data from PERSIANN netCDF file
            dataset = netCDF4.Dataset(fname, 'r')
            data = np.array(dataset.variables['precipitation'])
            
            # convert missing values to NaNs
            data[data == float(-9999.0)] = np.NaN
            
            # assume values are in lat/lon orientation
            data = np.reshape(data, (1, 1440, 480))
            
            data_variable[days_index, :, :] = data[:, : lon_len, : lat_len] # tweaked to use index values
            
            days_index += 1


#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    """
    This module is used aggregate PERSIANN datasets to one single NetCDF.

    Example command line usage for reading all daily files for all months into a single NetCDF file containing gauge 
    adjusted daily precipitation for the full period of record (all months), with all files downloaded from FTP and 
    left in place:
    
    $ python persiann_aggregate.py --persiann_dir /data/persiann/raw \
                                 --out_file C:/home/data/persiann_file.nc \
                                 --start_date 1983-01-01 \
                                 --end_date 2018-12-31
                                 
    """
    try:
        # log some timing info, used later for elapsed time
        start_datetime = datetime.now()
        _logger.info("Starting aggregation: ", start_datetime)
        
        # parse the command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("--persiann_dir", 
                            help="Directory containing daily PERSIANN data files for a single month", 
                            required=True)
        parser.add_argument("--out_file", 
                            help="NetCDF output file containing variables read from the input data", 
                            required=True)
        # Added to allow user specified start-/end-dates for specific data periods
        parser.add_argument("--start_date",
                            help="Start date (YYYY-MM-DD format) for data being downloaded if not downloading a period of record starting on Jan. 1, 1998",
                            required=True)
        parser.add_argument("--end_date",
                            help="End date (YYYY-MM-DD format) for data being downloaded if not downloading a period of record ending on Dec. 31, 2017",
                            required=True)
        args = parser.parse_args()
        
        # display run info
        _logger.info('\nCombining PERSIANN precipitation dataset')
        _logger.info('Result NetCDF:   %s' % args.out_file)
        _logger.info('Work directory:  %s' % args.persiann_dir)
        _logger.info('\nRunning...\n')
        
        # Perform the aggregation
        aggregate_persiann(args.persiann_dir,
                           args.out_file,
                           args.start_date,
                           args.end_date)
        
        # display the info in case the above info has scrolled past due to output from the ingest process itself
        _logger.info('\nSuccessfully completed')
        _logger.info('\nResult NetCDF:   %s\n' % args.out_file)
        
        # report on the elapsed time
        end_datetime = datetime.now()
        _logger.info("End time:      %s", end_datetime)
        elapsed = end_datetime - start_datetime
        _logger.info("Elapsed time:  %s", elapsed)
        
    except Exception as ex:
        _logger.exception('Failed to complete', exc_info=True)
        raise
