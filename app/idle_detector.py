import os
from openstack import connection

conn = connection.Connection(
    auth_url=os.environ['OS_AUTH_URL'],
    project_name=os.environ['OS_PROJECT_NAME'],
    username=os.environ['OS_USERNAME'],
    password=os.environ['OS_PASSWORD'],
    user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
    project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
    region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'),
    app_name='cloudcost_idle',
)
def detect_idle_instances(cpu_threshold=5.0):
    conn = create_connection()
    idle_instances = []

    for server in conn.compute.servers(details=True):
        metrics = conn.telemetry.sample_list(meter_name='cpu_util', q=[
            {"field": "resource_id", "op": "eq", "value": server.id}
        ])
        if metrics:
            avg_cpu = sum([m.counter_volume for m in metrics]) / len(metrics)
            if avg_cpu < cpu_threshold:
                idle_instances.append({
                    "id": server.id,
                    "name": server.name,
                    "cpu_util": round(avg_cpu, 2)
                })
    return idle_instances
