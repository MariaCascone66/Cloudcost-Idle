from cost_estimator import create_connection
from datetime import datetime, timezone

def detect_idle_instances(idle_hours_threshold=6):
    """Trova VM che sembrano essere inattive in modo più realistico."""
    conn = create_connection()
    instances = conn.compute.servers(details=True)

    idle_vms = []
    now = datetime.now(timezone.utc)

    for instance in instances:
        # Se la VM è spenta, non è idle, è già shutdown
        if instance.status == 'SHUTOFF':
            continue

        # Calcola da quanto tempo è stata aggiornata l'ultima volta
        updated_at = getattr(instance, 'updated_at', None)
        if updated_at:
            # updated_at viene restituito come stringa, esempio: '2025-04-25T09:21:32Z'
            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            hours_since_update = (now - updated_time).total_seconds() / 3600

            # Se sono passate tante ore dall'ultimo aggiornamento, consideriamo la VM "idle"
            if hours_since_update >= idle_hours_threshold:
                idle_vms.append({
                    "instance_name": instance.name,
                    "id": instance.id,
                    "hours_since_last_update": round(hours_since_update, 2)
                })
        else:
            # Se non c'è updated_at (strano), puoi decidere se considerarla o ignorarla
            pass

    return idle_vms
