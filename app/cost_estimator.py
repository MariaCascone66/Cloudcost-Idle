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
        raise Exception(f"Variabile d'ambiente mancante: {e}")

def parse_iso_time(iso_str):
    if iso_str:
        return datetime.fromisoformat(iso_str.replace('Z', '+00:00')).astimezone(timezone.utc)
    return None

def get_actual_uptime_seconds(instance_id, created_at=None):
    conn = create_connection()
    actions = list(conn.compute.server_actions(instance_id))

    def extract_time(action):
        return parse_iso_time(getattr(action, 'timestamp', None) or getattr(action, 'start_time', None)) or datetime.min.replace(tzinfo=timezone.utc)

    actions_sorted = sorted(actions, key=extract_time)

    print(f"\n[DEBUG] VM {instance_id} - Server Actions trovate:")
    for a in actions_sorted:
        t_str = getattr(a, 'timestamp', None) or getattr(a, 'start_time', None)
        print(f"  - Azione: {a.action} | Timestamp: {t_str}")

    total_uptime = 0
    start_time = None

    for action in actions_sorted:
        action_type = action.action.upper()
        action_time = parse_iso_time(getattr(action, 'timestamp', None) or getattr(action, 'start_time', None))
        if not action_time:
            continue

        if action_type == 'START':
            if start_time is None:
                start_time = action_time
                print(f"  > START alle {start_time}")
        elif action_type == 'STOP':
            if start_time:
                delta = (action_time - start_time).total_seconds()
                total_uptime += delta
                print(f"  > STOP alle {action_time} (sessione: {delta} sec)")
                start_time = None

    # Se la VM è ancora attiva
    if start_time:
        now = datetime.now(timezone.utc)
        delta = (now - start_time).total_seconds()
        total_uptime += delta
        print(f"  > La VM è attiva. Uptime corrente: {delta} sec")

    # Se nessun evento ha generato uptime, fallback su CREATE o created_at
    if total_uptime == 0:
        create_action = next((a for a in actions_sorted if a.action.upper() == 'CREATE'), None)
        if create_action:
            created_time = parse_iso_time(getattr(create_action, 'timestamp', None) or getattr(create_action, 'start_time', None))
            if created_time:
                delta = (datetime.now(timezone.utc) - created_time).total_seconds()
                print(f"  > Solo evento CREATE disponibile. Uptime: {delta} sec")
                total_uptime = delta
        elif created_at:
            created_time = parse_iso_time(created_at) if isinstance(created_at, str) else created_at.astimezone(timezone.utc)
            delta = (datetime.now(timezone.utc) - created_time).total_seconds()
            print(f"  > Uso created_at fornito. Uptime: {delta} sec")
            total_uptime = delta

    print(f"[DEBUG] Totale uptime VM {instance_id}: {total_uptime} sec\n")
    return total_uptime

def estimate_instance_cost(instance):
    conn = create_connection()

    flavor_id = instance.flavor.get('id') or instance.flavor.get('original_name') or instance.flavor.get('name')
    flavor = next((f for f in conn.compute.flavors() if f.id == flavor_id or f.name == flavor_id), None)

    if not flavor:
        raise Exception(f"Flavor non trovato: {flavor_id}")

    vcpu = flavor.vcpus
    ram = flavor.ram  # MB
    disk = flavor.disk  # GB

    cost_cpu_hr = vcpu * 0.05
    cost_ram_hr = (ram / 1024) * 0.01
    cost_disk_hr = disk * 0.001

    created_time = parse_iso_time(instance.created_at) if hasattr(instance, 'created_at') else None
    now = datetime.now(timezone.utc)
    total_lifetime_hours = ((now - created_time).total_seconds() / 3600) if created_time else 0

    uptime_seconds = get_actual_uptime_seconds(instance.id, created_time)
    uptime_hours = uptime_seconds / 3600

    cost_cpu = round(cost_cpu_hr * uptime_hours, 4)
    cost_ram = round(cost_ram_hr * uptime_hours, 4)
    cost_disk = round(cost_disk_hr * total_lifetime_hours, 4)
    total = round(cost_cpu + cost_ram + cost_disk, 4)

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
        "estimated_cost": total
    }

def get_instance_cost_and_uptime(instance_id, created_at=None):
    conn = create_connection()
    instance = conn.compute.get_server(instance_id)

    if created_at:
        instance.created_at = created_at.isoformat() if not isinstance(created_at, str) else created_at

    return estimate_instance_cost(instance)
