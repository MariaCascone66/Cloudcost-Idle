import os
from openstack import connection
from ceilometerclient import client as ceilometer_client
from keystoneauth1 import loading, session

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

def create_ceilometer_client():
    loader = loading.get_plugin_loader('password')
    auth = loader.load_from_options(
        auth_url=os.environ['OS_AUTH_URL'],
        username=os.environ['OS_USERNAME'],
        password=os.environ['OS_PASSWORD'],
        project_name=os.environ['OS_PROJECT_NAME'],
        user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
        project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default')
    )
    sess = session.Session(auth=auth)
    ceilometer = ceilometer_client.get_client('2', session=sess)
    return ceilometer

def detect_idle_instances(cpu_threshold=5.0):
    conn = create_connection()
    ceilometer = create_ceilometer_client()
    idle_instances = []

    for server in conn.compute.servers(details=True):
        samples = ceilometer.samples.list(
            meter_name='cpu_util',
            q=[{'field': 'resource_id', 'op': 'eq', 'value': server.id}],
            limit=10  # puoi anche aumentare se vuoi una media più robusta
        )

        if samples:
            avg_cpu = sum([s.counter_volume for s in samples]) / len(samples)
            if avg_cpu < cpu_threshold:
                idle_instances.append({
                    "id": server.id,
                    "name": server.name,
                    "cpu_util": round(avg_cpu, 2)
                })

    return idle_instances
