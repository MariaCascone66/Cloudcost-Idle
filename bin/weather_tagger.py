import time
import random
import logging
from auth import get_openstack_connection

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

while True:
    servers = list(conn.compute.servers())
    for server in servers:
        cpu = get_fake_cpu_load(server.id)
        ram = get_fake_ram_load(server.id)
        disk = get_fake_disk_load(server.id)
        weather = get_weather(cpu)

        # Set metadata for the server (including simulated values)
        conn.compute.set_server_metadata(server, {
            "weather": weather,
            "sim_cpu": round(cpu, 2),
            "sim_ram": round(ram, 2),
            "sim_disk": round(disk, 2)
        })
        logging.info(f"[Tagger] {server.name} → {weather} (CPU: {cpu}%, RAM: {ram}%, Disk: {disk}%)")
    time.sleep(60)
