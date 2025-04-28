import os
from flask import Flask, render_template, redirect, url_for, request
from openstack import connection
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, '../templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

def create_connection():
    """Crea una connessione a OpenStack usando variabili ambiente."""
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
        print(f"[ERROR] La variabile d'ambiente {e} non è impostata.")
        raise


@app.route('/')
def index():
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    vms = []
    for i in instances:
        # Convert created_at to a datetime object if it's a string
        created_at = getattr(i, 'created_at', None)
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))  # Convert to datetime
            except ValueError:
                created_at = None
        
        created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else 'N/A'
        
        vm_info = {
            "instance_name": i.name,
            "id": i.id,
            "vcpu": i.flavor.vcpus,
            "ram": i.flavor.ram,
            "disk": i.flavor.disk,
            "status": i.status,
            "created_at": created_at_str,
        }
        vms.append(vm_info)
    return render_template('index.html', vms=vms)
    
@app.route('/reactivate_vm/<instance_id>', methods=['GET', 'POST'])
def reactivate_vm(instance_id):
    if request.method == 'POST':
        conn = create_connection()
        instance = conn.compute.get_server(instance_id)
        
        # Reactivate the instance
        conn.compute.start_server(instance_id)
        
        return redirect(url_for('index'))

    return render_template('reactivate_modal.html', instance_id=instance_id)

@app.route('/delete_vm/<instance_id>', methods=['GET', 'POST'])
def delete_vm(instance_id):
    if request.method == 'POST':
        conn = create_connection()
        instance = conn.compute.get_server(instance_id)
        
        # Delete the instance
        conn.compute.delete_server(instance_id)
        return redirect(url_for('index'))
    
    return render_template('delete_modal.html', instance_id=instance_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
