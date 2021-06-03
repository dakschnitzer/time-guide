import gc

import machine, neopixel
import time
import datetime
from datetime import timedelta
from pytz import timezone
from skyfield.api import N, W, wgs84, load, utc
from skyfield.almanac import find_discrete, risings_and_settings

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

# define variables
lat = 38.7135
lon = 78.1594
#define city just by lat/lon for almanac lookup
city = wgs84.latlon(lat * N, lon * W)
names = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']

# #initialize neopixel
# n = 81
# p = 13
# np = neopixel.NeoPixel(machine.Pin(p), n, bpp=4)
# # LED list for each light
# LED = [(0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25),
#        (0, 0, 0, 25)]


def planet_timestamp(name, action):
    # this function returns the next rise or set time from now
    t0 = datetime.datetime.now()
    t1 = t0 + datetime.timedelta(hours=24)

    t0 = t0.replace(tzinfo=utc)
    t0 = ts.utc(t0)
    t1 = t1.replace(tzinfo=utc)
    t1 = ts.utc(t1)

    f = risings_and_settings(eph, planets[names.index(name)], city)
    #This returns a function taking a Time argument returning True if the body’s altazimuth altitude angle plus radius_degrees is greater than horizon_degrees, else False
    t, values = find_discrete(t0, t1, f)
    #Find the times at which a discrete function of time changes value. in this case, find the set (0) and rise (1) times, t.

    if action == 'rise':
        #values array is 1 for the rise. we look up the index of the rise in the time array, t, to get the time of the rise event.
        timestamp = t[np.where(values == 1)].utc_datetime()
        timestamp = timestamp[0].timestamp()

    elif action == 'sett':
        #values array is 0 for the set. we look up the index of the set in the time array, t, to get the time of the set event.
        timestamp = t[np.where(values == 0)].utc_datetime()
        timestamp = timestamp[0].timestamp()

    return int(timestamp)


def make_planet_list():
    rise = [[0 for i in range(3)] for j in range(len(names))]
    sett = [[0 for i in range(3)] for j in range(len(names))]
    for i, name in enumerate(names) :
        # obtain the next rise time
        rise[i][0] = planet_timestamp(name, 'rise')
        rise[i][1] = name
        rise[i][2] = 'rise'

        print('acquired:', rise[i][0], name, 'rise')

        # obtain the next set time
        sett[i][0] = planet_timestamp(name, 'sett')
        sett[i][1] = name
        sett[i][2] = 'sett'

        print('acquired:', sett[i][0], name, 'sett')


    rise = [tuple(l) for l in rise]
    sett = [tuple(l) for l in sett]
    planet_list = rise + sett
    return planet_list

now = int(time.time()) # return time since the Epoch
print('current unix timestamp:', now)
now_local = time.localtime(now)
now_local_str = " ".join(map(str, now_local))

print('local time:', now_local)
print('local time string:', now_local_str)

planet_list = make_planet_list()


###########################

for i in range(len(names)):

    #clear LEDs at boot
    np[i * 9] = (0, 0, 0, 0)
    np[i * 9 + 1] = (0, 0, 0, 0)
    np[i * 9 + 2] = (0, 0, 0, 0)
    np[i * 9 + 3] = (0, 0, 0, 0)
    np[i * 9 + 4] = (0, 0, 0, 0)
    np[i * 9 + 5] = (0, 0, 0, 0)
    np[i * 9 + 6] = (0, 0, 0, 0)
    np[i * 9 + 7] = (0, 0, 0, 0)
    np[i * 9 + 8] = (0, 0, 0, 0)
    np.write()
    time.sleep(0.5)

    #turn on LEDs for planets already above horizon
    if planet_list[i][0] > planet_list[i + 9][0]: # if rise time is later than set time, it's above the horizon
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




names = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune']

stripl = 9

ts = load.timescale()

lat = 38.7135
lon = 78.1594
#define city just by lat/lon for almanac lookup
city = wgs84.latlon(lat * N, lon * W)


# now = datetime.datetime.now()
today = ts.utc(datetime.date.today())
yday = ts.utc(datetime.date.today() - datetime.timedelta(days=1))

f = risings_and_settings(planets, planet_name, city)
#This returns a function taking a Time argument returning True if the body’s altazimuth altitude angle plus radius_degrees is greater than horizon_degrees, else False
t, y = find_discrete(yday, today, f)
#Find the times at which a discrete function of time changes value.
tz = pytz.timezone('US/Eastern')

for ti, yi in zip(t, y):
    print(ti.utc_iso(), 'rise' if yi else 'set')




######


#define city with earth vector
city = earth + wgs84.latlon(lat * N, lon * W)



astro = city.at(t).observe(planet_name)
alt, az, d = astro.apparent().altaz()

    print(t)
    print(alt)
    print(az)
    return jsonify(
        n=n
        )


if __name__ == '__main__':
    app.run()

