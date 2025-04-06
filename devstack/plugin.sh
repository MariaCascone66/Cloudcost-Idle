#!/bin/bash
import os

# Stampa il percorso del file corrente
print("Percorso corrente:", os.getcwd())

function install_snapshot_scheduler {
    echo "Installing snapshot-scheduler plugin"
    
    # Crea il virtualenv in /opt/stack/snapshot-scheduler/app/venv
    if [ ! -d "/opt/stack/snapshot-scheduler/app/venv" ]; then
        python3 -m venv "/opt/stack/snapshot-scheduler/app/venv"
    fi

    # Attiva l'ambiente e installa i pacchetti
    source "/opt/stack/snapshot-scheduler/app/venv/bin/activate"
    
    # Installa le dipendenze
    if [ -f "/opt/stack/snapshot-scheduler/app/requirements.txt" ]; then
        pip install -r "/opt/stack/snapshot-scheduler/app/requirements.txt" || { echo "Failed to install dependencies"; exit 1; }
    else
        echo "requirements.txt not found!"
        exit 1
    fi
}

function start_snapshot_scheduler {
    echo "Starting snapshot-scheduler service"
    sudo cp "/opt/stack/snapshot-scheduler/scheduler/snap-scheduler.service" "/etc/systemd/system/"

    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable snap-scheduler.service
    sudo systemctl start snap-scheduler.service
}

if [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_snapshot_scheduler 
elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    start_snapshot_scheduler 
fi
