from flask import Flask, render_template
from cost_estimator import estimate_instance_cost
from idle_detector import detect_idle_instances
from openstack import connection
import os

def create_connection():
    return connection.Connection(
        auth_url=os.environ['OS_AUTH_URL'],
        project_name=os.environ['OS_PROJECT_NAME'],
        username=os.environ['OS_USERNAME'],
        password=os.environ['OS_PASSWORD'],
        user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
        project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
        region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'),
        app_name='cloudcost_idle',
    )

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
