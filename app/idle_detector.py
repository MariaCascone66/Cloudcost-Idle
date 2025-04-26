import random
from cost_estimator import create_connection

def detect_idle_instances():
    """Trova VM che sembrano essere inattive (idle)."""
    conn = create_connection()
    instances = conn.compute.servers(details=True)

    idle_vms = []

    for instance in instances:
        # Simuliamo un valore casuale di utilizzo CPU (in futuro puoi integrare metriche reali)
        cpu_usage_percent = random.uniform(0, 100)

        if cpu_usage_percent < 10:  # VM considerate 'idle' se uso CPU <10%
            idle_vms.append({
                "instance_name": instance.name,
                "id": instance.id,
                "cpu_usage_percent": round(cpu_usage_percent, 2)
            })

    return idle_vms
