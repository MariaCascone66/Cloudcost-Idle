import openstack
from datetime import datetime

PRICING = {
    'm1.small': 0.01,
    'm1.medium': 0.02,
    'm1.large': 0.04,
}

def estimate_cost(conn):
    servers = conn.compute.servers()
    costs = []

    for server in servers:
        if server.status != 'ACTIVE':
            continue
        flavor = conn.compute.get_flavor(server.flavor['id'])
        hourly_price = PRICING.get(flavor.name, 0.01)

        uptime_hours = (datetime.utcnow() - server.launched_at.replace(tzinfo=None)).total_seconds() / 3600
        cost = round(uptime_hours * hourly_price, 4)

        costs.append({
            'name': server.name,
            'flavor': flavor.name,
            'uptime': round(uptime_hours, 2),
            'cost': cost,
        })

    return costs
