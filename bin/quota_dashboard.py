#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask, render_template
import openstack
import os
import logging
from openstack import connection
from auth import get_openstack_connection

app = Flask(__name__, template_folder='/opt/stack/cloudwatcher/templates')
logging.basicConfig(level=logging.INFO)
logging.info("Quota Dashboard in esecuzione su http://0.0.0.0:5001")

# Connessione a OpenStack
conn = get_openstack_connection()

#clouds_yaml = os.getenv('OS_CLOUDS_YAML', '/opt/stack/cloudwatcher/config/clouds.yaml')

#conn = connection.Connection(
#    auth_url="http://10.0.2.15/identity",
#    project_name="admin",
#    username="admin",
#    password="secret",
#    user_domain_name="Default",
#    project_domain_name="Default",
#    region_name="RegionOne",
#    interface="public",
#    identity_api_version='3'
#)

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

    for s in servers:
        s.weather = s.metadata.get('weather', '❓')

    return render_template('index.html', servers=servers, projects=project_data)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=5001)
