import gc

import ssd1306
import gfx
import machine, neopixel
from machine import I2C, Pin
import network
import utime as time
import urllib.urequest
import ujson as json
from credentials import WIFI_SSID, WIFI_PASSWORD
from ntptime import settime
# from scron.week import simple_cron
import ubinascii

mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print(mac)

time.sleep(1)

#initialize display and graphics
oled_reset_pin = Pin(16, Pin.OUT)
oled_reset_pin.value(1)
time.sleep(1)
oled_i2c = I2C(scl=Pin(15), sda=Pin(4))
time.sleep(1)
oled = ssd1306.SSD1306_I2C(128, 64, oled_i2c)
time.sleep(1)
graphics = gfx.GFX(128, 64, oled.pixel)
time.sleep(1)

# define variables
names = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']

#initialize neopixel
n = 81
p = 13
np = neopixel.NeoPixel(machine.Pin(p), n, bpp=4)
stripl = int(n/len(names))

eepoch = 946684800 #time between epoch and embedded epoch in seconds

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep(0.5)
    if not wlan.isconnected():
        wlan.config(dhcp_hostname="esp32-planet-chimes")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        time.sleep(0.5)
        while not wlan.isconnected():
            time.sleep(0.5)
            pass
    print('network config:', wlan.ifconfig())

do_connect()
gc.collect()

oled.fill(0)
oled.text('wifi connected',0,0,1)
oled.show()
time.sleep(1)


def make_planet_list(date):
    with urllib.urequest.urlopen("https://time-guide.herokuapp.com/data?date={0}".format(date)) as url:
        data = json.loads(url.read().decode())
    planet_list = data["events"]
    return planet_list

# LED list for each light
LED = [(0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25),
       (0, 0, 0, 25)]

#clear LEDs at boot
for j in range(n):
    np[j] = (0, 0, 0, 0)
np.write()
time.sleep(0.5)

# set the RTC
def set_time_with_retry(retries):
    while True:
        if retries == 0:
            return
        try:
            settime()
            print('settime successful')
            oled.fill(0)
            oled.text('settime successful',0,0,1)
            oled.show()
            time.sleep(1)
        except:
            retries -= 1
            time.sleep(5)
            print('retries remaining: {}'.format(retries))
        else:
            return

set_time_with_retry(3)

now = int(time.time()) + eepoch # return time since the Epoch in Unix time
print(now)
now_local = time.localtime(now)
now_local_str = " ".join(map(str, now_local))

print(now_local)
print(now_local_str)

oled.fill(0)
oled.text('last now:',0,0,1)
oled.text(now_local_str,0,16,1)
oled.show()
time.sleep(1)

#get next 24h planet list
#first get today's list
with urllib.urequest.urlopen("https://time-guide.herokuapp.com/data") as url:
    data = json.loads(url.read().decode())
