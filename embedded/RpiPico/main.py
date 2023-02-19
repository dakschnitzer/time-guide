import math
from datetime import datetime
from siderial_time import siderial_time



now = datetime.utcnow()
year = now.year
month = now.month
day = now.day
utc = now.hour + now.minute/60 + now.second/3600

lat = 38.9072
long = -77.0369

lst = siderial_time(year, month, day, utc, long)


# ha = hour angle of star = (lst - RA)(360/24); lst = local sidereal time
ha = (lst - ra) * 15.04107
print('ha hours is', ha, sep='\n')


lat = math.radians(lat)
long = math.radians(long)
dec = math.radians(dec)
ha = math.radians(ha)


# Use RA and Dec to calculate Alt and time between rising and setting at GPS location
# alt

alt= math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(ha))
alt = math.degrees(alt)
print('altitude degrees is', alt, sep='\n')

# calculate time above horizon from local coordinates
dur = 0.13333 * (180 - math.degrees(math.acos(math.tan(lat) * math.tan(dec))))
print('duration hours is', dur, sep='\n')








