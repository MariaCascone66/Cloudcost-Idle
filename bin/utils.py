import openstack
import os

def get_openstack_connection():
    return openstack.connect(cloud=os.getenv('OS_CLOUD'))