planet_list = data["events"]
#then get tomorrow's list
date = '{0}/{1}/{2}'.format(now_local.tm_mon, now_local.tm_year, now_local.tm_year


#sort chronologically
planet_list.sort(key=lambda x: int(x[2]))

#get rid of timestamps before now
planet_list = [item for item in planet_list if item[2] > now]


for i in range(len(names)):


    #turn on LEDs for planets already above horizon

    if [item for item in planet_list if item[2] == planetname and item[2] == 'rise']:
    if planet_list[i][1] == planetname and planet_list[i][2] == action:


    if planet_list[i][2] > planet_list[i + 9][2]: # if rise time is later than set time, it's above the horizon
        print('above horizon:', planet_list[i][1])

        dur_rem = planet_list[i + 9][0] - now #find time remaining until set
        dur = (24 * 3600) - (planet_list[i][0] - planet_list[i + 9][0]) #find approximate total time above horizon
        dur_int = int(dur / (2 * (n / len(names)) - 1)) #find duration of a single timestemp interval
        int_rem = int(dur_rem / dur_int) # number of intervals remaining is the duration remaining divided by duration interval
        if int_rem > 17:
            int_rem = 17

        dur_int_rem = dur % dur_int #remainder of time in final interval
        print('duration remaining:', dur_rem)
        print('intervals remaining:', int_rem)

        timestamp, planetname, action = planet_list[i + 9]

        #if the planet is setting:
        if int_rem < (n / len(names)) and not int_rem == 0:
            # 1. find a_set timestamps
            for j in range(int_rem - 1):
                above_set_timestamp = int(timestamp - ((dur_int * (j + 1)) + dur_int_rem))
                above_set_tuple = (above_set_timestamp, planetname, 'a_set')
                planet_list.append(above_set_tuple)

            # 2. light up last int_rem LEDs for setting
            if i % 2 == 1:
                for j in range(int_rem):
                    np[i * 9 + 9 - (j + 1)] = LED[j]
                    np.write()
            elif i % 2 == 0:
                for j in range(int_rem):
                    np[i * 9 + j] = LED[j]
                    np.write()
        elif int_rem == 0: #if the planet is about to set, light up last LED only
            if i % 2 == 1:
                np[i * 9 + 9 - 1] = LED[0]
                np.write()
            elif i % 2 == 0:
                np[i * 9] = LED[0]
                np.write()

        # if the planet is rising:
        else:
            #1. find a_rise timestamps
            for j in range(int_rem - int(n / len(names))):
                above_rise_timestamp = int(timestamp - (int((n / len(names)) - 1) * dur_int + dur_int * (j + 1) + dur_int_rem))
                above_rise_tuple = (above_rise_timestamp, planetname, 'a_rise')
                planet_list.append(above_rise_tuple)
            #2. find a_set timestamps
            for j in range(int(n / len(names) - 1)):
                above_set_timestamp = int(timestamp - (dur_int * (j + 1) + dur_int_rem))
                above_set_tuple = (above_set_timestamp, planetname, 'a_set')
                planet_list.append(above_set_tuple)
            #3. light up LEDs
            for j in range(2 * int(n / len(names)) - int_rem):
                if i % 2 == 1:
                    np[i * 9 + j] = LED[j]
                    np.write()
                elif i % 2 == 0:
                    np[i * 9 + 9 - (j + 1)] = LED[j]
                    np.write()

list.sort(planet_list) #sort list of rise and set chronologically
print('planet list:')
print(planet_list)

while True:
    timestamp, planetname, action = planet_list.pop(0)
    print('next up:', planetname, action, timestamp)
    timestamp_local = time.localtime(timestamp)
    timestamp_local_str = " ".join(map(str, timestamp_local))
    print(timestamp_local_str)

    planet_num = names.index(planetname)

    #sleep until the action
    delay = timestamp - now
    print('delay is:', delay)

    if delay > 0:
        oled.fill(0)
        oled.text('next',0,0,1)
        oled.text(planetname,35,0,1)
        oled.text(action,95,0,1)
        oled.text(timestamp_local_str,0,10,1)
        oled.text('last now:',0,20,1)
        oled.text(now_local_str,0,30,1)
        oled.text('sleep:',0,40,1)
        oled.text(str(delay),0,50,1)
        oled.text('secs',95,50,1)
        oled.show()

        # sleep until timestamp
        time.sleep(delay)

    if action == 'rise':
        print('action is:', action)

        #part 1: create list of above horizon intervals to adjust LEDs
        dur = [item for item in planet_list if planetname in item][0][0] - timestamp
        #find duration above horizon in seconds by looking up the timstamp of that planet's set time in planet_list (the rise time has been popped out)
        dur_int = int(dur / (2 * (n / len(names)) - 1)) #find duration of a single timestemp interval
        #dur_rem = dur % dur_int #find duration leftover (might not need this)
        print('total time above horizon:', dur)

        #add action timestamps for above_rise and above_set intervals between rise and set
        for j in range(int((n / len(names)) - 1)):
            above_rise_timestamp = int((timestamp + dur_int * (j + 1)))
            above_rise_tuple = (above_rise_timestamp, planetname, 'a_rise')
            planet_list.append(above_rise_tuple)
        for j in range(int((n / len(names)) - 1)):
            above_set_timestamp = int((timestamp + int((n / len(names)) - 1) * dur_int + dur_int * (j + 1)))
            above_set_tuple = (above_set_timestamp, planetname, 'a_set')
            planet_list.append(above_set_tuple)

        #turn on first LED at rise action timestamp
        if planet_num % 2 == 1:
            np[planet_num * 9] = LED[0]
            np.write()
        if planet_num % 2 == 0:
            np[planet_num * 9 + 9 - 1] = LED[0]
            np.write()

        print(planetname)
        print('rise')

    elif action == "a_rise":
        print('action is:', action)

        #count remaining instances of a_rise
        count = 0
        for i in range(len(planet_list)):
            if planet_list[i][1] == planetname and planet_list[i][2] == action:
                count += 1
        LED_count = int(n / len(names)) - count
        print('count is:', count)

        for i in range(LED_count):
            if planet_num % 2 == 1:
                np[planet_num * 9 + i] = LED[i]
                np.write()
            elif planet_num % 2 == 0:
                np[planet_num * 9 + 9 - (i + 1)] = LED[i]
                np.write()

    elif action == "a_set":
        print('action is:', action)

        count = 0
        for i in range(len(planet_list)):
            if planet_list[i][1] == planetname and planet_list[i][2] == action:
                count += 1
        LED_count = count + 1
        print('count is:', count)

        np[planet_num * 9] = (0, 0, 0, 0)
        np[planet_num * 9 + 1] = (0, 0, 0, 0)
        np[planet_num * 9 + 2] = (0, 0, 0, 0)
        np[planet_num * 9 + 3] = (0, 0, 0, 0)
        np[planet_num * 9 + 4] = (0, 0, 0, 0)
        np[planet_num * 9 + 5] = (0, 0, 0, 0)
        np[planet_num * 9 + 6] = (0, 0, 0, 0)
        np[planet_num * 9 + 7] = (0, 0, 0, 0)
        np[planet_num * 9 + 8] = (0, 0, 0, 0)

        for i in range(LED_count):
            if planet_num % 2 == 1:
                np[planet_num * 9 + 9 - (i + 1)] = LED[i]
                np.write()
            if planet_num % 2 == 0:
                np[planet_num * 9 + i] = LED[i]
                np.write()

    elif action == "sett":
        print('action is:', action)
        np[planet_num * 9] = (0, 0, 0, 0)
        np[planet_num * 9 + 1] = (0, 0, 0, 0)
        np[planet_num * 9 + 2] = (0, 0, 0, 0)
        np[planet_num * 9 + 3] = (0, 0, 0, 0)
        np[planet_num * 9 + 4] = (0, 0, 0, 0)
        np[planet_num * 9 + 5] = (0, 0, 0, 0)
        np[planet_num * 9 + 6] = (0, 0, 0, 0)
        np[planet_num * 9 + 7] = (0, 0, 0, 0)
        np[planet_num * 9 + 8] = (0, 0, 0, 0)
        np.write()

        time.sleep(5)

        if [item for item in planet_list if item[1] == planetname and item[2] == 'rise']:
            #get next set timestamp only and add to list if there's already a 'rise' timestamp
            next_set_timestamp = planet_timestamp(planetname, 'set')
            next_set_tuple = (next_set_timestamp, planetname, 'sett')
            planet_list.append(next_set_tuple)
            print('rise found in planet_list')
            print('next set:', next_set_timestamp)
        else:
            print('no rise found in planet_list')
            #get next rise timestamp and add to tuple if there isn't a rise
            next_rise_timestamp = planet_timestamp(planetname, 'rise')
            next_rise_tuple = (next_rise_timestamp, planetname, 'rise')
            planet_list.append(next_rise_tuple)
            print('next rise:', next_rise_timestamp)

            #get next set timestamp and add to list
            next_set_timestamp = planet_timestamp(planetname, 'set')
            next_set_tuple = (next_set_timestamp, planetname, 'sett')
            planet_list.append(next_set_tuple)
            print('next set:', next_set_timestamp)

    set_time_with_retry(3)

    now = int(time.time()) # return time since the Epoch (embedded)
    print('now:', now)
    now_local = time.localtime(now)
    now_local_str = " ".join(map(str, now_local))
    print(now_local_str)

    list.sort(planet_list)
    print('planet list:')
    print(planet_list)
