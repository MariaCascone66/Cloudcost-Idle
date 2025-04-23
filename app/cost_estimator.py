from openstack import connection
from openstack.config import openstack_config

def create_connection():
    cloud = openstack_config.get_cloud_region()
    return connection.Connection(config=cloud)

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
