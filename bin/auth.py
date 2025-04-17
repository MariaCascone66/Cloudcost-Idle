# cloudwatcher/bin/auth.py
import os
import logging
from keystoneauth1.identity import v3
from keystoneauth1 import session
from openstack import connection

def get_openstack_connection():
    try:
        auth_args = {
            'auth_url': os.environ['OS_AUTH_URL'],
            'username': os.environ['OS_USERNAME'],
            'password': os.environ['OS_PASSWORD'],
            'project_name': os.environ['OS_PROJECT_NAME'],
            'user_domain_id': os.environ['OS_USER_DOMAIN_ID'],
            'project_domain_id': os.environ['OS_PROJECT_DOMAIN_ID'],
            'region_name': os.environ['OS_REGION_NAME'],
            'volume_api_version': os.environ['OS_VOLUME_API_VERSION'],
        }

        auth = v3.Password(**auth_args)
        # Create a session
        sess = session.Session(auth=auth)
        return connection.Connection(session=sess, region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'))

    except KeyError as missing:
        logging.error(f"Missing environment variable: {missing}")
        raise
    except Exception as e:
        logging.error(f"Failed to create OpenStack connection: {e}")
        raise
