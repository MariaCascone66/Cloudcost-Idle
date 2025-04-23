from flask import Flask, render_template
from cost_estimator import estimate_instance_cost
from idle_detector import detect_idle_instances
from openstack import connection
import os

def create_connection():
    return connection.Connection(
        auth_url=os.environ.get("OS_AUTH_URL"),
        project_name=os.environ.get("OS_PROJECT_NAME"),
        username=os.environ.get("OS_USERNAME"),
        password=os.environ.get("OS_PASSWORD"),
        user_domain_name=os.environ.get("OS_USER_DOMAIN_NAME"),
        project_domain_name=os.environ.get("OS_PROJECT_DOMAIN_NAME")
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
