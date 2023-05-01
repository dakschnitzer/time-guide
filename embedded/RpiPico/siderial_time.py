def julian_date(year, month, day, utc=0):
    """
    Returns the Julian date, number of days since 1 January 4713 BC 12:00.
    utc is UTC in decimal hours. If utc=0, returns the date at 12:00 UTC.
    """
    if month > 2:
        y = year
        m = month
    else:
        y = year - 1
        m = month + 12
    d = day
    h = utc/24
    if year <= 1582 and month <= 10 and day <= 4:
        # Julian calendar
        b = 0
    elif year == 1582 and month == 10 and day > 4 and day < 15:
        # Gregorian calendar reform: 10 days (5 to 14 October 1582) were skipped.
        # In 1582 after 4 October follows the 15 October.
        d = 15
        b = -10
    else:
        # Gregorian Calendar
        a = int(y/100)
        b = 2 - a + int(a/4)
    jd = int(365.25*(y+4716)) + int(30.6001*(m+1)) + d + h + b - 1524.5
    return(jd)


def siderial_time(year, month, day, utc, lon):
    """
    Returns the siderial time in decimal hours. Longitude (long) is in 
    decimal degrees. If long=0, return value is Greenwich Mean Siderial Time 
    (GMST).
    """
    jd = julian_date(year, month, day)
    t = (jd - 2451545.0)/36525
    # Greenwich siderial time at 0h UTC (hours)
    gst0 = (24110.54841 + 8640184.812866 * t +
          0.093104 * t**2 - 0.0000062 * t**3) / 3600
    # Greenwich siderial time at given UTC
    gst = gst0 + 1.00273790935*utc
    gst0 = gst0 % 24
    # Local siderial time at given UTC (longitude in degrees)
    lst = gst + lon/15
    lst = lst % 24
    return(lst, gst0)