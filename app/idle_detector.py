from cost_estimator import create_connection
from datetime import datetime, timezone

IDLE_MINUTES_THRESHOLD = 45

def detect_idle_instances():
    """Trova VM che sembrano essere inattive in modo più realistico."""
    conn = create_connection()
    instances = conn.compute.servers(details=True)

    idle_vms = []
    now = datetime.now(timezone.utc)

    for instance in instances:
        if instance.status == 'SHUTOFF':
            continue

        updated_at = getattr(instance, 'updated_at', None)
        if updated_at:
            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            minutes_since_update = (now - updated_time).total_seconds() / 60

            if minutes_since_update >= IDLE_MINUTES_THRESHOLD:
                idle_vms.append({
                    "instance_name": instance.name,
                    "id": instance.id,
                    "hours_since_last_update": round(minutes_since_update / 60, 2)
                })
    return idle_vms
