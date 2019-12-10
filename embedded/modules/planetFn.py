import gc

import ssd1306
import sh1106
import gfx
import math
import utime
import urequests as requests
from credentials import WOLFRAM_API_KEY

from machine import I2C, Pin, SPI

oled_reset_pin = Pin(16, Pin.OUT)

hspi = SPI(1, 10000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))

display1 = sh1106.SH1106_SPI(128, 64, hspi, dc=Pin(26), res=oled_reset_pin, cs=Pin(5))
display2 = sh1106.SH1106_SPI(128, 64, hspi, dc=Pin(33), res=oled_reset_pin, cs=Pin(2))

utime.sleep(1)

display1.sleep(False)
display1.rotate(1)
display2.sleep(False)
display2.rotate(1)
utime.sleep(1)

i2c = I2C(scl=Pin(15), sda=Pin(4))

oled = ssd1306.SSD1306_I2C(128, 64, i2c)
utime.sleep(1)

graphics = gfx.GFX(128, 64, oled.pixel)
graphics1 = gfx.GFX(128, 64, display1.pixel)
graphics2 = gfx.GFX(128, 64, display2.pixel)

names = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

def orbitTracker(name):
    # earth heliocentric longitude
    url = "http://api.wolframalpha.com/v1/result?i=earth%20heliocentric%20longitude%3F&appid={0}".format(WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    elong = [x.strip() for x in r.text.split(',')]
    elong = [x.strip() for x in elong[0].split()]
    elong = elong[0]
    r.close()
    del r
    print(elong)
    elong = float(elong)
    elong = math.radians(elong)

    #oled stuff
    display1.fill(0)
    display1.text("getting:", 0, 0)
    display1.text(name, 0, 10)
    display1.show()
    display2.fill(0)
    display2.show()
    utime.sleep(1)

    # heliocentric longitude
    url = "http://api.wolframalpha.com/v1/result?i={0}%20heliocentric%20longitude%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    long = [x.strip() for x in r.text.split(',')]
    long = [x.strip() for x in long[0].split()]
    long = long[0]
    r.close()
    del r
    print(long)
    long = float(long)

    # perihelion data
    url = "http://api.wolframalpha.com/v1/result?i={0}%20next%20periapsis%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    years = r.text
    years = [x.strip() for x in years.split()]
    years = years[0][:3] + " " + years[1] + " " + years[2]
    r.close()
    del r
    gc.collect()

    # heliocentric longitude @ next perihelion
    url = "http://api.wolframalpha.com/v1/result?i={0}%20heliocentric%20longitude%20at%20next%20perihelion%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    longp = [x.strip() for x in r.text.split(',')]
    longp = [x.strip() for x in longp[0].split()]
    longp = longp[0]
    r.close()
    del r
    print(longp)
    longp = float(longp)

    # distance from earth
    url = "http://api.wolframalpha.com/v1/result?i={0}%20distance%20from%20earth%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    dist = [x.strip() for x in r.text.split(',')]
    dist = [x.strip() for x in dist[0].split()]
    dist = dist[1]
    r.close()
    del r
    gc.collect()
    print(dist)
    dist = float(dist)

    #periods of planets without earth (hard coded)
    period = [0.2408467, 0.615197, 1.8808476, 11.862615, 29.447498, 84.016846, 164.79132]


    #oled stuff
    display1.fill(0)
    display1.text(name, 0, 0)
    display1.text("acquired!", 0, 10)
    display1.show()
    utime.sleep(1)

    # create log scale of sizes of planets
    arb = 0.9
    pre = [1, 2.48, 2.61, 1.39, 28.66, 23.9, 10.4, 10.1]
    pre.insert(0, arb)
    scale = 3.5
    pre = [scale * math.log(x/pre[0],10) for x in pre]
    pre.pop(0)
    pre = [int(math.ceil(x)) for x in pre]

    # size of planets without earth
    pr = list.copy(pre)
    pr.pop(2)

    # create log scale of distances of planets from sun
    arb = 0.2
    sdist_i = [0.466, 0.72, 1.02, 1.66, 5.29, 10, 19.8, 29.9]
    sdist_i.insert(0, arb)
    scale = 57
    sdist_i = [scale * math.log(x/sdist_i[0],10) - 1 for x in sdist_i]
    sdist_i.pop(0)
    sdist_i = [int(math.ceil(x)) for x in sdist_i]

    # distances of planets from sun without earth
    pxc = list.copy(sdist_i)
    pxc.pop(2)

    # graphics on display
    display1.fill(0)
    display2.fill(0)

    # calculate progress towards perihelion
    # orbit progress circle dims
    xc = 94
    yc = 31
    rad = int(pxc[names.index(name)]/4)

    #draw orbit progress circle outline
    graphics2.circle(xc, yc, rad, 1)

    #calculate orbit progress in radians
    p_rad = math.radians(long)
    print(p_rad)

    #calculate x,y position of planet in heliocentric coordinates relative to xc,yc
    xp = int(round(rad * math.cos(p_rad),0))
    yp = int(round(rad * math.sin(p_rad),0))

    #draw rectangle blocks and planet marker
    xblock = int(math.fabs(xp))

    # top-right
    if p_rad <= math.pi/2:
        #fill bottom half of circle
        graphics2.fill_rect(xc - rad, yc, 2 * rad + 1, rad + 1, 0)
        #fill top left of circle
        graphics2.fill_rect(xc - rad, yc - rad, rad + 1, rad + 1, 0)
        #partial fill top right of circle
        graphics2.fill_rect(xc, yc - rad, xblock + 1, rad + 1, 0)

    # top-left
    elif p_rad >= math.pi/2 and p_rad <= math.pi:
       #fill bottom half of circle
        graphics2.fill_rect(xc - rad, yc, 2 * rad + 1, rad + 1, 0)
        #partial fill top left of circle
        graphics2.fill_rect(xc - rad, yc - rad, rad - xblock, rad + 1, 0)

    # bottom left
    elif p_rad >= math.pi and p_rad <= 3 * math.pi/2:
       #fill bottom right of circle
        graphics2.fill_rect(xc, yc, rad + 1, rad + 1, 0)
        #partial fill bottom left of circle
        graphics2.fill_rect(xc - xblock, yc, xblock + 1, rad + 1, 0)

    # bottom-right
    else:
        #partial fill bottom right of circle
        graphics2.fill_rect(xc + xblock, yc, rad - xblock + 1, rad + 1, 0)

    # plot planet marker
    graphics2.circle(xc + xp, yc - yp, pr[names.index(name)], 1)
    graphics2.fill_circle(xc + xp, yc - yp, 1, 1)

    # plot earth
    xe = int(round((sdist_i[2]/4) * math.cos(elong),0))
    ye = int(round((sdist_i[2]/4) * math.sin(elong),0))
    graphics2.circle(xc + xe, yc - ye, 1, 1)

#        # plot earth - planet distance
#        display.line(xc + xp, yc + yp, xc + xe, yc + ye, 1)

    # make sun
    graphics2.fill_circle(xc, yc, 2, 1)

    # show perihelion location
    longp = math.radians(longp)
    xpp = int((rad) * math.cos(longp))
    ypp = int((rad) * math.sin(longp))
    graphics2.line(xc, yc, xc + xpp, yc - ypp, 1)

    display2.text(name, 0, 0)
    display2.show()


    # show data on display1
    display1.text(name, 0, 0)
    display1.text('Heliocent. long.: ',0,15)
    display1.text(str(int(long)),0,25)
    display1.text('D to Earth (AU): ',0,38)
    display1.text(str(round(dist,1)),0,48)

    display1.show()
    utime.sleep(10)

    display1.fill(0)
    display1.text(name, 0, 0)
    display1.text('Next perihelion:',0,15)
    display1.text(years,0,25)
    display1.text('Orbital pd (yr):',0,38)
    display1.text(str(round(period[names.index(name)],1)),0,48)
    display1.show()

    gc.collect()


def skyChart(name):

    #oled stuff
    display1.fill(0)
    display1.text("getting:", 0, 0)
    display1.text(name, 0, 10)
    display1.show()
    display2.fill(0)
    display2.show()
    utime.sleep(1)

    # obtain planet above horizon from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20above%20horizon%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    visible = [x.strip() for x in r.text.split(',')]
    visible = visible[0]
    print(visible)
    r.close()
    del r
    gc.collect()

    # sky chart data
    # obtain current planet azimuth from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20azimuth%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    azc = [x.strip() for x in r.text.split(',')]
    azc = [x.strip() for x in azc[0].split()]
    azc = azc[0]
    azc = float(azc)
    print(azc)
    r.close()
    del r
    gc.collect()

    # obtain current planet altitude from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20altitude%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    alc = [x.strip() for x in r.text.split(',')]
    alc = [x.strip() for x in alc[0].split()]
    alc = alc[0]
    alc = float(alc)
    print(alc)
    r.close()
    del r
    gc.collect()

    #oled stuff
    display1.fill(0)
    display1.text(name, 0, 0)
    display1.text("acquired!", 0, 10)
    display1.show()
    utime.sleep(1)

    # display stuff
    display1.fill(0)
    display2.fill(0)

    display1.text(name, 0, 0)
    display1.text("Visible:", 0,10)
    display1.text(visible, 80,10)
    display1.show()

    # show planet altitude
    if visible == 'Yes':
        display1.text("Altitude:", 0, 20)
        display1.text(str(round(alc)), 80, 20)
        graphics1.line(48, 63, 78, 63, 1)
        y = 30 * math.sin(math.radians(alc))
        y = int(round(y,0))
        graphics1.line(48, 63, 78, 63 - y, 1)
        display1.text(str(round(alc)), 82, 60 - y)

    # show planet azimuth
    xc = 63
    yc = 46
    rad = 17
    display2.text("Azimuth:", 0, 10)
    display2.text(str(round(azc)), 80, 10)
    display2.text("N", xc - 3, 20)
    graphics2.circle(xc, yc, rad, 1)
    x = rad * math.cos(math.radians(azc - 90))
    x = round(x,0)
    y = rad * math.sin(math.radians(azc - 90))
    y = round(y,0)
    display2.line(xc, yc, int(xc + x), int(yc + y), 1)

    display1.show()
    display2.show()

    gc.collect()

def skyLocation(name):
    #oled stuff
    display1.fill(0)
    display1.text("getting:", 0, 0)
    display1.text(name, 0, 10)
    display1.show()
    display2.fill(0)
    display2.show()
    utime.sleep(1)

    # obtain planet above horizon from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20above%20horizon%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    visible = [x.strip() for x in r.text.split(',')]
    visible = visible[0]
    print(visible)
    r.close()
    del r
    gc.collect()

    # sky chart data
    # obtain current planet azimuth from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20azimuth%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    azc = [x.strip() for x in r.text.split(',')]
    azc = [x.strip() for x in azc[0].split()]
    azc = azc[0]
    azc = float(azc)
    print(azc)
    r.close()
    del r
    gc.collect()


    # obtain planet azimuth rise from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20azimuth%20rise%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    azr = [x.strip() for x in r.text.split(',')]
    azr = [x.strip() for x in azr[0].split()]
    azr = azr[0]
    azr = float(azr)
    print(azr)
    r.close()
    del r
    gc.collect()


    # obtain planet azimuth set from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20azimuth%20set%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    azs = [x.strip() for x in r.text.split(',')]
    azs = [x.strip() for x in azs[0].split()]
    azs = azs[0]
    azs = float(azs)
    print(azs)
    r.close()
    del r
    gc.collect()


    # obtain planet azimuth at maximum altitude from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20azimuth%20at%20time%20of%20maximum%20altitude%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    azm = [x.strip() for x in r.text.split(',')]
    azm = [x.strip() for x in azm[0].split()]
    azm = azm[0]
    azm = float(azm)
    print(azm)
    r.close()
    del r
    gc.collect()


    # obtain current planet altitude from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20altitude%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    alc = [x.strip() for x in r.text.split(',')]
    alc = [x.strip() for x in alc[0].split()]
    alc = alc[0]
    alc = float(alc)
    print(alc)
    r.close()
    del r
    gc.collect()


    # obtain max planet altitude from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20maximum%20altitude%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    alm = [x.strip() for x in r.text.split(',')]
    alm = [x.strip() for x in alm[0].split()]
    alm = alm[0]
    alm = float(alm)
    print(alm)
    r.close()
    del r
    gc.collect()


    #oled stuff
    display1.fill(0)
    display1.text(name, 0, 0)
    display1.text("acquired!", 0, 10)
    display1.show()
    utime.sleep(1)

    # display stuff
    display1.fill(0)
    display2.fill(0)

    display1.text(name, 0, 0)
    display1.text("Visible:", 0,10)
    display1.text(visible, 80,10)
    display1.show()

    # sky chart
    xc = 63
    yc = 31
    rad = 29

    # calculate planet rise azimuth
    x = int(round(rad * math.cos(math.radians(azr - 90)),0))
    y = int(round(rad * math.sin(math.radians(azr - 90)),0))
    xr = xc + x
    yr = yc + y

    # calculate planet set azimuth
    x = int(round(rad * math.cos(math.radians(azs - 90)),0))
    y = int(round(rad * math.sin(math.radians(azs - 90)),0))
    xs = xc + x
    ys = yc + y

    # calculate location at maximum altitude
    rd = int(round(rad * (90 - alm)/90,0))
    x = int(round(rd * math.cos(math.radians(azm - 90)),0))
    y = int(round(rd * math.sin(math.radians(azm - 90)),0))
    xm = xc + x
    ym = yc + y

    # calculate current location if visible
    if visible == 'Yes':
        rd = int(round(rad * (90 - alc)/90,0))
        x = int(round(rd * math.cos(math.radians(azc - 90)),0))
        y = int(round(rd * math.sin(math.radians(azc - 90)),0))
        xcu = xc + x
        ycu = yc + y

    # find coefficients for path of transit
    A = [[xr ** 2, xr, 1], [xm ** 2, xm, 1], [xs ** 2, xs, 1]]
    B = [63 - yr, 63 - ym, 63 - ys]

    detA = (A[0][0]*A[1][1]*A[2][2] + A[0][1]*A[1][2]*A[2][0] + A[0][2]*A[1][0]*A[2][1] - A[0][2]*A[1][1]*A[2][0] - A[0][1]*A[1][0]*A[2][2] - A[0][0]*A[1][2]*A[2][1])


    invA = [[(A[1][1]*A[2][2] - A[1][2]*A[2][1])/detA, -(A[0][1]*A[2][2] - A[0][2]*A[2][1])/detA, (A[0][1]*A[1][2] - A[0][2]*A[1][1])/detA],
             [-(A[1][0]*A[2][2] - A[1][2]*A[2][0])/detA, (A[0][0]*A[2][2] - A[0][2]*A[2][0])/detA, -(A[0][0]*A[1][2] - A[0][2]*A[1][0])/detA],
             [(A[1][0]*A[2][1] - A[1][1]*A[2][0])/detA, -(A[0][0]*A[2][1] - A[0][1]*A[2][0])/detA, (A[0][0]*A[1][1] - A[0][1]*A[1][0])/detA]]

    X = [invA[0][0]*B[0] + invA[0][1]*B[1] + invA[0][2]*B[2],
         invA[1][0]*B[0] + invA[1][1]*B[1] + invA[1][2]*B[2],
         invA[2][0]*B[0] + invA[2][1]*B[1] + invA[2][2]*B[2]]

    # show location of rise, set, maximum altitude, and current location if visible on horizon circle
    graphics2.circle(xc, yc, rad, 1)
    graphics2.fill_circle(xr, yr, 2, 1)
    graphics2.fill_circle(xs, ys, 2, 1)
    graphics2.fill_circle(xm, ym, 2, 1)
    if visible == 'Yes':
        graphics2.circle(xcu, ycu, 2, 1)

    # show path of transit
    xt = [0] * (xr-xs)
    yt = [0] * (xr-xs)
    for i in range(xr - xs):
        xt = xs + i
        yt = int((X[0] * xt ** 2) + (X[1] * xt) + X[2])
        display2.pixel(xt, 63 - yt, 1)

    display1.show()
    display2.show()

    gc.collect()