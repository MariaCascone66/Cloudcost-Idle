from openstack import connection
import openstack
from dashboard import create_connection

def estimate_instance_cost(instance, conn):
     flavor_details = conn.get_flavor_by_id(instance.flavor['id'])

    vcpu = flavor_details.vcpus
    ram = flavor_details.ram  # in MB
    disk = flavor_details.disk  # in GB

    cost_per_hour = (vcpu * 0.05) + (ram / 1024 * 0.01) + (disk * 0.001)
    uptime_hours = (instance.uptime or 0) / 3600

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
