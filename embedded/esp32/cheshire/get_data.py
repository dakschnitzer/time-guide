
import requests
import gc


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


WOLFRAM_API_KEY = "WH5QHY-AEJ26XTJ95"

wolf = Wolfram(WOLFRAM_API_KEY)

names = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune']
visible_i = ['No', 'No', 'No', 'No', 'No', 'Yes', 'Yes']
azc_i = [306.0, 259.0, 342.0, 269.0, 259.0, 184.0, 233.0]
azr_i = [114.0, 121.0, 109.0, 120.0, 118.0, 73.0, 97.0]
azs_i = [245.0, 239.0, 250.0, 239.0, 241.0, 286.0, 262.0]
azm_i = [180.0, 179.0, 179.0, 179.0, 180.0, 179.0, 179.0]
alc_i = [60.0, 26.0, 65.0, 38.0, 23.0, 63.0, 27.0]
alm_i = [32.0, 26.0, 35.0, 27.0, 29.0, 63.0, 44.0]
long_i = [193.0, 327.0, 203.0, 274.0, 291.0, 35.0, 347.0]
dist_i = [1.22, 1.4, 2.34, 6.18, 10.9, 19.1, 29.9]
years_i = ['Feb 12, 2020', 'Mar 19, 2020', 'Aug 3, 2020', 'Jan 24, 2023', 'Dec 24, 2032', 'Feb 10, 2051', 'Jul 16, 2047']


for index, name in enumerate(names):
         # obtain planet heliocentric longitude from wolframalpha API
        long_i[index] = wolf.get_data(
            planet=name,
            parameter="heliocentric longitude",
        )

        # obtain planet distance from earth from wolframalpha API
        url = "http://api.wolframalpha.com/v1/result?i={0}%20distance%20from%20earth%3F&appid={1}".format(name, WOLFRAM_API_KEY)
        r = requests.get(url)
        dist = [x.strip() for x in r.text.split(',')]
        dist = [x.strip() for x in dist[0].split()]
        dist = dist[1]
        r.close()
        del r
        gc.collect()
        dist_i[index] = float(dist)

        # obtain next periapsis from wolframalpha API
        url = "http://api.wolframalpha.com/v1/result?i={0}%20next%20periapsis%3F&appid={1}".format(name, WOLFRAM_API_KEY)
        r = requests.get(url)
        years = r.text
        years = [x.strip() for x in years.split()]
        years = years[0][:3] + " " + years[1] + " " + years[2]
        r.close()
        del r
        gc.collect()
        years_i[index] = years


        # obtain planet above horizon from wolframalpha API
        visible_i[index] = wolf.get_data(
            planet=name,
            parameter="above horizon",
        )

        # sky chart data
        # obtain current planet azimuth from wolframalpha API
        azc_i[index] = wolf.get_data(
            planet=name,
            parameter="azimuth",
        )

        # obtain planet azimuth rise from wolframalpha API
        azr_i[index] = wolf.get_data(
            planet=name,
            parameter="azimuth rise",
        )

        # obtain planet azimuth set from wolframalpha API
        azs_i[index] = wolf.get_data(
            planet=name,
            parameter="azimuth set",
        )

        # obtain planet azimuth at maximum altitude from wolframalpha API
        azm_i[index] = wolf.get_data(
            planet=name,
            parameter="azimuth at time of maximum altitude",
        )

        # obtain current planet altitude from wolframalpha API
        alc_i[index] = wolf.get_data(
            planet=name,
            parameter="altitude",
        )

        # obtain max planet altitude from wolframalpha API
        alm_i[index] = wolf.get_data(
            planet=name,
            parameter="maximum altitude",
        )


