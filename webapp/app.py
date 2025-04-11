from flask import Flask, render_template, jsonify
import random

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    usage = {
        'cpu': round(random.uniform(30, 90), 2),
        'ram': round(random.uniform(1024, 4096), 2),  # in MB
    }
    co2_estimate = round(usage['cpu'] * usage['ram'] * 0.00001, 4)  # stima
    return jsonify({**usage, 'co2': co2_estimate})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')
