import time
import random
import logging
from datetime import datetime, timezone
from auth import get_openstack_connection

logging.basicConfig(level=logging.INFO)
conn = get_openstack_connection()

def get_fake_cpu_load(instance_id): return random.uniform(10, 90)
def get_fake_ram_load(instance_id): return random.uniform(5, 80)
def get_fake_disk_load(instance_id): return random.uniform(1, 70)

def get_weather(cpu):
    if cpu < 30: return "☀️ Sunny"
    if cpu < 70: return "🌤️ Cloudy"
    return "🌩️ Stormy"

def assign_weather_tag(server):
    created_time = server.created_at.replace(tzinfo=timezone.utc)
    if (datetime.now(timezone.utc) - created_time).total_seconds() < 120:
        return "⏳ Initializing..."
    return get_weather(get_fake_cpu_load(server.id))

while True:
    try:
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
            logging.info(f"[Tagger] {server.name} → {weather} (CPU: {cpu:.2f}%, RAM: {ram:.2f}%, Disk: {disk:.2f}%)")
    except Exception as e:
        logging.error(f"Errore nel tagger: {e}")
    time.sleep(60)
