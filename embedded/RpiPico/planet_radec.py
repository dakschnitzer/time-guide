import math

#define math stuff
sind = lambda x: math.sin(math.radians(x))
cosd = lambda x: math.cos(math.radians(x))
tand = lambda x: math.tan(math.radians(x))
atan2d = lambda y, x: math.degrees(math.atan2(y, x))
asind = lambda x: math.degrees(math.asin(x))
acosd = lambda x: math.degrees(math.acos(x))
pi = math.pi
sqrt = math.sqrt

def sun_rectangular(day_number):
	w = 282.9404 + 4.70935e-5 * day_number   # longitude of perihelion
	a = 1                                    # mean distance, a.u.
	e = 0.016709 - 1.151e-9 * day_number     # eccentricity
	M = 356.0470 + 0.9856002585 * day_number # mean anomaly
	M = revolve(M)
	oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic
	L = w + M				  # sun's mean longitude
	L = revolve(L)
	# sun's eccentric anomaly
	E = M + (180/pi) * e * sind(M) * (1 + e * cosd(M))
	# sun's rectrangular coordinates
	x = cosd(E) - e
	y = sind(E) * sqrt(1 - e*e)
	# convert to distance and true anomaly
	r = sqrt(x*x + y*y)
	v = atan2d(y, x)
	# sun's longitude
	lon_sun = v + w
	lon_sun = revolve(lon_sun)
	# sun's ecliptic rectangular coordinates
	x1 = r * cosd(lon_sun)
	y1 = r * sind(lon_sun)
	z1 = 0
	return x1, y1, z1, oblecl, L

def revolve(degree):
	return	degree - math.floor(degree/360)*360


def eccentric_anomaly(M, e, tol):
    e0 = M + (180/pi) * e * sind(M) * (1 + e + cosd(M))
    e1 = e0 - (e0 - (180/pi) * e * sind(e0) - M) / (1 - e * cosd(e0))
    while abs(e0-e1) > tol:
        e0 = e1
        e1 = e0 - (e0 - (180/pi) * e * sind(e0) -M) / (1 -e * cosd(e0))
    return e1

def revolve_hour_angle(hour):
	return hour - math.floor(hour/24)*24

def sun_siderial(day_number, lat, lon, UT):
    # rotate equitorial coordinates
    coords = sun_rectangular(day_number)
    xequat = coords[0]
    yequat = coords[1] * cosd(coords[3]) - coords[2] * sind(coords[3])
    zequat = coords[1] * sind(coords[3]) + coords[2] * cosd(coords[3])

    RA = atan2d(yequat, xequat)
    RA = revolve(RA) 
    # convert RA to hours
    RA = RA / 15 
    Decl = atan2d(zequat, sqrt(xequat**2 + yequat**2))
    
    # calculate GMST0     
    GMST0 = revolve(coords[4] + 180) / 15 

    # calculate SIDTIME and Hour Angle
    SIDTIME = GMST0 + UT + lon/15 
    #SIDTIME = revolve_ha(SIDTIME)
    HA = (SIDTIME - RA) * 15 

    # convert HA and Decl to rectangular system
    x2 = cosd(HA) * cosd(Decl) 
    y2 = sind(HA) * cosd(Decl) 
    z2 = sind(Decl) 

    # rotate this along the y2 axis
    xhor = x2 * sind(lat) - z2 * cosd(lat) 
    yhor = y2 
    zhor = x2 * cosd(lat) + z2 * sind(lat) 

    # finally calculate azimuth and altitude 
    azimuth = atan2d(yhor, xhor) + 180 
    altitude = atan2d(zhor, sqrt(xhor**2 + yhor**2))
    return SIDTIME, GMST0, azimuth, altitude

def sun_radec(day_number):
    # rotate equitorial coordinates
    coords = sun_rectangular(day_number)
    xequat = coords[0]
    yequat = coords[1] * cosd(coords[3]) - coords[2] * sind(coords[3])
    zequat = coords[1] * sind(coords[3]) + coords[2] * cosd(coords[3])

    RA = atan2d(yequat, xequat)
    RA = revolve(RA) 
    # convert RA to hours
    RA = RA / 15 
    Decl = atan2d(zequat, sqrt(xequat**2 + yequat**2))
    
    return RA, Decl


