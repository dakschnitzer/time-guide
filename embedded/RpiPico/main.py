from skyfield.api import load
import math
from siderial_time import siderial_time
from datetime import datetime



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

now = datetime.utcnow()
year = now.year
month = now.month
day = now.day
utc = now.hour + now.minute/60 + now.second/3600

t = ts.utc(year, month, day, utc)
astrometric = eph['earth'].at(t).observe(mars)
ra, dec, distance = astrometric.apparent().radec()
ra = ra.hours
dec = dec.degrees
print('ra is', ra, 'dec is', dec, sep='\n')


lat = 38.9072
long = -77.0369

lst = siderial_time(year, month, day, utc, long)


# ha = hour angle of star = (lst - RA)(360/24); lst = local sidereal time
ha = (lst - ra) * 15

lat = math.radians(lat)
long = math.radians(long)
dec = math.radians(dec)
ha = math.radians(ha)


# Use RA and Dec to calculate Alt and time between rising and setting at GPS location
# alt

alt= math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(ha))
alt = math.degrees(alt)
print('altitude is', alt)



