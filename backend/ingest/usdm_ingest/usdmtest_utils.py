import os.path
from zipfile import ZipFile as zip
import urllib2

def get_file(data_location, urlDownload, saveAs):    

    urlSave = data_location + saveAs

    try:
        fileHandle = urllib2.urlopen(urlDownload)
        zipText = fileHandle.read()
        fileHandle.close()
        if (len(zipText) < 100):
            return False
        
        output = open(urlSave,'wb')
        output.write(zipText)
        output.close()
        print ("---> Downloading file from: " + urlDownload)
    except:
        return False
    return True

def get_usdmData(temp_location, usdm_location, date_str):
    
    urlDownload = 'http://droughtmonitor.unl.edu/data/shapefiles_m/USDM_' + date_str + '_M.zip'
    urlSave = 'usdm' + date_str + '.zip'
#    directory = usdm_location
    if (not (os.path.exists(temp_location + urlSave))):
        get_file(temp_location, urlDownload, urlSave)
    
    unzip_data(temp_location + urlSave, usdm_location)
    print ("---> Downloaded: " + str(urlSave))

def unzip_data(temp_location, usdm_location):
        
    zipStuff = zip(temp_location)
    zipStuff.extractall(usdm_location);