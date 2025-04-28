from openstack import connection
import os

def create_connection():
    """Crea una connessione a OpenStack usando variabili ambiente."""
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

def estimate_instance_cost(instance):
    """Stima il costo totale di una VM basandosi su vCPU, RAM, disco e uptime."""
    conn = create_connection()

    # A volte instance.flavor['id'] è un nome invece dell'ID → cerchiamo tra tutti i flavor
    flavor_identifier = instance.flavor.get('id') or instance.flavor.get('original_name') or instance.flavor.get('name')

    # Cerchiamo tra tutti i flavor quello che ha quell'ID o quel nome
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

    # Prezzi simulati ma realistici
    cost_per_hour = (vcpu * 0.05) + (ram / 1024 * 0.01) + (disk * 0.001)
    
    # Calcolare l'uptime in ore, usando un valore predefinito di 0 se non esiste
    uptime_seconds = getattr(instance, 'uptime', 0)
    uptime_hours = uptime_seconds / 3600 if uptime_seconds else 0

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
