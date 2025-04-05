#!/bin/bash

function install_snapshot-scheduler {
    echo "Installing snapshot-scheduler plugin"
    pip install /opt/stack/snapshot-scheduler/app
}

function start_snapshot-scheduler {
    echo "Starting snapshot-scheduler service"
    sudo cp /opt/stack/snapshot-scheduler/snap-scheduler.service /etc/systemd/system/
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
