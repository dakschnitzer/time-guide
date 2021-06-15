from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forminfo', methods=['POST'])
def forminfo():
    lat = request.form['lat']
    lon = request.form['lon']
    return 'Lat: %s N, Lon: %s W confirmed<br/> <a href="/">Back Home</a>' % (lat, lon)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
