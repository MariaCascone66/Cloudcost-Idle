from flask import Flask, render_template
from openstack.config import OpenStackConfig
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Configurazione OpenStack
cloud_name = 'devstack'
config_path = os.getenv('OS_CLOUDS_YAML', '/opt/stack/cloudwatcher/config/clouds.yaml')

config = OpenStackConfig(config_files=[config_path])
conn = config.get_one_cloud(cloud=cloud_name).connect()

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
            logging.warning(f"Errore caricando dati per il progetto {project.name}: {e}")
            continue

    for s in servers:
        s.weather = s.metadata.get('weather', '❓')

    return render_template('index.html', servers=servers, projects=project_data)

if __name__ == '__main__':
    from waitress import serve
    logging.info("Quota Dashboard in esecuzione su http://0.0.0.0:5001")
    serve(app, host='0.0.0.0', port=5001)
