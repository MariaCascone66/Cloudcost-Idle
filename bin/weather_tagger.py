# cloudwatcher/bin/weather_tagger.py
import time
import random
import logging
from auth import get_openstack_connection

logging.basicConfig(level=logging.INFO)
conn = get_openstack_connection()

def get_fake_cpu_load(instance_id):
    return random.randint(0, 100)

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
        weather = get_weather(cpu)
        conn.compute.set_server_metadata(server, {"weather": weather})
        logging.info(f"[Tagger] {server.name} → {weather}")
    time.sleep(60)
