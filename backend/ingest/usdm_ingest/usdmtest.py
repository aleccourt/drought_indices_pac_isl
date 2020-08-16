#import tools
import sys
from datetime import date, timedelta
import usdmtest_utils

#Setting work path --> sys.path sets work path directory to script directory home
work_path = sys.path[0] + '\\'

temp_location = work_path + 'temp\\'
usdm_location = work_path + 'usdm\\'

print (work_path)

#starting process
print ("---INGEST of U.S. DROUGHT DATA from the National Drought Mitigation Center (NDMC)---")

#find the most recent USDM date (Tuesday - to download the latest available data)
td = 0
d = date.today()
if (d.weekday() >= 3):
    td = d.weekday() - 1
else:
    td = d.weekday() + 6 

d = date.today() - timedelta(td)
date_str = d.strftime("%Y%m%d")

print ('Latest USDM release date is: ' + date_str)

#ingest current weekly USDM files
print ('Ingesting current USDM Shapefiles...')
usdmtest_utils.get_usdmData(temp_location, usdm_location, date_str)

#ingest completed
print ('---Ingest Completed. Have a great day!---')