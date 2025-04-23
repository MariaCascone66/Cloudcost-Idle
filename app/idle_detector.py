import openstack
import random
from datetime import datetime

def detect_idle_vms(conn, cpu_threshold=5.0, uptime_threshold=1.0):
    idle_vms = []
    servers = conn.compute.servers()

    for server in servers:
        if server.status != 'ACTIVE':
            continue

        uptime_hours = (datetime.utcnow() - server.launched_at.replace(tzinfo=None)).total_seconds() / 3600
        simulated_cpu = random.uniform(0, 10)  # simulazione

        if simulated_cpu < cpu_threshold and uptime_hours > uptime_threshold:
            idle_vms.append({
                'name': server.name,
                'cpu': round(simulated_cpu, 2),
                'uptime': round(uptime_hours, 2),
            })

    return idle_vms
