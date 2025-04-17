# cloudwatcher/bin/auth.py
import os
import logging
from keystoneauth1.identity import v3
from keystoneauth1 import session
from openstack import connection
from dotenv import load_dotenv 


load_dotenv("/opt/stack/cloudwatcher/config/openstack.env") 
def get_openstack_connection():
    try:
        auth_args = {
            'auth_url': os.getenv('OS_AUTH_URL'),
            'username': os.getenv('OS_USERNAME'),
            'password': os.getenv('OS_PASSWORD'),
            'project_name': os.getenv('OS_PROJECT_NAME'),
            'user_domain_name': os.getenv('OS_USER_DOMAIN_NAME'),
            'project_domain_name': os.getenv('OS_PROJECT_DOMAIN_NAME'),
        }

        # Verifica che tutte le variabili siano settate
        missing = [key for key, val in auth_args.items() if not val]
        if missing:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

        auth = v3.Password(**auth_args)
        sess = session.Session(auth=auth)

        return connection.Connection(session=sess, region_name=os.getenv('OS_REGION_NAME', 'RegionOne'))

    except Exception as e:
        logging.error(f"Errore nella creazione della connessione: {e}")
        raise
