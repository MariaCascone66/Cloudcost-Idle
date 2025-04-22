<h1 align="center">💰 CloudCost‑Idle Plugin for DevStack</h1>

<p align="center">
<img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-blue">
<img alt="License" src="https://img.shields.io/badge/License-Apache%202-orange">
</p>

### What it does

| Feature | Description |
|---------|-------------|
| **Cost Estimator** | Simula il costo orario e mensile delle VM in base al flavor & uptime (listino fittizio ma realistico). |
| **Idle Detector** | Segnala VM con CPU &lt; 5 % per > 2 h con badge “Idle 🔕”. |
| **Dashboard**     | Flask + Bootstrap all’indirizzo `http://HOST:5100` con totale progetto. |
| **Systemd‑ready** | Collector e Dashboard avviati come servizi, gestibili con `systemctl`. |

---

### Quick‑start (con DevStack già installato)

```bash
# 1. Clona
cd /opt/stack
git clone https://github.com/MariaCascone66/Cloudcost-Idle.git

# 2. Abilita in devstack/settings
echo "enable_plugin cloudcost-idle https://github.com/MariaCascone66/Cloudcost-Idle.git" >> devstack/local.conf

# 3. Ricarica servizi (nessun nuovo stack.sh!)
cd devstack && ./rejoin-stack.sh
