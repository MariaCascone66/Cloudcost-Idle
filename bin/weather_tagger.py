#!/usr/bin/env python3
import openstack
import time
import random
import os
import logging
from openstack import connection

logging.basicConfig(level=logging.INFO)

# Connessione a OpenStack
clouds_yaml = os.getenv('OS_CLOUDS_YAML', '/opt/stack/cloudwatcher/config/clouds.yaml')

conn = connection.Connection(
    auth_url="http://10.0.2.15/identity",
    project_name="admin",
    username="admin",
    password="secret",
    user_domain_name="Default",
    project_domain_name="Default",
    region_name="RegionOne",
    interface="public",
    identity_api_version='3'
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
    servers = list(conn.compute.servers())
    for server in servers:
        cpu = get_fake_cpu_load(server.id)
        weather = get_weather(cpu)
        conn.compute.set_server_metadata(server, {"weather": weather})
        logging.info(f"[Tagger] {server.name} → {weather}")
    time.sleep(60)
