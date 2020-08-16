# Drought Indices for the Pacific Islands

This project is intended to calculate a variety of drought indices for the Pacific Islands using remote sensing data to provide a spatially continuous and near-real-time view of drought in the islands. This code utilizes 
other open source projects and 

This project contains and utilizes Python implementations of various climate index algorithms which provide
a geographical and temporal picture of the severity of precipitation and temperature anomalies
useful for climate monitoring and research. These python implementations are based on the work of [James Adams](https://github.com/monocongo/climate_indices).

The following indices are provided:

- [SPI](https://climatedataguide.ucar.edu/climate-data/standardized-precipitation-index-spi),
  Standardized Precipitation Index, utilizing both gamma and Pearson Type III distributions
- [SPEI](https://www.researchgate.net/publication/252361460_The_Standardized_Precipitation-Evapotranspiration_Index_SPEI_a_multiscalar_drought_index),
  Standardized Precipitation Evapotranspiration Index, utilizing both gamma and Pearson Type III distributions
- [PET](https://www.ncdc.noaa.gov/monitoring-references/dyk/potential-evapotranspiration), Potential Evapotranspiration, utilizing either [Thornthwaite](http://dx.doi.org/10.2307/21073)
  or [Hargreaves](http://dx.doi.org/10.13031/2013.26773) equations
- [PNP](http://www.droughtmanagement.info/percent-of-normal-precipitation/),
  Percentage of Normal Precipitation
