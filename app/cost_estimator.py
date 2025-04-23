from openstack import connection
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

def estimate_instance_cost(instance):
    conn = create_connection()

    flavor_id = instance.flavor['id']
    flavor_details = conn.compute.get_flavor(flavor_id)

    vcpu = flavor_details.vcpus
    ram = flavor_details.ram  # in MB
    disk = flavor_details.disk  # in GB

    # Prezzi simulati ma realistici
    cost_per_hour = (vcpu * 0.05) + (ram / 1024 * 0.01) + (disk * 0.001)
    uptime_hours = (getattr(instance, 'uptime', 0)) / 3600

    total_cost = round(cost_per_hour * uptime_hours, 4)
    return {
        "instance_name": instance.name,
        "id": instance.id,
        "vcpu": vcpu,
        "ram": ram,
        "disk": disk,
        "uptime": round(uptime_hours, 2),
        "estimated_cost": total_cost
    }
