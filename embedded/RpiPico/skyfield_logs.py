# write skyfield logs

from skyfield.api import load
from skyfield.api import N, W, wgs84, load, utc
from skyfield.almanac import find_discrete, risings_and_settings
from datetime import datetime, timedelta
import csv
from dateutil.relativedelta import relativedelta

def radec_list(start_year, start_month, start_day, start_hour, start_minute, start_second, name, int_days, n_days, n_months):
# for this function, pass through a start time and date. indicate whether you want a number of days or a number of months. if months, it will go for every month. if days, you can set an interval of days.
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

    return(radec)

    filename = "radec_files/" + str(name) + "_radec" + "_" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(start_date.day) + "-" + str(date.year) + "_" + str(date.month) + "_" + str(date.day) + ".csv"
    
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(radec)

def rise_set_list(lat, lon, start_year, start_month, start_day, start_hour, start_minute, start_second, name, n_months):
    # generate list of daily rise and set times to CSV given a number of months
    city = wgs84.latlon(float(lat), float(lon))
    names = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']
    f = risings_and_settings(eph, planets[names.index(name)], city)
    #This returns a function taking a Time argument returning True if the body’s altazimuth altitude angle plus radius_degrees is greater than horizon_degrees, else False

    start_date = datetime(start_year, start_month, start_day, start_hour, start_minute, start_second, tzinfo=utc)
    print(start_date)
    date = start_date + relativedelta(months = n_months)
    print(date)
    
    t0 = ts.utc(start_date)
    t1 = ts.utc(date)

    t, values = find_discrete(t0, t1, f)
    rise_set = [[0 for i in range(2)] for j in range(len(t))]

    for i in range(len(t)):
        rise_set[i][0] = t[i].utc_strftime('%Y/%m/%d %H:%M:%S')
        rise_set[i][1] = values[i]
        # print(t[i])
        # print(rise_set[i][0])
    # print(rise_set)

    return rise_set
    
    filename = "rise_set_files/" + str(name) + "_rise_set" + "_" + str(start_date.year) + "_" + str(start_date.month) + "_" + str(start_date.day) + "-" + str(date.year) + "_" + str(date.month) + "_" + str(date.day) + ".csv"
    
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerows(rise_set)

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

# # write a CSV file of Jupiter's RA and DEC starting on 2/1/2023 every day for 365 days
# radec_list(2023, 2, 1, 0, 0, 0, 'jupiter', 1, 365, 0)

# # write a CSV file of Jupiter's RA and DEC starting on 2/1/2023 every month for 10 years
# radec_list(2023, 2, 1, 0, 0, 0, 'jupiter', 0, 0, 120)

# # write a CSV file of Jupiter's risings (1) and settings (0) starting on 2/1/2023 every month for 1 year
# lat = 38.9072
# lon = -77.0369
# rise_set_list(lat, lon, 2023, 2, 1, 0, 0, 0, 'jupiter', 12)





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
