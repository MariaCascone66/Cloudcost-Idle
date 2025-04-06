#!/bin/bash
set -e

# Carica le credenziali OpenStack
source "/opt/stack/devstack/openrc admin admin"

# Attiva il virtualenv
source "/opt/stack/snapshot-scheduler/app/venv/bin/activate"

# Avvia lo scheduler
python3 "/opt/stack/snapshot-scheduler/app/scheduler.py"

chmod +x "/opt/stack/snapshot-scheduler/scheduler/start-scheduler.sh"
