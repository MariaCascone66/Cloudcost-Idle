from flask import Flask, render_template
from cost_estimator import estimate_instance_cost, create_connection
from idle_detector import detect_idle_instances

app = Flask(__name__)

@app.route('/')
def index():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    costs = [estimate_instance_cost(i) for i in instances]
    return render_template('index.html', costs=costs)

@app.route('/idle')
def idle():
    conn = create_connection()
    idle_vms = detect_idle_instances()
    return render_template('idle_modal.html', idle_vms=idle_vms)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
