from cost_estimator import create_connection
from datetime import datetime, timezone

IDLE_MINUTES_THRESHOLD = 30  # Puoi modificarlo facilmente qui

def detect_idle_instances():
    """Restituisce le VM considerate inattive basandosi sull'ultima modifica dello stato."""
    conn = create_connection()
    instances = conn.compute.servers(details=True)

    idle_vms = []
    now = datetime.now(timezone.utc)

    for instance in instances:
        if instance.status == 'SHUTOFF':
            continue  # Escludiamo VM già spente

        updated_at = getattr(instance, 'updated_at', None)
        if updated_at:
            try:
                updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                minutes_since_update = (now - updated_time).total_seconds() / 60

                if minutes_since_update >= IDLE_MINUTES_THRESHOLD:
                    idle_vms.append({
                        "instance_name": instance.name,
                        "id": instance.id,
                        "hours_since_last_update": round(minutes_since_update / 60, 2)
                    })
            except ValueError:
                print(f"Errore parsing updated_at per VM {instance.name}: {updated_at}")

    return idle_vms if idle_vms else None
