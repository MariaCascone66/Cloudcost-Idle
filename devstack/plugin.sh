#!/bin/bash

if [[ "$1" == "stack" && "$2" == "install" ]]; then
    echo_summary "Installing CloudCost-Idle"
    sudo apt-get install -y python3-flask
    python3 -m venv $COST_IDLE_VENV
    source $COST_IDLE_VENV/bin/activate
    pip install -r $COST_IDLE_DIR/requirements.txt
fi

if [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    echo_summary "Configuring CloudCost-Idle"
    sudo cp $COST_IDLE_DIR/systemd/cloudcost-idle.service /etc/systemd/system/
    sudo systemctl daemon-reexec
    sudo systemctl enable cloudcost-idle
    sudo systemctl start cloudcost-idle
fi

if [[ "$1" == "unstack" ]]; then
    echo_summary "Stopping CloudCost-Idle"
    sudo systemctl stop cloudcost-idle
fi
