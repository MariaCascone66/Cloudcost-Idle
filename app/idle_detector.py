from cost_estimator import create_connection
from datetime import datetime, timezone

IDLE_MINUTES_THRESHOLD = 30  # Threshold di inattività in minuti

def detect_idle_instances():
    """
    Restituisce le VM considerate inattive.
    Criteri:
    - VM è attiva (non SHUTOFF)
    - Nessuna attività recente (updated_at > soglia)
    - Nessun volume attivo associato
    - Nessun floating IP (accesso pubblico)
    """
    conn = create_connection()
    instances = conn.compute.servers(details=True)
    idle_vms = []
    now = datetime.now(timezone.utc)

    for instance in instances:
        # Saltiamo VM spente
        if instance.status == 'SHUTOFF':
            continue

        updated_at = getattr(instance, 'updated_at', None)
        if not updated_at:
            continue  # Nessun dato utile sullo stato

        try:
            updated_time = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            minutes_since_update = (now - updated_time).total_seconds() / 60
        except ValueError:
            print(f"[WARN] Errore parsing updated_at per VM {instance.name}: {updated_at}")
            continue

        if minutes_since_update < IDLE_MINUTES_THRESHOLD:
            continue  # La VM è ancora attiva di recente

        # Verifica volumi attaccati
        try:
            volume_attachments = conn.compute.volume_attachments(instance.id)
            has_attached_volumes = len(volume_attachments) > 0
        except Exception as e:
            print(f"[WARN] Impossibile controllare volumi per VM {instance.name}: {e}")
            has_attached_volumes = True  # Per sicurezza la consideriamo attiva

        # Verifica floating IP
        try:
            has_floating_ip = any(
                ip.get('OS-EXT-IPS:type') == 'floating'
                for net in instance.addresses.values()
                for ip in net
            )
        except Exception as e:
            print(f"[WARN] Impossibile controllare IP per VM {instance.name}: {e}")
            has_floating_ip = True  # Per sicurezza la consideriamo attiva

        # Solo se non ha IP pubblico né volumi
        if not has_attached_volumes and not has_floating_ip:
            idle_vms.append({
                "instance_name": instance.name,
                "id": instance.id,
                "status": instance.status,  
                "hours_since_last_update": round(minutes_since_update / 60, 2)
            })


    return idle_vms 
