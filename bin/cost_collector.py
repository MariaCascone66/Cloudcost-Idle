#!/usr/bin/env python3
"""
cost_collector.py
─────────────────
• Gira come service (systemd) ogni 60 s
• Calcola:
   – costo fittizio in $/h del flavor  (listino finto → see COST_TABLE)
   – marca VM come “idle” se (CPU < 5 %) *e* uptime > 2 h
• Scrive i risultati nei metadata della VM per
  essere letti dalla dashboard Flask.
"""

import time, logging
from datetime import datetime, timezone, timedelta
from openstack import connection

# ── config fittizi: costo orario flavour ─────────────────────────────
COST_TABLE = {               # USD/hour
    "m1.tiny":   0.004,
    "m1.small":  0.01,
    "m1.medium": 0.02,
    "m1.large":  0.04,
}

CHECK_INTERVAL = 60          # seconds
IDLE_CPU_THRESHOLD = 5       # percent
IDLE_UPTIME_HOURS  = 2

# ── OpenStack SDK connection (usa env OS_*) ──────────────────────────
conn = connection.from_config(cloud=None)  # prende variabili d’ambiente

log = logging.getLogger("cost_collector")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s")

def get_cost(flavor_name: str, hours: float) -> float:
    """Ritorna costo fittizio = prezzo_orario * ore_di_uptime"""
    rate = COST_TABLE.get(flavor_name, 0.015)   # default 0.015
    return round(rate * hours, 4)

def main():
    while True:
        try:
            for srv in conn.compute.servers(details=True):
                # uptime
                created = srv.created_at.replace(tzinfo=timezone.utc)
                hours_up = (datetime.now(timezone.utc)-created).total_seconds()/3600

                # costo
                flavor = conn.get_flavor(srv.flavor["id"])
                cost   = get_cost(flavor.name, hours_up)

                # fake CPU usage (0‑100) – per demo
                cpu_pct = float(srv.metadata.get("sim_cpu", 0))

                idle = (cpu_pct < IDLE_CPU_THRESHOLD
                        and hours_up > IDLE_UPTIME_HOURS)

                # scrive tutto nei metadati
                conn.compute.set_server_metadata(
                    srv,
                    metadata={
                        "est_cost": str(cost),
                        "idle": "yes" if idle else "no",
                        "last_update": datetime.utcnow().isoformat()
                    }
                )
                log.info("Updated %-20s cost=$%.4f idle=%s", srv.name, cost, idle)
        except Exception as exc:
            log.error("Collector error: %s", exc, exc_info=True)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