def moon_radec(day_number):
    N = 125.1228 - 0.0529538083 * day_number # long asc. node
    i = 5.1454                  # inclination
    w = 318.0634 + 0.1643573223 * day_number # Arg. of perigree
    a = 60.2666                  # mean distance
    e = 0.054900                  # eccentricity
    M = 115.3654 + 13.0649929509 * day_number# mean anomaly
    M = revolve(M)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic
   
    E = eccentric_anomaly(M, e, 0.0005)
    # moon's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # moon's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # convert to ecliptic longitude, latitude and distance
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip*xeclip + yeclip*yeclip))
   
    Sw = 282.9404 + 4.70935e-5   * day_number # sun's (longitude of perihelion)
    Ms = 356.0470 + 0.9856002585 * day_number # sun's mean anomaly
    Ls = Sw + Ms
    Ls = revolve(Ls)
    Lm = N + w + M
    Mm = M
    D = Lm - Ls
    F = Lm - N
   
    perturbations_in_longitude = -1.274 * sind(Mm - 2*D) +0.658 * sind(2*D) -0.186 * sind(Ms) -0.059 * sind(2*Mm - 2*D) -0.057 * sind(Mm - 2*D + Ms) +0.053 * sind(Mm + 2*D) +0.046 * sind(2*D - Ms) +0.041 * sind(Mm - Ms) -0.035 * sind(D) -0.031 * sind(Mm + Ms) -0.015 * sind(2*F - 2*D) +0.011 * sind(Mm - 4*D)
    perturbations_in_latitude = -0.173 * sind(F - 2*D) -0.055 * sind(Mm - F - 2*D) -0.046 * sind(Mm + F - 2*D) +0.033 * sind(F + 2*D) +0.017 * sind(2*Mm + F)
    perturbations_in_distance = -0.58 * cosd(Mm - 2*D) -0.46 * cosd(2*D)
    eclon = eclon + perturbations_in_longitude
    eclat = eclat + perturbations_in_latitude
    r = r + perturbations_in_distance
    x1 = cosd(eclon)*cosd(eclat)
    y1 = cosd(eclat)*sind(eclon)
    z1 = sind(eclat)
    x2 = x1
    y2 = y1 * cosd(oblecl) - z1 * sind(oblecl)
    z2 = y1 * sind(oblecl) + z1 * cosd(oblecl)
    RA = atan2d(y2,x2)
    # RA1 = RA
    RA = RA / 15
    RA = revolve_hour_angle(RA)
    Decl = atan2d(z2, sqrt(x2*x2 + y2*y2))
    
    
    # HA = (SIDTIME - RA) * 15
    # x = cosd(HA) * cosd(Decl)
    # y = sind(HA) * cosd(Decl)
    # z = sind(Decl)
    # xhor = x * sind(lat) - z * cosd(lat)
    # yhor = y
    # zhor = x * cosd(lat) + z * sind(lat)
    # az  = atan2d( yhor, xhor ) + 180
    # alt = asind( zhor )
    # mpar = asind(1/r)
    # gclat = eclat - 0.1924 * sind(2*eclat)
    # rho   = 0.99833 + 0.00167 * cosd(2*eclat)
    # g = atan2d( tand(gclat) / cosd(HA) ) 
    # topRA   = RA1  - mpar * rho * cosd(gclat) * sind(HA) / cosd(Decl)
    # topRA = revolve(topRA)
    # topDecl = Decl - mpar * rho * sind(gclat) * sind(g - Decl) / sind(g)
    #moon_data = [topRA, topDecl, az, alt]
    #moon_data = [RA, Decl, az, alt]
    return RA, Decl, eclon, eclat, r
   



def mercury_radec(day_number):
    N =  48.3313 + 3.24587e-5   * day_number   # (Long of asc. node)
    i =   7.0047 + 5.00e-8      * day_number   # (Inclination)
    w =  29.1241 + 1.01444e-5   * day_number   # (Argument of perihelion)
    a = 0.387098                               # (Semi-major axis)
    e = 0.205635 + 5.59e-10     * day_number   # (Eccentricity)
    M = 168.6562 + 4.0923344368 * day_number   # (Mean anonaly)
    M = revolve(M)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic

    E = eccentric_anomaly(M, e, 0.0005)
    # mercury's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # mercury's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA/15
    Decl = atan2d(zequat, sqrt(xequat*xequat + yequat*yequat))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip*xeclip + yeclip*yeclip))

    return RA, Decl, eclon, eclat, r, R

