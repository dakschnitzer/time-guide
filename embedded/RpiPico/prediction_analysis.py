from datetime import datetime, timedelta
import csv
from dateutil.relativedelta import relativedelta
import math
from datetime import datetime
from siderial_time import siderial_time
import numpy
from skyfield_logs import rise_set_list, radec_list
from main import find_rise_set


lat = 38.9072
lon = -77.0369


def predict_accuracy(lat, lon, start_year, start_month, start_day, start_hour, start_minute, start_second, name, n_months):
    #check the accuracy of the rise time predicted by the rise_set_list function against a list of actual rise times from skyfield
    
    #generate list of daily actual rise, set times from skyfield
    rise_set_actual = rise_set_list(lat, lon, start_year, start_month, start_day, start_hour, start_minute, start_second, name, n_months)
    rise_set_value = [column[1] for column in rise_set_actual]
    rise_set_value = numpy.array(rise_set_value)
    rise_set_time = [column[0] for column in rise_set_actual]
    rise_set_time = numpy.array(rise_set_time)
    
    rise_times_actual = rise_set_time[numpy.where(rise_set_value == 1)]
    rise_times_actual = [datetime.strptime(date, '%Y/%m/%d %H:%M:%S') for date in rise_times_actual]
    
    
    set_times_actual = rise_set_time[numpy.where(rise_set_value == 0)]
    set_times_actual = [datetime.strptime(date, '%Y/%m/%d %H:%M:%S') for date in set_times_actual]
    
    
    start_date = datetime(start_year, start_month, start_day, start_hour, start_minute, start_second)
    
    n_days = start_date + relativedelta(months = n_months) - start_date
    n_days = n_days.days
    
    #generate list of daily predicted rise times from ra, dec
    radec = radec_list(start_year, start_month, start_day, start_hour, start_minute, start_second, name, 1, n_days, 0)
    lrise = [[0 for i in range(1)] for j in range(len(radec))]
    lset = [[0 for i in range(1)] for j in range(len(radec))]

    for i in range(len(radec)):
        date = start_date + timedelta(days = i)
        
        ra = radec[i][1]
        dec = radec[i][2]
        
        lrise[i] = find_rise_set(lat, lon, date.year, date.month, date.day, date.hour, date.minute, date.second, ra, dec)[0]
        lset[i] =  find_rise_set(lat, lon, date.year, date.month, date.day, date.hour, date.minute, date.second, ra, dec)[1]
    

    return rise_times_actual
    

rise_times = predict_accuracy(lat, lon, 2023, 2, 1, 0, 0, 0, 'jupiter', 1)

# dates_list = [datetime.strptime(date, '%Y/%m/%d %H:%M:%S') for date in rise_times]

# (dates_list[1]-dates_list[0]).total_seconds()

start_year = 2023
start_month = 2
start_day = 1
start_hour = 0 
start_minute = 0
start_second = 0 
name = 'jupiter' 
n_months = 1