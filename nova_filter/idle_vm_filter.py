from nova.scheduler import filters
from oslo_log import log as logging
from openstack import connection
from datetime import datetime,timezone
import os

LOG = logging.getLogger (__name__)

class IdleVMFilter(filters.BaseHostFilter):
    """Evita di schedulare nuove VM su nodi con VM inattive"""

    def host_passes(self, host_state, spec_obj):
        conn = connection.Connection (
            auth_url=os.environ['OS_AUTH_URL'],
            project_name=os.environ['OS_PROJECT_NAME'],
            username=os.environ['OS_USERNAME'],
            password=os.environ['OS_PASSWORD'],
            user_domain_name=os.environ.get('OS_USER_DOMAIN_NAME', 'Default'),
            project_domain_name=os.environ.get('OS_PROJECT_DOMAIN_NAME', 'Default'),
            region_name=os.environ.get('OS_REGION_NAME', 'RegionOne'),
            app_name='cloudcost_idle',
        )

        try:
            instances = conn.compute.servers(all_projects=True)
        except Exception as e:
            LOG.warning("Errore nel recuper delle istanze: %s", str(e))
            return True
        
        for inst in instances:
            if inst.hypervisor_hostname != host_state.host:
                continue
            if inst.status == 'SHUTOFF':
                continue

            last_active = inst.updated_at or inst.created_at 
            if not last_active:
                continue

            last_active_dt = datetime.strptime(last_active, "%Y-%m-%dT%H:%M:%SZ")
            now = datetime.now(timezone.utc)
            minutes_inactive = (now - last_active_dt.replace(tzinfo=timezone.utc)).total_seconds() / 60

            if minutes_inactive > 30:
                LOG.info(f"Host {host_state.host} ha una VM inattiva: {inst.name}")
                return False
            
        return True