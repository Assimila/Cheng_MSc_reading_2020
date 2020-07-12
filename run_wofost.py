import netCDF4 as nc
import matplotlib.pyplot as plt

from PCSE_WOFOST_helpers import write_cabo_weather_file, change_year

from pcse.fileinput import CABOFileReader
from pcse.models import Wofost71_PP
from pcse.fileinput import CABOWeatherDataProvider
from pcse.base.parameter_providers import ParameterProvider
from pcse.util import WOFOST71SiteDataProvider
from pcse.fileinput import YAMLAgroManagementReader
from pcse.fileinput import YAMLCropDataProvider



#=========== Opening the nc file and writing the CABO files =========

# Where the nc data files are
input_directory = "/data/WOFOST_weather_data/era5/MSc_examples/"
# Where the weather text file will be written
cabo_directory = "./"

# Read the data from the nc files. Each file contains one parameter
nc_files = {
            "wind_speed":"ERA5_10m_wind_speed_1993-2015_wofost_meanspd10m_daily.nc",
            "mx2t":"ERA5_2m_temperature_1993-2015_wofost_maxt2m_daily.nc",
            "mn2t":"ERA5_2m_temperature_1993-2015_wofost_mint2m_daily.nc",
            "vapour_pressure":"ERA5_2m_vapour_pressure_1993-2015_wofost_meanvp2m_daily.nc",
            "surface_downwelling_shortwave_flux_in_air":"ERA5_surface_solar_radiation_downwards_1993-2015_wofost_sumssrd_daily.nc",
            "precipitation_flux":"ERA5_total_precipitation_1993-2015_wofost_sumprcp_daily.nc"}
# Store the data in a dictionary. keys are the parameter names and values are the data array.
era_data = {}
for parameter, filename in nc_files.items():
    if parameter in ("mx2t", "mn2t"):
        # both of these parameters use "air_temperature" as the variable name in the nc file.
        nc_param_name = "air_temperature"
    else:
        nc_param_name = parameter
    nc_data = nc.Dataset(input_directory+filename, 'r')
    era_data[parameter] = nc_data.variables[nc_param_name][:]
# Get the dates, latitudes and longitudes from the last nc file we looked at. (assumes all of the files contain
# the same dates, latitudes and longitudes)
latitudes = nc_data.variables['latitude'][:]
longitudes = nc_data.variables['longitude'][:]
years = nc_data.variables['year'][:]
day_of_year = nc_data.variables['day_of_year'][:]


print("read in data")
print('')

# This is the pixel and year we are going to look at. We'll select the pixel by index
lat_ind = 10
lon_ind = 15
year_of_interest = 2012

lat = latitudes[lat_ind]
lon = longitudes[lon_ind]

# Select data to write to this file and save it as a dictionary with the keys:
# ('doy', 'surface_downwelling_shortwave_flux_in_air', 'mn2t', 'mx2t', 'vapour_pressure', 'wind_speed', 'precipitation_flux')
# Finding data for the chosen year, latitude and longitude.
weather_data_to_write = {parameter:data[years==year_of_interest, lat_ind, lon_ind]
                         for parameter, data in era_data.items()}
weather_data_to_write['doy'] = day_of_year[years==year_of_interest]
print (weather_data_to_write.keys())

filename=f'{cabo_directory}/weather_cabo_China_{lat}_{lon}'

# Write the weather data to a cabo text file. cabo_file is a string to locate the file (Will be the same as filename)
# Don't add an extension to 'filename' write_cabo_weather_file will automatically add it.
cabo_weather_file = write_cabo_weather_file(year_of_interest, lat, lon, weather_data_to_write,
                                            filename=filename)


#=======================================
#======= Running the crop model ========

# Set up input paramter files describing soil and crop.
# You will always use the same files here
soil = CABOFileReader('Hengshui.soil')
site = WOFOST71SiteDataProvider(WAV=100, CO2=360)
crop = YAMLCropDataProvider('.')  # directory containing crop file
crop.set_active_crop('maize', 'Grain_maize_204')
parameters = ParameterProvider(crop, soil, site)

# Set up the parameters that describe sowing, harvest and crop management.
agromanagement = YAMLAgroManagementReader('timer_china_maize.amgt')
# Update agromanagement to the year we are interested in. This needs to
# match the year of the weather data you are using
new_agromanagement = change_year(agromanagement, year_of_interest)

# Set up the weather file with the weather data we wrote above
weather = CABOWeatherDataProvider(cabo_weather_file)

# Initialise the model
wofost = Wofost71_PP(parameters, weather, new_agromanagement)
# Run the crop model
wofost.run_till_terminate()
# Get the out put
output = wofost.get_output()

# Final yield, This is what we are interested in.
# We get the output on the last day (output[-1]) and
# we are interested in the Total Weight of Storage Organs (TWSO),
# which is strongly related to yield.
TWSO_final = output[-1]['TWSO']
print(f"The final yield is {TWSO_final} kg ha-1")

# Look at the outputs. You won't need all of these for your studies but
# It is good to check things look sensible and see some of the outputs
# of the model.

day = [x['day'] for x in output]
TWSO = [x['TWSO'] for x in output]
LAI = [x['LAI'] for x in output]

print(type(output))

fig, ax = plt.subplots(nrows=2, figsize=(12, 10))
ax[0].plot(day, TWSO)
ax[0].set_title('Change in Total weight of storage organs (TWSO) through growing season')
ax[0].set_ylabel('TWSO (kg ha-1)')

ax[1].plot(day, LAI)
ax[1].set_title('Change in Leaf Area Index (How "green" the crop is) through growing season')
ax[1].set_ylabel('Leaf Area Index (unitless)')
for a in ax:
    a.set_xlabel('date')
plt.show()

