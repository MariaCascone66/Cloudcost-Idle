from flask import Flask, render_template, request, redirect, url_for
import logging
from auth import get_openstack_connection
from openstack import exceptions

app = Flask(__name__, template_folder='/opt/stack/cloudwatcher/templates')
logging.basicConfig(level=logging.INFO)

conn = get_openstack_connection()

@app.route('/')
def index():
    servers = list(conn.compute.servers())
    projects = list(conn.identity.projects())

    project_data = []
    for project in projects:
        try:
            quotas = conn.get_compute_quotas(project.id)
            used = conn.get_compute_usage(project.id)
            project_data.append({
                'name': project.name,
                'id': project.id,
                'cpu': f"{used.total_vcpus_usage:.0f}/{quotas.cores}",
                'ram': f"{used.total_memory_mb_usage:.0f}/{quotas.ram}",
            })
        except Exception as e:
            logging.warning(f"Errore nel recupero delle quote per {project.name}: {e}")
            continue

    # Add the weather data to servers
    for s in servers:
        s.weather = s.metadata.get('weather', '❓')

    return render_template('index.html', servers=servers, projects=project_data)

@app.route('/create_vm', methods=['GET', 'POST'])
def create_vm():
    if request.method == 'POST':
        # Get the form data to create the VM
        name = request.form.get('name')
        image_id = request.form.get('image_id')
        flavor_id = request.form.get('flavor_id')
        network_id = request.form.get('network_id')

        try:
            # Create the new VM instance
            server = conn.compute.create_server(
                name=name,
                image_id=image_id,
                flavor_id=flavor_id,
                networks=[{"uuid": network_id}]
            )
            logging.info(f"VM {name} created successfully")
            return redirect(url_for('index'))
        except exceptions.SDKException as e:
            logging.error(f"Failed to create VM: {e}")
            return render_template('create_vm.html', error=f"Failed to create VM: {e}")
    
    return render_template('create_vm.html')

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5001)
