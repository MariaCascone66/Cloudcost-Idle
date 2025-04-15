import openstack
import time
import random
import os

# Connessione a OpenStack con clouds.yaml
cloud_name = os.getenv('OS_CLOUD_NAME', 'devstack-admin')  # default a devstack-admin
conn = openstack.connect(
    cloud=cloud_name,
    config_files=[clouds_yaml]
)

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
    for server in conn.compute.servers():
        cpu = get_fake_cpu_load(server.id)
        weather = get_weather(cpu)
        conn.compute.set_server_metadata(server, {"weather": weather})
        print(f"[Tagger] {server.name} → {weather}")
    time.sleep(60)
