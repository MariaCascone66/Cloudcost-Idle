#!/usr/bin/env python3
"""
cost_dashboard.py
─────────────────
Mini‑Flask che mostra:
 • tabella VM con costi stimati e badge “Idle”
 • totale mensile stimato progetto
"""

import logging, math
from datetime import datetime
from flask import Flask, render_template, request
from openstack import connection

app = Flask(__name__, template_folder="/opt/stack/Cloudcost-Idle/templates",
            static_folder="/opt/stack/Cloudcost-Idle/static")

log  = logging.getLogger("cost_dashboard")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

conn = connection.from_config(cloud=None)

def hours_to_month(h):   # converti a mese (≈730 h)
    return h / 730

@app.route("/")
def index():
    servers = conn.compute.servers(details=True)
    rows    = []
    monthly_tot = 0.0

    for s in servers:
        meta = s.metadata or {}
        cost_hour = float(meta.get("est_cost", 0.0))
        created   = s.created_at
        hours_up  = (datetime.utcnow() - created).total_seconds()/3600
        cost_month = cost_hour / hours_to_month(hours_up) if hours_up else 0

        monthly_tot += cost_month
        rows.append({
            "name": s.name,
            "status": s.status,
            "flavor": conn.get_flavor(s.flavor["id"]).name,
            "hours":  round(hours_up,1),
            "cost":   f"${cost_hour:.4f}",
            "monthly": f"${cost_month:.2f}",
            "idle":   meta.get("idle","no") == "yes",
            "cpu":    meta.get("sim_cpu","-")
        })

    return render_template("index.html", rows=rows,
                           total=f"${monthly_tot:.2f}")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5100)
