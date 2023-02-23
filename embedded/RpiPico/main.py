import math
from datetime import datetime, timedelta
from siderial_time import siderial_time


def find_alt(lat, lon, year, month, day, utc, ra, dec):
    #this function returns body altitude by calculating the local siderial time from longitude and the "hour angle" from LST and right ascension
    #utc variable is just UTC decimal hours (utc hour + minute/60 + second/3600)
    lst = siderial_time(year, month, day, utc, lon)[0]
    
    # ha = hour angle of star in degrees = (lst - RA)(360/24); lst = local sidereal time 
    ha = (lst - ra) * 15
    print('ha in degrees is', ha, sep='\n')
    
    lat = math.radians(lat)
    lon = math.radians(lon)
    dec = math.radians(dec)
    ha = math.radians(ha)
    
    # Use RA and Dec to calculate Alt and time between rising and setting at GPS location
    
    alt= math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(ha))
    alt = math.degrees(alt)
    print('altitude degrees is', alt, sep='\n')
    return(alt)

def find_dur(lat, year, month, day, utc, dec):
    #this function returns body duration above horizon from observer latitude and body declination
    # calculate time above horizon from local coordinates
    dur = 0.13333 * (180 - math.degrees(math.acos(math.tan(lat) * math.tan(dec))))
    print('duration hours is', dur, sep='\n')
    return(dur)


def find_rise_set(lat, lon, year, month, day, hour, minute, second, ra, dec):
    #find greenwich siderial time at midnight
    gst0 = siderial_time(year, month, day, hour + minute/60 + second/3600, lon)[1]
    lat = math.radians(lat)
    dec = math.radians(dec)
    
    #find hour angle of body when altitude = 0
    ha_set = math.acos((-math.sin(lat) * math.sin(dec)) / (math.cos(lat) * math.cos(dec)))
    ha_set = math.degrees(ha_set)
    #calculate UT of sun in south - can't figure out if a negative number means it's day before or day after.
    utss = (ra * 15 - gst0 * 15 - lon) / 15.0417
    if utss >= 0:
        utss = datetime(year, month, day, int(utss), int((utss * 60) % 60), int((utss * 3600 % 60)))
    elif utss < 0:
        utss = utss + 24
        utss = datetime(year, month, day, int(utss), int((utss * 60) % 60), int((utss * 3600 % 60))) - timedelta(days = 1)
    
    
    #local rise time in UTC
    lrise = utss - timedelta(hours = ha_set / 15)  
    #local set time in UTC
    lset = utss + timedelta(hours = ha_set / 15)
    
    
    print('gst- in hours is', gst0,'utss in hours is', utss, 'ha_set in degrees is', ha_set, 'lrise is', lrise, 'lset is', lset, sep='\n')
    
    return lrise, lset


now = datetime.utcnow()
year = now.year
month = now.month
day = now.day


lat = 38.9072
lon = -77.0369

ra = 5.0266
dec = 0.4406786676497294
