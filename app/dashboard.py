import os
from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
from idle_detector import detect_idle_instances
from openstack import connection
from datetime import datetime, timezone

def nocache(view):
    def no_cache_wrapper(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    no_cache_wrapper.__name__ = view.__name__
    return no_cache_wrapper

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '../templates')
STATIC_DIR = os.path.join(BASE_DIR, '../static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

def create_connection():
    try:
        return connection.Connection(
            auth_url=os.environ['OS_AUTH_URL'],
            project_name=os.environ['OS_PROJECT_NAME'],
            username=os.environ['OS_USERNAME'],
            password=os.environ['OS_PASSWORD'],
            user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
            project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
            region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'),
            app_name='cloudvm_manager',
        )
    except KeyError as e:
        print(f"[ERROR] Missing env variable: {e}")
        raise

@app.route('/')
@nocache
def index():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    vms = []
    for i in instances:
        created_at = getattr(i, 'created_at', None)
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                created_at = None

        created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else 'N/A'

        if created_at:
           uptime = (datetime.now(timezone.utc) - created_at.astimezone(timezone.utc)).total_seconds() / 3600
            estimated_cost = round((i.flavor.vcpus * 0.02 + i.flavor.ram / 1024 * 0.01 + i.flavor.disk * 0.005) * uptime, 2)
        else:
            uptime = 0
            estimated_cost = 0

        vm_info = {
            "instance_name": i.name,
            "id": i.id,
            "vcpu": i.flavor.vcpus,
            "ram": i.flavor.ram,
            "disk": i.flavor.disk,
            "status": i.status,
            "created_at": created_at_str,
            "uptime": round(uptime, 2),
            "estimated_cost": estimated_cost,
        }
        vms.append(vm_info)
    return render_template('index.html', vms=vms)

@app.route('/idle')
@nocache
def idle_vms():
    idle_vms = detect_idle_instances()
    return render_template('idle_modal.html', idle_vms=idle_vms)

@app.route('/reactivate_vm/<instance_id>', methods=['POST'])
def reactivate_vm(instance_id):
    conn = create_connection()
    conn.compute.start_server(instance_id)
    return '', 204

@app.route('/delete_vm/<instance_id>', methods=['POST'])
def delete_vm(instance_id):
    conn = create_connection()
    conn.compute.delete_server(instance_id)
    return '', 204

@app.route('/delete_idle_vm/<instance_id>', methods=['POST'])
def delete_idle_vm(instance_id):
    conn = create_connection()
    conn.compute.delete_server(instance_id)
    return '', 204

@app.route('/check_vm_exists/<instance_id>')
def check_vm_exists(instance_id):
    conn = create_connection()
    try:
        vm = conn.compute.get_server(instance_id)
        if vm is None:
            return jsonify({'exists': False})
        return jsonify({'exists': True})
    except Exception:
        return jsonify({'exists': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