def venus_radec(day_number):
    N =  76.6799 + 2.46590e-5   * day_number
    i =   3.3946 + 2.75e-8      * day_number
    w =  54.8910 + 1.38374e-5   * day_number
    a = 0.723330                
    e = 0.006773     - 1.302e-9 * day_number
    M =  48.0052 + 1.6021302244 * day_number
    M = revolve(M)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic
    
    E = eccentric_anomaly(M, e, 0.0005)
    # venus's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # venus's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA/15
    Decl = atan2d(zequat, sqrt(xequat**2 + yequat**2))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip**2 + yeclip**2))
    return RA, Decl, eclon, eclat, r, R



def mars_radec(day_number):
    N =  49.5574 + 2.11081e-5   * day_number
    i =   1.8497 - 1.78e-8      * day_number
    w = 286.5016 + 2.92961e-5   * day_number
    a = 1.523688                
    e = 0.093405     + 2.516e-9 * day_number
    M =  18.6021 + 0.5240207766 * day_number
    M = revolve(M)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic

    E = eccentric_anomaly(M, e, 0.0005)
    # mars's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # mars's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA / 15
    Decl = atan2d(zequat, sqrt(xequat*xequat + yequat*yequat))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip*xeclip + yeclip*yeclip))
    return RA, Decl, eclon, eclat, r, R


def jupiter_radec(day_number):
    N = 100.4542 + 2.76854e-5   * day_number # Long of asc. node
    i =   1.3030 - 1.557e-7     * day_number # Inclination
    w = 273.8777 + 1.64505e-5   * day_number # Argument of perihelion
    a = 5.20256                 # Semi-major axis
    e = 0.048498 + 4.469e-9     * day_number # eccentricity
    M =  19.8950 + 0.0830853001 * day_number # Mean anomaly Jupiter
    M = revolve(M)
    Mj = M
    Ms = 316.9670 + 0.0334442282 * day_number # Mean anomaly Saturn
    Ms = revolve(Ms)
    Mu = 142.5905 + 0.011725806 * day_number  # Mean anomaly Uranus
    Mu = revolve(Mu)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic
    
    E = eccentric_anomaly(M, e, 0.0005)
    # jupiter's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # jupiter's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA/15
    Decl = atan2d(zequat, sqrt(xequat**2 + yequat**2))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip**2 + yeclip**2))
    perturbations_of_longitude = -0.332 * sind(2*Mj - 5*Ms - 67.6) -0.056 * sind(2*Mj - 2*Ms + 21) +0.042 * sind(3*Mj - 5*Ms + 21) -0.036 * sind(Mj - 2*Ms) +0.022 * cosd(Mj - Ms) +0.023 * sind(2*Mj - 3*Ms + 52) -0.016 * sind(Mj - 5*Ms - 69)
    eclon = eclon + perturbations_of_longitude
    eclon = revolve(eclon)
    return RA, Decl, eclon, eclat, r, R


def saturn_radec(day_number):
    N = 113.6634 + 2.38980E-5   * day_number # Long of asc. node
    i =   2.4886 - 1.081E-7     * day_number # Inclination
    w = 339.3939 + 2.97661E-5   * day_number # Argument of perihelion
    a = 9.55475                 # Semi-major axis
    e = 0.055546 - 9.499E-9     * day_number # eccentricity
    M = 316.9670 + 0.0334442282 * day_number # Mean anomaly
    M = revolve(M)
    Ms = M
    Mj = 19.8950 + 0.0830853001 * day_number # Mean anomaly Jupiter
    Mj = revolve(Mj)
    Mu = 142.5905 + 0.011725806 * day_number # Mean anomaly Uranus
    Mu = revolve(Mu)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic

    E = eccentric_anomaly(M, e, 0.0005)
    # saturn's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # saturn's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA / 15
    Decl = atan2d(zequat, sqrt(xequat*xequat + yequat*yequat))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip*xeclip + yeclip*yeclip))
    perturbations_in_longitude = 0.812 * sind(2*Mj - 5*Ms - 67.6) -0.229 * cosd(2*Mj - 4*Ms - 2) +0.119 * sind(Mj - 2*Ms - 3) +0.046 * sind(2*Mj - 6*Ms - 69) +0.014 * sind(Mj - 3*Ms + 32)
    perturbations_in_latitude = -0.020 * cosd(2*Mj - 4*Ms - 2) +0.018 * sind(2*Mj - 6*Ms - 49)
    eclon = eclon + perturbations_in_longitude
    eclon = revolve(eclon)
    eclat = eclat + perturbations_in_latitude
    eclat = revolve(eclat)
    return RA, Decl, eclon, eclat, r, R


