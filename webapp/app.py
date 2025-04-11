from flask import Flask, render_template
import random

app = Flask(__name__)

# Dummy simulated data for demonstration
data = [
    {"name": "demo-instance", "cpu": random.randint(10, 80), "ram": random.randint(256, 2048), "co2": round(random.uniform(0.5, 5.0), 2)}
]

@app.route("/")
def index():
    return render_template("index.html", instances=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
