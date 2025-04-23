from flask import Flask, render_template
from cost_estimator import estimate_instance_cost
from idle_detector import detect_idle_instances
from openstack import connection
import openstack

app = Flask(__name__)

@app.route('/')
def index():
    conn = connection.Connection()
    instances = conn.compute.servers(details=True)
    costs = [estimate_instance_cost(i) for i in instances]
    return render_template('index.html', costs=costs)

@app.route('/idle')
def idle():
    idle_vms = detect_idle_instances()
    return render_template('idle_modal.html', idle_vms=idle_vms)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
