from flask import Flask, render_template
from cost_estimator import estimate_instance_cost
from idle_detector import detect_idle_instances
from openstack import connection
from openstack.config import openstack_config

def create_connection():
    required_vars = ["OS_AUTH_URL", "OS_USERNAME", "OS_PASSWORD", "OS_PROJECT_NAME"]
    for var in required_vars:
        if not os.environ.get(var):
            raise RuntimeError(f"Missing required OpenStack env var: {var}")
    cloud = openstack_config.get_cloud_region()
    return connection.Connection(config=cloud)

app = Flask(__name__)

@app.route('/')
def index():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    costs = [estimate_instance_cost(i,conn) for i in instances]
    return render_template('index.html', costs=costs)

@app.route('/idle')
def idle():
    conn=create_connection()
    idle_vms = detect_idle_instances(conn)
    return render_template('idle_modal.html', idle_vms=idle_vms)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