def uranus_radec(day_number):
    N =  74.0005 + 1.3978E-5    * day_number # Long of asc. node
    i =   0.7733 + 1.9E-8       * day_number # Inclination
    w =  96.6612 + 3.0565E-5    * day_number # Argument of perihelion
    a = 19.18171 - 1.55E-8      * day_number # Semi-major axis
    e = 0.047318 + 7.45E-9      * day_number # eccentricity
    M = 142.5905 + 0.011725806  * day_number # Mean anomaly Uranus
    M = revolve(M)
    Mu = M
    Ms = 316.9670 + 0.0334442282 * day_number # Mean anomaly Saturn
    Ms = revolve(Ms)
    Mj =  19.8950 + 0.0830853001 * day_number # Mean anomaly Jupiter
    Mj = revolve(Mj)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic

    E = eccentric_anomaly(M, e, 0.0005)
    # uranus's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # uranus's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA / 15
    Decl = atan2d(zequat, sqrt(xequat**2 + yequat**2))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip) * (180/pi)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip**2 + yeclip**2))
    perturbations_in_longitude = +0.040 * sind(Ms - 2*Mu + 6) +0.035 * sind(Ms - 3*Mu + 33) -0.015 * sind(Mj - Mu + 20)
    eclon = perturbations_in_longitude + eclon
    eclon = revolve(eclon)
    return RA, Decl, eclon, eclat, r, R



def neptune_radec(day_number):
    N = 131.7806 + 3.0173E-5    * day_number
    i =   1.7700 - 2.55E-7      * day_number
    w = 272.8461 - 6.027E-6     * day_number
    a = 30.05826 + 3.313E-8     * day_number
    e = 0.008606 + 2.15E-9      * day_number
    M = 260.2471 + 0.005995147  * day_number
    M = revolve(M)
    oblecl = 23.4393 - 3.563e-7 * day_number # obliquity of the eliptic
    
    E = eccentric_anomaly(M, e, 0.0005)
    # neptune's rectrangular coordinates
    x = a * (cosd(E) - e)
    y = a * sind(E) * sqrt(1 - e*e)
    # convert to distance and true anomaly
    r = sqrt(x*x + y*y)
    v = atan2d(y, x)
    # neptune's position in ecliptic coordinates
    xeclip = r * ( cosd(N) * cosd(v+w) - sind(N) * sind(v+w) * cosd(i))
    yeclip = r * ( sind(N) * cosd(v+w) + cosd(N) * sind(v+w) * cosd(i))
    zeclip = r * sind(v+w) * sind(i)
    # add sun's rectangular coordinates
    sunr = sun_rectangular(day_number)
    xgeoc = sunr[0] + xeclip
    ygeoc = sunr[1] + yeclip
    zgeoc = sunr[2] + zeclip
    # rotate the equitorial coordinates
    xequat = xgeoc
    yequat = ygeoc * cosd(oblecl) - zgeoc * sind(oblecl)
    zequat = ygeoc * sind(oblecl) + zgeoc * cosd(oblecl)
    # convert to RA and Decl
    RA = atan2d(yequat, xequat)
    RA = revolve(RA)
    RA = RA / 15
    Decl = atan2d(zequat, sqrt(xequat*xequat + yequat*yequat))
    R = sqrt(xequat**2+yequat**2+zequat**2)
    # convert to ecliptic longitude and latitude
    eclon = atan2d(yeclip, xeclip)
    eclon = revolve(eclon)
    eclat = atan2d(zeclip, sqrt(xeclip*xeclip + yeclip*yeclip))
    return RA, Decl, eclon, eclat, r, R


