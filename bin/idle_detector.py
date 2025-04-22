from openstack import connection
from .utils import get_openstack_connection
import datetime

def is_idle(instance, threshold_minutes=60):
    now = datetime.datetime.utcnow().replace(tzinfo=instance.launched_at.tzinfo)
    uptime = now - instance.launched_at

    # Simulazione: consideriamo inattivo se uptime > soglia e stato attivo ma basso carico (mock)
    return instance.status == "ACTIVE" and uptime.total_seconds() > threshold_minutes * 60

def get_idle_instances():
    conn = get_openstack_connection()
    servers = conn.compute.servers(details=True)

    idle = []
    for server in servers:
        if is_idle(server):
            idle.append({
                'name': server.name,
                'id': server.id,
                'uptime': str(server.launched_at),
                'status': server.status,
            })
    return idle
