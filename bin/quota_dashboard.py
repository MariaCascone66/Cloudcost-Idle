from flask import Flask, render_template, request, redirect, url_for
import logging
from auth import get_openstack_connection
from openstack_data import get_images, get_flavors, get_networks
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

            cpu_usage = used.total_vcpus_usage
            ram_usage = used.total_memory_mb_usage

            project_data.append({
                'name': project.name,
                'id': project.id,
                'cpu': f"{cpu_usage:.2f}/{quotas.cores}" if cpu_usage else f"0.00/{quotas.cores}",
                'ram': f"{ram_usage:.2f}/{quotas.ram}" if ram_usage else f"0.00/{quotas.ram}",
            })
        except Exception as e:
            logging.warning(f"Errore nel recupero delle quote per {project.name}: {e}")
            continue

    for s in servers:
        s.weather = s.metadata.get('weather', '❓')

    return render_template('index.html', servers=servers, projects=project_data)

@app.route('/create_vm', methods=['GET', 'POST'])
def create_vm():
    if request.method == 'POST':
        name = request.form.get('name')
        image_id = request.form.get('image')
        flavor_id = request.form.get('flavor')
        network_id = request.form.get('network')

        try:
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
            return render_template('create_vm.html', error=f"Errore: {e}")

    images = get_images(conn)
    flavors = get_flavors(conn)
    networks = get_networks(conn)

    return render_template('create_vm.html', images=images, flavors=flavors, networks=networks)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5001)
