#!/bin/bash

source $DEST/Cloudcost-Idle/devstack/settings

if [[ "$1" == "stack" && "$2" == "install" ]]; then
    echo_summary "Installing CloudCost-Idle"
    sudo apt-get install -y python3-flask
    pip install -r $CLOUDCOST_PLUGIN_DIR/requirements.txt
fi

if [[ "$1" == "stack" && "$2" == "post-config" ]]; then
    echo_summary "Configuring CloudCost-Idle"
    sudo cp $CLOUDCOST_PLUGIN_DIR/systemd/cloudcost-idle.service /etc/systemd/system/
    sudo systemctl daemon-reexec
    sudo systemctl daemon-reload
    sudo systemctl enable cloudcost-idle
    sudo systemctl restart cloudcost-idle
fi

if [[ "$1" == "unstack" ]]; then
    echo_summary "Unstacking CloudCost-Idle"
    sudo systemctl stop cloudcost-idle
fi
