"""
This file contains functions to help run PCSE WOFOST

Write weather data to the cabo format text file and return the filename (without extension)
write_cabo_weather_file(year, latitude, longitude, data, filename=None,
                            source='ERA5, preprocessed by Nick Klingaman', author='Cheng Han')

The agro-management text file is written for a single year. This function changes the year after
the agro-management information has been read in (in_agro)
change_year(in_agro, year)
"""
import datetime as dt


def write_cabo_weather_file(year, latitude, longitude, data, filename=None,
                            source='ERA5, preprocessed by Nick Klingaman', author='Cheng Han'):
    """
    The weather input files for WOFSOST are text files.
    The first few lines contain this standard text that describes the
    data columns and containts information about the location and source
    of the data. The data are then one row per day. The column order must be:
    ('doy', 'surface_downwelling_shortwave_flux_in_air', 'mn2t', 'mx2t', 'vapour_pressure',
     'wind_speed', 'precipitation_flux')

    year: integer year
    latitude: float latitude
    latitude: float longitude
    """

    if filename is None:
        filename = f'{latidude}_{longitude}'
    # filename has to end in '.yyy' where yyy is the last 3 digits of the year.
    outfile = open(f'{filename}.{str(year)[1:]}', 'w')
    elevation = 50
    header = '*---------------------------------------------------------------------------*\n*Station name: ' \
             + str(latitude) + ' ' + str(longitude) \
             + '\n* Column  Daily value' \
               '\n* 1       station number' \
               '\n* 2       year' \
               '\n* 3       day' \
               '\n* 4       irradiation                   (kJ m-2 d-1)' \
               '\n* 5       minimum temperature           (degrees Celsius)' \
               '\n* 6       maximum temperature           (degrees Celsius)' \
               '\n* 7       early morning vapour pressure (kPa)' \
               '\n* 8       mean wind speed (height: 2 m) (m s-1)' \
               '\n* 9       precipitation                 (mm d-1)' \
               '\n*' \
               '\n* ' + 'Source: ' + source + '\n* Conversion: nc2cabo, Author: q' + author + \
             '\n* File created: ' + str(dt.datetime.today()) + \
             '\n** WCCFORMAT=2\n*---------------------------------------------------------------------------*' \
             '\n' + '%s' % latitude + '  ' + '%s' % longitude + '  ' + '{:>2.6f}'.format(
        elevation) + '  -0.180000  -0.550000 \n'

    # write header
    outfile.write(header)
    # Each row in the output file is one day of data. Format a string for that row
    # and write to the files
    parameter_order = ('doy', 'surface_downwelling_shortwave_flux_in_air', 'mn2t', 'mx2t',
                       'vapour_pressure', 'wind_speed', 'precipitation_flux')
    for i in range(len(data['doy'])):
        row = [data[parameter][i] for parameter in parameter_order]
        thisline = '{:>7} {:>2} {:>4} {:>6.0f} {:>6.1f} {:>6.1f} {:>6.3f} {:>6.1f} {:>6.1f} \n'.format(
            1, year, *row)
        outfile.write(thisline)
    outfile.close()
    # return filename (without year), not outfile, because the PCSE automatically looks for the year.
    return filename


def change_year(in_agro, year):
    """
    The agro-management text file is written for a single year. This function changes the year of the
    sowing and harvest dates in the  agro-management information that has been read ifrom the file
    :param in_agro: agromanagement object
    :param year:
    :return:
    """
    # The agromanagement file contains the sowing date. Update this with the year we are interested in.
    import copy
    old_date = list(in_agro[0].keys())[0]
    new_agro = copy.deepcopy(in_agro[0][old_date])

    new_agro['CropCalendar']['crop_start_date'] = new_agro['CropCalendar']['crop_start_date'].replace(year=year)
    new_agro['CropCalendar']['crop_end_date'] = new_agro['CropCalendar']['crop_end_date'].replace(year=year)

    return [{old_date.replace(year): new_agro}]