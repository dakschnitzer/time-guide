from flask import Flask, render_template, request
import json
import os
import time
import logging

#initialize log
logging.basicConfig(filename='webapp.log', format='%(asctime)s %(levelname)-8s %(message)s',
datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logging.logProcesses = 0
logging.logThreads = 0

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def save_config(data):
    with open('config.json', 'w') as outfile:
        json.dump(data, outfile)
    os.chmod('config.json', 0o777)

@app.route('/forminfo', methods=['POST'])
def forminfo():
    lat = request.form['lat']
    lon = request.form['lon']
    data =  {
        'lat': lat,
        'lon': lon,
    }
    save_config(data)
    print(data)
    logging.info('%s' % data)
    time.sleep(3)
    os.system('sudo shutdown -r now')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
