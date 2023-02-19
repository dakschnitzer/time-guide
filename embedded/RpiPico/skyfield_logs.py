# write skyfield logs

from skyfield.api import load
from datetime import datetime, timedelta
import csv
from dateutil.relativedelta import relativedelta

#initialize skyfield stuff
eph = load('de421.bsp')
sun = eph['sun']
moon = eph['moon']
mercury = eph['mercury']
venus  = eph['venus']
earth  = eph['earth']
mars = eph['mars']
jupiter = eph['JUPITER BARYCENTER']
saturn = eph['SATURN BARYCENTER']
uranus = eph['URANUS BARYCENTER']
neptune = eph['NEPTUNE BARYCENTER']
planets = [sun,
           moon,
           mercury,
           venus,
           mars,
           jupiter,
           saturn,
           uranus,
           neptune]
ts = load.timescale()

def radec_list(start_year, start_month, start_day, start_hour, start_minute, start_second, name, int_days, n_days, n_months):
    radec = [[0 for i in range(3)] for j in range(n_days + n_months)]
    start_date = datetime(start_year, start_month, start_day, start_hour, start_minute, start_second)
    names = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
    
    if n_days == 0:
        for i in range(n_months):
            
            date = start_date + relativedelta(months = i)
    
            t = ts.utc(date.year, date.month, date.day, date.hour, date.minute, date.second)
            astrometric = eph['earth'].at(t).observe(planets[names.index(name)])
            ra, dec, distance = astrometric.apparent().radec()
            
            ra = ra.hours
            dec = dec.degrees
            
            radec[i][0] = date.strftime("%Y/%m/%d, %H:%M:%S")
            radec[i][1] = ra
            radec[i][2] = dec
    
    else:
        for i in range(n_days):
            
            date = start_date + timedelta(days = i * int_days)
    
            t = ts.utc(date.year, date.month, date.day, date.hour, date.minute, date.second)
            astrometric = eph['earth'].at(t).observe(planets[names.index(name)])
            ra, dec, distance = astrometric.apparent().radec()
            
            ra = ra.hours
            dec = dec.degrees
            
            radec[i][0] = date.strftime("%Y/%m/%d, %H:%M:%S")
            radec[i][1] = ra
            radec[i][2] = dec


    filename = "radec_files/" + str(name) + "_radec" + "_" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(start_date.day) + "-" + str(date.year) + "_" + str(date.month) + "_" + str(date.day) + ".csv"
    
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(radec)
    

radec_list(2023, 3, 1, 0, 0, 0, 'jupiter', 0, 0, 12)


# with open('RADEC.csv', 'w') as file:
#     writer = csv.writer(file)
#     writer.writerows(csv_rowlist)




# now = datetime.utcnow()
# year = now.year
# month = now.month
# day = now.day
# utc = now.hour + now.minute/60 + now.second/3600




# ra = ra.hours
# dec = dec.degrees
# print('ra hours is', ra, 'dec degrees is', dec, sep='\n')
