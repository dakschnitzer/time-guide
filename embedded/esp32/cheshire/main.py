import gc

import ssd1306
import sh1106
import gfx
import math
import utime
import network
import urequests as requests
#from rotary_irq_esp import RotaryIRQ
import urandom as random
from credentials import WIFI_SSID, WIFI_PASSWORD, WOLFRAM_API_KEY

from machine import I2C, Pin, SPI

button = Pin(27, Pin.IN, Pin.PULL_UP)

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

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
#            wdt.feed()
            pass
    print('network config:', wlan.ifconfig())

do_connect()
gc.collect()

oled.fill(0)
oled.text('wifi connected',0,0,1)
oled.show()
utime.sleep(1)

utime.sleep(1)

oled.fill(0)
display1.fill(0)
display2.fill(0)

oled.show()
display1.show()
display2.show()

names = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']


def orbitTracker(name):
    #orbit data
    # pre-allocate list values from 12/8/2019
    long_i = [193.0, 327.0, 203.0, 274.0, 291.0, 35.0, 347.0]

    # get fresh heliocentric longitude data
    url = "http://api.wolframalpha.com/v1/result?i={0}%20heliocentric%20longitude%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    long = [x.strip() for x in r.text.split(',')]
    long = [x.strip() for x in long[0].split()]
    long = long[0]
    r.close()
    del r
    print(long)
    # save planet data to list
    long_i[index] = float(long)

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

    # show planet index graphic as circles
    # orbit progress circle dims
    xc = 63
    yc = 31
    rad_i = [int(x/4) for x in pxc]
    p_rad = [math.radians(x) for x in long_i]
    xp = [int(round(a * math.cos(b))) for a,b in zip(rad_i,p_rad)]
    yp = [int(round(a * math.sin(b))) for a,b in zip(rad_i,p_rad)]

    #draw orbit progress circle outline
    graphics1.circle(xc, yc, rad_i[index], 1)
    graphics1.circle(xc + xp[index], yc - yp[index], pr[index], 1)
    graphics1.fill_circle(xc + xp[index], yc - yp[index], 1, 1)


def orbitData1(name):
    # pre-allocate list values from 12/8/2019
    dist_i = [1.22, 1.4, 2.34, 6.18, 10.9, 19.1, 29.9]
    long_i = [193.0, 327.0, 203.0, 274.0, 291.0, 35.0, 347.0]

    # get fresh orbit data
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
    # save planet data to list
    long_i[index] = float(long)

    # distance from earth
    url = "http://api.wolframalpha.com/v1/result?i={0}%20distance%20from%20earth%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    dist = [x.strip() for x in r.text.split(',')]
    dist = [x.strip() for x in dist[0].split()]
    dist = dist[1]
    r.close()
    del r
    print(dist)
    # save planet data to list
    dist_i[index] = float(dist)

    # show data on display2
    display2.text('Heliocent. long.: ',0,15)
    display2.text(str(long_i[index]),0,25)
    display2.text('D to Earth (AU): ',0,38)
    display2.text(str(round(dist_i[index],1)),0,48)


def orbitData2(name):
    #periods of planets without earth
    period = [0.2408467, 0.615197, 1.8808476, 11.862615, 29.447498, 84.016846, 164.79132]
    # pre-allocate list values from 12/8/2019
    years_i = ['Feb 12, 2020', 'Mar 19, 2020', 'Aug 3, 2020', 'Jan 24, 2023', 'Dec 24, 2032', 'Feb 10, 2051', 'Jul 16, 2047']

    # perihelion date
    url = "http://api.wolframalpha.com/v1/result?i={0}%20next%20periapsis%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    years = r.text
    years = [x.strip() for x in years.split()]
    years = years[0][:3] + " " + years[1] + " " + years[2]
    r.close()
    del r
    gc.collect()
    # save planet data to list
    years_i[index] = years

    display2.text('Next perihelion:',0,15)
    display2.text(years_i[index],0,25)
    display2.text('Orbital pd (yr):',0,38)
    display2.text(str(round(period[index],1)),0,48)


