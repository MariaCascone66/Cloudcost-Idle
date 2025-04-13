import openstack
import time
import random
import os
import logging
from openstack.config import OpenStackConfig

logging.basicConfig(level=logging.INFO)

# Configurazione OpenStack
cloud_name = 'devstack'
config_path = os.getenv('OS_CLOUDS_YAML', '/opt/stack/cloudwatcher/config/clouds.yaml')
config = OpenStackConfig(config_files=[config_path])
conn = config.get_one_cloud(cloud=cloud_name).connect()

def get_fake_cpu_load(instance_id):
    return random.randint(0, 100)

def get_weather(cpu):
    if cpu < 30:
        return "☀️ Sunny"
    elif cpu < 70:
        return "🌤️ Cloudy"
    else:
        return "🌩️ Stormy"

logging.info("Weather Tagger avviato...")

while True:
    for server in conn.compute.servers():
        cpu = get_fake_cpu_load(server.id)
        weather = get_weather(cpu)
        try:
            conn.compute.set_server_metadata(server, {"weather": weather})
            logging.info(f"[WeatherTagger] {server.name} ({server.id}) → CPU: {cpu}% → {weather}")
        except Exception as e:
            logging.warning(f"Errore aggiornando metadati per {server.name}: {e}")
    time.sleep(60)
