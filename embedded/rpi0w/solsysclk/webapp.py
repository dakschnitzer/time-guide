from flask import Flask, render_template, request
import json
from main import run_clock

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def save_config(data):
    with open('config.json', 'w') as outfile:
        json.dump(data, outfile)

@app.route('/forminfo', methods=['POST'])
def forminfo():
    lat = request.form['lat']
    lon = request.form['lon']
    data =  {
        'lat': lat,
        'lon': lon,
    }
    save_config(data)
    run_clock()
    return data

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