def skyLocation(name):
    # pre-allocate list values from 12/8/2019
    visible_i = ['No', 'No', 'No', 'No', 'No', 'Yes', 'Yes']
    azc_i = [306.0, 259.0, 342.0, 269.0, 259.0, 184.0, 233.0]
    azr_i = [114.0, 121.0, 109.0, 120.0, 118.0, 73.0, 97.0]
    azs_i = [245.0, 239.0, 250.0, 239.0, 241.0, 286.0, 262.0]
    azm_i = [180.0, 179.0, 179.0, 179.0, 180.0, 179.0, 179.0]
    alc_i = [60.0, 26.0, 65.0, 38.0, 23.0, 63.0, 27.0]
    alm_i = [32.0, 26.0, 35.0, 27.0, 29.0, 63.0, 44.0]

    # get fresh sky chart data
    # obtain planet above horizon from wolframalpha API
    url = "http://api.wolframalpha.com/v1/result?i={0}%20above%20horizon%3F&appid={1}".format(name, WOLFRAM_API_KEY)
    r = requests.get(url)
    print(r.text)
    visible = [x.strip() for x in r.text.split(',')]
    visible = visible[0]
    print(visible)
    r.close()
    del r
    visible_i[index] = visible
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
    azc_i[index] = azc
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
    azr_i[index] = azr
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
    azs_i[index] = azs
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
    azm_i[index] = azm
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
    alc_i[index] = alc
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
    alm_i[index] = alm
    gc.collect()


    xc = 63
    yc = 31
    rad = 29

    # calculate planet rise azimuth
    x = int(round(rad * math.cos(math.radians(azr_i[index] - 90)),0))
    y = int(round(rad * math.sin(math.radians(azr_i[index] - 90)),0))
    xr = xc + x
    yr = yc + y

    # calculate planet set azimuth
    x = int(round(rad * math.cos(math.radians(azs_i[index] - 90)),0))
    y = int(round(rad * math.sin(math.radians(azs_i[index] - 90)),0))
    xs = xc + x
    ys = yc + y

    # calculate location at maximum altitude
    rd = int(round(rad * (90 - alm_i[index])/90,0))
    x = int(round(rd * math.cos(math.radians(azm_i[index] - 90)),0))
    y = int(round(rd * math.sin(math.radians(azm_i[index] - 90)),0))
    xm = xc + x
    ym = yc + y

    # calculate current location if visible
    if visible_i[index] == 'Yes':
        rd = int(round(rad * (90 - alc_i[index])/90,0))
        x = int(round(rd * math.cos(math.radians(azc_i[index] - 90)),0))
        y = int(round(rd * math.sin(math.radians(azc_i[index] - 90)),0))
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
    graphics1.circle(xc, yc, rad, 1)
    graphics1.fill_circle(xr, yr, 2, 1)
    graphics1.fill_circle(xs, ys, 2, 1)
    graphics1.fill_circle(xm, ym, 2, 1)
    if visible_i[index] == 'Yes':
        graphics1.circle(xcu, ycu, 2, 1)

    # show path of transit
    xt = [0] * (xr-xs)
    yt = [0] * (xr-xs)
    for i in range(xr - xs):
        xt = xs + i
        yt = int((X[0] * xt ** 2) + (X[1] * xt) + X[2])
        display1.pixel(xt, 63 - yt, 1)


def skyLocGraph(name):
    visible_i = ['No', 'No', 'No', 'No', 'No', 'Yes', 'Yes']
    azc_i = [306.0, 259.0, 342.0, 269.0, 259.0, 184.0, 233.0]
    alc_i = [60.0, 26.0, 65.0, 38.0, 23.0, 63.0, 27.0]

    display2.text("Visible:", 0, 0)
    display2.text(visible_i[index], 64, 0)

    # show planet altitude
    if visible_i[index] == 'Yes':
        display2.text("Alt.:", 0, 20)
        display2.text(str(round(alc_i[index])), 40, 20)
        graphics2.line(8, 63, 38, 63, 1)
        y = 30 * math.sin(math.radians(alc_i[index]))
        y = int(round(y,0))
        graphics2.line(8, 63, 38, 63 - y, 1)

    # show planet azimuth
    xc = 95
    yc = 46
    rad = 17

    display2.text("Az.:", 68, 10)
    display2.text(str(round(azc_i[index])), 98, 10)
    display2.text("N", xc - 3, 20)
    graphics2.circle(xc, yc, rad, 1)
    x = rad * math.cos(math.radians(azc_i[index] - 90))
    x = round(x,0)
    y = rad * math.sin(math.radians(azc_i[index] - 90))
    y = round(y,0)
    display2.line(xc, yc, int(xc + x), int(yc + y), 1)


def initStar(i):
    if random.getrandbits(1) == 0:
        sign = 1
    else:
        sign = -1

    star_x[i] = int(100 * sign * random.getrandbits(9)/512)

    if random.getrandbits(1) == 0:
        sign = 1
    else:
        sign = -1

    star_y[i] = int(50 * sign * random.getrandbits(9)/512)

    star_z[i] = 100 + int(400 * random.getrandbits(9)/512)


def showStarfield():
    for i in range(stars):

        star_z[i] = star_z[i] - 10

        if star_z[i] < 1:
            initStar(i)

        x = int(star_x[i] / star_z[i] * 100 + xc)
        y = int(star_y[i] / star_z[i] * 100 + yc)

        if x < 0 or y < 0 or x > 127 or y > 63:
            initStar(i)

        oled.pixel(x, y, 1)
        display1.pixel(x, y, 1)
        display2.pixel(x, y, 1)

    oled.show()
    display1.show()
    display2.show()


#starfield
stars = 500
star_x = list(range(stars))
star_y = list(range(stars))
star_z = list(range(stars))

xc = 63;
yc = 31;

for i in range(stars):
    initStar(i)

