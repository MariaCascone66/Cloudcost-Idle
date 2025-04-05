#!/bin/bash

function install_snapshot-scheduler {
    echo "Installing snapshot-scheduler plugin"
    
    # Crea il virtualenv 
    if [ ! -d "/opt/stack/snapshot-scheduler/venv" ]; then
        python3 -m venv "/opt/stack/snapshot-scheduler/venv"
    fi

    # Attiva l'ambiente e installa i pacchetti
    source "/opt/stack/snapshot-scheduler/venv/bin/activate"
    
    # Install Requirements
    if [ -f "/opt/stack/snapshot-scheduler/app/requirements.txt" ]; then
        pip install -r "/opt/stack/snapshot-scheduler/app/requirements.txt" || { echo "Failed to install dependencies"; exit 1; }
    else
        echo "requirements.txt not found!"
        exit 1
    fi

     # Installa manualmente scheduler.py
    pip install -r "/opt/stack/snapshot-scheduler/app/scheduler.py"
}

function start_snapshot-scheduler {
    echo "Starting snapshot-scheduler service"
    sudo cp "/opt/stack/snapshot-scheduler/snap-scheduler.service" "/etc/systemd/system/"
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable snap-scheduler.service
    sudo systemctl start snap-scheduler.service
}

if [[ "$1" == "stack" && "$2" == "install" ]]; then
    install_snapshot-scheduler 
elif [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    start_snapshot-scheduler 
fi
