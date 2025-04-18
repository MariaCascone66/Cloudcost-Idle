import time
import random
import logging
from auth import get_openstack_connection
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
conn = get_openstack_connection()

def get_fake_cpu_load(instance_id):
    return random.uniform(10, 90)

def get_fake_ram_load(instance_id):
    return random.uniform(5, 80)

def get_fake_disk_load(instance_id):
    return random.uniform(1, 70)

def get_weather(cpu):
    if cpu < 30:
        return "☀️ Sunny"
    elif cpu < 70:
        return "🌤️ Cloudy"
    else:
        return "🌩️ Stormy"

def assign_weather_tag(server):
    # Ottieni il tempo di creazione della VM
    created_time = server.created_at.replace(tzinfo=timezone.utc)
    # Se la VM è stata creata meno di 2 minuti fa, non assegnare ancora un meteo
    if (datetime.now(timezone.utc) - created_time).total_seconds() < 120:
        return "⏳ Initializing..."  # Mostra che la VM è ancora in fase di inizializzazione

    # Se sono passati più di 2 minuti, assegna un meteo in base alla CPU
    cpu = get_fake_cpu_load(server.id)
    return get_weather(cpu)

while True:
    servers = list(conn.compute.servers())
    for server in servers:
        cpu = get_fake_cpu_load(server.id)
        ram = get_fake_ram_load(server.id)
        disk = get_fake_disk_load(server.id)
        weather = get_weather(cpu)

        conn.compute.set_server_metadata(server, {
            "weather": weather,
            "sim_cpu": round(cpu, 2),
            "sim_ram": round(ram, 2),
            "sim_disk": round(disk, 2)
        })
        logging.info(f"[Tagger] {server.name} → {weather} (CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%)")
    time.sleep(60)
