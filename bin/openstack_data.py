from openstack import connection

def get_images(conn):
    """Recupera tutte le immagini disponibili in OpenStack."""
    return list(conn.compute.images())

def get_flavors(conn):
    """Recupera tutti i flavor disponibili in OpenStack."""
    return list(conn.compute.flavors())

def get_networks(conn):
    """Recupera tutte le reti disponibili in OpenStack."""
    return list(conn.network.networks())
