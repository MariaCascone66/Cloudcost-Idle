from openstack import connection
import openstack 

def detect_idle_instances(cpu_threshold=5.0):
    conn = connection.Connection()
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
