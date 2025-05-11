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

    total_uptime = 0
    start_time = None

    for action in actions_sorted:
        action_type = action.action.upper()
        time_str = getattr(action, 'timestamp', None) or getattr(action, 'start_time', None)
        if not time_str:
            continue
        action_time = datetime.fromisoformat(time_str.replace('Z', '+00:00')).astimezone(timezone.utc)

        if action_type == 'START':
            if start_time is None:
                start_time = action_time
                print(f"  > START trovato alle {start_time}")
        elif action_type == 'STOP':
            if start_time is not None:
                delta = (action_time - start_time).total_seconds()
                print(f"  > STOP trovato alle {action_time} (durata sessione: {delta} sec)")
                total_uptime += delta
                start_time = None

    if start_time is not None:
        now = datetime.now(timezone.utc)
        delta = (now - start_time).total_seconds()
        print(f"  > La VM è attualmente attiva. Uptime corrente: {delta} sec")
        total_uptime += delta

    if not actions_sorted and created_at:
        now = datetime.now(timezone.utc)
        delta = (now - created_at).total_seconds()
        print(f"  > Nessuna azione registrata. VM probabilmente attiva da created_at: {delta} sec")
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
    ram = flavor_details.ram  # in MB
    disk = flavor_details.disk  # in GB

    # Costi per ora
    cost_per_hour_vcpu = vcpu * 0.05
    cost_per_hour_ram = (ram / 1024) * 0.01
    cost_per_hour_disk = disk * 0.001  # Applicato sempre, anche se VM spenta

    # Tempo di vita per il costo disco (basato su created_at)
    try:
        created_at = datetime.fromisoformat(instance.created_at.replace('Z', '+00:00')).astimezone(timezone.utc)
    except Exception:
        created_at = None

    now = datetime.now(timezone.utc)
    total_lifetime_seconds = (now - created_at).total_seconds() if created_at else 0
    total_lifetime_hours = total_lifetime_seconds / 3600

    # Uptime reale per CPU/RAM
    uptime_seconds = get_actual_uptime_seconds(instance.id, created_at)
    uptime_hours = uptime_seconds / 3600

    # Calcolo costi separati
    cost_cpu = round(cost_per_hour_vcpu * uptime_hours, 4)
    cost_ram = round(cost_per_hour_ram * uptime_hours, 4)
    cost_disk = round(cost_per_hour_disk * total_lifetime_hours, 4)

    total_cost = round(cost_cpu + cost_ram + cost_disk, 4)

    return {
        "instance_name": instance.name,
        "id": instance.id,
        "vcpu": vcpu,
        "ram": ram,
        "disk": disk,
        "uptime": round(uptime_hours, 2),
        "lifetime": round(total_lifetime_hours, 2),
        "cost_cpu": cost_cpu,
        "cost_ram": cost_ram,
        "cost_disk": cost_disk,
        "estimated_cost": total_cost
    }

def get_instance_cost_and_uptime(instance_id):
    conn = create_connection()
    server = conn.compute.get_server(instance_id)
    return estimate_instance_cost(server)
