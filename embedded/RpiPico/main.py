import math
from datetime import datetime, timedelta
from planet_radec import *

#define math stuff
sind = lambda x: math.sin(math.radians(x))
cosd = lambda x: math.cos(math.radians(x))
atan2d = lambda y, x: math.degrees(math.atan2(y, x))
asind = lambda x: math.degrees(math.asin(x))
acosd = lambda x: math.degrees(math.acos(x))
pi = math.pi
sqrt = math.sqrt


def find_day_number(year, month, day):
    day_number = 367*year - math.floor(7 * ( year + math.floor((month+9)/12))  / 4) + math.floor(275*month/9) + day - 730530
    return day_number

def altitude_azimuth(sidereal_time, right_ascension, declination, latitude):
	hour_angle = sidereal_time - right_ascension
	hour_angle = revolve_hour_angle(hour_angle)
	hour_angle = hour_angle * 15
	x = cosd(hour_angle)*cosd(declination)
	y = sind(hour_angle)*cosd(declination)
	z = sind(declination)
	x_horizon = x * sind(latitude) - z * cosd(latitude)
	y_horizon = y
	z_horizon = x * cosd(latitude) + z * sind(latitude)
	azimuth = atan2d(y_horizon,x_horizon) + 180 
	altitude = asind(z_horizon)
	return altitude, azimuth


def find_rise_set(lat, lon, name, day_number, UT):
    #need to select the appropriate planet_radec function based on the "name" input variable
    planet_radec = {'sun': sun_radec, 
                    'moon': moon_radec, 
                    'mercury': mercury_radec, 
                    'venus': venus_radec, 
                    'mars': mars_radec, 
                    'jupiter': jupiter_radec, 
                    'saturn': saturn_radec, 
                    'uranus': uranus_radec, 
                    'neptune': neptune_radec}
    
    #find RA, Dec for planet
    ra = planet_radec[name](day_number)[0]
    dec = planet_radec[name](day_number)[1]
        
    #find greenwich siderial time at midnight
    GMST0 = sun_siderial(day_number, lat, lon, UT)[1]
    
    #gst0 = siderial_time(year, month, day, hour + minute/60 + second/3600, lon)[1]


    #find hour angle of body when altitude = 0
    ha_set = acosd((-sind(lat) * sind(dec)) / (cosd(lat) * cosd(dec)))
    #calculate UT of sun in south - can't figure out if a negative number means it's day before or day after.
    utss_hr = (ra * 15 - GMST0 * 15 - lon) / 15.047
    # utss_hr = utss_hr % 24
    
    
    utss = datetime(year, month, day) + timedelta(hours = utss_hr)
    
    # if utss >= 0:
    #     utss = datetime(year, month, day, int(utss), int((utss * 60) % 60), int((utss * 3600 % 60)))
    # elif utss < 0:
    #     utss = utss + 24
    #     utss = datetime(year, month, day, int(utss), int((utss * 60) % 60), int((utss * 3600 % 60))) 
    #     #- timedelta(days = 1)
    
    #local rise time in UTC
    lrise = utss - timedelta(hours = ha_set / 15)  
    #local set time in UTC
    lset = utss + timedelta(hours = ha_set / 15)
    
    print('name: ', name)
    print('GMST0: ', GMST0)
    print('ra: ', ra)
    print('dec: ', dec)
    print('ha_set hours: ', ha_set/15)
    print('utss_hr: ', utss_hr)
    print('utss timestamp: ', utss)
    print('lrise timestamp: ', lrise)
    print('lset timestamp: ', lset)

    
    # print('gst- in hours is', gst0,'utss in hours is', utss, 'ha_set in degrees is', ha_set, 'lrise is', lrise, 'lset is', lset, sep='\n')
    
    return lrise, lset, ra, GMST0, utss_hr



now = datetime.utcnow()
year = now.year
month = now.month
day = now.day
UT = datetime.utcnow().hour + datetime.utcnow().minute/60 + datetime.utcnow().second/3600
day_number = find_day_number(year, month, day)
name = 'jupiter'
lat = 38.9072
lon = -77.0369

find_rise_set(lat, lon, name, day_number, UT)


# 

# ra = 5.0266
# dec = 0.4406786676497294
