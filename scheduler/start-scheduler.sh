#!/bin/bash
set -e
import os

# Stampa il percorso del file corrente
print("Percorso corrente:", os.getcwd())

# Carica le credenziali OpenStack
source "/opt/stack/devstack/openrc admin admin"

# Attiva il virtualenv
source "/opt/stack/snapshot-scheduler/app/venv/bin/activate"

# Avvia lo scheduler
python3 "/opt/stack/snapshot-scheduler/app/scheduler.py"

chmod +x "/opt/stack/snapshot-scheduler/scheduler/start-scheduler.sh"
