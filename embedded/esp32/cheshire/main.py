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

class Wolfram(object):

    _results = {}

    def __init__(self, api_key):
        self.api_key = api_key

    def get_data(self, planet, parameter):
        """Parse the text result from the wolframalpha api."""

        query = "{0} {1}".format(name, parameter)
        query = query.replace(" ", "+")

        # cache the results locally so next time we dont hit the api
        if query in self._results:
            return self._results[query]

        url = "http://api.wolframalpha.com/v1/result?i={0}&appid={1}".format(
            query,
            self.api_key
        )

        r = requests.get(url)
        value = r.text.split(' ')[0]

        try:
            # if its a number, turn it into a float
            value = float(value)
        except:
            # if turning it into a float failed, make sure there is no "," in there
            value = value.replace(",", "")

        # save the value to the cache for next time
        self._results[query] = value

        r.close()
        del r
        gc.collect()
        return value

def orbitTracker(name):
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
    p_rad = [math.radians(x) for x in long]
    xp = [int(round(a * math.cos(b))) for a,b in zip(rad_i,p_rad)]
    yp = [int(round(a * math.sin(b))) for a,b in zip(rad_i,p_rad)]

    #draw orbit progress circle outline
    graphics1.circle(xc, yc, rad_i[index], 1)
    graphics1.circle(xc + xp[index], yc - yp[index], pr[index], 1)
    graphics1.fill_circle(xc + xp[index], yc - yp[index], 1, 1)


def orbitData1(name):
    # show data on display2
    display2.text('Heliocent. long.: ',0,15)
    display2.text(str(long[index]),0,25)
    display2.text('D to Earth (AU): ',0,38)
    display2.text(str(round(dist[index],1)),0,48)


def orbitData2(name):
    display2.text('Next perihelion:',0,15)
    display2.text(years[index],0,25)
    display2.text('Orbital pd (yr):',0,38)
    display2.text(str(round(period[index],1)),0,48)




def skyLocation(name):
    xc = 63
    yc = 31
    rad = 29

    # calculate planet rise azimuth
    x = int(round(rad * math.cos(math.radians(azr[index] - 90)),0))
    y = int(round(rad * math.sin(math.radians(azr[index] - 90)),0))
    xr = xc + x
    yr = yc + y

    # calculate planet set azimuth
    x = int(round(rad * math.cos(math.radians(azs[index] - 90)),0))
    y = int(round(rad * math.sin(math.radians(azs[index] - 90)),0))
    xs = xc + x
    ys = yc + y

    # calculate location at maximum altitude
    rd = int(round(rad * (90 - alm[index])/90,0))
    x = int(round(rd * math.cos(math.radians(azm[index] - 90)),0))
    y = int(round(rd * math.sin(math.radians(azm[index] - 90)),0))
    xm = xc + x
    ym = yc + y

    # calculate current location if visible
    if visible[index] == 'Yes':
        rd = int(round(rad * (90 - alc[index])/90,0))
        x = int(round(rd * math.cos(math.radians(azc[index] - 90)),0))
        y = int(round(rd * math.sin(math.radians(azc[index] - 90)),0))
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
    if visible[index] == 'Yes':
        graphics1.circle(xcu, ycu, 2, 1)

    # show path of transit
    xt = [0] * (xr-xs)
    yt = [0] * (xr-xs)
    for i in range(xr - xs):
        xt = xs + i
        yt = int((X[0] * xt ** 2) + (X[1] * xt) + X[2])
        display1.pixel(xt, 63 - yt, 1)


def skyLocGraph(name):

    display2.text("Visible:", 0, 0)
    display2.text(visible[index], 64, 0)

    # show planet altitude
    if visible[index] == 'Yes':
        display2.text("Alt.:", 0, 20)
        display2.text(str(round(alc[index])), 40, 20)
        graphics2.line(8, 63, 38, 63, 1)
        y = 30 * math.sin(math.radians(alc[index]))
        y = int(round(y,0))
        graphics2.line(8, 63, 38, 63 - y, 1)

    # show planet azimuth
    xc = 95
    yc = 46
    rad = 17

    display2.text("Az.:", 68, 10)
    display2.text(str(round(azc[index])), 98, 10)
    display2.text("N", xc - 3, 20)
    graphics2.circle(xc, yc, rad, 1)
    x = rad * math.cos(math.radians(azc[index] - 90))
    x = round(x,0)
    y = rad * math.sin(math.radians(azc[index] - 90))
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

names = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
period = [0.2408467, 0.615197, 1.8808476, 11.862615, 29.447498, 84.016846, 164.79132]

# pre-allocate lists with Dec 9, 2019 values
visible = ['No', 'No', 'No', 'No', 'No', 'Yes', 'Yes']
azc = [306.0, 259.0, 342.0, 269.0, 259.0, 184.0, 233.0]
azr = [114.0, 121.0, 109.0, 120.0, 118.0, 73.0, 97.0]
azs = [245.0, 239.0, 250.0, 239.0, 241.0, 286.0, 262.0]
azm = [180.0, 179.0, 179.0, 179.0, 180.0, 179.0, 179.0]
alc = [60.0, 26.0, 65.0, 38.0, 23.0, 63.0, 27.0]
alm = [32.0, 26.0, 35.0, 27.0, 29.0, 63.0, 44.0]
long = [193.0, 327.0, 203.0, 274.0, 291.0, 35.0, 347.0]
dist = [1.22, 1.4, 2.34, 6.18, 10.9, 19.1, 29.9]
years = ['Feb 12, 2020', 'Mar 19, 2020', 'Aug 3, 2020', 'Jan 24, 2023', 'Dec 24, 2032', 'Feb 10, 2051', 'Jul 16, 2047']


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

        wolf = Wolfram(WOLFRAM_API_KEY)

        for index, name in enumerate(names):
            oled.fill(0)
            oled.text('Aquiring data:', 0, 0)
            oled.text(name, 0, 12)
            oled.show()

            # obtain planet distance from earth from wolframalpha API
            url = "http://api.wolframalpha.com/v1/result?i={0}%20distance%20from%20earth%3F&appid={1}".format(name, WOLFRAM_API_KEY)
            r = requests.get(url)
            dist[index] = [x.strip() for x in r.text.split(',')]
            dist[index] = [x.strip() for x in dist[index][0].split()]
            dist[index] = dist[index][1]
            r.close()
            del r
            gc.collect()
            dist[index] = float(dist[index])

            oled.pixel(0, 30, 1)
            oled.show()

            # obtain next periapsis from wolframalpha API
            url = "http://api.wolframalpha.com/v1/result?i={0}%20next%20periapsis%3F&appid={1}".format(name, WOLFRAM_API_KEY)
            r = requests.get(url)
            years[index] = r.text
            years[index] = [x.strip() for x in years[index].split()]
            years[index] = years[index][0][:3] + " " + years[index][1] + " " + years[index][2]
            r.close()
            del r
            gc.collect()

            oled.pixel(2, 30, 1)
            oled.show()

            # obtain planet heliocentric longitude from wolframalpha API
            long[index] = wolf.get_data(
                planet=name,
                parameter="heliocentric longitude",
            )
            oled.pixel(4, 30, 1)
            oled.show()

            # obtain planet above horizon from wolframalpha API
            visible[index] = wolf.get_data(
                planet=name,
                parameter="above horizon",
            )
            oled.pixel(6, 30, 1)
            oled.show()

            # sky chart data
            # obtain current planet azimuth from wolframalpha API
            azc[index] = wolf.get_data(
                planet=name,
                parameter="azimuth",
            )
            oled.pixel(8, 30, 1)
            oled.show()

            # obtain planet azimuth rise from wolframalpha API
            azr[index] = wolf.get_data(
                planet=name,
                parameter="azimuth rise",
            )
            oled.pixel(10, 30, 1)
            oled.show()

            # obtain planet azimuth set from wolframalpha API
            azs[index] = wolf.get_data(
                planet=name,
                parameter="azimuth set",
            )
            oled.pixel(12, 30, 1)
            oled.show()

            # obtain planet azimuth at maximum altitude from wolframalpha API
            azm[index] = wolf.get_data(
                planet=name,
                parameter="azimuth at time of maximum altitude",
            )
            oled.pixel(14, 30, 1)
            oled.show()

            # obtain current planet altitude from wolframalpha API
            alc[index] = wolf.get_data(
                planet=name,
                parameter="altitude",
            )
            oled.pixel(16, 30, 1)
            oled.show()

            # obtain max planet altitude from wolframalpha API
            alm[index] = wolf.get_data(
                planet=name,
                parameter="maximum altitude",
            )
            oled.pixel(18, 30, 1)
            oled.show()


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
