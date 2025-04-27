import os
import time
import paramiko
import datetime
import csv
from openstack import connection

CSV_FILE = 'uptime_cost_data.csv'

def init_csv_file():
    """Inizializza il file CSV se non esiste."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['instance_id', 'instance_name', 'last_activation', 'uptime_hours', 'estimated_cost'])  # intestazione

def update_uptime_cost_csv(instance_id, instance_name, uptime_hours, estimated_cost):
    """Aggiorna o aggiunge una riga nel CSV con i dati di uptime e costo."""
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Controlla se il file esiste già
    if os.path.exists(CSV_FILE):
        # Leggi tutte le righe esistenti
        with open(CSV_FILE, mode='r', newline='') as file:
            rows = list(csv.reader(file))
        
        # Verifica se la macchina è già registrata
        updated = False
        for row in rows:
            if row[0] == instance_id:  # Se l'ID della macchina esiste già
                row[2] = now  # Aggiorna la data di riattivazione
                row[3] = uptime_hours  # Aggiorna l'uptime in ore
                row[4] = estimated_cost  # Aggiorna il costo stimato
                updated = True
                break
        
        # Se la macchina non è ancora registrata, aggiungi una nuova riga
        if not updated:
            rows.append([instance_id, instance_name, now, uptime_hours, estimated_cost])

        # Scrivi di nuovo tutte le righe nel CSV
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
    else:
        # Se il file non esiste, crealo e aggiungi i dati
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([instance_id, instance_name, now, uptime_hours, estimated_cost])

    print(f"[INFO] Dati di uptime e costo aggiornati per {instance_name} ({instance_id}) nel CSV.")


def export_costs_to_csv(costs, filename="vm_costs.csv"):
    """Esporta i costi delle VM in un file CSV."""
    csv_file_path = os.path.join(BASE_DIR, filename)
    
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["instance_name", "id", "vcpu", "ram", "disk", "uptime", "estimated_cost", "created_at", "status"])
        writer.writeheader()
        writer.writerows(costs)
    
    return csv_file_path
    
def create_connection():
    """Crea una connessione a OpenStack usando variabili ambiente."""
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

def get_or_create_floating_ip(instance, conn, public_network_name='public'):
    """Ritorna il floating IP della VM, oppure ne crea uno nuovo."""
    for network_name, addresses in instance.addresses.items():
        for address in addresses:
            if address.get('OS-EXT-IPS:type') == 'floating':
                return address.get('addr')
    
    # Se non esiste un floating IP, creiamolo
    public_network = next((n for n in conn.network.networks() if n.name == public_network_name), None)
    if not public_network:
        raise Exception(f"Network pubblico '{public_network_name}' non trovato!")

    # Alloca un nuovo floating IP
    new_ip = conn.network.create_ip(floating_network_id=public_network.id)

    # Associa il floating IP alla VM
    conn.compute.add_floating_ip_to_server(instance, new_ip.floating_ip_address)

    print(f"[INFO] Creato e associato nuovo floating IP: {new_ip.floating_ip_address}")
    return new_ip.floating_ip_address

def get_uptime_via_ssh(ip_address, username="ubuntu", private_key_path=os.path.expanduser("~/.ssh/mykey"), ssh_port=22):
    """Recupera l'uptime reale di una VM collegandosi via SSH."""
    key = paramiko.RSAKey.from_private_key_file(private_key_path)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"[INFO] Connessione SSH a {ip_address} sulla porta {ssh_port}...")
    ssh.connect(hostname=ip_address, username=username, pkey=key, port=ssh_port, timeout=10)

    stdin, stdout, stderr = ssh.exec_command("cat /proc/uptime")
    output = stdout.read().decode().strip()

    ssh.close()

    uptime_seconds = float(output.split()[0])  # primo valore è uptime in secondi
    return uptime_seconds

def estimate_instance_cost(instance):
    """Stima il costo totale di una VM basandosi su vCPU, RAM, disco e uptime reale."""
    conn = create_connection()

    # Ottieni dettagli flavor
    flavor_identifier = instance.flavor.get('id') or instance.flavor.get('original_name') or instance.flavor.get('name')
    flavor_details = next(
        (f for f in conn.compute.flavors() if f.id == flavor_identifier or f.name == flavor_identifier),
        None
    )
    if not flavor_details:
        raise Exception(f"Flavor non trovato per: {flavor_identifier}")

    vcpu = flavor_details.vcpus
    ram = flavor_details.ram  # in MB
    disk = flavor_details.disk  # in GB

    # Prezzi simulati ma realistici
    cost_per_hour = (vcpu * 0.05) + (ram / 1024 * 0.01) + (disk * 0.001)

    try:
        # Ottieni IP pubblico (se serve lo crea)
        ip_address = get_or_create_floating_ip(instance, conn)
        # Recupera uptime reale via SSH
        uptime_seconds = get_uptime_via_ssh(ip_address)
    except Exception as e:
        print(f"[WARNING] Non è stato possibile calcolare uptime via SSH per {instance.name}: {e}")
        try:
            # Fallback: calcola l'uptime usando la data di creazione della VM
            created_at = instance.created_at  # Data di creazione della VM (formato datetime)
            current_time = datetime.datetime.now()  # Tempo attuale
            uptime_seconds = (current_time - created_at).total_seconds()  # Calcola l'uptime in secondi
            print(f"[INFO] Uptime calcolato dal tempo di creazione per {instance.name}: {uptime_seconds} secondi.")
        except Exception as e:
            print(f"[ERROR] Non è stato possibile calcolare l'uptime dalla data di creazione per {instance.name}: {e}")
            uptime_seconds = 0  # fallback se non riesce nemmeno questo

    uptime_hours = uptime_seconds / 3600
    total_cost = round(cost_per_hour * uptime_hours, 4)

    # Salva o aggiorna i dati nel CSV
    update_uptime_cost_csv(instance.id, instance.name, round(uptime_hours, 2), total_cost)

    return {
        "instance_name": instance.name,
        "id": instance.id,
        "vcpu": vcpu,
        "ram": ram,
        "disk": disk,
        "uptime": round(uptime_hours, 2),
        "estimated_cost": total_cost
    }

# Inizializza il CSV al primo avvio
init_csv_file()
