from flask import Flask, render_template, request, redirect, url_for
import logging
import random
from auth import get_openstack_connection
from openstack_data import get_images, get_flavors, get_networks
from openstack import exceptions

app = Flask(__name__, template_folder='/opt/stack/cloudwatcher/templates')
logging.basicConfig(level=logging.INFO)

conn = get_openstack_connection()

@app.route('/')
def index():
    try:
        servers = list(conn.compute.servers())
        projects = list(conn.identity.projects())
    except Exception as e:
        logging.error(f"Errore durante il recupero di server/progetti: {e}")
        return render_template('index.html', servers=[], projects=[], error="Errore di connessione.")

    project_data = []
    for project in projects:
        try:
            quotas = conn.get_compute_quotas(project.id)
            used = conn.get_compute_usage(project.id)
            cpu_usage = used.total_vcpus_usage or 0
            ram_usage = used.total_memory_mb_usage or 0

            project_data.append({
                'name': project.name,
                'id': project.id,
                'cpu': f"{cpu_usage:.2f}/{quotas.cores}",
                'ram': f"{ram_usage:.2f}/{quotas.ram}",
            })
        except Exception as e:
            logging.warning(f"Errore nel recupero delle quote per {project.name}: {e}")
            continue

    for server in servers:
        metadata = server.metadata or {}
        server.weather = metadata.get('weather', '❓')
        server.sim_cpu = metadata.get('sim_cpu', 'N/A')
        server.sim_ram = metadata.get('sim_ram', 'N/A')
        server.sim_disk = metadata.get('sim_disk', 'N/A')
        server.tags = []

        if server.status == "ERROR":
            server.tags.append(('🚫', "La VM è in stato di errore."))

        sec_groups = getattr(server, 'security_groups', [])
        if any(g.get('name') == "restricted" for g in sec_groups):
            server.tags.append(('🔒', "Gruppo di sicurezza 'restricted' attivo."))

        if any(addr.get("OS-EXT-IPS:type") == "floating"
               for net in server.addresses.values() for addr in net):
            server.tags.append(('🌍', "Ha un IP pubblico (floating IP)."))

        server.tags.append(('🌤️', "Condizione meteo simulata basata sul carico."))

    return render_template('index.html', servers=servers, projects=project_data)

@app.route('/create_vm', methods=['GET', 'POST'])
def create_vm():
    if request.method == 'POST':
        name = request.form.get('name')
        image_id = request.form.get('image')
        flavor_id = request.form.get('flavor')
        network_id = request.form.get('network')

        metadata = {
            "sim_cpu": str(random.randint(10, 90)),
            "sim_ram": str(random.randint(10, 90)),
            "sim_disk": str(random.randint(10, 90))
        }

        try:
            conn.compute.create_server(
                name=name,
                image_id=image_id,
                flavor_id=flavor_id,
                networks=[{"uuid": network_id}],
                metadata=metadata
            )
            logging.info(f"VM '{name}' creata con metadata: {metadata}")
            return redirect(url_for('index'))
        except exceptions.SDKException as e:
            logging.error(f"Errore creazione VM: {e}")
            return render_template('create_vm.html',
                                   images=get_images(conn),
                                   flavors=get_flavors(conn),
                                   networks=get_networks(conn),
                                   error=str(e))

    return render_template('create_vm.html',
                           images=get_images(conn),
                           flavors=get_flavors(conn),
                           networks=get_networks(conn))

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5001)