while True:
    oled.fill(0)
    display1.fill(0)
    display2.fill(0)

    showStarfield()

    if not button.value():
        # get earth heliocentric longitude
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

        # plot earth
        xc = 63
        yc = 31
        xe = int(round((40/4) * math.cos(elong),0))
        ye = int(round((40/4) * math.sin(elong),0))

        #oled display Earth name
        oled.fill(0)
        oled.text('Earth', 0, 0)

        #display1 display Earth
        display1.fill(0)
        graphics1.circle(xc + xe, yc - ye, 1, 1)

        #display2 display text
        display2.fill(0)
        display2.text('You are here.',0,0)

        oled.show()
        display1.show()
        display2.show()
        utime.sleep(4)

        display2.fill(0)
        display2.show()
        utime.sleep(2)

        display2.text('This is the',0,0)
        display2.text('current',0,12)
        display2.text('configuration of',0,24)
        display2.text('our Solar System.',0,36)
        display2.show()

        #call function in loop for overlay of Orbits
        for index, name in enumerate(names):
            oled.fill(0)
            orbitTracker(name)
            oled.text(name, 0, 0)
            oled.show()
            display1.show()
            utime.sleep(2)

        oled.fill(0)
        display1.fill(0)
        display2.fill(0)

        oled.show()
        display1.show()
        display2.show()

        utime.sleep(2)

        display2.text('This is some',0,0)
        display2.text('information',0,12)
        display2.text('about where the',0,24)
        display2.text('planets are now.',0,36)
        display2.show()

        utime.sleep(4)

        display2.fill(0)
        display2.show()

        #call orbit function in loop for each individual planet
        for index, name in enumerate(names):
            oled.fill(0)
            oled.text(name, 0, 0)
            oled.show()

            orbitTracker(name)
            # show earth on display 1
            graphics1.circle(xc + xe, yc - ye, 1, 1)
            orbitData1(name)

            display1.show()
            display2.show()
            utime.sleep(2)

            display2.fill(0)
            orbitData2(name)
            display2.show()
            utime.sleep(2)

            display1.fill(0)
            display2.fill(0)
            display1.show()
            display2.show()


        oled.fill(0)
        display1.fill(0)
        display2.fill(0)

        oled.show()
        display1.show()
        display2.show()

        utime.sleep(2)

        display2.text('This is our sky',0,0)
        display2.text('from here.',0,12)

        xc = 63
        yc = 31
        rad = 29
        graphics1.circle(xc, yc, rad, 1)

        display1.show()
        display2.show()

        utime.sleep(4)

        display2.fill(0)
        display2.show()

        #call skychart function in loop for overlay
        display2.text('This is the',0,0)
        display2.text('transit of each',0,15)
        display2.text('planet across',0,30)
        display2.text('our sky today.',0,45)
        display2.show()

        for index, name in enumerate(names):
            oled.fill(0)
            oled.text('Aquiring transit:', 0, 0)
            oled.text(name, 0, 12)
            oled.show()
            skyLocation(name)

            oled.fill(0)
            oled.text(name, 0, 0)
            oled.show()

            display1.show()

        utime.sleep(5)

        oled.fill(0)
        display1.fill(0)
        display2.fill(0)

        oled.show()
        display1.show()
        display2.show()

        utime.sleep(2)

        display2.text('Not that it',0,0)
        display2.text('matters, but not',0,12)
        display2.text('all the planets',0,24)
        display2.text('are visible now.',0,36)
        display2.show()

        utime.sleep(4)

        display2.fill(0)
        display2.show()

        #call SkyLocation function in loop for each individual planet
        for index, name in enumerate(names):
            oled.fill(0)
            oled.text('Aquiring transit:', 0, 0)
            oled.text(name, 0, 12)
            oled.show()
            skyLocation(name)
            skyLocGraph(name)

            oled.fill(0)
            oled.text(name, 0, 0)
            oled.show()

            display1.show()
            display2.show()

            utime.sleep(4)

            display1.fill(0)
            display2.fill(0)
            display1.show()
            display2.show()

        oled.fill(0)
        display1.fill(0)
        display2.fill(0)

        oled.show()
        display1.show()
        display2.show()

        utime.sleep(2)


        # art text
        display1.text('We will never',0,0)
        display1.text('have an all-',0,12)
        display1.text('watching eye',0,24)
        display1.text('over the',0,36)
        display1.text('Cosmos.',0,48)

        display1.show()
        utime.sleep(5)

        display1.fill(0)
        display1.show()
        utime.sleep(2)


        display1.text('Watching the sky',0,0)
        display1.text('was always',0,12)
        display1.text('fundamental to',0,24)
        display1.text('humanity.',0,36)

        display1.show()
        utime.sleep(5)

        display1.fill(0)
        display1.show()
        utime.sleep(2)

        display2.text('Someday we might',0,0)
        display2.text('keep watch over',0,12)
        display2.text('the Solar System',0,24)
        display2.text('; an act of',0,36)
        display2.text('mass surveilance.',0,48)

        display2.show()
        utime.sleep(5)

        display1.fill(0)
        display2.fill(0)

        display1.show()
        display2.show()

        utime.sleep(4)
