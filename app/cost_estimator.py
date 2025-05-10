from openstack import connection
from datetime import datetime, timezone
import os

def create_connection():
    try:
        return connection.Connection(
            auth_url=os.environ['OS_AUTH_URL'],
            project_name=os.environ['OS_PROJECT_NAME'],
            username=os.environ['OS_USERNAME'],
            password=os.environ['OS_PASSWORD'],
            user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
            project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
            region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'),
            app_name='cloudcost_idle',
        )
    except KeyError as e:
        raise Exception(f"Impossibile connettersi a OpenStack: variabile d'ambiente mancante: {e}")

def get_actual_uptime_seconds(instance_id, created_at=None):
    conn = create_connection()
    actions = list(conn.compute.server_actions(instance_id))

    def extract_time(action):
        time_str = getattr(action, 'timestamp', None) or getattr(action, 'start_time', None)
        if time_str:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00')).astimezone(timezone.utc)
        return datetime.min.replace(tzinfo=timezone.utc)

    actions_sorted = sorted(actions, key=extract_time)

    print(f"\n[DEBUG] VM {instance_id} - Server Actions trovate:")
    for a in actions_sorted:
        t_str = getattr(a, 'timestamp', None) or getattr(a, 'start_time', None)
        print(f"  - Azione: {a.action} | Timestamp: {t_str}")

    start_time = None
    total_uptime = 0

    for action in actions_sorted:
        action_type = action.action.upper()
        time_str = getattr(action, 'timestamp', None) or getattr(action, 'start_time', None)
        if not time_str:
            continue

        time = datetime.fromisoformat(time_str.replace('Z', '+00:00')).astimezone(timezone.utc)

        if action_type == 'START' and start_time is None:
            start_time = time
            print(f"  > START trovato alle {start_time}")
        elif action_type == 'STOP' and start_time:
            delta = (time - start_time).total_seconds()
            print(f"  > STOP trovato alle {time} (durata sessione: {delta} sec)")
            total_uptime += delta
            start_time = None

    if start_time:
        now = datetime.now(timezone.utc)
        delta = (now - start_time).total_seconds()
        print(f"  > La VM è ancora attiva. Aggiungo uptime attuale: {delta} sec")
        total_uptime += delta
    elif not actions_sorted and created_at:
        # Nessuna azione, ma created_at esiste ⇒ VM appena creata
        now = datetime.now(timezone.utc)
        delta = (now - created_at).total_seconds()
        print(f"  > Solo CREATE presente. VM attiva. Uptime da created_at: {delta} sec")
        total_uptime = delta
    elif created_at:
        # Caso VM attiva ma senza START
        now = datetime.now(timezone.utc)
        delta = (now - created_at).total_seconds()
        print(f"  > VM attiva senza START. Uptime da created_at: {delta} sec")
        total_uptime = delta

    print(f"[DEBUG] Totale uptime VM {instance_id}: {total_uptime} sec\n")
    return total_uptime

def estimate_instance_cost(instance):
    conn = create_connection()

    flavor_identifier = instance.flavor.get('id') or instance.flavor.get('original_name') or instance.flavor.get('name')

    flavor_details = next(
        (f for f in conn.compute.flavors()
         if f.id == flavor_identifier or f.name == flavor_identifier),
        None
    )

    if not flavor_details:
        raise Exception(f"Flavor non trovato per: {flavor_identifier}")

    vcpu = flavor_details.vcpus
    ram = flavor_details.ram
    disk = flavor_details.disk

    cost_per_hour = (vcpu * 0.05) + (ram / 1024 * 0.01) + (disk * 0.001)

    try:
        created_at = datetime.fromisoformat(instance.created_at.replace('Z', '+00:00')).astimezone(timezone.utc)
    except Exception:
        created_at = None

    uptime_seconds = get_actual_uptime_seconds(instance.id, created_at)
    uptime_hours = uptime_seconds / 3600

    total_cost = round(cost_per_hour * uptime_hours, 4)

    return {
        "instance_name": instance.name,
        "id": instance.id,
        "vcpu": vcpu,
        "ram": ram,
        "disk": disk,
        "uptime": round(uptime_hours, 2),
        "estimated_cost": total_cost
    }

def get_instance_cost_and_uptime(instance_id):
    conn = create_connection()
    server = conn.compute.get_server(instance_id)
    return estimate_instance_cost(server)
