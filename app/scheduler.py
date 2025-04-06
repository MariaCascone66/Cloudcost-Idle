import time
import os
from datetime import datetime
from openstack import connection

conn = connection.from_config(cloud='devstack-admin')

def create_snapshot():
    for volume in conn.block_storage.volumes(details=True):
        if volume.status == 'available':
            snapshot_name = f"auto-snap-{volume.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            print(f"Creating snapshot: {snapshot_name}")
            conn.block_storage.create_snapshot(volume_id=volume.id, name=snapshot_name)

if __name__ == "__main__":
    while True:
        create_snapshot()
        time.sleep(3600) 


# Stampa il percorso del file corrente
print("Percorso corrente:", os.getcwd())


