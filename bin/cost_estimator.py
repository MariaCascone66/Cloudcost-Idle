from openstack import connection
from .utils import get_openstack_connection

# Prezzi simulati (basati su listini pubblici tipo AWS)
FLAVOR_PRICES = {
    'm1.tiny': 0.005,
    'm1.small': 0.01,
    'm1.medium': 0.02,
    'm1.large': 0.04,
}

def estimate_instance_cost(instance, flavors):
    flavor_id = instance.flavor['id']
    flavor = next((f for f in flavors if f.id == flavor_id), None)
    if not flavor:
        return None

    price_per_hour = FLAVOR_PRICES.get(flavor.name, 0.01)
    uptime_hours = (instance.updated_at - instance.created_at).total_seconds() / 3600
    return round(price_per_hour * uptime_hours, 4)

def get_costs():
    conn = get_openstack_connection()
    servers = list(conn.compute.servers(details=True))
    flavors = list(conn.compute.flavors())

    costs = []
    for server in servers:
        cost = estimate_instance_cost(server, flavors)
        if cost is not None:
            costs.append({
                'name': server.name,
                'status': server.status,
                'flavor': server.flavor['original_name'],
                'cost': f"${cost:.2f}"
            })
    return costs
