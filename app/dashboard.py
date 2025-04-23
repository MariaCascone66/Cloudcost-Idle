from flask import Flask, render_template
import openstack
from app.cost_estimator import estimate_cost
from app.idle_detector import detect_idle_vms

app = Flask(__name__)

conn = openstack.connect()

@app.route('/')
def index():
    cost_data = estimate_cost(conn)
    idle_data = detect_idle_vms(conn)
    return render_template('index.html', costs=cost_data, idle=idle_data)

if __name__ == '__main__':
    app.run(port=8080)
